# set_ui_button_as__non_toggleable

**File of origin:** `core/include/ui/ui_button.h`

## Semantic

Sets the UI element as a non-toggleable button by clearing the `IS_TOGGLEABLE` flag and also resetting the `IS_TOGGLED` flag, since a non-toggleable button should not retain a toggled state.

## Pre-conditions

1. `p_ui_button` must be non-null. The function dereferences it directly without null checking; passing null results in undefined behavior.
2. `p_ui_button` must point to a valid `UI_Element` struct whose `ui_button_flags` field is accessible and writable.

## Post-conditions

1. The `UI_BUTTON_FLAGS__BIT_IS_TOGGLEABLE` bit (bit 0) of `p_ui_button->ui_button_flags` is cleared (set to 0).
2. The `UI_BUTTON_FLAGS__BIT_IS_TOGGLED` bit (bit 1) of `p_ui_button->ui_button_flags` is cleared (set to 0), via the call to `set_ui_button_as__untoggled`.
3. All other bits in `p_ui_button->ui_button_flags` remain unchanged.

## Correctness Verdict

**Correct**

## Semantic Alignment

The implementation correctly fulfills the semantic intent. Making a button non-toggleable logically implies that it should also be reset to an untoggled state, since a non-toggleable button cannot meaningfully be "toggled." The function achieves this by:

1. Clearing `UI_BUTTON_FLAGS__BIT_IS_TOGGLEABLE` using `&= ~UI_BUTTON_FLAGS__BIT_IS_TOGGLEABLE`, which is the standard idiom for clearing a specific bit in a flags field.
2. Delegating to `set_ui_button_as__untoggled`, which in turn clears `UI_BUTTON_FLAGS__BIT_IS_TOGGLED` using `&= ~UI_BUTTON_FLAGS__BIT_IS_TOGGLED`.

Both operations use the correct bitwise AND-with-complement pattern, and the flag definitions (`UI_BUTTON_FLAGS__BIT_IS_TOGGLEABLE` and `UI_BUTTON_FLAGS__BIT_IS_TOGGLED`) are properly defined in `core/include/defines.h` using the `BIT()` macro.

## Implementation Correctness

- **Type compatibility:** `ui_button_flags` is of type `UI_Button_Flags__u8` (i.e., `uint8_t`). The flag macros expand to `BIT(n)` which is `(1U) << (n)`, yielding an `unsigned int`. The bitwise AND assignment (`&=`) and bitwise NOT (`~`) operations on a `uint8_t` promote to `int`/`unsigned int` and then truncate back to `uint8_t`, which is well-defined and safe for these flag values. No implicit truncation issues arise.
- **Undefined behavior:** No null dereference is guarded against, but this is consistent with the codebase convention — all sibling inline functions (`set_ui_button_as__toggleable`, `set_ui_button_as__toggled`, `set_ui_button_as__untoggled`, etc.) also assume a non-null pointer. No out-of-bounds access, broken pointer arithmetic, or type punning occurs.
- **Validation:** No parameter validation is performed, which is appropriate for this low-level inline helper. Null checking is the caller's responsibility, consistent with the rest of the UI button inline API.

## Side Effects

- Mutates `p_ui_button->ui_button_flags` by clearing the `IS_TOGGLEABLE` bit and the `IS_TOGGLED` bit.
- Calls `set_ui_button_as__untoggled(p_ui_button)` as a side effect of its own execution, which further mutates the same field.
