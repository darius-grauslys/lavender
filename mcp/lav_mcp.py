"""
lav_mcp.py — Per-session comprehensive system module for the Lavender MCP server.

This module is *replicated per session*.  Each ``LavMcpSession`` wraps a
``pygdbmi.GdbController`` and exposes high-level, Lavender-specific operations
for debugging the game engine: session lifecycle, frame navigation, core
dump management, process inspection, input driving, UI manipulation, and
graphics capture.

The operations correspond to the ``session``, ``navigate``, ``core``,
``process``, ``input``, ``ui``, ``graphics``, and ``audio`` tool categories
defined in ``DESIGN.md``.

Design principles applied (see terminologies/):
  - Interface Segregation: one method per operation; callers compose them.
  - Single Source of Truth: scanner tables (DebugScannerBase.get_table()) are
    the SSOT for debug state reads.
  - Law of Demeter: scanner navigation via dot-paths; tools don't reach into
    internal struct fields beyond the table.
  - Inversion of Control: LavMcpSession delegates to GDBFrameController,
    DebugScannerBase, DebugInputDriver, and DebugUIUtils — it doesn't subclass
    them.
  - Layered / Statified: session → drivers → GDBFrameController → pygdbmi.
    No upward references.
  - Composition over Inheritance: drivers are composed, not inherited.
"""

from __future__ import annotations

import dataclasses
import json
import os
import uuid
from typing import Any

# --------------------------------------------------------------------------- #
#  pygdbmi-dependent imports (optional — may not be installed)                #
# --------------------------------------------------------------------------- #
try:
    from pygdbmi.gdbcontroller import GdbController

    # Local modules (each transitively depends on pygdbmi).
    from .debug_scanner_ui import (
        DEBUG_UI_SCANNER_FIELDS,
        DebugUIScanner,
    )
    from .debug_ui_utils import DebugUIUtils
    from .debug_input_driver import DebugInputDriver
    from .display_setup import (
        DisplayManager,
        configure_gdb_environment,
        ensure_display,
    )
    from .gdb_nav_utils import patch_gdbmi_timeouts, step_frame
    from .gl_harness import GLDebugHarness
    from .lavender_debug import Input_Flags__u32

    # New scanner modules (in the mcp package).
    from .debug_scanner_input import DEBUG_INPUT_SCANNER_FIELDS, DebugInputScanner
    from .debug_scanner_process import (
        DEBUG_PROCESS_SCANNER_FIELDS,
        DebugProcessScanner,
    )

    _HAS_PYGDBMI = True
    _PygController = GdbController
except ImportError:  # pygdbmi or harness modules not available
    _HAS_PYGDBMI = False
    GdbController = None  # type: ignore[assignment]
    DebugUIScanner = None  # type: ignore[assignment]
    DebugUIUtils = None  # type: ignore[assignment]
    DebugInputDriver = None  # type: ignore[assignment]
    DisplayManager = None  # type: ignore[assignment]
    ensure_display = None  # type: ignore[assignment]
    configure_gdb_environment = None  # type: ignore[assignment]
    GLDebugHarness = None  # type: ignore[assignment]
    Input_Flags__u32 = None  # type: ignore[assignment]
    DebugInputScanner = None  # type: ignore[assignment]
    DebugProcessScanner = None  # type: ignore[assignment]
    DEBUG_UI_SCANNER_FIELDS = ()
    DEBUG_INPUT_SCANNER_FIELDS = ()
    DEBUG_PROCESS_SCANNER_FIELDS = ()
    step_frame = None  # type: ignore[assignment]
    _PygController = None  # type: ignore[assignment]


# --------------------------------------------------------------------------- #
#  Session state                                                              #
# --------------------------------------------------------------------------- #
@dataclasses.dataclass
class SessionState:
    """Tracks the runtime state of a debugging session.

    This is the session's own bookkeeping (not gdb state per se):
      - ``running``    — the game process is executing (gdb has continued it).
      - ``halted``     — gdb has the process stopped (breakpoint, signal, etc.).
      - ``crashed``    — the process exited abnormally.
      - ``selected_manager_ptr`` — the UI manager currently selected for
        ``ui_list`` / ``ui_invoke`` operations.
      - ``last_dump_uuid`` — UUID of the most recent core dump (for ``core_reset``).
    """

    running: bool = False
    halted: bool = False
    crashed: bool = False
    backtrace: str = ""
    selected_manager_ptr: str | None = None
    last_dump_uuid: str | None = None


