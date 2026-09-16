# Plan — Process Lifecycle Trace (4 correlated properties, keyed by pointer)

**Status:** **IMPLEMENTED + VERIFIED.** The full 4-property trace is wired up and
verified end-to-end on the real binary (parasitic suite green, ~51 s, no deadlock).
Two real bugs found and fixed along the way:
1. The pointer was being read but written to a *separate* file, invisible in the main
   log — now all process-trace records are written into the **session JSONL**
   (`GDBSession.log_record`), greppable in one place and correlated by the process
   pointer.
2. The error event's ptr was read with **`-stack-info-args`, which is not a GDB MI
   command** ("Undefined MI command"), so it always errored and the ptr stayed `None`.
   Fixed to use **`-stack-info-frame`** (its payload `args`), with a fallback to the
   run-handler frame's first arg when `poll_process_manager`'s `p_process` local is
   `<optimized out>` at `-O2`.

The error path is reproduced by the CLI **`;`/`[]`** features (see
`LAYERS.md` §Layer 3): a one-line sequence
`start; step; ui list; ui invoke clicked [type=*Button,n=1]; step 2; … ; step 102`
drives the game into the world-load scene where the outbound-offline handler raises
`debug_error`. Verified live: the `event=error` record carries the full error callstack
(debug_error → handler → poll_process_manager → … → world_load → main).

**Goal.** While the game runs under GDB, record a process's **ephemeral slot
lifecycle** as a set of correlated log records, **all keyed by the process pointer**
(`Process *p_process`). Correlating on the pointer lets an AI agent distinguish one
slot's re-use from another and answer: *what process is problematic, what handler
caused the error, and which callee formed it.* The four properties:

| # | Property | Where captured | Record |
|---|----------|----------------|--------|
| 1 | **create** — ptr + the callee stack that **formed** the process | `add_process_to__process_table` hit (transient stop) | `event=add` |
| 2 | **remove** — same ptr + the callee stack that **destructured** it | `remove_process_from__process_table` hit (transient stop) | `event=remove` |
| 3 | **error** — same ptr in the `poll_process_manager` frame + the **error** callstack | `debug_error` hit (handler raised it, invoked *inside* `poll_process_manager`) | `event=error` |
| 4 | **handler** — the run-handler's **function name**, resolved at a **safe scanner** point | `process_handler` scanner driver (on demand, game halted) | `event=handler` |

Properties 1–3 are **time-sensitive** (the callee/error stack is gone once a
transient stop is continued past) → captured **at the hit** by a gated capture.
Property 4 is a **stable** value (the handler is bound *after* creation, so it's only
meaningful once the process is running) → resolved **later**, at a safe, halted
scanner point (never a transient stop), which is both deadlock-safe and correct.

**Encapsulation + toggle.** Each hit-driven property is a `BreakpointHook` object
whose `enable()`/`disable()` toggles the underlying GDB breakpoint. **On by
default**; the `trace` command calls `enable`/`disable` for the Process and
Game_Action hook groups. Property 4 is a scanner driver (`process_handler`)
exposed as an MCP tool.

> **Why this replaced the old "ptr-reuse detection" objective.** The earlier
> `process_ptr_reuse.md` framed this as hunting use-after-free / aliasing in the
> fixed slot pools. That is a *derived* analysis. The thing actually needed right
> now is the **trace** — a faithful, pointer-keyed record of a process's lifecycle
> (who formed it, what it errored with, who destroyed it). Ptr-reuse detection
> becomes a *future consumer* of this trace (§6).

---

## 1. The process model (grounding, unchanged)

Both subsystems are **fixed-size slot arrays** (stable slot addresses; re-allocation
overwrites slot *contents*, not location):

| System | Container | Slot array | Size |
|--------|-----------|-----------|------|
| Process | `Process_Manager` (embedded in `Game`) | `processes[512]` | `PROCESS_MAX_QUANTITY_OF` |
| Game_Action (in/out) | `Client.game_action_manager__{in,out}bound` | `game_actions[512]` | `MAX_QUANTITY_OF__GAME_ACTIONS` |

Source of truth (confirmed in-tree):
- `core/include/defines.h`: `Process_t` @1274 (`p_process_data` @1282, status @1300,
  kind @1301), `Process_Manager_t` @1333, `Game_Action_t` @2342,
  `Game_Action_Manager_t` @2389, `Client_t` @2421, `Game_t` @2547
  (`process_manager` @2554, `pM_clients` @2581).
- `core/include/defines_weak.h`: `enum Process_Status_Kind` @270
  (`None,Stopped,Idle,Busy,Stopping,Enqueued,Complete,Fail,Unknown`),
  `enum Process_Kind` @283.
- `core/include/process/process_table.h`: the two traced functions (signatures above).
- `core/include/process/process.h`: `initialize_process` @9, `complete_process` @50 /
  `fail_process` @67 ("release your p_process_data … lost following this call").

