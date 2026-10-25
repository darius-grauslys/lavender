set_ui_tile_span_of__ui_element — core/source/ui/ui_element.c

Sets a UI_Element to use a UI_Tile_Span by copying the span into the element, marking the element as using a tile span (not a sprite), and ensuring a compose handler is assigned.

Pre-conditions:
1. p_ui_element must be a non-null pointer to a writable UI_Element object.
2. p_ui_tile_span must be a non-null pointer to a valid UI_Tile_Span object.

Post-conditions:
1. p_ui_element->ui_tile_span is overwritten with a copy of *p_ui_tile_span (all fields of the UI_Tile_Span struct are copied).
2. The UI_FLAGS__BIT_IS_USING__SPRITE_OR_UI_TILE_SPAN flag in p_ui_element->ui_flags is cleared, indicating the element is now using a UI_Tile_Span rather than a sprite.
3. If p_ui_element did not already have a compose handler (i.e., does_ui_element_have__compose_handler returned false), the default compose handler m_ui_element__compose_handler__default is assigned to p_ui_element->m_ui_compose_handler.

Correctness Verdict: Correct

Semantic Alignment:
The function correctly fulfills its intent: it configures a UI_Element to render via a UI_Tile_Span. It first marks the element as using a tile span (clearing the sprite flag), copies the tile span data, and ensures a compose handler exists so the element can be composed during rendering. The compose handler check (does_ui_element_have__compose_handler) correctly verifies both that the element is using a tile span and that a compose handler is set; if either condition fails, the default handler is assigned.

Implementation Correctness:
Type compatibility — p_ui_element is UI_Element * and p_ui_tile_span is UI_Tile_Span *, matching the struct field types exactly. The assignment p_ui_element->ui_tile_span = *p_ui_tile_span is a struct copy of identical types (UI_Tile_Span = UI_Tile_Span). No implicit conversions or truncation.
No undefined behavior — no pointer arithmetic, no type punning, no out-of-bounds access. The struct copy is a valid value copy.
No validation (null checks) is performed on p_ui_element or p_ui_tile_span. This is consistent with the codebase pattern where low-level struct mutation functions delegate null-pointer validation to the caller. The caller (e.g., set_ui_element__compose_handler) is responsible for ensuring valid pointers.

Side Effects:
1. p_ui_element->ui_flags is modified (the UI_FLAGS__BIT_IS_USING__SPRITE_OR_UI_TILE_SPAN bit is cleared).
2. p_ui_element->ui_tile_span is overwritten with a copy of *p_ui_tile_span.
3. p_ui_element->m_ui_compose_handler may be set to m_ui_element__compose_handler__default if no compose handler was previously assigned.
