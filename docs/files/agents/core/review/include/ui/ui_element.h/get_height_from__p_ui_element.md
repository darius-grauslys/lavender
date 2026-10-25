get_height_from__p_ui_element — core/include/ui/ui_element.h

Retrieves the height of a UI_Element by looking up its associated Hitbox_AABB via the hitbox_aabb_manager and returning the height field of that hitbox.

Pre-conditions:
1. p_hitbox_aabb_manager must be a non-null pointer to a valid Hitbox_AABB_Manager. (Debug builds of the callee get_p_hitbox_aabb_by__uuid_u32_from__hitbox_aabb_manager check for this; release builds do not.)
2. p_ui_element must be a non-null pointer to a valid UI_Element. The UI_Element must have a valid Serialization_Header as its first member (which it does by struct definition), and its uuid must correspond to a registered hitbox in the manager. No null check is performed on p_ui_element before GET_UUID_P dereferences it.
3. The UI_Element's UUID must map to an existing Hitbox_AABB in the manager's pool. If no hitbox is found, get_p_hitbox_aabb_of__ui_element returns NULL, and get_height_u32_of__hitbox_aabb will dereference NULL (debug builds return 0; release builds are undefined behavior).

Post-conditions:
1. Returns the height__quantity_u32 field of the Hitbox_AABB associated with the given UI_Element's UUID.
2. No objects are mutated.

Correctness Verdict: Correct

Semantic Alignment:
The implementation correctly fulfills its semantic intent: it retrieves the height of a UI element by first resolving the UI_Element's UUID to its associated Hitbox_AABB via the hitbox_aabb_manager, then reading the height field from that hitbox. The delegation chain (get_p_hitbox_aabb_of__ui_element → get_p_hitbox_aabb_by__uuid_u32_from__hitbox_aabb_manager → get_height_u32_of__hitbox_aabb) is correct and consistent with the pattern used by sibling accessors such as get_width_from__p_ui_element and get_position_3i32_from__p_ui_element.

Implementation Correctness:
Type compatibility — the return type Quantity__u32 matches the return type of get_height_u32_of__hitbox_aabb. The Hitbox_AABB* returned by get_p_hitbox_aabb_of__ui_element is passed directly to get_height_u32_of__hitbox_aabb which expects Hitbox_AABB* — exact type match, no implicit conversion.
Undefined behavior — the function itself performs no pointer arithmetic, no direct dereference of its parameters, and no out-of-bounds access. However, the callee get_p_hitbox_aabb_of__ui_element dereferences p_ui_element via the GET_UUID_P macro without a null check, and get_height_u32_of__hitbox_aabb dereferences the returned hitbox pointer without a null check in release builds. These are latent risks in the callee chain, not in this function's own body.
Validation — no validation is performed within this function. Validation is appropriately delegated to the callee functions (get_p_hitbox_aabb_of__ui_element and get_height_u32_of__hitbox_aabb), which perform debug-only null checks. This is consistent with the Lavender pattern for low-level accessor functions.

Side Effects:
No side effects — this is a pure read accessor. No objects are mutated, no state is changed.
