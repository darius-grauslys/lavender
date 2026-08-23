"""mcp_server.py — FastMCP server that wraps lav_impl with pluggable execution backends.

This is the single authority for all Lavender tool execution.  Tools are
registered dynamically from ``lavender_tools.lav_impl.tools`` and dispatched
through either a ``DirectBackend`` (in-process) or a
``SandboxRedirectBackend`` (containerised via podman/docker).

Run with:
    python -m lavender_tools.lav_ai.mcp_server \\
        --project-dir /game --lavender-dir /lavender --backend direct

Or with sandbox execution:
    python -m lavender_tools.lav_ai.mcp_server \\
        --project-dir /game --lavender-dir /lavender --backend sandbox
"""
from __future__ import annotations

import argparse
import atexit
import inspect
import json
import logging
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP

# Ensure the 'tools/' directory is on sys.path so that imports resolve when
# this module is run directly.
_TOOLS_DIR = str(Path(__file__).resolve().parents[2])
if _TOOLS_DIR not in sys.path:
    sys.path.insert(0, _TOOLS_DIR)

from lavender_tools.lav_impl import tools as lav_tools

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Container runtime helpers
# ---------------------------------------------------------------------------


def _detect_runtime() -> str:
    """Detect the container runtime — prefer podman, fall back to docker."""
    if shutil.which("podman"):
        return "podman"
    if shutil.which("docker"):
        return "docker"
    raise RuntimeError(
        "Neither podman nor docker found in PATH. "
        "Install podman (recommended) or docker to use the sandbox backend."
    )


# ---------------------------------------------------------------------------
# Execution backends
# ---------------------------------------------------------------------------


class ExecutionBackend:
    """Abstract base for tool execution backends."""

    def call_tool(self, tool_name: str, params: dict[str, Any]) -> str:
        raise NotImplementedError


class DirectBackend(ExecutionBackend):
    """Executes tools directly in-process."""

    def __init__(self, project_dir: str):
        self.project_dir = project_dir

    def call_tool(self, tool_name: str, params: dict[str, Any]) -> str:
        func = getattr(lav_tools, tool_name, None)
        if func is None:
            return f"ERROR: Unknown tool '{tool_name}'"
        return func(project_dir=self.project_dir, **params)


class SandboxRedirectBackend(ExecutionBackend):
    """Redirects tool execution into a container via podman/docker exec."""

    def __init__(
        self,
        project_dir: str,
        lavender_dir: str,
        image: str = "lav-sandbox",
        runtime: str | None = None,
        restart_per_call: bool = False,
    ):
        self.project_dir = os.path.abspath(project_dir)
        self.lavender_dir = os.path.abspath(lavender_dir)
        self.image = image
        self.runtime = runtime or _detect_runtime()
        self.restart_per_call = restart_per_call
        self.container_name: str | None = None
        self._running = False

    def start(self) -> None:
        """Start the sandbox container with engine mounted RO and project RW."""
        if self._running:
            logger.debug("Container already running")
            return

        rt = self.runtime
        self.container_name = f"lav-mcp-{os.getpid()}"

        # Defensive cleanup of any stale container with the same name
        subprocess.run(
            [rt, "kill", self.container_name],
            capture_output=True, text=True, timeout=5,
        )
        subprocess.run(
            [rt, "rm", "-f", self.container_name],
            capture_output=True, text=True, timeout=10,
        )

        cmd = [
            rt, "run",
            "--detach",
            "--name", self.container_name,
            "--network", "none",
            "--volume", f"{self.lavender_dir}:/lavender:ro",
            "--volume", f"{self.project_dir}:/project:rw",
            "--env", "LAVENDER_DIR=/lavender",
            "--env", "PYTHONPATH=/lavender/tools",
            "--env", "PYTHONUNBUFFERED=1",
            self.image,
            "sleep", "infinity",
        ]

        logger.info("Starting sandbox container %s", self.container_name)
        t0 = time.monotonic()
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        elapsed = time.monotonic() - t0

        if result.returncode != 0:
            raise RuntimeError(
                f"Failed to start container: {result.stderr or result.stdout}"
            )

        # Wait for the container to enter the running state
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline:
            res = subprocess.run(
                [rt, "inspect", "-f", "{{.State.Running}}", self.container_name],
                capture_output=True, text=True,
            )
            if res.stdout.strip() == "true":
                self._running = True
                logger.info("Container started in %.2fs", elapsed)
                return
            time.sleep(0.05)

        raise RuntimeError("Container did not become ready within 10s")

    def stop(self) -> None:
        """Kill and remove the sandbox container."""
        if not self.container_name:
            return

        rt = self.runtime
        logger.info("Stopping sandbox container %s", self.container_name)

        try:
            subprocess.run(
                [rt, "kill", self.container_name],
                capture_output=True, text=True, timeout=5,
            )
        except Exception:
            pass

        try:
            subprocess.run(
                [rt, "rm", "-f", self.container_name],
                capture_output=True, text=True, timeout=10,
            )
        except Exception:
            pass

        self._running = False

    def restart(self) -> None:
        """Kill, remove, and re-create the sandbox container."""
        self.stop()
        self.start()

    def call_tool(self, tool_name: str, params: dict[str, Any]) -> str:
        """Execute a tool inside the sandbox container."""
        if self.restart_per_call:
            self.restart()
        if not self._running:
            self.start()

        rt = self.runtime
        exec_cmd = [rt, "exec", "--workdir", "/project"]

        # Propagate pipeline context env vars into the container
        for env_var in ("LAV_PIPELINE_RUN_ID", "LAV_PIPELINE_ID", "LAV_NODE_ID"):
            val = os.environ.get(env_var)
            if val:
                exec_cmd.extend(["--env", f"{env_var}={val}"])

        exec_cmd.extend([
            self.container_name,
            "python3", "-m", "lavender_tools.lav_impl",
            tool_name,
            json.dumps(params),
            "/project",
        ])

        logger.debug("Container exec: %s", " ".join(exec_cmd))
        result = subprocess.run(exec_cmd, capture_output=True, text=True, timeout=120)
        output = result.stdout + result.stderr
        if result.returncode != 0:
            return f"ERROR (exit {result.returncode}):\n{output}"
        return output


