# Planning: hitbox_aabb.h — Incorrect Modules

**Review source:** `agents/core/review/include/collisions/core/aabb/hitbox_aabb.h/incorrect_modules.md`

**Source files reviewed (read-only):**
- `core/include/collisions/core/aabb/hitbox_aabb.h`
- `core/source/collisions/core/aabb/hitbox_aabb.c`
- `core/include/vectors.h`
- `core/include/numerics.h`
- `core/include/defines.h`

---

## 1. Problem Identification

Seven functions flagged as **Incorrect** in the review:

| # | Function | Core Defect |
|---|----------|-------------|
| 1 | `initialize_vector_3i32_as__aa_bb_without__velocity` | **Mode Confusion** — z-component assigns raw `i32F4` to an `i32` field without the `i32F4_to__i32` conversion that x/y perform. Result: z is 16× the intended integer value. |
| 2 | `is_this_hitbox_aabb__fully_inside_this_hitbox_aabb__without_velocity` | **State Desync** — the "without_velocity" qualifier applies only to `hitbox__one`'s corners; the containment check on `hitbox__two` routes through `is_vector_3i32F4_inside__hitbox_aabb` → `get_aa_bb_as__vectors_3i32F4_from__hitbox_aabb` → `initialize_vector_3i32F4_as__aa_bb` (velocity-inclusive). The semantic contract promises a fully static comparison but delivers a mixed-velocity one. |
| 3 | `is_vector_3i32F4_inside__hitbox_aabb` | **Aliasing Bug** (copy-paste) — z-axis upper bound compares against `aa.z__i32F4` instead of `bb.z__i32F4`. Collapses the range check to an equality check. Currently latent because `aa.z == bb.z` (AABB has no z-extent), but breaks silently if z-extent is introduced. |
| 4 | `apply_velocity_to__hitbox_aabb` | **State Desync** — omits `set_hitbox_aabb_as__dirty`, unlike every sibling velocity setter. Downstream collision systems key off the dirty flag to detect spatial changes; an unflagged velocity mutation leaves them with stale state. Additionally, no null-check on the `vector` pointer parameter (UB risk). |
| 5 | `set_hitbox_aabb__position_with__3i32` | **Boundary Condition** violation — raw left-shift (`x << 4`) on potentially negative `Signed_Index__i32` values is undefined behavior per C11 §6.5.7.4. The engine provides `i32_to__i32F4()` / `ARITHMETIC_L_SHIFT` specifically to avoid this, and the canonical converter `vector_3i32_to__vector_3i32F4` exists but is unused here. |
| 6 | `is_vector_3i32_inside__hitbox_aabb` | **Aliasing Bug** — identical to #3: z-axis upper bound uses `aa.z__i32` instead of `bb.z__i32`. Same latent nature. |
| 7 | `initialize_vector_3i32_as__aa_bb` | **Coupled** to broken callee #1 — inherits the z Mode Confusion transitively. Also contains a copy-paste artifact in the debug error string (references the F4 variant name). |

---

## 2. Impact Assessment

### Internal call graph within `hitbox_aabb.c`

```
is_this_hitbox_aabb__fully_inside_this_hitbox_aabb__without_velocity
  ├── initialize_vector_3i32F4_as__aa_bb_without__velocity  (correct)
  └── is_vector_3i32F4_inside__hitbox_aabb  [BUG #3: z-bound]
        └── get_aa_bb_as__vectors_3i32F4_from__hitbox_aabb
              └── initialize_vector_3i32F4_as__aa_bb  (velocity-inclusive → State Desync for #2)

get_aa_bb_as__vectors_3i32_from__hitbox_aabb
  └── initialize_vector_3i32_as__aa_bb  [BUG #7: z Mode Confusion]
        ├── initialize_vector_3i32_as__aa_bb_without__velocity  [BUG #1: z Mode Confusion]
        └── get_x/y_i32_from__vector_3i32F4(velocity)  (correct)

clamp_p_vector_3i32_to__hitbox_aabb
  └── get_aa_bb_as__vectors_3i32_from__hitbox_aabb  (inherits #1/#7 z bug)

is_vector_3i32_inside__hitbox_aabb  [BUG #6: z-bound]
  └── get_aa_bb_as__vectors_3i32_from__hitbox_aabb  (inherits #1/#7 z bug)
```

### Affected consumers

- **`clamp_p_vector_3i32_to__hitbox_aabb`** — clamps a position to the hitbox's aa/bb corners. With the z Mode Confusion (#1), `bb.z` is 16× the actual integer z, so clamping on z is effectively a no-op for positions below the inflated bound. Any entity or UI element relying on this clamp gets incorrect z bounds.

- **`is_vector_3i32_inside__hitbox_aabb`** — consumers checking integer-space containment (e.g., tile-touch detection, UI hit-testing) get an incorrect z predicate. Currently latent (aa.z == bb.z in practice), but the combined effect of #1 (inflated bb.z from corner computation) and #6 (upper bound uses aa.z) means the function is doubly broken on z.

