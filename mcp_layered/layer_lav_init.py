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
import re
import time
from typing import Any

from mcp_layered.layer_lav_config import LavConfig, default_config, load_config
from mcp_layered.layer_lav_cmd import invoke, CommandError, register_driver, get_driver
from mcp_layered.layer_pygdbmi import GDBSession, BreakpointHook
from mcp_layered.debug_error import build_error_report, get_relevant_frame
from mcp_layered.debug_response import DebugResponse, ResponseType
from mcp_layered.debug_scanner_scene import parse_hex, _to_int, _is_null
from mcp_layered.debug_scanner_process import DebugProcessScanner
from mcp_layered.debug_scanner_client import DebugClientScanner


# -- Scene transition tracking -- #
#
# Where the scene-transition marker lives. The run_game scene loop
# (core/source/game.c) begins each iteration — i.e. each time a NEW scene
# becomes active — with a `debug_info("TRANSITION p_active_scene -> %p",
# ...)` line. A breakpoint on that line is an inlining-immune transition
# marker (set_active_scene_for__scene_manager is inlined by -O2 and its
# out-of-line copy never runs). The line number is a constant so it's easy
# to re-point if the source reflows; see _SCENE_TRANSITION_LINE.
_SCENE_TRANSITION_FILE = "game.c"
_SCENE_TRANSITION_LINE = 702

# Module-level (shared across sessions, like _session_state). The
# game.c:702 hook only sets "dirty"; the actual scene read is deferred to
# resolve_pending_scene_transitions() at a safe point. session_status and
# step drivers surface the result to MCP callers (grounding truth for QA
# agents verifying UI navigation).
_scene_state: dict[str, Any] = {
    "active_kind": None,     # Scene_Kind enum name of the active scene
    "active_ptr": None,      # bare hex address of the active scene
    "transitions": [],       # [{"from", "to", "new_scene_ptr", "ts"}, ...]
    "dirty": 0,              # transitions observed since last resolution
}

# Shared SessionState (bridged to mcp.lav_mcp.SessionState), set by
# _register_builtin_drivers. Exposed at module level so tests can reset it
# (it is otherwise closure-local and would leak running=True between
# independent sessions in the same process).
_SESSION_STATE: Any = None


def reset_scene_state() -> None:
    """Reset the scene transition state (used by tests)."""
    _scene_state["active_kind"] = None
    _scene_state["active_ptr"] = None
    _scene_state["transitions"] = []
    _scene_state["dirty"] = 0


def reset_session_state() -> None:
    """Reset the shared session state (used by tests).

    The session drivers capture a single module-level SessionState; without
    this, one session's session_start leaves running=True and poisons a
    later session's session_start in the same process.
    """
    if _SESSION_STATE is None:
        return
    _SESSION_STATE.running = False
    _SESSION_STATE.halted = False
    _SESSION_STATE.crashed = False
    _SESSION_STATE.backtrace = ""
    if hasattr(_SESSION_STATE, "last_dump_uuid"):
        _SESSION_STATE.last_dump_uuid = None
    if hasattr(_SESSION_STATE, "crash_signal"):
        _SESSION_STATE.crash_signal = None


def _normalize_scene_kind(value: Any) -> str:
    """Normalize a gdb-printed Scene_Kind value to an enum name.

    With debug info, GDB prints enum arguments by name (e.g.
    "Scene_Kind__MainMenu"). Without debug info the value is a plain
    integer, which becomes a numeric placeholder name. Null/empty
    values normalize to Scene_Kind__None.
    """
    if value is None:
        return "Scene_Kind__None"
    text = str(value).strip()
    if not text or _is_null(text):
        return "Scene_Kind__None"
    if text.startswith("Scene_Kind__"):
        return text
    try:
        return f"Scene_Kind__{int(text, 0)}"
    except ValueError:
        return text


def format_scene_status() -> str:
    """Format the scene section for session_status responses.

    Returns the active scene (kind + pointer) and the most recent
    transitions, or "" when no scene has been identified yet.
    """
    lines: list[str] = []
    if _scene_state.get("active_kind"):
        lines.append(
            f"Scene: {_scene_state['active_kind']} "
            f"(ptr={_scene_state.get('active_ptr') or '?'})"
        )
        recent = _scene_state["transitions"][-5:]
        if recent:
            lines.append("Scene transitions (most recent last):")
            for t in recent:
                lines.append(f"  {t.get('from') or 'None'} -> {t.get('to')}")
    return "\n".join(lines)


def format_scene_transitions(since_count: int) -> str:
    """Format scene transitions recorded since index *since_count*.

    Returns a "Scene transitions: A -> B -> C" line (for step driver
    responses), or "" when no new transitions occurred.
    """
    new = _scene_state["transitions"][since_count:]
    if not new:
        return ""
    chain = " -> ".join(
        [new[0].get("from") or "None"] + [t.get("to") for t in new]
    )
    return f"Scene transitions: {chain}"


def _read_active_scene(gdb) -> tuple[str | None, str | None]:
    """Read the current active scene as (kind, ptr) via direct global reads.

    The ``Game`` struct is a global (``game`` in core/source/main.c) and
    ``Scene_Manager`` is an embedded member, so
    ``game.scene_manager.p_active_scene`` and ``&game.scene_manager.scenes``
    are pure memory reads — no inferior function call (the
    ``debug_get_scene_scanner`` call path hangs under pygdbmi). Because
    ``Scene_Manager.scenes`` is indexed by ``Scene_Kind``, the active scene's
    kind is its element offset from the array base.

    Returns ``(kind, ptr)``; ``(None, None)`` when there is no active scene
    or the reads fail (release build / game not running).

    MUST be called at a safe point (game stably stopped, NOT during a step's
    polling get_gdb_response) — see :func:`resolve_pending_scene_transitions`.
    """
    def _eval(expr: str) -> str | None:
        try:
            for r in gdb.write(f"-data-evaluate-expression {expr}"):
                if r.type.value == "result" and r.raw.get("message") == "done":
                    return (r.raw.get("payload") or {}).get("value")
        except Exception:
            return None
        return None

    active_raw = _eval("game.scene_manager.p_active_scene")
    base_raw = _eval("&game.scene_manager.scenes")
    size_raw = _eval("sizeof(Scene)")

    # No active scene (p_active_scene is null) → nothing active.
    if _is_null(active_raw):
        return None, None

    active = parse_hex(active_raw)
    base = parse_hex(base_raw)
    size = _to_int(size_raw)
    if not active or not base or not size:
        return None, None  # reads failed (release build / not running)

    idx = (int(active, 16) - int(base, 16)) // size
    if idx < 0:
        return None, active
    name = _eval(f"(Scene_Kind){idx}")
    kind = _normalize_scene_kind(name) if name else f"Scene_Kind__{idx}"
    return kind, active


def resolve_pending_scene_transitions(gdb) -> str:
    """Resolve pending scene transitions (deferred from the hook).

    The game.c:702 breakpoint hook only sets ``_scene_state["dirty"]`` — it
    must not issue GDB commands because it can fire while the step driver is
    polling ``get_gdb_response`` (a nested GDB command there deadlocks). This
    function performs the actual scene read at a SAFE point (game stably
    stopped), records the transition, and returns a
    ``"Scene transitions: ..."`` line for the caller to surface — or ``""``
    when there was nothing new to record.

    Idempotent and safe to call repeatedly: a no-op while ``dirty`` is 0, and
    it always clears the dirty flag (even if the read fails or the scene is
    unchanged).
    """
    if _scene_state.get("dirty", 0) <= 0:
        return ""

    count_before = len(_scene_state["transitions"])
    old_kind = _scene_state.get("active_kind")
    try:
        kind, ptr = _read_active_scene(gdb)
    except Exception:
        kind, ptr = None, None

    # Clear the flag regardless — resolution was attempted.
    _scene_state["dirty"] = 0

    if kind is None:
        return ""  # couldn't read the scene (release build / not running)
    if kind != old_kind:
        _scene_state["transitions"].append({
            "from": old_kind,
            "to": kind,
            "new_scene_ptr": ptr,
            "ts": time.time(),
        })
        _scene_state["active_kind"] = kind
        _scene_state["active_ptr"] = ptr or _scene_state.get("active_ptr")
        print(f"\n[scene] transition: {old_kind or 'None'} -> {kind}")

    return format_scene_transitions(count_before)


# GDB prints a pointer value as "0xADDR <symbol>" when the address matches a
# known symbol (function or data). We exploit that to resolve an address to a
# name without any dedicated symbol-lookup MI command (which this GDB build
# lacks) and without a function *call* (which hangs under pygdbmi).
_FUNC_ANNOT_RE = re.compile(r"<([^>]+)>")


def resolve_function_name(gdb, addr: str | None,
                          cache: dict | None = None) -> str | None:
    """Resolve a hex address to a function name via GDB's symbol annotation.

    GDB prints a pointer as ``0xADDR <symbol>`` when the address is a known
    symbol. We cast the address to a pointer (``(void*)0xADDR``) and parse the
    ``<symbol>`` annotation — a plain ``-data-evaluate-expression`` (a read,
    not a call, so it never hangs). This is game-agnostic: it returns whatever
    symbol GDB knows for the address, or ``None`` if the address is not a
    known symbol (e.g. a PLT thunk or a heap address).

    *cache* (addr→name) dedupes lookups — many UI elements share the same
    handler function, so each unique address is resolved at most once. Must be
    called at a safe point (game stopped).
    """
    if not addr:
        return None
    if cache is not None and addr in cache:
        return cache[addr]
    name: str | None = None
    try:
        for r in gdb.write(f"-data-evaluate-expression (void*){addr}"):
            if r.type.value == "result" and r.raw.get("message") == "done":
                value = (r.raw.get("payload") or {}).get("value") or ""
                m = _FUNC_ANNOT_RE.search(value)
                name = m.group(1) if m else None
                break
    except Exception:
        name = None
    if cache is not None:
        cache[addr] = name
    return name


# -- Process create/remove trace -- #
#
# Breakpoint hooks on the two process-lifecycle entry points
# (add/remove_process_to__process_table). On each hit a BreakpointHook CAPTURE
# — run only in a safe, non-nested context (the transient stop window, where the
# game is stopped at the process function and the stream is clean) — records the
# process pointer, the handler's function name, and the callee stack. The callee
# stack is time-sensitive: it is gone once the stop is continued past, so it must
# be captured *at the hit*. The captured events accumulate in each hook's
# captured_events; resolve_process_trace() drains them at a safe point (the step
# driver's post-work / session_status) and writes structured lines to the log —
# never the MCP response.
#
# ON by default (a live game churns many processes per frame, so this is verbose);
# toggleable via the BreakpointHook enable/disable (a future MCP toggle will call
# those). The capture issues GDB commands only when GDBSession._in_nested_read is
# False, so it can never deadlock the connection.

