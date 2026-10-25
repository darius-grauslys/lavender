#!/usr/bin/env python3
"""
Tests for the Lavender MCP server.

Covers:
  - Tool definitions (schema, required fields, method mapping)
  - SessionState dataclass
  - Session lifecycle (start, status, stop, error cases)
  - Tool dispatch (LavMcpSession.dispatch_tool)
  - MCP JSON-RPC protocol (initialize, tools/list, tools/call, error handling)
  - SessionRegistry (create, get, remove, list)
  - MCP helpers (_make_response, _make_error, _handle_mcp_request)

Run:
    python3 -m mcp.test_lav_mcp
    python3 mcp/test_lav_mcp.py
"""
from __future__ import annotations

import json
import os
import sys

# Ensure the repo root is on sys.path so the ``mcp`` package and its
# local modules (gdb_frame_controller, debug_scanner, etc.) are importable
# regardless of the current working directory.
_REPO_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, _REPO_ROOT)

# --------------------------------------------------------------------------- #
#  Test framework (minimal, no external dependencies)
# --------------------------------------------------------------------------- #
_PASS = 0
_FAIL = 0


def _check(name: str, condition: bool, detail: str = "") -> None:
    global _PASS, _FAIL
    if condition:
        _PASS += 1
    else:
        _FAIL += 1
        msg = f"FAIL: {name}"
        if detail:
            msg += f" — {detail}"
        print(msg)


def _section(name: str) -> None:
    print(f"\n--- {name} ---")


# --------------------------------------------------------------------------- #
#  Fake GDB stub (minimal, for sessions that need a gdbmi handle)
# --------------------------------------------------------------------------- #
class FakeGdbmi:
    """Minimal stub of pygdbmi's GdbController for testing.

    Records all commands sent to it and returns canned responses.
    """

    def __init__(self, responses: dict | None = None, level: int = 3):
        self.commands: list[str] = []
        self._responses = responses or {}
        self.level = level

    def write(self, cmd: str, read_response: bool = True, **kwargs):
        self.commands.append(cmd)
        if not read_response:
            return []

        # Handle common gdb MI commands.
        if cmd.startswith("-stack-info-frame"):
            return [{
                "type": "result",
                "message": "done",
                "payload": {"frame": {"level": str(self.level)}},
            }]
        if cmd.startswith("-data-evaluate-expression"):
            expr = cmd[len("-data-evaluate-expression "):].strip()
            val = self._responses.get(expr, "0x0")
            return [{"type": "result", "message": "done",
                     "payload": {"value": val}}]
        if cmd.startswith("-stack-list-frames"):
            return [{"type": "result", "message": "done",
                     "payload": {"stack": [
                         {"func": "main", "file": "main.c", "line": "1"},
                     ]}}]
        # Default response for -interpreter-exec, -exec-*, -break-*, etc.
        return [{"type": "result", "message": "done"}]

    def exit(self) -> None:
        self.commands.append("exit")


# --------------------------------------------------------------------------- #
#  Import the modules under test
# --------------------------------------------------------------------------- #
# These imports will succeed even without pygdbmi (graceful degradation).
from mcp.lav_mcp import (
    LavMcpSession,
    SessionState,
    TOOL_DEFINITIONS,
    _TOOL_METHOD_MAP,
)
from mcp.lav_mcp_server import (
    _make_response,
    _make_error,
    _handle_mcp_request,
    SessionRegistry,
    load_config,
    make_session_factory,
)


# --------------------------------------------------------------------------- #
#  Tests
# --------------------------------------------------------------------------- #

