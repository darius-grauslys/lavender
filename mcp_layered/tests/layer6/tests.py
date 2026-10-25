"""Tests for Layer 6 (layer_lav_mcp_server.py)."""

import os
import sys
import unittest
from unittest.mock import MagicMock, patch

# Setup import paths
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_LAYERED_ROOT = os.path.abspath(os.path.join(_THIS_DIR, "..", ".."))
_REPO_ROOT = os.path.abspath(os.path.join(_LAYERED_ROOT, ".."))
sys.path.insert(0, _REPO_ROOT)
sys.path.insert(0, _LAYERED_ROOT)

from mcp_layered.layer_lav_mcp_server import (
    SessionRegistry,
    SessionManager,
    _handle_mcp_request,
    _make_response,
    _make_error,
)
from mcp_layered.layer_lav_init import (
    LavSession,
    _register_builtin_drivers,
    _executable_missing_message,
)
from mcp_layered.layer_lav_cmd import (
    register_driver,
    unregister_driver,
    get_driver,
)


class TestSessionRegistry(unittest.TestCase):
    """Test the SessionRegistry class."""

    def setUp(self):
        self.registry = SessionRegistry()

    def tearDown(self):
        self.registry.clear()

    def test_create_session(self):
        """create() returns a session ID and stores the session."""
        with patch("mcp_layered.layer_lav_mcp_server.create_session") as mock_create:
            mock_session = MagicMock()
            mock_create.return_value = mock_session

            session_id = self.registry.create()

            self.assertIsInstance(session_id, str)
            self.assertIs(self.registry.get(session_id), mock_session)

    def test_create_with_existing_session(self):
        """create() stores an existing LavSession."""
        mock_session = MagicMock()
        session_id = self.registry.create(session=mock_session)
        self.assertIs(self.registry.get(session_id), mock_session)

    def test_get_unknown_returns_none(self):
        """get() returns None for unknown session ID."""
        self.assertIsNone(self.registry.get("nonexistent"))

    def test_get_or_create_existing(self):
        """get_or_create() returns existing session if ID matches."""
        mock_session = MagicMock()
        session_id = self.registry.create(session=mock_session)

        returned_id, returned_session = self.registry.get_or_create(session_id)
        self.assertEqual(returned_id, session_id)
        self.assertIs(returned_session, mock_session)

    def test_get_or_create_new(self):
        """get_or_create() creates new session when ID doesn't exist."""
        with patch("mcp_layered.layer_lav_mcp_server.create_session") as mock_create:
            mock_session = MagicMock()
            mock_create.return_value = mock_session

            session_id, session = self.registry.get_or_create("nonexistent")
            self.assertIsInstance(session_id, str)
            self.assertIs(session, mock_session)

    def test_remove_session(self):
        """remove() closes and removes a session."""
        mock_session = MagicMock()
        session_id = self.registry.create(session=mock_session)

        result = self.registry.remove(session_id)
        self.assertTrue(result)
        self.assertIsNone(self.registry.get(session_id))
        mock_session.close.assert_called_once()

    def test_remove_unknown_returns_false(self):
        """remove() returns False for unknown session ID."""
        self.assertFalse(self.registry.remove("nonexistent"))

    def test_list_ids(self):
        """list_ids() returns all session IDs."""
        mock1 = MagicMock()
        mock2 = MagicMock()
        id1 = self.registry.create(session=mock1)
        id2 = self.registry.create(session=mock2)

        ids = self.registry.list_ids()
        self.assertIn(id1, ids)
        self.assertIn(id2, ids)
        self.assertEqual(len(ids), 2)

    def test_clear(self):
        """clear() closes all sessions and returns count."""
        mock1 = MagicMock()
        mock2 = MagicMock()
        self.registry.create(session=mock1)
        self.registry.create(session=mock2)

        count = self.registry.clear()
        self.assertEqual(count, 2)
        self.assertEqual(self.registry.count, 0)
        mock1.close.assert_called_once()
        mock2.close.assert_called_once()

    def test_count_property(self):
        """count returns the number of active sessions."""
        self.assertEqual(self.registry.count, 0)
        mock1 = MagicMock()
        self.registry.create(session=mock1)
        self.assertEqual(self.registry.count, 1)

    def test_thread_safety(self):
        """Multiple threads can create sessions concurrently."""
        import threading

        with patch("mcp_layered.layer_lav_mcp_server.create_session") as mock_create:
            mock_create.return_value = MagicMock()
            errors = []

            def create_many():
                try:
                    for _ in range(10):
                        self.registry.create()
                except Exception as e:
                    errors.append(e)

            threads = [threading.Thread(target=create_many) for _ in range(5)]
            for t in threads:
                t.start()
            for t in threads:
                t.join()

            self.assertEqual(len(errors), 0)
            self.assertEqual(self.registry.count, 50)


