"""
gdb_nav_utils.py — High-level GDB navigation helpers.

Reduces the friction of moving through the game loop in gdb by wrapping
raw MI3 command sequences into ergonomic calls. The module is intentionally
small: it has no base class and no state of its own. Each public function
takes a ``GdbController`` (or ``GDBFrameController``-compatible) instance and
operates on it directly.

Public API (currently only one function):
    step_frame(breakpoint_func, timeout=5.0) -> bool

Usage:
    from pygdbmi.gdbcontroller import GdbController
    from mcp.gdb_nav_utils import step_frame

    gdb = GdbController()
    # ... load binary, run to main, etc. ...

    if step_frame(gdb, "manage_game__post_render", timeout=5.0):
        print("Successfully stepped to end of frame")
    else:
        print("Timed out — infinite loop or breakpoint storm detected")
"""

from __future__ import annotations

import time
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pygdbmi.gdbcontroller import GdbController


# --------------------------------------------------------------------------- #
#  Timeout configuration                                                      #
# --------------------------------------------------------------------------- #
# pygdbmi's GdbController.write() and get_gdb_response() both default to a
# 1-second timeout.  For game-loop stepping and scene loading this is far too
# short — frames can take several seconds under GDB on slow machines or with
# GL context initialization.  We patch GdbController instances to use 15s
# by default so callers don't need to remember to pass timeout_sec everywhere.
_PYGDBMI_TIMEOUT = 15.0


def patch_gdbmi_timeouts(
    gdbmi: "GdbController | None",
    timeout: float = _PYGDBMI_TIMEOUT,
) -> "GdbController | None":
    """Patch a GdbController instance to use a longer default timeout.

    This wraps ``write()`` and ``get_gdb_response()`` so that when no
    explicit ``timeout_sec`` is passed, *timeout* is used instead of
    pygdbmi's 1-second default.

    This can be applied to any GdbController instance — the patches are
    per-instance (not global), so other code that uses pygdbmi with its
    default timeout is unaffected.

    Args:
        gdbmi: The GdbController instance to patch.  If None, returns None.
        timeout: The default timeout in seconds (default: 15.0).

    Returns:
        The same GdbController instance, with patched methods.
    """
    if gdbmi is None:
        return None

    _orig_write = gdbmi.write
    _orig_get_response = gdbmi.get_gdb_response

    def _write(
        cmd,
        timeout_sec: float = timeout,
        raise_error_on_timeout: bool = True,
        read_response: bool = True,
        **kwargs,
    ):
        return _orig_write(
            cmd,
            timeout_sec=timeout_sec,
            raise_error_on_timeout=raise_error_on_timeout,
            read_response=read_response,
            **kwargs,
        )

    def _get_gdb_response(
        timeout_sec: float = timeout,
        raise_error_on_timeout: bool = True,
    ):
        return _orig_get_response(
            timeout_sec=timeout_sec,
            raise_error_on_timeout=raise_error_on_timeout,
        )

    gdbmi.write = _write
    gdbmi.get_gdb_response = _get_gdb_response
    return gdbmi


def _normalize_resp(resp) -> list[dict]:
    """Normalize a pygdbmi response into a list of dict records.

    pygdbmi's get_gdb_response() and write() can return:
    - A list of dict records
    - A single dict record
    - None (on timeout / gdb exit)
    - A dict with payload=None

    This helper normalizes all of these into a clean list of dicts,
    filtering out None entries and non-dict entries.
    """
    if resp is None:
        return []
    if isinstance(resp, dict):
        return [resp] if resp else []
    if isinstance(resp, list):
        return [r for r in resp if isinstance(r, dict)]
    return []


def _is_breakpoint_hit_response(mi_record: dict | None) -> bool:
    """Check if an MI response indicates a breakpoint was hit.

    Args:
        mi_record: A dictionary from ``gdbmi.get_gdb_response()``.

    Returns:
        True if this record represents a breakpoint-hit stop.
    """
    if not mi_record:
        return False
    if mi_record.get("type") != "notify":
        return False
    if mi_record.get("message") != "stopped":
        return False
    payload = mi_record.get("payload") or {}
    reason = payload.get("reason", "")
    return reason == "breakpoint-hit"


