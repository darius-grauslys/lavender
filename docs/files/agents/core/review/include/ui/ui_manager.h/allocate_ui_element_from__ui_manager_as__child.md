allocate_ui_element_from__ui_manager_as__child — core/source/ui/ui_manager.c

Allocates a new UI element from the UI manager's pool and attaches it as a child of the specified parent, synchronizing the child's position to the parent's position.

Pre-conditions:
1. p_game must be a non-null pointer (used to retrieve the hitbox context).
2. p_graphics_window must be a non-null pointer (passed to set_position_3i32_of__ui_element).
3. p_ui_manager must be a non-null pointer (used for element allocation and parent-child linking).
4. p_parent must be a non-null pointer — set_ui_element_as__the_parent_of__this_ui_element will debug_abort if p_parent is null, and get_position_3i32_from__p_ui_element dereferences p_parent via GET_UUID_P.
5. The UI manager's element pool must have available capacity; otherwise allocate_ui_element_from__ui_manager may return null or access out-of-bounds memory (a pre-existing issue in the allocation function, not introduced here).

Post-conditions:
1. A new UI_Element is allocated from p_ui_manager's pool and registered in the pointer array.
2. The new element is initialized with default values (kind None, no flags, no parent/child/next) by allocate_ui_element_from__ui_manager, then enabled and the manager marked dirty.
3. The parent-child relationship is established: p_parent->p_child is set to the new child, and the child's p_parent is set to p_parent. Any prior child or parent of either element is detached.
4. The child's priority in the pointer array is adjusted so it ranks higher than the parent's (via set_ui_element_priority_higher_than__this_ui_element_in__ui_manager).
5. The child's position is set to match the parent's current position via set_position_3i32_of__ui_element, which also propagates the position change to any existing child of the new element (none at allocation time).
6. The newly allocated child element pointer is returned.

Correctness Verdict: Correct

Semantic Alignment:
The implementation fulfills the semantic intent. The function allocates a UI element, establishes it as a child of the given parent, and positions it at the parent's location. Each step delegates to well-tested helper functions: allocate_ui_element_from__ui_manager for allocation and initialization, set_ui_element_as__the_parent_of__this_ui_element for the parent-child link, and set_position_3i32_of__ui_element for position synchronization. No reordering or omission of steps occurs.

Implementation Correctness:
Type compatibility — all pointer parameters (Game*, Graphics_Window*, UI_Manager*, UI_Element*) are passed directly to functions expecting those exact types. No implicit conversions or truncation.
No undefined behavior — assuming all pre-conditions hold, there is no null dereference, no out-of-bounds access, and no type punning. The GET_UUID_P macro safely casts p_ui_manager and p_parent to Serialization_Header* since both are guaranteed non-null by pre-conditions.
No validation is performed in this function itself — this is consistent with the codebase convention where low-level allocation functions do not validate parameters (e.g., allocate_many_ui_elements_from__ui_manager also does not check). Validation of p_parent is delegated to set_ui_element_as__the_parent_of__this_ui_element, which debug_aborts on null. The lack of a null check on the return value of allocate_ui_element_from__ui_manager is also consistent with all other callers in this file.

Side Effects:
The function mutates the following state:
1. p_ui_manager's element pool and pointer array — a new slot is consumed (p_ptr_of__ui_element__latest_in_ptr_array is incremented).
2. The newly allocated UI_Element — initialized to defaults, then enabled.
3. p_ui_manager — marked as dirty via set_ui_manager_as__dirty.
4. p_parent->p_child — reassigned to the new child; any prior child's p_parent is set to null.
5. The new child's p_parent — set to p_parent; any prior parent's p_child is set to null.
6. The pointer array ordering — the child's entry is swapped with the parent's to ensure higher priority (earlier index) for the child.
7. The new child's hitbox AABB position — updated via set_position_3i32_of__ui_element, which also invokes any transformed handler if present (none at initialization time).