_process_trace_state: dict[str, Any] = {
    "add_hook": None,      # BreakpointHook for add_process_to__process_table
    "remove_hook": None,   # BreakpointHook for remove_process_from__process_table
    "error_hook": None,    # BreakpointHook for debug_error (process that errored)
    "sym_cache": {},       # addr -> handler symbol name (dedupe resolution)
    "enabled": True,       # on by default
}

# The Game_Action RECEIVE lifecycle marker: a lightweight print-only
# BreakpointHook (no GDB I/O — it can fire mid-poll), ON by default and
# toggled together with the Process hooks by `trace`.
#
# The Game_Action DISPATCH deep-trace is deliberately SEPARATE (below): it is
# expensive (a backtrace + a client-scanner read on EVERY dispatch) and its
# purpose is a deep full trace of the engine, not speed — so it defaults OFF
# and is opted in via `trace ga`.
_game_action_trace_state: dict[str, Any] = {
    "receive_hook": None,  # BreakpointHook for receive_game_action_for__client
    "enabled": True,       # on by default (toggled by `trace`)
}

# Deep Game_Action DISPATCH trace (dispatch_game_action_for__client). OFF by
# default — the point is a deep, full trace of the engine (a callee backtrace +
# a client-scanner snapshot of the dispatched action/client on every dispatch),
# which is intentionally NOT fast/snappy. Toggled by `trace ga`. The capture
# (GDB I/O) runs only in a safe, non-nested context (gated on
# GDBSession._in_nested_read); the time-sensitive backtrace + client snapshot are
# captured at the hit and the records are drained to the log at a safe point by
# resolve_game_action_dispatch_trace() — the same pattern as the process trace.
_ga_dispatch_deep_trace_state: dict[str, Any] = {
    "hook": None,      # BreakpointHook for dispatch_game_action_for__client (deep)
    "enabled": False,  # off by default (opt in via `trace ga`)
}

# Non-fatal debug_error REPORTING (separate from the process-trace
# "process.error" hook, which also breaks on debug_error but only records
# the erroring process pointer for the process lifecycle trace).
#
# Since -DCRASH_ON_ERROR was dropped from the build, debug_error() no longer
# aborts: it prints the error and RETURNS, the game keeps running, and the
# step driver never sees a crash signal — the error would be invisible.
# This hook stops the game at every debug_error, captures the same report
# the SIGABRT crash path used to produce (backtrace with the debug_error
# caller highlighted + arguments, via debug_error.build_error_report), and
# the game is continued by the step driver (the hit is an "unexpected_bp"
# to step_frame_detailed, which continues toward the frame target).
#
# Burst suppression: a debug_error STORM (e.g. pool-exhaustion allocation
# failures repeating every frame for hours) must not cost a full capture —
# stack read + argument round-trips — on every hit. Only the first
# full_captures_per_signature occurrences per signature (derived from the
# stop response alone, zero GDB I/O — see _debug_error_signature) get the
# full report; repeats are counted with zero GDB I/O and surfaced as one
# aggregated record per signature by resolve_debug_error_events().
#
# ON by default and NOT part of the `trace` toggle (like the
# initialize_ui_manager / scene-transition hooks): error reporting is core
# diagnostics, not verbose churn.

_debug_error_report_state: dict[str, Any] = {
    "hook": None,      # BreakpointHook for debug_error (error reporting)
    "enabled": True,   # on by default
    # Burst suppression: signature -> {"seen", "full", "suppressed",
    # "suppressed_reported", "last_ts"} (see _capture_debug_error_event).
    "signatures": {},
    "full_captures_per_signature": 3,
}


# Frame heartbeat: reset__game_tick_timer() is called exactly ONCE per game
# frame — immediately after the scene loop's tick spin ends — in EVERY scene
# (main menu, singleplayer, world_load, world, ...; see the
# `while(!poll__game_tick_timer(p_game));` loop at the top of each
# m_enter_scene_*_handler). A breakpoint on it is a frame-boundary marker:
# a hit proves the game crossed into a new frame.
#
# The step driver's watchdog (step timeout) is extended ONLY on heartbeat
# hits, never on bursty hook hits (process/game-action/debug_error). A game
# stuck inside one frame — e.g. an infinite non-fatal debug_error retry
# loop after CRASH_ON_ERROR was dropped — produces a bp storm but never
# crosses a frame boundary, so the watchdog detects it (and returns a
# timeout with the captured debug_error events) instead of hanging the step
# forever. (A bp storm keeps the GDB idle-timeout alive, so the idle
# timeout alone cannot catch it.)
FRAME_HEARTBEAT_FUNC = "reset__game_tick_timer"

_frame_heartbeat_state: dict[str, Any] = {
    "hook": None,  # BreakpointHook for the frame boundary (lightweight)
}


def reset_game_action_trace_state() -> None:
    """Reset the Game_Action receive-marker state (used by tests)."""
    _game_action_trace_state["receive_hook"] = None
    _game_action_trace_state["enabled"] = True


def reset_ga_dispatch_deep_trace_state() -> None:
    """Reset the deep Game_Action dispatch-trace state (used by tests)."""
    _ga_dispatch_deep_trace_state["hook"] = None
    _ga_dispatch_deep_trace_state["enabled"] = False


def reset_process_trace_state() -> None:
    """Reset the process-trace state (and the paired Game_Action state)."""
    _process_trace_state["add_hook"] = None
    _process_trace_state["remove_hook"] = None
    _process_trace_state["error_hook"] = None
    _process_trace_state["sym_cache"] = {}
    _process_trace_state["enabled"] = True
    reset_game_action_trace_state()


def reset_debug_error_report_state() -> None:
    """Reset the non-fatal debug_error reporting state (used by tests)."""
    _debug_error_report_state["hook"] = None
    _debug_error_report_state["enabled"] = True
    _debug_error_report_state["signatures"] = {}


def reset_frame_heartbeat_state() -> None:
    """Reset the frame-heartbeat state (used by tests)."""
    _frame_heartbeat_state["hook"] = None


def reset_trace_state() -> None:
    """Reset both toggleable trace categories, the always-on debug_error
    reporting state, and the frame-heartbeat state (used by tests, so a
    prior test's hooks — bound to its fake GDBSession — never leak into the
    next test's registration)."""
    reset_process_trace_state()
    reset_ga_dispatch_deep_trace_state()
    reset_debug_error_report_state()
    reset_frame_heartbeat_state()


def _set_trace_hooks_enabled(hooks, enabled: bool) -> None:
    for hook in hooks:
        if hook is None:
            continue
        if enabled:
            hook.enable()
        else:
            hook.disable()


def trace_hook_groups() -> tuple[list, list]:
    """Return the toggleable BreakpointHook groups: (process, game_action).

    Only the lightweight Game_Action RECEIVE marker is in these groups (toggled
    with the Process hooks by `trace`). The deep Game_Action DISPATCH trace has
    its own state + default (OFF) and is toggled separately by `trace ga` (see
    set_ga_dispatch_deep_trace_enabled / toggle_ga_dispatch_deep_trace).
    """
    process_hooks = [
        _process_trace_state["add_hook"],
        _process_trace_state["remove_hook"],
        _process_trace_state["error_hook"],
    ]
    game_action_hooks = [
        _game_action_trace_state["receive_hook"],
    ]
    return process_hooks, game_action_hooks


def set_trace_enabled(gdb, enabled: bool) -> None:
    """Enable or disable the Process + Game_Action receive-marker hooks.

    (The deep Game_Action DISPATCH trace is separate — OFF by default, toggled
    by `trace ga` / set_ga_dispatch_deep_trace_enabled.) Other breakpoint hooks
    (initialize_ui_manager, scene transition, debug_error reporting, frame
    heartbeat) are left alone. If the hooks have not been registered yet (the
    game has not started), the flags are still stored and applied at
    registration time.
    """
    enabled = bool(enabled)
    _process_trace_state["enabled"] = enabled
    _game_action_trace_state["enabled"] = enabled
    process_hooks, game_action_hooks = trace_hook_groups()
    _set_trace_hooks_enabled(process_hooks, enabled)
    _set_trace_hooks_enabled(game_action_hooks, enabled)


def toggle_trace_hooks(gdb) -> bool:
    """Toggle the Process + Game_Action receive-marker BreakpointHooks.

    Returns True when the hooks are enabled after the toggle, False when they
    are disabled. (The deep Game_Action DISPATCH trace is toggled separately —
    see toggle_ga_dispatch_deep_trace.)

    When the hooks are already registered, their *actual* enabled state is used
    for the toggle (so a hook whose breakpoint could not be set is not treated
    as "on"). Before registration, the stored flags are used.
    """
    process_hooks, game_action_hooks = trace_hook_groups()
    registered_hooks = [
        h for h in process_hooks + game_action_hooks if h is not None
    ]
    if registered_hooks:
        currently_on = all(h.enabled for h in registered_hooks)
    else:
        currently_on = (
            _process_trace_state["enabled"]
            and _game_action_trace_state["enabled"]
        )
    enabled = not currently_on
    set_trace_enabled(gdb, enabled)
    return enabled


def set_ga_dispatch_deep_trace_enabled(gdb, enabled: bool) -> None:
    """Enable or disable the deep Game_Action DISPATCH trace (default OFF).

    If the hook has not been registered yet (the game has not started), the
    flag is stored and applied at registration time.
    """
    enabled = bool(enabled)
    _ga_dispatch_deep_trace_state["enabled"] = enabled
    hook = _ga_dispatch_deep_trace_state["hook"]
    if hook is None:
        return
    if enabled:
        hook.enable()
    else:
        hook.disable()


def toggle_ga_dispatch_deep_trace(gdb) -> bool:
    """Toggle the deep Game_Action DISPATCH trace. Returns the new state.

    When the hook is already registered, its *actual* enabled state is used for
    the toggle; before registration, the stored flag is used.
    """
    hook = _ga_dispatch_deep_trace_state["hook"]
    if hook is not None:
        currently_on = hook.enabled
    else:
        currently_on = _ga_dispatch_deep_trace_state["enabled"]
    enabled = not currently_on
    set_ga_dispatch_deep_trace_enabled(gdb, enabled)
    return enabled


def _describe_trace_hook(hook) -> str:
    if hook is None:
        return "not registered"
    state = "on" if hook.enabled else "off"
    return f"{hook.name}={state}"


