m_ui_drop_zone__receive_drop_handler__default — core/source/ui/ui_drop_zone.c

Default handler for when a UI element is dropped onto a drop zone.

Pre-conditions:
1. p_this_drop_zone must be a non-null pointer to a valid UI_Element of kind UI_Element_Kind__Drop_Zone.
2. p_ui_element__dropped may be NULL; if NULL, the function returns early without doing anything.
3. p_game must be a non-null pointer to a valid Game instance.
4. p_graphics_window must be a non-null pointer to a valid Graphics_Window instance.
5. p_this_drop_zone must have a valid hitbox AABB registered in the hitbox AABB manager associated with p_graphics_window.

Post-conditions:
1. If p_ui_element__dropped is NULL, no state is modified.
2. If p_ui_element__dropped has a parent, the children of p_this_drop_zone and p_ui_element__dropped's former parent are swapped via swap_ui_element__children.
3. If p_ui_element__dropped has no parent, it is reparented to p_this_drop_zone via set_ui_element_as__the_parent_of__this_ui_element, and its position is set to match p_this_drop_zone's position via set_position_3i32_of__ui_element.
4. If p_ui_element__dropped had a former parent with a child that has a dropped handler, that handler is invoked with the child as the receiver.
5. If p_ui_element__dropped had a former parent with a receive-drop handler, that handler is invoked with the former parent as the receiver and NULL as the dropped element.

Correctness Verdict: Correct

Semantic Alignment:
The implementation correctly fulfills the semantic intent of a default drop-zone receive-drop handler. When a dropped element has a parent, the children are swapped between the drop zone and the former parent, which is a reasonable behavior for transferring ownership. When the dropped element has no parent, it is simply reparented to the drop zone and positioned at the drop zone's location. After the reparenting, the former parent's child dropped handler and receive-drop handler are invoked if present, allowing the former parent to react to losing its child. The logic flow matches the intended behavior.

Implementation Correctness:
Type compatibility — all function parameters match their expected types. p_this_drop_zone and p_ui_element__dropped are UI_Element*, p_game is Game*, p_graphics_window is Graphics_Window*. The cast of the return of get_pV_hitbox_manager_from__graphics_window to Hitbox_AABB_Manager* is consistent with the pattern used elsewhere in the codebase.
No undefined behavior — null checks are performed on p_ui_element__dropped (early return), p_ui_manager (debug-only check), and the former parent pointer (early return). The function does not perform any pointer arithmetic, array indexing, or type punning. The calls to m_ui_receive_drop_handler and m_ui_dropped_handler are guarded by does_ui_element_have__receive_drop_handler and does_ui_element_have__dropped_handler checks respectively, which verify both the element pointer and the handler function pointer are non-null.
Validation — the null check on p_ui_element__dropped is appropriate for this function's role. The debug-only check on p_ui_manager is reasonable since in release builds, a null p_ui_manager would result in a null pointer dereference in swap_ui_element__children or set_ui_element_as__the_parent_of__this_ui_element, which is a caller responsibility.

Side Effects:
Mutates the UI element hierarchy by swapping children or reparenting the dropped element. Invokes the former parent's child dropped handler and receive-drop handler if present. Marks the UI manager as dirty (indirectly through swap_ui_element__children and set_ui_element_as__the_parent_of__this_ui_element which call set_ui_element_priority_higher_than__this_ui_element_in__ui_manager).