def _get_breakpoint_number(mi_record: dict | None) -> int | None:
    """Extract the breakpoint number from a breakpoint-hit response.

    In a ``stopped`` notify with ``reason: "breakpoint-hit"``, the breakpoint
    number is in ``payload.bkptno``. (On MI3 ``result`` records from
    ``-break-insert``, it's in ``payload.bkpt.number`` — see
    ``_add_temporary_breakpoint``.)

    Args:
        mi_record: A breakpoint-hit MI response (a ``stopped`` notify).

    Returns:
        The breakpoint number as an int, or None if not present.
    """
    if not mi_record:
        return None
    payload = mi_record.get("payload") or {}
    # The standard field for a breakpoint-hit stopped event is "bkptno".
    number = payload.get("bkptno")
    if number is not None:
        try:
            return int(number)
        except (ValueError, TypeError):
            pass
    # Fallback: some MI variants put it in bkpt.number (e.g. -break-insert done).
    bkpt = payload.get("bkpt", {})
    if isinstance(bkpt, list) and bkpt:
        bkpt = bkpt[0]
    if isinstance(bkpt, dict):
        number = bkpt.get("number")
        if number is not None:
            return int(number)
    return None


def _get_breakpoint_location(mi_record: dict | None) -> str | None:
    """Extract the breakpoint's function name from a breakpoint-hit response.

    Handles two record shapes:
    - ``*stopped`` notify (breakpoint-hit): function is in ``payload.frame.func``.
    - ``-break-insert`` result (done): function is in ``payload.bkpt.func``.

    Args:
        mi_record: A breakpoint-hit MI response.

    Returns:
        The function name as a string, or None if not present.
    """
    if not mi_record:
        return None
    payload = mi_record.get("payload") or {}

    # -break-insert result: info is in payload.bkpt.
    bkpt = payload.get("bkpt", {})
    if isinstance(bkpt, list) and bkpt:
        bkpt = bkpt[0]
    if isinstance(bkpt, dict) and bkpt.get("func"):
        return bkpt.get("func")

    # *stopped (breakpoint-hit) notify: func is in payload.frame.func.
    frame = payload.get("frame", {})
    if isinstance(frame, dict):
        return frame.get("func")

    return None


def _get_signal_from_stopped(record: dict) -> str | None:
    """Extract signal name from a *stopped (signal-received) record.

    Returns the signal name (e.g. 'SIGABRT', 'SIGSEGV') if this is a
    signal-received stop, otherwise None.
    """
    if not isinstance(record, dict):
        return None
    if record.get("type") != "notify" or record.get("message") != "stopped":
        return None

    payload = record.get("payload") or {}
    if not isinstance(payload, dict):
        return None

    reason = payload.get("reason", "")
    if reason != "signal-received":
        return None

    signal = payload.get("signal-name", "")
    if signal:
        return signal

    # Fallback: signal number → name mapping
    sig = payload.get("signal", "")
    if sig:
        sig_map = {
            "6": "SIGABRT",
            "11": "SIGSEGV",
            "8": "SIGFPE",
            "4": "SIGILL",
            "7": "SIGBUS",
            "13": "SIGPIPE",
            "1": "SIGHUP",
            "15": "SIGTERM",
            "2": "SIGINT",
            "9": "SIGKILL",
        }
        return sig_map.get(str(sig), f"SIG{sig}")

    return None


def _add_temporary_breakpoint(gdb: "GdbController", func_name: str, timeout: float) -> int:
    """Set a temporary breakpoint at the given function.

    Uses ``-break-insert -t`` (temporary breakpoint) via MI3 so we get
    a proper result record with the breakpoint number. The breakpoint
    is automatically deleted after one hit, avoiding stale breakpoint
    accumulation across calls.

    Args:
        gdb: A GdbController instance.
        func_name: The C function name to break at.
        timeout: pygdbmi response timeout in seconds.

    Returns:
        The breakpoint number assigned by gdb, or 1 as a fallback.
    """
    # Use MI3 -break-insert with -t (temporary) flag.
    resp = gdb.write(f"-break-insert -t {func_name}")

    # Normalize and drain the response list to find the breakpoint-created record.
    for record in _normalize_resp(resp):
        if record.get("type") == "result" and record.get("message") == "done":
            payload = record.get("payload") or {}
            bkpt = payload.get("bkpt")
            if isinstance(bkpt, list) and bkpt:
                bkpt = bkpt[0]
            if isinstance(bkpt, dict):
                number = bkpt.get("number")
                if number is not None:
                    return int(number)

    # Fallback: no breakpoint number found in the response.
    return 1


def _delete_breakpoint(gdb: "GdbController", bpnum: int, timeout: float) -> None:
    """Delete a breakpoint by number (cleanup helper).

    Uses ``read_response=False`` so the ``-break-delete`` result record stays
    in the pipe and is consumed by the next ``gdb.write()`` call (e.g. the next
    ``-break-insert`` in a subsequent ``step_frame`` call). This avoids
    accidentally consuming a ``*stopped`` event that might arrive concurrently,
    and keeps cleanup from blocking on ``get_gdb_response()``.
    """
    try:
        gdb.write(f"-break-delete {bpnum}", read_response=False)
    except Exception:
        pass  # best-effort cleanup


