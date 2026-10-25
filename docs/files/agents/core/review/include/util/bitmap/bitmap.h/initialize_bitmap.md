# initialize_bitmap

**File of origin:** `core/source/util/bitmap/bitmap.c`

## Semantic

Resets (initializes) a raw bitmap buffer by setting all of its bytes to either all-1s (`0xff`) or all-0s (`0x00`), depending on the `state` parameter. This is Lavender-style initialization — it cleans up a bitmap to its initial conditions so it can be returned to a free pool or reused. It is NOT RAII-style resource acquisition.

## Pre-conditions

1. `p_bitmap` must point to a valid, writable memory region of at least `size_of__bitmap` bytes.
2. `size_of__bitmap` must accurately reflect the size (in bytes) of the bitmap buffer pointed to by `p_bitmap`.
3. `state` is a boolean: when `true`, all bits in the bitmap are set to 1; when `false`, all bits are set to 0.

## Post-conditions

1. After return, all `size_of__bitmap` bytes starting at `p_bitmap` are set to `0xff` if `state` is `true`, or `0x00` if `state` is `false`.
2. The bitmap buffer is in a fully initialized state — every bit is uniformly set or cleared.

## Correctness Verdict

Correct

## Semantic Alignment

This function performs Lavender-style initialization (resetting a bitmap to its initial conditions for pool reuse), not RAII-style resource acquisition. The implementation correctly delegates to `memset`, selecting `0xff` or `0x00` based on the `state` parameter. The computation matches the semantic intent: uniformly setting all bytes in the buffer to the desired bit pattern.

## Implementation Correctness

- **Type compatibility:** `p_bitmap` is `u8 *`, which is compatible with `memset`'s `void *` parameter. The ternary expression `state ? 0xff : 0x00` yields an `int`, which matches `memset`'s second parameter type exactly. `size_of__bitmap` is `Quantity__u32` (uint32_t), which is implicitly promoted to `size_t` for `memset` — no truncation risk on typical platforms.
- **No undefined behavior:** No null dereference (caller must provide a valid pointer), no out-of-bounds access (caller must ensure the buffer is large enough), no broken pointer arithmetic. The function is a thin wrapper around `memset`.
- **Validation:** The function does not validate `p_bitmap` for null. This is appropriate for a low-level utility function — null/bounds checking is the caller's responsibility. This is consistent with the codebase pattern where debug-only bounds checks are present in other bitmap functions (e.g., `is_bit_set_in__bitmap`, `set_bit_in__bitmap`) but not in this simple initialization wrapper.

## Side Effects

- Modifies the memory pointed to by `p_bitmap`: writes `size_of__bitmap` bytes, each set to `0xff` (if `state` is `true`) or `0x00` (if `state` is `false`).
- No other observable side effects.
