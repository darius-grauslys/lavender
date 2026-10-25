allocate_hitbox_for__ui_element — core/source/ui/ui_element.c, lines 157-197

Allocates a Hitbox_AABB from the graphics window's hitbox manager pool, assigns it the UUID of the given UI_Element, sets its size and position, and then invokes the UI_Element's transformed handler (if present) so that child elements can be repositioned relative to the new hitbox position.

Pre-conditions:
1. p_game must be a non-null pointer to a valid Game object. It is used to retrieve the hitbox context via get_pV_hitbox_manager_from__graphics_window.
2. p_graphics_window must be a non-null pointer to a valid Graphics_Window. It is used to retrieve the hitbox AABB manager. However, the graphics window may not have a hitbox manager allocated; in that case get_pV_hitbox_manager_from__graphics_window returns NULL.
3. p_ui_element must be a non-null pointer to a valid UI_Element. It is used in GET_UUID_P(p_ui_element), which dereferences the pointer as a Serialization_Header to read its UUID. No null check is performed before this dereference.
4. width_of__hitbox__u32 and height_of__hitbox__u32 are Quantity__u32 (u32) values with no enforced range constraint.
5. position_of__hitbox__3i32 is a Vector__3i32 (integer position) with no enforced range constraint.

Post-conditions:
1. A new Hitbox_AABB is allocated from the hitbox manager's pool, associated with p_ui_element's UUID.
2. The allocated hitbox's width and height are set to width_of__hitbox__u32 and height_of__hitbox__u32 respectively (via set_size_of__hitbox_aabb, which also marks the hitbox dirty).
3. The allocated hitbox's position is set to position_of__hitbox__3i32 (via set_hitbox_aabb__position_with__3i32, which converts the integer position to fixed-point i32F4 and marks the hitbox dirty).
4. If p_ui_element has a transformed handler installed, that handler is invoked with p_ui_element, the newly allocated hitbox, position_of__hitbox__3i32, p_game, and p_graphics_window. The handler's behavior (e.g., repositioning child elements) is implementation-defined.

Correctness Verdict: Incorrect

