"""Tests for Layer 5 (layer_lav_mcp.py)."""

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

from mcp_layered.layer_lav_mcp import (
    TOOL_DEFINITIONS,
    MCPAdapter,
    _TOOL_BY_NAME,
)
from mcp_layered.layer_lav_init import LavSession
from mcp_layered.layer_lav_config import LavConfig
from mcp_layered.layer_lav_cmd import CommandError, register_driver, unregister_driver


class TestToolDefinitions(unittest.TestCase):
    """Test the MCP tool definitions schema."""

    def test_all_tools_have_required_fields(self):
        """Every tool definition has name, description, and inputSchema."""
        for tool in TOOL_DEFINITIONS:
            self.assertIn("name", tool, f"Tool missing 'name': {tool}")
            self.assertIn("description", tool, f"Tool missing 'description': {tool}")
            self.assertIn("inputSchema", tool, f"Tool missing 'inputSchema': {tool}")
            self.assertIn("type", tool["inputSchema"])

    def test_tool_lookup_by_name(self):
        """Tools can be looked up by name in _TOOL_BY_NAME."""
        self.assertIn("session_start", _TOOL_BY_NAME)
        self.assertIn("navigate_step", _TOOL_BY_NAME)
        self.assertIn("navigate_source", _TOOL_BY_NAME)
        self.assertIn("ui_invoke", _TOOL_BY_NAME)

    def test_expected_tool_names_present(self):
        """All expected MCP tool names are present."""
        expected = [
            "session_start", "session_status", "session_stop",
            "navigate_step", "navigate_source",
            "core_dump", "core_load", "core_reset",
            "process_list", "process_watch",
            "input_read", "input_write",
            "ui_list", "ui_invoke",
            "graphics_screenshot",
            "audio_list", "audio_listen",
        ]
        actual = [t["name"] for t in TOOL_DEFINITIONS]
        for name in expected:
            self.assertIn(name, actual, f"Missing tool: {name}")

    def test_navigate_step_has_count_param(self):
        """navigate_step tool has a 'count' parameter with default 1."""
        tool = _TOOL_BY_NAME["navigate_step"]
        props = tool["inputSchema"]["properties"]
        self.assertIn("count", props)
        self.assertEqual(props["count"]["type"], "integer")
        self.assertEqual(props["count"]["default"], 1)

    def test_core_load_requires_uuid(self):
        """core_load tool requires 'uuid' parameter."""
        tool = _TOOL_BY_NAME["core_load"]
        self.assertIn("uuid", tool["inputSchema"]["required"])

    def test_ui_invoke_requires_element_ptr_and_handler(self):
        """ui_invoke tool requires 'element_ptr' and 'handler'."""
        tool = _TOOL_BY_NAME["ui_invoke"]
        self.assertIn("element_ptr", tool["inputSchema"]["required"])
        self.assertIn("handler", tool["inputSchema"]["required"])

    def test_input_write_requires_flag(self):
        """input_write tool requires 'flag' parameter."""
        tool = _TOOL_BY_NAME["input_write"]
        self.assertIn("flag", tool["inputSchema"]["required"])


class TestMCPAdapter(unittest.TestCase):
    """Test the MCPAdapter class."""

    def setUp(self):
        self.mock_session = MagicMock(spec=LavSession)
        self.mock_session.invoke.return_value = "test_result"
        self.adapter = MCPAdapter(self.mock_session)

    def test_list_tools(self):
        """list_tools returns all tool definitions."""
        tools = self.adapter.list_tools()
        self.assertEqual(len(tools), len(TOOL_DEFINITIONS))
        names = [t["name"] for t in tools]
        self.assertIn("session_start", names)

    def test_list_tools_returns_copy(self):
        """list_tools returns a copy (modifying it doesn't affect internal)."""
        tools = self.adapter.list_tools()
        tools.clear()
        # Internal should be unaffected
        self.assertGreater(len(self.adapter.list_tools()), 0)

    def test_get_tool_found(self):
        """get_tool returns the tool definition for known tools."""
        tool = self.adapter.get_tool("session_start")
        self.assertIsNotNone(tool)
        self.assertEqual(tool["name"], "session_start")

    def test_get_tool_not_found(self):
        """get_tool returns None for unknown tools."""
        self.assertIsNone(self.adapter.get_tool("nonexistent_tool"))

    def test_session_property(self):
        """session property returns the backing LavSession."""
        self.assertIs(self.adapter.session, self.mock_session)


