# LAYERS.md — Layered Architecture of `mcp_layered/`

This document describes the stratified layering structure of `mcp_layered/`, a
refactored, hermit-crab shell-swap of `mcp/`. The existing `mcp/` code is
functional working code — the refactor replicates its semantics under a clean
layered architecture so that each concern is isolated, testable, and
composable.

## Layering Principle

Each layer **depends only on the layer directly below it**. Higher layers never
import or call lower layers directly except through the interface exposed by the
layer immediately beneath them. Each layer has a single, well-defined
responsibility.

```
┌────────────────────────────────────┐
│  6. layer_lav_mcp_server.py        │  MCP protocol adapter + session routing
├────────────────────────────────────┤
│  5. layer_lav_mcp.py               │  MCP protocol adaptation
├────────────────────────────────────┤
│  4. layer_lav_init.py              │  Initialization & default config
├────────────────────────────────────┤
│  3. layer_lav_cmd.py               │  Scanner drivers + Lavender commands
├────────────────────────────────────┤
│  2. layer_lav_config.py            │  Configuration
├────────────────────────────────────┤
│  1c. debug_scanner_scene.py        │  Scene scanner (scan pattern)
│      debug_scanner_process.py      │  Process handler-name scanner (prop. 4)
│  1b. layer_pygdbmi.py              │  Dispatch layer (wraps pygdbmi)
│  1a. debug_response.py             │  GDB/MI response object model
│      debug_error.py                │  Crash frame analysis
├────────────────────────────────────┤
│  0. pygdbmi (external dependency)  │  Python interface to GDB/MI
└────────────────────────────────────┘
```

---

## Layer 0: `pygdbmi` (External Dependency)

**Package:** `pygdbmi`
**Role:** The Python interface to GDB's Machine Interface (MI) protocol.

`pygdbmi.GdbController` provides:
- `write(cmd: str)` — send an MI command to GDB.
- `get_gdb_response() -> list[dict]` — read the raw JSON response list.

This is the **only** external dependency and the lowest-level interface to GDB.
All higher layers operate through it.

---

## Layer 1a: `debug_response.py`

**File:** `mcp_layered/debug_response.py`
**Depends on:** Layer 0 (`pygdbmi` — only for type reference, not import)

**Role:** Represent a GDB/MI response as comprehensive Python objects.

`pygdbmi` returns a list of dictionaries. `debug_response.py` parses this JSON
output and builds a rich object model:

```python
class DebugResponse:
    """A single GDB/MI response record."""

class ResponseType(Enum):
    TARGET = "target"       # %..., @..., &..., ~...
    RESULT = "result"       # ^done, ^error, ^running, ^connected
    NOTIFY = "notify"       # *stopped, +=breakpoint-modified, etc.
    IMMEDIATE = "immediate" # raw prompt/output

class StoppedReason(Enum):
    BREAKPOINT_HIT = "breakpoint-hit"
    SIGNAL_RECEIVED = "signal-received"
    FUNCTION_DONE = "function-finished"
    WATCHPOINT_HIT = "watchpoint-triggered"
    SINGLE_STEP = "single-step"
    EXCEPTION = "exception-received"
    EXIT = "exited"
    EXIT_Q = "exited-normally"
    EXIT_SIG = "exited-signalled"
```

The module provides a `parse(response_list: list[dict]) -> DebugResponse` or
`parse_stream(response_list: list[dict]) -> list[DebugResponse]` function that
converts raw `pygdbmi` output into typed objects.

Each `DebugResponse` exposes:
- `type` — the `ResponseType`
- `reason` — the stop reason (for notify messages)
- `payload` — the full payload dict
- `bkpt_num` — breakpoint number if applicable
- `signal` — signal name if applicable
- `frame` — current frame info (pc, func, args, etc.)
- `threads` — thread list if applicable
- Convenience methods: `is_stopped()`, `is_error()`, `is_success()`, etc.

---

## Layer 1b: `layer_pygdbmi.py`

**File:** `mcp_layered/layer_pygdbmi.py`
**Depends on:** Layer 0 (`pygdbmi`), Layer 1a (`debug_response.py`)

**Role:** Abstract the dispatching process onto `pygdbmi`. Provides a
middleware/wrapper around `GdbController`.

