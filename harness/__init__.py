"""
harness — Agentic QA harness for executing and interrogating programs.

Public API (re-exported for convenience):
    GDBFrameController         — base class: frame stack + MI primitives
    DebugScannerBase           — base class for the scan pattern (table API)
    DebugUIScanner             — inspect UI state via debug_get_ui_scanner
    DebugEntityScanner         — inspect entities via debug_get_entity_scanner
    DebugSceneScanner          — inspect scenes via debug_get_scene_scanner
    DebugInputDriver           — drive game input via debug_drive_* functions
    Input_Flags__u32           — mirror of platform_defaults.h INPUT_* macros
    DEBUG_UI_SCANNER_FIELDS    — field list of DEBUG_UI_Scanner struct
    main                       — CLI entry point: parse_args + session loop

Scanner API (see debug_scanner.py / TODOS.md item 1):
    scanner.get_scanner()             capture the debug struct by value
    scanner.get_table()               nested JSON-parsable snapshot of the state
    scanner.get_fields()              top-level field names (table keys)
    scanner.get_field(demeter)        value at a dot-path ("demeter")
    scanner.find_demeters(substring)  dot-paths whose key contains *substring*

Usage:
    python3 -m harness --program /path/to/executable

Sub-modules:
    main                — CLI, session setup, read-loop, teardown
    harness             — langchain agent loop (skeleton)
    gdb_mcp             — MCP tools for external AI agents (skeleton)
    gdb_frame_controller— GDBFrameController (frame management + primitives)
    lavender_debug      — utils + Input_Flags__u32
    debug_input_driver  — DebugInputDriver
    debug_scanner       — DebugScannerBase (table / demeter machinery)
    debug_scanner_ui    — DebugUIScanner
    debug_scanner_entity— DebugEntityScanner
    debug_scanner_scene — DebugSceneScanner
"""

from .gdb_frame_controller import GDBFrameController
from .lavender_debug import Input_Flags__u32, parse_hex
from .debug_scanner import DebugScannerBase
from .debug_scanner_ui import (
    DebugUIScanner,
    DEBUG_UI_SCANNER_FIELDS,
)
from .debug_scanner_entity import DebugEntityScanner, DEBUG_ENTITY_SCANNER_FIELDS
from .debug_scanner_scene import DebugSceneScanner, DEBUG_SCENE_SCANNER_FIELDS
from .debug_input_driver import DebugInputDriver
from .main import main

__version__ = "0.1.0"

__all__ = [
    "GDBFrameController",
    "DebugScannerBase",
    "DebugUIScanner",
    "DebugEntityScanner",
    "DebugSceneScanner",
    "DebugInputDriver",
    "Input_Flags__u32",
    "DEBUG_UI_SCANNER_FIELDS",
    "DEBUG_ENTITY_SCANNER_FIELDS",
    "DEBUG_SCENE_SCANNER_FIELDS",
    "parse_hex",
    "main",
]