class TestSessionManager(unittest.TestCase):
    """Test the SessionManager class."""

    def tearDown(self):
        # Clean up any test drivers
        for alias in ["test_cmd"]:
            if __import__("mcp_layered.layer_lav_cmd", fromlist=["get_driver"]).get_driver("test_cmd"):
                unregister_driver("test_cmd")

    def test_multi_session_mode(self):
        """SessionManager in multi-session mode creates per-session adapters."""
        with patch("mcp_layered.layer_lav_mcp_server.create_session") as mock_create:
            mock_session = MagicMock()
            mock_session.invoke.return_value = "result"
            mock_create.return_value = mock_session

            manager = SessionManager(use_single_session=False)
            adapter = manager.create_session()

            from mcp_layered.layer_lav_mcp import MCPAdapter
            self.assertIsInstance(adapter, MCPAdapter)
            manager.close()

    def test_single_session_mode(self):
        """SessionManager in single-session mode shares one session."""
        with patch("mcp_layered.layer_lav_mcp_server.create_session") as mock_create:
            mock_session = MagicMock()
            mock_session.invoke.return_value = "result"
            mock_create.return_value = mock_session

            manager = SessionManager(use_single_session=True)

            adapter1 = manager.create_session()
            adapter2 = manager.create_session()

            # Should return the same adapter for single-session mode
            self.assertIs(adapter1, adapter2)
            manager.close()

    def test_dispatch_tool_single_session(self):
        """dispatch_tool works in single-session mode."""
        def test_driver(gdb, config, kwargs):
            return "test_result"
        register_driver("session_status", test_driver)

        with patch("mcp_layered.layer_lav_mcp_server.create_session") as mock_create:
            mock_session = MagicMock(spec=LavSession)

            def mock_invoke(alias, **kwargs):
                return test_driver(None, None, kwargs)
            mock_session.invoke = mock_invoke
            mock_create.return_value = mock_session

            manager = SessionManager(use_single_session=True)
            adapter = manager.create_session()

            result = manager.dispatch_tool(None, "session_status")
            self.assertEqual(result, "test_result")
            manager.close()

    def test_dispatch_tool_multi_session(self):
        """dispatch_tool works in multi-session mode with session_id."""
        def test_driver(gdb, config, kwargs):
            return "result"
        register_driver("session_status", test_driver)

        with patch("mcp_layered.layer_lav_mcp_server.create_session") as mock_create:
            mock_session = MagicMock(spec=LavSession)

            def mock_invoke(alias, **kwargs):
                return test_driver(None, None, kwargs)
            mock_session.invoke = mock_invoke
            mock_create.return_value = mock_session

            manager = SessionManager(use_single_session=False)
            adapter = manager.create_session()

            # Get the session ID from the registry
            session_id = list(manager.registry._sessions.keys())[0]
            result = manager.dispatch_tool(session_id, "session_status")
            self.assertEqual(result, "result")
            manager.close()

    def test_dispatch_no_session_raises(self):
        """dispatch_tool raises when no session is found."""
        manager = SessionManager(use_single_session=False)
        with self.assertRaises(ValueError):
            manager.dispatch_tool(None, "test_cmd")
        manager.close()

    def test_list_tools(self):
        """list_tools returns all MCP tool definitions."""
        with patch("mcp_layered.layer_lav_mcp_server.create_session"):
            manager = SessionManager(use_single_session=True)
            tools = manager.list_tools()
            self.assertGreater(len(tools), 0)
            self.assertIn("name", tools[0])
            manager.close()

    def test_close(self):
        """close() frees all resources."""
        with patch("mcp_layered.layer_lav_mcp_server.create_session") as mock_create:
            mock_session = MagicMock()
            mock_create.return_value = mock_session

            manager = SessionManager(use_single_session=True)
            manager.close()

            self.assertIsNone(manager._single_session_id)
            self.assertIsNone(manager._single_adapter)

    def test_close_session(self):
        """close_session() removes a specific session."""
        with patch("mcp_layered.layer_lav_mcp_server.create_session") as mock_create:
            mock_session = MagicMock()
            mock_create.return_value = mock_session

            manager = SessionManager(use_single_session=False)
            adapter = manager.create_session()
            session_id = list(manager.registry._sessions.keys())[0]

            result = manager.close_session(session_id)
            self.assertTrue(result)
            self.assertEqual(manager.registry.count, 0)
            manager.close()