- **`apply_velocity_to__hitbox_aabb`** (inline, header-visible) — any translation unit that includes `hitbox_aabb.h` and calls this function triggers the missing-dirty-flag State Desync. The collision resolver and hitbox manager rely on the dirty flag to schedule re-evaluation. An unflagged velocity change means a hitbox can move without the collision system detecting it until some *other* mutation sets dirty.

- **`set_hitbox_aabb__position_with__3i32`** — called during initialization (`initialize_hitbox_aabb_as__allocated` does not call it directly, but entity spawn/teleport code paths do). Negative world positions are routine; the UB means compiler optimizations may produce arbitrary results for negative coordinates.

- **Structs embedding `Hitbox_AABB`:** `Typer`, `Room`, `Structure`, `Site` (defined in `defines.h`). Their position/velocity management flows through these functions.

### De facto contracts invalidated by the fix

- The z-equality coincidence (`aa.z == bb.z`) is a **de facto invariant** that masks bugs #3 and #6. Fixing the Aliasing Bug makes the z range check *active*, which is correct but changes behavior if any caller was (accidentally) relying on the collapsed equality semantics. In practice no caller should rely on this, but it warrants a `Property Based Testing` pass to confirm.

- The missing dirty flag in `apply_velocity_to__hitbox_aabb` means some code paths may have been *working around* the stale state by manually setting dirty after velocity changes. Adding the dirty flag makes those workarounds redundant but not harmful (setting dirty twice is idempotent).

---

## 3. Resolution Assessment

### Fix 1: `initialize_vector_3i32_as__aa_bb_without__velocity` (hitbox_aabb.c)

**Change:** Replace the raw z assignment with the canonical conversion:
```c
// Before (broken):
hitbox_point->z__i32 = p_hitbox_aabb->position__3i32F4.z__i32F4;

// After (correct):
hitbox_point->z__i32 = get_z_i32_from__hitbox_aabb(p_hitbox_aabb);
```
This mirrors the x/y pattern and uses the existing `i32F4_to__i32` arithmetic right-shift internally.

**Also fix:** The debug error string (copy-paste artifact referencing "F4" variant name).

**Callers needing update:** None — the function signature is unchanged. The fix corrects the value, not the interface.

### Fix 2: `is_this_hitbox_aabb__fully_inside_this_hitbox_aabb__without_velocity` (hitbox_aabb.c)

**Change:** Eliminate the State Desync by computing `hitbox__two`'s bounds using the velocity-free path. Two options:

- **Option A (preferred):** Inline the containment check using `initialize_vector_3i32F4_as__aa_bb_without__velocity` for both hitboxes, performing the range comparison directly without delegating to `is_vector_3i32F4_inside__hitbox_aabb`.
- **Option B:** Introduce a new internal helper `is_vector_3i32F4_inside__hitbox_aabb__without_velocity` that uses the velocity-free corner computation, and delegate to it.

Option A is simpler (avoids adding a new public API) and makes the "without_velocity" contract explicit in the function body.

**Callers needing update:** None — signature unchanged.

### Fix 3: `is_vector_3i32F4_inside__hitbox_aabb` (hitbox_aabb.c)

**Change:** Correct the z upper-bound reference:
```c
// Before (broken):
&& vector.z__i32F4 <= aa.z__i32F4

// After (correct):
&& vector.z__i32F4 <= bb.z__i32F4
```

**Callers needing update:** None — signature unchanged. Behavior change is from "z must equal aa.z" to "z must be in [aa.z, bb.z]". Currently latent; becomes active only if z-extent is introduced.

### Fix 4: `apply_velocity_to__hitbox_aabb` (hitbox_aabb.h, inline)

**Change:**
1. Add `set_hitbox_aabb_as__dirty(p_hitbox_aabb);` before the per-axis delegation.
2. Add a null-check for `vector` in the `#ifndef NDEBUG` guard:
   ```c
   if (!vector) {
       debug_error("apply_velocity_to__hitbox_aabb, vector == 0.");
       return;
   }
   ```
3. Fix the debug error string to use the full function name.
4. Resolve or remove the stale TODO comment about pointer requirement.

**Callers needing update:** None — signature unchanged. The added dirty flag is additive (idempotent with existing manual dirty-setting).

### Fix 5: `set_hitbox_aabb__position_with__3i32` (hitbox_aabb.c)

**Change:** Replace the manual left-shift with the canonical converter:
```c
// Before (UB on negative values):
i32F4 x__global = position__3i32.x__i32;
p_hitbox_aabb->position__3i32F4.x__i32F4 = x__global << FRACTIONAL_PERCISION_4__BIT_SIZE;
// ... (repeated for y, z)

// After (safe, uses ARITHMETIC_L_SHIFT internally):
p_hitbox_aabb->position__3i32F4 = vector_3i32_to__vector_3i32F4(position__3i32);
```

