"""test_mcp_server.py — Unit tests for mcp_server.py execution backends and CLI.

Tests the contracts of DirectBackend, SandboxRedirectBackend, _register_tools,
and the main() CLI entry point.
"""

import inspect
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from lavender_tools.lav_ai.mcp_server import (
    DirectBackend,
    SandboxRedirectBackend,
    _create_mcp_server,
    _register_tools,
    main,
)
from lavender_tools.lav_impl import tools as lav_tools

# ---------------------------------------------------------------------------
# Container-runtime detection helpers
# ---------------------------------------------------------------------------


def _has_container_runtime() -> bool:
    return bool(shutil.which("podman") or shutil.which("docker"))


def _has_lav_sandbox() -> bool:
    if not _has_container_runtime():
        return False
    rt = "podman" if shutil.which("podman") else "docker"
    result = subprocess.run(
        [rt, "image", "exists", "lav-sandbox"],
        capture_output=True,
    )
    return result.returncode == 0


HAS_CONTAINER_RUNTIME = _has_container_runtime()
HAS_LAV_SANDBOX = _has_lav_sandbox()

# ---------------------------------------------------------------------------
# Happy path tests
# ---------------------------------------------------------------------------


class TestDirectBackend:
    def test_direct_backend_unknown_tool(self):
        """Calling a nonexistent tool must return the expected error string."""
        backend = DirectBackend("/tmp")
        result = backend.call_tool("nonexistent_tool_xyz", {})
        assert result == "ERROR: Unknown tool 'nonexistent_tool_xyz'"

    def test_direct_backend_echo(self, tmp_path):
        """Calling a known read-only tool must return a non-empty string."""
        backend = DirectBackend(str(tmp_path))
        result = backend.call_tool("scan_assets", {})
        assert isinstance(result, str)
        assert result.strip()

    def test_direct_backend_project_dir_passed(self, monkeypatch):
        """The backend must inject project_dir into the underlying tool call."""
        captured = {}

        def mock_scan_assets(**kwargs):
            captured["kwargs"] = kwargs
            return "mocked_scan_assets_output"

        monkeypatch.setattr(lav_tools, "scan_assets", mock_scan_assets)

        backend = DirectBackend("/tmp/test_project")
        result = backend.call_tool("scan_assets", {})

        assert result == "mocked_scan_assets_output"
        assert captured["kwargs"]["project_dir"] == "/tmp/test_project"