class TestSessionManagerContextManager(unittest.TestCase):
    """Test SessionManager as a context manager."""

    def test_context_manager(self):
        """SessionManager can be used as a context manager."""
        with patch("mcp_layered.layer_lav_mcp_server.create_session") as mock_create:
            mock_session = MagicMock()
            mock_create.return_value = mock_session

            with SessionManager(use_single_session=True) as manager:
                adapter = manager.create_session()
                self.assertIsNotNone(adapter)

            # After context exit, sessions should be cleaned up
            self.assertIsNone(manager._single_adapter)


class TestExecutableMissingMessage(unittest.TestCase):
    """Test the _executable_missing_message helper."""

    def test_existing_path_returns_none(self):
        """An existing path returns None (no error)."""
        self.assertIsNone(_executable_missing_message(__file__))

    def test_missing_path_returns_message(self):
        """A missing path returns a clear error message."""
        msg = _executable_missing_message("/fake/path/game")
        self.assertIsNotNone(msg)
        self.assertIn("executable not found", msg)
        self.assertIn("/fake/path/game", msg)


class TestSessionStartExecutableDriver(unittest.TestCase):
    """Test the session_start/status drivers' executable handling."""

    def setUp(self):
        # Register the real builtin drivers (no GDB process is spawned).
        _register_builtin_drivers()
        self.start_driver = get_driver("session_start")
        self.status_driver = get_driver("session_status")
        self.assertIsNotNone(self.start_driver)
        self.assertIsNotNone(self.status_driver)
        self._reset_shared_state()

    def tearDown(self):
        self._reset_shared_state()

    @staticmethod
    def _reset_shared_state() -> None:
        # The builtin drivers share one module-level SessionState object;
        # reset the run flags so tests are independent of execution order.
        from mcp_layered import layer_lav_init
        state = layer_lav_init._SESSION_STATE
        if state is not None:
            state.running = False
            state.halted = False
            state.crashed = False

    def _config(self, executable: str):
        from mcp_layered.layer_lav_config import default_config
        config = default_config()
        config.executable = executable
        return config

    def test_start_missing_executable_fails_cleanly(self):
        """session_start with a missing executable returns a clean error."""
        import os
        config = self._config("/fake/path/game")
        gdb = MagicMock(is_closed=False)
        result = self.start_driver(gdb, config, {})
        self.assertIn("executable not found", result)
        self.assertIn("/fake/path/game", result)
        # No GDB commands were issued.
        self.assertFalse(gdb.write.called)

    def test_start_executable_override(self):
        """session_start(executable=...) overrides the configured path."""
        config = self._config("/fake/path/game")
        gdb = MagicMock(is_closed=False)
        result = self.start_driver(gdb, config, {"executable": __file__})
        self.assertNotIn("executable not found", result)
        self.assertEqual(config.executable, __file__)
        self.assertIn("Game started under GDB", result)

    def test_start_executable_tilde_expansion(self):
        """~ in the executable override is expanded."""
        import os
        config = self._config("/fake/path/game")
        gdb = MagicMock(is_closed=False)
        self.start_driver(gdb, config, {"executable": "~/definitely-missing-game"})
        self.assertEqual(
            config.executable,
            os.path.expanduser("~/definitely-missing-game"),
        )

    def test_status_hints_at_missing_executable(self):
        """session_status mentions a missing executable when not started."""
        config = self._config("/fake/path/game")
        gdb = MagicMock(is_closed=False)
        result = self.status_driver(gdb, config, {})
        self.assertIn("NOT started", result)
        self.assertIn("executable not found", result)


