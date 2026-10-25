# Planning: numerics.h — Incorrect Modules

**Review source:** `agents/core/review/include/numerics.h/incorrect_modules.md`

**Source files reviewed (read-only):**
- `core/include/numerics.h`
- `core/include/defines.h`
- `tests/sdl/source/test_suite_sdl_numerics.c`

---

## 1. Problem Identification

Eight functions in `core/include/numerics.h` were flagged as **Incorrect**. They fall into three defect classes:

### A. Inverted Minimum-Clamp Comparison (Boundary Condition violation)

- **`subtract_u8__clamped`** (line 240): The post-underflow clamp check uses `if (subtraction > min__u8) return min__u8;`. This is inverted — it clamps values *above* the minimum and passes through values *below* it. The correct comparison is `<`.
- **`subtract_u16__clamped`** (line 255): Identical inverted-comparison defect (`subtraction > min__u16`).
- **`subtract_u32__clamped`** (line 270): Identical inverted-comparison defect (`subtraction > min__u32`).

The `Postcondition` "result ≥ min" is violated. The `Precondition` (underflow guard) is correct; only the secondary clamp comparison is wrong. Sibling functions `r_bitshift_u8__clamped`, `r_bitshift_u16__clamped`, `r_bitshift_u32__clamped`, and `clamp__u8` all correctly use `<` for minimum clamping, confirming the intended convention.

### B. Insufficient Overflow Detection in Clamped Multiplication (Conservative invariant violated)

- **`multiply_u8__clamped`** (lines 379–380): Overflow guard is `(MAX__U8>>1) < first || (MAX__U8>>1) < second`. This is neither `Conservative` nor sufficient: it rejects valid products where one operand > 127 but the product still fits (e.g., 128×1=128), and it misses overflows where both operands ≤ 127 but their product exceeds 255 (e.g., 127×127=16129 wraps to 25 in u8).
- **`multiply_u16__clamped`** (lines 395–396): Same pattern with `MAX__U16>>1`. Misses e.g., 300×300=90000 which wraps in u16.
- **`multiply_u32__clamped`** (lines 411–412): Same pattern with `MAX__U32>>1`. Misses e.g., 0x10000×0x10000 which wraps to 0 in u32.

The `Postcondition` "return value ≤ clamp" is violated in the missed-overflow cases because the truncated product can fall below the clamp.

### C. Mode Confusion — Return Type Mismatch (State Desync)

- **`divide_into__i32F4`** (line 575): Declared return type is `i32F8` but the body calls `i32_to__i32F4(p)` (4-bit fractional shift), producing a value with only 4-bit fractional precision. The result is off by a factor of 2⁴=16 relative to a true `i32F8` representation. This is a `State Desync` between the declared type contract and the actual precision of the computation.

### D. Surface-form Leakage — Semantic Type Mismatch

- **`is_quantity_u32__out_of_bounds`** (line 65): Parameter is typed `Index__u32` but should be `Quantity__u32`. Both are `uint32_t` at the binary level, so no runtime bug exists. However, the codebase distinguishes `Index__uN` (position in array/pool) from `Quantity__uN` (count/size) as distinct semantic types. Using `Index__u32` in a function named `is_quantity_*` is a `Surface-form leakage`: the syntactic surface (the type name) does not match the semantic role, inviting misuse. The same pattern exists in `is_quantity_u8__out_of_bounds` and `is_quantity_u16__out_of_bounds`.

---

## 2. Impact Assessment

All eight functions are `static inline` in `core/include/numerics.h`, meaning they are available to any translation unit that includes this header (directly or transitively via `defines.h`). The impact is bounded by which callers actually invoke these functions.

### A. Inverted Clamp (subtract_*__clamped)

**Affected semantics:** Any caller relying on `subtract_uN__clamped(a, b, min)` to guarantee "result ≥ min" currently receives the *opposite*: values above `min` are clamped down to `min`, and values below `min` pass through unclamped. If any caller has adapted its logic to compensate for this inverted behavior (e.g., passing `min` as the *maximum* bound it actually wants enforced), correcting the comparison will break that compensation.

**Likely callers:** Inventory quantity arithmetic (item stack counts), buffer/queue position tracking, resource budget subtraction. The `Quantity__u8` fields in `Item_Stack`, `Inventory`, and `Sprite_Animation` in `defines.h` suggest inventory and rendering code may use these for clamped decrements.

**Blast radius if no caller has adapted:** Low — the fix restores the documented contract and callers that were passing `min=0` (the most common case) are unaffected since `subtraction > 0` and `subtraction < 0` are equivalent for unsigned types when min is 0. Callers passing a non-zero `min` value are the ones affected.

