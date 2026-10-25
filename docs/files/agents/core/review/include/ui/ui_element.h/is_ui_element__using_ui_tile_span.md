is_ui_element__using_ui_tile_span — core/include/ui/ui_element.h

Queries whether a UI_Element is rendering via a UI_Tile_Span by negating the sprite-or-tile-span flag check.

Pre-conditions:
1. p_ui_element must be a non-null pointer to a valid, initialized UI_Element struct.
2. No null check is performed internally; this is consistent with all other is_ui_element__* query functions in this header (e.g., is_ui_element__enabled, is_ui_element__using_sprite). The caller is responsible for ensuring the pointer is valid.

Post-conditions:
1. Returns true if the UI_FLAGS__BIT_IS_USING__SPRITE_OR_UI_TILE_SPAN flag is clear (element is using a UI tile span).
2. Returns false if the UI_FLAGS__BIT_IS_USING__SPRITE_OR_UI_TILE_SPAN flag is set (element is using a sprite).
3. The pointed-to struct is not mutated; the function is a pure query.

Correctness Verdict: Correct

Semantic Alignment:
The function correctly implements its semantic intent. The flag UI_FLAGS__BIT_IS_USING__SPRITE_OR_UI_TILE_SPAN (BIT(6)) serves as a binary discriminator between two mutually exclusive rendering modes:
- Set (1) → element is using a sprite (set by set_ui_element_as__using_sprite).
- Clear (0) → element is using a UI tile span (set by set_ui_element_as__using_ui_tile_span).

The function is_ui_element__using_ui_tile_span negates the result of is_ui_element__using_sprite_or__ui_tile_span, which returns true when the flag is set. Therefore is_ui_element__using_ui_tile_span returns true when the flag is clear — i.e., when the element is using a UI tile span. This is exactly the intended behavior.

The usage in does_ui_element_have__compose_handler confirms this design: a compose handler is only relevant when the element is using a UI tile span, and set_ui_element__compose_handler internally calls set_ui_element_as__using_ui_tile_span to clear the flag before assigning the handler.

Implementation Correctness:
- Type compatibility: The return type is bool. The inner call to is_ui_element__using_sprite_or__ui_tile_span returns bool, and the ! operator on a bool yields a bool. No implicit conversions or truncation issues.
- Undefined behavior: No pointer arithmetic, no null dereference (caller must provide valid pointer, per the consistent design pattern of all is_ui_element__* functions), no type punning, no out-of-bounds access. The only memory access is reading p_ui_element->ui_flags via the delegated call, which is a valid read of a u16 field.
- Validation: No validation is needed for this low-level query function. The absence of a null check is consistent with the family of is_ui_element__* functions and is the caller's responsibility.

Side Effects:
No side effects. The function is a pure query — it reads the ui_flags field of the UI_Element and returns a boolean result without modifying any state.
