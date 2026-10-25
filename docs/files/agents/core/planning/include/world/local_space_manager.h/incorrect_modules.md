# Planning: local_space_manager.h — Incorrect Modules

**Review source:** `agents/core/review/include/world/local_space_manager.h/incorrect_modules.md`

**Source files reviewed (read-only):**
- `core/include/world/local_space_manager.h`
- `core/source/world/local_space_manager.c`
- `core/include/defines.h`
- `sdl/include/platform_defines.h`
- `tests/core/source/world/test_suite_world_local_space_manager.c`

---

## 1. Problem Identification

Three functions in the local space manager were flagged as **Incorrect**. Each has a distinct defect class.

### 1a. `is_local_space_manager__loaded` (inline, `.h` lines 33–43)

**Defect:** Mode Confusion — the threshold formula uses `CHUNK__WIDTH`, `CHUNK__HEIGHT`, `CHUNK__DEPTH` instead of `LOCAL_SPACE_MANAGER__WIDTH`, `LOCAL_SPACE_MANAGER__HEIGHT`, `LOCAL_SPACE_MANAGER__DEPTH`. The function operates on the `Local_Space_Manager` domain but computes its tolerance from the chunk domain. With default values (CHUNK 8×8×2, LSM 8×8×1, VOLUME = 64), the formula yields 128, which exceeds VOLUME_OF__LOCAL_SPACE_MANAGER. The delegate's `quantity_of__loading_spaces <= 128` guard therefore always passes, making the function a no-op that unconditionally returns `true`.

### 1b. `get_p_local_space_from__local_space_manager` (`.c`)

**Defect:** Unenforced Precondition — the function dereferences `p_local_space_manager->p_local_space__south_west` without a null check. It also performs pointer-chasing traversal (`move_p_ptr_local_space_*`) without validating that the requested `chunk_vector__3i32` falls within the grid bounds. If the delta exceeds grid dimensions, neighbor pointers become null, and the `move_p_ptr_local_space_*` helpers dereference null — undefined behavior. The final vector-equality check (which would return null for out-of-bounds targets) is unreachable in these cases because traversal crashes first.

### 1c. `get_p_local_space_by__index_from__local_space_manager` (inline, `.h` lines 69–79)

**Defect:** Boundary Condition — the debug-only guard uses `>` (strict greater-than) instead of `>=` (greater-than-or-equal). The array has exactly `VOLUME_OF__LOCAL_SPACE_MANAGER` (64) elements with valid indices 0–63. When `index_of__local_space == 64`, the check `64 > 64` evaluates false, the guard is bypassed, and `local_spaces[64]` is an out-of-bounds access. In release builds (`NDEBUG` defined) no guard exists at all.

---

## 2. Impact Assessment

### 2a. `is_local_space_manager__loaded` — de facto contract already violated

- **Callers:** This is a `static inline` function in the header; any translation unit that includes `local_space_manager.h` can call it. It is intended to gate behavior that depends on all (or nearly all) local spaces having active global spaces (e.g., rendering, collision queries, game-loop progression).
- **Coupled assumption:** Callers assume the function returns `false` while spaces are still loading and `true` only when the manager is fully loaded. Because the threshold (128) exceeds VOLUME (64), the function always returns `true`. Any caller that uses this as a gate is operating under a **State Desync** — it believes the manager is loaded when it may not be.
- **Blast radius of fix:** Correcting the constants will make the function start returning `false` in states where spaces are genuinely still loading. Callers that currently "work" only because the check is a no-op may break or exhibit different timing behavior. This is a de facto contract: the broken always-true behavior has been relied upon implicitly.

### 2b. `get_p_local_space_from__local_space_manager` — undefined behavior on out-of-bounds input

- **Direct callers:**
  - `get_p_local_space_by__3i32F4_from__local_space_manager` (inline, `.h`) — wraps this function; any caller of the 3i32F4 variant is a transitive caller.
  - `get_p_tile_by__3i32F4_from__local_space_manager` (`.c`) — calls the 3i32F4 wrapper.
