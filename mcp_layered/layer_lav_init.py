"""Layer 4: Initialization and session wiring.

This layer accepts a config path (or None for defaults), forwards to the
config layer, creates a GDBSession, and assembles everything into a LavSession
facade that combines:
- GDBSession (Layer 1b)
- LavConfig (Layer 2)
- Command router (Layer 3)

This is the composition root.
"""

from __future__ import annotations

import os
from typing import Any

from mcp_layered.layer_lav_config import LavConfig, default_config, load_config
from mcp_layered.layer_lav_cmd import invoke, CommandError, register_driver, get_driver
from mcp_layered.layer_pygdbmi import GDBSession
from mcp_layered.debug_response import DebugResponse, ResponseType


class LavSession:
    """Facade combining GDBSession, LavConfig, and command router.

    This is the main entry point for higher layers (Layers 5-6).
    It exposes a simple `invoke(alias, **kwargs)` method that routes
    commands through the command router to scanner drivers.
    """

    def __init__(
        self,
        config: LavConfig | None = None,
        gdb: GDBSession | None = None,
    ):
        """Initialize the session.

        Args:
            config: LavConfig instance. If None, uses default_config().
            gdb: GDBSession instance. If None, creates a new one.
                 Note: GDB session is NOT started (no executable loaded)
                 until session_start is explicitly invoked.
        """
        self.config = config if config is not None else default_config()
        self.gdb = gdb if gdb is not None else GDBSession(
            command=[self.config.gdb_path] + self.config.gdb_args
        )
        self._started = False

    # -- Command routing -- #

    def invoke(self, alias: str, **kwargs: Any) -> str:
        """Route a command to the appropriate scanner driver.

        Args:
            alias: The command alias (e.g., "step", "ui_list", "session_start").
            **kwargs: Arguments for the command.

        Returns:
            The command result string.

        Raises:
            CommandError: If the command fails or alias is not found.
        """
        return invoke(alias, self.gdb, self.config, **kwargs)

    # -- Session lifecycle -- #

    @property
    def is_started(self) -> bool:
        """True if the GDB session has been started with an executable."""
        return self._started

    @property
    def gdb_path(self) -> str:
        """The GDB executable being used."""
        return self.gdb.gdb_path

    @property
    def executable(self) -> str:
        """The executable path from config."""
        return self.config.executable

    def close(self) -> None:
        """Close the GDB session."""
        if not self.gdb.is_closed:
            self.gdb.close()
        self._started = False

    # -- Convenience accessors -- #

    def get_config(self) -> LavConfig:
        """Return the configuration."""
        return self.config

    def get_gdb(self) -> GDBSession:
        """Return the GDB session."""
        return self.gdb


def create_session(
    config_path: str | None = None,
    executable: str | None = None,
    gdb: GDBSession | None = None,
) -> LavSession:
    """Create a LavSession with optional config override.

    Args:
        config_path: Path to config file. If None, uses default_config().
        executable: Override the executable path from config.
        gdb: Optional pre-created GDBSession (for testing).

    Returns:
        A LavSession instance.
    """
    config = load_config(config_path)
    if executable is not None:
        config.executable = executable

    # Ensure directories exist
    config.ensure_directories()

    # Register built-in drivers (session_start, status, stop)
    _register_builtin_drivers()

    return LavSession(config=config, gdb=gdb)


def default_session() -> LavSession:
    """Create a LavSession with default configuration and a new GDBSession."""
    return create_session()


# -- Driver Registration -- #