class TestSandboxBackendMocked:
    """SandboxRedirectBackend tests using mocked subprocess."""

    def test_sandbox_backend_lifecycle(self, monkeypatch):
        """start() and stop() must manage _running and container_name state."""
        calls = []

        def fake_run(cmd, *args, **kwargs):
            calls.append(cmd)
            mock = MagicMock()
            mock.returncode = 0
            if "inspect" in cmd:
                mock.stdout = "true\n"
            else:
                mock.stdout = ""
            mock.stderr = ""
            return mock

        monkeypatch.setattr(subprocess, "run", fake_run)

        backend = SandboxRedirectBackend(
            project_dir="/tmp",
            lavender_dir="/tmp",
            runtime="podman",
        )

        backend.start()
        assert backend._running is True
        assert backend.container_name == f"lav-mcp-{os.getpid()}"
        assert any(c[0] == "podman" and c[1] == "run" for c in calls)

        backend.stop()
        assert backend._running is False
        assert any(
            c == ["podman", "kill", backend.container_name] for c in calls
        )
        assert any(
            c == ["podman", "rm", "-f", backend.container_name] for c in calls
        )

    def test_sandbox_backend_call_tool(self, monkeypatch):
        """call_tool must execute a containerised command and return stdout."""
        calls = []

        def fake_run(cmd, *args, **kwargs):
            calls.append(cmd)
            mock = MagicMock()
            mock.returncode = 0
            if "exec" in cmd:
                mock.stdout = "mocked_exec_output\n"
            elif "inspect" in cmd:
                mock.stdout = "true\n"
            else:
                mock.stdout = ""
            mock.stderr = ""
            return mock

        monkeypatch.setattr(subprocess, "run", fake_run)

        backend = SandboxRedirectBackend(
            project_dir="/tmp",
            lavender_dir="/tmp",
            runtime="podman",
        )
        backend._running = True
        backend.container_name = "lav-mcp-test"

        result = backend.call_tool("query_tools_list", {})
        assert result == "mocked_exec_output\n"
        exec_cmd = next(c for c in calls if "exec" in c)
        assert exec_cmd[0] == "podman"
        assert "query_tools_list" in exec_cmd
        assert json.dumps({}) in exec_cmd
        assert "/project" in exec_cmd

    def test_sandbox_restart_per_call(self, monkeypatch):
        """When restart_per_call=True, call_tool must trigger restart every time."""
        restart_calls = []
        start_calls = []
        stop_calls = []

        def mock_start(self):
            start_calls.append(True)
            self._running = True
            self.container_name = "lav-mcp-test"

        def mock_stop(self):
            stop_calls.append(True)
            self._running = False

        def mock_restart(self):
            restart_calls.append(True)
            mock_stop(self)
            mock_start(self)

        monkeypatch.setattr(SandboxRedirectBackend, "start", mock_start)
        monkeypatch.setattr(SandboxRedirectBackend, "stop", mock_stop)
        monkeypatch.setattr(SandboxRedirectBackend, "restart", mock_restart)

        def fake_run(cmd, *args, **kwargs):
            mock = MagicMock()
            mock.returncode = 0
            mock.stdout = "output"
            mock.stderr = ""
            return mock

        monkeypatch.setattr(subprocess, "run", fake_run)

        backend = SandboxRedirectBackend(
            project_dir="/tmp",
            lavender_dir="/tmp",
            runtime="podman",
            restart_per_call=True,
        )

        result = backend.call_tool("query_tools_list", {})
        assert len(restart_calls) == 1
        assert result == "output"

        result = backend.call_tool("scan_assets", {})
        assert len(restart_calls) == 2
        assert result == "output"

    def test_sandbox_backend_error_propagation(self, monkeypatch):
        """A non-zero exit code from the container exec must be wrapped in an error string."""

        def fake_run(cmd, *args, **kwargs):
            mock = MagicMock()
            if "exec" in cmd:
                mock.returncode = 42
                mock.stdout = "some stdout"
                mock.stderr = "some stderr"
            elif "inspect" in cmd:
                mock.returncode = 0
                mock.stdout = "true\n"
            else:
                mock.returncode = 0
                mock.stdout = ""
            return mock

        monkeypatch.setattr(subprocess, "run", fake_run)

        backend = SandboxRedirectBackend(
            project_dir="/tmp",
            lavender_dir="/tmp",
            runtime="podman",
        )
        backend._running = True
        backend.container_name = "lav-mcp-test"

        result = backend.call_tool("query_tools_list", {})
        assert result.startswith("ERROR (exit 42):")
        assert "some stdout" in result
        assert "some stderr" in result


@pytest.mark.skipif(
    not HAS_LAV_SANDBOX,
    reason="lav-sandbox image not available or container runtime missing",
)
class TestSandboxBackendRealContainer:
    """Integration tests against a real podman/docker container."""

    def test_sandbox_real_container_start_stop(self, tmp_path):
        backend = SandboxRedirectBackend(
            project_dir=str(tmp_path),
            lavender_dir="/home/shalidor/Projects/Lavender",
            runtime="podman",
        )
        backend.start()
        assert backend._running is True
        assert backend.container_name.startswith("lav-mcp-")

        # Run a trivial tool inside the container via call_tool
        result = backend.call_tool("scan_assets", {})
        assert isinstance(result, str)
        assert "scan_assets" in result

        backend.stop()
        assert backend._running is False


# ---------------------------------------------------------------------------
# Tool registry tests
# ---------------------------------------------------------------------------


