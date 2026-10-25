# Planning: ga_type__global_space__request.h — Incorrect Modules

**Review source:** `agents/core/review/include/types/core/game_action/global_space/ga_type__global_space__request.h/incorrect_modules.md`

**Source files reviewed (read-only):**
- `core/include/types/core/game_action/global_space/ga_type__global_space__request.h`
- `core/source/game_action/core/global_space/game_action__global_space__request__multiplayer.c`
- `core/source/game_action/core/global_space/game_action__global_space__request__offline.c`
- `core/include/timer.h`
- `tests/core/source/game_action/core/global_space/test_suite_game_action_core_global_space_game_action__global_space__request__multiplayer.c`
- `tests/core/source/game_action/core/global_space/test_suite_game_action_core_global_space_game_action__global_space__request__offline.c`

---

## 1. Problem Identification

**Flagged:** `get_p_timeout_timer_u32_from__ga_global_space__request` (header line 75–82) — verdict **Incorrect**.

- **Defect (Aliasing Bug / Surface-form leakage):** The pointer accessor declares return type `Timer__u32 *` but its body returns `&...->gsv_3i32`, i.e. a `Global_Space_Vector__3i32 *`. The member access was never updated after a copy-paste from the sibling `get_p_gsv_3i32_from__ga_global_space__request` (line 45–52, which correctly returns `&...->gsv_3i32`). The name's surface form promises the timeout field; the body delivers the vector field.
- **Type mismatch:** `Timer__u32` is `{ uint32_t remaining__u32; uint32_t start__u32; }`; `Global_Space_Vector__3i32` is `struct Vector__3i32_t { int32_t x, y, z; }`. Both are 12 bytes, so the incompatible pointer conversion may compile silently (with a suppressed warning), and callers dereference the wrong struct layout.
- **Resulting State Desync:** Any write through the returned "timer" pointer actually mutates the first 8 bytes of `gsv_3i32`, and any read interprets vector coordinates as timer fields. The payload's two logical fields alias the same memory region — violating the Representation Invariant that each struct member is the Single Source of Truth for its value.
- **Precondition/Postcondition violation:** Postcondition 1 ("caller receives a non-null pointer to `timeout__timer_u32`") is not met; the value-returning sibling `get_timeout_timer_u32_from__ga_global_space__request` (line 64–72) is correct and confirms the intended field.

## 2. Impact Assessment

Callers of the broken accessor (only file: `core/source/game_action/core/global_space/game_action__global_space__request__multiplayer.c`):

1. **`initialize_game_action_for__global_space__request` (line 359–373):**
   Sets `*get_p_gsv_3i32... = global_space_vector__3i32` (line 366), then calls `initialize_timer_u32(get_p_timeout_timer_u32..., GA_KIND__GBLOAL_SPACE__REQUEST__TIMEOUT << 20)` (line 368–372). Through the broken pointer, this writes `start__u32`/`remaining__u32` into `gsv_3i32.x` and `gsv_3i32.y`, **corrupting the destination vector the request was just given**. The timer field itself is never initialized.
   - Downstream: `get_gsv_3i32_from__ga_global_space__request` (value getter) and any peer receiving the serialized `GA_Global_Space__Request` TCP payload observe a corrupted vector — a Cascade Failure into networking and remote resolution.

2. **`m_process__game_action__global_space__request__outbound_client` (line ~205–215):**
   On `PLATFORM_Read_File_Error__System_Busy`, it calls `poll_timer_by__this_duration_u32(get_p_timeout_timer_u32..., get_elapsed_time__u32F20_of__game(...))`. Through the broken pointer, polling reads/decrements `gsv_3i32.x`/`gsv_3i32.y` as `remaining__u32`/`start__u32`. The debug assertion `remaining > start` and elapsed logic operate on garbage; timeout detection is effectively undefined.

**Assumptions invalidated by the fix:**
- The broken behavior is **not** a de facto contract: no test or caller asserts on the corrupted coupling. Callers were written against the *intended* contract (timer pointer), so correcting the accessor restores their semantics rather than breaking them.
- The only "coupling" created by the bug is accidental aliasing between `timeout__timer_u32` and `gsv_3i32` inside any `GA_Global_Space__Request` payload; after the fix, no code path touches that alias. No production data layout changes — the struct definition is untouched.
- The offline variant (`game_action__global_space__request__offline.c`) does not reference the timeout field and is unaffected.

## 3. Resolution Assessment

**Phase 1 — Core fix (single token change):**
- In `core/include/types/core/game_action/global_space/ga_type__global_space__request.h` line 80, change `->gsv_3i32` to `->timeout__timer_u32` inside `get_p_timeout_timer_u32_from__ga_global_space__request`.
- No caller changes required: both call sites in the multiplayer `.c` were already written for the intended contract; they become correct as-is.
- No struct/serialization changes: `GA_Global_Space__Request` layout, `TCP_PAYLOAD_BITMAP`, and wire format are unchanged.

**Phase 2 — Regression prevention:**
- Add a **Lint Gate**: enable `-Werror=incompatible-pointer-types` (or equivalent Static Analysis check) so any future copy-paste divergence between an accessor's declared return type and its accessed member is a hard build error. This defect is exactly the class this gate catches.
- Equivalence Check test: for a `Game_Action` of kind `Global_Space__Request`, assert `*get_p_timeout_timer_u32... == get_timeout_timer_u32...` after any mutation via the pointer accessor (pointer/value siblings must stay in lockstep).
- **Round Trip Check** test: `initialize_game_action_for__global_space__request(p_ga, v)` then verify (a) `get_gsv_3i32...` still equals `v` (frame condition: vector untouched by timer init), and (b) the timer reads back `GA_KIND__GBLOAL_SPACE__REQUEST__TIMEOUT << 20` for both `start__u32` and `remaining__u32`.
- **Property Based Testing**: for arbitrary vectors, assert the Representation Invariant that initializing/advancing the timeout timer never mutates `gsv_3i32`, and vice versa — the two fields are Orthogonal.
- Timeout path test: simulate `System_Busy` polls in the outbound client processor and assert `poll_timer_by__this_duration_u32` eventually fires after the expected elapsed time, then reverts to normal processing (no spurious early timeout).

**Test impact (blast radius: Low):**
- Existing suites (`test_suite_..._request__multiplayer.c`, `test_suite_..._request__offline.c`) contain **no** assertions on the timeout path or on the broken aliasing (verified: no references to `get_p_timeout_timer_u32...` or "timeout" in either file), so no existing assertions are invalidated.
- New tests above are additive only. No phased test migration needed.

## 4. Blast Radius Summary

- **Files changed:** 1 (`ga_type__global_space__request.h`, one member-access token) + test additions.
- **Behavior-preserving for callers?** Yes — callers were written against the intended contract; the fix *restores* intended behavior (correct timer init, intact request vector, defined timeout polling). The only behavior that "changes" is the removal of accidental data corruption.
- **De facto contracts invalidated:** None — the broken aliasing was never asserted or depended upon.
- **Phased approach:** Not required; a single atomic change plus additive tests and a lint gate suffices.
