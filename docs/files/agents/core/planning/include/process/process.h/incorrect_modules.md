# Planning: process.h — Incorrect Modules

**Review source:** `agents/core/review/include/process/process.h/incorrect_modules.md`

**Source files reviewed (read-only):**
- `core/include/process/process.h` — all three flagged functions are `static inline` here
- `core/source/process/process.c` — `initialize_process()` unconditionally sets `the_kind_of__process_this__process_is = Process_Kind__None` (lines 24–25) and status to `Process_Status_Kind__None`
- `core/source/process/process_manager.c` — `poll_process_manager()` dequeues via the single `p_enqueued_process` slot and calls `set_process_as__dequeued()` (lines 166–175)
- `core/include/defines.h` — `Process` struct; `p_enqueued_process` and `p_sub_process` share an anonymous `union` (lines 1278–1281)
- `core/include/defines_weak.h` — `Process_Kind` enum (`Process_Kind__None`, `Process_Kind__Serialized`, …)
- `core/source/process/tcp_game_action_process.c` — `set_game_action_process_as__tcp_payload_receiver()` manually calls `set_the_kind_of__process(p_process, Process_Kind__Serialized)` (lines 58–60); does **not** use the flagged helper
- `core/source/game_action/core/tcp/game_action__tcp_delivery.c` — `m_process__game_action__tcp_delivery__inbound` switches on `get_the_kind_of__process(p_process)` and accepts only `Process_Kind__Serialized` (lines 30–37)
- **Test suite:** `tests/core/source/process/test_suite_process_process.c` (MUnit) — contains tests for all three flagged functions, including a **currently-failing** test that asserts the correct behavior for `initialize_process_as__serialized_process`

---

## 1. Problem Identification

Three `static inline` functions in `core/include/process/process.h` were flagged **Incorrect**.

### 1.1 `set_process_as__enqueued` (process.h, lines 193–198)
**Boundary Condition** / **Invariant** violation. The body dereferences `p_process` with no null guard. Every sibling status-setter in the file (`complete_process`, `fail_process`, `stop_process`, `set_process_as__stopped`, and even `set_process_as__dequeued`) wraps its body in `#ifndef NDEBUG` with a `debug_abort` on null. This function omits the guard, so a null `p_process` is undefined behavior (null dereference) in debug builds where the siblings would abort safely. The omission is an inconsistency, not a design choice.

### 1.2 `initialize_process_as__serialized_process` (process.h, lines 27–43)
**Translation Gap** / **State Desync**. The name and post-conditions promise a serialized process (`Process_Kind__Serialized`), but the wrapper only delegates to `initialize_process()`, which hard-codes `the_kind_of__process_this__process_is = Process_Kind__None`. The wrapper never overrides the kind, so any consumer reading `get_the_kind_of__process()` sees `None` for a process that is semantically serialized. This is a **Stub-real divergence** from the established pattern in `tcp_game_action_process.c`, which explicitly calls `set_the_kind_of__process(p_process, Process_Kind__Serialized)` after wiring the serialization request.

### 1.3 `enqueue_process` (process.h, lines 207–222)
Three distinct defects:
- **Boundary Condition** / **Invariant**: neither `p_process_to__enqueue` nor `p_process_to__enqueue_behind` is null-checked in any build. A null host pointer makes the write to `->p_enqueued_process` a null dereference. All sibling functions carry a `#ifndef NDEBUG` null guard; this one does not.
- **Translation Gap** / **Non-Injective Translation**: the name implies queue semantics, but `p_enqueued_process` is a single pointer (in a union with `p_sub_process`, defines.h lines 1278–1281), not a list. A second enqueue on the same host silently overwrites the first, orphaning it (never dequeued, never run).
- **Aliasing Bug** / **Mode Confusion**: `p_enqueued_process` and `p_sub_process` alias the same storage. Enqueuing behind a host that is simultaneously used as a sub-process clobbers `p_sub_process`.
- The only validation present (self-enqueue check) is `#ifndef NDEBUG`-guarded, so release builds have **zero** validation.

---

## 2. Impact Assessment