class TestStdioRequestHandler(unittest.TestCase):
    """Test _handle_mcp_request (the stdio JSON-RPC router)."""

    def setUp(self):
        self.manager = MagicMock(spec=SessionManager)
        self.manager.list_tools.return_value = [{"name": "session_start"}]
        self.manager.dispatch_tool.return_value = "ok"

    def test_initialize(self):
        response = _handle_mcp_request(
            {"jsonrpc": "2.0", "id": 1, "method": "initialize",
             "params": {}},
            self.manager,
        )
        import json
        parsed = json.loads(response)
        self.assertEqual(parsed["id"], 1)
        self.assertEqual(parsed["result"]["serverInfo"]["name"],
                         "lavender-debug-mcp")
        self.assertIn("tools", parsed["result"]["capabilities"])

    def test_tools_list(self):
        import json
        response = _handle_mcp_request(
            {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}},
            self.manager,
        )
        parsed = json.loads(response)
        self.assertEqual(parsed["result"]["tools"],
                         [{"name": "session_start"}])

    def test_tools_call(self):
        import json
        response = _handle_mcp_request(
            {"jsonrpc": "2.0", "id": 3, "method": "tools/call",
             "params": {"name": "session_start", "arguments": {}}},
            self.manager,
        )
        parsed = json.loads(response)
        self.assertEqual(parsed["result"]["content"][0]["text"], "ok")
        self.manager.dispatch_tool.assert_called_once_with(
            None, "session_start", {})

    def test_tools_call_error(self):
        import json
        self.manager.dispatch_tool.side_effect = RuntimeError("boom")
        response = _handle_mcp_request(
            {"jsonrpc": "2.0", "id": 4, "method": "tools/call",
             "params": {"name": "session_start", "arguments": {}}},
            self.manager,
        )
        parsed = json.loads(response)
        self.assertEqual(parsed["error"]["code"], -32000)

    def test_unknown_method(self):
        import json
        response = _handle_mcp_request(
            {"jsonrpc": "2.0", "id": 5, "method": "bogus"},
            self.manager,
        )
        parsed = json.loads(response)
        self.assertEqual(parsed["error"]["code"], -32601)

    def test_notification_returns_empty(self):
        response = _handle_mcp_request(
            {"jsonrpc": "2.0", "method": "initialized"},
            self.manager,
        )
        self.assertEqual(response, "")


class TestStdioEndToEnd(unittest.TestCase):
    """Drive the real entry point as a subprocess (stdio MCP protocol)."""

    def _run_server(self, requests: list) -> list[dict]:
        import json
        import subprocess
        server_cmd = [
            sys.executable, "-m", "mcp_layered.layer_lav_mcp_server",
            "--stdio",
            "-e", "/fake/path/game",
        ]
        stdin = "".join(json.dumps(r) + "\n" for r in requests)
        proc = subprocess.run(
            server_cmd,
            input=stdin,
            capture_output=True,
            text=True,
            timeout=90,
            cwd=_REPO_ROOT,
        )
        self.assertEqual(
            proc.returncode, 0,
            f"server exited {proc.returncode}; stderr: {proc.stderr[-2000:]}",
        )
        return [json.loads(line) for line in proc.stdout.splitlines() if line]

    def test_stdio_handshake_and_executable_handling(self):
        responses = self._run_server([
            {"jsonrpc": "2.0", "id": 1, "method": "initialize",
             "params": {"protocolVersion": "2024-11-05", "capabilities": {},
                        "clientInfo": {"name": "test", "version": "0"}}},
            {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}},
            {"jsonrpc": "2.0", "id": 3, "method": "tools/call",
             "params": {"name": "session_start", "arguments": {}}},
            {"jsonrpc": "2.0", "id": 4, "method": "tools/call",
             "params": {"name": "session_start",
                        "arguments": {"executable": "/bin/true"}}},
            {"jsonrpc": "2.0", "id": 5, "method": "tools/call",
             "params": {"name": "session_stop", "arguments": {}}},
        ])
        by_id = {r["id"]: r for r in responses}

        # 1) initialize succeeds despite the missing -e executable.
        self.assertIn("serverInfo", by_id[1]["result"])

        # 2) tools/list exposes the executable override argument.
        tools = {t["name"]: t for t in by_id[2]["result"]["tools"]}
        self.assertIn("executable",
                      tools["session_start"]["inputSchema"]["properties"])

        # 3) session_start with the missing executable fails cleanly.
        text3 = by_id[3]["result"]["content"][0]["text"]
        self.assertIn("executable not found", text3)

        # 4) session_start(executable=...) overrides and starts the game.
        text4 = by_id[4]["result"]["content"][0]["text"]
        self.assertIn("Game started under GDB", text4)
        self.assertIn("/bin/true", text4)

        # 5) session_stop cleans up.
        text5 = by_id[5]["result"]["content"][0]["text"]
        self.assertIn("stopped", text5)


class TestMainArgParsing(unittest.TestCase):
    """Test main() CLI argument handling."""

    def test_requires_stdio(self):
        """main() without --stdio exits with an argparse error."""
        from mcp_layered.layer_lav_mcp_server import main
        with patch("sys.argv", ["layer_lav_mcp_server"]):
            with self.assertRaises(SystemExit):
                main()

    def test_rejects_unknown_flag(self):
        """main() rejects unknown flags."""
        from mcp_layered.layer_lav_mcp_server import main
        with patch("sys.argv", ["layer_lav_mcp_server", "--nope"]):
            with self.assertRaises(SystemExit):
                main()


if __name__ == "__main__":
    unittest.main(verbosity=2)
