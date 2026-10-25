# Planning: random.h — Incorrect Modules

**Review source:** `agents/core/review/include/random.h/incorrect_modules.md`

**Source files reviewed (read-only):**
- `core/include/random.h`
- `core/source/random.c`
- `core/include/defines.h`
- `tests/core/source/test_suite_random.c`

---

## 1. Problem Identification

### `get_pseudo_random_i32_with__xy__intrusively`

**Defect: State Desync (naming vs. behavior) + Mode Confusion (signed/unsigned arithmetic).**

The function name asserts "intrusive" semantics — i.e., it should mutate the struct's mutable state (`seed__current_random`), as the sibling `get_pseudo_random_i32__intrusively` does. The implementation does **not** modify `seed__current_random`; it only reads `seed__initial`. The name and the behavior are decoupled.

Additionally, the seed computation mixes `Signed_Index__i32` (int32_t, signed) with `Psuedo_Random_Seed__u32` (uint32_t, unsigned). C integer promotion converts the signed operand to unsigned before addition. A negative `x` wraps to a large unsigned value, producing a seed far from the intended range. The final return converts the unsigned sum back to `int32_t`, which is implementation-defined when the value exceeds `INT32_MAX`.

### `get_pseudo_random_i32__non_intrusively`

**Defect: Ordering error breaks determinism (State Desync).**

The implementation calls `rand()` **before** `srand()`:

```c
Psuedo_Random__i32 random = rand();   // consumes whatever global state exists
srand(p_repeatable_psuedo_random->seed__current_random);  // seeds AFTER
return random;
```

The returned value is therefore **not** deterministic with respect to the struct's `seed__current_random`. It depends on the prior global RNG state. The correct pattern (as used by `get_pseudo_random_i32__non_intrusively_with__seed`) seeds first, then generates.

---

## 2. Impact Assessment

### Callers of the broken functions

An exhaustive search of all `.c` files under `core/source/` found **no callers** of either `get_pseudo_random_i32_with__xy__intrusively` or `get_pseudo_random_i32__non_intrusively`. Both functions are declared in `random.h` and defined in `random.c` but are currently unused.

### Coupled assumptions

- **Global RNG state coupling**: Both functions call `srand()`, mutating the global C library RNG. Any future caller that interleaves these functions with direct `rand()` calls would observe non-deterministic behavior if the ordering bug in `get_pseudo_random_i32__non_intrusively` persists.
- **Struct state contract**: The `Repeatable_Psuedo_Random` struct is embedded in at least seven manager types (`Entity_Manager`, `Process_Manager`, `Aliased_Texture_Manager`, `Game_Action_Manager`, world context, `Graphics_Window_Manager`, UI element pool). Callers that use the *other* functions in this module (`get_pseudo_random_i32__intrusively`, `get_pseudo_random_i32__non_intrusively_with__seed`) rely on the SSOT of `seed__current_random` being the authoritative state for reproducibility. The broken `non_intrusively` variant, if ever called, would silently desync expectations about determinism.
- **No de facto contract exists** because no current code calls either broken function.

### Blast radius of correction

Since no existing callers depend on the broken behavior, correcting both functions is **behavior-preserving for all current code**. No cascading changes are required in `./include` or `./source`.

---

## 3. Resolution Assessment

### Fix 1: `get_pseudo_random_i32__non_intrusively`

**Change**: Swap the order of `srand()` and `rand()`.

```c
Psuedo_Random__i32 get_pseudo_random_i32__non_intrusively(
        Repeatable_Psuedo_Random *p_repeatable_psuedo_random) {
    srand(p_repeatable_psuedo_random->seed__current_random);
    Psuedo_Random__i32 random = rand();
    return random;
}
```

- The struct is not mutated (preserves "non-intrusive" contract).
- The result is now deterministic w.r.t. `seed__current_random`.
- No caller updates needed (no callers exist).

### Fix 2: `get_pseudo_random_i32_with__xy__intrusively`

Two sub-issues to resolve:

**(a) State Desync — name vs. behavior:**

Option A (preferred): Rename to `get_pseudo_random_i32_with__xy__non_intrusively` to match the actual behavior (reads `seed__initial`, does not mutate the struct). Update the declaration in `random.h` and the definition in `random.c`.

