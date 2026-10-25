# Function Review: delta_u16__no_overflow

## File of Origin
`core/include/numerics.h` (lines 312-319)

## Semantic
Computes the absolute difference between two `u16` (`uint16_t`) values. The
"no_overflow" qualifier in the name signals that the subtraction is structured
so that the larger operand is always the minuend, guaranteeing the result is
non-negative and within the representable range of `u16` — i.e. no unsigned
underflow/overflow can occur.

## Pre-conditions
1. `first__u16` is a `u16` (`uint16_t`) value; any value in `[0, 65535]` is
   acceptable. There is no constraint on its magnitude relative to the other
   argument.
2. `second__u16` is a `u16` (`uint16_t`) value; any value in `[0, 65535]` is
   acceptable.
3. Both parameters are passed by value, so there are no pointer/null
   preconditions to satisfy. No external state is read.

## Post-conditions
1. The function returns a `u16` equal to `|first__u16 - second__u16|`.
2. The returned value is always in the range `[0, MAX__U16]` (`[0, 65535]`),
   which is exactly the representable range of `u16`. Because the minuend is
   always the larger (or equal) operand, the subtraction never underflows,
   satisfying the "no_overflow" contract.
3. When `first__u16 == second__u16`, the function returns `0`.

## Correctness Verdict
**Correct**

## Semantic Alignment
The implementation fulfills its semantic intent exactly. It branches on
`first__u16 < second__u16` and, in each branch, subtracts the smaller operand
from the larger one:

- `first < second` → returns `second - first` (larger minus smaller)
- `first >= second` → returns `first - second` (larger-or-equal minus smaller)

In both cases the result is the absolute difference, and because the minuend is
always the greater-or-equal value, no unsigned underflow is possible. This is
consistent with the sibling functions `delta_u8__no_overflow` and
`delta_u32__no_overflow`, which use the identical structure. There is no
semantic drift and no bug.

## Implementation Correctness
- **Type compatibility:** `u16` is `typedef uint16_t u16`. The operands of the
  subtraction are `uint16_t`, which undergo integer promotion to `int` for the
  arithmetic; the resulting `int` is then implicitly converted back to the
  return type `u16`. Because the computed value is guaranteed to lie in
  `[0, 65535]`, this conversion is safe and lossless — no truncation occurs.
  This matches the established pattern of the sibling `delta_*` functions, so it
  is consistent with the codebase style.
- **Undefined behavior:** None. There are no pointers, no null dereferences, no
  pointer arithmetic, no type punning, and no out-of-bounds array access. The
  subtraction is always valid unsigned arithmetic (larger minus smaller).
- **Validation:** No validation is required or appropriate here. The function
  accepts arbitrary `u16` values and computes a well-defined result for all of
  them. Validation of any domain-specific constraints (e.g. whether a delta
  exceeds an expected magnitude) is the caller's responsibility, consistent with
  the other `delta_*` / `subtract_*` helpers in this header.

## Side Effects
No side effects. This is a pure function: it takes two value parameters and
returns a computed `u16` without modifying memory, performing I/O, or invoking
other functions.
