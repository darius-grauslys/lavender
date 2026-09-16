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

# Error records are deduplicated per (command, error): only the first
# GDB_ERROR_LOG_LIMIT occurrences of each distinct pair are written to the
# log; repeats are counted and summarized once at close(). A single
# repeatedly-failing command (e.g. an unsupported MI command retried by a
# bursty hook) must not be able to flood the session log.
GDB_ERROR_LOG_LIMIT = 3

# Signal name → signal number mapping (POSIX standard signals 1-31)
_SIGNAL_NUM_TO_NAME = {
    "1": "SIGHUP", "2": "SIGINT", "3": "SIGQUIT", "4": "SIGILL",
    "5": "SIGTRAP", "6": "SIGABRT", "7": "SIGBUS", "8": "SIGFPE",
    "9": "SIGKILL", "10": "SIGUSR1", "11": "SIGSEGV", "12": "SIGUSR2",
    "13": "SIGPIPE", "14": "SIGALRM", "15": "SIGTERM", "16": "SIGSTKFLT",
    "17": "SIGCHLD", "18": "SIGCONT", "19": "SIGSTOP", "20": "SIGTSTP",
    "21": "SIGTTIN", "22": "SIGTTOU", "23": "SIGURG", "24": "SIGXCPU",
    "25": "SIGXFSZ", "26": "SIGVTALRM", "27": "SIGPROF", "28": "SIGWINCH",
    "29": "SIGIO", "30": "SIGPWR", "31": "SIGSYS",
}