def _toggle_ga_dispatch_deep_trace_driver(gdb: GDBSession) -> str:
    """Render the result of toggling the deep Game_Action dispatch trace."""
    enabled = toggle_ga_dispatch_deep_trace(gdb)
    hook = _ga_dispatch_deep_trace_state["hook"]
    lines = [
        f"game-action dispatch deep-trace {'ON' if enabled else 'OFF'} "
        f"(captures a backtrace + client-scanner snapshot on every dispatch; "
        f"drained to the log at a safe point)"
    ]
    lines.append("Dispatch deep-trace: " + _describe_trace_hook(hook))
    if hook is None:
        lines.append(
            "Hook is not registered yet; the current flag applies when "
            "session_start registers the breakpoint hooks.")
    return "\n".join(lines)


def trace_driver(gdb: GDBSession, config: LavConfig, kwargs: dict) -> str:
    """CLI/MCP command: toggle the trace BreakpointHooks.

    - ``trace`` (no arg): toggle the Process + Game_Action receive-marker hooks
      (ON by default). Running it disables them; running it again re-enables.
    - ``trace ga`` (or ``trace game_action`` / ``trace dispatch``): toggle the
      deep Game_Action DISPATCH trace (OFF by default) — a backtrace +
      client-scanner capture on every dispatch, drained to the log at a safe
      point.

    The UI-manager cache hook and the scene-transition hook are intentionally
    left unchanged.
    """
    if gdb.is_closed:
        return "GDB session is closed."

    # Optional sub-argument selects which trace group to toggle.
    target = str(kwargs.get("target") or "").strip().lower()
    if target in ("ga", "game_action", "game-action", "dispatch"):
        return _toggle_ga_dispatch_deep_trace_driver(gdb)

    enabled = toggle_trace_hooks(gdb)
    process_hooks, game_action_hooks = trace_hook_groups()

    lines = [
        f"trace {'ON' if enabled else 'OFF'} "
        f"(toggles Process + Game_Action receive-marker BreakpointHooks only; "
        f"use `trace ga` for the deep dispatch trace)"
    ]
    lines.append("Process: " + ", ".join(
        _describe_trace_hook(h) for h in process_hooks))
    lines.append("Game_Action receive: " + ", ".join(
        _describe_trace_hook(h) for h in game_action_hooks))
    lines.append("Game_Action dispatch (deep, `trace ga`): " +
                 _describe_trace_hook(_ga_dispatch_deep_trace_state["hook"]))
    lines.append("Unchanged: initialize_ui_manager, scene transition, "
                 "debug_error reporting, frame heartbeat")

    if all(h is None for h in process_hooks + game_action_hooks
           + [_ga_dispatch_deep_trace_state["hook"]]):
        lines.append(
            "Hooks are not registered yet; the current flag applies when "
            "session_start registers the breakpoint hooks."
        )
    return "\n".join(lines)


def _arg_value_from_frame(frame, name: str):
    """Return the value string of a named arg from a stop frame, or None."""
    if frame is None or not getattr(frame, "args", None):
        return None
    for a in frame.args:
        if isinstance(a, dict) and a.get("name") == name:
            return a.get("value")
    return None


def _read_stack_arg(gdb, name: str):
    """Read a named function-arg of the current (selected) frame.

    Uses -stack-info-frame. NOTE: -stack-info-args is NOT a GDB MI command
    ("Undefined MI command"); the args live in the payload's `frame` object —
    the MI result is {"frame": {"args": [{name, value}, ...], ...}}, so the
    args are at payload["frame"]["args"] (NOT payload["args"]).
    """
    try:
        for r in gdb.write("-stack-info-frame"):
            if r.type.value == "result" and r.raw.get("message") == "done":
                frame = (r.raw.get("payload") or {}).get("frame") or {}
                for arg in frame.get("args", []):
                    if isinstance(arg, dict) and arg.get("name") == name:
                        return arg.get("value")
    except Exception:
        pass
    return None


def _read_first_stack_arg(gdb):
    """Read the FIRST arg (by position) of the current (selected) frame.

    Uses -stack-info-frame. The MI result is {"frame": {"args": [...], ...}},
    so the args are at payload["frame"]["args"] (NOT payload["args"]). For a
    run-handler — invoked as ``p_process->handler(p_process, p_game)`` — the
    first arg is the process pointer. A function *parameter* is passed by value
    and (if the handler uses it after an inner call) spilled to the stack, so it
    survives -O2 even when the caller's loop-local ``p_process`` is <optimized
    out>. Returns the value string, or None.
    """
    try:
        for r in gdb.write("-stack-info-frame"):
            if r.type.value == "result" and r.raw.get("message") == "done":
                frame = (r.raw.get("payload") or {}).get("frame") or {}
                args = frame.get("args", [])
                if args and isinstance(args[0], dict):
                    return args[0].get("value")
    except Exception:
        pass
    return None


def _read_expr(gdb, expr: str) -> str:
    """Evaluate an expression (a read, never a call) -> the value string."""
    try:
        for r in gdb.write(f"-data-evaluate-expression {expr}"):
            if r.type.value == "result" and r.raw.get("message") == "done":
                return (r.raw.get("payload") or {}).get("value") or ""
    except Exception:
        pass
    return ""


def _read_stack_frames(gdb) -> list:
    """Read the full callee stack via -stack-list-frames (1 round-trip) -> raw frames."""
    try:
        for r in gdb.write("-stack-list-frames"):
            if r.type.value == "result" and r.raw.get("message") == "done":
                return [f for f in (r.raw.get("payload") or {}).get("stack", [])
                        if isinstance(f, dict)]
    except Exception:
        pass
    return []


def raw_stack_frame_to_debug_error_frame(i: int, frame: dict) -> dict:
    """Convert one raw -stack-list-frames frame into the structured frame dict
    that debug_error.py (parse_backtrace / adjust_frame_for_debug_error /
    build_error_report) consumes: keys level, func, location, line, addr.

    ``location`` is ``file:line`` when both are present, else the file, else
    the pc/addr, else "???" — so a frame always carries a displayable location.
    """
    func = frame.get("func", "?")
    file = frame.get("file", "")
    line = frame.get("line", "")
    addr = frame.get("pc", "") or frame.get("addr", "")
    if file and line:
        loc = f"{file}:{line}"
    elif file:
        loc = file
    elif addr:
        loc = addr
    else:
        loc = "???"
    return {
        'level': f'#{i}',
        'func': func,
        'location': loc,
        'line': line,
        'addr': addr,
    }


def _frame_str(i: int, f: dict) -> str:
    func = f.get("func", "?")
    file = f.get("file", "")
    line = f.get("line", "")
    loc = f"{file}:{line}" if file and line else (file or f.get("pc", "???"))
    return f"#{i} {func} at {loc}"


def _read_backtrace(gdb) -> list:
    """Read the callee stack as readable "#N func at file:line" strings (1 round-trip)."""
    return [_frame_str(i, f) for i, f in enumerate(_read_stack_frames(gdb))]


def _find_frame_index(frames: list, func_name: str):
    """Index of the first stack frame whose func matches, or None."""
    for i, f in enumerate(frames):
        if f.get("func") == func_name:
            return i
    return None


def _process_trace_record(ev: dict) -> dict:
    """Build the structured JSONL record for one process-trace event.

    Every record shares this schema so the whole trace is greppable in ONE file
    (the session's JSONL log) and can be correlated by the process pointer (ptr)
    across its ephemeral lifecycle: create -> (error) -> remove. The AI identifies
    a problematic process by its ptr, the handler that caused an error, and the
    callee that formed it.
    """
    return {
        "timestamp": ev.get("ts"),
        "type": "process-trace",
        "event": ev.get("event"),          # add / remove / error / handler
        "ptr": ev.get("ptr"),              # correlation key (Process *p_process)
        "handler": ev.get("handler"),      # run-handler symbol (bound after create)
        "stack": ev.get("stack", []),      # callee stack at the hit
        "context": f"process-trace:{ev.get('event')}",
    }


def _capture_process_event(gdb, responses, event_type: str) -> dict:
    """Capture one process create/remove event (GDB I/O) at the hit.

    Run by the BreakpointHook only in a safe, non-nested context (game stopped at
    the process function, clean stream). Reads the process pointer, the handler
    (with GDB's <symbol> annotation), and the callee stack. Never raises.
    """
    import time as _t
    event = {"event": event_type, "ts": _t.time(), "ptr": None,
             "handler": None, "stack": []}

    frame = None
    for r in responses:
        if r.is_breakpoint_hit() and r.frame is not None:
            frame = r.frame
            break

    # 1. Process pointer (2nd arg p_process): prefer the stop frame's args
    #    (0 round-trips), fall back to -stack-info-frame.
    ptr = _arg_value_from_frame(frame, "p_process")
    if ptr is None:
        ptr = _read_stack_arg(gdb, "p_process")
    event["ptr"] = ptr

    # 2. Handler (p_process->m_process_run__handler): GDB prints the pointer with
    #    a <symbol> annotation; resolve it (cached) for a readable name.
    if ptr and not _is_null(ptr):
        val = _read_expr(gdb, "p_process->m_process_run__handler")
        m = re.search(r"0x[0-9a-fA-F]+", val or "")
        addr = m.group(0) if m else None
        if addr:
            event["handler"] = (
                resolve_function_name(gdb, addr, _process_trace_state["sym_cache"])
                or addr)

    # 3. Callee stack (time-sensitive — only correct at the hit).
    event["stack"] = _read_backtrace(gdb)
    return event


def _capture_error_event(gdb, responses) -> dict:
    """Capture the process that caused a debug_error (GDB I/O) at the hit.

    A run-handler is invoked *inside* poll_process_manager
    (``p_process->m_process_run__handler(p_process, p_game)``), so when a handler
    raises debug_error the stack is  debug_error <- <handler> <- poll_process_manager.
    We read the full error callstack, then — if a poll_process_manager frame is
    present — select it and read its local ``p_process`` (the process whose handler
    is running). That ptr is the SAME value seen at create/remove, so the whole
    lifecycle correlates on it. Never raises.
    """
    import time as _t

    frames = _read_stack_frames(gdb)
    idx = _find_frame_index(frames, "poll_process_manager")
    if idx is None:
        # Not a process error (debug_error called outside the process poll loop) —
        # skip, so only process-handler errors are traced (avoids log noise).
        return None

    event = {"event": "error", "ts": _t.time(), "ptr": None, "handler": None,
             "stack": [_frame_str(i, f) for i, f in enumerate(frames)]}

    # Recover the process pointer. poll_process_manager's `p_process` is a loop
    # local that is <optimized out> at -O2, so first try it; if it's unavailable,
    # fall back to the run-handler frame's first arg — the handler is invoked as
    # p_process->handler(p_process, p_game), and a function parameter is passed by
    # value (in a register), so it survives -O2. That first arg IS the process
    # pointer, giving the same correlation key as the create/remove events.
    ptr = None
    try:
        for _ in gdb.write(f"-stack-select-frame {idx}"):
            pass
        # poll_process_manager's loop-local p_process (usually <optimized out> at
        # -O2); the reliable recovery is the run-handler frame's first arg below.
        ptr = _read_expr(gdb, "p_process")
    except Exception:
        ptr = None
    if ptr is None or _is_null(ptr) or "optimized out" in (ptr or ""):
        hidx = idx - 1  # the run-handler frame (direct callee of poll_process_manager)
        if 0 <= hidx < len(frames):
            try:
                for _ in gdb.write(f"-stack-select-frame {hidx}"):
                    pass
                a = _read_first_stack_arg(gdb)
                if a is not None and not _is_null(a) and "optimized out" not in a:
                    ptr = a
            except Exception:
                pass
    if ptr is not None and "optimized out" in ptr:
        ptr = None
    event["ptr"] = ptr
    return event


