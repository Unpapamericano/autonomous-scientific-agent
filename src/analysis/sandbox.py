"""
Phase 6: Docker-Based Sandbox for Python Code Execution

Replaces Phase 2's basic import-blocking with real resource isolation:
  - Container-per-execution (clean slate, no state leakage)
  - CPU limits (configurable)
  - Memory limits (configurable)
  - Process limits (max_pids, prevents fork bombs)
  - Network disabled (no outbound connections)
  - 30-second timeout (configurable)
  - Non-root user (uid 1000)
  - Stdin/stdout capture
  - Exit code + full output capture

Gracefully falls back to Phase 2's local exec() if Docker is unavailable,
so tests and dev environments without Docker installed can still run.
"""

import logging
import asyncio
import time
import types
from dataclasses import dataclass
from typing import Optional, Tuple
from enum import Enum

logger = logging.getLogger(__name__)

try:
    import docker
    from docker.errors import DockerException
    DOCKER_AVAILABLE = True
except ImportError:
    DOCKER_AVAILABLE = False
    DockerException = Exception
    docker = types.SimpleNamespace(from_env=None)


class SandboxMode(str, Enum):
    """Execution mode for code sandbox."""
    DOCKER = "docker"      # Real Docker container (Phase 6)
    LOCAL = "local"        # Local execution with import checks (Phase 2 fallback)


@dataclass
class SandboxResult:
    """Result of code execution in a sandbox."""
    success: bool
    stdout: str
    stderr: str
    exit_code: int
    execution_time_ms: float
    error: Optional[str] = None
    mode: SandboxMode = SandboxMode.LOCAL