def detect_signal(responses: list[DebugResponse]) -> str | None:
    """Detect if any response is a signal-received stop.

    Returns the signal name (e.g. 'SIGABRT') if a signal was received,
    otherwise None.

    This is the unified signal detection logic in layer_pygdbmi. All layers
    above should use this function instead of implementing their own.
    """
    for r in responses:
        if r.is_signal():
            # is_signal() returns True for DebugResponse objects where
            # type==NOTIFY, reason=='signal-received'
            # The signal name is stored in signal_name field
            sig_name = r.signal_name
            if sig_name:
                return sig_name
            # Fallback: try signal number → name mapping from raw payload
            sig_num = r.raw.get("payload", {}).get("signal", "")
            if sig_num:
                return _SIGNAL_NUM_TO_NAME.get(str(sig_num), f"SIG{sig_num}")
    return None


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
        timeout_sec: float = 0.0,  # 0 means no overall timeout (unbounded)
        log_file: str | None = None,
        activity_timeout: bool = True,
        idle_timeout: float = 5.0,  # Reset on each response; kills idle loops
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
        self._timeout_sec = timeout_sec  # 0 = unbounded (no overall timeout)
        self._activity_timeout = activity_timeout  # Use activity-based polling
        self._idle_timeout = idle_timeout  # Reset on each response; kills idle loops
        self._log_file = log_file
        self._log_all_responses = log_file is not None  # Log ALL responses if file is set
        self._log_error_responses = True  # Always log errors before hooks
        # (command, error) -> occurrences seen. Dedupes the gdb_error records
        # (see _log_error_response / GDB_ERROR_LOG_LIMIT); repeats are
        # summarized once in close().
        self._error_log_counts: dict[tuple[str, str], int] = {}
        self._last_signal: str | None = None  # Last detected signal (e.g. 'SIGABRT')
        # True while hooks are being run from *inside* a get_gdb_response/write
        # (a nested read). A hook that issues GDB commands while nested deadlocks
        # the connection, so hooks that need GDB I/O must check this and defer.
        # The timeout-critical poll path (_poll_for_stops) runs hooks via
        # process_hooks_on_raw() with this flag False = a safe (stopped) context.
        self._in_nested_read = False

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
                # Nested read: hooks run inside get_gdb_response. Flag it so any
                # hook doing GDB I/O can defer (a nested GDB command deadlocks).
                self._in_nested_read = True
                try:
                    self.process_hooks_on_raw(raw)
                finally:
                    self._in_nested_read = False
            return raw

        def _activity_timeout_get_gdb_response(*args, **kwargs):
            """get_gdb_response with activity-based timeout.

            If _activity_timeout is enabled on the session, this polls
            with the unified timeout logic instead of returning immediately.

            The timeout_sec kwarg is used as the call_timeout (pygdbmi timeout
            per individual get_gdb_response call). The overall deadline is
            controlled by idle_timeout (which resets on each response).
            """
            if not self._activity_timeout:
                return _hooked_get_gdb_response(*args, **kwargs)

            # timeout_sec from caller is treated as call_timeout (per-response wait)
            call_timeout = kwargs.get("timeout_sec", 0.5)
            idle_timeout = kwargs.get("idle_timeout", None) or self._idle_timeout

            # Poll with activity-based timeout:
            # - overall_timeout=0 (unbounded): no total deadline, world loading ok
            # - idle_timeout: resets on each response, catches infinite loops
            # - call_timeout: how long to wait for each individual pygdbmi response
            raw = self.poll_with_activity_timeout(
                overall_timeout=0,  # 0 = unbounded
                idle_timeout=idle_timeout,
                call_timeout=call_timeout,
            )

            # Run hooks if not skipped
            if raw and not getattr(self._gdbmi, '_skip_hooks', False):
                self._in_nested_read = True
                try:
                    self.process_hooks_on_raw(raw)
                finally:
                    self._in_nested_read = False

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
            timeout_sec = kwargs.get("timeout_sec")
            if timeout_sec is None or timeout_sec == 0:
                # 0 = unbounded, but pygdbmi needs a positive timeout
                timeout_sec = self._timeout_sec if self._timeout_sec > 0 else 15.0
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
                # Run hooks if not skipped (nested context: a write that reads a
                # response; flag it so GDB-I/O hooks can defer).
                if not getattr(self._gdbmi, '_skip_hooks', False):
                    self._in_nested_read = True
                    try:
                        for hook in self._hooks:
                            responses = hook(responses)
                    finally:
                        self._in_nested_read = False
                # Return raw dicts for backward compatibility
                return raw
            return raw

        # Expose hook control methods on the GdbController so external code
        # can skip/process hooks without needing a GDBSession reference.
        # Use activity-based timeout get_gdb_response if enabled, otherwise
        # use the basic hooked version.
        if self._activity_timeout:
            self._gdbmi.get_gdb_response = _activity_timeout_get_gdb_response
        else:
            self._gdbmi.get_gdb_response = _hooked_get_gdb_response
        self._gdbmi._skip_hooks = False
        self._gdbmi.process_hooks_on_raw = self.process_hooks_on_raw
        self._gdbmi.write = _hooked_write
        # Expose activity-based timeout polling method
        self._gdbmi.poll_with_activity_timeout = self.poll_with_activity_timeout

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

    @property
    def last_signal(self) -> str | None:
        """The last detected signal (e.g. 'SIGABRT'), or None if no signal."""
        return self._last_signal

    def reset_signal_state(self) -> None:
        """Clear the last detected signal state."""
        self._last_signal = None

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
        # Track signal detection
        sig = detect_signal(responses)
        if sig:
            self._last_signal = sig
        # Run hooks
        for hook in self._hooks:
            responses = hook(responses)
        return responses

    def poll_with_activity_timeout(
        self,
        overall_timeout: float | None = None,
        idle_timeout: float | None = None,
        call_timeout: float = 0.5,
    ) -> list | None:
        """Poll for GDB responses with activity-based timeout.

        This is the unified timeout logic used by all layer_pygdbmi operations.
        The idle timeout resets each time a non-None response is received, so
        long-running operations that produce periodic output don't time out.

        Args:
            overall_timeout: Maximum total time to wait. None or 0 means
                unbounded (no overall deadline). Uses session's _timeout_sec
                by default.
            idle_timeout: Maximum time to wait without any response before
                giving up. Each response resets this timer. Uses session's
                _idle_timeout by default.
            call_timeout: How long to wait for each individual get_gdb_response()
                call before retrying.

        Returns:
            The raw response from get_gdb_response(), or None if timed out.

        The logic:
        1. Set overall deadline (overall_timeout from now), or no deadline if 0/None.
        2. Set idle deadline (idle_timeout from now).
        3. Call get_gdb_response with call_timeout.
        4. If we get a non-None response, reset the idle deadline.
        5. If we get None or an exception, don't reset idle deadline.
        6. Continue until idle deadline is exceeded (or overall deadline if set).
        """
        import time
        if overall_timeout is None:
            overall_timeout = self._timeout_sec  # 0 = unbounded
        if idle_timeout is None:
            idle_timeout = self._idle_timeout

        start_time = time.monotonic()
        has_deadline = overall_timeout > 0
        deadline = start_time + overall_timeout if has_deadline else None
        idle_deadline = start_time + idle_timeout

        while True:
            # Check overall deadline
            if has_deadline and time.monotonic() >= deadline:
                return None

            # Wait up to the lesser of idle time and call_timeout
            remaining_idle = idle_deadline - time.monotonic()
            current_timeout = min(call_timeout, remaining_idle)
            if current_timeout <= 0:
                break

            try:
                # Use the original (unwrapped) get_gdb_response to avoid
                # recursion through the activity timeout wrapper
                raw = self._orig_get_response(timeout_sec=current_timeout)
            except Exception:
                # Timeout on get_gdb_response — check idle deadline
                if time.monotonic() >= idle_deadline:
                    return None
                if has_deadline and time.monotonic() >= deadline:
                    return None
                continue

            if raw is None:
                # No response available
                if time.monotonic() >= idle_deadline:
                    return None
                if has_deadline and time.monotonic() >= deadline:
                    return None
                continue

            # Got a response — reset idle deadline
            idle_deadline = time.monotonic() + idle_timeout
            return raw

        return None

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

    def _resolve_log_path(self) -> str | None:
        """The JSONL file this session logs to (None if unconfigured).

        Mirrors the resolution in _log_responses_to_file: a directory becomes
        <dir>/gdb_responses.jsonl; a file path is used as-is (the per-session
        jsonl set via set_log_file)."""
        import os
        if not self._log_file:
            return None
        log_path = self._log_file
        if os.path.isdir(log_path):
            log_path = os.path.join(log_path, "gdb_responses.jsonl")
        return log_path

    def log_record(self, entry: dict) -> bool:
        """Append one structured record to the session's JSONL log — the SAME file
        that carries the GDB-response records — so higher-layer derived data (e.g.
        a process create/remove/error trace) lives alongside the raw GDB audit
        trail and is greppable in one place. The record is written verbatim as one
        JSON line. Returns True if written. Never raises."""
        import json
        import os
        path = self._resolve_log_path()
        if not path:
            return False
        try:
            d = os.path.dirname(path)
            if d:
                os.makedirs(d, exist_ok=True)
            with open(path, "a") as f:
                f.write(json.dumps(entry) + "\n")
            return True
        except Exception:
            return False

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

    def delete_breakpoint(self, number) -> bool:
        """Delete a breakpoint by number (the inverse of set_breakpoint).

        Args:
            number: The breakpoint number (int or str) returned by set_breakpoint.

        Returns:
            True if GDB acknowledged the deletion (^done), False otherwise
            (including when *number* is None — a no-op).
        """
        if number is None:
            return False
        cmd = f"-break-delete {number}"
        try:
            responses = self.write(cmd)
            for r in responses:
                if r.type == ResponseType.RESULT and r.raw.get("message") == "done":
                    return True
        except Exception:
            pass
        return False

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
            # For write(), use the session's timeout (which may be 0 = unbounded)
            # or a default of 15s if the session timeout is 0 (unbounded).
            # The activity-based timeout in get_gdb_response handles long polling.
            timeout_sec = self._timeout_sec if self._timeout_sec > 0 else 15.0

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

        # Track signal detection (layer_pygdbmi unified logic)
        sig = detect_signal(responses)
        if sig:
            self._last_signal = sig

        # Run hooks (middleware) on the parsed responses
        for hook in self._hooks:
            responses = hook(responses)

        return responses

    def _log_error_response(self, command: str, response: DebugResponse) -> None:
        """Log an error response to the log file if one is configured.

        Deduplicated per (command, error): only the first GDB_ERROR_LOG_LIMIT
        occurrences of each distinct pair are written; repeats are counted in
        self._error_log_counts and summarized once by _log_suppressed_errors()
        at close(). Logging is best-effort.
        """
        if self._log_file is None:
            return
        key = (command, response.reason)
        count = self._error_log_counts.get(key, 0) + 1
        self._error_log_counts[key] = count
        if count > GDB_ERROR_LOG_LIMIT:
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

    def _log_suppressed_errors(self) -> None:
        """Write one summary record per (command, error) pair whose repeats
        were suppressed by _log_error_response's dedupe (best-effort)."""
        if self._log_file is None:
            return
        try:
            import json
            import os
            log_path = self._log_file
            if os.path.isdir(log_path):
                log_path = os.path.join(log_path, "gdb_responses.jsonl")
            with open(log_path, "a") as f:
                for (command, error), count in sorted(self._error_log_counts.items()):
                    suppressed = count - GDB_ERROR_LOG_LIMIT
                    if suppressed > 0:
                        f.write(json.dumps({
                            "type": "gdb_error",
                            "timestamp": self._time.time(),
                            "command": command,
                            "error": error,
                            "suppressed_repeats": suppressed,
                            "total": count,
                        }) + "\n")
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
        self._log_suppressed_errors()
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