# ---------------------------------------------------------------------------
# FastMCP server
# ---------------------------------------------------------------------------


def _create_mcp_server(host: str = "127.0.0.1", port: int = 8000) -> FastMCP:
    """Create a FastMCP server instance with the given HTTP bind address."""
    return FastMCP(
        "lavender-tools",
        warn_on_duplicate_tools=True,
        host=host,
        port=port,
    )


def _register_tools(mcp: FastMCP, backend: ExecutionBackend) -> None:
    """Dynamically register every public function in lav_impl.tools as an MCP tool."""
    for name, func in inspect.getmembers(lav_tools, inspect.isfunction):
        if name.startswith("_"):
            continue

        # Build a wrapper signature that strips project_dir (injected by backend)
        orig_sig = inspect.signature(func)
        wrapper_params = [
            p.replace(default=p.default)  # keep defaults
            for param_name, p in orig_sig.parameters.items()
            if param_name != "project_dir"
        ]

        def make_wrapper(tool_name: str):
            def wrapper(**kwargs: Any) -> str:
                return backend.call_tool(tool_name, kwargs)

            wrapper.__name__ = tool_name
            wrapper.__doc__ = getattr(lav_tools, tool_name).__doc__
            wrapper.__signature__ = orig_sig.replace(parameters=wrapper_params)
            return wrapper

        mcp.tool()(make_wrapper(name))


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Lavender MCP server")
    parser.add_argument("--project-dir", required=True, help="Path to the game project directory")
    parser.add_argument("--lavender-dir", required=True, help="Path to the Lavender engine directory")
    parser.add_argument(
        "--backend",
        choices=["direct", "sandbox"],
        default="direct",
        help="Execution backend",
    )
    parser.add_argument(
        "--transport",
        choices=["stdio", "streamable-http"],
        default="streamable-http",
        help="MCP transport protocol",
    )
    parser.add_argument("--host", default="127.0.0.1", help="Bind address for HTTP transport")
    parser.add_argument("--port", type=int, default=8000, help="Bind port for HTTP transport")
    parser.add_argument(
        "--restart-per-call",
        action="store_true",
        help="Restart the sandbox container before each tool call",
    )
    args = parser.parse_args()

    backend: ExecutionBackend
    if args.backend == "sandbox":
        backend = SandboxRedirectBackend(
            args.project_dir,
            args.lavender_dir,
            restart_per_call=args.restart_per_call,
        )
        backend.start()
        atexit.register(backend.stop)
    else:
        backend = DirectBackend(args.project_dir)

    mcp = _create_mcp_server(host=args.host, port=args.port)
    _register_tools(mcp, backend)
    mcp.run(transport=args.transport)


if __name__ == "__main__":
    main()