Semantic Alignment:
The function's intent is to allocate and initialize a hitbox for a UI element and then notify the element's transform handler so child elements can be repositioned. The sequence of operations — allocate, set size, set position, invoke transform handler — is semantically correct and matches the comment explaining why position must be set before the transform handler runs (the handler may need to read the hitbox's current position). The call to the transformed handler uses the correct signature and argument order matching the m_UI_Transformed typedef. The semantic intent is fulfilled by the implementation's logic flow.

However, the function contains critical null-safety defects that can cause undefined behavior, violating the semantic contract (see Implementation Correctness).

Implementation Correctness:
Type compatibility — All parameter and return types are compatible:
- get_pV_hitbox_manager_from__graphics_window returns void*, cast to Hitbox_AABB_Manager* — valid C cast.
- allocate_hitbox_aabb_from__hitbox_aabb_manager expects (Hitbox_AABB_Manager*, Identifier__u32) and receives (Hitbox_AABB_Manager*, GET_UUID_P(p_ui_element)) where GET_UUID_P returns Identifier__u32 — exact match.
- set_size_of__hitbox_aabb expects (Hitbox_AABB*, Quantity__u32, Quantity__u32) and receives (p_hitbox_aabb, width_of__hitbox__u32, height_of__hitbox__u32) — exact match.
- set_hitbox_aabb__position_with__3i32 expects (Hitbox_AABB*, Vector__3i32) and receives (p_hitbox_aabb, position_of__hitbox__3i32) — exact match.
- The transformed handler call passes (UI_Element*, Hitbox_AABB*, Vector__3i32, Game*, Graphics_Window*) matching the m_UI_Transformed typedef — exact match.

Undefined behavior — Three null-safety defects:

1. (Critical) Missing NULL check on p_hitbox_aabb: allocate_hitbox_aabb_from__hitbox_aabb_manager can return NULL when:
   - p_hitbox_aabb_manager is NULL (the function has a debug-only null check at hitbox_aabb_manager.c:198-202, but in release builds it dereferences the null manager pointer).
   - The hitbox pool is full (hitbox_aabb_manager.c:204-208).
   - A UUID collision is detected (hitbox_aabb_manager.c:216-219).
   The return value is used immediately without any null check. In release builds (NDEBUG defined), set_size_of__hitbox_aabb and set_hitbox_aabb__position_with__3i32 only have debug-only null guards (hitbox_aabb.h:212-216 and hitbox_aabb.c:94-98 respectively), so a NULL p_hitbox_aabb would be dereferenced, causing undefined behavior. The sibling function set_ui_element__hitbox (ui_element.c:330-332) correctly checks `if (!p_hitbox_aabb)` and returns with an error message. The sibling function m_ui_element__dispose_handler__default (ui_element.c:102-103) also checks `if (p_hitbox_aabb)` before proceeding.

2. (Critical) Missing NULL check on p_hitbox_aabb_manager: get_pV_hitbox_manager_from__graphics_window (graphics_window.h:274-280) calls get_pV_hitbox_manager_from__hitbox_context, which can return NULL if the graphics window's uuid_of__hitbox_manager does not map to a valid manager. The code passes this potentially-NULL pointer directly to allocate_hitbox_aabb_from__hitbox_aabb_manager. While that function has a debug-only null check, in release builds it dereferences the null pointer at hitbox_aabb_manager.c:204-206 (`p_hitbox_aabb_manager->index_of__next_hitbox_aabb_in__records >= p_hitbox_aabb_manager->quantity_of__hitboxes`). The sibling function m_ui_element__dispose_handler__default (ui_element.c:97) correctly checks `if (p_hitbox_aabb_manager)` before proceeding.

3. (Critical) Missing NULL check on p_ui_element: GET_UUID_P(p_ui_element) dereferences p_ui_element by casting it to Serialization_Header* and accessing ->uuid. This occurs before the does_ui_element_have__transformed_handler check (which does null-check p_ui_element at ui_element.h:614). If p_ui_element is NULL, this is undefined behavior.

Validation — The function performs no validation of its pointer parameters. The codebase pattern (seen in update_ui_element_origin__relative_to at ui_element.c:503-507, and set_ui_element__hitbox at ui_element.c:326-332) is to check for null pointers and return early with a debug_error message. This function does not follow that pattern.

Side Effects:
1. Mutates the hitbox AABB pool via allocate_hitbox_aabb_from__hitbox_aabb_manager: increments index_of__next_hitbox_aabb_in__records and assigns the hitbox into pM_ptr_array_of__hitbox_records.
2. Mutates the allocated Hitbox_AABB: sets width__quantity_u32, height__quantity_u32, position__3i32F4 (x, y, z), and hitbox_aabb_flags__u8 (dirty bit set).
3. May invoke the UI_Element's transformed handler, which can have arbitrary side effects (e.g., recursively setting positions of child UI elements, as in m_ui_element__transformed_handler__default at ui_element.c:451-465).
4. Does not modify p_ui_element itself (only reads its UUID and handler pointer).

Issues Found:
1. (Critical) Missing NULL check on p_hitbox_aabb after allocate_hitbox_aabb_from__hitbox_aabb_manager returns. The function proceeds to call set_size_of__hitbox_aabb and set_hitbox_aabb__position_with__3i32 with a potentially-NULL pointer. In release builds, both callees only have debug-only null guards, so a NULL p_hitbox_aabb causes null pointer dereference. Recommend adding: `if (!p_hitbox_aabb) { debug_error("allocate_hitbox_for__ui_element, failed to allocate hitbox."); return; }` after the allocation call, matching the pattern in set_ui_element__hitbox (ui_element.c:330-332).
2. (Critical) Missing NULL check on p_hitbox_aabb_manager before passing to allocate_hitbox_aabb_from__hitbox_aabb_manager. Recommend adding a guard `if (!p_hitbox_aabb_manager) { debug_error("allocate_hitbox_for__ui_element, no hitbox manager."); return; }`, matching the pattern in m_ui_element__dispose_handler__default (ui_element.c:97).
3. (Critical) Missing NULL check on p_ui_element before GET_UUID_P(p_ui_element). The macro dereferences the pointer unconditionally. Recommend adding a null check for p_ui_element at the top of the function, consistent with the pattern in update_ui_element_origin__relative_to (ui_element.c:503-507).