"""
Phase 2: Agent Orchestration

Orchestration layer connecting Muse Glimmer inference with tool calling.
Supports:
  - Multi-turn conversations
  - Structured tool invocation
  - Failure recovery & retries
  - Execution trajectory logging
  - State management

This layer uses LangChain patterns but keeps the implementation lightweight.
"""

import asyncio
import json
import logging
import uuid
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum

from src.core.inference import MuseGlimmerInference, InferenceConfig
from src.core.tools import ToolRegistry, get_tool_registry

logger = logging.getLogger(__name__)


class MessageRole(str, Enum):
    """Message sender role."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


@dataclass
class Message:
    """A single message in the conversation."""
    role: MessageRole
    content: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ToolCall:
    """A tool invocation by the agent."""
    tool_name: str
    tool_input: Dict[str, Any]
    call_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ToolResult:
    """Result from a tool execution."""
    tool_name: str
    call_id: str
    success: bool
    result: Any
    error: Optional[str] = None
    execution_time_ms: float = 0.0
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ExecutionStep:
    """Single step in agent execution trajectory."""
    step_id: int
    agent_output: Optional[str] = None
    tool_calls: List[ToolCall] = field(default_factory=list)
    tool_results: List[ToolResult] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    latency_ms: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class AgentState:
    """
    Conversation state for multi-turn agent interaction.
    
    Maintains:
      - Message history
      - Execution trajectory
      - Tool call history
      - Session metadata
    """

    def __init__(self, session_id: Optional[str] = None):
        self.session_id = session_id or str(uuid.uuid4())
        self.messages: List[Message] = []
        self.trajectory: List[ExecutionStep] = []
        self.tool_registry: ToolRegistry = get_tool_registry()
        self.step_counter = 0

    def add_message(self, role: MessageRole, content: str, metadata: Optional[Dict] = None):
        """Add a message to conversation history."""
        msg = Message(role=role, content=content, metadata=metadata or {})
        self.messages.append(msg)
        logger.info(f"[{self.session_id}] {role.value}: {content[:100]}...")

    def get_conversation_context(self, max_messages: int = 10) -> str:
        """Get formatted conversation history for LLM context."""
        recent = self.messages[-max_messages:]
        context = ""
        for msg in recent:
            context += f"{msg.role.value.upper()}: {msg.content}\n\n"
        return context

    def record_step(self, step: ExecutionStep):
        """Record an execution step."""
        self.step_counter += 1
        step.step_id = self.step_counter
        self.trajectory.append(step)
        logger.info(f"[{self.session_id}] Step {step.step_id}: latency={step.latency_ms:.1f}ms")

    def get_trajectory_summary(self) -> Dict[str, Any]:
        """Get summary of execution trajectory."""
        total_tools = sum(len(s.tool_calls) for s in self.trajectory)
        total_time = sum(s.latency_ms for s in self.trajectory)

        return {
            "session_id": self.session_id,
            "total_steps": len(self.trajectory),
            "total_tool_calls": total_tools,
            "total_execution_time_ms": total_time,
            "messages_exchanged": len(self.messages),
        }


class ResearchAgent:
    """
    Core research agent orchestrator.
    
    Coordinates:
      - LLM inference (Muse Glimmer)
      - Tool execution
      - Multi-turn conversations
      - State management
      - Error recovery
    """

    def __init__(
        self,
        inference_config: Optional[InferenceConfig] = None,
        tool_registry: Optional[ToolRegistry] = None,
        max_tool_calls: int = 10,
        max_retries: int = 3,
    ):
        """
        Initialize research agent.
        
        Args:
            inference_config: Muse Glimmer configuration
            tool_registry: Tool registry (uses global if None)
            max_tool_calls: Max tools per query
            max_retries: Retry attempts on failures
        """
        self.inference_config = inference_config or InferenceConfig.from_env()
        self.tool_registry = tool_registry or get_tool_registry()
        if tool_registry is None and not self.tool_registry._tools:
            from src.core.tools_impl import register_core_tools

            register_core_tools(self.tool_registry)
        self.max_tool_calls = max_tool_calls
        self.max_retries = max_retries

        logger.info("Initializing ResearchAgent...")
        self.llm = MuseGlimmerInference(self.inference_config)

        # System prompt
        self.system_prompt = (
            "You are a scientific research assistant capable of using tools. "
            "Your goal is to answer research questions by searching literature, "
            "analyzing data, and verifying claims. "
            "Always be precise and cite sources. "
            "When you need to use a tool, respond with JSON like: "
            '{"tool_name": "search_literature", "parameters": {...}}'
        )

        logger.info("ResearchAgent initialized")

    async def query(
        self,
        query: str,
        session_state: Optional[AgentState] = None,
    ) -> Tuple[str, AgentState]:
        """
        Process a research query with tool use.
        
        Args:
            query: Research question
            session_state: Existing conversation state (or creates new)
            
        Returns:
            (final_answer, updated_state)
        """
        if session_state is None:
            session_state = AgentState()

        session_state.add_message(MessageRole.USER, query)
        logger.info(f"[{session_state.session_id}] Processing query: {query}")

        final_answer = None
        tool_call_count = 0

        for attempt in range(self.max_retries):
            try:
                # Create execution step
                import time
                step_start = time.time()
                step = ExecutionStep()

                # Generate LLM response
                context = session_state.get_conversation_context()
                prompt = (
                    f"{self.system_prompt}\n\n"
                    f"Conversation history:\n{context}\n"
                    f"Assistant:"
                )

                response = self.llm.generate(
                    prompt,
                    max_new_tokens=1024,
                    temperature=0.7,
                )

                step.agent_output = response
                session_state.add_message(MessageRole.ASSISTANT, response)

                # Try to extract tool calls
                tool_calls = self._extract_tool_calls(response)

                if tool_calls:
                    step.tool_calls = tool_calls

                    # Execute tools
                    for tool_call in tool_calls:
                        if tool_call_count >= self.max_tool_calls:
                            logger.warning("Max tool calls reached")
                            break

                        result = await self._execute_tool(tool_call)
                        step.tool_results.append(result)
                        tool_call_count += 1

                        # Add result to context
                        result_msg = (
                            f"Tool result from {result.tool_name}: "
                            f"success={result.success}, result={result.result}"
                        )
                        session_state.add_message(MessageRole.SYSTEM, result_msg)

                    # Re-generate after tool results (if tools were used)
                    if tool_calls and tool_call_count < self.max_tool_calls:
                        context = session_state.get_conversation_context()
                        prompt = (
                            f"{self.system_prompt}\n\n"
                            f"Conversation history:\n{context}\n"
                            f"Assistant:"
                        )

                        response = self.llm.generate(
                            prompt,
                            max_new_tokens=1024,
                            temperature=0.7,
                        )

                        step.agent_output = response
                        session_state.add_message(MessageRole.ASSISTANT, response)
                        final_answer = response

                else:
                    # No tool call, final answer
                    final_answer = response

                step.latency_ms = (time.time() - step_start) * 1000
                session_state.record_step(step)

                logger.info(f"[{session_state.session_id}] Query complete (attempt {attempt+1})")
                break

            except Exception as e:
                logger.error(f"[{session_state.session_id}] Attempt {attempt+1} failed: {e}")
                if attempt == self.max_retries - 1:
                    final_answer = f"Error: {str(e)}"
                    session_state.add_message(MessageRole.SYSTEM, final_answer)

        return final_answer or "No response generated", session_state

    def _extract_tool_calls(self, response: str) -> List[ToolCall]:
        """
        Extract tool calls from LLM response.
        
        Looks for JSON patterns like:
        {"tool_name": "search_literature", "parameters": {...}}
        """
        tool_calls = []

        # Decode every JSON object, including objects containing nested parameters.
        decoder = json.JSONDecoder()
        for start, character in enumerate(response):
            if character != "{":
                continue
            try:
                obj, _ = decoder.raw_decode(response[start:])
                if not isinstance(obj, dict) or "tool_name" not in obj:
                    continue
                tool_name = obj.get("tool_name")
                parameters = obj.get("parameters", {})

                if tool_name and self.tool_registry.get(tool_name):
                    tool_calls.append(
                        ToolCall(tool_name=tool_name, tool_input=parameters)
                    )
                    logger.info(f"Extracted tool call: {tool_name}")
                else:
                    logger.warning(f"Unknown tool: {tool_name}")

            except json.JSONDecodeError:
                continue

        return tool_calls

    async def _execute_tool(self, tool_call: ToolCall) -> ToolResult:
        """
        Execute a single tool call with error handling.
        """
        import time
        start = time.perf_counter()

        try:
            result = await self.tool_registry.execute(
                tool_call.tool_name,
                tool_call.tool_input,
            )

            elapsed_ms = max((time.perf_counter() - start) * 1000, 0.001)

            logger.info(
                f"Tool '{tool_call.tool_name}' executed successfully "
                f"in {elapsed_ms:.1f}ms"
            )

            return ToolResult(
                tool_name=tool_call.tool_name,
                call_id=tool_call.call_id,
                success=True,
                result=result,
                execution_time_ms=elapsed_ms,
            )

        except Exception as e:
            elapsed_ms = max((time.perf_counter() - start) * 1000, 0.001)

            logger.error(
                f"Tool '{tool_call.tool_name}' failed: {e} "
                f"(after {elapsed_ms:.1f}ms)"
            )

            return ToolResult(
                tool_name=tool_call.tool_name,
                call_id=tool_call.call_id,
                success=False,
                result=None,
                error=str(e),
                execution_time_ms=elapsed_ms,
            )

    def get_session_summary(self, state: AgentState) -> Dict[str, Any]:
        """Get summary of a session."""
        return {
            "session_id": state.session_id,
            "trajectory": state.get_trajectory_summary(),
            "messages": [
                {
                    "role": m.role.value,
                    "content": m.content[:200],
                    "timestamp": m.timestamp.isoformat(),
                }
                for m in state.messages
            ],
        }
