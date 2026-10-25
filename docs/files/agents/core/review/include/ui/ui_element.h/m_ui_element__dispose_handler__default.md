m_ui_element__dispose_handler__default — core/source/ui/ui_element.c

Recursively disposes a UI element's child and next-sibling sub-tree, then releases the element's associated hitbox AABB and sprite, and finally nulls the element's parent/child/next pointers to reset it to its initial (pooled) state.

Pre-conditions:
1. p_this_ui_element must be a non-null pointer to a valid, initialized UI_Element. (No explicit null check exists in the function; the caller is responsible for ensuring validity. Recursive calls are guarded by does_ui_element_have__dispose_handler, which checks for null.)
2. p_game must be a non-null pointer to a valid Game instance. (get_p_ui_manager_from__graphics_window and get_p_sprite_manager_from__graphics_window include debug-mode null checks for p_game.)
3. p_graphics_window must be a non-null pointer to a valid Graphics_Window. (Same debug-mode null checks apply.)
4. The UI element must have been previously initialized via initialize_ui_element or equivalent, so that its Serialization_Header (and thus its UUID) is valid for resource lookups.

Post-conditions:
1. p_this_ui_element->p_parent, p_this_ui_element->p_child, and p_this_ui_element->p_next are all set to NULL (0).
2. Any Hitbox_AABB associated with this element's UUID is released back to the Hitbox_AABB_Manager (if a manager exists and the hitbox is found).
3. Any Sprite associated with this element's UUID is released back to the Sprite_Manager (if a manager exists and the sprite is found).
4. The UI_Manager is marked as dirty, signaling that recomposition is needed.
5. If the element has a child with a dispose handler, that child's dispose handler is invoked recursively.
6. If the element has a next sibling with a dispose handler, that sibling's dispose handler is invoked recursively.

Correctness Verdict: Correct

Semantic Alignment:
The implementation fulfills the semantic intent of a dispose handler in the Lavender engine. This is a Lavender-style "initialization" (i.e., cleanup/reset to initial conditions), NOT RAII-style resource acquisition. The function:
- Recursively disposes the child and next-sibling sub-tree by invoking their respective dispose handlers, ensuring the entire linked structure is cleaned up.
- Releases the hitbox AABB and sprite resources associated with this element by UUID lookup.
- Nulls the parent/child/next pointers, resetting the element to a state suitable for return to a free pool or reuse.
- Marks the UI manager as dirty so the rendering system knows to recompose.

The recursive disposal of child and next occurs BEFORE nulling the pointers on p_this_ui_element. This is correct because the child's dispose handler will set the child's p_parent to 0 (breaking the child's reference to this element), and then this function nullifies its own p_child pointer afterward. No dangling references remain.

The comment in the UI_Element struct (defines.h, line 1693) instructs custom dispose handlers to also invoke m_ui_element__dispose_handler__default, confirming this function is the canonical cleanup implementation.

Implementation Correctness:
Type compatibility — all function calls use correct types: p_this_ui_element is UI_Element*, p_game is Game*, p_graphics_window is Graphics_Window*. GET_UUID_P correctly casts to Serialization_Header* to access the uuid field, which is valid because Serialization_Header is the first member of UI_Element.
Undefined behavior — no broken pointer arithmetic, no null dereference (all pointer dereferences are guarded by null checks on managers/handboxes/sprites, and recursive calls are guarded by does_ui_element_have__dispose_handler), no type punning, no out-of-bounds access.
Validation — validation is appropriate for the function's role. The does_ui_element_have__child/does_ui_element_have__next guards protect recursive calls. The null checks on p_hitbox_aabb_manager and p_sprite_manager protect resource lookups. The does_ui_element_have__sprite check protects sprite lookup. The caller is responsible for ensuring p_this_ui_element, p_game, and p_graphics_window are non-null (consistent with the codebase pattern for handler functions).
Note: set_ui_manager_as__dirty is called without a null check on the returned UI_Manager pointer. In debug builds, get_p_ui_manager_from__graphics_window returns 0 if p_game or p_graphics_window is null, which would cause a null dereference in set_ui_manager_as__dirty. However, this is an established pattern throughout the codebase (e.g., m_ui_element__compose_handler__default_non_recursive and m_ui_element__compose_handler__default_only_recursive use the same pattern), indicating it is an accepted assumption that a valid UI manager always exists when these handlers are invoked.

Side Effects:
- Marks the UI_Manager as dirty (ui_manager_flags__u8 |= UI_MANAGER_FLAG__IS_DIRTY).
- Mutates p_this_ui_element: p_parent, p_child, and p_next are set to NULL.
- May release a Hitbox_AABB from the Hitbox_AABB_Manager (if one is associated with this element's UUID).
- May release a Sprite from the Sprite_Manager (if one is associated with this element's UUID).
- Recursively invokes dispose handlers on child and next-sibling UI elements (if present and if they have dispose handlers), which in turn produce their own side effects.
