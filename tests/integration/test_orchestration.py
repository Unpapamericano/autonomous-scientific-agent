"""
Integration tests for Phase 2: Tool Calling & Orchestration

Tests:
  - Tool registry operations
  - Tool execution
  - Agent orchestration
  - Multi-turn conversations
  - Error handling & retries
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock

from src.core.tools import ToolRegistry, ToolType, ToolStatus
from src.core.tools_impl import CORE_TOOLS, register_core_tools
from src.core.orchestration import ResearchAgent, AgentState, MessageRole


class TestToolRegistry:
    """Test tool registry operations."""

    def test_register_tool(self):
        """Test registering a tool."""
        registry = ToolRegistry()
        assert len(registry.list_available()) == 0

        register_core_tools(registry)
        available = registry.list_available()

        assert len(available) > 0
        assert all(t.status == ToolStatus.AVAILABLE for t in available)

    def test_get_tool(self):
        """Test retrieving a tool."""
        registry = ToolRegistry()
        register_core_tools(registry)

        tool = registry.get("search_literature")
        assert tool is not None
        assert tool.name == "search_literature"
        assert tool.type == ToolType.SEARCH

    def test_list_by_type(self):
        """Test filtering tools by type."""
        registry = ToolRegistry()
        register_core_tools(registry)

        search_tools = registry.list_by_type(ToolType.SEARCH)
        assert len(search_tools) >= 1
        assert all(t.type == ToolType.SEARCH for t in search_tools)

    def test_export_json_schema(self):
        """Test exporting JSON schema."""
        registry = ToolRegistry()
        register_core_tools(registry)

        schema = registry.export_json_schema()
        assert len(schema) > 0
        assert all("name" in s and "properties" in s for s in schema)

    def test_export_openai_format(self):
        """Test exporting OpenAI function calling format."""
        registry = ToolRegistry()
        register_core_tools(registry)

        schema = registry.export_openai_format()
        assert len(schema) > 0
        assert all("name" in s and "parameters" in s for s in schema)

    def test_registry_stats(self):
        """Test registry statistics."""
        registry = ToolRegistry()
        register_core_tools(registry)

        stats = registry.get_stats()
        assert stats["total_tools"] > 0
        assert stats["available_tools"] > 0


class TestToolExecution:
    """Test tool execution."""

    @pytest.mark.asyncio
    async def test_search_tool(self):
        """Test search tool execution."""
        from src.core.tools_impl import search_literature

        result = await search_literature(
            query="CRISPR gene editing",
            limit=5,
        )

        assert isinstance(result, list)
        assert len(result) > 0
        assert all("paper_id" in r and "title" in r for r in result)

    @pytest.mark.asyncio
    async def test_execute_code_tool(self):
        """Test code execution tool."""
        from src.core.tools_impl import execute_python_code

        result = await execute_python_code(
            code="x = 2 + 2",
            description="Simple math",
        )

        assert result["success"] is True
        assert result["error"] is None

    @pytest.mark.asyncio
    async def test_dangerous_import_blocked(self):
        """Test that dangerous imports are blocked."""
        from src.core.tools_impl import execute_python_code

        result = await execute_python_code(
            code="import os",
            description="Dangerous",
        )

        assert result["success"] is False
        assert "Dangerous import" in result["stderr"]

    @pytest.mark.asyncio
    async def test_parse_table_tool(self):
        """Test table parsing."""
        from src.core.tools_impl import parse_table_data

        content = """
        | Name | Value |
        |------|-------|
        | A    | 1     |
        | B    | 2     |
        """

        result = await parse_table_data(content)

        assert result["rows"]
        assert len(result["columns"]) == 2
        assert result["summary"]

    @pytest.mark.asyncio
    async def test_registry_execution(self):
        """Test executing tools through registry."""
        registry = ToolRegistry()
        register_core_tools(registry)

        result = await registry.execute(
            "search_literature",
            {"query": "test", "limit": 5},
        )

        assert isinstance(result, dict)


class TestAgentState:
    """Test agent conversation state."""

    def test_create_state(self):
        """Test creating agent state."""
        state = AgentState()
        assert state.session_id
        assert len(state.messages) == 0
        assert len(state.trajectory) == 0

    def test_add_message(self):
        """Test adding messages."""
        state = AgentState()
        state.add_message(MessageRole.USER, "test query")

        assert len(state.messages) == 1
        assert state.messages[0].role == MessageRole.USER
        assert state.messages[0].content == "test query"

    def test_get_conversation_context(self):
        """Test getting conversation context."""
        state = AgentState()
        state.add_message(MessageRole.USER, "What is CRISPR?")
        state.add_message(MessageRole.ASSISTANT, "CRISPR is...")

        context = state.get_conversation_context()
        assert "USER:" in context
        assert "ASSISTANT:" in context
        assert "CRISPR" in context

    def test_trajectory_summary(self):
        """Test trajectory summary."""
        state = AgentState()
        state.add_message(MessageRole.USER, "test")

        summary = state.get_trajectory_summary()
        assert summary["session_id"] == state.session_id
        assert summary["total_steps"] == 0


class TestResearchAgent:
    """Test research agent orchestration."""

    def test_agent_initialization(self):
        """Test agent initialization."""
        with patch("src.core.orchestration.MuseGlimmerInference"):
            agent = ResearchAgent()
            assert agent.max_tool_calls == 10
            assert agent.max_retries == 3

    def test_extract_tool_calls(self):
        """Test extracting tool calls from response."""
        with patch("src.core.orchestration.MuseGlimmerInference"):
            agent = ResearchAgent()

            response = 'I will search: {"tool_name": "search_literature", "parameters": {"query": "test"}}'
            tool_calls = agent._extract_tool_calls(response)

            assert len(tool_calls) == 1
            assert tool_calls[0].tool_name == "search_literature"
            assert tool_calls[0].tool_input["query"] == "test"

    def test_extract_multiple_tool_calls(self):
        """Test extracting multiple tool calls."""
        with patch("src.core.orchestration.MuseGlimmerInference"):
            agent = ResearchAgent()

            response = (
                'First: {"tool_name": "search_literature", "parameters": {"query": "A"}} '
                'Then: {"tool_name": "search_literature", "parameters": {"query": "B"}}'
            )
            tool_calls = agent._extract_tool_calls(response)

            assert len(tool_calls) == 2

    @pytest.mark.asyncio
    async def test_execute_tool(self):
        """Test executing a tool through agent."""
        with patch("src.core.orchestration.MuseGlimmerInference"):
            agent = ResearchAgent()

            from src.core.orchestration import ToolCall
            tool_call = ToolCall(
                tool_name="search_literature",
                tool_input={"query": "test", "limit": 5},
            )

            result = await agent._execute_tool(tool_call)

            assert result.success
            assert result.tool_name == "search_literature"
            assert result.execution_time_ms > 0

    def test_get_session_summary(self):
        """Test session summary."""
        with patch("src.core.orchestration.MuseGlimmerInference"):
            agent = ResearchAgent()
            state = AgentState()
            state.add_message(MessageRole.USER, "test")

            summary = agent.get_session_summary(state)

            assert summary["session_id"]
            assert summary["trajectory"]
            assert summary["messages"]


class TestErrorHandling:
    """Test error handling and recovery."""

    def test_tool_not_found(self):
        """Test tool not found error."""
        registry = ToolRegistry()

        with pytest.raises(KeyError):
            asyncio.run(registry.execute("nonexistent_tool", {}))

    def test_tool_unavailable(self):
        """Test tool unavailable error."""
        registry = ToolRegistry()
        register_core_tools(registry)

        # Disable a tool
        tool = registry.get("execute_python_code")
        tool.status = ToolStatus.DISABLED

        with pytest.raises(ValueError):
            asyncio.run(registry.execute("execute_python_code", {}))


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