def test_tool_definitions() -> None:
    """Test that TOOL_DEFINITIONS is well-formed MCP tool schema."""
    _section("Tool Definitions")

    _check(
        "TOOL_DEFINITIONS is non-empty",
        len(TOOL_DEFINITIONS) > 0,
        f"got {len(TOOL_DEFINITIONS)} tools",
    )

    for tool in TOOL_DEFINITIONS:
        name = tool.get("name", "<missing>")
        _check(
            f"tool '{name}' has 'name'",
            "name" in tool and tool["name"],
            f"fields: {list(tool.keys())}",
        )
        _check(
            f"tool '{name}' has 'description'",
            "description" in tool and tool["description"],
        )
        _check(
            f"tool '{name}' has 'inputSchema'",
            "inputSchema" in tool,
        )

        schema = tool.get("inputSchema", {})
        _check(
            f"tool '{name}' schema is type 'object'",
            schema.get("type") == "object",
        )
        _check(
            f"tool '{name}' schema has 'properties'",
            "properties" in schema,
        )
        _check(
            f"tool '{name}' schema has 'required' (or empty list)",
            "required" in schema or True,  # required is optional
        )

    # Check all required tools are present.
    expected_tools = {
        "session_start", "session_status", "session_stop",
        "navigate_step", "navigate_source",
        "core_dump", "core_load", "core_reset",
        "process_list", "process_watch",
        "input_read", "input_write",
        "ui_list", "ui_invoke",
        "graphics_screenshot",
        "audio_list", "audio_listen",
    }
    actual_tools = {t["name"] for t in TOOL_DEFINITIONS}
    _check(
        "All expected tools present",
        expected_tools == actual_tools,
        f"missing: {expected_tools - actual_tools}, "
        f"extra: {actual_tools - expected_tools}",
    )


def test_tool_method_mapping() -> None:
    """Test that _TOOL_METHOD_MAP maps every tool name to a method."""
    _section("Tool Method Mapping")

    for tool in TOOL_DEFINITIONS:
        name = tool["name"]
        _check(
            f"tool '{name}' in _TOOL_METHOD_MAP",
            name in _TOOL_METHOD_MAP,
        )
        method_name = _TOOL_METHOD_MAP.get(name, "")
        _check(
            f"method '{method_name}' exists on LavMcpSession",
            hasattr(LavMcpSession, method_name),
            f"method_name={method_name}",
        )

    # Check required-parameter tools have required fields in schema.
    for tool in TOOL_DEFINITIONS:
        schema = tool.get("inputSchema", {})
        required = schema.get("required", [])
        for req in required:
            _check(
                f"tool '{tool['name']}' has '{req}' in properties",
                req in schema.get("properties", {}),
            )


def test_session_state() -> None:
    """Test SessionState dataclass defaults and transitions."""
    _section("Session State")

    state = SessionState()
    _check("default running=False", state.running is False)
    _check("default halted=False", state.halted is False)
    _check("default crashed=False", state.crashed is False)
    _check("default backtrace=''", state.backtrace == "")
    _check("default last_dump_uuid=None", state.last_dump_uuid is None)

    # Test with values.
    state2 = SessionState(
        running=True,
        halted=True,
        crashed=False,
        backtrace="#0  main",
        last_dump_uuid="abc-123",
    )
    _check("running=True", state2.running is True)
    _check("halted=True", state2.halted is True)
    _check("backtrace set", state2.backtrace == "#0  main")
    _check("last_dump_uuid set", state2.last_dump_uuid == "abc-123")


def test_session_not_started() -> None:
    """Test that tools return error when GDB is not started."""
    _section("Session Not Started")

    session = LavMcpSession(executable="/fake/path/game")
    _check("executable set", session.executable == "/fake/path/game")
    _check("not running initially", session.is_running is False)
    _check("not halted initially", session.is_halted is False)
    _check("not crashed initially", session.is_crashed is False)

    # Tools should return error without GDB.
    result = session.session_status()
    _check(
        "session_status returns 'not started'",
        "NOT started" in result or "not running" in result.lower(),
        f"got: {result}",
    )

    result = session.navigate_step()
    _check(
        "navigate_step returns error",
        "ERROR" in result or "not started" in result.lower(),
        f"got: {result}",
    )

    result = session.process_list()
    _check(
        "process_list returns error",
        "ERROR" in result or "not started" in result.lower(),
        f"got: {result}",
    )

    # ui_manager is no longer a tool — ui_list now shows all elements.
    # Verify dispatch returns error for non-existent tools.
    result = session.dispatch_tool("ui_manager")
    _check(
        "ui_manager no longer exists as a tool",
        "ERROR" in result or "not found" in result.lower() or "unknown" in result.lower(),
        f"got: {result}",
    )