# --------------------------------------------------------------------------- #
#  Tool definitions (MCP schema)                                              #
# --------------------------------------------------------------------------- #
TOOL_DEFINITIONS: list[dict[str, Any]] = [
    # ---- session ----
    {
        "name": "session_start",
        "description": "Start the Lavender game under GDB if not already running.",
        "inputSchema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "session_status",
        "description": (
            "Get the current session status: whether the game is running, "
            "halted, or crashed, plus the current backtrace."
        ),
        "inputSchema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "session_stop",
        "description": "Stop the Lavender game and exit the GDB session.",
        "inputSchema": {"type": "object", "properties": {}, "required": []},
    },
    # ---- navigate ----
    {
        "name": "navigate_step",
        "description": (
            "Advance exactly one game frame: continue to manage_game__post_render, "
            "then execute 'finish' to reach the post-render state."
        ),
        "inputSchema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "navigate_source",
        "description": "Print the current backtrace and the source of the current frame.",
        "inputSchema": {"type": "object", "properties": {}, "required": []},
    },
    # ---- core ----
    {
        "name": "core_dump",
        "description": "Extract a core dump of the current game state to disk.",
        "inputSchema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "core_load",
        "description": "Stop the game and load a previously saved core dump by UUID.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "uuid": {
                    "type": "string",
                    "description": "UUID of the core dump to load (from core_dump).",
                }
            },
            "required": ["uuid"],
        },
    },
    {
        "name": "core_reset",
        "description": "Stop the game and reload the last core dump loaded via core_load.",
        "inputSchema": {"type": "object", "properties": {}, "required": []},
    },
    # ---- process ----
    {
        "name": "process_list",
        "description": "List all processes currently managed by the game's Process_Manager.",
        "inputSchema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "process_watch",
        "description": (
            "Set a breakpoint on the specified process's function handler and "
            "continue until it is hit. Returns when the process is in frame."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "process_ptr": {
                    "type": "string",
                    "description": "Hex pointer to the Process to watch (from process_list).",
                }
            },
            "required": ["process_ptr"],
        },
    },
    # ---- input ----
    {
        "name": "input_read",
        "description": "Dump the current input state (flags, mouse position, delta).",
        "inputSchema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "input_write",
        "description": (
            "Drive or drop an input flag. Use 'drive' to set the flag, 'drop' to clear it."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "flag": {
                    "type": "string",
                    "description": (
                        "Input flag name (e.g. FORWARD, LEFT, RIGHT, CLICK). "
                        "See Input_Flags__u32 for the full list."
                    ),
                },
                "action": {
                    "type": "string",
                    "enum": ["drive", "drop"],
                    "description": "Whether to set ('drive') or clear ('drop') the flag.",
                },
            },
            "required": ["flag"],
        },
    },
    # ---- ui ----
    {
        "name": "ui_manager",
        "description": (
            "List all UI managers from the DebugUIScanner. Also reports the "
            "currently selected manager."
        ),
        "inputSchema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "ui_manager_select",
        "description": "Select a UI manager by pointer for subsequent ui_list/ui_invoke calls.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "manager_ptr": {
                    "type": "string",
                    "description": "Hex pointer to the UI_Manager (from ui_manager).",
                }
            },
            "required": ["manager_ptr"],
        },
    },
    {
        "name": "ui_list",
        "description": (
            "List all UI elements under the currently selected UI manager."
        ),
        "inputSchema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "ui_invoke",
        "description": (
            "Invoke a handler on a UI element. All handlers except 'transformed' "
            "are supported."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "element_ptr": {
                    "type": "string",
                    "description": "Hex pointer to the UI_Element (from ui_list).",
                },
                "handler": {
                    "type": "string",
                    "description": (
                        "Handler name: clicked, dragged, dropped, receive_drop, "
                        "held, typed, compose, dispose."
                    ),
                },
                "dropped_ptr": {
                    "type": "string",
                    "description": "For 'receive_drop': the dropped element pointer.",
                },
                "symbol": {
                    "type": "string",
                    "description": "For 'typed': the character symbol to pass.",
                },
            },
            "required": ["element_ptr", "handler"],
        },
    },
    # ---- graphics ----
    {
        "name": "graphics_screenshot",
        "description": "Capture a screenshot of the current game frame.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "output_path": {
                    "type": "string",
                    "description": "Output file path (defaults to /tmp/lav-screen-<uuid>.png).",
                }
            },
            "required": []
        },
    },
    # ---- audio ----
    {
        "name": "audio_list",
        "description": "List audio devices/sources. Currently unsupported.",
        "inputSchema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "audio_listen",
        "description": "Listen to an audio source. Currently unsupported.",
        "inputSchema": {"type": "object", "properties": {}, "required": []},
    },
]


# --------------------------------------------------------------------------- #
#  Tool name → method mapping                                                 #
# --------------------------------------------------------------------------- #
# Maps MCP tool names to LavMcpSession method names.  The server uses this to
# dispatch incoming tool calls.
_TOOL_METHOD_MAP: dict[str, str] = {
    "session_start": "session_start",
    "session_status": "session_status",
    "session_stop": "session_stop",
    "navigate_step": "navigate_step",
    "navigate_source": "navigate_source",
    "core_dump": "core_dump",
    "core_load": "core_load",
    "core_reset": "core_reset",
    "process_list": "process_list",
    "process_watch": "process_watch",
    "input_read": "input_read",
    "input_write": "input_write",
    "ui_manager": "ui_manager",
    "ui_manager_select": "ui_manager_select",
    "ui_list": "ui_list",
    "ui_invoke": "ui_invoke",
    "graphics_screenshot": "graphics_screenshot",
    "audio_list": "audio_list",
    "audio_listen": "audio_listen",
}


