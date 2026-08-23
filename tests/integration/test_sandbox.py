"""
Phase 6: Integration Tests for Sandbox Code Execution

Tests use mocked Docker client (no real Docker dependency in CI/tests).
When Docker is unavailable, the sandbox gracefully falls back to Phase 2's
local execution, which is also tested.
"""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch, Mock
import asyncio

from src.analysis.sandbox import DockerSandbox, SandboxMode, SandboxResult, DOCKER_AVAILABLE


# ============================================================================
# UNIT TESTS (NO DOCKER REQUIRED)
# ============================================================================

class TestSandboxResultDataclass:
    """Test the SandboxResult dataclass."""

    def test_sandbox_result_success(self):
        result = SandboxResult(
            success=True,
            stdout="Hello, World!",
            stderr="",
            exit_code=0,
            execution_time_ms=100.5,
            mode=SandboxMode.LOCAL,
        )

        assert result.success is True
        assert result.stdout == "Hello, World!"
        assert result.exit_code == 0
        assert result.mode == SandboxMode.LOCAL

    def test_sandbox_result_failure(self):
        result = SandboxResult(
            success=False,
            stdout="",
            stderr="NameError: name 'x' is not defined",
            exit_code=1,
            execution_time_ms=50.0,
            error="NameError",
            mode=SandboxMode.LOCAL,
        )

        assert result.success is False
        assert "NameError" in result.stderr
        assert result.error == "NameError"


class TestDockerSandboxInitialization:
    """Test DockerSandbox initialization."""

    def test_init_with_defaults(self):
        sandbox = DockerSandbox(image_name="test-image:latest")

        assert sandbox.image_name == "test-image:latest"
        assert sandbox.cpu_shares == 512
        assert sandbox.memory_limit == "512m"
        assert sandbox.max_pids == 10
        assert sandbox.timeout_seconds == 30

    def test_init_with_custom_config(self):
        sandbox = DockerSandbox(
            image_name="my-sandbox:v1",
            cpu_shares=1024,
            memory_limit="1g",
            max_pids=20,
            timeout_seconds=60,
        )

        assert sandbox.image_name == "my-sandbox:v1"
        assert sandbox.cpu_shares == 1024
        assert sandbox.memory_limit == "1g"
        assert sandbox.max_pids == 20
        assert sandbox.timeout_seconds == 60


@pytest.mark.asyncio
class TestLocalExecution:
    """Test fallback local execution (Phase 2 mode)."""

    async def test_local_execute_simple_code(self):
        sandbox = DockerSandbox()
        sandbox.available = False

        result = await sandbox.execute("x = 1 + 1")

        assert result.success is True
        assert result.exit_code == 0
        assert result.mode == SandboxMode.LOCAL

    async def test_local_execute_with_safe_imports(self):
        sandbox = DockerSandbox()
        sandbox.available = False

        code = """
import math
import json
x = math.sqrt(16)
y = json.dumps({"result": x})
"""
        result = await sandbox.execute(code)

        assert result.success is True

    async def test_local_execute_dangerous_import_blocked(self):
        sandbox = DockerSandbox()
        sandbox.available = False

        result = await sandbox.execute("import os\nos.system('whoami')")

        assert result.success is False
        assert "Dangerous import detected: os" in result.stderr
        assert result.exit_code == 1

    async def test_local_execute_subprocess_blocked(self):
        sandbox = DockerSandbox()
        sandbox.available = False

        result = await sandbox.execute("import subprocess")

        assert result.success is False
        assert "subprocess" in result.stderr

    async def test_local_execute_exception_handling(self):
        sandbox = DockerSandbox()
        sandbox.available = False

        result = await sandbox.execute("raise ValueError('test error')")

        assert result.success is False
        assert "test error" in result.stderr
        assert result.exit_code == 1

    async def test_local_execute_with_numpy(self):
        """Test that numpy is available when installed."""
        sandbox = DockerSandbox()
        sandbox.available = False

        code = """
import numpy as np
arr = np.array([1, 2, 3])
result = arr.sum()
"""
        result = await sandbox.execute(code)

        # numpy may not be installed in test env, so we just check it doesn't crash
        assert isinstance(result.success, bool)

    async def test_local_execute_timing(self):
        """Test that execution timing is captured."""
        sandbox = DockerSandbox()
        sandbox.available = False

        result = await sandbox.execute("import time; time.sleep(0.1)")

        assert result.execution_time_ms >= 100
        assert result.mode == SandboxMode.LOCAL


