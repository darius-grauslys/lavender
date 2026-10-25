get_y_i32_from__p_ui_element — core/include/ui/ui_element.h

Retrieves the Y-coordinate of a UI element's associated hitbox AABB as a signed 32-bit index, by looking up the hitbox via the UI element's UUID in the hitbox manager.

Pre-conditions:
1. p_hitbox_aabb_manager must be a non-null pointer to an initialized Hitbox_AABB_Manager. In debug builds, a null pointer is detected and logged; in release builds, passing NULL results in undefined behavior (dereferenced inside dehash_identitier_u32_in__contigious_array).
2. p_ui_element must be a non-null pointer to a valid UI_Element with a valid UUID. The UUID is extracted via GET_UUID_P (which dereferences the pointer); a null p_ui_element causes undefined behavior in release builds.
3. The UI element's UUID must correspond to an allocated hitbox in the manager's pool. If no hitbox is found, get_p_hitbox_aabb_by__uuid_u32_from__hitbox_aabb_manager returns NULL, which is handled by debug-only null checks in the callee chain (get_y_i32_from__hitbox_aabb and get_position_3i32F4_of__hitbox_aabb). In release builds, a NULL hitbox pointer would cause undefined behavior.

Post-conditions:
1. Returns the Y-coordinate of the UI element's associated hitbox AABB as a Signed_Index__i32.
2. If any pointer in the call chain is NULL (in debug builds), an error is logged and 0 is returned.
3. The function does not modify any state — it is a pure query.

Correctness Verdict: Correct

Semantic Alignment:
The implementation correctly fulfills the semantic intent of retrieving the Y-coordinate of a UI element. It delegates to get_p_hitbox_aabb_of__ui_element to resolve the hitbox via UUID lookup, then calls get_y_i32_from__hitbox_aabb to extract the Y coordinate. This follows the exact same delegation pattern as its sibling functions get_x_i32_from__p_ui_element and get_z_i32_from__p_ui_element, ensuring consistency. The computation chain (UUID lookup → hitbox retrieval → position extraction → Y component) matches the expected semantic flow.

Implementation Correctness:
Type compatibility — the return type Signed_Index__i32 matches the return type of get_y_i32_from__hitbox_aabb. The parameter types (Hitbox_AABB_Manager * and UI_Element *) match the callee's expected types exactly. No implicit conversions or truncation occur.
Undefined behavior — in release builds (NDEBUG defined), null pointer checks are compiled out. If p_ui_element is NULL, GET_UUID_P dereferences it directly, causing UB. If the hitbox lookup returns NULL, get_y_i32_from__hitbox_aabb dereferences it via get_position_3i32F4_of__hitbox_aabb, also causing UB. However, this is consistent with the codebase-wide pattern where null validation is debug-only and the caller is responsible for ensuring valid inputs.
Validation — no validation is performed in this function itself. This is appropriate for a low-level inline accessor; validation responsibility lies with the caller, consistent with the Lavender engine's pattern of debug-only defensive checks in leaf functions.

Side Effects:
No side effects. The function is a pure query that reads from the hitbox manager's pool and returns a value without modifying any state.