def _process_trace_log_path(config) -> str | None:
    """Derive a dedicated process-trace log path from the config (or None)."""
    lf = getattr(config, "log_file", None)
    if not lf:
        return None
    if os.path.isdir(lf):
        return os.path.join(lf, "process_trace.log")
    return os.path.join(os.path.dirname(lf) or ".", "process_trace.log")


def _log_process_event(path: str | None, ev: dict) -> None:
    """Write one captured process event to the log file (or stdout). Never raises."""
    stack = " ".join(ev.get("stack", [])) or "<no stack>"
    line = (f"[process-trace] {ev['event']} ptr={ev.get('ptr')} "
            f"handler={ev.get('handler')} ts={ev.get('ts'):.3f} stack=[{stack}]")
    try:
        if path:
            os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
            with open(path, "a") as f:
                f.write(line + "\n")
        else:
            print(line)
    except Exception:
        pass


def resolve_process_trace(gdb, config) -> int:
    """Drain captured process-trace events at a safe point and write them to the log.

    Call from the step driver's post-work / session_status (a safe,
    non-deadlocking section). The events were captured at the hits (the transient
    stop window); here we only read the stored dicts — no GDB command is issued.

    Each event is written TWICE:
      * as a STRUCTURED record into the session's JSONL log (gdb.log_record) — the
        primary, greppable trace, correlated by the process pointer; and
      * as a human-readable line to <log dir>/process_trace.log (a convenience).
    Returns the number of events logged.
    """
    path = _process_trace_log_path(config)
    log_record = getattr(gdb, "log_record", None)
    count = 0
    for hook in (_process_trace_state["add_hook"],
                 _process_trace_state["remove_hook"],
                 _process_trace_state["error_hook"]):
        if hook is None:
            continue
        for ev in hook.consume_events():
            if log_record is not None:
                log_record(_process_trace_record(ev))
            _log_process_event(path, ev)
            count += 1
    return count


# -- Deep Game_Action dispatch trace -- #
#
# A deep, default-OFF trace of dispatch_game_action_for__client. On every
# dispatch it captures, AT THE HIT (a safe, non-nested context — gated on
# GDBSession._in_nested_read, the same way the process-trace capture is):
#   * the callee backtrace (time-sensitive — gone once the transient stop is
#     continued past), and
#   * a lightweight client-scanner snapshot (the client's current uuid/flags/
#     local-space center + its current inbound/outbound game action kind/uuid +
#     queue counts) — one by-value DEBUG_Client_Scanner read.
# The records are drained to the session JSONL + a dedicated log at a safe
# point (the step driver's post-work / session_status). This is the "deep full
# trace of the engine": intentionally NOT fast/snappy (a backtrace + a
# client-scanner read on EVERY dispatch), so it is OFF by default and opted in
# via `trace ga`.


def _capture_game_action_dispatch(gdb, responses) -> dict:
    """Capture one game-action dispatch (GDB I/O) at the hit.

    Run by the BreakpointHook only in a safe, non-nested context (gated on
    GDBSession._in_nested_read). Reads the callee backtrace (time-sensitive),
    the p_game_action (4th arg) / p_client (1st arg) pointers (frame args, 0
    round-trips), and a lightweight client-scanner snapshot. Never raises.
    """
    import time as _t
    event = {"event": "dispatch", "ts": _t.time(), "stack": [],
             "game_action_ptr": None, "client_ptr": None, "client": None}

    frame = None
    for r in responses:
        if r.is_breakpoint_hit() and r.frame is not None:
            frame = r.frame
            break

    # 1. Callee stack (time-sensitive — only correct at the hit).
    event["stack"] = _read_backtrace(gdb)

    # 2. The dispatched game action + the client (frame args, 0 round-trips).
    event["game_action_ptr"] = _arg_value_from_frame(frame, "p_game_action")
    event["client_ptr"] = _arg_value_from_frame(frame, "p_client")

    # 3. Lightweight client-scanner snapshot (the client's current state at the
    #    dispatch): current client uuid/flags/center + current inbound/outbound
    #    game action kind/uuid + queue counts. One by-value struct read.
    try:
        scanner = DebugClientScanner(gdb)
        event["client"] = scanner._parse_struct(scanner.get_scanner())
    except Exception:
        event["client"] = None
    return event


def _ga_dispatch_trace_record(ev: dict) -> dict:
    """Build the structured JSONL record for one game-action dispatch event."""
    return {
        "timestamp": ev.get("ts"),
        "type": "game-action-trace",
        "event": ev.get("event"),            # dispatch
        "game_action_ptr": ev.get("game_action_ptr"),
        "client_ptr": ev.get("client_ptr"),
        "stack": ev.get("stack", []),
        "client": ev.get("client"),          # client-scanner snapshot (or None)
        "context": f"game-action-trace:{ev.get('event')}",
    }


def _ga_dispatch_trace_log_path(config) -> str | None:
    """Derive a dedicated game-action-trace log path from the config (or None)."""
    lf = getattr(config, "log_file", None)
    if not lf:
        return None
    if os.path.isdir(lf):
        return os.path.join(lf, "game_action_trace.log")
    return os.path.join(os.path.dirname(lf) or ".", "game_action_trace.log")


def _log_ga_dispatch_event(path: str | None, ev: dict) -> None:
    """Write one captured game-action dispatch event to the log (or stdout).
    Never raises."""
    stack = " ".join(ev.get("stack", [])) or "<no stack>"
    client = ev.get("client") or {}
    kind = client.get("ga_outbound_kind")
    uuid = client.get("ga_outbound_uuid")
    line = (f"[game-action-trace] dispatch ptr={ev.get('game_action_ptr')} "
            f"client={ev.get('client_ptr')} "
            f"action={kind or '?'}:{uuid or '?'} "
            f"client_uuid={client.get('uuid')} "
            f"center={client.get('center')} "
            f"ts={ev.get('ts'):.3f} stack=[{stack}]")
    try:
        if path:
            os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
            with open(path, "a") as f:
                f.write(line + "\n")
        else:
            print(line)
    except Exception:
        pass


def resolve_game_action_dispatch_trace(gdb, config) -> int:
    """Drain captured game-action dispatch events at a safe point and log them.

    Call from the step driver's post-work / session_status (a safe,
    non-deadlocking section). The events were captured at the hits (backtrace +
    client-scanner snapshot); here we only read the stored dicts — no GDB
    command is issued. Each event is written to the session JSONL (structured)
    and to <log dir>/game_action_trace.log (human-readable). Returns the number
    of events logged.
    """
    hook = _ga_dispatch_deep_trace_state["hook"]
    if hook is None:
        return 0
    path = _ga_dispatch_trace_log_path(config)
    log_record = getattr(gdb, "log_record", None)
    count = 0
    for ev in hook.consume_events():
        if log_record is not None:
            log_record(_ga_dispatch_trace_record(ev))
        _log_ga_dispatch_event(path, ev)
        count += 1
    return count


# -- Non-fatal debug_error reporting -- #
#
# The pair to the crash path: _get_signal_info reports a FATAL stop (a
# signal) with a backtrace built via debug_error.py; the functions below do
# the same for a NON-FATAL debug_error hit (the game keeps running), so the
# step driver surfaces "ERROR: debug_error on step N: <same report shape>".
#
# The capture runs by the BreakpointHook only in a safe, non-nested context
# (the game is stopped at the breakpoint with a clean response stream — the
# same conditions _get_signal_info runs under after a crash), so it may issue
# GDB commands. The game is continued automatically: step_frame_detailed
# treats the hit as an "unexpected_bp" and continues toward the frame target.


def _debug_error_signature(responses) -> str | None:
    """Derive a burst-suppression signature from the STOP response alone.

    Zero GDB I/O: the debug_error breakpoint's stop notification carries the
    stopped frame's args, and debug_error's msg_fmt arg — the error text,
    which by convention begins with the originating function name (e.g.
    "poll_for_collision_node_update, p_global_space__new == 0.") — is a
    stable signature for the error. A storm of the same error (e.g.
    pool-exhaustion allocation failures repeating every frame) therefore
    collapses to ONE signature. Falls back to the stopped frame's
    func:file:line when no msg_fmt arg is present; None when the stop
    response carries no usable frame info (suppression stays off — the
    safe default).
    """
    for r in responses:
        if not r.is_breakpoint_hit():
            continue
        frame = r.frame
        if frame is not None:
            func, file_, line = frame.func, frame.file, frame.line
            args = frame.args or []
        else:
            fr = (r.payload or {}).get("frame", {}) or {}
            func, file_, line = fr.get("func"), fr.get("file"), fr.get("line")
            args = fr.get("args") or []
        for a in args:
            if isinstance(a, dict) and a.get("name") == "msg_fmt":
                value = a.get("value")
                if value:
                    return f"msg={value}"
        if func:
            return f"frame={func}:{file_}:{line}"
    return None


