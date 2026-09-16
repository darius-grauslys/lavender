"""Debug error handling module.

Takes a stack trace and identifies the most relevant error frame.

Logic:
1. Parse the stack trace and find the frame containing 'debug_error' function.
2. If 'debug_error' is found:
   - Move the frame to the function that called 'debug_error'.
   - This is because 'debug_error' is a wrapper/trampoline - the real
     error originated in the calling code.
3. If 'debug_error' is NOT found:
   - The error is likely occurring in the current frame (no stack manipulation needed).
4. After frame adjustment, attempt to print argument values of the relevant frame.
   - For pointer arguments, just print the pointer address.
   - This helps identify what data structures are involved in the error.

This module is a dependency of layer_pygdbmi and is used by _get_signal_info
to provide meaningful error context when the game crashes.

MI capability cache: -stack-info-arguments is not a standard MI command in
the GDB builds we use (it errors "Undefined MI command"), so each failed
round-trip would stall the traced game ~2s and log a gdb_error record.
Once a command has errored in a session it will never work again in that
session, so the negative result is cached per session (see
_mi_capability_cache) and the command — plus its slow console fallback —
is never attempted again.
"""

from __future__ import annotations

import re
from typing import Any


def parse_backtrace(backtrace_text: str) -> list[dict[str, str]]:
    """Parse a backtrace string into structured frame data.

    Args:
        backtrace_text: The backtrace output (e.g. from -stack-list-frames).

    Returns:
        List of frame dicts with keys: level, func, file, line, addr.
    """
    frames = []
    # Match lines like: "#0 func at file:line" or "#0 func at addr"
    pattern = re.compile(
        r'^(#\d+)\s+(\S+)\s+at\s+(.+?)(?::(\d+))?$'
    )
    for line in backtrace_text.strip().split('\n'):
        line = line.strip()
        match = pattern.match(line)
        if match:
            level, func, location, lineno = match.groups()
            frames.append({
                'level': level,
                'func': func,
                'location': location,
                'line': lineno or '',
                'addr': '',
            })
        else:
            # Fallback: try to parse minimal info
            if line.startswith('#'):
                parts = line.split(None, 2)
                if len(parts) >= 2:
                    frames.append({
                        'level': parts[0],
                        'func': parts[1],
                        'location': parts[2] if len(parts) > 2 else '',
                        'line': '',
                        'addr': '',
                    })
    return frames


def find_debug_error_frame(frames: list[dict[str, str]]) -> int | None:
    """Find the index of the 'debug_error' frame in the stack trace.

    Args:
        frames: List of frame dicts from parse_backtrace.

    Returns:
        Index of the debug_error frame, or None if not found.
    """
    for i, frame in enumerate(frames):
        if 'debug_error' in frame.get('func', ''):
            return i
    return None


def adjust_frame_for_debug_error(
    frames: list[dict[str, str]]
) -> tuple[list[dict[str, str]], int, bool]:
    """Adjust the frame list based on debug_error presence.

    Args:
        frames: Parsed stack frames.

    Returns:
        Tuple of (adjusted_frames, relevant_frame_index, was_adjusted):
        - adjusted_frames: the frame list (possibly reordered)
        - relevant_frame_index: index of the frame to inspect
        - was_adjusted: True if we moved to the caller frame
    """
    debug_error_idx = find_debug_error_frame(frames)

    if debug_error_idx is None:
        # debug_error is not in the stack trace.
        # The error is likely occurring in the present frame (frame 0).
        # No stack frame manipulation is needed.
        return frames, 0, False

    # debug_error was found. Move the frame to the function calling debug_error.
    # The caller is the next frame after debug_error.
    caller_idx = debug_error_idx + 1
    if caller_idx >= len(frames):
        # No caller frame available, use debug_error frame itself
        return frames, debug_error_idx, False

    return frames, caller_idx, True


