detect_focus__strictly_under_cursor_in__ui_manager — core/source/ui/ui_manager.c

Ensures the currently focused UI element (or a newly detected one) is strictly under the cursor by verifying the cursor position falls within the element's hitbox. If the focused element is not under the cursor, it drops focus and re-detects a new element under the cursor.

Pre-conditions:
1. p_ui_manager must be a non-null pointer to an initialized UI_Manager with allocated members (pool and ptr array must be allocated via allocate_ui_manager__members).
2. p_game must be a non-null pointer to a valid Game instance with an initialized input system and hitbox context.
3. The UI_Manager must be registered in the game's hitbox context so that get_pV_hitbox_manager_from__hitbox_context can return a valid Hitbox_AABB_Manager.

Post-conditions:
1. Returns a pointer to a UI_Element that is focused and whose hitbox contains the current cursor position, or 0 if no such element exists.
2. If the previously focused element's hitbox does not contain the cursor, that element's focus is dropped (UI_FLAGS__BIT_IS_FOCUSED cleared, p_ui_manager->p_ui_element__focused set to 0) and a new element under the cursor is focused via detect_focus_in__ui_manager.
3. The UI_Manager's p_ui_element__focused field is updated to reflect the current focus state.

Correctness Verdict: Incorrect

Semantic Alignment:
The implementation correctly captures the intent of "detect focus strictly under cursor." The logic flow is:
1. Resolve the hitbox AABB manager from the game's hitbox context.
2. Call detect_focus_in__ui_manager to get a candidate focused element (either a pre-existing focused element or one found under the cursor).
3. If no candidate, return 0.
4. Check whether the current cursor position is inside the candidate's hitbox.
5. If not inside, drop focus and re-detect via detect_focus_in__ui_manager.
6. Return the (re-detected) focused element.

This matches the semantic intent.

Implementation Correctness:
- Null pointer dereference (BUG): The function calls get_p_hitbox_aabb_of__ui_element(p_hitbox_aabb_manager, p_ui_element__focused) and passes the result directly to is_vector_3i32_inside__hitbox_aabb without checking for null. If the focused UI element has no associated hitbox (e.g., the hitbox was removed after focus was set, or the element was returned as previously-focused by detect_focus_in__ui_manager without a hitbox), get_p_hitbox_aabb_of__ui_element returns null. is_vector_3i32_inside__hitbox_aabb does not handle null hitbox pointers — it calls get_aa_bb_as__vectors_3i32_from__hitbox_aabb, which calls initialize_vector_3i32_as__aa_bb, which only has a debug-mode null guard that prints an error and returns early without initializing the output vectors. In debug builds this leads to use of uninitialized variables (undefined behavior); in release builds (NDEBUG defined) it leads to a direct null pointer dereference and crash. The sibling function get_highest_priority_ui_element_thats__under_this_ui_element properly checks if (!p_hitbox_aabb) { continue; }, but detect_focus__strictly_under_cursor_in__ui_manager does not follow this pattern.
- Type compatibility: All parameter types match target field/function types exactly. No implicit conversions or truncation.
- No out-of-bounds access: The function does not directly index into arrays.
- Validation: No debug null checks for p_ui_manager or p_game, which is inconsistent with other functions in the file (e.g., initialize_ui_manager, compose_all_ui_elements_in__ui_manager) but is consistent with detect_focus_in__ui_manager and get_highest_priority_ui_element_thats__under_the_cursor which also lack such checks. This is acceptable given the internal usage context, but the missing hitbox null check is not.

Side Effects:
1. May drop focus from the previously focused UI element: clears the UI_FLAGS__BIT_IS_FOCUSED flag on the element (via set_ui_element_as__NOT_focused) and sets p_ui_manager->p_ui_element__focused to 0 (via drop_ui_element_focus_for__ui_manager).
2. May set focus on a new UI element: sets the UI_FLAGS__BIT_IS_FOCUSED flag and updates p_ui_manager->p_ui_element__focused (via detect_focus_in__ui_manager -> set_p_ui_element_as__focused_in__ui_manager).
3. May call set_input_mode_of__input (via detect_focus_in__ui_manager) to set the input mode to INPUT_MODE__NORMAL when a new element is searched for.
4. Reads the cursor position from the game's input (p_game->p_input->cursor__3i32).