- **Coupled assumption:** The function's Postcondition promises to return null if the target is not found. But the traversal path (null neighbor dereference) causes undefined behavior before the verification step can execute. Callers that pass a `chunk_vector__3i32` outside the manager's grid extent are subject to a **Boundary Condition** violation that manifests as a crash, not a clean null return.
- **Blast radius of fix:** Adding null checks and bounds validation before traversal is behavior-preserving for in-bounds callers (the traversal path is unchanged). For out-of-bounds callers, the fix converts undefined behavior into the documented null return. No caller that currently works correctly will break.

### 2c. `get_p_local_space_by__index_from__local_space_manager` — debug guard off-by-one

- **Direct callers:**
  - `drop_all__local_spaces_in__local_space_manager` (`.c`) — iterates index 0 to VOLUME−1; safe.
  - `hold_all__unheld_local_spaces_in__local_space_manager` (`.c`) — iterates index 0 to VOLUME−1; safe.
  - Test file (`test_suite_world_local_space_manager.c`) — uses index 0 and VOLUME−1; safe.
- **Coupled assumption:** No current caller passes `index == VOLUME` (64). The off-by-one is latent: it only manifests if a future caller or a bug upstream computes an index equal to VOLUME. In release builds the guard is entirely absent, so the risk is unbounded.
- **Blast radius of fix:** Changing `>` to `>=` is behavior-preserving for all current callers (all use indices in [0, VOLUME−1]). No cascading changes required.

---

## 3. Resolution Assessment

### 3a. Fix `is_local_space_manager__loaded`

**What to change in the implementation:**
- Replace `CHUNK__WIDTH`, `CHUNK__HEIGHT`, `CHUNK__DEPTH` with `LOCAL_SPACE_MANAGER__WIDTH`, `LOCAL_SPACE_MANAGER__HEIGHT`, `LOCAL_SPACE_MANAGER__DEPTH` in the threshold formula.
- **Re-evaluate the formula itself.** Even with correct constants, the surface-area-style formula `(W−1)(D−1)·2 + (H−1)(D−1)·2 + (W−1)(H−1)·2 + 2` yields 100 for the default 8×8×1 manager, which still exceeds VOLUME (64). The formula computes a surface-area-like quantity, not a meaningful loading tolerance. The correct threshold should be derived from the actual number of local spaces that can be in a transitional state. Options:
  - Use `VOLUME_OF__LOCAL_SPACE_MANAGER` as the threshold (allow all spaces to still be loading — effectively "is the manager initialized?").
  - Use a smaller, explicitly defined tolerance (e.g., 0 for "fully loaded" or a named constant).
  - Remove the inline wrapper entirely and require callers to pass an explicit threshold via `is_local_space_manager__loaded_except_with__this_many_spaces`.

**Callers:** Any caller of `is_local_space_manager__loaded` will see a behavior change. Audit all call sites and confirm they handle a `false` return correctly (e.g., by waiting or skipping the gated operation).

**Tests:** Add tests that verify the function returns `false` when spaces are genuinely in a loading state and `true` when all spaces are active.

### 3b. Fix `get_p_local_space_from__local_space_manager`

**What to change in the implementation:**
- Add a null check on `p_local_space_manager` at function entry; return 0 if null.
- Add a null check on `p_local_space_manager->p_local_space__south_west`; return 0 if null.
- Add bounds validation before the traversal loops: verify that `chunk_vector__3i32` falls within the grid extent spanned by the south_west and north_east corners (similar to what `is_vector_3i32F4_within__local_space_manager` does). If out of bounds, return 0 immediately. This prevents null neighbor dereference during traversal.

**Callers:** No caller changes needed. The fix is behavior-preserving for in-bounds inputs and converts undefined behavior to the documented null return for out-of-bounds inputs.

**Tests:** Add a test that calls the function with an out-of-bounds `chunk_vector__3i32` and asserts it returns 0 (not a crash). Add a test with a null `p_local_space_manager` and assert null return.