def _continue(gdb: "GdbController", timeout: float) -> None:
    """Send -exec-continue WITHOUT reading any response.

    This is the critical fix for the "works first time, fails every sequential
    time" bug. pygdbmi's ``write()`` with the default ``read_response=True``
    sends the command *and* reads the response, which means it can consume the
    ``*stopped`` (breakpoint-hit) notify record before ``_poll_for_stops`` gets
    a chance to see it.

    The failure mode was:

    * On the **first** call (program starting from ``main``), the program takes
      a while to reach ``manage_game__post_render`` (SDL/GL init, etc.). The
      ``*stopped`` doesn't arrive within pygdbmi's 0.2-second
      additional-output-check window, so ``write()`` only reads ``*running``.
      ``_poll_for_stops`` then polls and successfully gets ``*stopped``.

    * On **sequential** calls (game loop already running), the breakpoint is
      hit almost immediately. ``*running`` and ``*stopped`` can arrive in the
      same output chunk. pygdbmi's ``write()`` reads both, consuming
      ``*stopped``. ``_poll_for_stops`` then polls for a ``*stopped`` that was
      already eaten and times out.

    The fix: use ``read_response=False`` so ``write()`` only writes the command
    to gdb's stdin without reading anything. All response reading is deferred
    to ``_poll_for_stops``, which correctly ignores ``*running`` and other
    non-breakpoint-hit records, only acting on ``breakpoint-hit`` stops.
    """
    try:
        gdb.write("-exec-continue", read_response=False)
    except Exception:
        pass  # gdb may have exited; _poll_for_stops will handle the timeout


def _poll_for_stops(
    gdb: "GdbController",
    target_bpnum: int,
    deadline: float,
    timeout: float,
) -> tuple[bool, str | None]:
    """Poll gdb responses until we hit the target breakpoint, timeout, or EOF.

    Args:
        gdb: A GdbController instance.
        target_bpnum: The breakpoint number we're waiting for.
        deadline: Absolute time by which we must give up.
        timeout: pygdbmi response timeout in seconds for each get_gdb_response call.

    Returns:
        A tuple of (hit_target, last_stop_func):
        - If the target breakpoint was hit, returns (True, func_name).
        - If timeout, returns (False, reason_description).
        - If an unexpected breakpoint was hit, returns (False, "unexpected_bp").

    Note:
        ``GdbTimeoutError`` from pygdbmi is expected when the program is still
        running and hasn't produced any output yet. We catch it and keep
        polling within the deadline, using a short retry interval to avoid
        busy-waiting.

        This function is the **sole consumer** of gdb responses in the
        ``step_frame`` flow. Because ``_continue`` now uses
        ``read_response=False``, all notify records (``*running``,
        ``*stopped``, ``library-loaded``, etc.) arrive here via
        ``get_gdb_response``. Non-breakpoint-hit records are silently ignored;
        only ``breakpoint-hit`` stops are acted upon.
    """
    # Use short poll intervals so we don't exceed the deadline by much.
    poll_interval = min(timeout, 0.5)

    # If the GdbController has our hook wrapper, skip hooks during the
    # timeout-bounded get_gdb_response call, then process them separately
    # so hook overhead doesn't eat into our timeout budget.
    has_hook_wrapper = hasattr(gdb, '_skip_hooks')
    has_hook_processor = hasattr(gdb, 'process_hooks_on_raw')

    while time.monotonic() < deadline:
        if has_hook_wrapper:
            gdb._skip_hooks = True
        try:
            resp = gdb.get_gdb_response(timeout_sec=poll_interval)
        except Exception:
            # pygdbmi timeout — program is still running, no output yet.
            # Check if we've exceeded the deadline.
            if time.monotonic() >= deadline:
                return False, "timeout"
            continue
        finally:
            if has_hook_wrapper:
                gdb._skip_hooks = False

        if resp is None:
            # gdb exited or no response available.
            return False, "gdb_no_response"

        # Process hooks separately (outside the timeout boundary)
        if has_hook_processor:
            gdb.process_hooks_on_raw(resp)

        for record in _normalize_resp(resp):
            if _is_breakpoint_hit_response(record):
                bpnum = _get_breakpoint_number(record)
                func = _get_breakpoint_location(record)
                if bpnum == target_bpnum:
                    return True, func
                else:
                    # Unexpected breakpoint — caller should continue.
                    return False, "unexpected_bp"

            # Detect signal-received stops (SIGABRT, SIGSEGV, etc.)
            signal = _get_signal_from_stopped(record)
            if signal:
                return False, f"signal_{signal}"

    return False, "timeout"