The **handler** field to log: `Process.m_process_run__handler` (a function pointer).
It is the single best "what is this process" identifier. Resolving it to a name
reuses the existing `resolve_function_name` symbol-annotation helper (the same one
`ui list` now uses).

---

## 2. Encapsulated object (implemented) — `BreakpointHook`

In `mcp_layered/layer_pygdbmi.py` (Layer 1b), a reusable component that owns one
GDB breakpoint **and** the hook that reacts to it, and can toggle the breakpoint:

- `BreakpointHook(gdb, name, target, handler)` — `target` is a function name (or
  `file:line`). `handler(responses)` is the lightweight reaction fired on hit.
- `enable()` — set the breakpoint (`-break-insert`), remember its number, register
  the hook (fired only for this breakpoint). Idempotent.
- `disable()` — delete the breakpoint (`-break-delete`, the new
  `GDBSession.delete_breakpoint`) and unregister the hook. Idempotent.
- `enabled` property; `bp_number` property.

`enable`/`disable` are the primitive used by the implemented `trace` command (a
single toggle for the Game_Action + Process hook groups; per-event `on|off`
arguments remain a possible extension). A **disabled** hook neither stops the game
nor fires — that is the whole point of making verbose tracking toggleable.

> Contract carried over from the Scene-Tracking work: **`handler` must not issue GDB
> commands** (a nested call during polling deadlocks the connection — §5). The
> handler records state; any GDB read is done elsewhere.

---

## 3. The logged fields, and where each can be read

| Field | How to obtain | Needs GDB I/O? | Timing-safe? |
|-------|---------------|----------------|--------------|
| pointer | stop-response `frame.args` (`p_process = 0x…`), **or** `-stack-info-frame` (payload `args`) | maybe / yes | yes (stable) |
| pointer (error) | select the `poll_process_manager` frame, read its local `p_process`; **if `<optimized out>` at `-O2`, fall back to the run-handler frame's first arg via `-stack-info-frame`** | **yes** | yes (stable) |
| handler name | `((Process *)<ptr>)->m_process_run__handler` → symbol | **yes** | yes (stable) — but **bound after create** |
| callee / error stack | `-stack-list-frames` | **yes** | **NO — time-sensitive, see §5** |

Two key facts shape the design:

- The **callee/error stack is time-sensitive**: it must be captured **at the moment
  of the hit** (the chain that formed / errored / destroyed the process) and is
  meaningless once the game has run on. → properties 1–3, captured at the hit.
- The **handler is bound *after* creation** — `add_process_to__process_table`
  inserts a process whose `m_process_run__handler` is still **NULL**; the creating
  callee sets it only *after* the add returns (confirmed: the file-system-context
  process logs `handler=0x0` at create). So the handler name is only meaningful once
  the process is **running**, and is a *stable* value after that. → property 4,
  resolved later at a safe, halted scanner point (not the create hit).

---

## 4. Why the stack trace is the hard part (the fork)

A process create/remove happens **inside the game loop**, so the breakpoint stop is
**transient**: `step_frame_detailed` (the `step` driver) detects the stop as an
*unexpected* breakpoint and **immediately continues past it**
(`mcp/gdb_nav_utils.py:519` `continue`) to reach `manage_game__post_render`. By the
time the driver's post-work "safe point" runs, the game is at `post_render` — the
callee chain is gone.

So the backtrace must be read **in the stop window** (game stopped at the process
function), and the only clean stop window is the one `_poll_for_stops` creates
(it reads the `*stopped`, runs hooks via `process_hooks_on_raw` **outside**
`get_gdb_response`, then continues). Reading GDB there is the proven-safe "top-level
safe point" (the Scene-Tracking deadlock was the *nested* `get_gdb_response` case,
which this path avoids). The cost: it requires the nav logic to know which
unexpected stops are *process-trace* stops and to capture the stack there.

