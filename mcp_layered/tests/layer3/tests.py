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
    parse_selector,
    select_from,
    resolve_value,
    _flatten_ui_elements,
)
from mcp_layered.layer_lav_config import LavConfig
from mcp_layered.layer_pygdbmi import GDBSession
from mcp_layered.verify_cli import split_commands, run_script


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


class _FakeGdb:
    """Minimal stand-in for GDBSession: only needs a settable _ui_cache."""
    pass


def _ui_cache_with(elements):
    """Build a ui_list-shaped cache from a list of (ptr, kind) tuples."""
    ui_elements = {ptr: {"uuid": "0xdeadbeef", "kind": kind}
                   for ptr, kind in elements}
    return {"ui_managers": {"0x1000": {
        "uuid": "0x1",
        "quantity_of__ui_elements": len(ui_elements),
        "ui_elements": ui_elements,
    }}}


class TestSelectorParse(unittest.TestCase):
    """parse_selector: `[...]` body -> dict."""

    def test_type_and_n(self):
        self.assertEqual(parse_selector("type=*Button,n=2"),
                         {"type": "*Button", "n": 2})

    def test_idx(self):
        self.assertEqual(parse_selector("idx=2"), {"idx": 2})

    def test_type_only(self):
        self.assertEqual(parse_selector("type=*Button"), {"type": "*Button"})

    def test_bad_n_becomes_none(self):
        self.assertIsNone(parse_selector("n=abc")["n"])


class TestSelectFrom(unittest.TestCase):
    """select_from: apply a selector to a flat item list."""

    def setUp(self):
        self.items = [
            {"ptr": "0x1", "kind": "UI_Element_Kind__Text"},
            {"ptr": "0x2", "kind": "UI_Element_Kind__Button"},
            {"ptr": "0x3", "kind": "UI_Element_Kind__Button"},
            {"ptr": "0x4", "kind": "UI_Element_Kind__Slider"},
        ]

    def test_type_n_first(self):
        self.assertEqual(select_from(self.items, {"type": "*Button", "n": 1})["ptr"], "0x2")

    def test_type_n_second(self):
        self.assertEqual(select_from(self.items, {"type": "*Button", "n": 2})["ptr"], "0x3")

    def test_type_n_out_of_range(self):
        self.assertIsNone(select_from(self.items, {"type": "*Button", "n": 3}))

    def test_idx(self):
        self.assertEqual(select_from(self.items, {"idx": 0})["ptr"], "0x1")

    def test_single_match_no_ordinal(self):
        self.assertEqual(select_from(self.items, {"type": "*Slider"})["ptr"], "0x4")

    def test_ambiguous_no_ordinal(self):
        self.assertIsNone(select_from(self.items, {"type": "*Button"}))

    def test_no_match(self):
        self.assertIsNone(select_from(self.items, {"type": "*Window"}))


class TestFlattenUiElements(unittest.TestCase):
    """_flatten_ui_elements: ui_list table -> ordered element items."""

    def test_flattens_sorted_by_ptr(self):
        cache = _ui_cache_with([("0xb", "UI_Element_Kind__Button"),
                                ("0xa", "UI_Element_Kind__Text")])
        items = _flatten_ui_elements(cache)
        self.assertEqual([it["ptr"] for it in items], ["0xa", "0xb"])
        self.assertEqual(items[1]["kind"], "UI_Element_Kind__Button")
        self.assertEqual(items[0]["manager"], "0x1000")

    def test_empty_cache(self):
        self.assertEqual(_flatten_ui_elements(None), [])
        self.assertEqual(_flatten_ui_elements({}), [])


