poll_ui_manager__update_for__drag — core/source/ui/ui_manager.c

Polls the UI manager for drag updates. Detects the focused UI element, verifies it has a dragged handler (falling back to finding one strictly under the cursor), optionally marks the element as being dragged if it was being held, and invokes the element's dragged handler.

Pre-conditions:
1. p_game must be non-null (used to access input and hitbox context via detect_focus_in__ui_manager and detect_focus__strictly_under_cursor_in__ui_manager).
2. p_graphics_window must be non-null (passed through to the dragged handler).
3. p_ui_manager must be non-null and properly initialized with allocated members (used for focus detection, element lookup, and storing the focused element pointer).
4. p_ui_manager->pM_ptr_array_of__ui_elements must be a valid array of UI_Element pointers (used by get_highest_priority_ui_element_thats__under_the_cursor).

Post-conditions:
1. If no focused UI element with a dragged handler can be found (neither the initially focused element nor any element strictly under the cursor), the function returns early without invoking any handler.
2. If the focused element is being held (UI_FLAGS__BIT_IS_BEING_HELD is set), its UI_FLAGS__BIT_IS_BEING_DRAGGED flag is set via set_ui_element_as__being_dragged.
3. The m_ui_dragged_handler of the focused element is invoked with p_ui_manager->p_ui_element__focused as the first argument (p_this_ui_element), p_game as the second, and p_graphics_window as the third.
4. p_ui_manager->p_ui_element__focused may be updated as a side effect of focus detection (detect_focus_in__ui_manager sets it via set_p_ui_element_as__focused_in__ui_manager; detect_focus__strictly_under_cursor_in__ui_manager may drop and re-detect focus).

Correctness Verdict: Correct

Semantic Alignment:
The implementation fulfills its semantic intent. It correctly:
- Detects focus via detect_focus_in__ui_manager, which returns the manager's focused element or finds a new one under the cursor.
- Falls back to detect_focus__strictly_under_cursor_in__ui_manager when the focused element lacks a dragged handler, ensuring the element is strictly under the cursor (not just previously focused).
- Guards the handler invocation with does_ui_element_have__dragged_handler checks at both branches — the initial focused element and the fallback element are both verified to have a non-null handler before invocation.
- Sets the "being dragged" flag (UI_FLAGS__BIT_IS_BEING_DRAGGED) only when the element is "being held" (UI_FLAGS__BIT_IS_BEING_HELD), which is the correct gating condition for transitioning from a hold to a drag.
- Invokes the handler with the correct element reference and matching parameter types.

One notable detail: the handler is invoked on the local p_ui_element__focused but receives p_ui_manager->p_ui_element__focused as its first argument. These are guaranteed to be the same pointer at this point because both detect_focus_in__ui_manager and detect_focus__strictly_under_cursor_in__ui_manager synchronize p_ui_manager->p_ui_element__focused with their return values (via set_p_ui_element_as__focused_in__ui_manager). This is consistent with the pattern used in poll_ui_manager__update_for__held and handle_drop_in__ui_manager in the same file, so it is not a bug, though it is a redundancy.

This is NOT a Lavender-style initialization function (the name contains "update" and "drag", not "init"/"initialize"/"reset"), so the initialization-vs-RAII distinction does not apply.

Implementation Correctness:
Type compatibility — The m_UI_Dragged typedef is void (*)(UI_Element *, Game *, Graphics_Window *). The call passes p_ui_manager->p_ui_element__focused (UI_Element *), p_game (Game *), and p_graphics_window (Graphics_Window *), which match exactly. No implicit conversions or truncation.
Undefined behavior — No null dereference. p_ui_element__focused is null-checked before use (line 380-381). The handler invocation is guarded by does_ui_element_have__dragged_handler which checks both pointer validity (p_ui_element != NULL) and handler non-null (p_ui_element->m_ui_dragged_handler != NULL). p_ui_manager->p_ui_element__focused is guaranteed non-null at the handler call point because the focus detection functions only return non-null when they also set the manager's focused pointer to that same element. No out-of-bounds access, no type punning, no broken pointer arithmetic.
Validation — Appropriate for the function's role. Null checks on the focused element are performed. Null checks on p_game, p_graphics_window, and p_ui_manager are the caller's responsibility, consistent with the rest of the file (e.g., poll_ui_manager__update does not null-check p_ui_manager before passing it).

Side Effects:
1. May set input mode to INPUT_MODE__NORMAL (via detect_focus_in__ui_manager calling set_input_mode_of__input).
2. May modify p_ui_manager->p_ui_element__focused (via set_p_ui_element_as__focused_in__ui_manager inside detect_focus_in__ui_manager).
3. May clear and re-set focus on UI elements (via drop_ui_element_focus_for__ui_manager inside detect_focus__strictly_under_cursor_in__ui_manager, which calls set_ui_element_as__NOT_focused on the old element).
4. May set the UI_FLAGS__BIT_IS_BEING_DRAGGED flag on the focused element (via set_ui_element_as__being_dragged).
5. Invokes the element's m_ui_dragged_handler, which may have arbitrary side effects (e.g., repositioning the element, as seen in m_ui_draggable__dragged_handler__default which calls set_position_3i32_of__ui_element).