def format_adjusted_backtrace(frames: list[dict[str, str]]) -> str:
    """Format the adjusted backtrace for display.

    Shows the frames with the relevant frame highlighted.
    """
    result = []
    relevant_idx, was_adjusted = 0, False

    try:
        _, relevant_idx, was_adjusted = adjust_frame_for_debug_error(frames)
    except Exception:
        pass

    for i, frame in enumerate(frames):
        marker = ">>" if i == relevant_idx else "  "
        loc = frame.get('location', '')
        lineno = frame.get('line', '')
        if lineno:
            loc_str = f"{loc}"
        else:
            loc_str = loc or frame.get('addr', '')

        level = frame.get('level', f'#{i}')
        func = frame.get('func', '?')
        result.append(f"{marker} {level} {func} at {loc_str}")

    return '\n'.join(result)


def get_relevant_frame(frames: list[dict[str, str]]) -> dict[str, str] | None:
    """Get the frame that should be inspected for debugging.

    Applies the debug_error adjustment logic and returns the relevant frame.
    """
    if not frames:
        return None

    try:
        adjusted_frames, idx, _ = adjust_frame_for_debug_error(frames)
        if 0 <= idx < len(adjusted_frames):
            return adjusted_frames[idx]
    except Exception:
        pass

    return frames[0] if frames else None


def build_error_report(
    frames: list[dict[str, str]],
    gdb=None,
    include_arguments: bool = True,
) -> str:
    """Build the formatted error report presented for an error stop.

    This is the SHARED presentation logic for both error surfaces in the
    step driver:

    - the crash path (a SIGABRT/SIGSEGV ... stop): the caller builds the
      structured frames from -stack-list-frames and passes them here;
    - the non-fatal path (the debug_error BreakpointHook): when
      -DCRASH_ON_ERROR is not in the build, debug_error() returns and the
      game keeps running, so the stop is a breakpoint hit, not a signal —
      the hook captures the same report from the hit.

    The report:
    1. Runs the frames through adjust_frame_for_debug_error() so the frame
       highlighted with '>>' is the function that CALLED debug_error (the
       real origin of the error), not the debug_error trampoline itself
       (or frame 0 when debug_error is not in the stack).
    2. Formats the full backtrace with the '>>' marker on the relevant frame.
    3. If a gdb session is given (and include_arguments is True), appends the
       relevant frame's argument values via format_arguments_for_frame().
       For a debug_error hit this includes msg_fmt — the error message text
       itself — which is exactly the context a crash backtrace would show.

    Args:
        frames: Structured frame dicts (keys: level, func, location, line,
            addr) built by the caller from -stack-list-frames.
        gdb: Optional GDBSession; when given, arguments are read from GDB.
        include_arguments: Whether to attempt reading argument values.

    Returns:
        The formatted report string, or "" if there are no frames.
    """
    if not frames:
        return ""

    try:
        adjusted_frames, relevant_idx, _ = adjust_frame_for_debug_error(frames)
    except Exception:
        adjusted_frames, relevant_idx = frames, 0

    lines = []
    for i, frame in enumerate(adjusted_frames):
        marker = ">>" if i == relevant_idx else "  "
        loc = frame.get('location') or frame.get('addr') or '???'
        lines.append(
            f"{marker} {frame.get('level', f'#{i}')} "
            f"{frame.get('func', '?')} at {loc}"
        )

    result = "\n".join(lines)

    if gdb is not None and include_arguments:
        args_info = format_arguments_for_frame(gdb, relevant_idx)
        if args_info:
            result += f"\nArguments:\n{args_info}"

    return result


def _mi_capability_cache(gdb_session) -> set:
    """Per-session negative cache of MI commands this GDB does not support.

    debug_error.py is a lower layer than the session wrapper, so the cache
    is duck-typed onto the session object itself: each GDB session (i.e.
    each GDB version/build) gets its own cache, and a fresh session starts
    clean. Returns the set (created on first use).
    """
    cache = getattr(gdb_session, "mi_unsupported_commands", None)
    if cache is None:
        cache = set()
        try:
            gdb_session.mi_unsupported_commands = cache
        except AttributeError:
            pass
    return cache