### 2.1 `set_process_as__enqueued`
- **Direct caller:** `enqueue_process` (process.h, lines 220–221). No other production callers found.
- **Dequeue path is independent:** `poll_process_manager` (process_manager.c, lines 167–170) reads `p_enqueued_process` and calls `set_process_as__dequeued` — it does **not** call `set_process_as__enqueued`, so the fix does not touch the dequeue logic.
- **De facto contract:** every observed `enqueue_process` caller passes non-null pointers, so the missing guard has not yet triggered UB in practice. Correcting it is **behavior-preserving** for all valid callers; it only adds a debug-only abort on an invalid `Precondition`.

### 2.2 `initialize_process_as__serialized_process`
- **Root cause:** `initialize_process()` (process.c, lines 24–25) sets kind to `Process_Kind__None`; the wrapper does not correct it.
- **No production callers found.** The TCP receiver path — the natural consumer of a serialized process — is built by `set_game_action_process_as__tcp_payload_receiver` (tcp_game_action_process.c), which sets `Process_Kind__Serialized` **manually** and does not call this helper. The downstream check in `game_action__tcp_delivery.c` (lines 30–37) therefore never sees a mis-kinded process in the current code.
- **Consequence:** the defect is **latent**, not an active broken path. Its concrete, observable impact today is a **failing test** (see §4): `initialize_process_as__serialized_process__sets_kind_to_serialized` asserts `get_the_kind_of__process() == Process_Kind__Serialized` and currently fails because the implementation yields `None`.
- **Correcting** the wrapper to set `Process_Kind__Serialized` invalidates the (incorrect) assumption that this helper produces a `Process_Kind__None` process. Since no caller depends on `None`, the change is **behavior-preserving** for existing code and turns the failing test green.

### 2.3 `enqueue_process`
- **Callers (verified):**
  - `core/source/world/global_space.c` — 8 references (lines 233, 328, 429, 486, 509, 581, 638, 658); line 328 sits inside a `/* … */` block comment, so **7 are live**. Each enqueues exactly one sub-process (chunk/entity/container ser/deser) behind a host global-space process.
  - `core/source/game_action/core/world/game_action__world__load_client.c` — 3 sites (lines 77, 125, 195).
  - `core/source/game_action/core/tcp/game_action__tcp_connect.c` — 1 site (line 93).
  - `core/source/game_action/core/global_space/game_action__global_space__resolve.c` — 1 site (line 130).
- **Dequeue consumer:** `poll_process_manager` (process_manager.c, lines 166–175) reads the single `p_enqueued_process` and dequeues exactly one process per finished host. This is the de facto contract: **one enqueued process per host**.
- **No caller relies on multi-enqueue or on the overwrite behavior** — every live call enqueues one sub-process behind a fresh host. The overwrite/orphan path is a latent hazard, not an exercised feature.
- **Aliasing:** no current caller sets `p_sub_process` on a process that also serves as an enqueue host, but the union makes this a fragile, **Coupled** assumption.

---

## 3. Resolution Assessment

All three fixes are in `core/include/process/process.h`. No signature changes are required; no production caller needs editing for the low-risk fixes.

### 3.1 `set_process_as__enqueued`
- Add the `#ifndef NDEBUG` null guard (`debug_abort` + early return) matching its siblings.
- Callers: none to update. Tests: existing usage stays valid; add a null-guard test (§4).
- Terminology: **Boundary Condition**, **Invariant**, **Precondition**, **Postcondition**, **Conservative**.

### 3.2 `initialize_process_as__serialized_process`
- After the `initialize_process()` call, add `set_the_kind_of__process(p_process, Process_Kind__Serialized)` — mirroring `tcp_game_action_process.c` (lines 58–60). This closes the **Translation Gap** / **State Desync**.
- Callers: none to update (no production callers). The existing failing test will pass.
- Terminology: **Translation Gap**, **State Desync**, **Stub-real divergence**.

### 3.3 `enqueue_process`
Primary (low-risk, behavior-preserving) fix:
1. Add `#ifndef NDEBUG` null guards for **both** arguments, consistent with siblings.
2. Keep the self-enqueue check; document that it is debug-only, or promote it to a release-safe no-op guard if a `Conservative` runtime check is desired.
3. **Preserve the single-slot design** (it matches `poll_process_manager` and every live caller). Document the single-enqueued-process-per-host limit and the `p_enqueued_process`/`p_sub_process` union aliasing as an explicit **Invariant** / **Precondition** in the header comment. Add a debug assertion that the host's `p_enqueued_process` is currently null (not already occupied) to catch the orphan case early.

