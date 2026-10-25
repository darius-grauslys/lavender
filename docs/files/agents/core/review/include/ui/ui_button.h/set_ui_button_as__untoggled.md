# set_ui_button_as__untoggled

**File of origin:** `core/include/ui/ui_button.h`

## Semantic

Clears the `UI_BUTTON_FLAGS__BIT_IS_TOGGLED` bit in the `ui_button_flags` field of the provided `UI_Element`, marking the button as untoggled.

## Pre-conditions

1. `p_ui_button` must be a non-null pointer to a valid `UI_Element` struct.
2. The `ui_button_flags` field must be a valid `UI_Button_Flags__u8` (uint8_t) value.

## Post-conditions

1. The `UI_BUTTON_FLAGS__BIT_IS_TOGGLED` bit (bit 1) in `p_ui_button->ui_button_flags` is cleared (set to 0).
2. All other bits in `p_ui_button->ui_button_flags` are preserved unchanged.
3. After return, `is_ui_button__toggled(p_ui_button)` will return `false`.

## Correctness Verdict

Correct

## Semantic Alignment

The implementation correctly fulfills its semantic intent. The expression `p_ui_button->ui_button_flags &= ~UI_BUTTON_FLAGS__BIT_IS_TOGGLED` performs a bitwise AND with the complement of the toggle bit, which clears only that specific bit while preserving all others. This matches the function's name and purpose of marking the button as untoggled.

The function does **not** perform Lavender-style initialization (reset/cleanup to initial conditions). It only clears a single flag bit, leaving the rest of the struct untouched. This is consistent with its role as a flag-setter helper, not a struct initializer.

## Implementation Correctness

- **Type compatibility:** `ui_button_flags` is of type `UI_Button_Flags__u8` (typedef'd as `uint8_t`). `UI_BUTTON_FLAGS__BIT_IS_TOGGLED` is defined as `BIT(UI_BUTTON_FLAGS__BIT_SHIFT_IS_TOGGLED)`, which expands to `((1U) << 1)` — an `unsigned int`. The `&=` operation between a `uint8_t` lvalue and an `unsigned int` rvalue is well-defined: the rvalue is implicitly converted to `uint8_t` for the compound assignment. Since the value `~UI_BUTTON_FLAGS__BIT_IS_TOGGLED` in the context of a uint8_t is `0xFD` (all bits set except bit 1), this is safe and correct. No truncation occurs because the result fits within the uint8_t range.
- **Undefined behavior:** No null pointer dereference guard is present, but this is consistent with the rest of the file's inline helpers (e.g., `set_ui_button_as__toggleable`, `set_ui_button_as__toggled`). The caller is expected to provide a valid pointer. No other undefined behavior is present.
- **Validation:** No parameter validation (null check) is performed. This is appropriate given the function's role as a lightweight inline helper, and is consistent with the other flag-setter functions in the same file. Validation is the caller's responsibility.

## Side Effects

- Mutates `p_ui_button->ui_button_flags` by clearing the `UI_BUTTON_FLAGS__BIT_IS_TOGGLED` bit.
- No other side effects. Does not call any other functions, does not perform I/O, and does not modify any global state.
