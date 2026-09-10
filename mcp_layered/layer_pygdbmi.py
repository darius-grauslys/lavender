"""Layer 1b: GDB dispatch layer.

Wraps pygdbmi.GdbController with:
1. Parsing of all responses via debug_response.py
2. A hook system that intercepts every response before returning it to callers

This is the SINGLE gateway through which all GDB interaction occurs.
"""

from __future__ import annotations

from typing import Callable

try:
    from pygdbmi.gdbcontroller import GdbController
    _HAS_PYGDBMI = True
except ImportError:
    _HAS_PYGDBMI = False

from .debug_response import DebugResponse, parse


# Hook type: receives list of DebugResponse, returns (possibly modified) list
GDBHook = Callable[[list[DebugResponse]], list[DebugResponse]]


class GDBSession:
    """Middleware wrapper around pygdbmi.GdbController.

    All GDB commands go through write(), and all responses are parsed via
    debug_response.py before being returned. Registered hooks are called
    on every response list, allowing inspection and modification.

    Example:
        gdb = GDBSession()
        gdb.add_hook(on_breakpoint_stop)
        responses = gdb.write("-exec-continue")
        # hooks ran on 'responses' before this returns
    """

    def __init__(
        self,
        command: list[str] | None = None,
        timeout_sec: float = 15.0,
    ):
        if not _HAS_PYGDBMI:
            raise RuntimeError("pygdbmi is not installed. Cannot create GDBSession.")

        # pygdbmi GdbController takes a 'command' list, e.g. ["/usr/bin/gdb", "--nx"]
        # timeout_sec is passed to write() calls, not the constructor
        self._gdbmi = GdbController(command=command)

        # Apply pygdbmi timeout patching from gdb_nav_utils
        # This ensures all internal pygdbmi calls use the specified timeout
        try:
            from mcp.gdb_nav_utils import patch_gdbmi_timeouts
            self._gdbmi = patch_gdbmi_timeouts(self._gdbmi, timeout_sec)
        except ImportError:
            pass  # mcp/ not available, use default pygdbmi timeouts

        self._hooks: list[GDBHook] = []
        self._closed = False
        self._timeout_sec = timeout_sec

    @property
    def gdb_path(self) -> str:
        """The GDB executable path being used."""
        cmd = getattr(self._gdbmi, "command", None)
        if cmd:
            return cmd[0]
        return "/usr/bin/gdb"

    @property
    def gdbmi(self):
        """Raw pygdbmi GdbController (for backward compat with mcp/ drivers)."""
        return self._gdbmi

    def add_hook(self, hook: GDBHook) -> None:
        """Register a hook to be called on every GDB response.

        Hooks are called in registration order. Each hook receives the list
        of DebugResponse objects and must return a (possibly modified) list
        of DebugResponse objects.
        """
        if hook not in self._hooks:
            self._hooks.append(hook)

    def remove_hook(self, hook: GDBHook) -> None:
        """Remove a previously registered hook."""
        if hook in self._hooks:
            self._hooks.remove(hook)

    def clear_hooks(self) -> None:
        """Remove all registered hooks."""
        self._hooks.clear()

    def write(self, command: str, timeout_sec: float | None = None) -> list[DebugResponse]:
        """Send a command to GDB and return parsed responses.

        All hooks are invoked on the parsed response list before returning.

        Args:
            command: The GDB/MI command to send.
            timeout_sec: Override the default timeout. None uses self._timeout_sec.
        """
        if self._closed:
            raise RuntimeError("GDBSession is closed.")
        # Use provided timeout or default
        if timeout_sec is None:
            timeout_sec = self._timeout_sec

        # pygdbmi write() returns the response list directly
        try:
            raw_write_responses = self._gdbmi.write(command, timeout_sec=timeout_sec)
        except TypeError:
            # GdbController.write may not accept timeout_sec in all pygdbmi versions
            raw_write_responses = self._gdbmi.write(command)
        except Exception:
            # Re-raise non-TypeError exceptions (like GdbTimeoutError)
            raise

        # Parse into DebugResponse objects
        responses = parse(raw_write_responses)

        # Run hooks (middleware) on the parsed responses
        for hook in self._hooks:
            responses = hook(responses)

        return responses

    def write_raw(self, command: str) -> list[dict]:
        """Send a command to GDB and return raw (unparsed) responses.

        Hooks are NOT called for this method. Use write() for hook support.
        """
        if self._closed:
            raise RuntimeError("GDBSession is closed.")
        return self._gdbmi.write(command)

    def get_responses(self) -> list[DebugResponse]:
        """Read pending responses from GDB without sending a command.

        Hooks are invoked on the parsed responses.
        """
        if self._closed:
            raise RuntimeError("GDBSession is closed.")
        raw = self._gdbmi.get_gdb_response()
        responses = parse(raw)
        for hook in self._hooks:
            responses = hook(responses)
        return responses

    def close(self) -> int:
        """Exit GDB. Returns exit code."""
        if self._closed:
            return 0
        self._closed = True
        return self._gdbmi.exit()

    @property
    def is_closed(self) -> bool:
        return self._closed

    def __enter__(self) -> "GDBSession":
        return self

    def __exit__(self, *args) -> None:
        self.close()


# Convenience: a no-op hook that just logs all responses
def logging_hook_factory(log_fn: Callable[[list[DebugResponse]], None]) -> GDBHook:
    """Create a hook that calls log_fn on every response list."""
    def hook(responses: list[DebugResponse]) -> list[DebugResponse]:
        log_fn(responses)
        return responses
    return hook


# Convenience: hook that triggers a callback only on breakpoint hits
def on_breakpoint_hook_factory(
    callback: Callable[[list[DebugResponse]], None]
) -> GDBHook:
    """Create a hook that calls callback only when a breakpoint is hit."""
    def hook(responses: list[DebugResponse]) -> list[DebugResponse]:
        for resp in responses:
            if resp.is_breakpoint_hit():
                callback(responses)
                break
        return responses
    return hook
