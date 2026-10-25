# Function Review

## 1. Header

- **Function name** — `get_y_i32_from__vector_3i32F4`
- **File of origin** — `core/include/vectors.h`

## 2. Semantic

Returns the integer-rounded **y** component of a `Vector__3i32F4`. The vector is
stored in fixed-point fractional precision 4 (`i32F4`), so this function extracts
the fractional `y` component and rounds it to the nearest integer index.

## 3. Pre-conditions

1. The parameter `vector__3i32F4` must be a valid, well-formed `Vector__3i32F4`
   value whose `y__i32F4` member is defined.
2. Because the parameter is passed **by value** (not by pointer/reference), no
   nullability or liveness constraints apply to any caller-provided object.

## 4. Post-conditions

1. Returns the y component of `vector__3i32F4`, rounded from fractional precision 4
   (`i32F4`) to an integer index (`Signed_Index__i32`).
2. The result equals `ARITHMETRIC_R_SHIFT(y, 4)`, i.e. the fractional `y` value
   right-shifted by the fractional precision bit size — a rounding-to-nearest
   (symmetric) of the fixed-point representation.

## 5. Correctness Verdict

**Correct**

## 6. Semantic Alignment

The implementation fulfills its semantic intent. It isolates the `y` axis of the
vector (`get_y_i32F4_from__vector_3i32F4` returns `vector.y__i32F4`) and converts it
to an integer index via `i32F4_to__i32`. This is consistent with its sibling
accessors `get_x_i32_from__vector_3i32F4` and `get_z_i32_from__vector_3i32F4`,
which perform the identical extract-then-round pattern for their respective axes.

## 7. Implementation Correctness

- **Type compatibility** — Exact. The parameter is a `Vector__3i32F4`; the y
  component is an `i32F4`. `get_y_i32F4_from__vector_3i32F4` returns that
  `i32F4`, and `i32F4_to__i32` takes an `i32F4` and returns a
  `Signed_Index__i32`. The return type matches the function signature exactly — no
  implicit conversions or truncation beyond the intended fixed-point rounding.
- **Undefined behavior** — None. The fractional-to-integer conversion uses the
  project's defined `ARITHMETIC_R_SHIFT` macro, which normalizes signed right shift
  for both signs and defines bit-wise shift behavior for negatives, avoiding the
  UB that a plain signed right-shift-on-negative would introduce. No broken pointer
  arithmetic, null dereference, or type punning occurs.
- **Validation** — Appropriate. The function takes its argument by value and does
  not dereference any pointer; no input validation is required or expected here.

## 8. Side Effects

**No side effects.** The `vector__3i32F4` parameter is passed by value, so the
function operates on a local copy and leaves any caller object unmodified. It is a
pure read accessor over the vector's `y` component.
