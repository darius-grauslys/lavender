"""Tests for Layer 4 (layer_lav_init.py)."""

import os
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, patch

# Setup import paths
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_LAYERED_ROOT = os.path.abspath(os.path.join(_THIS_DIR, "..", ".."))
_REPO_ROOT = os.path.abspath(os.path.join(_LAYERED_ROOT, ".."))
sys.path.insert(0, _REPO_ROOT)
sys.path.insert(0, _LAYERED_ROOT)

from mcp_layered.layer_lav_init import (
    LavSession,
    create_session,
    default_session,
)
from mcp_layered.layer_lav_config import LavConfig
from mcp_layered.layer_lav_cmd import register_driver, unregister_driver
from mcp_layered.layer_pygdbmi import GDBSession


class TestLavSessionCreation(unittest.TestCase):
    """Test LavSession creation and initialization."""

    def test_default_config(self):
        """LavSession() with no args uses default config."""
        with patch("mcp_layered.layer_lav_init.GDBSession") as mock_gdb_cls:
            mock_gdb = MagicMock()
            mock_gdb.is_closed = False
            mock_gdb_cls.return_value = mock_gdb

            session = LavSession()
            self.assertIsInstance(session.config, LavConfig)
            self.assertEqual(session.config.executable, "/home/shalidor/Projects/Projects__Lavender/AncientsGame/build/sdl/AncientsGame")
            # Should have created a GDBSession
            self.assertIs(session.gdb, mock_gdb)

    def test_custom_config(self):
        """LavSession with custom config uses it."""
        with patch("mcp_layered.layer_lav_init.GDBSession") as mock_gdb_cls:
            mock_gdb = MagicMock()
            mock_gdb.is_closed = False
            mock_gdb_cls.return_value = mock_gdb

            config = LavConfig(executable="/custom/game")
            session = LavSession(config=config)
            self.assertEqual(session.config.executable, "/custom/game")

    def test_custom_gdb_session(self):
        """LavSession with custom GDB session uses it."""
        mock_gdb = MagicMock()
        mock_gdb.is_closed = False
        config = LavConfig()

        session = LavSession(config=config, gdb=mock_gdb)
        self.assertIs(session.gdb, mock_gdb)


class TestLavSessionInvoke(unittest.TestCase):
    """Test LavSession.invoke() routing."""

    def setUp(self):
        self.mock_gdb = MagicMock()
        self.mock_gdb.is_closed = True  # avoid close errors
        self.config = LavConfig()

        # Register a test driver
        self._test_results = []
        def test_driver(gdb, config, kwargs):
            self._test_results.append((gdb, config, kwargs))
            return "test_result"
        self._original_driver = None
        try:
            self._original_driver = __import__(
                "mcp_layered.layer_lav_cmd", fromlist=["get_driver"]
            ).get_driver("test_invoke_cmd")
        except:
            pass
        register_driver("test_invoke_cmd", test_driver)

        self.session = LavSession(config=self.config, gdb=self.mock_gdb)

    def tearDown(self):
        unregister_driver("test_invoke_cmd")

    def test_invoke_routes_to_driver(self):
        """invoke() routes to the correct driver."""
        result = self.session.invoke("test_invoke_cmd", arg1="value")
        self.assertEqual(result, "test_result")
        self.assertEqual(len(self._test_results), 1)
        gdb, config, kwargs = self._test_results[0]
        self.assertIs(gdb, self.mock_gdb)
        self.assertIs(config, self.config)
        self.assertEqual(kwargs, {"arg1": "value"})

    def test_invoke_unknown_alias_raises(self):
        """invoke() raises CommandError for unknown alias."""
        from mcp_layered.layer_lav_cmd import CommandError
        with self.assertRaises(CommandError):
            self.session.invoke("unknown_command")


class TestLavSessionLifecycle(unittest.TestCase):
    """Test session lifecycle methods."""

    def setUp(self):
        self.mock_gdb = MagicMock()
        self.mock_gdb.is_closed = False
        self.config = LavConfig()
        self.session = LavSession(config=self.config, gdb=self.mock_gdb)

    def test_is_started_false_initially(self):
        """Session is not started initially."""
        self.assertFalse(self.session.is_started)

    def test_gdb_path_property(self):
        """gdb_path returns the GDB path from the gdb session."""
        self.mock_gdb.gdb_path = "/usr/bin/gdb"
        self.assertEqual(self.session.gdb_path, "/usr/bin/gdb")

    def test_executable_property(self):
        """executable returns the config executable."""
        self.assertEqual(self.session.executable, self.config.executable)

    def test_get_config(self):
        """get_config returns the config."""
        self.assertIs(self.session.get_config(), self.config)

    def test_get_gdb(self):
        """get_gdb returns the gdb session."""
        self.assertIs(self.session.get_gdb(), self.mock_gdb)

    def test_close_closes_gdb(self):
        """close() closes the GDB session."""
        self.mock_gdb.is_closed = False
        self.session.close()
        self.mock_gdb.close.assert_called_once()
        self.assertFalse(self.session.is_started)


class TestCreateSession(unittest.TestCase):
    """Test create_session() factory function."""

    def test_create_session_with_defaults(self):
        """create_session() with no args creates a working session."""
        with patch("mcp_layered.layer_lav_init.GDBSession") as mock_gdb_cls:
            mock_gdb = MagicMock()
            mock_gdb.is_closed = True
            mock_gdb_cls.return_value = mock_gdb

            session = create_session()
            self.assertIsInstance(session, LavSession)
            self.assertIsInstance(session.config, LavConfig)

    def test_create_session_with_config_path(self):
        """create_session() with config path loads from file."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as f:
            f.write('{"executable": "/custom/game"}')
            config_path = f.name
        try:
            session = create_session(config_path=config_path)
            self.assertEqual(session.config.executable, "/custom/game")
        finally:
            os.unlink(config_path)

    def test_create_session_with_executable_override(self):
        """create_session() executable param overrides config."""
        with patch("mcp_layered.layer_lav_init.GDBSession") as mock_gdb_cls:
            mock_gdb = MagicMock()
            mock_gdb.is_closed = True
            mock_gdb_cls.return_value = mock_gdb

            session = create_session(executable="/override/game")
            self.assertEqual(session.config.executable, "/override/game")

    def test_create_session_with_custom_gdb(self):
        """create_session() accepts a custom GDBSession."""
        mock_gdb = MagicMock()
        mock_gdb.is_closed = True
        session = create_session(gdb=mock_gdb)
        self.assertIs(session.gdb, mock_gdb)


class TestDefaultSession(unittest.TestCase):
    """Test default_session() factory function."""

    def test_default_session_returns_lav_session(self):
        """default_session() returns a LavSession instance."""
        with patch("mcp_layered.layer_lav_init.GDBSession") as mock_gdb_cls:
            mock_gdb = MagicMock()
            mock_gdb.is_closed = True
            mock_gdb_cls.return_value = mock_gdb

            session = default_session()
            self.assertIsInstance(session, LavSession)


if __name__ == "__main__":
    unittest.main(verbosity=2)