class TestMCPDispatch(unittest.TestCase):
    """Test MCPAdapter.dispatch_tool()."""

    def setUp(self):
        # Create a mock session that delegates invoke() to the real command router
        self.real_invoke = None
        from mcp_layered.layer_lav_cmd import invoke as _real_invoke
        self._real_invoke = _real_invoke
        self.mock_gdb = MagicMock()
        self.config = LavConfig()

        self.mock_session = MagicMock(spec=LavSession)
        # Override invoke to use the real command router
        def session_invoke(alias, **kwargs):
            return self._real_invoke(alias, self.mock_gdb, self.config, **kwargs)
        self.mock_session.invoke = MagicMock(side_effect=session_invoke)
        self.adapter = MCPAdapter(self.mock_session)

        # Register a test driver
        self._session_start_driver = None
        try:
            self._session_start_driver = __import__(
                "mcp_layered.layer_lav_cmd", fromlist=["get_driver"]
            ).get_driver("session_start")
        except:
            pass

        def test_driver(gdb, config, kwargs):
            return f"driver called with {kwargs}"
        register_driver("session_start", test_driver)

    def tearDown(self):
        if self._session_start_driver:
            register_driver("session_start", self._session_start_driver)
        else:
            unregister_driver("session_start")

    def test_dispatch_known_tool(self):
        """dispatch_tool routes known tool to session.invoke."""
        result = self.adapter.dispatch_tool("session_start")
        self.assertEqual(result, "driver called with {}")

    def test_dispatch_unknown_tool_raises(self):
        """dispatch_tool raises CommandError for unknown tool."""
        with self.assertRaises(CommandError) as ctx:
            self.adapter.dispatch_tool("unknown_tool")
        self.assertIn("Unknown tool", str(ctx.exception))

    def test_dispatch_with_arguments(self):
        """dispatch_tool passes arguments to the driver."""
        # Register a driver for process_watch
        def pw_driver(gdb, config, kwargs):
            return f"watching {kwargs.get('process_ptr')}"
        register_driver("process_watch", pw_driver)
        try:
            result = self.adapter.dispatch_tool("process_watch", {"process_ptr": "0x1234"})
            self.assertIn("0x1234", result)
        finally:
            unregister_driver("process_watch")

    def test_dispatch_applies_defaults(self):
        """dispatch_tool applies schema defaults for missing arguments."""
        # Register a mock driver for step (mapped from navigate_step)
        def step_driver(gdb, config, kwargs):
            return "stepped"
        register_driver("step", step_driver)
        try:
            result = self.adapter.dispatch_tool("navigate_step", {})
            # invoke should be called with count=1 (the default)
            call_kwargs = self.mock_session.invoke.call_args
            self.assertEqual(call_kwargs[0][0], "step")
            self.assertEqual(call_kwargs[1].get("count"), 1)
        finally:
            unregister_driver("step")

    def test_dispatch_does_not_override_provided_args(self):
        """Provided arguments take precedence over schema defaults."""
        def step_driver(gdb, config, kwargs):
            return "stepped"
        register_driver("step", step_driver)
        try:
            self.adapter.dispatch_tool("navigate_step", {"count": 5})
            call_kwargs = self.mock_session.invoke.call_args
            self.assertEqual(call_kwargs[1].get("count"), 5)
        finally:
            unregister_driver("step")

    def test_dispatch_none_arguments(self):
        """dispatch_tool handles None arguments."""
        def status_driver(gdb, config, kwargs):
            return "ok"
        register_driver("session_status", status_driver)
        try:
            self.adapter.dispatch_tool("session_status", None)
            self.mock_session.invoke.assert_called()
        finally:
            unregister_driver("session_status")

    def test_dispatch_error_propagates(self):
        """CommandError from invoke propagates to caller."""
        # Register a failing driver
        def failing_driver(gdb, config, kwargs):
            raise CommandError("something failed")
        register_driver("session_status", failing_driver)
        try:
            with self.assertRaises(CommandError):
                self.adapter.dispatch_tool("session_status")
        finally:
            unregister_driver("session_status")


class TestMCPAdapterToolCoverage(unittest.TestCase):
    """Verify all tools can be dispatched."""

    def setUp(self):
        self.mock_session = MagicMock(spec=LavSession)
        self.mock_session.invoke.return_value = "mocked"
        self.adapter = MCPAdapter(self.mock_session)

    def test_all_tools_dispatchable(self):
        """Every tool in TOOL_DEFINITIONS can be dispatched without error."""
        # Register mock drivers for all tools
        for tool in TOOL_DEFINITIONS:
            name = tool["name"]
            register_driver(name, lambda gdb, cfg, kw: "mocked")

        for tool in TOOL_DEFINITIONS:
            name = tool["name"]
            required = tool["inputSchema"].get("required", [])
            # Provide dummy values for required args
            args = {}
            for req in required:
                args[req] = "dummy_value"
            try:
                result = self.adapter.dispatch_tool(name, args)
                self.assertEqual(result, "mocked")
            except Exception as e:
                self.fail(f"dispatch_tool('{name}') raised {type(e).__name__}: {e}")
            finally:
                unregister_driver(name)


if __name__ == "__main__":
    unittest.main(verbosity=2)