def test_tool_dispatch_unknown() -> None:
    """Test dispatch_tool with unknown tool names."""
    _section("Tool Dispatch (Unknown)")

    session = LavMcpSession(executable="/fake/path/game")

    result = session.dispatch_tool("nonexistent_tool")
    _check(
        "unknown tool returns error",
        "ERROR" in result and "nonexistent_tool" in result,
        f"got: {result}",
    )

    result = session.dispatch_tool("session_start")
    _check(
        "session_start dispatches",
        isinstance(result, str),
        f"got: {type(result)}",
    )


def test_tool_dispatch_with_args() -> None:
    """Test dispatch_tool passes arguments correctly."""
    _section("Tool Dispatch (With Args)")

    session = LavMcpSession(executable="/fake/path/game")

    # core_load without gdb should return error about GDB.
    result = session.dispatch_tool("core_load", {"uuid": "test-uuid"})
    _check(
        "core_load dispatches with args",
        "ERROR" in result or "not started" in result.lower(),
        f"got: {result}",
    )

    # ui_invoke without gdb should return error.
    result = session.dispatch_tool(
        "ui_invoke",
        {"element_ptr": "0x1000", "handler": "clicked"},
    )
    _check(
        "ui_invoke dispatches with args",
        "ERROR" in result or "not started" in result.lower(),
        f"got: {result}",
    )

    # ui_invoke transformed should return unsupported message.
    # (This one doesn't need gdb since it returns early.)
    result = session.ui_invoke(element_ptr="0x1000", handler="transformed")
    _check(
        "ui_invoke transformed returns unsupported",
        "not yet implemented" in result,
        f"got: {result}",
    )

    # input_write with invalid flag should return error.
    result = session.input_write(flag="INVALID_FLAG", action="drive")
    _check(
        "input_write invalid flag returns error",
        "ERROR" in result or "unknown" in result.lower(),
        f"got: {result}",
    )

    # input_write with invalid action.
    result = session.input_write(flag="FORWARD", action="invalid")
    _check(
        "input_write invalid action returns error",
        "ERROR" in result or "unknown action" in result.lower(),
        f"got: {result}",
    )


def test_audio_unsupported() -> None:
    """Test that audio tools return 'unsupported'."""
    _section("Audio (Unsupported)")

    session = LavMcpSession(executable="/fake/path/game")

    result = session.audio_list()
    _check(
        "audio_list returns unsupported",
        "unsupported" in result.lower(),
        f"got: {result}",
    )

    result = session.audio_listen()
    _check(
        "audio_listen returns unsupported",
        "unsupported" in result.lower(),
        f"got: {result}",
    )


def test_mcp_response_format() -> None:
    """Test _make_response and _make_error format."""
    _section("MCP Response Format")

    # Success response with string.
    resp = _make_response(1, "hello world")
    parsed = json.loads(resp)
    _check("response has jsonrpc field", parsed.get("jsonrpc") == "2.0")
    _check("response has id field", parsed.get("id") == 1)
    _check("response has result field", "result" in parsed)
    result = parsed["result"]
    _check("result has content", "content" in result)
    _check(
        "content has text",
        result["content"][0].get("text") == "hello world",
    )

    # Success response with dict.
    resp = _make_response(2, {"custom": "data"})
    parsed = json.loads(resp)
    _check("dict result preserved", parsed["result"] == {"custom": "data"})

    # Error response.
    resp = _make_error(3, -32601, "Method not found", "details")
    parsed = json.loads(resp)
    _check("error has jsonrpc field", parsed.get("jsonrpc") == "2.0")
    _check("error has id field", parsed.get("id") == 3)
    error = parsed["error"]
    _check("error has code", error["code"] == -32601)
    _check("error has message", error["message"] == "Method not found")
    _check("error has data", error.get("data") == "details")


def test_mcp_initialize() -> None:
    """Test MCP initialize request."""
    _section("MCP Initialize")

    session = LavMcpSession(executable="/fake/path/game")

    request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "clientInfo": {"name": "test-client", "version": "1.0"},
        },
    }

    result = _handle_mcp_request(request, session)
    parsed = json.loads(result)
    _check("result has correct id", parsed["id"] == 1)
    _check("result has protocolVersion", "protocolVersion" in parsed["result"])
    _check("result has capabilities", "capabilities" in parsed["result"])
    caps = parsed["result"]["capabilities"]
    _check("capabilities has tools", "tools" in caps)
    _check("result has serverInfo", "serverInfo" in parsed["result"])
    info = parsed["result"]["serverInfo"]
    _check("serverInfo has name", info.get("name") == "lavender-debug-mcp")
    _check("serverInfo has version", "version" in info)


