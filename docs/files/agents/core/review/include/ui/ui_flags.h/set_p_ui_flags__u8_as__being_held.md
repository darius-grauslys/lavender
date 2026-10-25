# set_p_ui_flags__u8_as__being_held

**File of origin:** `core/include/ui/ui_flags.h`

## Semantic

Sets the `UI_FLAGS__BIT_IS_BEING_HELD` bit (bit 3) in the `UI_Flags__u16` value pointed to by the parameter, marking the UI element as currently being held (e.g., by mouse or touch input).

## Pre-conditions

1. `p_ui_flags__u8` must be a valid, non-null pointer to a `UI_Flags__u16` (i.e., `uint16_t`) value.
2. The caller is responsible for ensuring the pointer is valid; no null-check is performed (consistent with the pattern used by all sibling setter functions in this header).

## Post-conditions

1. The `UI_FLAGS__BIT_IS_BEING_HELD` bit (bit 3) in the `UI_Flags__u16` value pointed to by `p_ui_flags__u8` will be set to 1.
2. All other bits in the value remain unchanged (the operation is a bitwise OR, which only sets bits).

## Correctness Verdict

**Correct**

## Semantic Alignment

The implementation correctly sets the "being held" flag by OR-ing the `UI_FLAGS__BIT_IS_BEING_HELD` bitmask (`BIT(3)` = `(1U) << 3` = 8) into the value pointed to by the parameter. The function name, parameter naming, and implementation all align with the semantic intent of marking a UI element as being held. This is consistent with the sibling functions in the same header (e.g., `set_p_ui_flags__u8_as__allocated`, `set_p_ui_flags__u8_as__being_dragged`, `set_p_ui_flags__u8_as__enabled`), which all follow the same pattern of OR-ing a single bit flag.

## Implementation Correctness

- **Type compatibility:** The parameter `p_ui_flags__u8` is of type `UI_Flags__u16 *` (which is `uint16_t *`). The macro `UI_FLAGS__BIT_IS_BEING_HELD` expands to `BIT(3)` = `((1U) << 3)` = `8`, an unsigned int value. The expression `*p_ui_flags__u8 |= UI_FLAGS__BIT_IS_BEING_HELD` performs a bitwise OR between a `uint16_t` lvalue and an `unsigned int` rvalue. The value 8 fits within `uint16_t`, so no truncation occurs. The compound assignment `|=` handles the type promotion/demotion correctly.
- **Undefined behavior:** No pointer arithmetic, type punning, or out-of-bounds access occurs. The function assumes the pointer is non-null (as do all sibling functions in this header). Dereferencing a null pointer would be undefined behavior, but this is the caller's responsibility.
- **Validation:** No validation is performed, which is appropriate for an inline setter function of this role. The pattern is consistent across all setter functions in this header file.

**Note on naming convention:** The parameter is named `p_ui_flags__u8`, suggesting an 8-bit value, but the actual type is `UI_Flags__u16` (a 16-bit unsigned integer). This naming inconsistency is a pre-existing convention across all functions in this header file (every setter and checker uses `p_ui_flags__u8` or `ui_flags__u8` as the parameter name despite the type being 16-bit). This is not a bug in this specific function but a file-wide naming convention that may warrant future cleanup.

## Side Effects

- Mutates the `UI_Flags__u16` value pointed to by `p_ui_flags__u8`, setting the `UI_FLAGS__BIT_IS_BEING_HELD` bit (bit 3).
- No other side effects. No global state is modified. No memory is allocated or freed.