def _capture_debug_error_event(gdb, responses) -> dict:
    """Capture one non-fatal debug_error hit as a full error report (GDB I/O).

    Built with debug_error.build_error_report() — the identical presentation
    the SIGABRT crash path uses:
      - full backtrace, with the frame that CALLED debug_error highlighted
        (adjust_frame_for_debug_error), because debug_error is a trampoline;
      - the relevant frame's arguments (format_arguments_for_frame) — for a
        debug_error hit this includes msg_fmt, the error message text itself
        (e.g. "poll_for_collision_node_update, p_global_space__new == 0."),
        which is exactly the context the old CRASH_ON_ERROR core dumps gave.

    Burst suppression: the signature (see _debug_error_signature) is
    decided from the stop response BEFORE any GDB I/O. Only the first
    full_captures_per_signature occurrences per signature pay for the full
    capture; repeats return None (zero GDB I/O — not even the stack read)
    and are counted in _debug_error_report_state["signatures"], where
    resolve_debug_error_events() surfaces them as one aggregated record per
    signature. (Historically each error cost ~2.5s — an undefined
    -stack-info-arguments round-trip plus a 2s console-fallback read, each
    logged as a gdb_error record — and a storm of thousands of them
    dominated the whole trace.)

    Returns an event dict, or None when nothing usable was captured (the
    BreakpointHook drops None events). Never raises.
    """
    import time as _t
    event = {"event": "debug_error", "ts": _t.time(), "report": "",
             "func": None, "file": None, "line": None, "message": None,
             "stack": []}
    try:
        # The actual error message: debug_error's first argument (msg_fmt)
        # is carried in the stop frame's args by GDB — no round-trip needed.
        # (This is the text the game printed to its stdout; the old
        # CRASH_ON_ERROR core dumps never captured it.) Read it first: it
        # also drives the burst-suppression decision below.
        for r in responses:
            if r.is_breakpoint_hit() and r.frame is not None:
                for a in (r.frame.args or []):
                    if isinstance(a, dict) and a.get("name") == "msg_fmt":
                        event["message"] = a.get("value")
                break

        # Burst suppression — decided before any GDB I/O.
        sig = _debug_error_signature(responses)
        sig_state = None
        if sig is not None:
            sigs = _debug_error_report_state["signatures"]
            sig_state = sigs.setdefault(
                sig,
                {"seen": 0, "full": 0, "suppressed": 0,
                 "suppressed_reported": 0, "last_ts": None})
            sig_state["seen"] += 1
            sig_state["last_ts"] = event["ts"]
            if (sig_state["full"]
                    >= _debug_error_report_state["full_captures_per_signature"]):
                sig_state["suppressed"] += 1
                # A repeat of an already-logged error — no GDB I/O at all.
                # resolve_debug_error_events() reports the count.
                return None

        raw_frames = _read_stack_frames(gdb)
        if not raw_frames:
            return None
        frames = [raw_stack_frame_to_debug_error_frame(i, f)
                  for i, f in enumerate(raw_frames)]
        event["stack"] = [_frame_str(i, f) for i, f in enumerate(raw_frames)]

        # The frame where the error ORIGINATED (debug_error's caller).
        relevant = get_relevant_frame(frames)
        if relevant is not None:
            event["func"] = relevant.get("func")
            loc = relevant.get("location") or ""
            event["file"] = loc.split(":")[0] or None
            event["line"] = loc.rsplit(":", 1)[1] if ":" in loc else None

        report = build_error_report(frames, gdb)
        if event["message"]:
            report = f"Error message: {event['message']}\n" + report
        event["report"] = report
        if sig_state is not None:
            # The full capture succeeded — charge it to the signature.
            sig_state["full"] += 1
    except Exception:
        # A capture failure must never break the driver — but an event with
        # no report is useless, so drop it unless a partial one was built.
        if not event["report"]:
            return None
    return event


def resolve_debug_error_events(gdb, config=None) -> list:
    """Drain captured non-fatal debug_error events at a safe point.

    Call from the step driver's post-work / session_status (a safe,
    non-deadlocking section). Each event is written as a structured record
    into the session's JSONL log (type "debug-error") and returned so the
    calling driver can surface it in its response.

    Suppressed repeats (see _capture_debug_error_event) are drained here
    too: since the previous drain, one aggregated "debug-error" record per
    signature is written (and one synthetic event appended, so the step
    response can show the count). Never raises; returns [] when the hook
    is unregistered/disabled or nothing was captured.
    """
    hook = _debug_error_report_state["hook"]
    if hook is None:
        return []
    events = [ev for ev in hook.consume_events() if ev]
    log_record = getattr(gdb, "log_record", None)
    for ev in events:
        if log_record is not None:
            log_record({
                "timestamp": ev.get("ts"),
                "type": "debug-error",
                "event": "debug_error",
                "func": ev.get("func"),
                "file": ev.get("file"),
                "line": ev.get("line"),
                "message": ev.get("message"),
                "stack": ev.get("stack", []),
                "report": ev.get("report", ""),
            })

    # Surface suppressed repeats as one aggregated record per signature
    # (per drain) — a storm becomes a count, not thousands of records.
    for sig, st in _debug_error_report_state["signatures"].items():
        new_suppressed = st["suppressed"] - st.get("suppressed_reported", 0)
        if new_suppressed <= 0:
            continue
        summary = (f"{new_suppressed} repeat(s) of the same debug_error "
                   f"suppressed (signature: {sig})")
        if log_record is not None:
            log_record({
                "timestamp": st.get("last_ts"),
                "type": "debug-error",
                "event": "debug_error",
                "aggregated": True,
                "signature": sig,
                "count": new_suppressed,
                "total": st["seen"],
                "report": summary,
            })
        events.append({
            "event": "debug_error",
            "ts": st.get("last_ts"),
            "aggregated": True,
            "report": summary,
        })
        st["suppressed_reported"] = st["suppressed"]
    return events


def format_debug_error_events(events: list, count: int, fatal: bool = False) -> str:
    """Format drained debug_error events for a step response.

    Mirrors the SIGABRT crash message shape ("ERROR: ... on step N/count."
    followed by the report). When ``fatal`` is False (the common case now —
    no CRASH_ON_ERROR, the game KEEPS running) the section header says so
    explicitly; when True the events are context captured before a real
    crash on the same step. Reports are capped (the full history is in the
    JSONL log). Returns "" when there are no events.
    """
    if not events:
        return ""
    shown = events[:5]
    if fatal:
        header = (f"{len(events)} debug_error(s) occurred before the crash "
                  f"on this step:")
    else:
        header = (f"{len(events)} non-fatal debug_error(s) occurred during "
                  f"this step (no CRASH_ON_ERROR — the game kept running):")
    lines = ["", header]
    for ev in shown:
        step = ev.get("step")
        step_str = f"step {step}/{count}" if step else "this step"
        lines.append(
            f"ERROR: debug_error on {step_str}.\n"
            f"{ev.get('report') or '(no report captured)'}"
        )
    if len(events) > len(shown):
        lines.append(
            f"  ... and {len(events) - len(shown)} more "
            f"(see the session log for the full history).")
    return "\n".join(lines)


def process_handler_driver(gdb: GDBSession, config: LavConfig, kwargs: dict) -> str:
    """Resolve the run-handler name of a process (by pointer), safely.

    Property 4 of PLANS/process_trace.md. A process's run-handler is bound
    AFTER creation, so it is only meaningful once the process is running; this runs
    at a safe, halted point (a scanner context — never a transient stop, so no
    deadlock) to read ``((Process*)<ptr>)->m_process_run__handler`` and resolve the
    function name. The result is logged as a process-trace record (event=handler,
    keyed by ptr) so it correlates with the process's create / error / remove
    events. The AI invokes it with a ptr it saw in the trace to learn "what handler
    caused the error". Module-level (not a closure) so it registers in both the full
    and minimal driver paths.
    """
    process_ptr = kwargs.get("process_ptr") or kwargs.get("ptr") or ""
    scanner = DebugProcessScanner(gdb)
    info = scanner.scan(process_ptr, _process_trace_state["sym_cache"])
    ptr = info.get("ptr")
    handler = info.get("handler")
    gdb.log_record(_process_trace_record(
        {"event": "handler", "ts": time.time(), "ptr": ptr,
         "handler": handler, "stack": []}))
    if not ptr:
        return "ERROR: no process pointer given (pass process_ptr=0x...)."
    if handler is None:
        return f"process {ptr}: handler unbound or not a known symbol."
    return f"process {ptr}: handler = {handler}"


def _format_process_pool(pool: dict) -> str:
    """Render a DebugProcessScanner.scan_pool() result as a human-readable report.

    The point is to distinguish pool SATURATION (the 512-slot pool is full — a
    capacity problem) from a single handler over-accumulating (a leak). The
    by-handler tally is the discriminator.
    """
    if pool.get("error"):
        return f"ERROR: {pool['error']}"
    cap = pool.get("capacity", 512)
    active = pool.get("active", 0)
    free = pool.get("free", 0)
    sat = pool.get("saturated", False)
    if sat:
        state = "SATURATED (pool full — new allocations will fail)"
    elif free <= 16:
        state = "near-full"
    else:
        state = "ok"
    lines = [f"Process pool: {active}/{cap} active, {free} free — {state}"]
    by_handler = pool.get("by_handler") or {}
    if by_handler:
        lines.append("By run-handler (count  handler):")
        for h, n in by_handler.items():
            lines.append(f"  {n:>4}  {h}")
    by_kind = pool.get("by_kind") or {}
    if by_kind:
        lines.append("By Process_Kind:")
        for k, n in by_kind.items():
            lines.append(f"  {n:>4}  {k}")
    return "\n".join(lines)


def process_pool_driver(gdb: GDBSession, config: LavConfig, kwargs: dict) -> str:
    """Snapshot the process pool: how many of the 512 slots are occupied and by
    which run-handlers.

    Drives the C ``DEBUG_Process_Scanner`` (``debug_get_process_scanner(&game)``)
    to enumerate the active processes, then tallies them by handler and by
    Process_Kind. This is the fast, one-shot diagnostic that distinguishes a pool
    SATURATION (capacity) problem from a specific handler over-accumulating (a
    leak) — e.g. dozens of ``global_space__resolve`` / ``deserialize_global_space``
    processes vs. a single handler that should have completed.

    MUST be called while the game is HALTED (e.g. at a stuck point after a step
    timeout) — the scanner call runs in the inferior. Module-level (not a
    closure) so it registers in both the full and minimal driver paths.
    """
    if gdb.is_closed:
        return "ERROR: GDB session is closed."
    scanner = DebugProcessScanner(gdb)
    if scanner.get_scanner() is None:
        return ("ERROR: process scanner unavailable (release build without debug "
                "symbols, or game not started/halted).")
    max_iter = kwargs.get("max_iter") or DebugProcessScanner._POOL_CAPACITY
    try:
        max_iter = int(max_iter)
    except (TypeError, ValueError):
        max_iter = DebugProcessScanner._POOL_CAPACITY
    pool = scanner.scan_pool(max_iter=max_iter)
    return _format_process_pool(pool)