### B. Insufficient Overflow (multiply_*__clamped)

**Affected semantics:** Any caller relying on `multiply_uN__clamped(a, b, clamp)` to never return a wrapped/truncated product currently receives incorrect results for operand pairs where both operands ≤ MAX/2 but the product exceeds MAX. The returned value is a silent wraparound, not the clamp.

**Likely callers:** Size calculations (width × height for buffer allocation), quantity multiplication (items × stacks), scaling factors in rendering or physics. The `Quantity__u32` fields in `Serialization_Pool`, `Hitbox_AABB_Manager`, and `Sprite_Manager` suggest pool sizing and graphics code may use these.

**Blast radius:** Medium. Callers that only multiply small values (both well below MAX/4) are unaffected. Callers multiplying values in the range (1, MAX/2] × (1, MAX/2] where the product exceeds MAX are affected. The overly-conservative rejection of operands > MAX/2 also means some valid multiplications currently return `clamp` unnecessarily — correcting this changes behavior in that direction too.

### C. Mode Confusion (divide_into__i32F4)

**Affected semantics:** Any caller using `divide_into__i32F4(p, q)` and treating the result as `i32F8` (8-bit fractional) is receiving a value with only 4-bit fractional precision — off by a factor of 16. If callers have compensated by shifting the result right by 4 bits before using it as i32F8, the fix (changing return type to i32F4 or changing the internal conversion to i32_to__i32F8) will break that compensation.

**Likely callers:** Fixed-point arithmetic in camera, physics, or pathfinding code. The `Camera` struct uses `i32F20` fields; `Path` uses `i32F4`. The function's name suggests it was intended for 4-bit precision division but was typed as i32F8 in error.

**Blast radius:** Low-Medium. If the function is rarely called (the name is specific to F4 precision), impact is contained. If callers have compensated with manual shifts, the fix requires updating those call sites.

### D. Type Mismatch (is_quantity_u32__out_of_bounds)

**Affected semantics:** No runtime behavior change — `Index__u32` and `Quantity__u32` are both `uint32_t`. The fix is purely a type annotation correction. No caller behavior changes. However, if any static analysis or lint tooling relies on the type name to enforce semantic discipline, correcting the type strengthens the `Invariant` that quantity-checking functions accept quantity-typed arguments.

**Blast radius:** Low. Purely a type-name correction with no binary-level change.

---

## 3. Resolution Assessment

### Fix A: Inverted Clamp (subtract_u8/u16/u32__clamped)

**Change:** In each of the three functions, change the comparison operator in the post-underflow clamp check from `>` to `<`:

```c
// BEFORE (incorrect):
if (subtraction > min__uN) { return min__uN; }

// AFTER (correct):
if (subtraction < min__uN) { return min__uN; }
```

**Callers:** Audit all call sites. Callers passing `min=0` are unaffected (unsigned subtraction result is always ≥ 0, so `< 0` is never true). Callers passing a non-zero `min` need verification that they were not compensating for the inverted behavior. If compensation exists, remove it.

**Tests:** Add `Property Based Testing` cases:
- For all valid (a, b, min) where a ≥ b: assert result == max(min, a - b).
- For all valid (a, b, min) where a < b: assert result == min.
- `Boundary Condition` cases: a==b (result=0), min==0, min==MAX.

### Fix B: Insufficient Overflow (multiply_u8/u16/u32__clamped)

**Change:** Replace the `MAX>>1` heuristic with a correct overflow check using division, or use a wider intermediate type:

```c
// Option 1: Division-based check (no wider type needed)
u8 multiply_u8__clamped(u8 a, u8 b, u8 clamp) {
    if (a != 0 && b > MAX__U8 / a) { return clamp; }
    u8 multiple = a * b;  // safe: no overflow
    if (multiple > clamp) { return clamp; }
    return multiple;
}

// Option 2: Wider intermediate (simpler, slightly more code)
u8 multiply_u8__clamped(u8 a, u8 b, u8 clamp) {
    u16 multiple = (u16)a * (u16)b;  // no overflow in wider type
    if (multiple > clamp) { return clamp; }
    return (u8)multiple;
}
```

For `multiply_u32__clamped`, Option 2 requires `u64` intermediate. Option 1 (division check) avoids this and is preferred for the u32 variant to avoid 64-bit operations on constrained platforms.

**Callers:** Callers that were receiving wrapped values for "both operands ≤ MAX/2" inputs will now correctly receive `clamp`. Callers that were receiving `clamp` for valid products where one operand > MAX/2 (overly-conservative rejection) will now receive the actual product. Both directions of behavior change need verification at call sites.

