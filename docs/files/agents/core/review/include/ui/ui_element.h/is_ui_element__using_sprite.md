is_ui_element__using_sprite — core/include/ui/ui_element.h

Checks whether a UI_Element is configured to use a sprite (as opposed to a UI tile span) by testing the UI_FLAGS__BIT_IS_USING__SPRITE_OR_UI_TILE_SPAN bit in the element's ui_flags field.

Pre-conditions:
1. p_ui_element must be a non-null pointer to a valid, initialized UI_Element struct.
2. The caller is responsible for ensuring p_ui_element is valid; no null-check is performed (consistent with all other is_* query functions in this file).

Post-conditions:
1. Returns true if the UI_FLAGS__BIT_IS_USING__SPRITE_OR_UI_TILE_SPAN bit is set in p_ui_element->ui_flags (i.e., the element is using a sprite).
2. Returns false if the bit is not set (i.e., the element is using a UI tile span).
3. No state is mutated; the function is a pure read-only query.

Correctness Verdict: Correct

Semantic Alignment:
The function correctly delegates to is_ui_element__using_sprite_or__ui_tile_span, which tests the UI_FLAGS__BIT_IS_USING__SPRITE_OR_UI_TILE_SPAN bit. This flag is SET by set_ui_element_as__using_sprite and CLEARED by set_ui_element_as__using_ui_tile_span, confirming that the flag being set means "using sprite" and the flag being clear means "using UI tile span." The function therefore correctly returns true when the element is using a sprite. The sibling function is_ui_element__using_ui_tile_span returns the logical negation, which is consistent with this interpretation.

Implementation Correctness:
Type compatibility — p_ui_element is UI_Element *, matching the parameter type. The ui_flags field is UI_Flags__u16 (uint16_t), and UI_FLAGS__BIT_IS_USING__SPRITE_OR_UI_TILE_SPAN is a BIT() macro producing a uint16_t-compatible value. The bitwise AND yields a uint16_t, which is implicitly converted to bool on return (any non-zero value becomes true). This is functionally correct, though it does not use an explicit (bool) cast like some sibling functions (e.g., is_ui_element__enabled). This is a minor style inconsistency, not a correctness issue.
No undefined behavior — no pointer arithmetic, no null dereference (caller's responsibility), no type punning, no out-of-bounds access. The function only reads the ui_flags field.
No validation is needed — this is a low-level inline query function. Validation is the caller's responsibility, consistent with the pattern of all is_* functions in this file.

Side Effects:
No side effects. The function is a pure read-only query that only reads p_ui_element->ui_flags and returns a boolean.