def _center_display(center: dict | None) -> str:
    """Render a local-space center as ``(x,y,z)``.

    The ``VECTOR__3i32__OUT_OF_BOUNDS`` sentinel is ``{BIT(31), BIT(31), BIT(31)}``
    — ``-2147483648`` as a signed i32 — and ``is_vectors_3i32__out_of_bounds`` is
    true if ANY component matches. A client whose center is still that sentinel has
    not been positioned yet (world load not complete), so read it as such rather
    than a literal coordinate.
    """
    if not center:
        return "(unknown)"
    x, y, z = center.get("x"), center.get("y"), center.get("z")
    if any(v == -(1 << 31) for v in (x, y, z)):
        return "(out of bounds / not positioned)"
    return f"({x},{y},{z})"


def _format_client_list(result: dict) -> str:
    """Render a DebugClientScanner.list_clients() result as a report."""
    if result.get("error"):
        return f"ERROR: {result['error']}"
    clients = result.get("clients") or []
    declared = result.get("declared")
    head = f"Clients: {len(clients)} connected"
    if declared is not None:
        head += f" (scanner reports {declared})"
    lines = [head]
    if not clients:
        lines.append("  (no connected clients)")
        return "\n".join(lines)
    for c in clients:
        lines.append(
            f"  uuid={c.get('uuid')}  flags={c.get('flags')}  "
            f"local_space_center={_center_display(c.get('center'))}"
        )
    return "\n".join(lines)


def _format_client_actions(result: dict) -> str:
    """Render a DebugClientScanner.scan_actions() result as a report.

    Surfaces the queue lengths (the clog magnitude) and the by-kind tally (what is
    clogging the queue — e.g. a wall of Global_Space__Store after a mass drop).
    """
    if result.get("error"):
        return f"ERROR: {result['error']}"
    direction = result.get("direction", "outbound")
    inbound = result.get("inbound_count", 0)
    outbound = result.get("outbound_count", 0)
    total = result.get("total", 0)
    tallied = result.get("tallied", 0)
    complete = result.get("complete", False)
    cur_kind = result.get("current_kind")
    lines = [
        f"Client game-action queues: inbound={inbound}  outbound={outbound}"
    ]
    if total:
        scope = f"{total}" if complete else f"{tallied}/{total} (partial sample)"
        lines.append(f"{direction.capitalize()} queue: {scope} action(s)")
        if cur_kind:
            lines.append(f"  current: {cur_kind}")
        by_kind = result.get("by_kind") or {}
        if by_kind:
            lines.append(f"  by Game_Action_Kind {'' if complete else '(sampled)'}:")
            for k, n in by_kind.items():
                lines.append(f"    {n:>6}  {k}")
    else:
        lines.append(f"{direction.capitalize()} queue: empty")
    return "\n".join(lines)


def client_list_driver(gdb: GDBSession, config: LavConfig, kwargs: dict) -> str:
    """List every connected client: uuid, flags, and its local-space center.

    Drives the C ``DEBUG_Client_Scanner`` (``debug_get_client_scanner(&game)``),
    walking ``m_next_client``. The ``local_space_center`` field is the diagnostic
    for a stark center jump (e.g. ``{0,63,2}`` while the manager center is
    ``{0,1,3}``) that the incremental scroll path cannot absorb. Module-level (not
    a closure) so it registers in both the full and minimal driver paths. MUST be
    called while the game is HALTED.
    """
    if gdb.is_closed:
        return "ERROR: GDB session is closed."
    scanner = DebugClientScanner(gdb)
    if scanner.get_scanner() is None:
        return ("ERROR: client scanner unavailable (release build without debug "
                "symbols, or game/world not started).")
    max_iter = kwargs.get("max_iter")
    try:
        max_iter = int(max_iter) if max_iter is not None else None
    except (TypeError, ValueError):
        max_iter = None
    return _format_client_list(scanner.list_clients(max_iter=max_iter))


def client_actions_driver(gdb: GDBSession, config: LavConfig, kwargs: dict) -> str:
    """Snapshot the current client's game-action queue (lengths + kind tally).

    Drives the C ``DEBUG_Client_Scanner``, walking ``m_next_game_action__<dir>`` to
    tally the queue by ``Game_Action_Kind``. This is the diagnostic for a queue
    CLOG: a world-load that mass-drops global spaces parks thousands of
    ``Global_Space__Store`` actions in a client's outbound queue. *direction* is
    'outbound' (default) or 'inbound'; *max_iter* bounds the walk (default is a
    representative sample). Module-level (not a closure) so it registers in both
    the full and minimal driver paths. MUST be called while the game is HALTED.
    """
    if gdb.is_closed:
        return "ERROR: GDB session is closed."
    direction = kwargs.get("direction") or "outbound"
    if direction not in ("inbound", "outbound"):
        return "ERROR: direction must be 'outbound' or 'inbound'."
    scanner = DebugClientScanner(gdb)
    if scanner.get_scanner() is None:
        return ("ERROR: client scanner unavailable (release build without debug "
                "symbols, or game/world not started).")
    max_iter = kwargs.get("max_iter")
    try:
        max_iter = int(max_iter) if max_iter is not None else None
    except (TypeError, ValueError):
        max_iter = None
    return _format_client_actions(
        scanner.scan_actions(direction=direction, max_iter=max_iter))


def _normalize_watchdog_timeout(raw: Any) -> float:
    """Parse a step watchdog timeout and normalize it.

    Returns a float seconds value where a NEGATIVE input (e.g. ``-1``) maps to
    ``0.0`` (an unbounded step — no watchdog). ``0`` stays ``0`` (unbounded,
    legacy); positive values pass through unchanged. Raises ``ValueError`` /
    ``TypeError`` for non-numeric input (the caller turns that into an error).
    """
    timeout = float(raw)
    return 0.0 if timeout < 0 else timeout


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
            command=[self.config.gdb_path] + self.config.gdb_args,
            timeout_sec=15.0,
            log_file=self.config.log_file,
        )
        self._started = False
        self._breakpoint_hooks_registered = False

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

    # -- Breakpoint hook registration -- #

    def _register_breakpoint_hooks(self) -> None:
        """Register breakpoint hooks for key game functions.

        These hooks fire when GDB hits a breakpoint at a specific function.
        """
        _register_breakpoint_hooks_for_gdb(self.gdb)


