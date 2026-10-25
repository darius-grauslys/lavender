# set_ui_element_as__being_dragged

**File of origin:** `core/include/ui/ui_element.h`

## Semantic

Sets the `UI_FLAGS__BIT_IS_BEING_DRAGGED` flag (bit 4) in the `ui_flags` field of the given `UI_Element`, marking the element as currently being dragged by the user.

## Pre-conditions

1. `p_ui_element` must be a non-null pointer to a writable `UI_Element` object.
2. `p_ui_element` must point to a valid, initialized `UI_Element` struct (the `ui_flags` field must be accessible).

## Post-conditions

1. The `ui_flags` field of the `UI_Element` pointed to by `p_ui_element` has the `UI_FLAGS__BIT_IS_BEING_DRAGGED` bit set to 1.
2. All other bits in `ui_flags` are preserved (the operation is a bitwise OR, which only sets the target bit and leaves all others unchanged).
3. No other fields of the `UI_Element` struct are modified.

## Correctness Verdict

Correct

## Semantic Alignment

The implementation directly fulfills the semantic intent: it performs a bitwise OR of `UI_FLAGS__BIT_IS_BEING_DRAGGED` (`BIT(4)`) into `p_ui_element->ui_flags`, which sets exactly the "is being dragged" flag bit and nothing else. The flag constant and the field are both defined in `defines.h` (lines 1624 and 1636 respectively), and `ui_flags` is the `UI_Flags__u16` (`uint16_t`) member of `UI_Element` (line 1727 of `defines.h`). The operation is consistent with the sibling functions `set_ui_element_as__focused`, `set_ui_element_as__being_held`, and `set_ui_element_as__enabled`, all of which use the same `|=` pattern.

## Implementation Correctness

- **Type compatibility:** `p_ui_element->ui_flags` is of type `UI_Flags__u16` (`uint16_t`). `UI_FLAGS__BIT_IS_BEING_DRAGGED` is defined as `BIT(4)`, which expands to `(1u << 4)` — a `uint16_t`-compatible value. The `|=` operation is type-safe with no implicit conversions or truncation.
- **Undefined behavior:** No pointer arithmetic, no null dereference (the caller is responsible for ensuring `p_ui_element` is non-null, consistent with all other `set_ui_element_as__*` functions in this header), no type punning, no out-of-bounds access.
- **Validation:** No validation is performed, which is appropriate for this low-level inline helper. The caller is responsible for ensuring `p_ui_element` is valid. This is consistent with the pattern used by every other `set_ui_element_as__*` function in this header, none of which perform null checks.

## Side Effects

Mutates the `ui_flags` field of the `UI_Element` pointed to by `p_ui_element` by setting the `UI_FLAGS__BIT_IS_BEING_DRAGGED` bit. No other observable side effects.
