# is_ui_flags__being_held

**File of origin:** `core/include/ui/ui_flags.h`

## Semantic

Checks whether the `UI_FLAGS__BIT_IS_BEING_HELD` bit is set in the given UI flags value, returning `true` if the UI element is currently being held (e.g., by a cursor or touch input).

## Pre-conditions

1. `ui_flags__u8` is a valid `UI_Flags__u16` value (a 16-bit unsigned integer). No further constraints are required; the function accepts any bit pattern.

## Post-conditions

1. Returns `true` if the `UI_FLAGS__BIT_IS_BEING_HELD` bit (bit 3, value `0x0008`) is set in `ui_flags__u8`.
2. Returns `false` otherwise.
3. The input `ui_flags__u8` is not modified; the function is a pure read operation.

## Correctness Verdict

**Correct**

## Semantic Alignment

The implementation correctly checks the `UI_FLAGS__BIT_IS_BEING_HELD` flag using a bitwise AND against `BIT(3)` (defined in `defines.h` as `UI_FLAGS__BIT_IS_BEING_HELD`). The result is cast to `bool`, which yields `true` for any non-zero value and `false` for zero. This matches the semantic intent of querying whether the "being held" state is active.

## Implementation Correctness

- **Type compatibility:** The parameter `ui_flags__u8` is typed as `UI_Flags__u16` (which is `uint16_t`), and `UI_FLAGS__BIT_IS_BEING_HELD` is `BIT(3)` which expands to `((1U) << (3))`, a `u32` value of `8`. The bitwise AND between a `u16` and a `u32` promotes the `u16` to `u32`, which is safe and well-defined. The cast to `bool` is valid.
- **Undefined behavior:** No undefined behavior. There is no pointer dereference, no array access, and no out-of-bounds access.
- **Validation:** The function is a simple bit-query function. No validation is needed for its role; it is the caller's responsibility to pass a meaningful flags value.

## Side Effects

No side effects. The function is a pure read operation that does not modify any state.