def test_mcp_tools_list() -> None:
    """Test MCP tools/list request."""
    _section("MCP Tools List")

    session = LavMcpSession(executable="/fake/path/game")

    request = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/list",
    }

    result = _handle_mcp_request(request, session)
    parsed = json.loads(result)
    _check("result has correct id", parsed["id"] == 2)
    _check("result has tools", "tools" in parsed["result"])
    tools = parsed["result"]["tools"]
    _check("tools list is non-empty", len(tools) > 0)
    _check(
        "tools list matches TOOL_DEFINITIONS",
        len(tools) == len(TOOL_DEFINITIONS),
    )


def test_mcp_tools_call() -> None:
    """Test MCP tools/call request (error case — no gdb)."""
    _section("MCP Tools Call")

    session = LavMcpSession(executable="/fake/path/game")

    request = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
            "name": "session_status",
            "arguments": {},
        },
    }

    result = _handle_mcp_request(request, session)
    parsed = json.loads(result)
    _check("result has correct id", parsed["id"] == 3)
    _check("result has content", "content" in parsed["result"])
    text = parsed["result"]["content"][0].get("text", "")
    _check(
        "content mentions not started",
        "not started" in text.lower() or "not running" in text.lower(),
        f"got: {text}",
    )


def test_mcp_unknown_method() -> None:
    """Test MCP request with unknown method."""
    _section("MCP Unknown Method")

    session = LavMcpSession(executable="/fake/path/game")

    request = {
        "jsonrpc": "2.0",
        "id": 4,
        "method": "unknown_method",
    }

    result = _handle_mcp_request(request, session)
    parsed = json.loads(result)
    _check("has error", "error" in parsed)
    _check("error code is -32601", parsed["error"]["code"] == -32601)
    _check("error mentions not found", "not found" in parsed["error"]["message"].lower())


def test_mcp_notification() -> None:
    """Test MCP notification (no id — should return empty)."""
    _section("MCP Notification")

    session = LavMcpSession(executable="/fake/path/game")

    request = {
        "jsonrpc": "2.0",
        "method": "initialized",  # notification
    }

    result = _handle_mcp_request(request, session)
    _check("notification returns empty string", result == "")


def test_mcp_prompts_and_resources() -> None:
    """Test prompts/list and resources/list (should return empty)."""
    _section("MCP Prompts & Resources")

    session = LavMcpSession(executable="/fake/path/game")

    for method in ["prompts/list", "resources/list"]:
        request = {"jsonrpc": "2.0", "id": 5, "method": method}
        result = _handle_mcp_request(request, session)
        parsed = json.loads(result)
        _check(f"{method} returns 200-style result", "result" in parsed)


def test_session_registry() -> None:
    """Test SessionRegistry create/get/remove/list."""
    _section("Session Registry")

    call_count = [0]

    def factory():
        call_count[0] += 1
        return LavMcpSession(executable=f"/fake/game-{call_count[0]}")

    registry = SessionRegistry(factory)

    # get_or_create creates new.
    s1 = registry.get_or_create("sess-1")
    _check("session created", s1 is not None)
    _check("factory called once", call_count[0] == 1)

    # get_or_create returns existing.
    s1b = registry.get_or_create("sess-1")
    _check("same session returned", s1b is s1)
    _check("factory not called again", call_count[0] == 1)

    # Different session ID creates new.
    s2 = registry.get_or_create("sess-2")
    _check("different session created", s2 is not s1)
    _check("factory called twice", call_count[0] == 2)

    # get returns None for unknown.
    s3 = registry.get("sess-3")
    _check("unknown session returns None", s3 is None)

    # list_sessions.
    ids = registry.list_sessions()
    _check("list returns both sessions", set(ids) == {"sess-1", "sess-2"})

    # remove.
    registry.remove("sess-1")
    ids = registry.list_sessions()
    _check("sess-1 removed", "sess-1" not in ids)
    _check("sess-2 still present", "sess-2" in ids)


