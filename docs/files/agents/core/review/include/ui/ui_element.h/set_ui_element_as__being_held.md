# set_ui_element_as__being_held

## File of Origin
`core/include/ui/ui_element.h` (lines 403-407)

## Semantic
Sets the `UI_FLAGS__BIT_IS_BEING_HELD` bit in the `ui_flags` field of the given `UI_Element`, marking it as currently being held (e.g., by a cursor or drag operation).

## Pre-conditions
1. `p_ui_element` must be non-null. The function dereferences `p_ui_element` directly without a null check; passing null results in undefined behavior.
2. `p_ui_element->ui_flags` must be a valid `UI_Flags__u16` (i.e., `uint16_t`) value. This is guaranteed if the `UI_Element` struct has been properly initialized via `initialize_ui_element`.

## Post-conditions
1. The `UI_FLAGS__BIT_IS_BEING_HELD` bit (bit 3) is set in `p_ui_element->ui_flags`.
2. All other bits in `ui_flags` remain unchanged (bitwise OR semantics).
3. After return, `is_ui_element__being_held(p_ui_element)` will return `true`.

## Correctness Verdict
**Correct**

## Semantic Alignment
The implementation faithfully fulfills the semantic intent. The function name `set_ui_element_as__being_held` directly corresponds to setting the `UI_FLAGS__BIT_IS_BEING_HELD` flag. The bitwise OR operation (`|=`) is the correct idiom for setting a bit flag, and it is consistent with every other flag-setting inline function in this header (e.g., `set_ui_element_as__focused`, `set_ui_element_as__being_dragged`, `set_ui_element_as__enabled`, etc.). The counterpart `set_ui_element_as__dropped` correctly clears this same bit (along with `IS_BEING_DRAGGED`), confirming the flag's intended semantics.

## Implementation Correctness
- **Type compatibility**: `ui_flags` is of type `UI_Flags__u16` (typedef'd to `uint16_t` in `defines.h`). `UI_FLAGS__BIT_IS_BEING_HELD` is defined as `BIT(3)` which expands to `1 << 3` (i.e., `8`), a value well within the range of `uint16_t`. The `|=` compound assignment is type-safe with no implicit conversions or truncation.
- **Undefined behavior**: No undefined behavior is introduced. There is no pointer arithmetic, no type punning, and no out-of-bounds access. The only requirement is that `p_ui_element` is non-null, which is the caller's responsibility (consistent with all sibling inline functions in this header that also perform no null checks).
- **Validation**: No validation is performed. This is appropriate for the function's role as a low-level inline flag setter — all sibling functions (`set_ui_element_as__focused`, `set_ui_element_as__being_dragged`, etc.) follow the same pattern of no null-check, placing that responsibility on the caller.

## Side Effects
- **Mutates** `p_ui_element->ui_flags` by setting the `UI_FLAGS__BIT_IS_BEING_HELD` bit (bit 3).
- No other state is modified.
- No allocations, deallocations, or I/O operations are performed.