class TestRegisterTools:
    def test_register_tools_populates_registry(self):
        """_register_tools must add at least 40 public tools to the MCP server."""
        mcp = _create_mcp_server()
        backend = DirectBackend("/tmp")
        _register_tools(mcp, backend)

        tools = mcp._tool_manager._tools
        assert len(tools) >= 40
        assert "gen_ui_code" in tools
        assert "scan_assets" in tools
        assert "query_tools_list" in tools

    def test_register_tools_strips_project_dir(self):
        """The exposed wrapper signatures must not contain the project_dir parameter."""
        mcp = _create_mcp_server()
        backend = DirectBackend("/tmp")
        _register_tools(mcp, backend)

        tools = mcp._tool_manager._tools
        assert "scan_assets" in tools
        tool = tools["scan_assets"]
        sig = inspect.signature(tool.fn)
        assert "project_dir" not in sig.parameters

    def test_register_tools_preserves_docstring(self):
        """The wrapper must preserve the original function's docstring."""
        mcp = _create_mcp_server()
        backend = DirectBackend("/tmp")
        _register_tools(mcp, backend)

        tools = mcp._tool_manager._tools
        assert "scan_assets" in tools
        tool = tools["scan_assets"]
        assert tool.description
        assert "Discover and classify project assets" in tool.description


# ---------------------------------------------------------------------------
# CLI tests
# ---------------------------------------------------------------------------


class TestCli:
    def test_cli_help(self):
        """Running with --help must print usage and list all expected arguments."""
        tools_dir = str(Path(__file__).resolve().parents[3])
        env = os.environ.copy()
        env["PYTHONPATH"] = tools_dir + os.pathsep + env.get("PYTHONPATH", "")
        result = subprocess.run(
            [sys.executable, "-m", "lavender_tools.lav_ai.mcp_server", "--help"],
            capture_output=True,
            text=True,
            cwd=tools_dir,
            env=env,
        )
        assert result.returncode == 0
        stdout = result.stdout
        assert "--project-dir" in stdout
        assert "--lavender-dir" in stdout
        assert "--backend" in stdout
        assert "--transport" in stdout
        assert "--host" in stdout
        assert "--port" in stdout
        assert "--restart-per-call" in stdout

    def test_cli_argument_parser(self, monkeypatch):
        """main() must create the correct backend based on CLI arguments."""
        backend_instances = []

        class MockBackend:
            def __init__(self, *args, **kwargs):
                backend_instances.append((args, kwargs))

            def call_tool(self, *a, **kw):
                return ""

            def start(self):
                pass

            def stop(self):
                pass

        monkeypatch.setattr(
            "lavender_tools.lav_ai.mcp_server.DirectBackend",
            MockBackend,
        )
        monkeypatch.setattr(
            "lavender_tools.lav_ai.mcp_server.SandboxRedirectBackend",
            MockBackend,
        )
        monkeypatch.setattr(
            "lavender_tools.lav_ai.mcp_server.FastMCP.run",
            lambda *args, **kwargs: None,
        )
        monkeypatch.setattr(
            "lavender_tools.lav_ai.mcp_server._register_tools",
            lambda mcp, backend: None,
        )

        monkeypatch.setattr(
            sys,
            "argv",
            [
                "mcp_server",
                "--project-dir",
                "/tmp/proj",
                "--lavender-dir",
                "/tmp/lav",
                "--backend",
                "direct",
                "--transport",
                "stdio",
                "--host",
                "0.0.0.0",
                "--port",
                "9000",
            ],
        )
        try:
            main()
        except SystemExit:
            pass

        assert len(backend_instances) == 1
        args, kwargs = backend_instances[0]
        assert args == ("/tmp/proj",)

        backend_instances.clear()

        monkeypatch.setattr(
            sys,
            "argv",
            [
                "mcp_server",
                "--project-dir",
                "/tmp/proj",
                "--lavender-dir",
                "/tmp/lav",
                "--backend",
                "sandbox",
                "--restart-per-call",
            ],
        )
        try:
            main()
        except SystemExit:
            pass

        assert len(backend_instances) == 1
        args, kwargs = backend_instances[0]
        assert kwargs.get("restart_per_call") is True