class TestResolveValue(unittest.TestCase):
    """resolve_value: the single `[]` seam the dispatcher calls."""

    def test_substitutes_embedded_selector(self):
        gdb = _FakeGdb()
        gdb._ui_cache = _ui_cache_with([("0x2", "UI_Element_Kind__Button"),
                                        ("0x3", "UI_Element_Kind__Button")])
        self.assertEqual(resolve_value(gdb, "clicked [type=*Button,n=2]"),
                         "clicked 0x3")

    def test_bare_selector_whole_value(self):
        gdb = _FakeGdb()
        gdb._ui_cache = _ui_cache_with([("0x2", "UI_Element_Kind__Button")])
        self.assertEqual(resolve_value(gdb, "[type=*Button]"), "0x2")

    def test_no_selector_unchanged(self):
        gdb = _FakeGdb()
        gdb._ui_cache = _ui_cache_with([("0x2", "UI_Element_Kind__Button")])
        self.assertEqual(resolve_value(gdb, "0xdeadbeef"), "0xdeadbeef")

    def test_non_string_unchanged(self):
        self.assertEqual(resolve_value(_FakeGdb(), 5), 5)

    def test_no_cache_raises(self):
        with self.assertRaises(CommandError):
            resolve_value(_FakeGdb(), "[type=*Button,n=1]")

    def test_no_match_raises(self):
        gdb = _FakeGdb()
        gdb._ui_cache = _ui_cache_with([("0x2", "UI_Element_Kind__Button")])
        with self.assertRaises(CommandError):
            resolve_value(gdb, "[type=*Window,n=1]")


class TestInvokeResolvesSelector(unittest.TestCase):
    """invoke() resolves `[]` in kwargs before the driver runs."""

    def setUp(self):
        self._saved = {a: get_driver(a) for a in list_drivers()}
        for a in list(list_drivers()):
            unregister_driver(a)
        self.config = LavConfig()

    def tearDown(self):
        for a in list(list_drivers()):
            unregister_driver(a)
        for a, d in self._saved.items():
            register_driver(a, d)

    def test_invoke_resolves_before_driver(self):
        received = {}
        def drv(gdb, config, kwargs):
            received["element_ptr"] = kwargs["element_ptr"]
            return "ok"
        register_driver("ui_invoke", drv)
        gdb = _FakeGdb()
        gdb._ui_cache = _ui_cache_with([("0x2", "UI_Element_Kind__Button"),
                                        ("0x3", "UI_Element_Kind__Button")])
        invoke("ui_invoke", gdb, self.config,
               element_ptr="[type=*Button,n=2]", handler="clicked")
        self.assertEqual(received["element_ptr"], "0x3")


class TestSplitCommands(unittest.TestCase):
    """split_commands: ';' separator for the CLI."""

    def test_single_command(self):
        self.assertEqual(split_commands("start"), ["start"])

    def test_multiple_commands(self):
        self.assertEqual(split_commands("start; step; ui list"),
                         ["start", "step", "ui list"])

    def test_drops_empty_fragments(self):
        self.assertEqual(split_commands("start;; step ;"), ["start", "step"])

    def test_selector_stays_one_token(self):
        self.assertEqual(
            split_commands("ui invoke clicked [type=*Button,n=2]"),
            ["ui invoke clicked [type=*Button,n=2]"])


class TestRunScript(unittest.TestCase):
    """run_script: file of ';' separated commands."""

    def _write(self, content: str) -> str:
        path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            f"test_script_{os.getpid()}_{abs(hash(content))}.txt")
        with open(path, "w") as f:
            f.write(content)
        self.addCleanup(os.remove, path)
        return path

    def test_runs_semicolon_separated_commands(self):
        path = self._write("start; status; stop")
        call_tool = MagicMock(return_value="ok")
        self.assertTrue(run_script(path, call_tool))
        self.assertEqual(
            [c.args[0] for c in call_tool.call_args_list],
            ["session_start", "session_status", "session_stop"])

    def test_missing_file_returns_none(self):
        call_tool = MagicMock()
        self.assertIsNone(run_script("/nonexistent/lav_script.txt", call_tool))
        call_tool.assert_not_called()

    def test_empty_script_returns_true(self):
        path = self._write("   \n")
        call_tool = MagicMock()
        self.assertTrue(run_script(path, call_tool))
        call_tool.assert_not_called()

    def test_quit_in_script_stops_script(self):
        path = self._write("status; quit; stop")
        call_tool = MagicMock(return_value="ok")
        self.assertFalse(run_script(path, call_tool))
        self.assertEqual(
            [c.args[0] for c in call_tool.call_args_list],
            ["session_status"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