Option B: Change the implementation to actually update `seed__current_random` after computing the result, making it truly "intrusive." This is semantically heavier and less predictable for a coordinate-keyed lookup.

**Recommendation**: Option A. The function's intent is a deterministic, coordinate-keyed hash — it should not advance the struct's sequential state. Renaming aligns the surface form with the semantic intent.

**(b) Mode Confusion — signed/unsigned arithmetic:**

Explicitly cast operands to a common unsigned width before arithmetic to make the wrapping behavior intentional and well-defined:

```c
Psuedo_Random__i32 get_pseudo_random_i32_with__xy__non_intrusively(
        Repeatable_Psuedo_Random *p_repeatable_psuedo_random,
        Signed_Index__i32 x,
        Signed_Index__i32 y) {
    Psuedo_Random_Seed__u32 seed_a =
        (Psuedo_Random_Seed__u32)x + p_repeatable_psuedo_random->seed__initial;
    srand(seed_a);
    Psuedo_Random_Seed__u32 r1 = (Psuedo_Random_Seed__u32)rand();

    Psuedo_Random_Seed__u32 seed_b =
        r1 + (Psuedo_Random_Seed__u32)y + p_repeatable_psuedo_random->seed__initial;
    srand(seed_b);
    Psuedo_Random_Seed__u32 r2 = (Psuedo_Random_Seed__u32)rand();

    return (Psuedo_Random__i32)(r1 + r2);
}
```

The explicit casts make the unsigned wrap-around a deliberate design choice rather than an implicit, compiler-dependent conversion. The final cast to `int32_t` is well-defined for two's-complement (C99+ guarantees modular arithmetic for unsigned; the final narrowing to signed is a defined reinterpretation of the bit pattern on all practical platforms).

### Caller updates

None required. No existing code calls either function.

### Documentation updates

- Update `random.h` declaration if renaming (Fix 2a).
- Add a brief comment in `random.c` noting that both functions mutate global RNG state as a side effect (Information Hiding: document the global-state coupling explicitly).

---

## 4. Test Verification Checklist

### Existing tests

`tests/core/source/test_suite_random.c` is an empty placeholder (`#warning Please make tests for...`). No existing assertions will be invalidated.

### New tests required

| Function | Test Strategy | Rationale |
|----------|--------------|-----------|
| `get_pseudo_random_i32__non_intrusively` | **Determinism check**: Call twice with same struct seed; assert equal results. Call with different seeds; assert different results (probabilistic). | Verifies the ordering fix restores the determinism Postcondition. |
| `get_pseudo_random_i32__non_intrusively` | **Non-intrusive check**: Record `seed__current_random` before and after; assert unchanged. | Verifies the struct is not mutated. |
| `get_pseudo_random_i32_with__xy__non_intrusively` (renamed) | **Determinism check**: Same (x, y, seed) → same result across calls. Different (x, y) → different results (probabilistic). | Verifies coordinate-keyed reproducibility. |
| `get_pseudo_random_i32_with__xy__non_intrusively` | **Boundary Condition / Fuzzing**: Exercise with `x = INT32_MIN`, `x = INT32_MAX`, `y = INT32_MIN`, `y = INT32_MAX`. Assert no UB (valgrind/ASan clean) and that results are stable across repeated calls. | Verifies the explicit unsigned cast handles negative coordinates without implementation-defined behavior. |
| Both | **Equivalence Check**: After fix, verify that `get_pseudo_random_i32__non_intrusively` with seed S produces the same value as `get_pseudo_random_i32__non_intrusively_with__seed` with the same struct and seed S (since both should now do `srand(seed); rand()`). | Confirms internal consistency between the two "non-intrusive" variants. |

### Test blast radius

**Low.** The test file is empty; all test additions are net-new. No existing assertions are invalidated.

---

## 5. Blast Radius Summary

| Dimension | Assessment |
|-----------|-----------|
| Files requiring changes | 2 (`core/include/random.h`, `core/source/random.c`) + 1 test file |
| Behavior-preserving for current callers? | **Yes** — no current callers exist for either function |
| Phased approach needed? | **No** — both fixes are independent and small; can be done in a single commit |
| De facto contracts invalidated? | **None** — no code depends on the broken behavior |
| Risk of global RNG side effects | Unchanged — both functions already call `srand()`; the fix does not introduce new global-state mutation |