def _register_breakpoint_hooks_for_gdb(gdb: GDBSession) -> None:
    """Register breakpoint hooks on a GDBSession for key game functions.

    Breakpoints are set on:
    1. remove_process_from__process_table → log process removal
    2. add_process_to__process_table → log process addition
    3. debug_error → report the non-fatal error (backtrace + args, like the
       old SIGABRT crash report); the game keeps running
    4. initialize_ui_manager → log UI manager initialization
    5. receive_game_action_for__client → Game_Action receipt marker
    6. dispatch_game_action_for__client → Game_Action dispatch marker
    7. game.c:702 (the run_game "TRANSITION" line) → scene transition
    8. reset__game_tick_timer → frame heartbeat (once per frame, at the
       frame boundary; arms the step watchdog — see FRAME_HEARTBEAT_FUNC)

    The Process hooks and the Game_Action hooks are toggleable BreakpointHooks
    (on by default); the `trace` command enables/disables exactly those groups.
    The debug_error reporting hook, the initialize_ui_manager hook, the
    scene-transition hook, and the frame-heartbeat hook are always registered
    and are not affected by `trace`. The scene-transition hook only flags
    _scene_state["dirty"] (it must not issue GDB commands — it can fire
    mid-poll); the scene read is deferred to resolve_pending_scene_transitions()
    at a safe point. The session_status / step drivers surface the result.

    Only registers once per GDBSession (idempotent).
    """
    registered = getattr(gdb, '_breakpoint_hooks_registered', False)
    if registered:
        return
    gdb._breakpoint_hooks_registered = True

    from mcp_layered.debug_response import DebugResponse

    # Hooks 1-3: process-lifecycle TRACE (on by default). Each is a
    # BreakpointHook whose capture (GDB I/O, gated to a safe, non-nested context)
    # records the process pointer + callee stack at the hit. Together they trace a
    # process pool slot's ephemeral lifecycle, correlated by the process pointer:
    #   add  -> the callee that FORMED the process (creation stack)
    #   error-> the process whose run-handler raised debug_error (poll_process_manager)
    #   remove-> the callee that DESTRUCTED the process (removal stack)
    # Events accumulate in captured_events and are drained + written to the log by
    # resolve_process_trace() at the driver's safe point (see _capture_error_event
    # for the debug_error hook, which reads the ptr from the poll_process_manager
    # frame — the handler is invoked inside it).
    _process_trace_state["add_hook"] = BreakpointHook(
        gdb, "process.add", "add_process_to__process_table",
        capture=lambda g, r: _capture_process_event(g, r, "add"))
    _process_trace_state["remove_hook"] = BreakpointHook(
        gdb, "process.remove", "remove_process_from__process_table",
        capture=lambda g, r: _capture_process_event(g, r, "remove"))
    _process_trace_state["error_hook"] = BreakpointHook(
        gdb, "process.error", "debug_error",
        capture=_capture_error_event)
    if _process_trace_state["enabled"]:
        _process_trace_state["add_hook"].enable()
        _process_trace_state["remove_hook"].enable()
        _process_trace_state["error_hook"].enable()

    # Hook: non-fatal debug_error REPORTING (always on; not part of `trace`).
    #
    # Since -DCRASH_ON_ERROR was dropped from the build, debug_error() prints
    # the error and RETURNS — the game keeps running, so the step driver never
    # sees a crash signal and the error is otherwise invisible. This
    # BreakpointHook stops the game at every debug_error and captures, via
    # debug_error.build_error_report(), the SAME report the old SIGABRT crash
    # path produced (backtrace with the debug_error caller highlighted +
    # arguments, which include the msg_fmt error text). The game is continued
    # automatically by step_frame_detailed (the hit is an "unexpected_bp");
    # the event is drained by resolve_debug_error_events() at the driver's
    # safe point and surfaced in the step response.
    #
    # Burst suppression: only the first full_captures_per_signature
    # occurrences per signature (the msg_fmt error text, read from the stop
    # response at zero GDB cost) get the full capture; repeats cost zero GDB
    # I/O and are surfaced as one aggregated record per signature. This
    # keeps an error STORM (e.g. pool-exhaustion allocation failures
    # repeating every frame) from stalling the trace — historically each
    # error cost ~2.5s of GDB round-trips.
    #
    # (This coexists with the process-trace "process.error" hook above, which
    # breaks on the SAME function for a different purpose — correlating the
    # erroring process pointer. GDB allows both breakpoints at one address;
    # each hook matches on the frame function, so both react to the one stop.)
    _debug_error_report_state["hook"] = BreakpointHook(
        gdb, "debug_error", "debug_error",
        capture=_capture_debug_error_event)
    if _debug_error_report_state["enabled"]:
        _debug_error_report_state["hook"].enable()

    # Hook: frame heartbeat (always on; not part of `trace`).
    #
    # reset__game_tick_timer runs exactly once per frame, at the frame
    # boundary, in every scene. No handler/capture (zero GDB I/O) — the
    # step driver's watchdog recognizes hits of this breakpoint by function
    # name (see FRAME_HEARTBEAT_FUNC) and extends its "time since last
    # frame boundary" deadline ONLY on these. Best-effort: if the symbol is
    # absent from the binary, enable() returns False and the step driver
    # falls back to the legacy unbounded behavior (no watchdog) rather than
    # false-timing-out long frames.
    _frame_heartbeat_state["hook"] = BreakpointHook(
        gdb, "frame.heartbeat", FRAME_HEARTBEAT_FUNC)
    _frame_heartbeat_state["hook"].enable()

    # Hook 3: initialize_ui_manager
    def on_init_ui(responses: list[DebugResponse]) -> list[DebugResponse]:
        for r in responses:
            if r.is_breakpoint_hit() and r.frame and r.frame.func:
                print(f"\n[breakpoint] initialize_ui_manager triggered")
                # A UI manager was (re)allocated, so any cached element
                # contents may be stale. Clear the cache so the next `[]`
                # selector forces a fresh `ui list`. This is a pure attribute
                # write (no GDB I/O), so it is safe to run in a nested
                # (mid-poll) hook context where GDB commands would deadlock.
                gdb._ui_cache = None
        return responses
    gdb.register_breakpoint_hook("initialize_ui_manager", on_init_ui)

    # Hook 4: Game_Action RECEIVE lifecycle marker. A lightweight BreakpointHook
    # (print only, no GDB I/O — it can fire mid-poll), toggled together with the
    # Process hooks by `trace`.
    def on_receive_action(responses: list[DebugResponse]) -> list[DebugResponse]:
        for r in responses:
            if r.is_breakpoint_hit() and r.frame and r.frame.func:
                print(f"\n[breakpoint] receive_game_action_for__client triggered")
        return responses

    _game_action_trace_state["receive_hook"] = BreakpointHook(
        gdb, "game_action.receive",
        "receive_game_action_for__client",
        handler=on_receive_action)
    if _game_action_trace_state["enabled"]:
        _game_action_trace_state["receive_hook"].enable()

    # Hook 5: Deep Game_Action DISPATCH trace (OFF by default; toggled by
    # `trace ga`). A BreakpointHook whose gated `capture` (GDB I/O only in a
    # safe, non-nested context) records the callee backtrace + a client-scanner
    # snapshot at the hit, mirroring the process-trace pattern. Events are
    # drained to the log by resolve_game_action_dispatch_trace() at the driver's
    # safe point. The deep trace is deliberately NOT in the `trace` (no-arg)
    # group — it is expensive and defaults off.
    _ga_dispatch_deep_trace_state["hook"] = BreakpointHook(
        gdb, "game_action.dispatch",
        "dispatch_game_action_for__client",
        capture=_capture_game_action_dispatch)
    if _ga_dispatch_deep_trace_state["enabled"]:
        _ga_dispatch_deep_trace_state["hook"].enable()

    # Hook 6: scene transition tracking — LINE breakpoint at the run_game
    # "TRANSITION" marker (game.c:702), NOT a function breakpoint.
    #
    # WHY a line breakpoint: set_active_scene_for__scene_manager is inlined
    # by -O2 at every call site, so a breakpoint on its (dead) out-of-line
    # copy never fires. game.c:702 is the debug_info("TRANSITION ...") line
    # at the top of the run_game scene loop; the loop body
    # (m_enter_scene_handler) blocks for a scene's whole lifetime, so that
    # line runs exactly once per scene entry — a clean, inlining-immune
    # transition marker.
    #
    # WHY the hook makes NO GDB calls: it can fire while the step driver is
    # polling get_gdb_response, where a nested GDB command deadlocks the
    # connection. So it only flags _scene_state["dirty"]. The real scene
    # read is deferred to resolve_pending_scene_transitions(), which runs
    # at a safe point (after the step returns / on session_status) and
    # records the transition in _scene_state for the MCP drivers to surface.
    def on_scene_transition(responses: list[DebugResponse]) -> list[DebugResponse]:
        for r in responses:
            if not r.is_breakpoint_hit() or not r.frame:
                continue
            f = r.frame
            if (f.file or "").endswith(_SCENE_TRANSITION_FILE) and \
               str(f.line) == str(_SCENE_TRANSITION_LINE):
                _scene_state["dirty"] += 1
                print(f"\n[scene] transition pending "
                      f"({_SCENE_TRANSITION_FILE}:{_SCENE_TRANSITION_LINE})")
        return responses

    # Set the line breakpoint directly (the function-breakpoint helper can't
    # target a line). Degrade gracefully if the line isn't in the binary.
    try:
        for r in gdb.write(
            f"-break-insert {_SCENE_TRANSITION_FILE}:{_SCENE_TRANSITION_LINE}"
        ):
            if r.type == ResponseType.RESULT and r.raw.get("message") == "error":
                print(f"\n[scene] WARNING: could not set breakpoint "
                      f"{_SCENE_TRANSITION_FILE}:{_SCENE_TRANSITION_LINE}: "
                      f"{r.raw.get('msg')}")
    except Exception as e:
        print(f"\n[scene] WARNING: breakpoint setup failed: {e}")
    gdb.add_hook(on_scene_transition)


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

    # Reuse the shared SessionState if a prior create_session() already created
    # it; otherwise create it. Re-register the drivers on EVERY call
    # (register_driver overwrites, so this is idempotent), so create_session()
    # stays robust: even if a test or a prior session unregistered the builtin
    # drivers, a fresh create_session() restores the full set while keeping the
    # ONE shared state that already-registered drivers captured.
    #
    # (An earlier one-shot `_drivers_registered` guard made this non-idempotent:
    # once set, it skipped re-registration forever, so driver unregistration by
    # other tests leaked into later sessions and broke session_start.)
    global _SESSION_STATE
    if _SESSION_STATE is None:
        _SESSION_STATE = SessionState()
    _session_state = _SESSION_STATE

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

        # Register breakpoint hooks now that the executable is loaded
        _register_breakpoint_hooks_for_gdb(gdb)

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

        # Scene state (grounding truth for QA agents): resolve any pending
        # transition (safe point — the game is stopped here) and show the
        # active scene + most recent transitions.
        resolve_pending_scene_transitions(gdb)
        # Process trace: drain events captured at the (transient) process
        # create/remove stops and write them to the log (not the MCP response).
        resolve_process_trace(gdb, config)
        # Deep Game_Action dispatch trace (off by default; `trace ga`): drain
        # events captured at the (transient) dispatch stops to the log.
        resolve_game_action_dispatch_trace(gdb, config)
        # Non-fatal debug_error events: drain (logs them as structured
        # "debug-error" records) and surface the most recent ones as
        # one-line summaries — the full report of each is in the session log.
        recent_debug_errors = resolve_debug_error_events(gdb, config)
        if recent_debug_errors:
            status_parts.append(
                f"debug_error events since last status: "
                f"{len(recent_debug_errors)}")
            for ev in recent_debug_errors[-3:]:
                if ev.get("file") and ev.get("line"):
                    loc = f" at {ev['file']}:{ev['line']}"
                elif ev.get("file"):
                    loc = f" at {ev['file']}"
                else:
                    loc = ""
                status_parts.append(
                    f"  ERROR: debug_error in {ev.get('func') or '?'}{loc}")
        scene_section = format_scene_status()
        if scene_section:
            status_parts.append(scene_section)

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
    register_driver("trace", trace_driver)

    # -- navigation drivers -- #
    # These bridge to mcp/ logic using the raw gdbmi via GDBSession.gdbmi

    from mcp.gdb_nav_utils import step_frame, step_frame_detailed
    from mcp_layered.layer_pygdbmi import detect_signal

    def _get_signal_info(gdb: GDBSession) -> str:
        """Get signal info from the current stopped state.

        Returns a string with the signal name, full backtrace, and any
        relevant context about the crash (e.g., faulting address for SIGSEGV).

        Uses debug_error.py to identify the most relevant frame:
        - If 'debug_error' is in the stack trace, moves to the caller frame
        - If not, uses the current frame
        - Attempts to print argument values (ptr addresses for pointers)

        Note: The backtrace is parsed by debug_error.py from the structured
        stack frames returned by GDB. All responses from GDB are fully consumed
        before debug_error.py processes them, ensuring parsing assumptions hold.
        """
        # Ensure all pending GDB responses are consumed before parsing
        try:
            gdb.write("-gdb-set confirm off")
        except Exception:
            pass

        try:
            # Get full backtrace using -stack-list-frames, as structured frames
            # (the format debug_error.py's adjust_frame_for_debug_error expects)
            frames = []
            try:
                responses = gdb.write("-stack-list-frames")
                for r in responses:
                    if r.type.value == "result" and r.raw.get("message") == "done":
                        payload = r.raw.get("payload") or {}
                        frame_list = payload.get("stack", [])
                        for i, frame in enumerate(frame_list):
                            if isinstance(frame, dict):
                                frames.append(
                                    raw_stack_frame_to_debug_error_frame(i, frame))
                        break
            except Exception:
                pass

            # debug_error.py adjusts the frames (highlighting the debug_error
            # caller) and builds the report: backtrace + argument values.
            if frames:
                return build_error_report(frames, gdb)

            # Fallback: if -stack-list-frames failed
            try:
                responses = gdb.write("-stack-info-frame")
                for r in responses:
                    if r.type.value == "result" and r.raw.get("message") == "done":
                        payload = r.raw.get("payload") or {}
                        frame_obj = payload.get("frame", {})
                        if isinstance(frame_obj, dict):
                            pc = frame_obj.get("pc", "?")
                            func = frame_obj.get("func", "?")
                            file = frame_obj.get("file", "")
                            line = frame_obj.get("line", "")
                            if file and line:
                                loc = f"{file}:{line}"
                            elif file:
                                loc = file
                            else:
                                loc = f"pc={pc}"
                            return f"#0 {func} at {loc}"
                        break
            except Exception:
                pass

            return "(no frame info available)"
        except Exception as e:
            return f"(could not get signal info: {e})"

    def step_driver(gdb: GDBSession, config: LavConfig, kwargs: dict) -> str:
        """Advance one or more game frames.

        Kwargs:
            count:   frames to step (default 1).
            timeout: watchdog in seconds — the maximum time allowed
                     WITHOUT the game crossing a frame boundary (the
                     reset__game_tick_timer heartbeat, once per frame).
                     Default 30.0. As long as the game keeps crossing
                     frame boundaries it is game-looping and the step
                      never times out, however long individual frames take.
                      0 — or any NEGATIVE value, e.g. -1 — disables the watchdog
                      (unbounded step). The watchdog exists because a non-fatal error can
                     leave the game alive but stuck inside one frame
                     (e.g. an infinite debug_error retry loop) — the bp
                     storm keeps the GDB idle-timeout alive, so only a
                     frame-boundary watchdog can detect it.
        """
        count = kwargs.get("count", 1)
        if count < 1:
            return "ERROR: count must be >= 1."
        try:
            # A negative timeout (e.g. -1) is normalized to 0.0 (unbounded —
            # no watchdog); see _normalize_watchdog_timeout.
            timeout = _normalize_watchdog_timeout(kwargs.get("timeout", 30.0))
        except (TypeError, ValueError):
            return "ERROR: timeout must be a number of seconds."

        # The watchdog can only be armed if the frame-heartbeat breakpoint
        # actually exists in this binary; otherwise fall back to the legacy
        # unbounded behavior (a watchdog with no heartbeat would
        # false-time-out every frame).
        heartbeat_hook = _frame_heartbeat_state.get("hook")
        heartbeat_func = (
            FRAME_HEARTBEAT_FUNC
            if (heartbeat_hook is not None and heartbeat_hook.enabled)
            else None
        )
        if heartbeat_func is None and timeout > 0:
            timeout = 0.0

        # Snapshot the transition log so we can report the full chain of
        # transitions that occur DURING this step.
        transitions_before = len(_scene_state["transitions"])

        # Non-fatal debug_error events captured during this step (no
        # CRASH_ON_ERROR — the game keeps running, so these are surfaced in
        # the step response in the same shape the SIGABRT crash report had).
        debug_error_events = []
        current_step = 0

        def _resolve() -> None:
            """Resolve deferred state at this safe point (side effect only;
            idempotent — a no-op while clean): any pending scene transition,
            drain process-trace events captured at the (transient) process
            stops to the log, drain the deep Game_Action dispatch trace (off by
            default; `trace ga`), and drain non-fatal debug_error events (tagged
            with the step they occurred in) for the response."""
            resolve_pending_scene_transitions(gdb)
            resolve_process_trace(gdb, config)
            resolve_game_action_dispatch_trace(gdb, config)
            for ev in resolve_debug_error_events(gdb, config):
                ev["step"] = current_step
                debug_error_events.append(ev)

        def _scene_suffix() -> str:
            """'Scene transitions: A -> B -> C' line for the transitions
            recorded since this step began, or '' if none."""
            line = format_scene_transitions(transitions_before)
            return f"\n{line}" if line else ""

        try:
            for i in range(count):
                current_step = i + 1
                # Watchdog = max seconds without a frame-boundary (heartbeat)
                # crossing; extended on every heartbeat hit inside
                # step_frame_detailed. timeout=0 (or a missing heartbeat bp)
                # = legacy unbounded step.
                hit, stop_reason = step_frame_detailed(
                    gdb.gdbmi, "manage_game__post_render",
                    timeout=timeout, heartbeat_func=heartbeat_func
                )
                if not hit:
                    if stop_reason and stop_reason.startswith("signal_"):
                        sig = stop_reason[7:]  # Remove "signal_" prefix
                        _resolve()
                        sig_info = _get_signal_info(gdb)
                        return (
                            f"ERROR: Game crashed with {sig} "
                            f"on step {i+1}/{count}.\n{sig_info}"
                            f"{format_debug_error_events(debug_error_events, count, fatal=True)}"
                            f"{_scene_suffix()}"
                        )
                    _resolve()
                    if timeout > 0:
                        detail = (
                            f" (no frame boundary crossed within {timeout:g}s — "
                            f"the game may be stuck inside a frame, e.g. in a "
                            f"non-fatal debug_error retry loop)"
                        )
                    else:
                        detail = ""
                    return (
                        f"ERROR: timed out waiting for manage_game__post_render "
                        f"on step {i+1}/{count}.{detail}"
                        f"{format_debug_error_events(debug_error_events, count)}"
                        f"{_scene_suffix()}"
                    )

                # Finish the post_render frame. -exec-finish also lets the
                # GDB response stream settle after step_frame_detailed's
                # polling — a scene read while still stopped inside
                # post_render can fail, so we resolve only after this.
                finish_responses = gdb.write("-exec-finish")
                sig = detect_signal(finish_responses)
                if sig:
                    sig_info = _get_signal_info(gdb)
                    return (
                        f"ERROR: Game crashed with {sig} "
                        f"on step {i+1}/{count}.\n{sig_info}"
                        f"{format_debug_error_events(debug_error_events, count, fatal=True)}"
                        f"{_scene_suffix()}"
                    )
                # Safe point (stopped after post_render, clean connection):
                # resolve any scene transition that happened this frame.
                _resolve()

            _resolve()
            return (
                f"Stepped {count} game frame(s) to post-render."
                f"{format_debug_error_events(debug_error_events, count)}"
                f"{_scene_suffix()}"
            )
        except Exception as e:
            _resolve()
            return (
                f"ERROR stepping frame: {type(e).__name__}: {e}"
                f"{format_debug_error_events(debug_error_events, count)}"
                f"{_scene_suffix()}"
            )

    def navigate_source_driver(gdb: GDBSession, config: LavConfig, kwargs: dict) -> str:
        """Print full backtrace and source of current frame."""
        try:
            responses = gdb.write("-stack-list-frames")
            frame_lines = []
            current_found = False
            for r in responses:
                if r.type.value == "result" and r.raw.get("message") == "done":
                    payload = r.raw.get("payload") or {}
                    frames = payload.get("stack", [])
                    for i, frame in enumerate(frames):
                        if isinstance(frame, dict):
                            level = frame.get("level", str(i))
                            func = frame.get("func", "?")
                            file = frame.get("file", "")
                            line = frame.get("line", "")
                            addr = frame.get("addr", "")
                            if file and line:
                                loc = f"{file}:{line}"
                            elif addr:
                                loc = f"addr {addr}"
                            else:
                                loc = "???"
                            bt_line = f"#{level} {func} at {loc}"
                            frame_lines.append(bt_line)
                            # Also get source context for current frame (level 0)
                            if level == "0" or level == 0:
                                current_found = True
                    break

            # Fallback: if -stack-list-frames didn't work, use -stack-info-frame
            if not frame_lines:
                responses = gdb.write("-stack-info-frame")
                for r in responses:
                    if r.type.value == "result" and r.raw.get("message") == "done":
                        payload = r.raw.get("payload") or {}
                        frame_obj = payload.get("frame", {})
                        if isinstance(frame_obj, dict):
                            level = frame_obj.get("level", "0")
                            func = frame_obj.get("func", "?")
                            file = frame_obj.get("file", "")
                            line = frame_obj.get("line", "")
                            addr = frame_obj.get("addr", "")
                            if file and line:
                                loc = f"{file}:{line}"
                            elif addr:
                                loc = f"addr {addr}"
                            else:
                                loc = "???"
                            frame_lines.append(f"#{level} {func} at {loc}")
                        break

            if frame_lines:
                return f"Backtrace:\n" + "\n".join(frame_lines)
            return "Backtrace: (no frames available)"
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

    # -- process handler (property 4: safe, on-demand handler-name resolution) -- #
    # (process_handler_driver is module-level so it also registers in the
    # minimal drivers; see its definition above.)
    register_driver("process_handler", process_handler_driver)
    # -- process pool snapshot (C DEBUG_Process_Scanner; self-contained) -- #
    register_driver("process_pool", process_pool_driver)
    # -- client scanner (C DEBUG_Client_Scanner; self-contained) -- #
    register_driver("client_list", client_list_driver)
    register_driver("client_actions", client_actions_driver)

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
                # Cache the structured table on the session for `[]` selector
                # resolution (e.g. ui invoke clicked [type=*Button,n=2]).
                # Element pointers are stable pool slots, so the cache stays
                # address-valid; `ui list` is the freshness mechanism and the
                # initialize_ui_manager hook clears it on a manager rebuild.
                gdb._ui_cache = table
                managers = table.get("ui_managers", {})
                if not managers:
                    return "No UI managers found."
                lines = ["UI Elements:"]
                total = 0
                # Handler names come for free: the scanner's batched iteration
                # already prints each handler as "0xADDR <symbol>" and
                # _normalize_handler_ptr keeps that annotation. We only fall
                # back to resolve_function_name (cached) for the rare
                # unannotated address — so no per-handler GDB round-trip in the
                # common case (see PLANS/ui_scan_latency.md).
                func_cache: dict = {}
                for mgr_ptr, mgr in sorted(managers.items()):
                    elements = mgr.get("ui_elements", {})
                    for el_ptr, info in sorted(elements.items()):
                        uuid_val = info.get("uuid", "?")
                        kind = info.get("kind", "?")
                        handlers = info.get("handlers", {})
                        parts = []
                        for name in sorted(handlers):
                            val = handlers[name]
                            if val is None:
                                continue
                            m = _FUNC_ANNOT_RE.search(val)
                            if m:  # name available at zero round-trip cost
                                parts.append(f"{name}={m.group(1)}")
                                continue
                            addr = val.split()[0]  # unannotated: resolve (cached)
                            func = resolve_function_name(gdb, addr, func_cache)
                            parts.append(f"{name}={func}" if func else name)
                        handler_names = ", ".join(parts) if parts else "none"
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
    """Register minimal fallback drivers when mcp/ is not available.

    Re-registered on every call (the minimal drivers hold no shared state),
    so it stays idempotent even if a test unregistered the fallback drivers.
    """
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
    register_driver("trace", trace_driver)

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
    # process_handler is self-contained (no mcp/ dependency) — real driver.
    register_driver("process_handler", process_handler_driver)
    # process_pool is self-contained (C DEBUG_Process_Scanner) — real driver.
    register_driver("process_pool", process_pool_driver)
    # client_list / client_actions are self-contained (C DEBUG_Client_Scanner).
    register_driver("client_list", client_list_driver)
    register_driver("client_actions", client_actions_driver)
    register_driver("input_read", _not_implemented("input_read"))
    register_driver("input_write", _not_implemented("input_write"))
    register_driver("ui_list", _not_implemented("ui_list"))
    register_driver("ui_invoke", _not_implemented("ui_invoke"))
    register_driver("graphics_screenshot", _not_implemented("graphics_screenshot"))
    register_driver("audio_list", _not_implemented("audio_list"))
    register_driver("audio_listen", _not_implemented("audio_listen"))