This layer:
1. Wraps `pygdbmi.GdbController` in a class (e.g., `GDBSession`).
2. Uses `debug_response.py` to parse all responses from `pygdbmi`.
3. Holds a list of **hooks** (callables) that are invoked on every GDB response.
4. Hooks receive the parsed `DebugResponse` objects and can:
   - Inspect (e.g., detect breakpoint hits, signals)
   - Trigger side-effects (e.g., scan processes, log events)
   - Modify the response objects before they are returned to callers
  5. Exposes a clean API:
    - `write(cmd: str) -> list[DebugResponse]` — send command, return parsed
    - `add_hook(hook_fn: Callable[[list[DebugResponse]], list[DebugResponse]])`
    - `remove_hook(hook_fn)`
  6. **Dedupes error logging** (`_log_error_response`): only the first
     `GDB_ERROR_LOG_LIMIT` (3) occurrences of each (command, error) pair are
     written to the log; suppressed repeats are counted and summarized once
     in `close()` (`_log_suppressed_errors`). A single repeatedly-failing
     command (e.g. an unsupported MI command retried by a bursty hook) cannot
     flood the session log.

This is the **single gateway** through which all GDB interaction occurs. All
higher layers interact with GDB through this layer's API.

---

## Layer 1c: `debug_scanner_scene.py`

**File:** `mcp_layered/debug_scanner_scene.py`
**Depends on:** Layer 1b (`GDBSession` write API only)

**Role:** Scene scanner, ported self-contained from the retired shells'
scan pattern (`harness/debug_scanner_scene.py` + `mcp/debug_scanner.py`
+ `mcp/gdb_frame_controller.py`). No dependency on the obsolete `mcp/`
package.

`DebugSceneScanner(gdb)` wraps `debug_get_scene_scanner(&game)` (a
`DEBUG_Scene_Scanner` returned by value, captured into
`$debug_scene_scanner`). Key APIs:

- `get_active_scene_kind()` — the active scene's `Scene_Kind`, resolved
  by pointer arithmetic (`Scene_Manager.scenes` is indexed by kind) and
  enum-name lookup *inside GDB*, so it is game-agnostic.
- `get_active_scene_ptr()` — bare hex address of the active scene (for
  pointer tracking).
- `get_scenes_table()` — every allocated scene → `{kind, is_active}`.
- `iterate_scene()` / `go_to__scene()` — cast-and-call advancement
  (parity with the retired scanner API).

All methods degrade to `None`/`{}` in release builds (the debug symbols
are `#ifndef NDEBUG` guarded).

### Scene transition tracking (Layer 4)

Two findings shaped the design:

1. **`set_active_scene_for__scene_manager` is inlined by `-O2`** at every
   call site, so a breakpoint on its (dead) out-of-line copy **never
   fires**. The transition marker is instead a **line breakpoint at the
   `run_game` "TRANSITION" line** (`game.c:702`, a constant in
   `layer_lav_init`); the scene loop's `m_enter_scene_handler` blocks for
   a scene's whole lifetime, so that line runs exactly once per scene
   entry — inlining-immune and game-agnostic.
2. **A hook that fires mid-poll must not issue GDB commands** (a nested
   call deadlocks the connection), and the `debug_get_scene_scanner(&game)`
   *call* path hangs under pygdbmi. So the hook only sets a `dirty` flag;
   the read is **deferred** to `resolve_pending_scene_transitions()`,
   which runs at a safe point and reads the `game.scene_manager` **global
   directly** (pure memory reads, no function call). The kind is the
   active scene's offset in the `scenes` array.

The resolved transition is recorded in the module-level scene state and
surfaced through MCP responses (`session_status` and the `step` driver),
giving QA agents grounding truth on scene state. `DebugSceneScanner`
remains available as a standalone scanner; the hook does not depend on it.

### Process lifecycle trace — **implemented** (`PLANS/process_trace.md`)

A **pointer-keyed** record of each process's ephemeral slot lifecycle, written into
the **session JSONL** (`GDBSession.log_record`) so it's greppable in one place. Four
correlated properties (all `{"type":"process-trace","ptr":…}`):

1. **create** — ptr + the callee stack that formed it (`add_process_to__process_table`
   hit, gated capture at the transient stop).
2. **remove** — same ptr + the callee stack that destroyed it
   (`remove_process_from__process_table` hit).
3. **error** — same ptr + the error callstack (`debug_error` hit). The ptr is read
   from the `poll_process_manager` frame (where the run-handler is invoked); its loop
   local `p_process` is `<optimized out>` at `-O2`, so the capture falls back to the
   run-handler frame's **first arg** (the handler is invoked
   `p_process->handler(p_process, p_game)` — a by-value param that survives `-O2`),
   read via `-stack-info-frame` (its payload `args`; `-stack-info-args` is not a GDB
   MI command). Verified live: a `debug_error` in
   `m_process__game_action__global_space__request__outbound_offline` during the
   world-load scene yields the full error callstack (debug_error → handler →
   poll_process_manager → manage_game__post_render → world_load → run_game → main).