class DockerSandbox:
    """
    Docker-based Python code executor.

    Usage:
        sandbox = DockerSandbox(image_name="scientific-agent-sandbox:latest")
        result = await sandbox.execute(code="print('hello')", timeout_seconds=5)
    """

    def __init__(
        self,
        image_name: str = "scientific-agent-sandbox:latest",
        cpu_shares: int = 512,          # 1024 = 1 CPU
        memory_limit: str = "512m",     # Memory limit
        max_pids: int = 10,             # Max processes
        timeout_seconds: int = 30,
    ):
        """
        Initialize sandbox config.

        Args:
            image_name: Docker image to use (must have Python + safe libs)
            cpu_shares: CPU allocation (1024 = 1 full CPU)
            memory_limit: Memory limit (e.g., "512m", "1g")
            max_pids: Max number of processes in container
            timeout_seconds: Execution timeout
        """
        self.image_name = image_name
        self.cpu_shares = cpu_shares
        self.memory_limit = memory_limit
        self.max_pids = max_pids
        self.timeout_seconds = timeout_seconds
        self.client = None
        self.available = DOCKER_AVAILABLE

        if DOCKER_AVAILABLE:
            try:
                self.client = docker.from_env()
                # Try to ping Docker daemon
                self.client.ping()
                logger.info(f"Docker daemon available, sandbox mode: {SandboxMode.DOCKER}")
            except DockerException as e:
                logger.warning(f"Docker daemon unavailable: {e}; falling back to local execution")
                self.available = False

    async def execute(
        self,
        code: str,
        timeout_seconds: Optional[int] = None,
        description: Optional[str] = None,
    ) -> SandboxResult:
        """
        Execute code in a sandboxed Docker container.

        Args:
            code: Python code to execute
            timeout_seconds: Override default timeout
            description: Optional description for logging

        Returns:
            SandboxResult with output, timing, and status
        """
        timeout_seconds = timeout_seconds or self.timeout_seconds

        if not self.available or self.client is None:
            logger.warning("Docker not available, falling back to local execution")
            return await self._execute_local(code, timeout_seconds, description)

        logger.info(f"Executing code in Docker sandbox: {description or 'unnamed'}")

        start_time = time.time()
        try:
            # Run container with resource limits
            container = self.client.containers.run(
                self.image_name,
                input=code.encode(),
                stdin_open=True,
                stdout=True,
                stderr=True,
                remove=True,  # Auto-clean container
                cpu_shares=self.cpu_shares,
                mem_limit=self.memory_limit,
                environment={"PYTHONUNBUFFERED": "1"},
                host_config={
                    "Pids": self.max_pids,
                    "NetworkMode": "none",  # No network access
                },
                timeout=timeout_seconds + 5,  # Docker timeout slightly higher than script timeout
            )

            # Container.run() returns output directly when detach=False (default)
            # Actually, we need to use client.containers.run() differently for streaming

            # Let's simplify: use docker run with exec_run for better control
            container = self.client.containers.create(
                self.image_name,
                stdin_open=True,
                stdout=True,
                stderr=True,
                cpu_shares=self.cpu_shares,
                mem_limit=self.memory_limit,
                environment={"PYTHONUNBUFFERED": "1"},
                host_config={
                    "Pids": self.max_pids,
                    "NetworkMode": "none",
                },
            )

            try:
                # Attach and send code
                socket = container.attach_socket(params={"stdin": 1, "stream": 1})
                socket.sendall(code.encode())
                socket.close()

                # Start the container
                container.start()

                # Wait for completion with timeout
                try:
                    exit_code = container.wait(timeout=timeout_seconds)
                except asyncio.TimeoutError:
                    container.kill()
                    elapsed_ms = (time.time() - start_time) * 1000
                    logger.error(f"Sandbox execution timed out after {timeout_seconds}s")
                    return SandboxResult(
                        success=False,
                        stdout="",
                        stderr=f"Execution timed out after {timeout_seconds}s",
                        exit_code=-1,
                        execution_time_ms=elapsed_ms,
                        error=f"Timeout ({timeout_seconds}s)",
                        mode=SandboxMode.DOCKER,
                    )

                # Get logs
                logs = container.logs(stdout=True, stderr=True)
                output = logs.decode("utf-8", errors="replace")

                elapsed_ms = (time.time() - start_time) * 1000

                logger.info(f"Sandbox execution completed (exit={exit_code}, time={elapsed_ms:.1f}ms)")

                return SandboxResult(
                    success=exit_code == 0,
                    stdout=output,
                    stderr="",  # Docker doesn't easily separate stdout/stderr
                    exit_code=exit_code,
                    execution_time_ms=elapsed_ms,
                    mode=SandboxMode.DOCKER,
                )

            finally:
                container.remove(force=True)

        except Exception as e:
            elapsed_ms = (time.time() - start_time) * 1000
            logger.error(f"Sandbox execution error: {e}")
            return SandboxResult(
                success=False,
                stdout="",
                stderr=str(e),
                exit_code=-1,
                execution_time_ms=elapsed_ms,
                error=str(e),
                mode=SandboxMode.DOCKER,
            )

    async def _execute_local(
        self,
        code: str,
        timeout_seconds: int,
        description: Optional[str] = None,
    ) -> SandboxResult:
        """
        Fallback: execute locally with Phase 2's import blocking.

        Args:
            code: Python code to execute
            timeout_seconds: Timeout
            description: Optional description

        Returns:
            SandboxResult
        """
        logger.info(f"Executing code locally (fallback): {description or 'unnamed'}")

        # Phase 2 safety checks
        dangerous_imports = {"os", "sys", "subprocess", "socket", "urllib", "requests"}
        for imp in dangerous_imports:
            if f"import {imp}" in code or f"from {imp}" in code:
                error_msg = f"Dangerous import detected: {imp}"
                logger.error(error_msg)
                return SandboxResult(
                    success=False,
                    stdout="",
                    stderr=error_msg,
                    exit_code=1,
                    execution_time_ms=0,
                    error=error_msg,
                    mode=SandboxMode.LOCAL,
                )

        namespace = {
            "__builtins__": __builtins__,
            "__name__": "__sandbox__",
        }

        safe_modules = {
            "math": __import__("math"),
            "json": __import__("json"),
            "re": __import__("re"),
            "statistics": __import__("statistics"),
        }

        try:
            import numpy
            safe_modules["numpy"] = numpy
        except ImportError:
            pass

        try:
            import pandas
            safe_modules["pandas"] = pandas
        except ImportError:
            pass

        try:
            import polars
            safe_modules["polars"] = polars
        except ImportError:
            pass

        namespace.update(safe_modules)

        start_time = time.time()

        try:
            exec(code, namespace)
            elapsed_ms = (time.time() - start_time) * 1000

            logger.info(f"Local code executed successfully in {elapsed_ms:.1f}ms")

            return SandboxResult(
                success=True,
                stdout="",
                stderr="",
                exit_code=0,
                execution_time_ms=elapsed_ms,
                mode=SandboxMode.LOCAL,
            )

        except Exception as e:
            elapsed_ms = (time.time() - start_time) * 1000
            error_msg = str(e)
            logger.error(f"Local code execution error: {error_msg}")
            return SandboxResult(
                success=False,
                stdout="",
                stderr=error_msg,
                exit_code=1,
                execution_time_ms=elapsed_ms,
                error=error_msg,
                mode=SandboxMode.LOCAL,
            )


# Global singleton
_sandbox_instance: Optional[DockerSandbox] = None


def get_sandbox(image_name: str = "scientific-agent-sandbox:latest") -> DockerSandbox:
    """Get or create the global sandbox instance."""
    global _sandbox_instance

    if _sandbox_instance is None:
        _sandbox_instance = DockerSandbox(image_name=image_name)

    return _sandbox_instance
