"""
Phase 2 Demo: Tool Calling & Orchestration

Demonstrates:
  - Tool registry operations
  - Tool execution
  - Agent orchestration
  - Multi-turn research queries

Run with: python -m scripts.phase2_demo
"""

import asyncio
import json
import logging
from typing import Optional

from src.core.tools import get_tool_registry
from src.core.tools_impl import register_core_tools
from src.core.orchestration import ResearchAgent, AgentState
from src.core.inference import InferenceConfig

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def print_section(title: str):
    """Print a section header."""
    print(f"\n{'=' * 80}")
    print(f"  {title}")
    print(f"{'=' * 80}\n")


async def demo_tool_registry():
    """Demo 1: Tool registry operations."""
    print_section("DEMO 1: Tool Registry")

    registry = get_tool_registry()
    register_core_tools(registry)

    print(f"Available tools: {len(registry.list_available())}")
    for tool in registry.list_available():
        print(f"  - {tool.name}: {tool.description[:60]}...")

    print("\nRegistry stats:")
    stats = registry.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")

    print("\nJSON schema (first tool):")
    schemas = registry.export_json_schema()
    print(json.dumps(schemas[0], indent=2)[:200] + "...\n")


async def demo_tool_execution():
    """Demo 2: Execute individual tools."""
    print_section("DEMO 2: Tool Execution")

    registry = get_tool_registry()
    register_core_tools(registry)

    # Test search tool
    print("Executing: search_literature")
    result = await registry.execute(
        "search_literature",
        {
            "query": "CRISPR gene editing",
            "limit": 3,
            "source": "all",
        },
    )
    print(f"Found {len(result)} papers")
    if result:
        print(f"  First paper: {result[0]['title']}")

    # Test code execution
    print("\nExecuting: execute_python_code")
    result = await registry.execute(
        "execute_python_code",
        {
            "code": "import math; result = math.sqrt(16)",
            "description": "Calculate square root",
        },
    )
    print(f"Success: {result['success']}")
    print(f"Execution time: {result['execution_time_ms']:.1f}ms")

    # Test table parsing
    print("\nExecuting: parse_table_data")
    table_content = """
    | Gene | Success Rate | Notes |
    |------|--------------|-------|
    | RPE65 | 95% | Established |
    | MERTK | 87% | Promising |
    | USH2A | 65% | Early stage |
    """
    result = await registry.execute(
        "parse_table_data",
        {
            "content": table_content,
            "extraction_goal": "Treatment success rates",
        },
    )
    print(f"Parsed {len(result['rows'])} rows × {len(result['columns'])} columns")
    print(f"Summary: {result['summary']}")

    # Test verification
    print("\nExecuting: verify_claim")
    result = await registry.execute(
        "verify_claim",
        {
            "claim": "CRISPR can treat inherited retinal diseases",
            "source_documents": [
                "CRISPR therapy has been tested for inherited retinal disease.",
                "Gene editing shows promise for treating blindness.",
            ],
        },
    )
    print(f"Verified: {result['verified']} (confidence: {result['confidence_score']:.2f})")


async def demo_agent_orchestration():
    """Demo 3: Agent orchestration (requires model)."""
    print_section("DEMO 3: Agent Orchestration")

    # Check if model can be loaded
    try:
        # Use CPU for demo to avoid GPU requirement
        config = InferenceConfig(
            device="cpu",
            max_new_tokens=256,
            quantization="bf16",  # CPU only supports bf16
        )

        logger.info("Initializing research agent...")
        agent = ResearchAgent(inference_config=config)

        # Create a session
        state = AgentState()

        # Query 1: Simple search
        print("Query 1: Search for recent CRISPR research")
        answer, state = await agent.query(
            "Find recent research on CRISPR for inherited blindness",
            session_state=state,
        )
        print(f"Answer: {answer[:200]}...\n")

        # Query 2: Follow-up
        print("Query 2: Follow-up question")
        answer, state = await agent.query(
            "What are the success rates of these treatments?",
            session_state=state,
        )
        print(f"Answer: {answer[:200]}...\n")

        # Print session summary
        print("Session Summary:")
        summary = agent.get_session_summary(state)
        print(json.dumps(summary, indent=2, default=str)[:500] + "...")

    except Exception as e:
        logger.warning(f"Agent demo skipped: {e}")
        print(
            "Note: Full agent demo requires GPU. "
            "Skipping model inference for CPU-only testing."
        )


async def demo_multi_turn_conversation():
    """Demo 4: Multi-turn conversation state."""
    print_section("DEMO 4: Multi-turn Conversation State")

    from src.core.orchestration import MessageRole, ExecutionStep

    state = AgentState()

    # Add conversation
    state.add_message(MessageRole.USER, "What is CRISPR?")
    state.add_message(
        MessageRole.ASSISTANT,
        "CRISPR is a gene-editing technology...",
    )
    state.add_message(MessageRole.USER, "How does it work?")
    state.add_message(
        MessageRole.ASSISTANT,
        "CRISPR works by cutting DNA at specific locations...",
    )

    # Add execution step
    step = ExecutionStep()
    step.agent_output = "Research complete"
    state.record_step(step)

    # Print conversation context
    print("Conversation Context:")
    print(state.get_conversation_context())

    # Print trajectory
    print("\nExecution Trajectory Summary:")
    summary = state.get_trajectory_summary()
    for key, value in summary.items():
        print(f"  {key}: {value}")


async def main():
    """Run all demos."""
    logger.info("=" * 80)
    logger.info("PHASE 2: TOOL CALLING & ORCHESTRATION DEMO")
    logger.info("=" * 80)

    # Demo 1: Registry
    await demo_tool_registry()

    # Demo 2: Tool execution
    await demo_tool_execution()

    # Demo 3: Agent (skip model if CPU)
    await demo_agent_orchestration()

    # Demo 4: Conversation state
    await demo_multi_turn_conversation()

    logger.info("\n" + "=" * 80)
    logger.info("PHASE 2 DEMO COMPLETE")
    logger.info("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