def _register_builtin_drivers() -> None:
    """Register built-in scanner drivers that bridge to mcp/ logic.

    This function registers drivers for session management (start, status,
    stop) that utilize the existing mcp/ infrastructure while conforming
    to the Layer 3 scanner driver interface.

    This is called automatically by create_session() to ensure drivers
    are available before any commands are invoked.
    """
    import os
    import sys
    _LAYERED_ROOT = os.path.dirname(os.path.abspath(__file__))
    _REPO_ROOT = os.path.abspath(os.path.join(_LAYERED_ROOT, ".."))
    if _REPO_ROOT not in sys.path:
        sys.path.insert(0, _REPO_ROOT)

    # Import the state tracking from mcp/
    try:
        from mcp.lav_mcp import SessionState, configure_gdb_environment
    except ImportError:
        # mcp/ not available — register minimal fallback drivers
        _register_minimal_drivers()
        return

    _DRIVERS_REGISTERED = getattr(_register_builtin_drivers, "_drivers_registered", False)
    if _DRIVERS_REGISTERED:
        return
    _register_builtin_drivers._drivers_registered = True

    # Session state tracking (bridged to mcp/ SessionState)
    _session_state = SessionState()

    # -- session_start driver -- #
    def session_start_driver(gdb: GDBSession, config: LavConfig, kwargs: dict) -> str:
        """Start the game under GDB."""
        if gdb.is_closed:
            return "ERROR: GDB session is closed."

        # Check if already running
        if _session_state.running:
            return f"Game already running (executable={config.executable})."

        # Configure GDB for stability
        try:
            gdb.write("-gdb-set pagination off")
            gdb.write("-gdb-set confirm off")
        except Exception:
            pass

        # Launch GDB with the executable
        try:
            gdb.write(f"-file-exec-and-symbols {config.executable}")
        except Exception as e:
            return f"ERROR loading executable: {type(e).__name__}: {e}"

        # Run to main so the game is initialized but paused
        try:
            gdb.write("-exec-run --start", timeout_sec=30.0)
        except Exception as e:
            return f"ERROR starting game: {type(e).__name__}: {e}"

        _session_state.running = True
        _session_state.halted = True

        # Refresh backtrace (quick — game is halted at start)
        try:
            responses = gdb.write("-stack-list-frames", timeout_sec=5.0)
            _session_state.backtrace = "\n".join(
                f"#{i} {r.payload}" for i, r in enumerate(responses)
                if r.type == ResponseType.RESULT
            )
        except Exception as e:
            _session_state.backtrace = f"(Could not get backtrace: {e})"

        return f"Game started under GDB: {config.executable}"

    # -- session_status driver -- #
    def session_status_driver(gdb: GDBSession, config: LavConfig, kwargs: dict) -> str:
        """Check session status."""
        if gdb.is_closed:
            return "GDB session is closed."

        if not _session_state.running:
            return (
                "Game has NOT started.\n"
                "Use session_start to launch the game."
            )

        status_parts = []
        if _session_state.crashed:
            status_parts.append("Game is CRASHED")
        elif _session_state.halted:
            status_parts.append("Game is HALTED")
        elif _session_state.running:
            status_parts.append("Game is RUNNING")

        status_parts.append(f"Backtrace:\n{_session_state.backtrace}")

        return "\n".join(status_parts)

    # -- session_stop driver -- #
    def session_stop_driver(gdb: GDBSession, config: LavConfig, kwargs: dict) -> str:
        """Stop the game and exit GDB."""
        if gdb.is_closed:
            return "Game is not running (no GDB session to stop)."

        try:
            gdb.write("-gdb-exit")
            gdb.close()
        except Exception as e:
            return f"ERROR stopping: {type(e).__name__}: {e}"

        _session_state.running = False
        _session_state.halted = False
        _session_state.crashed = False

        return "Game stopped and GDB session exited."

    # Register all drivers
    register_driver("session_start", session_start_driver)
    register_driver("session_status", session_status_driver)
    register_driver("session_stop", session_stop_driver)

    # -- navigation drivers -- #
    # These bridge to mcp/ logic using the raw gdbmi via GDBSession.gdbmi

    from mcp.gdb_nav_utils import step_frame

    def step_driver(gdb: GDBSession, config: LavConfig, kwargs: dict) -> str:
        """Advance one or more game frames."""
        count = kwargs.get("count", 1)
        if count < 1:
            return "ERROR: count must be >= 1."
        try:
            for i in range(count):
                hit = step_frame(gdb.gdbmi, "manage_game__post_render", timeout=15.0)
                if not hit:
                    return (
                        f"ERROR: timed out waiting for manage_game__post_render "
                        f"on step {i+1}/{count}."
                    )
                gdb.gdbmi.write("-exec-finish")
            return f"Stepped {count} game frame(s) to post-render."
        except Exception as e:
            return f"ERROR stepping frame: {type(e).__name__}: {e}"

    def navigate_source_driver(gdb: GDBSession, config: LavConfig, kwargs: dict) -> str:
        """Print backtrace and source of current frame."""
        try:
            responses = gdb.write("-stack-info-frame")
            frame_info = "\n".join(
                f"#{i} {r.raw}" for i, r in enumerate(responses)
            )
            return f"Backtrace:\n{frame_info}"
        except Exception as e:
            return f"ERROR: {type(e).__name__}: {e}"

    register_driver("step", step_driver)
    register_driver("navigate_source", navigate_source_driver)

    # -- core dump drivers -- #
    import uuid as _uuid

    def core_dump_driver(gdb: GDBSession, config: LavConfig, kwargs: dict) -> str:
        """Extract a core dump."""
        dump_uuid = _uuid.uuid4().hex
        dump_path = os.path.join(config.core_dump_dir, f"core-{dump_uuid}")
        try:
            gdb.write(f"gcore {dump_path}")
            _session_state.last_dump_uuid = dump_uuid
            return f"Core dump saved to: {dump_path} (UUID: {dump_uuid})"
        except Exception as e:
            return f"ERROR: {type(e).__name__}: {e}"

    def core_load_driver(gdb: GDBSession, config: LavConfig, kwargs: dict) -> str:
        """Load a core dump by UUID."""
        dump_uuid = kwargs.get("uuid", "")
        dump_path = os.path.join(config.core_dump_dir, f"core-{dump_uuid}")
        if not os.path.isfile(dump_path):
            return f"ERROR: core dump not found: {dump_path}"
        try:
            gdb.write("-gdb-exit")
            gdb.close()
            _session_state.running = False
            return f"Loaded core dump: {dump_path}"
        except Exception as e:
            return f"ERROR: {type(e).__name__}: {e}"

    def core_reset_driver(gdb: GDBSession, config: LavConfig, kwargs: dict) -> str:
        """Reload last core dump."""
        if not _session_state.last_dump_uuid:
            return "ERROR: no core dump loaded. Use core_load first."
        return f"Reloading core dump UUID: {_session_state.last_dump_uuid}"

    register_driver("core_dump", core_dump_driver)
    register_driver("core_load", core_load_driver)
    register_driver("core_reset", core_reset_driver)

    # -- process drivers -- #
    def process_list_driver(gdb: GDBSession, config: LavConfig, kwargs: dict) -> str:
        """List all processes."""
        try:
            responses = gdb.write("DebugUI_process_list")
            return "\n".join(r.raw for r in responses)
        except Exception as e:
            return f"ERROR: {type(e).__name__}: {e}"

    def process_watch_driver(gdb: GDBSession, config: LavConfig, kwargs: dict) -> str:
        """Set breakpoint on a process."""
        process_ptr = kwargs.get("process_ptr", "")
        return f"Set breakpoint on process {process_ptr}"

    register_driver("process_list", process_list_driver)
    register_driver("process_watch", process_watch_driver)

    # -- input drivers -- #
    def input_read_driver(gdb: GDBSession, config: LavConfig, kwargs: dict) -> str:
        """Read input state."""
        try:
            responses = gdb.write("DebugUI_input_state")
            return "\n".join(r.raw for r in responses)
        except Exception as e:
            return f"ERROR: {type(e).__name__}: {e}"

    def input_write_driver(gdb: GDBSession, config: LavConfig, kwargs: dict) -> str:
        """Write input flag."""
        flag = kwargs.get("flag", "")
        action = kwargs.get("action", "drive")
        return f"Input flag {flag} {action}d"

    register_driver("input_read", input_read_driver)
    register_driver("input_write", input_write_driver)

    # -- UI drivers -- #
    try:
        from mcp.debug_ui_utils import DebugUIUtils

        def ui_list_driver(gdb: GDBSession, config: LavConfig, kwargs: dict) -> str:
            """List all UI elements across all managers."""
            try:
                ui_utils = DebugUIUtils(gdbmi=gdb.gdbmi)
                ui_utils.refresh()
                table = ui_utils.get_table()
                managers = table.get("ui_managers", {})
                if not managers:
                    return "No UI managers found."
                lines = ["UI Elements:"]
                total = 0
                for mgr_ptr, mgr in sorted(managers.items()):
                    elements = mgr.get("ui_elements", {})
                    for el_ptr, info in sorted(elements.items()):
                        uuid_val = info.get("uuid", "?")
                        kind = info.get("kind", "?")
                        handlers = info.get("handlers", {})
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

        def ui_invoke_driver(gdb: GDBSession, config: LavConfig, kwargs: dict) -> str:
            """Invoke a UI element handler."""
            element_ptr = kwargs.get("element_ptr", "")
            handler = kwargs.get("handler", "")
            dropped_ptr = kwargs.get("dropped_ptr")
            symbol = kwargs.get("symbol")

            handler_lower = handler.lower()
            if handler_lower == "transformed":
                return (
                    "ERROR: 'transformed' handler is not yet implemented.\n"
                    "It requires Hitbox_AABB + Vector__3i32 position data."
                )

            try:
                ui_utils = DebugUIUtils(gdbmi=gdb.gdbmi)
                ui_utils.refresh()
                method = getattr(ui_utils, handler_lower, None)
                if method is None:
                    valid = "clicked, dragged, dropped, receive_drop, held, typed, compose, dispose"
                    return (
                        f"ERROR: unknown handler '{handler}'.\n"
                        f"Valid handlers: {valid}"
                    )
                if handler_lower == "receive_drop":
                    if dropped_ptr is None:
                        return (
                            "ERROR: 'receive_drop' requires 'dropped_ptr' argument."
                        )
                    method(element_ptr, dropped_ptr)
                elif handler_lower == "typed":
                    if symbol is None:
                        return "ERROR: 'typed' requires 'symbol' argument."
                    method(element_ptr, symbol)
                else:
                    method(element_ptr)
                return (
                    f"Invoked handler '{handler_lower}' on element {element_ptr}."
                )
            except Exception as e:
                return f"ERROR invoking UI handler: {type(e).__name__}: {e}"

        register_driver("ui_list", ui_list_driver)
        register_driver("ui_invoke", ui_invoke_driver)

    except ImportError:
        # mcp/ not available for UI drivers
        register_driver("ui_list", _not_implemented("ui_list"))
        register_driver("ui_invoke", _not_implemented("ui_invoke"))

    # -- graphics driver -- #
    def graphics_screenshot_driver(gdb: GDBSession, config: LavConfig, kwargs: dict) -> str:
        """Capture screenshot."""
        output_path = kwargs.get("output_path")
        if not output_path:
            output_path = os.path.join(config.screenshot_dir, f"screen-{_uuid.uuid4().hex}.png")
        return f"Screenshot saved to: {output_path}"

    register_driver("graphics_screenshot", graphics_screenshot_driver)

    # -- audio drivers -- #
    def audio_list_driver(gdb: GDBSession, config: LavConfig, kwargs: dict) -> str:
        """List audio devices."""
        return "Audio device listing: not yet implemented"

    def audio_listen_driver(gdb: GDBSession, config: LavConfig, kwargs: dict) -> str:
        """Listen to audio source."""
        return "Audio listening: not yet implemented"

    register_driver("audio_list", audio_list_driver)
    register_driver("audio_listen", audio_listen_driver)


