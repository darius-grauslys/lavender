# is_index_u16__out_of_bounds

**File of origin:** `core/include/numerics.h`

## Semantic

Checks whether a given 16-bit index is "out of bounds" by comparing it against the sentinel `INDEX__UNKNOWN__u16`, which represents an invalid or uninitialized index value.

## Pre-conditions

1. `index__u16` is a valid `uint16_t` value (any value in the range 0–65535 is accepted; no pointer dereferencing or memory access is required).

## Post-conditions

1. Returns `true` if `index__u16` equals `INDEX__UNKNOWN__u16` (i.e., `(uint16_t)(-1)` = 65535), indicating the index is out of bounds / invalid.
2. Returns `false` otherwise, indicating the index is a valid, in-bounds value.

## Correctness Verdict

**Correct**

## Semantic Alignment

The implementation directly and correctly fulfills the semantic intent. The function compares the provided index against the sentinel value `INDEX__UNKNOWN__u16` and returns a boolean indicating whether the index is the invalid sentinel. There is no drift between the intended behavior and the implementation — the comparison is straightforward and matches the pattern used by the sibling functions `is_index_u8__out_of_bounds` and `is_index_u32__out_of_bounds`.

## Implementation Correctness

- **Type compatibility:** The parameter `index__u16` is of type `Index__u16` (which is `typedef`'d to `uint16_t`), and `INDEX__UNKNOWN__u16` is defined as `(uint16_t)(-1)`. Both operands of the `==` comparison are `uint16_t`, so there is no implicit conversion, truncation, or type mismatch.
- **Undefined behavior:** None. The function performs a simple integer comparison with no pointer arithmetic, no dereferences, and no out-of-bounds array access.
- **Validation:** The function's sole purpose is validation (checking against a sentinel), which is appropriate for its role. No additional validation is required.

## Side Effects

No side effects. This is a pure function: it reads its input parameter, performs a comparison, and returns a boolean result without modifying any state.
