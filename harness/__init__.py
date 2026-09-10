"""
harness — Agentic QA harness for executing and interrogating programs.

Public API (re-exported for convenience):
    GDBFrameController         — base class: frame stack + MI primitives
    DebugScannerBase           — base class for the scan pattern (table API)
    DebugUIScanner             — inspect UI state via debug_get_ui_scanner
    DebugEntityScanner         — inspect entities via debug_get_entity_scanner
    DebugSceneScanner         — inspect scenes via debug_get_scene_scanner
    DebugUIUtils               — drive UI element handler fields (debug hooks)
    DebugInputDriver           — drive game input via debug_drive_* functions
    GLDebugHarness             — OpenGL screenshot + input debugging helpers
    DisplayManager             — headless X display (Xvfb) lifecycle management
    Input_Flags__u32           — mirror of platform_defaults.h INPUT_* macros
    DEBUG_UI_SCANNER_FIELDS    — field list of DEBUG_UI_Scanner struct
    main                       — CLI entry point: parse_args + session loop

Scanner API (see debug_scanner.py / TODOS.md item 1):
    scanner.get_scanner()             capture the debug struct by value
    scanner.get_table()               nested JSON-parsable snapshot of the state
    scanner.get_fields()              top-level field names (table keys)
    scanner.get_field(demeter)        value at a dot-path ("demeter")
    scanner.find_demeters(substring)  dot-paths whose key contains *substring*

Display/OpenGL debugging:
    ensure_display()                  get a usable DISPLAY (starts Xvfb if needed)
    configure_gdb_signals(gdbmi)      pass-through SDL/Pulse signal handling
    configure_gdb_nonstop(gdbmi)      enable GDB non-stop mode for threads
    configure_gdb_environment(gdbmi)  set DISPLAY/XAUTHORITY inside GDB

Usage:
    python3 -m harness --program /path/to/executable

Sub-modules:
    main                — CLI, session setup, read-loop, teardown
    harness             — langchain agent loop (skeleton)
    gdb_mcp             — MCP tools for external AI agents (skeleton)
    gdb_frame_controller— GDBFrameController (frame management + MI primitives)
    lavender_debug      — utils + Input_Flags__u32
    display_setup       — Xvfb/display management for headless GL debugging
    gl_harness          — OpenGL screenshot + context persistence helpers
    debug_input_driver  — DebugInputDriver
    debug_scanner       — DebugScannerBase (table / demeter machinery)
    debug_scanner_ui    — DebugUIScanner
    debug_scanner_entity— DebugEntityScanner
    debug_scanner_scene — DebugSceneScanner
    debug_ui_utils      — DebugUIUtils (drive UI element handler fields)
"""

# --- pygdbmi-dependent imports (optional — may not be installed) --- #
try:
    from .gdb_frame_controller import GDBFrameController
    _HAS_PYGDBMI = True
except ImportError:
    GDBFrameController = None  # type: ignore[assignment]
    _HAS_PYGDBMI = False

from .lavender_debug import Input_Flags__u32, parse_hex

# display_setup has no pygdbmi dependency and is always available.
from .display_setup import (
    DisplayManager,
    ensure_display,
    configure_gdb_signals,
    configure_gdb_nonstop,
    configure_gdb_environment,
)

if _HAS_PYGDBMI:
    from .debug_scanner import DebugScannerBase
    from .debug_scanner_ui import (
        DebugUIScanner,
        DEBUG_UI_SCANNER_FIELDS,
    )
    from .debug_scanner_entity import DebugEntityScanner, DEBUG_ENTITY_SCANNER_FIELDS
    from .debug_scanner_scene import DebugSceneScanner, DEBUG_SCENE_SCANNER_FIELDS
    from .debug_ui_utils import DebugUIUtils
    from .gl_harness import GLDebugHarness
    from .debug_input_driver import DebugInputDriver
else:
    DebugScannerBase = None  # type: ignore[assignment]
    DebugUIScanner = None  # type: ignore[assignment]
    DebugEntityScanner = None  # type: ignore[assignment]
    DebugSceneScanner = None  # type: ignore[assignment]
    DebugUIUtils = None  # type: ignore[assignment]
    GLDebugHarness = None  # type: ignore[assignment]
    DebugInputDriver = None  # type: ignore[assignment]
    DEBUG_UI_SCANNER_FIELDS = ()
    DEBUG_ENTITY_SCANNER_FIELDS = ()
    DEBUG_SCENE_SCANNER_FIELDS = ()

try:
    from .main import main
except ImportError:
    main = None  # type: ignore[assignment]

__version__ = "0.1.0"

__all__ = [
    "GDBFrameController",
    "DebugScannerBase",
    "DebugUIScanner",
    "DebugEntityScanner",
    "DebugSceneScanner",
    "DebugUIUtils",
    "DebugInputDriver",
    "Input_Flags__u32",
    "DEBUG_UI_SCANNER_FIELDS",
    "DEBUG_ENTITY_SCANNER_FIELDS",
    "DEBUG_SCENE_SCANNER_FIELDS",
    "parse_hex",
    "main",
    "GLDebugHarness",
    "DisplayManager",
    "ensure_display",
    "configure_gdb_signals",
    "configure_gdb_nonstop",
    "configure_gdb_environment",
]