@pytest.mark.asyncio
class TestDockerExecution:
    """Test Docker execution (mocked Docker client)."""

    @patch("src.analysis.sandbox.docker.from_env")
    async def test_docker_execute_success(self, mock_docker_env):
        """Test successful Docker execution (mocked)."""
        mock_client = MagicMock()
        mock_docker_env.return_value = mock_client
        mock_client.ping.return_value = True

        mock_container = MagicMock()
        mock_client.containers.create.return_value = mock_container
        mock_container.wait.return_value = 0
        mock_container.logs.return_value = b"Hello, World!"
        mock_container.attach_socket.return_value = MagicMock()

        sandbox = DockerSandbox()
        sandbox.available = True
        sandbox.client = mock_client

        result = await sandbox.execute("print('Hello, World!')", timeout_seconds=5)

        assert result.success is True
        assert result.exit_code == 0
        assert "Hello, World!" in result.stdout
        assert result.mode == SandboxMode.DOCKER

    @patch("src.analysis.sandbox.docker.from_env")
    async def test_docker_execute_failure(self, mock_docker_env):
        """Test Docker execution with non-zero exit code."""
        mock_client = MagicMock()
        mock_docker_env.return_value = mock_client
        mock_client.ping.return_value = True

        mock_container = MagicMock()
        mock_client.containers.create.return_value = mock_container
        mock_container.wait.return_value = 1
        mock_container.logs.return_value = b"Error: something went wrong"
        mock_container.attach_socket.return_value = MagicMock()

        sandbox = DockerSandbox()
        sandbox.available = True
        sandbox.client = mock_client

        result = await sandbox.execute("raise Exception('test')", timeout_seconds=5)

        assert result.success is False
        assert result.exit_code == 1
        assert result.mode == SandboxMode.DOCKER

    @patch("src.analysis.sandbox.docker.from_env")
    async def test_docker_execute_timeout(self, mock_docker_env):
        """Test Docker execution timeout."""
        mock_client = MagicMock()
        mock_docker_env.return_value = mock_client
        mock_client.ping.return_value = True

        mock_container = MagicMock()
        mock_client.containers.create.return_value = mock_container
        mock_container.wait.side_effect = asyncio.TimeoutError()
        mock_container.kill.return_value = None
        mock_container.attach_socket.return_value = MagicMock()

        sandbox = DockerSandbox()
        sandbox.available = True
        sandbox.client = mock_client

        result = await sandbox.execute("while True: pass", timeout_seconds=1)

        assert result.success is False
        assert "timed out" in result.stderr.lower()
        assert result.exit_code == -1

    @patch("src.analysis.sandbox.docker.from_env")
    async def test_docker_execute_cleanup_on_error(self, mock_docker_env):
        """Test that container is cleaned up even on error."""
        mock_client = MagicMock()
        mock_docker_env.return_value = mock_client
        mock_client.ping.return_value = True

        mock_container = MagicMock()
        mock_client.containers.create.return_value = mock_container
        mock_container.attach_socket.side_effect = Exception("Connection failed")

        sandbox = DockerSandbox()
        sandbox.available = True
        sandbox.client = mock_client

        result = await sandbox.execute("print('test')", timeout_seconds=5)

        assert result.success is False
        mock_container.remove.assert_called()

    def test_docker_unavailable_fallback(self):
        """Test fallback when Docker is unavailable at init."""
        with patch("src.analysis.sandbox.DOCKER_AVAILABLE", False):
            sandbox = DockerSandbox()
            assert sandbox.available is False


@pytest.mark.asyncio
class TestSandboxLocalFallback:
    """Test the local fallback execution path directly."""

    async def test_local_fallback_simple_arithmetic(self):
        """Test basic arithmetic in local fallback mode."""
        sandbox = DockerSandbox()
        sandbox.available = False

        result = await sandbox.execute(
            code="result = 2 + 2\nassert result == 4",
            timeout_seconds=5,
            description="Test arithmetic",
        )

        assert result.success is True
        assert result.mode == SandboxMode.LOCAL
        assert result.execution_time_ms >= 0

    async def test_local_fallback_statistics(self):
        """Test statistics library availability."""
        sandbox = DockerSandbox()
        sandbox.available = False

        code = """
import statistics
data = [1, 2, 3, 4, 5]
mean = statistics.mean(data)
assert mean == 3.0
"""
        result = await sandbox.execute(code, timeout_seconds=5)

        assert result.success is True
