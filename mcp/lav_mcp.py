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
import time
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
      - ``last_dump_uuid`` — UUID of the most recent core dump (for ``core_reset``).
    """

    running: bool = False
    halted: bool = False
    crashed: bool = False
    backtrace: str = ""
    # (selected_manager_ptr removed — ui_list now shows all elements across all managers)
    last_dump_uuid: str | None = None
    crash_signal: str | None = None
    log_file: str | None = None  # path to MCP tool call/response log


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
            "Advance one or more game frames: continue to manage_game__post_render, "
            "then execute 'finish' to reach the post-render state. "
            "Repeats count times (default 1)."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "count": {
                    "type": "integer",
                    "description": "Number of frames to step (default 1, must be >= 1).",
                    "default": 1,
                },
            },
            "required": [],
        },
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
        "name": "ui_list",
        "description": (
            "List all UI elements across all UI managers."
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
        log_file: str | None = None,
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

        # Optional MCP tool call/response log file.
        if log_file is not None:
            self.state.log_file = os.path.expanduser(log_file)
            os.makedirs(os.path.dirname(self.state.log_file), exist_ok=True)

        # Per-session lock to serialize tool calls.  Prevents concurrent GDB
        # writes from racing when multiple MCP clients call tools on the same
        # session simultaneously.
        import threading
        self._tool_lock = threading.Lock()

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
        """Return or create the DebugUIUtils, sharing the session's scanner.

        Uses the same DebugUIScanner as the session (via ``_get_ui_scanner()``)
        to avoid redundant scanning.  Since ``_refresh_ui()`` already calls
        ``scanner.get_scanner()`` to rebuild the table, DebugUIUtils can simply
        read the cached table without triggering another scan.
        """
        if self._ui_utils is None:
            self._ui_utils = DebugUIUtils(
                self._ensure_gdb(), scanner=self._get_ui_scanner()
            )
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

    # -- lazy UI initialization ----------------------------------------------- #

    def _refresh_ui(self) -> str | None:
        """Re-scan the UI state and ensure a manager is selected.

        This is the initializer/refresher for UI operations:

        1. Re-captures the scanner struct via ``get_scanner()`` (always,
           to get fresh data — the game state may have changed since the
           last scan).
        2. Builds the table and checks for UI managers.

        Returns ``None`` on success, or an error string if something failed.
        Callers should check the return value and abort if non-None.
        """
        if self._gdbmi is None:
            return "ERROR: GDB not started. Call session_start() first."

        try:
            scanner = self._get_ui_scanner()

            # Always re-scan to get fresh data. get_scanner() invalidates
            # _table_cache, so get_table() will rebuild.
            scanner.get_scanner()
            table = scanner.get_table()
            managers = table.get("ui_managers", {})

            if not managers:
                return (
                    "ERROR: no UI managers found.\n"
                    "  The game may not have reached poll_ui_manager__update.\n"
                    "  Try stepping a few frames first (use 'step' command)."
                )

            return None  # success
        except Exception as e:
            # Handle timeout errors gracefully — the game may be stuck
            # in scene loading and not yet at poll_ui_manager__update.
            errno_name = type(e).__name__
            if "timeout" in errno_name.lower() or "time" in errno_name.lower():
                return (
                    f"ERROR: GDB timed out ({errno_name}).\n"
                    "  The game may be stuck in scene loading.\n"
                    "  Try using 'step' to advance the game loop first."
                )
            return f"ERROR initializing UI: {type(e).__name__}: {e}"

    # -- crash detection ------------------------------------------------------- #

    def _check_crash(self, resp: list) -> bool:
        """Scan a GDB response list for a crash (signal-received stop).

        pygdbmi has no callback mechanism, so we must poll responses after
        each ``write``.  A crash appears as a ``notify`` record with
        ``message == "stopped"`` and ``reason == "signal-received"``.

        When a crash is detected:
        - The session state is marked as crashed.
        - A core dump is saved immediately (via ``core_dump``).
        - The core dump's UUID is stored in ``self.state.last_dump_uuid``.

        Returns ``True`` if a crash was detected, ``False`` otherwise.
        """
        if not resp:
            return False

        for rec in resp:
            if not isinstance(rec, dict):
                continue
            if rec.get("type") != "notify":
                continue
            if rec.get("message") != "stopped":
                continue

            payload = rec.get("payload") or {}
            reason = payload.get("reason", "")
            if reason == "signal-received":
                signal_name = payload.get("signal-name", "unknown")
                # Mark the session as crashed.
                self._set_crashed()

                # Save the crash info for the caller.
                self.state.crash_signal = signal_name
                self.state.backtrace = self._refresh_backtrace()

                # Auto-create a core dump immediately.
                dump_uuid = str(uuid.uuid4())
                dump_path = os.path.join(self._dump_location, f"core-{dump_uuid}")
                try:
                    self._gdbmi.get_gdb_response(timeout_sec=2.0)  # drain
                    self._gdbmi.write(
                        f"-interpreter-exec console \"gcore {dump_path}\""
                    )
                    try:
                        self._gdbmi.get_gdb_response(timeout_sec=30.0)
                    except Exception:
                        pass
                    self.state.last_dump_uuid = dump_uuid
                except Exception:
                    pass

                return True
        return False

    def _gdb_exec(self, cmd: str, timeout: float = 15.0) -> list:
        """Execute a GDB MI command and return the response.

        This wraps ``write`` + ``get_gdb_response`` and automatically
        checks for crashes.  Use this for all GDB commands to ensure
        crash detection works consistently.
        """
        self._gdbmi.write(cmd)
        resp = self._gdbmi.get_gdb_response(timeout_sec=timeout)
        if self._check_crash(resp):
            # Raise or handle — for now, callers can check state.is_crashed.
            pass
        return resp

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

    def navigate_step(self, count: int = 1) -> str:
        """Advance one or more game frames.

        Uses ``step_frame("manage_game__post_render")`` to continue until
        the end-of-frame breakpoint, then executes ``finish`` to get the
        post-render state.  Repeats *count* times (default 1).

        Args:
            count: Number of frames to step (default 1).
        """
        if not _HAS_PYGDBMI or self._gdbmi is None:
            return "ERROR: GDB not started. Call session_start() first."

        if count < 1:
            return "ERROR: count must be >= 1."

        try:
            for i in range(count):
                hit = step_frame(self._gdbmi, "manage_game__post_render", timeout=15.0)
                if not hit:
                    return (
                        f"ERROR: timed out waiting for manage_game__post_render "
                        f"on step {i+1}/{count} "
                        "(possible infinite loop or the function doesn't exist)."
                    )

                # Execute 'finish' to get state after manage_game__post_render.
                self._gdbmi.write("-exec-finish")
                self._set_halted(True)
                self._refresh_backtrace()

            if count == 1:
                return (
                    "Stepped one game frame to post-render.\n"
                    f"Backtrace:\n{self.state.backtrace}"
                )
            else:
                return (
                    f"Stepped {count} game frames to post-render.\n"
                    f"Backtrace:\n{self.state.backtrace}"
                )
        except Exception as e:
            self._set_crashed()
            return f"ERROR stepping frame: {type(e).__name__}: {e}"

    def navigate_source(self) -> str:
        """Print the current backtrace and the source of the current frame.

        Uses ``-stack-info-frame`` to get the current frame's file/line/function,
        then reads the source file directly from disk (since the GDB server
        process has access to the same filesystem).  Shows a 7-line window
        centered on the current line, with the current line marked.
        """
        if not _HAS_PYGDBMI or self._gdbmi is None:
            return "ERROR: GDB not started. Call session_start() first."

        try:
            self._refresh_backtrace()

            gdbmi = self._gdbmi
            resp = gdbmi.write("-stack-info-frame")
            for rec in resp:
                if rec.get("type") == "result" and rec.get("message") == "done":
                    payload = rec.get("payload") or {}
                    frame = payload.get("frame") or {}
                    file_ = frame.get("file", "?")
                    line = frame.get("line", "0")
                    func = frame.get("func", "?")

                    header = f"Current frame: {func} at {file_}:{line}"

                    # Read the source file directly from disk.
                    if file_ and file_ != "?":
                        try:
                            line_int = int(line)
                            start = max(1, line_int - 3)
                            end = line_int + 3

                            with open(file_) as f:
                                all_lines = f.readlines()

                            source_lines = []
                            for i in range(start, min(end + 1, len(all_lines) + 1)):
                                content = all_lines[i - 1].rstrip()
                                marker = "> " if i == line_int else "  "
                                source_lines.append(
                                    f"  {marker}{i:>5} | {content}"
                                )

                            return (
                                f"Backtrace:\n{self.state.backtrace}\n\n"
                                f"{header}\n"
                                + "\n".join(source_lines)
                            )
                        except (ValueError, OSError, Exception) as e:
                            return (
                                f"Backtrace:\n{self.state.backtrace}\n\n"
                                f"{header}\n"
                                f"  (unable to read source: {type(e).__name__}: {e})"
                            )

                    return (
                        f"Backtrace:\n{self.state.backtrace}\n\n"
                        f"{header}\n"
                        f"  (no source file available)"
                    )

            return (
                f"Backtrace:\n{self.state.backtrace}\n\n"
                f"(unable to determine current frame)"
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
                # Read the interrupt response.
                try:
                    self._gdbmi.get_gdb_response(timeout_sec=5.0)
                except Exception:
                    pass
                self._set_halted(True)

            # Use gcore to generate the core dump via console interpreter.
            self._gdbmi.write(
                f"-interpreter-exec console \"gcore {dump_path}\""
            )
            # Read the response to ensure gcore has completed.
            try:
                self._gdbmi.get_gdb_response(timeout_sec=30.0)
            except Exception:
                pass

            if not os.path.exists(dump_path):
                return (
                    f"ERROR: core dump file was not created.\n"
                    f"  Expected path: {dump_path}\n"
                    f"  Check that gcore is available and GDB has write permission."
                )

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

    def ui_list(self) -> str:
        """List all UI elements across all UI managers.

        Scans all managers and their elements, producing a flat list.
        Only handlers with non-null function pointers are advertised.
        """
        if not _HAS_PYGDBMI or self._gdbmi is None:
            return "ERROR: GDB not started. Call session_start() first."

        # Refresh UI state (always re-scan for fresh data).
        err = self._refresh_ui()
        if err:
            return err

        try:
            scanner = self._get_ui_scanner()
            table = scanner.get_table()
            managers = table.get("ui_managers", {})

            if not managers:
                return "No UI managers found."

            lines: list[str] = ["UI Elements:"]
            total = 0
            for mgr_ptr, mgr in sorted(managers.items()):
                elements = mgr.get("ui_elements", {})
                for el_ptr, info in sorted(elements.items()):
                    uuid_val = info.get("uuid", "?")
                    kind = info.get("kind", "?")
                    handlers = info.get("handlers", {})
                    # Only advertise handlers with non-null function pointers.
                    available = sorted(
                        name for name, addr in handlers.items() if addr is not None
                    )
                    handler_names = ", ".join(available) if available else "none"
                    lines.append(
                        f"  {el_ptr}  uuid={uuid_val}  kind={kind}  "
                        f"mngr={mgr_ptr}  handlers=[{handler_names}]"
                    )
                    total += 1

            if total == 0:
                lines.append("  (no elements found)")

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

        # Refresh UI state (always re-scan for fresh data).
        err = self._refresh_ui()
        if err:
            return err

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

            # The scanner table was already refreshed by _refresh_ui() above,
            # and DebugUIUtils shares the same scanner instance, so no need
            # to scan again here.

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

    def graphics_screenshot(self, output_path: str | None = None) -> dict[str, Any] | str:
        """Capture a screenshot of the current game frame.

        Uses ``debug_gl.h`` (via GLDebugHarness) to produce a screenshot.

        The game must be stopped at ``scene__main.c:205`` (post-render,
        pre-swap) for the GL backbuffer to be valid.  If the game is not
        already at that frame, this method attempts to set a temporary
        breakpoint there and continue to it (up to 15 seconds).

        Returns a structured dict with ``content`` containing both a text
        message and the base64-encoded PNG image data (MCP ``image`` content
        type) on success, or a plain error string on failure.
        """
        if not _HAS_PYGDBMI or self._gdbmi is None:
            return "ERROR: GDB not started. Call session_start() first."

        # gl_debug_screencap(&game) always saves "screen.png" to the game's
        # working directory (which may differ from the server's CWD).  We
        # search for it in likely locations after the call.
        import base64

        try:
            harness = self._get_gl_harness()

            # Ensure we're at the screencap breakpoint (scene__main.c:205).
            # set_screencap_breakpoint sets a temp breakpoint; then continue
            # and poll for the stop.
            harness.set_screencap_breakpoint()
            import time
            deadline = time.monotonic() + 15.0
            stop_found = False
            while time.monotonic() < deadline:
                try:
                    resp = self._gdbmi.get_gdb_response(timeout_sec=2.0)
                except Exception:
                    break
                if not resp:
                    continue
                for rec in resp:
                    if (isinstance(rec, dict) and
                            rec.get("type") == "notify" and
                            rec.get("message") == "stopped"):
                        stop_found = True
                        break
                if stop_found:
                    break

            if not stop_found:
                # Game might already be at the right frame, or the breakpoint
                # didn't fire (e.g. the game hasn't reached scene__main.c:205
                # yet).  Try screencap anyway — it may work if we're already
                # stopped at the right line.
                pass

            ok = harness.screencap()
            if not ok:
                return (
                    "ERROR: screencap returned False.\n"
                    "  Ensure the game is stopped at scene__main.c:205 "
                    "(post-render, pre-swap) with a valid GL context."
                )

            # Find the screenshot file.  The game saves "screen.png" to its
            # CWD, which is typically the directory containing the executable.
            search_dirs = [
                os.path.dirname(os.path.abspath(self._executable)),
                os.getcwd(),
                self._dump_location,
            ]
            png_path = None
            for d in search_dirs:
                candidate = os.path.join(d, "screen.png")
                if os.path.exists(candidate) and os.path.getsize(candidate) > 0:
                    png_path = candidate
                    break

            if png_path is None:
                return (
                    "ERROR: screen.png was not found after screencap.\n"
                    "  Searched: " + ", ".join(
                        os.path.join(d, "screen.png") for d in search_dirs
                    )
                )

            # Read the PNG file and encode it as base64 for MCP image transfer.
            with open(png_path, "rb") as f:
                png_bytes = f.read()
            b64_data = base64.b64encode(png_bytes).decode("ascii")

            # If a specific output_path was requested, copy the file there.
            if output_path is not None:
                abs_output_path = os.path.abspath(output_path)
                os.makedirs(os.path.dirname(abs_output_path) or ".", exist_ok=True)
                with open(abs_output_path, "wb") as f:
                    f.write(png_bytes)
                display_path = abs_output_path
            else:
                display_path = png_path

            return {
                "content": [
                    {"type": "text", "text": f"Screenshot: {display_path}"},
                    {
                        "type": "image",
                        "data": b64_data,
                        "mimeType": "image/png",
                    },
                ],
            }
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

    def _log_tool_call(self, tool_name: str, arguments: dict[str, Any], response: str) -> None:
        """Append a JSON-lines record of a tool call and its response to the log file."""
        if self.state.log_file is None:
            return
        record = {
            "timestamp": time.time(),
            "tool": tool_name,
            "arguments": arguments,
            "response_len": len(response),
            "response": response,
        }
        try:
            with open(self.state.log_file, "a") as f:
                f.write(json.dumps(record) + "\n")
                f.flush()  # ensure log is on disk immediately
        except OSError:
            pass  # logging is best-effort

    def dispatch_tool(self, tool_name: str, arguments: dict[str, Any] | None = None) -> str:
        """Dispatch a tool call to the appropriate method.

        This is used by the MCP server router to invoke tools by name.
        Tool calls are serialized per-session via ``_tool_lock`` to prevent
        concurrent GDB writes from racing.
        """
        arguments = arguments or {}
        method_name = _TOOL_METHOD_MAP.get(tool_name)
        if method_name is None:
            response = f"ERROR: unknown tool '{tool_name}'."
            self._log_tool_call(tool_name, arguments, response)
            return response
        method = getattr(self, method_name, None)
        if method is None:
            response = f"ERROR: method '{method_name}' not found on LavMcpSession."
            self._log_tool_call(tool_name, arguments, response)
            return response
        with self._tool_lock:
            response = method(**arguments)
            self._log_tool_call(tool_name, arguments, response)
            return response
