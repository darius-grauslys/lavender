set_position_3i32_of__ui_element — core/source/ui/ui_element.c, lines 231-283

Recursively sets the position of a UI_Element and its child UI_Element, preserving the relative offset between parent and child.

Pre-conditions:
1. p_game must be a non-null pointer to a valid Game object.
2. p_graphics_window must be a non-null pointer to a valid Graphics_Window object.
3. p_ui_element must be a non-null pointer to a valid UI_Element object.
4. p_ui_element must have an associated Hitbox_AABB registered in the Hitbox_AABB_Manager (retrieved via get_p_hitbox_aabb_of__ui_element). If no hitbox exists, p_hitbox_aabb will be NULL and subsequent operations are undefined in release builds.
5. position__3i32 is any Vector__3i32; no range constraints.

Post-conditions:
1. The UI_Element's Hitbox_AABB position is set to position__3i32 via set_hitbox_aabb__position_with__3i32.
2. If p_ui_element has a transformed handler (m_ui_transformed_handler), it is invoked with the new position before the hitbox is updated.
3. If p_ui_element has a child, set_position_3i32_of__ui_element is recursively called on the child. The child's new position is intended to preserve the relative offset between parent and child (child moves by the same delta as the parent).

Correctness Verdict: Incorrect

Semantic Alignment:
The function's intent is to move a parent UI element to a new position and propagate that movement to its child while preserving the relative offset between them. The child's new position should be: child_old_position + (parent_new_position - parent_old_position).

However, the implementation contains a semantic bug in the computation of the child's new position:

- The variable `vector_of__child_relative_to__parent` is intended to represent the child's position relative to the parent (i.e., `child_old - parent_old`). However, it is computed as `position__3i32 - old_parent_position`, which is the parent's movement delta (`parent_new - parent_old`), not the child's relative offset. The child's old position is never retrieved.

- In the recursive call, the child's new position is computed as `add_vectors__3i32(vector_of__child_relative_to__parent, get_position_3i32_of__hitbox_aabb(p_hitbox_aabb))`. Since the parent's position has already been set to `position__3i32` by this point, `get_position_3i32_of__hitbox_aabb(p_hitbox_aabb)` returns the parent's NEW position. This results in: child_new = (parent_new - parent_old) + parent_new = 2 * parent_new - parent_old, which is incorrect.

- The correct computation should be: child_new = child_old + (parent_new - parent_old). The child's old position must be retrieved from the child's hitbox before the parent's position is updated.

Example: If parent_old=(10,20,0), parent_new=(30,40,0), child_old=(15,25,0):
- Expected child_new: (15,25,0) + (20,20,0) = (35,45,0)
- Actual child_new: (20,20,0) + (30,40,0) = (50,60,0) — incorrect.

Additionally, there is a secondary issue: when the UI_Element has a transformed handler, the default handler (m_ui_element__transformed_handler__default) calls set_position_3i32_of__ui_element on the child with the parent's new position (not the delta-adjusted position). The subsequent recursive call at the end of this function then overwrites the child's position with the incorrect computation, resulting in the child being positioned twice with conflicting values.

Implementation Correctness:
Type compatibility: All parameter types match target field/function types exactly. Vector__3i32 is used consistently throughout. No implicit conversions or truncation.
Undefined behavior: No broken pointer arithmetic. However, p_hitbox_aabb is obtained from get_p_hitbox_aabb_of__ui_element without a null check before being dereferenced in get_position_3i32F4_of__hitbox_aabb and set_hitbox_aabb__position_with__3i32. In debug builds, the getter checks for null; in release builds, this would be undefined behavior. This is consistent with the codebase pattern (e.g., set_ui_element__size at line 285 also does not null-check), though set_ui_element__hitbox at line 314 does check.
Validation: No validation of p_hitbox_aabb is performed. This is consistent with the codebase pattern for similar functions, where the caller is expected to ensure the UI element has an allocated hitbox.

Side Effects:
1. Mutates the Hitbox_AABB of p_ui_element by setting its position to position__3i32 (marks it dirty).
2. If a transformed handler is present, invokes it (may have additional side effects depending on the handler implementation).
3. Recursively calls itself on p_ui_element->p_child, which mutates the child's Hitbox_AABB position.
4. Sets the UI manager as dirty indirectly through set_hitbox_aabb__position_with__3i32 (which calls set_hitbox_aabb_as__dirty).
