# get_vector__3i32F4_using__i32

**File of origin:** `core/include/vectors.h`

## Semantic

Constructs a `Vector__3i32F4` from whole-number (`i32`) inputs by converting each component to 4-bit fixed-point representation (i32F4). The function name implies it accepts raw integer values and applies the fixed-point scaling (left shift by `FRACTIONAL_PERCISION_4__BIT_SIZE`).

## Pre-conditions

1. The caller passes three integer values representing whole-number coordinates.
2. The values should be in the range representable by `i32F4` after left-shifting by 4 bits (i.e., the caller must ensure no overflow occurs after the shift).

## Post-conditions

1. Returns a `Vector__3i32F4` where each component has been scaled by `2^4` (left-shifted by `FRACTIONAL_PERCISION_4__BIT_SIZE` = 4) to convert from whole-number representation to i32F4 fixed-point.

## Correctness Verdict

**Incorrect**

## Semantic Alignment

The implementation does **not** fulfill the semantic intent of the function name `get_vector__3i32F4_using__i32`.

**Bug 1 — Type mismatch in parameters:** The function name explicitly states it accepts `i32` (whole integer) values and converts them to `i32F4`. However, the parameters are declared as `i32F4` (which is `int32_t` used as fixed-point). This means:

- If a caller passes raw `i32` values (e.g., `5`), the compiler may implicitly convert them to `i32F4`, but the semantic intent is ambiguous.
- If a caller passes values that are already in `i32F4` format (e.g., `i32_to__i32F4(5)` = `80`), the function would shift them again, producing `80 << 4 = 1280`, which is `5 * 256` — a double conversion error.

The correct parameter type should be `Signed_Index__i32` (which is `int32_t`), matching the pattern used by the dedicated conversion function `i32_to__i32F4`:

```c
i32F4 i32_to__i32F4(Signed_Index__i32 x) {
    return ARITHMETRIC_L_SHIFT(x, FRACTIONAL_PERCISION_4__BIT_SIZE);
}
```

**Bug 2 — Undefined behavior with left shift on signed integers:** The expression `x << FRACTIONAL_PERCISION_4__BIT_SIZE` operates directly on `i32F4` (signed `int32_t`). Per the C standard, left-shifting a negative signed integer is undefined behavior. The codebase already provides the correct macro `ARITHMETRIC_L_SHIFT` (defined in `defines_weak.h`) which casts to `u32` before shifting and back to `i32` afterward, avoiding this UB. The function should use `i32_to__i32F4()` or `ARITHMETRIC_L_SHIFT` instead of the raw `<<` operator.

The correct implementation should be:

```c
static inline
Vector__3i32F4 get_vector__3i32F4_using__i32(
        Signed_Index__i32 x,
        Signed_Index__i32 y,
        Signed_Index__i32 z) {
    return (Vector__3i32F4) {
        i32_to__i32F4(x),
        i32_to__i32F4(y),
        i32_to__i32F4(z)
    };
}
```

## Implementation Correctness

- **Type compatibility:** Parameters are typed `i32F4` but should be `Signed_Index__i32` to match the semantic intent. This is a type mismatch that could lead to double-conversion bugs.
- **Undefined behavior:** Direct left shift (`<<`) on signed `int32_t` is UB when the value is negative. The codebase's `ARITHMETRIC_L_SHIFT` macro and `i32_to__i32F4()` function exist specifically to avoid this.
- **Validation:** No validation is needed for this function's role — it is a pure conversion constructor. The responsibility for ensuring values fit within the target range lies with the caller, consistent with other vector construction functions in this file.

## Side Effects

No side effects. This is a pure function that returns a new `Vector__3i32F4` value without modifying any state.