**Tests:**
- `Property Based Testing`: for all (a, b, clamp), assert result ≤ clamp AND (if true product ≤ clamp, result == true product).
- `Fuzzing` with random u8/u16/u32 operand pairs to find any residual overflow.
- `Equivalence Check` against a reference implementation using wider arithmetic.

### Fix C: Mode Confusion (divide_into__i32F4)

**Change (preferred):** Change the return type from `i32F8` to `i32F4` to match the actual precision of the computation:

```c
// BEFORE (incorrect):
static inline i32F8 divide_into__i32F4(i32 p, i32 q) {
    return i32_to__i32F4(p) / q;
}

// AFTER (correct):
static inline i32F4 divide_into__i32F4(i32 p, i32 q) {
    return i32_to__i32F4(p) / q;
}
```

**Alternative:** If callers genuinely need i32F8 precision, change the body to `return i32_to__i32F8(p) / q;` — but this changes the function's precision semantics and contradicts its name.

**Callers:** Any caller storing the result in an `i32F8` variable will get an implicit conversion (both are `int32_t`) so no compile error, but the semantic precision changes. Audit call sites to determine whether they expect F4 or F8 precision. If callers were compensating with a manual >> 4 shift, remove that compensation.

**Tests:**
- `Round Trip Check`: `i32F4_to__i32(divide_into__i32F4(x, 1))` should equal `x` for representable x.
- `Equivalence Check`: for small values where both F4 and F8 are exact, verify the result matches the mathematical quotient scaled to the correct precision.

### Fix D: Type Mismatch (is_quantity_u32__out_of_bounds)

**Change:** Change parameter type from `Index__u32` to `Quantity__u32`:

```c
// BEFORE:
bool is_quantity_u32__out_of_bounds(Index__u32 quantity__u32);
// AFTER:
bool is_quantity_u32__out_of_bounds(Quantity__u32 quantity__u32);
```

Also apply the same fix to `is_quantity_u8__out_of_bounds` and `is_quantity_u16__out_of_bounds` (same pattern, flagged in review context).

**Callers:** No binary-level change. Callers passing `uint32_t` values will continue to compile without modification since both types are `uint32_t`. No caller updates required.

**Tests:** No new tests needed — the comparison logic is unchanged. A `Lint Gate` rule could be added to prevent future Index/Quantity type confusion.

---

## 4. Test Verification Checklist

**Existing test coverage:** `tests/sdl/source/test_suite_sdl_numerics.c` is an empty stub (`DEFINE_SUITE(sdl_numerics, END_TESTS)` with a `#warning` to add tests). No existing assertions will be invalidated by the fixes.

**New tests required:**

| Function | Test Strategy | Rationale |
|----------|--------------|-----------|
| `subtract_u8/u16/u32__clamped` | `Property Based Testing` + `Boundary Condition` cases | Verify postcondition "result ≥ min" for exhaustive/random inputs. Boundary: a==b, min==0, min==MAX, a<b. |
| `multiply_u8/u16/u32__clamped` | `Property Based Testing` + `Fuzzing` + `Equivalence Check` | Verify postcondition "result ≤ clamp" and "result == true product when product ≤ clamp". Fuzz with random operands. Equivalence check against wider-precision reference. |
| `divide_into__i32F4` | `Round Trip Check` + `Equivalence Check` | Verify i32F4_to__i32(divide_into__i32F4(x,1)) == x. Verify quotient matches expected F4-scaled value. |
| `is_quantity_u32__out_of_bounds` | None (type annotation only) | No behavior change. |

**Blast radius for tests:** Low. The test suite is currently empty, so all test work is additive. No existing assertions are invalidated.

---

## 5. Blast Radius Summary

| Metric | Assessment |
|--------|-----------|
| Files requiring changes | 1 (`core/include/numerics.h`) + test file |
| Behavior-preserving for current callers? | **Partially.** Callers passing `min=0` to subtract functions are unaffected. Callers of multiply functions with small operands are unaffected. Callers relying on the *broken* behavior (compensating for inverted clamp or precision mismatch) will break. |
| Phased approach needed? | **Yes, recommended.** Phase 1: Fix type annotation (Fix D) — zero risk. Phase 2: Fix inverted clamp (Fix A) — audit callers with non-zero min. Phase 3: Fix overflow detection (Fix B) — widest behavioral change, audit all multiply call sites. Phase 4: Fix precision mismatch (Fix C) — audit fixed-point callers. |
| De facto contracts invalidated? | **Yes, potentially.** If any caller has adapted to the inverted clamp (treating `min` param as a max) or the precision mismatch (manually rescaling), those adaptations become incorrect after the fix. These must be identified and removed during implementation. |