This is a single-line replacement that eliminates the UB and aligns with the engine's **Single Source of Truth (SSOT)** principle for type conversions (the converter in `vectors.h` is the canonical path).

**Callers needing update:** None — signature unchanged.

### Fix 6: `is_vector_3i32_inside__hitbox_aabb` (hitbox_aabb.c)

**Change:** Identical to Fix 3 but for the i32 variant:
```c
// Before (broken):
&& vector.z__i32 <= aa.z__i32

// After (correct):
&& vector.z__i32 <= bb.z__i32
```

**Callers needing update:** None.

### Fix 7: `initialize_vector_3i32_as__aa_bb` (hitbox_aabb.c)

**Change:** No direct code change needed — the z bug is inherited from Fix 1. Once `initialize_vector_3i32_as__aa_bb_without__velocity` is corrected, this function is transitively fixed.

**Also fix:** The debug error string copy-paste artifact (references "F4" variant name).

**Callers needing update:** None.

### Phasing

All seven fixes are **independent and non-interfering**. They can be applied in a single pass:
- Fixes #3 and #6 are one-token changes (aa → bb).
- Fix #1 is a one-line change (raw assign → canonical getter).
- Fix #5 is a body replacement (3 lines → 1 line).
- Fix #4 adds 2 lines to an inline function.
- Fix #2 requires a small structural refactor (~10 lines) to inline the velocity-free containment check.
- Fix #7 is zero-change (transitive) + debug string correction.

No phased approach is required. A single commit addressing all seven is appropriate.

---

## 4. Test Verification Checklist

### Existing test coverage

No dedicated test file was found for `hitbox_aabb.c` in the source tree (the `test_suite_collisions_core_aabb_hitbox_aabb.c` referenced in search results does not exist on disk). The existing collision test suites (`test_suite_collisions_hitbox_context.c`, `test_suite_collisions_hitbox_manager_instance.c`) do not directly exercise the flagged functions.

### Required new tests

| Test | Strategy | What it verifies |
|------|----------|-----------------|
| `initialize_vector_3i32_as__aa_bb_without__velocity` z-conversion | **Equivalence Check** — for a set of hitboxes, assert `initialize_vector_3i32_as__aa_bb_without__velocity(...).z == i32F4_to__i32(hitbox->position.z)` | Fix #1: z is properly converted from F4 to i32 |
| `is_vector_3i32F4_inside__hitbox_aabb` z-range | **Property Based Testing** — generate random vectors; assert `inside == (z >= aa.z && z <= bb.z)` for all three axes independently | Fix #3: z range check is a true interval, not equality |
| `is_vector_3i32_inside__hitbox_aabb` z-range | **Property Based Testing** — same as above for i32 variant | Fix #6 |
| `is_this_hitbox_aabb__fully_inside_this_hitbox_aabb__without_velocity` velocity independence | **Differential Testing** — set non-zero velocity on hitbox__two; assert result is identical whether velocity is zero or non-zero | Fix #2: "without_velocity" contract holds for both operands |
| `apply_velocity_to__hitbox_aabb` dirty flag | **Round Trip Check** — call apply_velocity, assert `is_hitbox_aabb__dirty(hb) == true`; then `set_hitbox_aabb_as__not_dirty`, assert clean | Fix #4: dirty flag is set on velocity mutation |
| `set_hitbox_aabb__position_with__3i32` negative coordinates | **Fuzzing** — feed random i32 values (including INT32_MIN/4, -1, 0, 1, INT32_MAX/4) as position; assert no crash and `position__3i32F4 == vector_3i32_to__vector_3i32F4(input)` | Fix #5: no UB on negative values; canonical conversion |

### Blast radius for tests

**Low.** No existing tests are invalidated (no existing tests exercise these functions). New tests are additive. The `Property Based Testing` cases for #3/#6 should include a hitbox with non-zero z-extent (synthetic) to confirm the fix activates correctly when the latent condition changes.

---

## 5. Blast Radius Summary

| Metric | Assessment |
|--------|-----------|
| Files requiring changes | **2** (`hitbox_aabb.c`, `hitbox_aabb.h`) |
| Behavior-preserving for current callers? | **Yes** for #1, #3, #5, #6, #7 (latent or value-correction only). **Slight behavior change** for #2 (velocity no longer leaks into containment) and #4 (dirty flag now set — additive, idempotent). |
| Phased approach needed? | **No.** All fixes are small, independent, and non-interfering. Single-pass resolution. |
| De facto contracts invalidated? | The z-equality coincidence (masking #3/#6) is a de facto contract that *breaks* when the fix activates the true range check. In practice no caller exploits this (AAABB has no z-extent), but a **Property Based Testing** sweep confirms safety. |
| Header ABI change? | **No.** No function signatures change. Only inline body of `apply_velocity_to__hitbox_aabb` gains 2 lines. |