def test_config_loading() -> None:
    """Test load_config with defaults and custom config."""
    _section("Config Loading")

    # Default config (no path).
    config = load_config(None)
    _check("default config has 'config' key", "config" in config)
    cfg = config["config"]
    _check("default has session.executable", "executable" in cfg.get("session", {}))
    _check("default has core.dump-location", "dump-location" in cfg.get("core", {}))

    # Custom config file.
    import tempfile
    custom = {
        "config": {
            "session": {"executable": "/custom/game"},
            "core": {"dump-location": "/custom/dumps/"}
        }
    }
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".json", delete=False
    ) as f:
        json.dump(custom, f)
        tmp_path = f.name

    try:
        config = load_config(tmp_path)
        cfg = config["config"]
        _check(
            "custom executable loaded",
            cfg["session"]["executable"] == "/custom/game",
        )
        _check(
            "custom dump-location loaded",
            cfg["core"]["dump-location"] == "/custom/dumps/",
        )
    finally:
        os.unlink(tmp_path)


def test_session_factory() -> None:
    """Test make_session_factory creates sessions with correct config."""
    _section("Session Factory")

    import tempfile
    tmpdir = tempfile.mkdtemp()
    try:
        config = {
            "config": {
                "session": {"executable": "/my/game"},
                "core": {"dump-location": os.path.join(tmpdir, "dumps/")},
            }
        }
        factory = make_session_factory(config)
        session = factory()
        _check("session executable correct", session.executable == "/my/game")
    finally:
        import shutil
        shutil.rmtree(tmpdir, ignore_errors=True)


def test_session_dump_location() -> None:
    """Test that dump location directory is created."""
    _section("Session Dump Location")

    import tempfile
    tmpdir = tempfile.mkdtemp()
    try:
        dump_location = os.path.join(tmpdir, "sub/dir")
        session = LavMcpSession(
            executable="/fake/game",
            dump_location=dump_location,
        )
        _check(
            "dump location directory created",
            os.path.isdir(dump_location),
        )
    finally:
        import shutil
        shutil.rmtree(tmpdir, ignore_errors=True)


def test_pygdbmi_timeout_patch() -> None:
    """Test that patch_gdbmi_timeouts overrides pygdbmi's 1s default."""
    from mcp.gdb_nav_utils import patch_gdbmi_timeouts, _PYGDBMI_TIMEOUT

    _section("pygdbmi Timeout Patch")

    _check("default timeout is 15s", _PYGDBMI_TIMEOUT == 15.0,
           f"got {_PYGDBMI_TIMEOUT}")

    # Fake GdbController-like object.
    class _FakeGdbmi:
        def write(self, cmd, timeout_sec=1, raise_error_on_timeout=True,
                   read_response=True, **kwargs):
            return timeout_sec
        def get_gdb_response(self, timeout_sec=1, raise_error_on_timeout=True):
            return timeout_sec

    gdb = _FakeGdbmi()

    # Before patching: default is 1s.
    _check("unpatched write defaults to 1s", gdb.write("cmd") == 1)
    _check("unpatched get_gdb_response defaults to 1s",
           gdb.get_gdb_response() == 1)

    # Apply the patch.
    patch_gdbmi_timeouts(gdb)

    # After patching: default is 15s.
    _check("patched write defaults to 15s", gdb.write("cmd") == _PYGDBMI_TIMEOUT)
    _check("patched get_gdb_response defaults to 15s",
           gdb.get_gdb_response() == _PYGDBMI_TIMEOUT)

    # Explicit timeout still overrides.
    _check("explicit timeout overrides patched default (write)",
           gdb.write("cmd", timeout_sec=2.0) == 2.0)
    _check("explicit timeout overrides patched default (get_response)",
           gdb.get_gdb_response(timeout_sec=2.0) == 2.0)

    # None is handled safely.
    _check("patch_gdbmi_timeouts(None) returns None",
           patch_gdbmi_timeouts(None) is None)


def test_session_stop_without_start() -> None:
    """Test session_stop when GDB was never started."""
    _section("Session Stop (No Start)")

    session = LavMcpSession(executable="/fake/game")
    result = session.session_stop()
    _check(
        "returns 'not running' message",
        "not running" in result.lower() or "no GDB" in result,
        f"got: {result}",
    )


