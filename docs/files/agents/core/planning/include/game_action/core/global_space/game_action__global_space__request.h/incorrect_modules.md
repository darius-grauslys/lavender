# Planning: game_action__global_space__request — Incorrect Modules

**Review source:** `agents/core/review/include/game_action/core/global_space/game_action__global_space__request.h/incorrect_modules.md`

**Source files reviewed (read-only):**
- `core/include/game_action/core/global_space/game_action__global_space__request.h`
- `core/include/types/core/game_action/global_space/ga_type__global_space__request.h`
- `core/source/game_action/core/global_space/game_action__global_space__request__multiplayer.c`
- `core/source/game_action/core/global_space/game_action__global_space__request__offline.c`
- `core/source/world/global_space_manager.c`
- `core/include/world/global_space.h`
- `core/include/world/global_space_manager.h`
- `core/include/timer.h`
- `tests/core/source/game_action/core/global_space/test_suite_game_action_core_global_space_game_action__global_space__request__multiplayer.c`
- `tests/core/source/game_action/core/global_space/test_suite_game_action_core_global_space_game_action__global_space__request__offline.c`

---

## 1. Problem Identification

Four functions/modules were flagged as **Incorrect**. Two of them share a single root-cause defect in a shared accessor.

### 1.1 Root-cause accessor: `get_p_timeout_timer_u32_from__ga_global_space__request`
**File:** `core/include/types/core/game_action/global_space/ga_type__global_space__request.h` (lines 75–80)

**Defect — `Aliasing Bug` / `State Desync` (translation-and-semantics):** The pointer-returning accessor returns `&…->gsv_3i32` instead of `&…->timeout__timer_u32`. The `GA_Global_Space__Request` payload lays out `gsv_3i32` first, then `chunk_payload_bitmap`, then `timeout__timer_u32`; the accessor therefore hands callers a `Timer__u32*` that aliases the `Global_Space_Vector__3i32` field. `Timer__u32` has `remaining__u32` / `start__u32`, which alias `x__i32` / `y__i32` of the vector. This is undefined behavior under C strict aliasing and desyncs timer state from the field that actually holds the timeout. The by-value getter `get_timeout_timer_u32_from__ga_global_space__request` is correct; only the pointer variant is broken.

### 1.2 `m_process__game_action__global_space__request__outbound_client`
**File:** `core/source/game_action/core/global_space/game_action__global_space__request__multiplayer.c` (lines 181–245)

**Defect — `Aliasing Bug` (downstream of 1.1):** The timeout poll calls `poll_timer_by__this_duration_u32(get_p_timeout_timer_u32_from__ga_global_space__request(p_game_action), …)`, which reads/writes timer state from the `gsv_3i32` field rather than `timeout__timer_u32`. The timeout mechanism is therefore non-functional: it is driven by the global-space vector's x/y coordinates instead of an initialized timer. Correcting accessor 1.1 invalidates the (broken) assumption that the timeout is derived from vector data.

### 1.3 `m_process__game_action__global_space__request__outbound_client__init`
**File:** `core/source/game_action/core/global_space/game_action__global_space__request__multiplayer.c` (lines 247–326)

**Defect — `Conservation Law` violation / resource leak (invariants-and-correctness):** On the collision-node allocation failure path, the already-allocated `Chunk` (lines 273–277) is not released. The chunk is only assigned to `p_global_space->p_chunk` at line 303 — *after* the collision-node check — so `release_global_space` (which gates release on `get_p_chunk_from__global_space(p_global_space)` being non-null) never sees it and the chunk leaks from the `Chunk_Pool`. The cleanup path is `Coupled` (design-principles) to `p_global_space->p_chunk` being set, but the assignment ordering breaks that coupling for this failure mode.

### 1.4 `m_process__game_action__global_space__request__outbound_server`
**File:** `core/source/game_action/core/global_space/game_action__global_space__request__multiplayer.c` (lines 29–76)

**Defect — `Postcondition` / `Invariant` violation (invariants-and-correctness):** When the target `Global_Space` is deconstructing (lines 57–62), the function returns early *without* calling `fail_process` or `complete_process`. The process is left in a non-terminal (`Busy`/`Idle`) status and is re-polled by the scheduler; the deconstructing condition is re-encountered every tick, producing an infinite loop that hangs the game action indefinitely. The `#warning TODO: impl timeout` confirms this is known incomplete code. (The offline variant `m_process__game_action__global_space__request__outbound_offline` exhibits the same deconstructing early-return pattern but is out of scope for this review file.)

