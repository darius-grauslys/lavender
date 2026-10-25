# Function Review: `vector_3i32F4_to__vector_3i32F20`

## 1. Header

- **Function name:** `vector_3i32F4_to__vector_3i32F20`
- **File of origin:** `core/include/vectors.h` (lines 287–294)

## 2. Semantic

Converts a 3-component fixed-point vector with 4-bit fractional precision (`Vector__3i32F4`) into a 3-component fixed-point vector with 20-bit fractional precision (`Vector__3i32F20`) by left-shifting each component by 16 bits (20 − 4 = 16).

## 3. Pre-conditions

1. The `vector` parameter is passed by value; no null-check or validity check is required.
2. Each field (`x__i32F4`, `y__i32F4`, `z__i32F4`) must be a valid `i32F4` value (32-bit signed integer with 4 fractional bits). No special range constraints are enforced by the function.
3. The caller is responsible for ensuring that the left-shift by 16 bits does not cause overflow. Since `i32F4` and `i32F20` are both `int32_t`, shifting left by 16 bits preserves the integer portion of the value but discards the 4-bit fractional portion (it is moved to the lower 20 bits of the 20-bit fractional field). This is by design — the fractional precision is increased, not the value range.

## 4. Post-conditions

1. The function returns a `Vector__3i32F20` struct.
2. All three fields of the returned struct are populated:
   - `.x__i32F20` = `i32F4_to__i32F20(vector.x__i32F4)` (i.e., `vector.x__i32F4 << 16`)
   - `.y__i32F20` = `i32F4_to__i32F20(vector.y__i32F4)` (i.e., `vector.y__i32F4 << 16`)
   - `.z__i32F20` = `i32F4_to__i32F20(vector.z__i32F4)` (i.e., `vector.z__i32F4 << 16`)
3. The input `vector` is not modified (passed by value).

## 5. Correctness Verdict

**Correct**

## 6. Semantic Alignment

The implementation fully fulfills its semantic intent. The function correctly converts each component from 4-bit fixed-point precision to 20-bit fixed-point precision using the `i32F4_to__i32F20` helper, which left-shifts by `FRACTIONAL_PERCISION_16__BIT_SIZE` (16 bits). This is the mathematically correct conversion since 20 − 4 = 16. All three struct fields (`x`, `y`, `z`) are assigned in the correct order with no fields omitted or reordered.

The struct initializer `(Vector__3i32F20){...}` properly initializes all three fields of the `Vector__3i32F20` struct, which is defined as:
```c
typedef struct Vector__3i32F20_t {
    i32F20 x__i32F20, y__i32F20, z__i32F20;
} Vector__3i32F20;
```

## 7. Implementation Correctness

- **Type compatibility:** The parameter type `Vector__3i32F4` is passed by value. The return type `Vector__3i32F20` is constructed via a compound literal. The conversion function `i32F4_to__i32F20` accepts `i32F4` (typedef for `int32_t`) and returns `Signed_Index__i32` (typedef for `int32_t`), which is identical to `i32F20` (also `int32_t`). No implicit conversions or truncation occur.
- **Undefined behavior:** No undefined behavior. The `ARITHMETRIC_L_SHIFT` macro used by `i32F4_to__i32F20` is defined as `((i32)((u32)(x) << (n)))`, which safely performs the left shift by casting to unsigned first, avoiding the undefined behavior of left-shifting a signed negative value. No null pointer dereference, no out-of-bounds access.
- **Validation:** No validation is needed for this function's role. It is a pure conversion utility that operates on a value parameter. Validation of vector values (e.g., bounds checking) is the responsibility of the caller, consistent with the pattern used by all other conversion functions in `vectors.h`.

## 8. Side Effects

No side effects. The function is a pure function: it takes a `Vector__3i32F4` by value, computes a new `Vector__3i32F20`, and returns it. No global state is read or modified, no memory is allocated, and no I/O occurs.