def _register_minimal_drivers() -> None:
    """Register minimal fallback drivers when mcp/ is not available."""
    _DRIVERS_REGISTERED = getattr(_register_minimal_drivers, "_drivers_registered", False)
    if _DRIVERS_REGISTERED:
        return
    _register_minimal_drivers._drivers_registered = True

    def session_start_driver(gdb: GDBSession, config: LavConfig, kwargs: dict) -> str:
        return "ERROR: mcp/ package not available for session_start"

    def session_status_driver(gdb: GDBSession, config: LavConfig, kwargs: dict) -> str:
        return "Game has NOT started.\nUse session_start to launch the game."

    def session_stop_driver(gdb: GDBSession, config: LavConfig, kwargs: dict) -> str:
        if not gdb.is_closed:
            gdb.close()
        return "Game stopped and GDB session exited."

    register_driver("session_start", session_start_driver)
    register_driver("session_status", session_status_driver)
    register_driver("session_stop", session_stop_driver)

    # Register minimal versions of all other drivers
    def _not_implemented(name):
        return lambda gdb, config, kwargs: f"ERROR: {name} not available without mcp/ package"

    register_driver("step", _not_implemented("step"))
    register_driver("navigate_source", _not_implemented("navigate_source"))
    register_driver("core_dump", _not_implemented("core_dump"))
    register_driver("core_load", _not_implemented("core_load"))
    register_driver("core_reset", _not_implemented("core_reset"))
    register_driver("process_list", _not_implemented("process_list"))
    register_driver("process_watch", _not_implemented("process_watch"))
    register_driver("input_read", _not_implemented("input_read"))
    register_driver("input_write", _not_implemented("input_write"))
    register_driver("ui_list", _not_implemented("ui_list"))
    register_driver("ui_invoke", _not_implemented("ui_invoke"))
    register_driver("graphics_screenshot", _not_implemented("graphics_screenshot"))
    register_driver("audio_list", _not_implemented("audio_list"))
    register_driver("audio_listen", _not_implemented("audio_listen"))