### 1.5 `initialize_game_action_for__global_space__request`
**File:** `core/source/game_action/core/global_space/game_action__global_space__request__multiplayer.c` (lines 359–376)

**Defect — `Aliasing Bug` (downstream of 1.1) + `Surface-form leakage` (translation-and-semantics):** `initialize_timer_u32` is called with the buggy accessor 1.1, so timer start/remaining values are written into `gsv_3i32`, corrupting the global-space vector that was set on the preceding line, while `timeout__timer_u32` stays zero from the preceding `initialize_game_action` memset. Additionally the macro `GA_KIND__GBLOAL_SPACE__REQUEST__TIMEOUT` (defined in the type header, line 7) contains a typo ("GBLOAL" → "GLOBAL") that leaks into the initialization call site.

---

## 2. Impact Assessment

### 2.1 Accessor defect (1.1) and its two consumers (1.2, 1.5)
- **Callers of `get_p_timeout_timer_u32_from__ga_global_space__request`:** Only two translation units include/use it — `initialize_game_action_for__global_space__request` (1.5) and `m_process__game_action__global_space__request__outbound_client` (1.2), both in `game_action__global_space__request__multiplayer.c`. The `resolve.c`, `store.c`, and `offline.c` translation units do **not** reference the accessor or the timeout macro.
- **De facto contract:** No correct code relies on the timer being stored in `gsv_3i32`. The by-value getter `get_timeout_timer_u32_from__ga_global_space__request` reads `timeout__timer_u32` and is the intended contract; nothing consumes it yet, so correcting the pointer variant aligns both getters without breaking a real caller.
- **Invalidated assumptions after fix:**
  - In `initialize` (1.5): `gsv_3i32` will no longer be overwritten by timer data, so the vector survives intact. The `timeout__timer_u32` field becomes the single initialized timer (`Single Source of Truth`), replacing the corrupted-vector-as-timer assumption.
  - In `outbound_client` (1.2): the timeout will fire after `GA_KIND__GBLOAL_SPACE__REQUEST__TIMEOUT << 20` ticks of real elapsed time instead of being driven by vector coordinates. Any caller that (incorrectly) expected the timeout to never fire or to fire based on vector magnitude will see changed behavior — but no such correct caller exists.
- **Macro typo (1.5):** `GA_KIND__GBLOAL_SPACE__REQUEST__TIMEOUT` is referenced only at the `initialize_game_action_for__global_space__request` call site. Renaming it invalidates only that single reference plus any future references; no other file uses it.

### 2.2 Resource leak (1.3)
- **Callers of the failure path:** `m_process__game_action__global_space__request__outbound_client__init` is the only producer of this leak. `drop_global_space_within__global_space_manager` → `release_global_space` (in `global_space_manager.c`) gates chunk release on `p_global_space->p_chunk`, which is still `NULL` in the collision-node-failure path, so the pool never recovers the chunk.
- **Invalidated assumptions after fix:** Correcting the ordering (or adding an explicit `release_chunk_from__chunk_pool`) means the `Chunk_Pool` count is restored on this path. No caller depends on the leak; the change is behavior-preserving for all successful paths and strictly corrective for the failure path.

### 2.3 Server infinite loop (1.4)
- **Callers affected:** `m_process__game_action__global_space__request__outbound_server` is registered via `register_game_action__global_space__request_for__server` and invoked by the process scheduler. The deconstructing early-return currently hangs the process.
- **Invalidated assumptions after fix:** Adding a terminal transition (`fail_process`) on the deconstructing path terminates the process instead of re-polling it. The `inbound_server` variant already fails on its deconstructing path (for contrast), so the server-side fix aligns `outbound_server` with the established convention. No caller relies on the hang.

---

## 3. Resolution Assessment

### Fix 1 — Correct the pointer accessor (root cause for 1.2 and 1.5)
**File:** `core/include/types/core/game_action/global_space/ga_type__global_space__request.h`
- Change `return &…->gsv_3i32;` to `return &…->timeout__timer_u32;` in `get_p_timeout_timer_u32_from__ga_global_space__request`, mirroring the correct by-value getter.
- Rename the macro `GA_KIND__GBLOAL_SPACE__REQUEST__TIMEOUT` → `GA_KIND__GLOBAL_SPACE__REQUEST__TIMEOUT` and update its single consumer in `initialize_game_action_for__global_space__request`.
- No caller updates required beyond the macro rename (one site).

