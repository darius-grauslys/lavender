"""Tests for Layer 3 (layer_lav_cmd.py)."""

import os
import sys
import unittest
from unittest.mock import MagicMock

# Setup import paths
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_LAYERED_ROOT = os.path.abspath(os.path.join(_THIS_DIR, "..", ".."))
_REPO_ROOT = os.path.abspath(os.path.join(_LAYERED_ROOT, ".."))
sys.path.insert(0, _REPO_ROOT)
sys.path.insert(0, _LAYERED_ROOT)

from mcp_layered.layer_lav_cmd import (
    invoke,
    register_driver,
    unregister_driver,
    get_driver,
    list_drivers,
    get_command_alias,
    get_required_kwargs,
    COMMAND_ALIASES,
    CommandError,
)
from mcp_layered.layer_lav_config import LavConfig
from mcp_layered.layer_pygdbmi import GDBSession


class TestDriverRegistry(unittest.TestCase):
    """Test the scanner driver registry."""

    def setUp(self):
        """Clean up any test drivers from previous tests."""
        # Save current state
        self._saved_drivers = {}
        for alias in list_drivers():
            self._saved_drivers[alias] = get_driver(alias)
        # Clear for clean test
        for alias in list(list_drivers()):
            unregister_driver(alias)

    def tearDown(self):
        """Restore original drivers."""
        for alias in list(list_drivers()):
            unregister_driver(alias)
        for alias, driver in self._saved_drivers.items():
            register_driver(alias, driver)

    def test_register_and_get_driver(self):
        """register_driver + get_driver work correctly."""
        def my_driver(gdb, config, kwargs):
            return "result"
        register_driver("test_cmd", my_driver)
        self.assertIs(get_driver("test_cmd"), my_driver)

    def test_get_unknown_driver_returns_none(self):
        """get_driver returns None for unknown alias."""
        self.assertIsNone(get_driver("nonexistent"))

    def test_unregister_driver(self):
        """unregister_driver removes a driver."""
        def my_driver(gdb, config, kwargs):
            return "result"
        register_driver("test_cmd", my_driver)
        unregister_driver("test_cmd")
        self.assertIsNone(get_driver("test_cmd"))

    def test_unregister_unknown_driver_no_error(self):
        """unregister_driver doesn't error for unknown alias."""
        unregister_driver("nonexistent")  # Should not raise

    def test_list_drivers(self):
        """list_drivers returns all registered aliases."""
        def d1(gdb, config, kwargs): return "1"
        def d2(gdb, config, kwargs): return "2"
        register_driver("cmd1", d1)
        register_driver("cmd2", d2)
        drivers = list_drivers()
        self.assertIn("cmd1", drivers)
        self.assertIn("cmd2", drivers)
        self.assertEqual(len(drivers), 2)

    def test_register_driver_overrides(self):
        """Registering a driver with an existing alias overrides it."""
        def d1(gdb, config, kwargs): return "1"
        def d2(gdb, config, kwargs): return "2"
        register_driver("cmd", d1)
        register_driver("cmd", d2)
        self.assertIs(get_driver("cmd"), d2)


class TestInvoke(unittest.TestCase):
    """Test the invoke() router function."""

    def setUp(self):
        self._saved_drivers = {}
        for alias in list_drivers():
            self._saved_drivers[alias] = get_driver(alias)
        for alias in list(list_drivers()):
            unregister_driver(alias)

        self.mock_gdb = MagicMock(spec=GDBSession)
        self.config = LavConfig()

    def tearDown(self):
        for alias in list(list_drivers()):
            unregister_driver(alias)
        for alias, driver in self._saved_drivers.items():
            register_driver(alias, driver)

    def test_invoke_known_driver(self):
        """invoke() calls the driver and returns its result."""
        def my_driver(gdb, config, kwargs):
            return f"called with {kwargs}"
        register_driver("test_cmd", my_driver)

        result = invoke("test_cmd", self.mock_gdb, self.config, arg1="value")
        self.assertEqual(result, "called with {'arg1': 'value'}")

    def test_invoke_unknown_driver_raises(self):
        """invoke() raises CommandError for unknown alias."""
        with self.assertRaises(CommandError) as ctx:
            invoke("unknown", self.mock_gdb, self.config)
        self.assertIn("Unknown scanner driver alias", str(ctx.exception))

    def test_invoke_driver_exception_wrapped(self):
        """invoke() wraps driver exceptions in CommandError."""
        def failing_driver(gdb, config, kwargs):
            raise ValueError("something went wrong")
        register_driver("failing_cmd", failing_driver)

        with self.assertRaises(CommandError) as ctx:
            invoke("failing_cmd", self.mock_gdb, self.config)
        self.assertIn("something went wrong", str(ctx.exception))

    def test_invoke_command_error_not_wrapped(self):
        """invoke() does not re-wrap CommandError instances."""
        def bad_kwargs_driver(gdb, config, kwargs):
            raise CommandError("invalid argument")
        register_driver("bad_cmd", bad_kwargs_driver)

        with self.assertRaises(CommandError) as ctx:
            invoke("bad_cmd", self.mock_gdb, self.config, bad="arg")
        self.assertIn("invalid argument", str(ctx.exception))

    def test_invoke_passes_gdb_and_config(self):
        """invoke() passes gdb and config to the driver."""
        received = {}
        def capturing_driver(gdb, config, kwargs):
            received['gdb'] = gdb
            received['config'] = config
            received['kwargs'] = kwargs
            return "captured"
        register_driver("capture_cmd", capturing_driver)

        invoke("capture_cmd", self.mock_gdb, self.config, key="value")
        self.assertIs(received['gdb'], self.mock_gdb)
        self.assertIs(received['config'], self.config)
        self.assertEqual(received['kwargs'], {'key': 'value'})


class TestCommandAliases(unittest.TestCase):
    """Test command alias mapping."""

    def test_known_aliases(self):
        """Known MCP tool names map to command aliases."""
        self.assertEqual(get_command_alias("step"), "step")
        self.assertEqual(get_command_alias("ui_list"), "ui_list")
        self.assertEqual(get_command_alias("session_start"), "session_start")

    def test_unknown_alias_returns_none(self):
        """Unknown MCP tool names return None."""
        self.assertIsNone(get_command_alias("unknown_tool"))

    def test_command_aliases_dict_has_all_tools(self):
        """COMMAND_ALIASES contains all expected tool names."""
        expected = [
            "session_start", "session_status", "session_stop",
            "step", "navigate_source",
            "core_dump", "core_load", "core_reset",
            "process_list", "process_watch",
            "input_read", "input_write",
            "ui_list", "ui_invoke",
            "graphics_screenshot",
            "audio_list", "audio_listen",
        ]
        for tool_name in expected:
            self.assertIn(tool_name, COMMAND_ALIASES,
                         f"Missing command alias: {tool_name}")

    def test_required_kwargs_empty_by_default(self):
        """get_required_kwargs returns empty list by default."""
        self.assertEqual(get_required_kwargs("any_cmd"), [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
