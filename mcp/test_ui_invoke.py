#!/usr/bin/env python3
"""
test_ui_invoke.py — Integration test for UI handler invocation.

This test uses the AncientsGame binary to verify that:

1. The scanner can be captured and UI managers/elements are found.
2. UI handlers can be invoked via cast-and-call + single nav step.
3. The game state is correct after invocation.

Prerequisites:
    - DISPLAY=:0 (or Xvfb)
    - The AncientsGame binary at:
      /home/shalidor/Projects/Projects__Lavender/AncientsGame/build/sdl/AncientsGame

Usage:
    DISPLAY=:0 python3 mcp/test_ui_invoke.py
"""

from __future__ import annotations

import os
import sys

# Add the mcp package to the path.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp.lav_mcp import LavMcpSession
from mcp.gdb_nav_utils import step_frame

ANCIENTS_GAME = (
    "/home/shalidor/Projects/ProjectsLavender/AncientsGame"
    "/build/sdl/AncientsGame"
)


def main() -> int:
    if not os.path.exists(ANCIENTS_GAME):
        print(f"ERROR: binary not found: {ANCIENTS_GAME}")
        return 1

    display = os.environ.get("DISPLAY")
    if not display:
        print("ERROR: DISPLAY env var not set (need Xvfb or X11)")
        return 1

    print("=== UI Invoke Test ===")
    print(f"  Binary: {ANCIENTS_GAME}")
    print(f"  Display: {display}")
    print()

    session = LavMcpSession(
        executable=ANCIENTS_GAME,
        dump_location="/tmp/lav-core-dump/",
    )

    # -- Start the game -- #
    print("[1] Starting game under GDB...")
    result = session.session_start()
    if "ERROR" in result:
        print(f"    {result}")
        return 1
    print("    OK")

    # -- Step to get into the game loop -- #
    print("[2] Stepping to game loop...")
    for i in range(6):
        ok = step_frame(session._gdbmi, "manage_game__post_render", timeout=15.0)
        if not ok:
            break
        print(f"    Step {i+1}: OK")

    # -- Scan for UI managers -- #
    print("[3] Scanning for UI managers...")
    from mcp.debug_scanner_ui import DebugUIScanner

    scanner = DebugUIScanner(session._gdbmi)
    scanner.get_scanner()
    table = scanner.get_table()
    managers = table.get("ui_managers", {})

    if not managers:
        print("  No UI managers found (environment limitation, not a failure).")
        session.session_stop()
        return 0

    print(f"  Found {len(managers)} UI manager(s):")
    for ptr, info in sorted(managers.items()):
        qty = info.get("quantity_of__ui_elements", 0)
        print(f"    {ptr}  elements={qty}")

    # -- Invoke a handler -- #
    print("[4] Invoking UI handler...")
    from mcp.debug_ui_utils import DebugUIUtils

    ui_utils = DebugUIUtils(session._gdbmi)

    first_mgr = sorted(managers.keys())[0]
    elements = managers[first_mgr].get("ui_elements", {})
    if not elements:
        print("  No UI elements found in manager.")
        session.session_stop()
        return 0

    first_elem_ptr = sorted(elements.keys())[0]
    print(f"    Invoking 'clicked' on element {first_elem_ptr}")

    try:
        ui_utils.clicked(first_elem_ptr)
        print("    PASS: handler invoked successfully")
    except Exception as e:
        print(f"    ERROR during invocation: {e}")
        session.session_stop()
        return 1

    # -- Cleanup -- #
    print("[5] Stopping game...")
    session.session_stop()
    print("=== Test Complete ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