### Fix 2 — Eliminate the chunk leak (1.3)
**File:** `core/source/game_action/core/global_space/game_action__global_space__request__multiplayer.c`
- Preferred: assign `p_global_space->p_chunk = p_chunk;` immediately after successful chunk allocation (before the collision-node allocation), so `release_global_space` can release it on any subsequent failure. This restores the `Coupled` cleanup invariant for all failure paths.
- Alternative (if assignment ordering must stay): explicitly call `release_chunk_from__chunk_pool(...)` in the collision-node failure path before `drop_global_space_within__global_space_manager`.
- No caller updates; `Chunk_Pool`/`Collision_Node_Pool` accounting is restored.

### Fix 3 — Terminate the deconstructing path (1.4)
**File:** `core/source/game_action/core/global_space/game_action__global_space__request__multiplayer.c`
- In the deconstructing branch of `m_process__game_action__global_space__request__outbound_server`, call `fail_process(p_this_process)` (and a `debug_error` log, matching the other error paths) before returning, so the process reaches a terminal state instead of looping.
- Consider applying the same pattern to the offline variant `m_process__game_action__global_space__request__outbound_offline` (out of scope for this review file, but noted for consistency).
- No caller updates; the scheduler simply observes a terminal process.

### Phased approach
The fixes are independent and low-risk:
1. Fix the accessor + macro typo (enables correct timeout semantics).
2. Fix the resource leak (restores pool conservation).
3. Fix the server termination (removes the hang).
Each can be landed and verified separately. No cross-file structural changes are required.

---

## 4. Test Verification Checklist

**Existing test coverage:** The multiplayer and offline test suites (`test_suite_game_action_core_global_space_game_action__global_space__request__multiplayer.c`, `..._offline.c`) only assert that `register_game_action__global_space__request_for__server` / `_for__client` / `_for__offline` populate the `Game_Action_Logic_Table`. They do **not** exercise the process run handlers, the timer accessor, the timeout, the allocation-failure path, or the server termination path. Therefore existing tests assert neither the broken behavior nor the corrected behavior — they are unaffected by the fixes (Low test blast radius).

**New tests needed:**
- **Accessor equivalence (1.1):** `Equivalence Check` — assert `get_p_timeout_timer_u32_from__ga_global_space__request(p_ga)` returns a pointer equal to `&p_ga->…->timeout__timer_u32` and *not* to `&p_ga->…->gsv_3i32`. A `Property Based Testing` variant: after `initialize_game_action_for__global_space__request`, the by-value getter and the dereferenced pointer getter return identical `Timer__u32` values.
- **Timeout semantics (1.2, 1.5):** `Property Based Testing` — after init, the timeout timer is non-zero and `poll_timer_by__this_duration_u32` flips to elapsed only after the full duration elapses; `Fuzzing` the elapsed-duration input around the boundary (0, duration-1, duration) to validate the `Boundary Condition`.
- **Resource conservation (1.3):** `Property Based Testing` / `Conservation Law` check — inject a collision-node allocation failure and assert the `Chunk_Pool` slot count is unchanged (chunk released) and `p_global_space->p_chunk` is `NULL` post-cleanup. `Mutation Testing` of the failure path guards against regression.
- **Server termination (1.4):** `Round Trip Check` — drive `m_process__game_action__global_space__request__outbound_server` against a deconstructing `Global_Space` and assert the process reaches a terminal status (`Fail`) on the first poll rather than remaining `Busy` across repeated polls.
- **Macro rename:** `Equivalence Check` that `GA_KIND__GLOBAL_SPACE__REQUEST__TIMEOUT << 20` equals the expected timeout quantity.

**Test blast radius: Low.** Existing registration-only tests remain valid; the new tests target previously-untested behavior paths.

---

## 5. Blast Radius Summary

- **Files changed:** 2 source files — `core/include/types/core/game_action/global_space/ga_type__global_space__request.h` (accessor + macro rename) and `core/source/game_action/core/global_space/game_action__global_space__request__multiplayer.c` (resource leak + server termination). No other production files require changes.
- **Behavior preservation for current callers:** The two accessor consumers (`initialize` and `outbound_client`) are the only dependents; fixing the accessor makes the timeout functional where it was previously non-functional/garbage-driven. The leak fix and server-termination fix are strictly corrective on failure/deconstructing paths. Successful happy paths are unchanged.
- **De facto contracts invalidated:** None of consequence — no correct code depended on the timer aliasing `gsv_3i32`, on the chunk leak, or on the server hang. The `inbound_server` deconstructing path already fails (providing the intended contract the `outbound_server` fix will match).
- **Phased approach:** Yes — the three fixes are independent and can be landed/verified separately.