Optional follow-up (higher risk, no current caller benefit — do **not** bundle with Phase 1):
4. If true multi-slot queue semantics are ever required, replace the single pointer with a linked list and update `poll_process_manager` to iterate it. This is a **Non-Injective Translation** fix and a **Coupled** change; defer until a caller actually needs it.
- Terminology: **Translation Gap**, **Non-Injective Translation**, **Aliasing Bug**, **Mode Confusion**, **Boundary Condition**, **Invariant**, **Coupled**.

---

## 4. Test Verification Checklist

A MUnit suite already exists at `tests/core/source/process/test_suite_process_process.c`. (The prior draft of this plan incorrectly stated no tests exist — corrected.)

**Existing tests and their status after the fix:**
- `initialize_process_as__serialized_process__sets_kind_to_serialized` — asserts kind == `Process_Kind__Serialized`. **Currently FAILS** (implementation yields `None`). The §3.2 fix makes it **pass**. This is the key regression signal for defect 1.2.
- `initialize_process_as__serialized_process__sets_critical_flag` — asserts the critical flag; currently passes and stays passing.
- `enqueue_process__sets_enqueued_status`, `enqueue_process__links_enqueued_process` — use valid, distinct pointers; assert the single-slot link and enqueued status. **Currently pass** and remain valid after adding null guards (behavior-preserving).
- `set_process_as__dequeued__sets_status_to_idle` — calls `set_process_as__enqueued` on a valid pointer; stays passing after the null-guard fix.

**Existing assertions invalidated by the fixes:** none. No test asserts on the broken behavior (missing null guard, or kind == `None`).

**New tests to add** (terminology from `agents/terminologies/testing.md`):
- `set_process_as__enqueued`: **Fuzzing** of null `p_process` in a debug build to confirm the guard aborts; **Property Based Testing** that a valid process reads back as `Process_Status_Kind__Enqueued`.
- `enqueue_process`: **Fuzzing** of null arguments and self-enqueue (same pointer twice) to confirm guards fire; **Round Trip Check** — enqueue behind a host, complete the host through the poll path, assert the child is dequeued to `Process_Status_Kind__Idle`; add a case asserting the debug assertion fires when enqueuing a second process behind an already-occupied host (the orphan case).
- `initialize_process_as__serialized_process`: **Equivalence Check** against the `set_game_action_process_as__tcp_payload_receiver` pattern (both must yield `Process_Kind__Serialized`); **Round Trip Check** that a process built by the helper is accepted by the `game_action__tcp_delivery.c` kind switch.

**Test blast radius:** Low–Medium. The suite already covers the happy paths; only the one failing test needs to flip green, plus a handful of new guard/edge tests. No existing assertion breaks, so no phased test migration is required.

*(Adjacent, out-of-scope observation: `initialize_process__sets_status_to_idle` asserts status == `Idle`, but `process.c` sets `Process_Status_Kind__None`. That test targets `initialize_process`, which is not part of this review; flag separately rather than folding into this plan.)*

---

## 5. Blast Radius Summary

| Metric | Assessment |
|---|---|
| **Files needing changes** | 1 for the low-risk fixes: `core/include/process/process.h` (all three functions are `static inline` here). A separate edit to `tests/core/source/process/test_suite_process_process.c` adds new guard/edge tests. The optional `enqueue_process` linked-list redesign would additionally require `core/source/process/process_manager.c` (`poll_process_manager`, lines 166–175) — deferred, not part of the primary fix. |
| **Behavior-preserving for current callers** | Yes. Null guards add a debug-only abort on invalid input only; the `Process_Kind__Serialized` fix has no production callers to disturb; the single-slot `enqueue_process` design is retained, so all 12 live call sites are unaffected. |
| **Phased approach needed** | Recommended. **Phase 1:** null guards on `set_process_as__enqueued` and `enqueue_process` + document the single-slot/union **Invariant** (lowest risk). **Phase 2:** set `Process_Kind__Serialized` in `initialize_process_as__serialized_process` (turns the failing test green). **Phase 3 (optional, deferred):** linked-list enqueue + `poll_process_manager` update only if a caller needs multi-slot queue semantics. |
| **De facto contracts invalidated** | The `Process_Kind__Serialized` fix invalidates the (incorrect) assumption that the helper yields `Process_Kind__None`; no caller relies on it. Retaining the single-slot `enqueue_process` preserves the one-enqueued-per-host contract in `poll_process_manager`. No de facto contract is broken by the primary fixes. |