def step_frame_detailed(
    gdb: "GdbController",
    breakpoint_func: str = "manage_game__post_render",
    timeout: float = 5.0,
) -> tuple[bool, str | None]:
    """Advance execution to a specific frame in the game loop.

    Returns a tuple of (hit_target, stop_reason):
        - (True, None): Target breakpoint was hit.
        - (False, "timeout"): Timeout expired.
        - (False, "signal_SIGABRT"): Game crashed with a signal (SIGABRT, SIGSEGV, etc.)
        - (False, "unexpected_bp"): Unexpected breakpoint fired (then timeout).
        - (False, "gdb_no_response"): GDB exited or no response.

    Sets a temporary breakpoint at *breakpoint_func* using MI3
    ``-break-insert -t``, then runs gdb until that breakpoint fires or
    *timeout* seconds elapse. If an unexpected breakpoint fires during the
    run, gdb is continued again (the timeout keeps ticking), which guards
    against breakpoint storms and infinite loops that never reach the
    target frame.

    Args:
        gdb: A ``GdbController`` instance with a binary loaded and
            execution paused at ``main`` (or similar starting point).
        breakpoint_func: The C function name to break at. Defaults to
            ``manage_game__post_render``, the canonical "end of scene loop"
            frame.
        timeout: Maximum seconds to wait for the target breakpoint.
            Defaults to 5.0.

    Example:
        >>> from pygdbmi.gdbcontroller import GdbController
        >>> from mcp.gdb_nav_utils import step_frame_detailed
        >>> gdb = GdbController()
        >>> # ... load and run to main ...
        >>> hit, reason = step_frame_detailed(gdb, "manage_game__post_render", timeout=5.0)
        >>> if hit:
        ...     # We're stopped at the end of the scene loop
        ...     pass
        ... elif reason and reason.startswith("signal_"):
        ...     # Game crashed with a signal
        ...     print(f"Game crashed: {reason[7:]}")
        ... else:
        ...     # Timeout — something's wrong (infinite loop, etc.)
        ...     pass
    """
    start_time = time.monotonic()
    deadline = start_time + timeout

    # Set a temporary breakpoint at the target function.
    target_bpnum = _add_temporary_breakpoint(gdb, breakpoint_func, timeout)

    # Response coordination strategy:
    #
    # _continue sends -exec-continue with read_response=False (no response
    # reading). This is critical: pygdbmi's write() with read_response=True
    # can consume the *stopped record if it arrives within ~0.2s of *running,
    # which happens on every sequential frame step because the game loop is
    # already running and hits the breakpoint almost immediately.
    #
    # _poll_for_stops is the sole reader: it polls get_gdb_response(), sees
    # *running (ignored), then *stopped (breakpoint-hit, returned). This
    # guarantees the stopped record is never silently consumed.
    try:
        while time.monotonic() < deadline:
            # Send continue — _continue does NOT read any response.
            _continue(gdb, timeout)

            # Poll for stop events — _poll_for_stops consumes all responses.
            hit_target, detail = _poll_for_stops(gdb, target_bpnum, deadline, timeout)

            if hit_target:
                return True, None

            if detail == "unexpected_bp":
                # An unexpected breakpoint fired. Continue running to try
                # to reach our target before the timeout.
                continue
            elif detail == "timeout":
                return False, "timeout"
            elif detail == "gdb_no_response":
                return False, "gdb_no_response"
            elif detail and detail.startswith("signal_"):
                return False, detail
            else:
                return False, detail
    finally:
        # Clean up: delete the breakpoint if it wasn't auto-deleted.
        # (tbreak auto-deletes on hit, but we want to clean up on timeout too.)
        try:
            _delete_breakpoint(gdb, target_bpnum, timeout)
        except Exception:
            pass  # best-effort cleanup

    return False, "timeout"


def step_frame(
    gdb: "GdbController",
    breakpoint_func: str = "manage_game__post_render",
    timeout: float = 5.0,
) -> bool:
    """Advance execution to a specific frame in the game loop.

    Wrapper around step_frame_detailed() that returns just the boolean
    hit/miss result for backward compatibility.

    Args:
        gdb: A ``GdbController`` instance with a binary loaded.
        breakpoint_func: The C function name to break at.
        timeout: Maximum seconds to wait for the target breakpoint.

    Returns:
        True if the target breakpoint was hit, False if timeout/crashed.
    """
    hit, _ = step_frame_detailed(gdb, breakpoint_func, timeout)
    return hit
