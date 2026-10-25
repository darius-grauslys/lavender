m_ui_element__transformed_handler__default — core/source/ui/ui_element.c

Default transformed handler that propagates the element's new position to its child UI element.

Pre-conditions:
1. p_this_ui_element must be a non-null pointer to a valid UI_Element (though the function uses does_ui_element_have__child, which internally null-checks).
2. p_hitbox_aabb is accepted as part of the handler signature but is unused by this default implementation; it may be NULL without causing issues.
3. position_NEW_of__hitbox__3i32 is a valid Vector__3i32 representing the new position to propagate to the child.
4. p_game must be non-null (passed through to set_position_3i32_of__ui_element, which dereferences it).
5. p_graphics_window must be non-null (passed through to set_position_3i32_of__ui_element, which dereferences it).

Post-conditions:
1. If p_this_ui_element has a child, the child's position is set to position_NEW_of__hitbox__3i32 via set_position_3i32_of__ui_element, which recursively propagates the position to grandchildren and marks the UI manager as dirty.
2. If p_this_ui_element has no child, no action is taken.

Correctness Verdict: Correct

Semantic Alignment:
The function correctly fulfills its semantic intent: when a UI element is transformed (its position changes), the default handler propagates that new position to the child element. The guard via does_ui_element_have__child prevents dereferencing a null child pointer. The child receives the same position_NEW_of__hitbox__3i32 that the parent received, which is consistent with how set_position_3i32_of__ui_element calls the transformed handler (passing the parent's new position as the argument).

Implementation Correctness:
Type compatibility — all parameter types match the m_UI_Transformed typedef exactly:
- UI_Element *p_this_ui_element
- Hitbox_AABB *p_hitbox_aabb
- Vector__3i32 position_NEW_of__hitbox__3i32
- Game *p_game
- Graphics_Window *p_graphics_window
No implicit conversions or truncation.
No undefined behavior — does_ui_element_have__child performs a null check on p_this_ui_element and checks p_child before accessing it. get_child_of__ui_element is only called after the guard confirms a child exists.
Validation is appropriate — the function relies on does_ui_element_have__child for null safety. The caller (set_position_3i32_of__ui_element or allocate_hitbox_for__ui_element) is responsible for ensuring p_game and p_graphics_window are valid before invoking the handler.

Side Effects:
- If the element has a child, mutates the child's position (and recursively descendants') via set_position_3i32_of__ui_element, which also marks the UI manager as dirty.
- No side effects when the element has no child.
