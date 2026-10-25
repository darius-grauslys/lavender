# add_u32__no_overflow

**File of origin:** `core/include/numerics.h`

## Semantic

Safely adds two `u32` values, detecting unsigned integer overflow. Returns `true` if the addition would overflow (leaving the output pointer unmodified), and `false` if the addition succeeds (storing the result in the output pointer).

## Pre-conditions

1. `p_out__u32` must be a valid, non-null pointer to a `u32` where the result will be written on success.
2. `first__u32` and `second__u32` are arbitrary `u32` values with no additional constraints.

## Post-conditions

1. If the function returns `true` (overflow detected): `*p_out__u32` is **not** written; the value at `p_out__u32` remains unchanged.
2. If the function returns `false` (no overflow): `*p_out__u32` is set to `first__u32 + second__u32`, which is guaranteed to be in the range `[0, UINT32_MAX]`.
3. The return value is `true` if and only if `first__u32 + second__u32` would exceed `UINT32_MAX`.

## Correctness Verdict

**Correct**

## Semantic Alignment

The implementation correctly fulfills its semantic intent. The overflow check `UINT32_MAX - first__u32 < second__u32` is a standard, well-known idiom for detecting unsigned addition overflow without itself overflowing. It is algebraically equivalent to checking whether `first__u32 + second__u32 > UINT32_MAX`, but rearranged to avoid performing the potentially overflowing addition.

Edge cases verified:
- When `first__u32 == 0`: `UINT32_MAX - 0 < second__u32` is always false (since `second__u32 <= UINT32_MAX`), so no overflow is reported — correct, as `0 + any_u32` cannot overflow.
- When `first__u32 == UINT32_MAX` and `second__u32 > 0`: `UINT32_MAX - UINT32_MAX < second__u32` becomes `0 < second__u32`, which is true, so overflow is correctly detected.
- When `first__u32 == UINT32_MAX` and `second__u32 == 0`: `0 < 0` is false, so no overflow — correct, as `UINT32_MAX + 0` does not overflow.

The function is consistent with the sibling functions `add_u8__no_overflow`, `add_u16__no_overflow`, and `add_u64__no_overflow`, which use the identical pattern with their respective `UINTn_MAX` constants.

## Implementation Correctness

- **Type compatibility:** All parameter types (`u32`, `u32`, `u32 *`) match the expected types exactly. No implicit conversions or truncation occur.
- **Undefined behavior:** No undefined behavior is present. The subtraction `UINT32_MAX - first__u32` cannot underflow because `first__u32` is a `u32` and thus `first__u32 <= UINT32_MAX`, ensuring the subtraction result is in `[0, UINT32_MAX]`. The comparison and assignment are well-defined. The only potential issue is a null `p_out__u32` pointer dereference on the success path, but this is a caller responsibility per the pre-conditions.
- **Validation:** The function does not validate that `p_out__u32` is non-null, which is appropriate for a `static inline` utility function — null-checking is the caller's responsibility. This is consistent with the codebase's performance-oriented style for inline utilities.

## Side Effects

- On overflow (return `true`): No side effects. `*p_out__u32` is not modified.
- On success (return `false`): `*p_out__u32` is written with the sum `first__u32 + second__u32`.