class BreakpointHook:
    """A named GDB breakpoint paired with a reaction hook, with enable/disable.

    Encapsulates "a breakpoint + the thing that reacts to it" as one toggleable
    unit:

    - ``enable()``  sets the GDB breakpoint (``-break-insert``) and registers the
      reaction hook (fired only for this breakpoint's hits).
    - ``disable()`` deletes the breakpoint (``-break-delete``) and unregisters the
      hook. While disabled the game neither stops here nor reacts.

    This is what makes verbose tracking (e.g. a hit on *every* process
    create/remove) cheap to switch off: a disabled hook has no effect on the
    running game. A future MCP toggle (``trace process on|off``) just calls
    ``enable``/``disable``.

    Two kinds of reaction are supported:
    - ``handler`` (a plain GDBHook, ``responses -> responses``): a lightweight
      reaction fired on every matching hit. It must NOT issue GDB commands.
    - ``capture`` (a callable ``gdb, responses -> event``): a reaction that MAY
      issue GDB commands (e.g. read the callee ``-stack-list-frames`` and the hit
      frame's args). It is run **only in a safe, non-deadlocking context** — the
      object checks ``GDBSession._in_nested_read`` and skips it while hooks run
      nested inside a ``get_gdb_response``/``write`` (where a GDB command would
      deadlock the connection). Its return value is appended to
      :attr:`captured_events`, to be drained by :meth:`consume_events` from a
      safe point (e.g. the step driver's post-work).

    This is how a time-sensitive value (the callee stack, which is gone once the
    transient stop is continued past) is captured *at the hit* yet consumed from
    a guaranteed-safe section.

    ``target`` may be a function name or a ``file:line`` location.

    Example:
        hook = BreakpointHook(gdb, "process.add",
                              "add_process_to__process_table",
                              capture=capture_process_event)
        hook.enable()              # on by default
        ...  # later, at a safe point:
        for event in hook.consume_events():
            log(event)
        hook.disable()             # turn the tracking off
    """

    def __init__(self, gdb, name: str, target: str,
                 handler: GDBHook | None = None,
                 capture: Callable | None = None):
        """
        Args:
            gdb: The GDBSession to attach to.
            name: A short human label (for logs / diagnostics).
            target: A function name, or a "file:line" location, to break at.
            handler: Optional lightweight reaction (``responses -> responses``),
                fired on every matching hit. Must not issue GDB commands.
            capture: Optional ``gdb, responses -> event`` reaction that may issue
                GDB commands; run only in a safe context, result -> captured_events.
        """
        self._gdb = gdb
        self.name = name
        self._target = target
        self._handler = handler
        self._capture = capture
        self._bp_number = None
        self._hook: GDBHook | None = None
        self._enabled = False
        self.captured_events: list = []

    @property
    def enabled(self) -> bool:
        return self._enabled

    @property
    def bp_number(self):
        """The GDB breakpoint number while enabled, else None."""
        return self._bp_number

    @property
    def target(self) -> str:
        return self._target

    def _match(self, r: DebugResponse) -> bool:
        """True if this bp-hit response is at our target (function or file:line)."""
        target = self._target
        if r.frame is not None:
            func, file, line = r.frame.func, r.frame.file, r.frame.line
        else:
            fr = (r.payload or {}).get("frame", {}) or {}
            func, file, line = fr.get("func"), fr.get("file"), fr.get("line")
        if ":" not in target:
            # function target: match on the frame function name
            return bool(func) and (target in func)
        # file:line target: match on frame file:line
        file_part, _, line_part = target.rpartition(":")
        return (file is not None and str(line) == str(line_part) and file_part in file)

    def _react(self, responses: list[DebugResponse]) -> list[DebugResponse]:
        """Run the reactions for a matching hit: handler (always) + capture (only
        in a safe, non-nested context)."""
        if self._handler is not None:
            responses = self._handler(responses)
        if self._capture is not None and not self._gdb._in_nested_read:
            try:
                event = self._capture(self._gdb, responses)
            except Exception:
                event = None  # a capture failure must never break the driver
            if event is not None:
                self.captured_events.append(event)
        return responses

    def _make_hook(self) -> GDBHook:
        """Build the reaction hook for the target (function or file:line)."""
        def hook(responses: list[DebugResponse]) -> list[DebugResponse]:
            for r in responses:
                if r.is_breakpoint_hit() and self._match(r):
                    return self._react(responses)
            return responses
        return hook

    def consume_events(self) -> list:
        """Drain and return the events captured since the last call (safe point).

        Call this from a safe, non-deadlocking section (e.g. the step driver's
        post-work) to read the stack traces / args captured at the hits without
        issuing any GDB command here.
        """
        events, self.captured_events = self.captured_events, []
        return events

    def enable(self) -> bool:
        """Set the breakpoint + register the hook. Idempotent.

        Returns True if the breakpoint is active after the call; False if it could
        not be set (e.g. the symbol is absent/inlined, so no bp was created).
        """
        if self._enabled:
            return True
        self._bp_number = self._gdb.set_breakpoint(self._target)
        if self._bp_number is None:
            return False  # leave disabled
        self._hook = self._make_hook()
        self._gdb.add_hook(self._hook)
        self._enabled = True
        return True

    def disable(self) -> None:
        """Delete the breakpoint + unregister the hook. Idempotent."""
        if not self._enabled:
            return
        if self._hook is not None:
            self._gdb.remove_hook(self._hook)
            self._hook = None
        if self._bp_number is not None:
            self._gdb.delete_breakpoint(self._bp_number)
            self._bp_number = None
        self._enabled = False

    def __repr__(self) -> str:
        state = "enabled" if self._enabled else "disabled"
        return f"BreakpointHook(name={self.name!r}, target={self._target!r}, {state})"