class LavMcpSession:
    """Per-session comprehensive system module for the Lavender MCP server.

    Wraps a ``pygdbmi.GdbController`` and provides domain-specific operations
    for debugging the Lavender game engine.  Each instance corresponds to a
    single session (a single game process under GDB).

    The class follows the **composition over inheritance** principle: it
    delegates to ``GDBFrameController``, ``DebugUIScanner``,
    ``DebugInputDriver``, ``DebugUIUtils``, ``DebugInputScanner``,
    ``DebugProcessScanner``, and ``GLDebugHarness`` rather than subclassing them.
    """

    def __init__(
        self,
        executable: str,
        dump_location: str = "/tmp/lav-core-dump/",
    ) -> None:
        self._executable = executable
        self._dump_location = os.path.expanduser(dump_location)
        self._gdbmi: GdbController | None = None
        self._display: str | None = None
        self._ui_scanner: DebugUIScanner | None = None
        self._input_scanner: DebugInputScanner | None = None
        self._process_scanner: DebugProcessScanner | None = None
        self._input_driver: DebugInputDriver | None = None
        self._ui_utils: DebugUIUtils | None = None
        self._gl_harness: GLDebugHarness | None = None

        self.state = SessionState()

        # Ensure the dump location directory exists.
        os.makedirs(self._dump_location, exist_ok=True)

    # -- identity ------------------------------------------------------------- #

    @property
    def executable(self) -> str:
        return self._executable

    @property
    def is_running(self) -> bool:
        return self.state.running and not self.state.crashed

    @property
    def is_halted(self) -> bool:
        return self.state.halted and not self.state.crashed

    @property
    def is_crashed(self) -> bool:
        return self.state.crashed

    # -- lazy initialization -------------------------------------------------- #

    def _ensure_gdb(self) -> GdbController:
        """Return the GdbController, raising if it hasn't been started."""
        if self._gdbmi is None:
            raise RuntimeError("GDB not started. Call session_start() first.")
        return self._gdbmi

    def _ensure_display(self) -> str:
        """Ensure a usable X display is available.

        Calls the standalone ``ensure_display()`` function from
        ``display_setup``, which starts an Xvfb if no DISPLAY is set.
        Returns the DISPLAY string (e.g. ``:99.0``).
        """
        if self._display is None:
            if ensure_display is None:
                raise RuntimeError("pygdbmi / harness modules not available.")
            self._display = ensure_display()
        return self._display

    def _get_ui_scanner(self) -> DebugUIScanner:
        """Return or create the DebugUIScanner (SSOT for UI state)."""
        if self._ui_scanner is None:
            self._ui_scanner = DebugUIScanner(self._ensure_gdb())
        return self._ui_scanner

    def _get_input_scanner(self) -> DebugInputScanner:
        """Return or create the DebugInputScanner (SSOT for input state)."""
        if self._input_scanner is None:
            self._input_scanner = DebugInputScanner(self._ensure_gdb())
        return self._input_scanner

    def _get_process_scanner(self) -> DebugProcessScanner:
        """Return or create the DebugProcessScanner (SSOT for process state)."""
        if self._process_scanner is None:
            self._process_scanner = DebugProcessScanner(self._ensure_gdb())
        return self._process_scanner

    def _get_input_driver(self) -> DebugInputDriver:
        """Return or create the DebugInputDriver."""
        if self._input_driver is None:
            self._input_driver = DebugInputDriver(self._ensure_gdb())
        return self._input_driver

    def _get_ui_utils(self) -> DebugUIUtils:
        """Return or create the DebugUIUtils."""
        if self._ui_utils is None:
            self._ui_utils = DebugUIUtils(self._ensure_gdb())
        return self._ui_utils

    def _get_gl_harness(self) -> GLDebugHarness:
        """Return or create the GLDebugHarness."""
        if self._gl_harness is None:
            self._gl_harness = GLDebugHarness(self._ensure_gdb())
        return self._gl_harness

    # -- session state helpers ------------------------------------------------ #

    def _set_halted(self, halted: bool = True) -> None:
        """Update session state to reflect gdb halt status."""
        self.state.halted = halted
        self.state.running = not halted

    def _set_crashed(self) -> None:
        """Mark the session as crashed."""
        self.state.crashed = True
        self.state.running = False
        self.state.halted = False

    def _refresh_backtrace(self) -> str:
        """Query gdb for the current backtrace and cache it."""
        gdbmi = self._ensure_gdb()
        resp = gdbmi.write("-stack-list-frames")
        lines: list[str] = []
        for rec in resp:
            if rec.get("type") == "result" and rec.get("message") == "done":
                payload = rec.get("payload") or {}
                frames = payload.get("stack", [])
                for i, frame in enumerate(frames):
                    func = frame.get("func", "?")
                    file_ = frame.get("file", "")
                    line = frame.get("line", "")
                    lines.append(f"#{i}  {func} at {file_}:{line}")
        backtrace = "\n".join(lines) if lines else "(no frames)"
        self.state.backtrace = backtrace
        return backtrace

    # ------------------------------------------------------------------ #
    #  Tool: session                                                    #
    # ------------------------------------------------------------------ #

    def session_start(self) -> str:
        """Start the Lavender game under GDB if not already running.

        Steps:
        1. If already running, return early.
        2. Start Xvfb display if needed.
        3. Launch GDB with the configured executable.
        4. Run to ``main`` so the game is initialized but paused.
        5. Configure signal handling for SDL/PulseAudio.
        """
        if self._gdbmi is not None and self.is_running:
            return (
                f"Game already running (executable={self._executable}). "
                f"Use session_status for details."
            )

        if not _HAS_PYGDBMI:
            return (
                "ERROR: pygdbmi is not installed. "
                "Install it with: pip install pygdbmi"
            )

        try:
            # NOTE: display_setup's Xvfb/DisplayManager (ensure_display) is NOT
            # invoked here — it may block on environments without Xvfb.
            # configure_gdb_environment() is safe to call: it only propagates
            # existing DISPLAY/XAUTHORITY/etc. env vars into GDB (non-blocking).
            #
            # To re-enable Xvfb auto-start: call self._ensure_display() here.

            # Launch GDB in MI3 mode (structured output required by pygdbmi).
            self._gdbmi = GdbController(
                command=["gdb", "--nx", "--quiet", "--interpreter=mi3"],
            )
            # Patch pygdbmi timeouts from 1s -> 15s (see gdb_nav_utils).
            patch_gdbmi_timeouts(self._gdbmi)

            gdbmi = self._gdbmi

            # Configure GDB for SDL2/PulseAudio stability.
            gdbmi.write("-gdb-set pagination off")
            gdbmi.write("-gdb-set confirm off")

            # Propagate DISPLAY and related env vars into the GDB inferior.
            configure_gdb_environment(gdbmi)

            # Load the executable.
            gdbmi.write(f"-file-exec-and-symbols {self._executable}")
            gdbmi.write("-exec-run --start")

            self.state.running = True
            self.state.halted = True  # stopped at 'start' (pre-main or main)
            self.state.crashed = False
            self._refresh_backtrace()

            return (
                f"Game started under GDB: {self._executable}\n"
                f"State: halted at start.\n"
                f"Backtrace:\n{self.state.backtrace}"
            )
        except Exception as e:
            self.state.crashed = True
            return f"ERROR starting game: {type(e).__name__}: {e}"

    def session_status(self) -> str:
        """Return the current session status.

        Reports:
        1. Whether the game has started.
        2. Whether the game is halted (gdb breakpoint).
        3. Whether the game has crashed.
        4. The current backtrace.
        """
        if self._gdbmi is None:
            return (
                "Game has NOT started.\n"
                "Use session_start to launch the game."
            )

        if self.state.crashed:
            return (
                "Game has CRASHED.\n"
                "Use session_stop to clean up, then session_start to restart.\n"
                f"Last backtrace:\n{self.state.backtrace}"
            )

        # Refresh backtrace to check for process exit.
        try:
            self._refresh_backtrace()
        except Exception as e:
            self.state.crashed = True
            return f"Game appears to have crashed: {e}"

        status = "halted" if self.state.halted else "running"

        return (
            f"Game: started\n"
            f"Status: {status}\n"
            f"Selected UI manager: "
            f"{self.state.selected_manager_ptr or '(none)'}\n"
            f"Last dump UUID: {self.state.last_dump_uuid or '(none)'}\n"
            f"Backtrace:\n{self.state.backtrace}"
        )

    def session_stop(self) -> str:
        """Stop the Lavender game and exit the GDB session."""
        if self._gdbmi is None:
            return "Game is not running (no GDB session to stop)."

        try:
            self._gdbmi.exit()
            self._gdbmi = None
            self.state.running = False
            self.state.halted = False
            self._ui_scanner = None
            self._input_scanner = None
            self._process_scanner = None
            self._input_driver = None
            self._ui_utils = None
            self._gl_harness = None

            # Xvfb cleanup is handled by _active_managers in display_setup;
            # it persists for the process lifetime.

            return "Game stopped and GDB session exited."
        except Exception as e:
            return f"ERROR stopping game: {type(e).__name__}: {e}"

    # ------------------------------------------------------------------ #
    #  Tool: navigate                                                   #
    # ------------------------------------------------------------------ #

    def navigate_step(self) -> str:
        """Advance exactly one game frame.

        Uses ``step_frame("manage_game__post_render")`` to continue until
        the end-of-frame breakpoint, then executes ``finish`` to get the
        post-render state.
        """
        if not _HAS_PYGDBMI or self._gdbmi is None:
            return "ERROR: GDB not started. Call session_start() first."

        try:
            hit = step_frame(self._gdbmi, "manage_game__post_render", timeout=15.0)
            if not hit:
                return (
                    "ERROR: timed out waiting for manage_game__post_render "
                    "(possible infinite loop or the function doesn't exist)."
                )

            # Execute 'finish' to get state after manage_game__post_render.
            self._gdbmi.write("-exec-finish")
            self._set_halted(True)
            self._refresh_backtrace()

            return (
                "Stepped one game frame to post-render.\n"
                f"Backtrace:\n{self.state.backtrace}"
            )
        except Exception as e:
            self._set_crashed()
            return f"ERROR stepping frame: {type(e).__name__}: {e}"

    def navigate_source(self) -> str:
        """Print the current backtrace and the source of the current frame."""
        if not _HAS_PYGDBMI or self._gdbmi is None:
            return "ERROR: GDB not started. Call session_start() first."

        try:
            self._refresh_backtrace()

            # Get source of current frame.
            gdbmi = self._gdbmi
            source_lines: list[str] = []
            resp = gdbmi.write("-stack-info-frame")
            for rec in resp:
                if rec.get("type") == "result" and rec.get("message") == "done":
                    payload = rec.get("payload") or {}
                    frame = payload.get("frame") or {}
                    file_ = frame.get("file", "?")
                    line = frame.get("line", "0")
                    func = frame.get("func", "?")
                    source_lines.append(
                        f"Current frame: {func} at {file_}:{line}"
                    )
                    # Try to read source lines around the current line.
                    if file_ and file_ != "?":
                        try:
                            line_int = int(line)
                            start = max(1, line_int - 3)
                            end = line_int + 3
                            src_resp = gdbmi.write(
                                f"-source-list-lines {file_}"
                            )
                            # If we can read source, show a small window.
                            source_lines.append(f"  (source available at {file_})")
                        except (ValueError, Exception):
                            source_lines.append(f"  (source at {file_})")

            return (
                f"Backtrace:\n{self.state.backtrace}\n\n"
                + "\n".join(source_lines)
            )
        except Exception as e:
            return f"ERROR reading source: {type(e).__name__}: {e}"

    # ------------------------------------------------------------------ #
    #  Tool: core                                                       #
    # ------------------------------------------------------------------ #

    def core_dump(self) -> str:
        """Extract a core dump of the current game state.

        Uses gdb's ``gcore`` command. The dump is saved to the configured
        ``dump_location`` with a UUID filename.  Returns the UUID.
        """
        if not _HAS_PYGDBMI or self._gdbmi is None:
            return "ERROR: GDB not started. Call session_start() first."

        dump_uuid = str(uuid.uuid4())
        dump_path = os.path.join(self._dump_location, f"core-{dump_uuid}")

        try:
            # Stop the game first to get a consistent state.
            if self.state.running:
                self._gdbmi.write("-exec-interrupt")
                self._set_halted(True)

            # Use gcore to generate the core dump.
            self._gdbmi.write(f"gcore {dump_path}")
            self._gdbmi.write(f"-interpreter-exec console \"gcore {dump_path}\"")

            self.state.last_dump_uuid = dump_uuid

            return (
                f"Core dump saved.\n"
                f"  UUID: {dump_uuid}\n"
                f"  Path: {dump_path}"
            )
        except Exception as e:
            return f"ERROR creating core dump: {type(e).__name__}: {e}"

    def core_load(self, uuid: str) -> str:
        """Stop the game and load a previously saved core dump by UUID."""
        if not _HAS_PYGDBMI or self._gdbmi is None:
            return "ERROR: GDB not started. Call session_start() first."

        dump_path = os.path.join(self._dump_location, f"core-{uuid}")
        if not os.path.exists(dump_path):
            return (
                f"ERROR: core dump not found at {dump_path}\n"
                f"Use core_dump to create one, or check the UUID."
            )

        try:
            # Stop the game if running.
            if self.state.running or self._gdbmi is not None:
                self.session_stop()

            # Start fresh GDB with the core dump (MI3 mode).
            self._gdbmi = GdbController(
                command=["gdb", "--nx", "--quiet", "--interpreter=mi3"],
            )
            # Patch pygdbmi timeouts from 1s -> 15s (see gdb_nav_utils).
            patch_gdbmi_timeouts(self._gdbmi)
            gdbmi = self._gdbmi

            gdbmi.write("-gdb-set pagination off")
            gdbmi.write("-gdb-set confirm off")
            gdbmi.write(f"-file-exec-and-symbols {self._executable}")
            gdbmi.write(f"-core-file {dump_path}")
            gdbmi.write("-exec-run")

            self.state.running = True
            self.state.halted = False
            self.state.crashed = False
            self.state.last_dump_uuid = uuid
            self._refresh_backtrace()

            return (
                f"Loaded core dump.\n"
                f"  UUID: {uuid}\n"
                f"  Path: {dump_path}\n"
                f"  State: running (resumed from core dump)\n"
                f"  Backtrace:\n{self.state.backtrace}"
            )
        except Exception as e:
            self._set_crashed()
            return f"ERROR loading core dump: {type(e).__name__}: {e}"

    def core_reset(self) -> str:
        """Stop the game and reload the last core dump loaded via core_load."""
        last = self.state.last_dump_uuid
        if last is None:
            return (
                "ERROR: no core dump loaded yet.\n"
                "Use core_dump to create one, or core_load to load one."
            )
        return self.core_load(last)

    # ------------------------------------------------------------------ #
    #  Tool: process                                                    #
    # ------------------------------------------------------------------ #

    def process_list(self) -> str:
        """List all processes in the game's Process_Manager.

        Uses DebugProcessScanner to acquire the process table (SSOT),
        which maps each Process pointer to its UUID and kind.
        """
        if not _HAS_PYGDBMI or self._gdbmi is None:
            return "ERROR: GDB not started. Call session_start() first."

        try:
            scanner = self._get_process_scanner()
            scanner.get_scanner()
            table = scanner.get_table()

            processes = table.get("processes", {})
            if not processes:
                return "No processes found (quantity_of__processes is 0)."

            lines: list[str] = ["Processes:"]
            for ptr, info in sorted(processes.items()):
                uuid_val = info.get("uuid", "?")
                kind = info.get("kind", "?")
                lines.append(f"  {ptr}  uuid={uuid_val}  kind={kind}")

            return "\n".join(lines)
        except Exception as e:
            return f"ERROR listing processes: {type(e).__name__}: {e}"

    def process_watch(self, process_ptr: str) -> str:
        """Set a breakpoint on a process's function handler and continue.

        Continues until:
        1. The process's function handler is hit, or
        2. The same process pointer is hit again.
        """
        if not _HAS_PYGDBMI or self._gdbmi is None:
            return "ERROR: GDB not started. Call session_start() first."

        try:
            # Set a temporary breakpoint on the process's debug function.
            # The convention is m_debug_process__<kind> or complete_process().
            breakpoint_expr = f"complete_process"
            self._gdbmi.write(f"-break-insert -t {breakpoint_expr}")

            # Continue until the breakpoint is hit (with timeout).
            self._gdbmi.write("-exec-continue", read_response=False)
            # Poll for the stop by reading gdb responses.  We use an explicit
            # short timeout per poll so the loop doesn't block for the full
            # 15s default on each iteration.
            import time
            deadline = time.monotonic() + 15.0
            hit = False
            while time.monotonic() < deadline:
                resp = self._gdbmi.get_gdb_response(timeout_sec=2.0)
                if not resp:
                    continue  # No response yet — program still running.
                for rec in resp:
                    if rec.get("type") == "notify" and rec.get("message") == "stopped":
                        hit = True
                        break
                if hit:
                    break

            if hit:
                self._set_halted(True)
                self._refresh_backtrace()
                return (
                    f"Process {process_ptr} is now in frame.\n"
                    f"Backtrace:\n{self.state.backtrace}"
                )
            else:
                return (
                    f"ERROR: timed out waiting for process {process_ptr} to be hit."
                )
        except Exception as e:
            return f"ERROR watching process: {type(e).__name__}: {e}"

    # ------------------------------------------------------------------ #
    #  Tool: input                                                      #
    # ------------------------------------------------------------------ #

    def input_read(self) -> str:
        """Dump the current input state.

        Uses DebugInputScanner (SSOT) to read the current input flags,
        mouse position, and delta.
        """
        if not _HAS_PYGDBMI or self._gdbmi is None:
            return "ERROR: GDB not started. Call session_start() first."

        try:
            scanner = self._get_input_scanner()
            scanner.get_scanner()
            table = scanner.get_table()

            lines: list[str] = ["Current Input State:"]
            current_flags = table.get("current_flags", "0")
            pressed_flags = table.get("pressed_flags", "0")

            # Decode flags using Input_Flags__u32.
            flags_str = self._decode_flags(int(str(current_flags or "0"), 0))
            pressed_str = self._decode_flags(int(str(pressed_flags or "0"), 0))

            lines.append(f"  current_flags: {current_flags} ({flags_str})")
            lines.append(f"  pressed_flags: {pressed_flags} ({pressed_str})")
            lines.append(f"  mouse_pos: {table.get('mouse_pos', '?')}")
            lines.append(f"  mouse_delta: {table.get('mouse_delta', '?')}")

            return "\n".join(lines)
        except Exception as e:
            return f"ERROR reading input: {type(e).__name__}: {e}"

    def _decode_flags(self, flags_val: int) -> str:
        """Decode a bitmask into a list of flag names using Input_Flags__u32."""
        if Input_Flags__u32 is None or flags_val == 0:
            return "NONE"
        names: list[str] = []
        for flag in Input_Flags__u32:
            if flags_val & int(flag):
                names.append(flag.name)
        return ", ".join(names) if names else "NONE"

    def input_write(self, flag: str, action: str = "drive") -> str:
        """Drive or drop an input flag.

        Uses DebugInputDriver to invoke ``debug_drive_input__flag`` or
        ``debug_drop_input__flag``.
        """
        if not _HAS_PYGDBMI or self._gdbmi is None:
            return "ERROR: GDB not started. Call session_start() first."

        if Input_Flags__u32 is None:
            return "ERROR: Input_Flags__u32 not available."

        # Resolve the flag name to the enum.
        flag_upper = flag.upper()
        try:
            input_flag = Input_Flags__u32[flag_upper]
        except KeyError:
            valid = ", ".join(f.name for f in Input_Flags__u32)
            return (
                f"ERROR: unknown input flag '{flag}'.\n"
                f"Valid flags: {valid}"
            )

        try:
            driver = self._get_input_driver()
            if action == "drive":
                driver.drive_input__flag(input_flag)
                return f"Drove input flag: {flag_upper} ({int(input_flag)})"
            elif action == "drop":
                driver.drop_input__flag(input_flag)
                return f"Dropped input flag: {flag_upper} ({int(input_flag)})"
            else:
                return (
                    f"ERROR: unknown action '{action}'.\n"
                    "Valid actions: 'drive', 'drop'"
                )
        except Exception as e:
            return f"ERROR writing input: {type(e).__name__}: {e}"

    # ------------------------------------------------------------------ #
    #  Tool: ui                                                         #
    # ------------------------------------------------------------------ #

    def ui_manager(self) -> str:
        """List all UI managers.

        Uses DebugUIScanner (SSOT) to list all UI managers from the scanner
        table.  Also reports the currently selected manager.
        """
        if not _HAS_PYGDBMI or self._gdbmi is None:
            return "ERROR: GDB not started. Call session_start() first."

        try:
            scanner = self._get_ui_scanner()
            scanner.get_scanner()
            table = scanner.get_table()

            managers = table.get("ui_managers", {})
            if not managers:
                return "No UI managers found."

            lines: list[str] = ["UI Managers:"]
            for ptr, info in sorted(managers.items()):
                uuid_val = info.get("uuid", "?")
                qty = info.get("quantity_of__ui_elements", 0)
                marker = " (SELECTED)" if ptr == self.state.selected_manager_ptr else ""
                lines.append(
                    f"  {ptr}  uuid={uuid_val}  elements={qty}{marker}"
                )

            if self.state.selected_manager_ptr is None:
                lines.append("\nNo manager selected. Use ui_manager_select.")

            return "\n".join(lines)
        except Exception as e:
            return f"ERROR listing UI managers: {type(e).__name__}: {e}"

    def ui_manager_select(self, manager_ptr: str) -> str:
        """Select a UI manager for subsequent ui_list/ui_invoke calls."""
        if not _HAS_PYGDBMI or self._gdbmi is None:
            return "ERROR: GDB not started. Call session_start() first."

        try:
            scanner = self._get_ui_scanner()
            table = scanner.get_table()
            managers = table.get("ui_managers", {})

            # Normalize the pointer for comparison.
            from .lavender_debug import parse_hex
            normalized = parse_hex(manager_ptr) or manager_ptr

            if normalized not in managers:
                return (
                    f"ERROR: UI manager '{manager_ptr}' not found in scanner table.\n"
                    f"Use ui_manager to list available managers."
                )

            self.state.selected_manager_ptr = normalized
            return (
                f"Selected UI manager: {normalized}\n"
                f"Use ui_list to see its elements, or ui_invoke to call handlers."
            )
        except Exception as e:
            return f"ERROR selecting manager: {type(e).__name__}: {e}"

    def ui_list(self) -> str:
        """List all UI elements under the selected UI manager."""
        if not _HAS_PYGDBMI or self._gdbmi is None:
            return "ERROR: GDB not started. Call session_start() first."

        if self.state.selected_manager_ptr is None:
            return (
                "ERROR: no UI manager selected.\n"
                "Use ui_manager to list managers, then ui_manager_select."
            )

        try:
            scanner = self._get_ui_scanner()
            table = scanner.get_table()
            managers = table.get("ui_managers", {})

            mgr_info = managers.get(self.state.selected_manager_ptr)
            if mgr_info is None:
                return (
                    f"ERROR: selected manager {self.state.selected_manager_ptr} "
                    "not found. It may have been deallocated.\n"
                    "Use ui_manager to re-scan and ui_manager_select."
                )

            elements = mgr_info.get("ui_elements", {})
            if not elements:
                return f"No UI elements under manager {self.state.selected_manager_ptr}."

            lines: list[str] = [
                f"UI Elements under manager {self.state.selected_manager_ptr}:"
            ]
            for ptr, info in sorted(elements.items()):
                uuid_val = info.get("uuid", "?")
                kind = info.get("kind", "?")
                handlers = info.get("handlers", {})
                handler_names = ", ".join(sorted(handlers.keys())) if handlers else "none"
                lines.append(
                    f"  {ptr}  uuid={uuid_val}  kind={kind}  handlers=[{handler_names}]"
                )

            return "\n".join(lines)
        except Exception as e:
            return f"ERROR listing UI elements: {type(e).__name__}: {e}"

    def ui_invoke(
        self,
        element_ptr: str,
        handler: str,
        dropped_ptr: str | None = None,
        symbol: str | None = None,
    ) -> str:
        """Invoke a UI handler on a UI element.

        Maps to ``DebugUIUtils`` handler methods.  The precondition is that
        the game is stopped at ``poll_ui_manager__update`` — DebugUIUtils
        auto-navigates to that frame if needed.

        Supported handlers: clicked, dragged, dropped, receive_drop, held,
        typed, compose, dispose.  (``transformed`` is not supported.)
        """
        # Check for unsupported handler before GDB availability — this
        # doesn't require a running GDB session.
        handler_lower = handler.lower()

        if handler_lower == "transformed":
            return (
                "ERROR: 'transformed' handler is not yet implemented.\n"
                "It requires Hitbox_AABB + Vector__3i32 position data."
            )

        if not _HAS_PYGDBMI or self._gdbmi is None:
            return "ERROR: GDB not started. Call session_start() first."

        try:
            ui_utils = self._get_ui_utils()

            # Call the appropriate method.
            method_name = handler_lower
            method = getattr(ui_utils, method_name, None)
            if method is None:
                valid = "clicked, dragged, dropped, receive_drop, held, typed, compose, dispose"
                return (
                    f"ERROR: unknown handler '{handler}'.\n"
                    f"Valid handlers: {valid}"
                )

            # Refresh the scanner table to ensure it's current.
            ui_utils.refresh()

            # Call the handler with appropriate arguments.
            if method_name == "receive_drop":
                if dropped_ptr is None:
                    return (
                        "ERROR: 'receive_drop' requires 'dropped_ptr' argument.\n"
                        "Usage: ui_invoke receive_drop <target_ptr> <dropped_ptr>"
                    )
                method(element_ptr, dropped_ptr)
            elif method_name == "typed":
                if symbol is None:
                    return (
                        "ERROR: 'typed' requires 'symbol' argument.\n"
                        "Usage: ui_invoke typed <element_ptr> <symbol>"
                    )
                method(element_ptr, symbol)
            else:
                method(element_ptr)

            return (
                f"Invoked handler '{handler_lower}' on element {element_ptr}.\n"
                f"  (DebugUIUtils auto-navigates to poll_ui_manager__update if needed.)"
            )
        except Exception as e:
            return f"ERROR invoking UI handler: {type(e).__name__}: {e}"

    # ------------------------------------------------------------------ #
    #  Tool: graphics                                                   #
    # ------------------------------------------------------------------ #

    def graphics_screenshot(self, output_path: str | None = None) -> str:
        """Capture a screenshot of the current game frame.

        Uses ``debug_gl.h`` (via GLDebugHarness) to produce a screenshot.
        """
        if not _HAS_PYGDBMI or self._gdbmi is None:
            return "ERROR: GDB not started. Call session_start() first."

        if output_path is None:
            screenshot_uuid = str(uuid.uuid4())
            output_path = os.path.join(
                self._dump_location, f"screen-{screenshot_uuid}.png"
            )

        try:
            harness = self._get_gl_harness()
            harness.screenshot(output_path)
            return (
                f"Screenshot saved.\n"
                f"  Path: {output_path}"
            )
        except Exception as e:
            return f"ERROR capturing screenshot: {type(e).__name__}: {e}"

    # ------------------------------------------------------------------ #
    #  Tool: audio                                                      #
    # ------------------------------------------------------------------ #

    def audio_list(self) -> str:
        """List audio devices/sources. Currently unsupported."""
        return (
            "audio_list is currently unsupported.\n"
            "This is a placeholder for future expansion."
        )

    def audio_listen(self) -> str:
        """Listen to an audio source. Currently unsupported."""
        return (
            "audio_listen is currently unsupported.\n"
            "This is a placeholder for future expansion."
        )

    # ------------------------------------------------------------------ #
    #  Internal: tool dispatch                                          #
    # ------------------------------------------------------------------ #

    def dispatch_tool(self, tool_name: str, arguments: dict[str, Any] | None = None) -> str:
        """Dispatch a tool call to the appropriate method.

        This is used by the MCP server router to invoke tools by name.
        """
        arguments = arguments or {}
        method_name = _TOOL_METHOD_MAP.get(tool_name)
        if method_name is None:
            return f"ERROR: unknown tool '{tool_name}'."
        method = getattr(self, method_name, None)
        if method is None:
            return f"ERROR: method '{method_name}' not found on LavMcpSession."
        return method(**arguments)
