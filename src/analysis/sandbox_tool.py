"""
Phase 6: Sandbox-Based Code Execution Agent Tool

Replaces Phase 2's `execute_python_code` tool with the Phase 6 Docker sandbox.
Automatically falls back to Phase 2's local execution if Docker is unavailable
(for tests/dev environments).

Same tool interface as Phase 2, so it's a drop-in replacement in the tool
registry (just swap the execution function).
"""

import logging
from typing import Any, Dict

from src.core.tools import (
    ToolDefinition,
    ToolType,
    ToolStatus,
    ExecuteCode,
    CodeExecutionResult,
)
from src.analysis.sandbox import get_sandbox

logger = logging.getLogger(__name__)


async def execute_python_code_phase6(
    code: str,
    timeout_seconds: int = 30,
    description: str = None,
) -> Dict[str, Any]:
    """
    Execute Python code in a sandboxed Docker container (Phase 6).

    Falls back to Phase 2's local execution if Docker is unavailable.

    Args:
        code: Python code to execute
        timeout_seconds: Execution timeout (max 300s)
        description: Optional description for logging

    Returns:
        CodeExecutionResult dict
    """
    logger.info(f"Executing code in Phase 6 sandbox: {description or 'unnamed'}")

    sandbox = get_sandbox()
    result = await sandbox.execute(code, timeout_seconds=timeout_seconds, description=description)

    return {
        "success": result.success,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "return_value": None,  # Not applicable for Docker/local exec
        "execution_time_ms": result.execution_time_ms,
        "error": result.error,
        "exit_code": result.exit_code,
        "sandbox_mode": result.mode.value,
    }


EXECUTE_CODE_TOOL_PHASE6 = ToolDefinition(
    name="execute_python_code",
    type=ToolType.EXECUTE,
    description=(
        "Execute Python code for data analysis, statistics, or visualization. "
        "Code runs in an isolated Docker sandbox with resource limits (512MB RAM, "
        "no network access, max 10 processes). Safe imports available: math, json, re, "
        "statistics, numpy, pandas. "
        "Use for numerical analysis, data manipulation, and calculations."
    ),
    input_schema=ExecuteCode,
    output_schema=CodeExecutionResult,
    execution_fn=execute_python_code_phase6,
    status=ToolStatus.AVAILABLE,
    tags=["analysis", "code", "python", "sandbox"],
)


def register_sandbox_tool(registry) -> None:
    """
    Register Phase 6 sandbox-based code execution tool.

    This replaces the Phase 2 tool in the registry.
    """
    # Remove the Phase 2 tool if it exists
    if "execute_python_code" in registry._tools:
        logger.info("Replacing Phase 2 execute_python_code with Phase 6 sandbox version")

    registry.register(EXECUTE_CODE_TOOL_PHASE6)
    logger.info("Registered Phase 6 sandbox code execution tool")
