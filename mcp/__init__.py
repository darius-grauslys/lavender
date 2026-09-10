"""Lavender MCP — MCP tools for debugging the Lavender game engine.

The ``mcp`` package is self-contained: all scanner, driver, and GDB
infrastructure modules have been relocated here from the old ``harness``
package.  This package is the "new shell" that grows to accommodate
the full debugging surface.

Public API:
    LavMcpSession    — per-session system module (gdb + scanner + driver)
    LavMcpServer     — MCP server router (HTTP + stdio)
    TOOL_DEFINITIONS — MCP tool schemas (list of dicts)
    SessionState     — runtime session state dataclass

Sub-modules:
    lav_mcp              — per-session system module (the "crab" itself)
    lav_mcp_server       — MCP server middleware router
    gdb_frame_controller — GDBFrameController (frame stack + MI primitives)
    debug_scanner        — DebugScannerBase (table / demeter machinery)
    debug_scanner_ui     — DebugUIScanner (UI state via debug_get_ui_scanner)
    debug_scanner_input  — DebugInputScanner (input state)
    debug_scanner_process— DebugProcessScanner (process list)
    debug_ui_utils       — DebugUIUtils (drive UI element handler fields)
    debug_input_driver   — DebugInputDriver (drive game input)
    display_setup        — DisplayManager (headless Xvfb lifecycle)
    gdb_nav_utils        — step_frame (game-loop frame stepping)
    gl_harness           — GLDebugHarness (OpenGL screenshot + context)
    lavender_debug       — Input_Flags__u32, parse_hex, utils

Usage:
    # HTTP mode:
    python3 -m mcp.lav_mcp_server --port 8890

    # stdio mode (for Claude Desktop):
    python3 -m mcp.lav_mcp_server --stdio

    # With config:
    python3 -m mcp.lav_mcp_server --config /path/to/config.json
"""

from .lav_mcp import (
    LavMcpSession,
    SessionState,
    TOOL_DEFINITIONS,
)

__version__ = "0.1.0"

__all__ = [
    "LavMcpSession",
    "SessionState",
    "TOOL_DEFINITIONS",
]