The options considered (resolved in §5 — the chosen design captures the stack in the
stop window via the object's gated capture, *without* touching the nav logic):
- **A.** Capture the full stack in the stop window. ✅ **Chosen** — but implemented
  as the `BreakpointHook`'s gated capture (no `gdb_nav_utils.py` change needed).
- **B.** Log pointer + handler only (defer the stack). Superseded — A is safe.
- **C.** Deferred backtrace (read at `post_render`). Not viable — wrong chain.

---

## 5. Decision (made) + how it's implemented

**Chosen approach (the user's "last stack trace" idea).** Rather than special-casing
process stops in the nav logic, the `BreakpointHook` object itself owns a **gated
capture**: on each hit it runs a `capture(gdb, responses)` callable that *may* issue
GDB commands (read the pointer, the handler, `-stack-list-frames`) — but **only when
`GDBSession._in_nested_read` is False** (a safe, stopped context). The capture's
result is appended to `captured_events`; a safe section (the step driver's post-work
/ `session_status`) calls `consume_events()` and writes the stored dicts to the log.
So the time-sensitive stack is captured *at the hit* (the transient stop window,
which is safe) yet consumed from a guaranteed-safe section with **no** GDB command.

The `_in_nested_read` flag is set True only on the three *nested* hook paths
(`_hooked_get_gdb_response`, `_activity_timeout_get_gdb_response`, `_hooked_write`)
and is False on the `_poll_for_stops` / `GDBSession.write` paths (both read the
response synchronously, so the game is stopped and the stream is clean there). A
capture failure is swallowed (never breaks the driver).

**How each property is implemented:**

- **1 & 2 (create/remove).** Two `BreakpointHook`s on the add/remove table functions;
  the shared `_capture_process_event` reads the pointer (stop frame args, fallback
  `-stack-info-frame`) + `-stack-list-frames` at the hit. The handler is *not* the
  point here (it's NULL at create) — the callee stack is.
- **3 (error).** A `BreakpointHook` on `debug_error`. `_capture_error_event` reads
  the full error callstack, finds the `poll_process_manager` frame (the run-handler
  is invoked *inside* it), and recovers the ptr: first the frame's local `p_process`,
  but that loop-local is `<optimized out>` at `-O2`, so it **falls back to the
  run-handler frame's first arg** (the handler is invoked
  `p_process->handler(p_process, p_game)` — a by-value param that survives `-O2`),
  read via `-stack-info-frame` (`-stack-info-args` is not a GDB MI command). If
  `poll_process_manager` is absent (a non-process error) the capture returns `None`
  and is skipped (no log noise).
- **4 (handler).** A self-contained `DebugProcessScanner` (Layer 1c,
  `debug_scanner_process.py`) + a `process_handler` scanner driver (exposed as an MCP
  tool). Given a ptr it reads `((Process*)<ptr>)->m_process_run__handler` and
  resolves the `<symbol>` — at a **safe, halted** point (a scanner context, never a
  transient stop). The AI invokes it with a ptr it saw in the trace to learn which
  handler a process uses.

**The main-log fix (the bug this iteration closed).** The GDB-response JSONL record
(`layer_pygdbmi._log_responses_to_file`) carries *no payloads* — so a pointer read
from the stop frame's args never appeared in the main log; it only landed in a
separate `process_trace.log`, invisible to anyone grepping the session log. Fix:
`GDBSession.log_record(entry)` appends a structured record to that **same** JSONL.
Every process-trace event is now written as
`{"type":"process-trace","event":…,"ptr":…,"handler":…,"stack":[…]}` into the
session log (keyed by `ptr`), with the human-readable `process_trace.log` kept as a
secondary convenience.

**Verified live** on `AncientsGame`: the session JSONL now contains
`{"type":"process-trace","event":"add","ptr":"0x5555556e3090 <game+832>",
"handler":"0x0","stack":["#0 add_process_to__process_table …", …]}` — pointer
captured, full correct callee chain, in the main log. Parasitic suite green (~51 s,
no deadlock).

---

## 6. Future (out of scope for now)

- **Finer-grained trace controls** — optional `trace on|off` arguments and
  per-event toggles. The basic `trace` command is implemented and toggles the
  Game_Action + Process `BreakpointHook` groups as a unit.
- **Ptr-reuse / UAF / aliasing detection** — the old `process_ptr_reuse.md`
  objective, now a *consumer* of this trace: correlate create/remove events with
  slot identity over time to flag a live process still referencing a re-used slot.

---

## 7. Acceptance criteria (met)
- ✅ `enable()` sets a real GDB breakpoint; `disable()` deletes it. Idempotent both
  ways (unit-tested in `tests/layer1/tests.py`).
- ✅ **Property 1/2:** a create/remove during `step` produces a `process-trace`
  record in the **session JSONL** with the pointer **and the full callee stack**
  (verified live, §5). The pointer is greppable in the main log (the bug is fixed).
- ✅ **Property 3:** a `debug_error` raised by a run-handler yields an `event=error`
  record with the process ptr (from the `poll_process_manager` frame, falling back to
  the run-handler's first arg via `-stack-info-frame` when that local is `<optimized
  out>` at `-O2`) + the error callstack; non-process errors are skipped.
- ✅ **Property 4:** `process_handler <ptr>` (MCP tool) resolves the run-handler
  name at a safe, halted point and logs an `event=handler` record keyed by ptr.
- ✅ All four records share `{"type":"process-trace","ptr":…}` so a slot's lifecycle
  (create → error → remove) correlates on one key; the AI can map a problematic ptr
  to its handler and forming callee.
- ✅ Nothing is written to the MCP tool *response*; all trace output goes to the log
  (the session JSONL, plus the human-readable `process_trace.log`).
- ✅ Full unit suite green (221 tests, incl. `tests/test_process_trace.py` 19 and
  `tests/layer3/tests.py` 39 with the selector/`;`-split tests); **no GDB command is
  issued from inside a polling hook** (captures gated on `_in_nested_read`; property 4
  runs only at a halted scanner point).
