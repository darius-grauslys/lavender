"""
gdb_mcp.py — MCP (Model Context Protocol) tools for the harness.

This module will house MCP server / tool functions that expose gdb operations
to external AI agents via the Model Context Protocol.  Initial tools will
mirror the debug_input and debug_scanner driver APIs:

  - drive_input__flag / drop_input__flag
  - drive_input__mouse_pos
  - dispatch_click
  - get_scanner / read_field / read_fields
  - next_element / next_manager

For now this is a placeholder — the tool signatures and MCP registration
will be filled in when the langchain agent loop (harness.py) is ready to
consume them.
"""

from __future__ import annotations

# TODO: MCP tool registration
#   from mcp import McpServer
#
#   from .debug_input_driver import DebugInputDriver
#   from .debug_scanner import DebugUIScannerExplorer
#   from .lavender_debug import Input_Flags__u32, parse_hex
#
#   _server = McpServer("lavender-gdb-mcp", "0.1.0")
#
#   @_server.call("drive_input__flag")
#   def _drive_input__flag(input_flag: Input_Flags__u32) -> None:
#       """Drive an input flag into the game via gdb."""
#       ...
