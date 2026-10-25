handle_drop_in__ui_manager — core/source/ui/ui_manager.c

Handles the drop event for a UI element that was being dragged. Marks the focused element as dropped, finds the UI element receiving the drop, invokes the receive-drop handler on that element, and invokes the dropped handler on the focused element.

Pre-conditions:
1. p_game must be a non-null pointer to a valid Game object.
2. p_graphics_window must be a non-null pointer to a valid Graphics_Window object.
3. p_ui_manager must be a non-null pointer to a valid UI_Manager object.
4. p_ui_element__focused may be NULL (the function returns early if so).
5. If p_ui_element__focused is non-null, it must be a valid UI_Element pointer.
6. p_ui_manager->p_ui_element__focused is expected to be in sync with the parameter p_ui_element__focused (i.e., they point to the same UI_Element). This is an implicit assumption that is not enforced.

Post-conditions:
1. If p_ui_element__focused was NULL, the function returns immediately with no side effects.
2. p_ui_element__focused has its BEING_HELD and BEING_DRAGGED flags cleared (via set_ui_element_as__dropped).
3. If p_ui_element__focused has no dropped handler, the UI manager's focused element is cleared (via drop_ui_element_focus_for__ui_manager) and the function returns.
4. If an element receiving the drop exists and has a receive_drop handler, that handler is invoked with the receiving element as the first argument and the focused element as the dropped element.
5. If p_ui_element__focused has a dropped handler, it is invoked with the focused element as the first argument.
6. p_ui_manager->p_ui_element__focused may be modified if the focused element lacks a dropped handler (set to 0 via drop_ui_element_focus_for__ui_manager).

Correctness Verdict: Incorrect

Semantic Alignment:
The function's intent is to handle a drop event on the element passed as p_ui_element__focused. However, the implementation inconsistently uses p_ui_manager->p_ui_element__focused (the UI_Manager member) instead of the parameter p_ui_element__focused in three critical locations:

1. When calling get_highest_priority_ui_element_thats__under_this_ui_element, the member p_ui_manager->p_ui_element__focused is passed as the "above" element instead of the parameter. This determines which element's position is used to find what is underneath it.

2. When calling m_ui_receive_drop_handler, the member p_ui_manager->p_ui_element__focused is passed as the "dropped" element (second argument) instead of the parameter. The receive-drop handler is told that a different element was dropped than the one actually being handled.

3. When calling m_ui_dropped_handler, the member p_ui_manager->p_ui_element__focused is passed as the first argument (p_this_ui_element) instead of the parameter. The dropped handler is invoked on the parameter object but told it is the member object.

At the current call site (poll_ui_manager__update_for__clicked_and_dropped), the parameter and member are always the same pointer because detect_focus__strictly_under_cursor_in__ui_manager sets the member via set_p_ui_element_as__focused_in__ui_manager before calling this function. However, this creates a fragile implicit contract: the function's behavior depends on the member being in sync with the parameter, rather than using the parameter it explicitly receives. If the member were modified between the call and its use within this function (e.g., by a handler invocation, or if the function were called from a different context), the behavior would be incorrect. The function should consistently use the parameter p_ui_element__focused throughout.

Implementation Correctness:
Type compatibility — All parameter types match their target field/function types exactly. The handler function pointer invocations use the correct typedef'd signatures (m_UI_Receive_Drop, m_UI_Dropped). No implicit conversions or truncation.
Undefined behavior — No pointer arithmetic, no null dereference (p_ui_element__focused is null-checked before use; p_hitbox_aabb_manager could theoretically be null if the hitbox context lookup fails, but this is consistent with the codebase's assumption that the UI manager has a registered hitbox manager). No type punning, no out-of-bounds access.
Validation — The function validates p_ui_element__focused for null, which is appropriate. p_game, p_graphics_window, and p_ui_manager are not validated, but this is consistent with the codebase convention where callers are responsible for ensuring these are valid (the function is only called from poll_ui_manager__update_for__clicked_and_dropped, which is called from poll_ui_manager__update, which operates on validated parameters).

Side Effects:
1. Mutates p_ui_element__focused by clearing its BEING_HELD and BEING_DRAGGED flags (via set_ui_element_as__dropped).
2. May mutate p_ui_manager->p_ui_element__focused (sets to 0 via drop_ui_element_focus_for__ui_manager) if the focused element lacks a dropped handler.
3. Invokes p_ui_element__receiving_drop->m_ui_receive_drop_handler if a receiving element with a handler exists.
4. Invokes p_ui_element__focused->m_ui_dropped_handler if the focused element has a dropped handler.
