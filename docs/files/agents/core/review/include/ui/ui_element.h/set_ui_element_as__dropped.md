# set_ui_element_as__dropped

**File of origin:** `core/include/ui/ui_element.h`

## Semantic

Clears the `UI_FLAGS__BIT_IS_BEING_HELD` and `UI_FLAGS__BIT_IS_BEING_DRAGGED` flags on the given `UI_Element`, transitioning it to a "dropped" state.

## Pre-conditions

1. `p_ui_element` must be non-null. No null check is performed; this is the caller's responsibility, consistent with all sibling setter functions in `ui_element.h` (e.g., `set_ui_element_as__focused`, `set_ui_element_as__being_dragged`).
2. `p_ui_element` must point to a valid, initialized `UI_Element` struct.

## Post-conditions

1. The `UI_FLAGS__BIT_IS_BEING_HELD` bit (bit 3) in `p_ui_element->ui_flags` is cleared (set to 0).
2. The `UI_FLAGS__BIT_IS_BEING_DRAGGED` bit (bit 4) in `p_ui_element->ui_flags` is cleared (set to 0).
3. All other bits in `p_ui_element->ui_flags` remain unchanged.

## Correctness Verdict

**Correct**

## Semantic Alignment

The implementation correctly fulfills the semantic intent of "setting the UI element as dropped." When an element is dropped, it should no longer be in a "being held" or "being dragged" state, so clearing both of these flags is appropriate. The equivalent function `set_p_ui_flags__u8_as__dropped` in `ui_flags.h` uses identical logic, confirming this is the intended pattern.

## Implementation Correctness

- **Type compatibility:** `ui_flags` is of type `UI_Flags__u16` (`uint16_t`). The flag macros (`UI_FLAGS__BIT_IS_BEING_HELD`, `UI_FLAGS__BIT_IS_BEING_DRAGGED`) expand to `BIT(n)` which is `(1U) << (n)` (type `unsigned int`). The `~` operator applied to `unsigned int` yields `unsigned int`, and the `&` between two `unsigned int` values yields `unsigned int`. The result is then implicitly narrowed to `uint16_t` during the `&=` assignment, which is well-defined behavior in C. The lower 16 bits correctly clear only bits 3 and 4.
- **Operator precedence:** `~` has higher precedence than `&`, so the expression is parsed as `(~UI_FLAGS__BIT_IS_BEING_HELD) & (~UI_FLAGS__BIT_IS_BEING_DRAGGED)`. By De Morgan's law, this is equivalent to `~(UI_FLAGS__BIT_IS_BEING_HELD | UI_FLAGS__BIT_IS_BEING_DRAGGED)`, which correctly produces a mask that clears exactly bits 3 and 4.
- **Undefined behavior:** No undefined behavior. There is no broken pointer arithmetic, no null dereference (under valid pre-conditions), no type punning, and no out-of-bounds access.
- **Validation:** No validation is performed, which is appropriate for this function's role as a simple inline flag setter. Null checking is the caller's responsibility, consistent with all sibling functions in the file.

## Side Effects

- Mutates `p_ui_element->ui_flags` by clearing the `UI_FLAGS__BIT_IS_BEING_HELD` and `UI_FLAGS__BIT_IS_BEING_DRAGGED` bits. All other bits in `ui_flags` are preserved.
- No other side effects.
