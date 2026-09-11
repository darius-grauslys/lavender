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

from .debug_response import DebugResponse, ResponseType, parse


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
        log_file: str | None = None,
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
        self._log_file = log_file
        self._log_all_responses = log_file is not None  # Log ALL responses if file is set
        self._log_error_responses = True  # Always log errors before hooks

        # Store time module for logging timestamps
        import time
        self._time = time

        # Wrap get_gdb_response to run hooks when called by external code (e.g. step_frame).
        # This ensures breakpoint hooks fire even when responses are read via polling.
        # If _skip_hooks is True (set on the GdbController), hooks are not run during
        # get_gdb_response — call process_hooks_on_raw() separately to run hooks on
        # raw responses. This allows timeout-critical code (like _poll_for_stops) to
        # skip hook overhead during timeout-bounded polling.
        self._skip_hooks = False
        self._orig_get_response = self._gdbmi.get_gdb_response
        self._orig_write = self._gdbmi.write

        def _hooked_get_gdb_response(*args, **kwargs):
            raw = self._orig_get_response(*args, **kwargs)
            # Check the GdbController's _skip_hooks flag (not self._skip_hooks)
            # so external code can control hook behavior on the controller itself.
            if raw and not getattr(self._gdbmi, '_skip_hooks', False):
                self.process_hooks_on_raw(raw)
            return raw

        def _hooked_write(*args, **kwargs):
            """Route GdbController.write() through GDBSession's processing
            so that error logging and hooks fire even when external code
            calls gdb.gdbmi.write() directly (layer contract enforcement).

            Returns raw dicts (same as original pygdbmi write) for backward
            compatibility with existing mcp/ code that expects dict responses.
            Use GDBSession.write() directly for DebugResponse objects.
            """
            # Extract command from args (first positional arg)
            command = args[0] if args else kwargs.get("command", "")
            timeout_sec = kwargs.get("timeout_sec", self._timeout_sec)
            read_response = kwargs.get("read_response", True)
            # Call the original pygdbmi write directly, then parse/hook/log
            try:
                raw = self._orig_write(command, timeout_sec=timeout_sec,
                                       read_response=read_response)
            except TypeError:
                try:
                    raw = self._orig_write(command, timeout_sec=timeout_sec)
                except TypeError:
                    raw = self._orig_write(command)
            except Exception:
                raise

            if raw:
                responses = parse(raw)
                self._last_command = command
                if self._log_all_responses:
                    self._log_responses_to_file(command, responses)
                for r in responses:
                    if r.is_error():
                        self._log_error_response(command, r)
                # Run hooks if not skipped
                if not getattr(self._gdbmi, '_skip_hooks', False):
                    for hook in self._hooks:
                        responses = hook(responses)
                # Return raw dicts for backward compatibility
                return raw
            return raw

        # Expose hook control methods on the GdbController so external code
        # can skip/process hooks without needing a GDBSession reference.
        self._gdbmi.get_gdb_response = _hooked_get_gdb_response
        self._gdbmi._skip_hooks = False
        self._gdbmi.process_hooks_on_raw = self.process_hooks_on_raw
        self._gdbmi.write = _hooked_write

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

    def process_hooks_on_raw(self, raw) -> list[DebugResponse]:
        """Parse raw pygdbmi output and run hooks on it.

        This is used internally by the get_gdb_response wrapper, but can be
        called manually if you need to skip hooks during timeout-critical
        polling and process them afterwards.

        Args:
            raw: Raw output from pygdbmi's get_gdb_response().

        Returns:
            The list of DebugResponse objects after hooks have been applied.
        """
        responses = parse(raw)
        # Log ALL responses to file if configured
        if self._log_all_responses:
            self._log_responses_to_file("poll", responses)
        # Log errors before hooks
        for r in responses:
            if r.is_error() and self._log_error_responses:
                self._log_error_response("poll", r)
        # Run hooks
        for hook in self._hooks:
            responses = hook(responses)
        return responses

    def _log_responses_to_file(self, context: str, responses: list[DebugResponse]) -> None:
        """Log ALL responses to the log file as JSONL.

        Each line is a JSON object with timestamp, context, command, and
        all response details. This provides a complete audit trail of GDB
        interaction for debugging layer contract violations or unexpected
        behavior.
        """
        import json
        import os

        if not self._log_file:
            return

        try:
            # Handle case where _log_file is a directory (resolve to a gdb log file inside)
            log_path = self._log_file
            if os.path.isdir(log_path):
                log_path = os.path.join(log_path, "gdb_responses.jsonl")

            ts = self._time.time()
            for r in responses:
                entry = {
                    "timestamp": ts,
                    "context": context,
                    "command": getattr(self, "_last_command", ""),
                    "type": r.type.value if r.type else None,
                    "message": r.raw.get("message", ""),
                    "reason": r.reason,
                    "func": r.frame.func if r.frame else None,
                    "signal": r.signal_name if r.is_signal() else None,
                    "is_error": r.is_error(),
                    "is_breakpoint_hit": r.is_breakpoint_hit(),
                    "is_signal": r.is_signal(),
                    "is_stopped": r.is_stopped(),
                }
                line = json.dumps(entry)
                with open(log_path, "a") as f:
                    f.write(line + "\n")
        except Exception:
            pass  # Logging must never fail the operation

    def remove_hook(self, hook: GDBHook) -> None:
        """Remove a previously registered hook."""
        if hook in self._hooks:
            self._hooks.remove(hook)

    def clear_hooks(self) -> None:
        """Remove all registered hooks."""
        self._hooks.clear()

    def set_breakpoint(self, function: str, temporary: bool = False) -> str | None:
        """Set a breakpoint on a function.

        Returns the breakpoint number as a string, or None on failure.
        """
        cmd = "-break-insert"
        if temporary:
            cmd += " -t"
        cmd += f" {function}"
        try:
            responses = self.write(cmd)
            for r in responses:
                if r.type == ResponseType.RESULT and r.raw.get("message") == "done":
                    payload = r.payload
                    bkpt = payload.get("bkpt", {})
                    if isinstance(bkpt, list):
                        bkpt = bkpt[0]
                    return bkpt.get("number")
        except Exception:
            pass
        return None

    def register_breakpoint_hook(
        self,
        function: str,
        hook_fn: Callable[[list[DebugResponse]], list[DebugResponse]],
    ) -> None:
        """Register a hook that fires only when the specified function breakpoint is hit.

        This also sets a breakpoint on the function (if not already set).
        """
        self.set_breakpoint(function)
        self.add_hook(self._on_breakpoint_hit(function, hook_fn))

    @staticmethod
    def _on_breakpoint_hit(function: str, hook_fn: GDBHook) -> GDBHook:
        """Create a hook that checks for breakpoint on a specific function."""
        def hook(responses: list[DebugResponse]) -> list[DebugResponse]:
            for r in responses:
                if r.is_breakpoint_hit():
                    # Check if the breakpoint hit is in the target function
                    func = None
                    if r.frame:
                        func = r.frame.func
                    # Also check the raw response for frame info
                    if func is None:
                        payload = r.payload
                        frame = payload.get("frame", {})
                        func = frame.get("func")
                    if func and function in func:
                        return hook_fn(responses)
            return responses

        return hook

    def write(self, command: str, timeout_sec: float | None = None,
              read_response: bool = True) -> list[DebugResponse]:
        """Send a command to GDB and return parsed responses.

        All hooks are invoked on the parsed response list before returning.

        Args:
            command: The GDB/MI command to send.
            timeout_sec: Override the default timeout. None uses self._timeout_sec.
            read_response: If False, don't read the response (for commands like
                -exec-continue that should only write without consuming responses).
        """
        if self._closed:
            raise RuntimeError("GDBSession is closed.")
        # Use provided timeout or default
        if timeout_sec is None:
            timeout_sec = self._timeout_sec

        # pygdbmi write() returns the response list directly.
        # Always use _orig_write (the pygdbmi/patched write, not _hooked_write)
        # to avoid double-parsing when GDBSession.write is called directly.
        # The _hooked_write wrapper on GdbController is for external code
        # that calls gdb.gdbmi.write() directly.
        write_func = self._orig_write

        try:
            raw_write_responses = write_func(command, timeout_sec=timeout_sec,
                                             read_response=read_response)
        except TypeError:
            # GdbController.write may not accept some kwargs in all pygdbmi versions
            try:
                raw_write_responses = write_func(command, timeout_sec=timeout_sec)
            except TypeError:
                raw_write_responses = write_func(command)
        except Exception:
            # Re-raise non-TypeError exceptions (like GdbTimeoutError)
            raise

        # Parse into DebugResponse objects
        responses = parse(raw_write_responses)

        # Store last command for context in response logging
        self._last_command = command

        # Log ALL responses to file if configured
        if self._log_all_responses:
            self._log_responses_to_file(command, responses)

        # Log any error responses before running hooks
        for r in responses:
            if r.is_error():
                self._log_error_response(command, r)

        # Run hooks (middleware) on the parsed responses
        for hook in self._hooks:
            responses = hook(responses)

        return responses

    def _log_error_response(self, command: str, response: DebugResponse) -> None:
        """Log an error response to the log file if one is configured."""
        if self._log_file is None:
            return
        try:
            import json
            import os
            log_path = self._log_file
            if os.path.isdir(log_path):
                log_path = os.path.join(log_path, "gdb_responses.jsonl")
            record = {
                "type": "gdb_error",
                "timestamp": self._time.time(),
                "command": command,
                "error": response.reason,
                "raw": response.raw,
            }
            with open(log_path, "a") as f:
                f.write(json.dumps(record) + "\n")
                f.flush()
        except Exception:
            pass  # logging is best-effort

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