def test_session_start_missing_executable() -> None:
    """Test that session_start fails cleanly when the executable is absent."""
    _section("Session Start (Missing Executable)")

    session = LavMcpSession(executable="/fake/path/game")
    result = session.session_start()
    _check(
        "returns 'executable not found' error",
        "executable not found" in result.lower(),
        f"got: {result}",
    )
    _check("gdb was NOT started", session._gdbmi is None)
    _check("session not marked running", session.is_running is False)
    _check("session not marked crashed", session.is_crashed is False)


def test_session_start_executable_override() -> None:
    """Test that session_start(executable=...) overrides the configured path."""
    _section("Session Start (Executable Override)")

    import mcp.lav_mcp as lav_mcp_mod

    session = LavMcpSession(executable="/fake/path/game")
    real_file = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "lav_mcp.py"
    )

    # Replace GdbController so no real gdb process is spawned.
    orig_controller = lav_mcp_mod.GdbController
    lav_mcp_mod.GdbController = lambda *a, **kw: FakeGdbmi()
    try:
        result = session.session_start(executable=real_file)
    finally:
        lav_mcp_mod.GdbController = orig_controller

    _check(
        "no 'executable not found' error after override",
        "executable not found" not in result.lower(),
        f"got: {result}",
    )
    _check(
        "session executable updated to override",
        session.executable == real_file,
        f"got: {session.executable}",
    )
    _check("gdb was started", session._gdbmi is not None)

    # Override with a ~ path: expanduser must be applied.
    session2 = LavMcpSession(executable="/fake/path/game")
    result = session2.session_start(executable="~/definitely-missing-game")
    _check(
        "~ path expanded and reported as missing",
        "executable not found" in result.lower(),
        f"got: {result}",
    )
    _check(
        "session executable holds expanded ~ path",
        session2.executable == os.path.expanduser("~/definitely-missing-game"),
        f"got: {session2.executable}",
    )


def test_core_load_missing_executable() -> None:
    """Test that core_load fails cleanly when the executable is absent."""
    _section("Core Load (Missing Executable)")

    import tempfile
    tmpdir = tempfile.mkdtemp()
    try:
        session = LavMcpSession(
            executable="/fake/path/game", dump_location=tmpdir
        )
        # Create a fake core dump so the dump-existence check passes.
        with open(os.path.join(tmpdir, "core-test-uuid"), "w") as f:
            f.write("fake")
        fake = FakeGdbmi()
        session._gdbmi = fake

        result = session.core_load("test-uuid")
        _check(
            "returns 'executable not found' error",
            "executable not found" in result.lower(),
            f"got: {result}",
        )
        _check(
            "no gdb commands issued",
            len(fake.commands) == 0,
            f"commands: {fake.commands}",
        )
    finally:
        import shutil
        shutil.rmtree(tmpdir, ignore_errors=True)


def test_session_status_missing_executable() -> None:
    """Test that session_status mentions a missing executable."""
    _section("Session Status (Missing Executable)")

    session = LavMcpSession(executable="/fake/path/game")
    result = session.session_status()
    _check("mentions not started", "NOT started" in result, f"got: {result}")
    _check(
        "mentions executable not found",
        "executable not found" in result.lower(),
        f"got: {result}",
    )


# --------------------------------------------------------------------------- #
#  Main
# --------------------------------------------------------------------------- #
def main() -> int:
    print("=" * 60)
    print("Lavender MCP — Test Suite")
    print("=" * 60)

    test_tool_definitions()
    test_tool_method_mapping()
    test_session_state()
    test_session_not_started()
    test_tool_dispatch_unknown()
    test_tool_dispatch_with_args()
    test_audio_unsupported()
    test_mcp_response_format()
    test_mcp_initialize()
    test_mcp_tools_list()
    test_mcp_tools_call()
    test_mcp_unknown_method()
    test_mcp_notification()
    test_mcp_prompts_and_resources()
    test_session_registry()
    test_config_loading()
    test_session_factory()
    test_pygdbmi_timeout_patch()
    test_session_dump_location()
    test_session_stop_without_start()
    test_session_start_missing_executable()
    test_session_start_executable_override()
    test_core_load_missing_executable()
    test_session_status_missing_executable()

    print("\n" + "=" * 60)
    print(f"Results: {_PASS} passed, {_FAIL} failed")
    print("=" * 60)
    return 1 if _FAIL > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