### 3c. Fix `get_p_local_space_by__index_from__local_space_manager`

**What to change in the implementation:**
- Change the debug guard comparison from `index_of__local_space > VOLUME_OF__LOCAL_SPACE_MANAGER` to `index_of__local_space >= VOLUME_OF__LOCAL_SPACE_MANAGER`.

**Callers:** No caller changes needed. All existing callers use indices in [0, VOLUME−1].

**Tests:** The existing tests cover valid indices (0 and VOLUME−1). Add a test that passes `index == VOLUME_OF__LOCAL_SPACE_MANAGER` and asserts the function returns 0 (in debug builds). This directly targets the off-by-one.

---

## 4. Test Verification Checklist

### Existing tests (`test_suite_world_local_space_manager.c`)

| Test | Asserts on | Post-fix status |
|------|-----------|-----------------|
| `local_space_manager__initialize__sets_center` | Correct center after init | Unaffected — no change to init path |
| `local_space_manager__get_by_index__valid_index` | Index 0 returns valid pointer | Unaffected — index 0 is valid |
| `local_space_manager__get_by_index__last_valid_index` | Index VOLUME−1 returns valid pointer | Unaffected — VOLUME−1 is the last valid index |

**No existing test asserts on the broken behavior.** No existing test will be invalidated by the fixes.

### New tests needed

| New test | Strategy | Target |
|----------|----------|--------|
| `get_by_index__out_of_bounds_index_returns_null` | **Boundary Condition** — pass index == VOLUME, assert null return (debug) | 3c off-by-one fix |
| `get_by_index__far_out_of_bounds_returns_null` | **Fuzzing**-adjacent — pass a large index (e.g., 999), assert null return (debug) | 3c off-by-one fix |
| `get_p_local_space__out_of_bounds_vector_returns_null` | **Boundary Condition** — pass a chunk vector outside the grid, assert null return | 3b bounds check fix |
| `get_p_local_space__null_manager_returns_null` | **Precondition** violation — pass null manager, assert null return | 3b null check fix |
| `is_loaded__returns_false_when_spaces_loading` | **Property Based Testing** — set up a manager with some non-active global spaces, assert `is_local_space_manager__loaded` returns false | 3a threshold fix |
| `is_loaded__returns_true_when_all_spaces_active` | **Equivalence Check** — set up a fully active manager, assert true; compare against direct count of non-active spaces | 3a threshold fix |

**Blast radius (test impact):** Low. Three new test functions for the off-by-one and null-check fixes, two for the loaded check. No existing tests need modification. A phased approach is not needed — all fixes are independent and can be tested in one pass.

---

## 5. Blast Radius Summary

| Fix | Files changed | Behavior-preserving for current callers? | Phased approach? | De facto contract invalidated? |
|-----|--------------|------------------------------------------|-------------------|-------------------------------|
| 3a: `is_local_space_manager__loaded` threshold | `core/include/world/local_space_manager.h` (1 file) | **No** — function will start returning `false` in states where it previously returned `true`. Callers that relied on the always-true behavior may need updating. | Yes — audit all callers first, then fix. | **Yes** — the always-true return is a de facto contract that some callers implicitly depend on. |
| 3b: `get_p_local_space_from__local_space_manager` null/bounds guards | `core/source/world/local_space_manager.c` (1 file) | **Yes** — in-bounds behavior unchanged; out-of-bounds converts UB to documented null return. | No | No |
| 3c: `get_p_local_space_by__index` off-by-one | `core/include/world/local_space_manager.h` (1 file) | **Yes** — all current callers use valid indices. | No | No |

**Total files modified:** 2 (`local_space_manager.h`, `local_space_manager.c`) + 1 test file.

**Recommended order:** Fix 3c (trivial, zero risk) → fix 3b (low risk, adds safety) → fix 3a (highest risk, requires caller audit). This ordering ensures the safe fixes land first and the behavior-changing fix is last with full caller understanding.