def reset_mi_capability_cache(gdb_session) -> None:
    """Clear the session's negative MI capability cache (used by tests)."""
    cache = getattr(gdb_session, "mi_unsupported_commands", None)
    if cache is not None:
        cache.clear()


def format_arguments_for_frame(
    gdb_session, frame_idx: int = 0
) -> str:
    """Attempt to print argument values for the given frame.

    Uses GDB's -stack-info-arguments to get argument values.
    For pointer arguments, only prints the pointer address.

    Negative-result caching: in the GDB builds we use, -stack-info-arguments
    is not an MI command at all (it replies "Undefined MI command"), and the
    console "info args" fallback below costs a 2s bounded read on top. Each
    failed attempt stalls the traced game and logs a gdb_error record — in a
    bursty error storm (thousands of debug_errors) that dominates the run.
    Once the probe has failed in this session it can never succeed again, so
    the failure is cached (_mi_capability_cache) and subsequent calls return
    immediately with no GDB round-trips at all.

    Args:
        gdb_session: A GDBSession instance.
        frame_idx: The stack frame index to inspect.

    Returns:
        String containing formatted argument values.
    """
    try:
        # -stack-info-arguments with frame selection.
        # In MI3 it is not available, so the console "info args" fallback
        # below is the recovery path (first attempt only — see the cache).
        if "stack-info-arguments" in _mi_capability_cache(gdb_session):
            # Already proved unsupported in this GDB — never pay for the
            # failed round-trip (or the slow console fallback) again.
            return "(no argument info available)"

        responses = gdb_session.write(f"-stack-info-arguments --frame {frame_idx}")
        has_args = False
        for r in responses:
            if r.is_error():
                # Not available in this MI version. (The old check compared
                # r.type.value == "error", which is dead code: type is the
                # top-level category "result" and "error" is the message
                # field — so this branch never fired and the slow console
                # fallback ran on EVERY error, ~2.5s each.) An undefined MI
                # command will never work in this GDB, so cache the negative
                # result: every retry would stall the traced game ~2s and
                # log a gdb_error record.
                if "undefined" in (r.reason or "").lower():
                    _mi_capability_cache(gdb_session).add("stack-info-arguments")
                break
            if r.type.value == "result" and r.raw.get("message") == "done":
                args = r.raw.get("payload", {}).get("arguments", [])
                if args:
                    lines = []
                    for arg in args:
                        if isinstance(arg, dict):
                            lines.append(f"  {arg.get('name', '?')} = {arg.get('value', '?')}")
                    return '\n'.join(lines)
                has_args = True

        # Fallback: use console "info args" after selecting the frame.
        # (Reached only on the FIRST attempt when the MI command is missing —
        # a cached miss returns above — or when it exists but reported no
        # arguments.)
        if not has_args:
            gdb_session.write(f"-stack-select-frame {frame_idx}")
            # Execute "info args" via console interpreter. No artificial
            # delay: get_gdb_response below blocks until output or timeout.
            gdb_session.write("-interpreter-exec console \"info args\"", read_response=False)
            # Read the console output
            args_lines = []
            try:
                resp = gdb_session.gdbmi.get_gdb_response(timeout_sec=2.0)
                if resp:
                    for r in resp:
                        rtype = r.get("type", "")
                        # Check for console stream output (payload contains the text)
                        if rtype in ("console", "target", "log") and r.get("payload"):
                            output = r.get("payload", "")
                            if isinstance(output, str):
                                lines = output.strip().split('\n')
                                args_lines.extend(l for l in lines if l.strip())
            except Exception:
                pass

            if args_lines:
                return '\n'.join(f"  {l.strip()}" for l in args_lines if l.strip())

        return "(no argument info available)"
    except Exception as e:
        return f"(could not get arguments: {e})"
