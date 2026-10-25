# add_u16__no_overflow

**File of origin:** `core/include/numerics.h`

## Semantic

Checks whether adding two u16 values would overflow, and if not, stores the sum in the output pointer.

## Pre-conditions

1. `p_out__u16` must be a non-null pointer to a writable u16 location.
2. `first__u16` and `second__u16` are any u16 values (0 to 65535).

## Post-conditions

1. If `first__u16 + second__u16` would overflow (i.e., exceed `UINT16_MAX`), the function returns `true` and `*p_out__u16` is left unmodified.
2. If no overflow would occur, the function writes `first__u16 + second__u16` to `*p_out__u16` and returns `false`.

## Correctness Verdict

Correct

## Semantic Alignment

The function correctly implements overflow-safe addition of two u16 values. The overflow check `UINT16_MAX - first__u16 < second__u16` is mathematically equivalent to checking whether `first__u16 + second__u16 > UINT16_MAX`, which is the correct condition for unsigned addition overflow. When overflow is detected, the function returns `true` without touching the output pointer, preserving its prior value. When no overflow occurs, the sum is computed and stored correctly. The implementation matches the semantic intent of the function name.

## Implementation Correctness

**Type compatibility** — `UINT16_MAX` is a standard macro from `<stdint.h>` (included at the top of the file) and evaluates to 65535, which fits in a u16. The arithmetic `UINT16_MAX - first__u16` is performed in u16 arithmetic (since both operands are u16), and the comparison with `second__u16` is between u16 values. No implicit conversions or truncation occur.

**Undefined behavior** — no pointer arithmetic, no null dereference (caller must ensure `p_out__u16` is non-null), no type punning, no out-of-bounds access. The subtraction `UINT16_MAX - first__u16` cannot underflow because `first__u16` is a u16 and `UINT16_MAX` is the maximum value of u16, so `UINT16_MAX >= first__u16` always holds.

**Validation** — no validation of `p_out__u16` for null is performed. This is appropriate for a low-level inline utility function; the caller is responsible for ensuring the pointer is valid.

## Side Effects

Writes to `*p_out__u16` when no overflow occurs. When overflow is detected, no write occurs. The function's return value indicates whether overflow was detected (`true`) or not (`false`).