4. **handler** — the run-handler's function name, resolved at a **safe, halted**
   scanner point by the `process_handler` driver / MCP tool (the handler is bound
   *after* creation, so it's only meaningful once running).

Properties 1–3 are time-sensitive → captured **at the hit** (GDB I/O only when
`_in_nested_read` is False — the transient stop window is safe), drained from a safe
point by `resolve_process_trace()`. Property 4 is stable → a scanner
(`debug_scanner_process.DebugProcessScanner`). Verified live (pointer + full callee
chain in the main JSONL; parasitic suite green, ~51 s, no deadlock). An AI agent maps
a problematic ptr → its handler + forming callee. Ptr-reuse/UAF detection is a
*future consumer*.

### Trace toggle — **implemented** (`trace`)

`trace` is a CLI/MCP command with an optional `target` sub-argument that selects
which trace group to toggle:

- **`trace`** (no arg) — toggles the lightweight **Process + Game_Action
  receive-marker** `BreakpointHook` group, **ON by default**: first `trace`
  disables the four hooks (`process.add`, `process.remove`, `process.error`,
  `game_action.receive`); second `trace` re-establishes them.
- **`trace ga`** (or `game_action` / `dispatch`) — toggles the deep **Game_Action
  DISPATCH** trace, **OFF by default** (see below).

The `initialize_ui_manager` cache-refresh hook, the scene-transition hook, the
always-on `debug_error` reporting hook, and the frame heartbeat are registered
separately and are intentionally left unchanged by `trace`. The command reports the
resulting per-hook state. If the session has not started yet, `trace` still flips
the stored flags; the flags are applied when `session_start` registers the
breakpoint hooks.

### Deep Game_Action dispatch trace — **implemented** (`trace ga`)

A deep, **default-OFF** trace of `dispatch_game_action_for__client` — the "deep
full trace of the engine", intentionally NOT fast/snappy. On **every** dispatch it
captures, at the hit (a safe, non-nested context — gated on
`GDBSession._in_nested_read`, the same pattern as the process trace):

- the **callee backtrace** (time-sensitive — gone once the transient stop is
  continued past), and
- the **`p_game_action` / `p_client` pointers** (frame args, 0 round-trips), and
- a **client-scanner snapshot** (`debug_scanner_client.DebugClientScanner`): the
  client's current uuid/flags/local-space center + its current inbound/outbound
  game-action kind/uuid + queue counts — one by-value `DEBUG_Client_Scanner` read.

The records are drained at a safe point (`resolve_game_action_dispatch_trace()`,
called from the step driver's post-work + `session_status`) into the **session
JSONL** (`{"type":"game-action-trace","event":"dispatch","game_action_ptr","client",
"stack"}`) + a `game_action_trace.log`. It is **off by default** (a backtrace + a
client-scanner read per dispatch is expensive) and is opted in via `trace ga`.

### Non-fatal debug_error reporting — **implemented** (burst-suppressed)

An always-on `BreakpointHook` on `debug_error` (NOT part of the `trace`
toggle): since `-DCRASH_ON_ERROR` was dropped from the build, `debug_error()`
prints and returns and the game keeps running — this hook is the only
observer. On each hit it captures, at the transient stop (safe, non-nested
context), the same report the old SIGABRT crash path produced (full backtrace
with the debug_error *caller* highlighted via `debug_error.adjust_frame_for_
debug_error`, plus the relevant frame's arguments), and the step driver /
`session_status` surface it; the game is continued automatically.

Two guards keep a debug_error **storm** (e.g. pool-exhaustion allocation
failures repeating every frame — thousands of hits) from dominating the run:

- **Burst suppression** (`layer_lav_init._capture_debug_error_event`): the
  signature is derived from the stop response ALONE (zero GDB I/O) — the
  `msg_fmt` error text, which by convention begins with the originating
  function name. Only the first `full_captures_per_signature` (3)
  occurrences per signature pay for the full capture; repeats cost **zero**
  GDB I/O and are surfaced by `resolve_debug_error_events()` as one
  aggregated `{"type":"debug-error","aggregated":true,…}` record per
  signature (per drain).
- **MI negative-capability cache** (`debug_error.format_arguments_for_frame`):
  `-stack-info-arguments` is not an MI command in the GDB builds we use; each
  failed probe used to cost ~2.5 s (the round-trip plus the `info args`
  console fallback's 2 s bounded read) and a `gdb_error` log record. The
  failure is now cached per session (duck-typed
  `GDBSession.mi_unsupported_commands`) and never retried. (The old code's
  error branch compared `r.type.value == "error"` — dead code, since `type`
  is the top-level category `"result"` and `"error"` is the `message` field
  — so the slow fallback ran on *every* error; the check is now
  `r.is_error()` gated on an "undefined" match.)

With both guards, a 3800-error storm collapses from ~2.6 h of GDB round-trips
(measured live) to a handful of full records plus counts.

### Planned next (plan only)

- `PLANS/process_trace.md` — remaining: the ptr-reuse/UAF consumer (§6).
- `PLANS/ui_scan_latency.md` — measured latency analysis + strategy for the UI
  scan. Headline: every GDB round-trip costs a **flat ≈ 200 ms** (read phase,
  complexity-independent), so `ui list` ≈ command-count × 200 ms. **Lever 1
  items 1–2 are implemented** (type-grouped console brace-list reads + keeping
  the `<symbol>` annotation so handler names are free): first `ui list`
  **~8.2 s → ~2.3 s** (30 → 11 round-trips). Remaining levers (direct pool read,
  session cache, fallback bound, the 200 ms floor) are documented follow-ups.

---

## Layer 2: `layer_lav_config.py`

**File:** `mcp_layered/layer_lav_config.py`
**Depends on:** None (pure configuration/data layer)

**Role:** Configuration — where core dumps go, where screenshots go, where
logs go, what executable is run. Built to be extensible.

Provides:
- A `LavConfig` dataclass/class with:
  - `executable: str`
  - `core_dump_dir: str`
  - `screenshot_dir: str`
  - `log_file: str | None`
  - `gdb_path: str`
  - `gdb_args: list[str]`
  - `env: dict[str, str]`
  - Plus extensible fields for future scanners.
- `load_config(path: str | None) -> LavConfig` — load from a config file, with
  defaults for everything if the file is absent.
- `default_config() -> LavConfig` — returns a sensible default config.
- Exposes **required aliases** to config (e.g., `lav_config.executable`
  is accessible, `lav_config.dump_location` maps to `core_dump_dir`).

This layer does **not** import any other layer. It is pure configuration.

---

## Layer 3: `layer_lav_cmd.py`

**File:** `mcp_layered/layer_lav_cmd.py`
**Depends on:** Layer 1b (`layer_pygdbmi`), Layer 2 (`layer_lav_config`)

**Role:** Holds all Lavender Scanner drivers (e.g., `DebugUIScanner`,
`ProcessScanner`, etc.) and individual Lavender commands (e.g., `step`,
`start`, `ui_list`, `process_watch`).

This layer:
1. Imports scanner drivers and command implementations.
2. Exposes the config layer to these drivers.
3. Exposes **a required `alias` argument** to route to a scanner driver, then
   `**kwargs` to provide arguments to the scanner driver.
4. Scanner drivers can **reject** invocation on invalid kwargs — this raises an
   exception which propagates to Layer 5.
5. Example API:
   ```python
   def invoke(alias: str, gdb: GDBSession, config: LavConfig, **kwargs) -> str:
       """Route to scanner driver by alias."""
       driver = SCANNER_REGISTRY[alias]
       return driver.invoke(gdb, config, **kwargs)
   ```

This layer is the **command registry** — all actual work (stepping, scanning,
UI interaction, process tracking) lives here, implemented as scanner drivers.

### Selector resolution — `[...]` delimiters (**implemented**)

A command argument may embed a `[...]` selector to name a scanner-table entry by a
stable property instead of a raw pointer (e.g. `ui invoke clicked [type=*Button,n=1]`).
`invoke()` resolves these **before dispatch** through a **single seam**,
`resolve_value(gdb, value)` — a future full path-query DSL
(`a.b.c.[idx=2].e.f.[type=*X]`) extends that one function (parse dotted paths, walk
the table); the dispatch call sites never change.

Selectors are **space-free** (so the CLI's whitespace tokenizer keeps each as one
token) and currently support:
- `[type=*Button,n=2]` — the *n*-th (1-based) element whose `kind` matches the
  fnmatch pattern; `n=1` is "first".
- `[idx=2]` — the 0-based positional element of the (filtered) set.

Resolution reads the **per-session UI cache** (`GDBSession._ui_cache`):
- **populated** by the `ui_list` driver (the structured `ui_managers → ui_elements`
  table, flattened in ptr-sorted order so "first/second" are deterministic);
- **cleared** by the `initialize_ui_manager` breakpoint hook (a manager was
  (re)allocated → contents may be stale). That clear is a pure attribute write (no
  GDB I/O), so it is safe even in a nested mid-poll hook context.

Because UI element pointers are **stable pool-slot addresses** (they do not dangle
across a UI rebuild; only slot *contents* change), a cached entry stays address-valid,
and the `ui list` refresh + init-hook clear keep it content-fresh. An unresolved
selector (empty/stale cache) raises a clear `CommandError` rather than passing a
literal `[...]` to the driver.

The `verify_cli.py` REPL additionally splits a line on **`;`** (`split_commands`) so an
entire reproduction runs in one line, e.g.
`start; step; ui list; ui invoke clicked [type=*Button,n=1]; step 2; …`.
The CLI also accepts `--script FILE`, which reads FILE as one `;`-separated command
string, runs it with the same dispatch path, then yields control to the interactive
REPL (an explicit `quit`/`exit` in the script exits cleanly; an unreadable script
exits nonzero).

---

## Layer 4: `layer_lav_init.py`

**File:** `mcp_layered/layer_lav_init.py`
**Depends on:** All layers below (1b, 2, 3)

**Role:** Initialization and wiring.

1. Accepts a `config_path: str | None` argument.
2. Forwards the path down to the config layer (Layer 2).
3. If no path is provided, uses `default_config()`.
4. Creates the `GDBSession` (Layer 1b) using config settings.
5. Returns a fully wired-up `LavSession` or similar facade that combines:
   - The `GDBSession` (Layer 1b)
   - The `LavConfig` (Layer 2)
   - The command router (Layer 3)

This layer is the **composition root** — it assembles all lower layers into a
working session.

---

## Layer 5: `layer_lav_mcp.py`

**File:** `mcp_layered/layer_lav_mcp.py`
**Depends on:** Layer 4 (`layer_lav_init`)

**Role:** Adapt the MCP protocol onto Layer 4.

This layer implements the MCP tool interface (tool discovery, tool calling) by
translating MCP tool names to Lavender scanner driver invocations through
`LavSession.invoke(alias, **kwargs)`.

It defines:
- The full MCP tool listing (`TOOLS` schema)
- A `dispatch_tool(name: str, arguments: dict) -> str` function
- Input validation and argument mapping

This layer **does not** know about GDB, pygdbmi, configs, or scanner drivers
directly — it only talks to `LavSession`.

---

## Layer 6: `layer_lav_mcp_server.py`

**File:** `mcp_layered/layer_lav_mcp_server.py`
**Depends on:** Layer 5 (`layer_lav_mcp`)

**Role:** Session tracking and session routing.

This is a **middleware** layer responsible for:
- Per-connection session management
- Session ID routing
- Forwarding config initialization to Layer 4 on session creation
- Managing the lifecycle of `LavSession` instances

It wraps the Layer 5 adapter in a session-aware envelope.

---

## Inspiration from `mcp/`

The existing `mcp/` code provides the semantics we are replicating:

| `mcp/` Concept | `mcp_layered/` Equivalent |
|---|---|
| `LavMcpSession` (single class) | Split across Layers 4+5 (`LavSession` + MCP adapter) |
| GDB interaction methods | Layer 1b (`GDBSession`) |
| Scanner drivers (`DebugUIScanner`, etc.) | Layer 3 (`layer_lav_cmd.py`) |
| Config fields in session | Layer 2 (`layer_lav_config.py`) |
| Response parsing (ad-hoc) | Layer 1a (`debug_response.py`) |
| Scene scanner (`harness/debug_scanner_scene.py`) | Layer 1c (`debug_scanner_scene.py`) |
| Session factory/routing | Layer 6 (`layer_lav_mcp_server.py`) |

The key improvement is **isolation of concerns**: a change to GDB interaction
affects only Layer 1b; a change to a scanner driver affects only Layer 3; a
change to the MCP protocol affects only Layers 5–6.

---

## Future Extensions

- Layer 1b hooks enable **breakpoints-driven automation**: e.g., when GDB
  stops at `remove_process_from__process_table`, a hook triggers
  `DebugUIScanner.scan()` automatically.
- Layer 1b hooks enable **rich logging**: every breakpoint hit, signal, and
  error is logged with full context.
- Layer 2's extensibility allows new scanner drivers to add configuration
  fields without touching existing code.
