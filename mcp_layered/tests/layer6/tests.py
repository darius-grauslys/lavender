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

from mcp_layered.layer_lav_mcp_server import SessionRegistry, SessionManager
from mcp_layered.layer_lav_init import LavSession
from mcp_layered.layer_lav_cmd import register_driver, unregister_driver


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


if __name__ == "__main__":
    unittest.main(verbosity=2)
