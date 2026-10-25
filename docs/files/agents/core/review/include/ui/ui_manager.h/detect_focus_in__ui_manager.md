detect_focus_in__ui_manager — core/source/ui/ui_manager.c

Detects and caches the UI element currently under the cursor as the focused element in the UI_Manager, or returns the already-cached focused element if it remains valid.

Pre-conditions:
1. p_ui_manager must be a non-null pointer to an initialized UI_Manager with its member arrays allocated via allocate_ui_manager__members.
2. p_game must be a non-null pointer to a valid Game with an initialized Input subsystem (accessible via get_p_input_from__game).
3. p_ui_manager->pM_ptr_array_of__ui_elements must be allocated and populated with valid UI_Element pointers (or null entries).
4. p_ui_manager->pM_ui_element_pool must be allocated for hitbox lookups performed by get_highest_priority_ui_element_thats__under_the_cursor.
5. The UI_Element_Hitbox_AABB_Manager associated with p_ui_manager must be allocated in the game's hitbox context.

Post-conditions:
1. If a valid focused element already exists (non-null pointer with IS_FOCUSED flag set), the function returns it without re-detecting.
2. If no valid focused element exists, the function resets input mode to INPUT_MODE__NORMAL and searches for the highest-priority UI element under the cursor.
3. If a new element is found under the cursor, p_ui_manager->p_ui_element__focused is updated to point to that element, and the element pointer is returned.
4. If no element is found under the cursor, the function returns 0 (null).
5. BUG: The IS_FOCUSED flag (UI_FLAGS__BIT_IS_FOCUSED) is NOT set on the detected UI_Element. The helper set_p_ui_element_as__focused_in__ui_manager only assigns the p_ui_element__focused pointer in UI_Manager, but never calls set_ui_element_as__focused to set the flag on the element itself. This is asymmetric with drop_ui_element_focus_for__ui_manager, which both clears the flag (via set_ui_element_as__NOT_focused) and nulls the pointer.

Correctness Verdict: Incorrect

Semantic Alignment:
The function's intent is to detect which UI element is under the cursor and cache it as the focused element. The caching mechanism is broken because the IS_FOCUSED flag is never set on the element. On every subsequent call to get_p_ui_element__focused_of__ui_manager, the function checks is_ui_element__focused(p_ui_manager->p_ui_element__focused), which returns false (since the flag was never set), causing the cached pointer to be cleared to 0. This means:

- The function re-detects focus on every single call, defeating the purpose of caching.
- The input mode is reset to INPUT_MODE__NORMAL on every call, even when the cursor hasn't moved or the focused element hasn't changed.
- The focused element's IS_FOCUSED flag remains unset, so any code that checks is_ui_element__focused on the element will see it as not focused.

The fix is to call set_ui_element_as__focused(p_ui_element) either in set_p_ui_element_as__focused_in__ui_manager (the static inline helper) or directly in detect_focus_in__ui_manager before returning. Adding it to the helper would make it symmetric with drop_ui_element_focus_for__ui_manager, which clears both the flag and the pointer.

Implementation Correctness:
Type compatibility — all parameter types match their target field types. UI_Manager * and Game * are passed consistently. The return type UI_Element * matches the internal variable type.
No undefined behavior — no broken pointer arithmetic, no null dereference (assuming pre-conditions are met), no type punning, no out-of-bounds access. The function relies on get_p_input_from__game(p_game) returning a valid Input *, which is expected per the game's initialization contract.
Validation — no null checks for p_ui_manager or p_game, which is consistent with the codebase pattern for non-debug builds (other functions like initialize_ui_manager do debug-only null checks). However, detect_focus_in__ui_manager has no debug null checks at all, unlike sibling functions such as compose_all_ui_elements_in__ui_manager which do include them.

Side Effects:
1. Mutates p_ui_manager->p_ui_element__focused (sets the pointer to the detected or cached element).
2. Mutates p_input->input_mode__u8 to INPUT_MODE__NORMAL when the previously focused element is invalid (null or not focused flag).
3. BUG: Does NOT set UI_FLAGS__BIT_IS_FOCUSED on the UI_Element — the focused flag is never set, which causes the caching to fail on subsequent calls.
