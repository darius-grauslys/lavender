poll_ui_manager__update_for__held — core/source/ui/ui_manager.c, lines 407-435

Polls the UI manager for a held-input event on the currently focused UI element, delegating to drag handling if the element is being dragged, or invoking the element's held handler otherwise.

Pre-conditions:
1. p_game must be a non-null pointer to a valid Game object.
2. p_graphics_window must be a non-null pointer to a valid Graphics_Window object.
3. p_ui_manager must be a non-null pointer to a valid UI_Manager object.
4. No null-check is performed on the parameters; validation is the caller's responsibility (consistent with the codebase convention).

Post-conditions:
1. If no UI element is focused (detect_focus_in__ui_manager returns NULL), the function returns without side effects beyond those of detect_focus_in__ui_manager.
2. If the focused UI element is being dragged, poll_ui_manager__update_for__drag is invoked and the function returns.
3. If the focused UI element has no held handler (m_ui_held_handler is NULL), the function returns without invoking any handler.
4. If the focused UI element has a held handler, m_ui_held_handler is invoked with the focused UI element (via p_ui_manager->p_ui_element__focused), p_game, and p_graphics_window as arguments.
5. p_ui_manager->p_ui_element__focused may be updated as a side effect of detect_focus_in__ui_manager.

Correctness Verdict: Correct

Semantic Alignment:
The implementation fulfills the semantic intent of polling for a held event on the focused UI element. The logic flow is sound:
  - It first detects focus via detect_focus_in__ui_manager, which also sets p_ui_manager->p_ui_element__focused.
  - It correctly short-circuits if the element is being dragged, delegating to the drag handler.
  - It correctly short-circuits if no held handler is present.
  - It invokes the held handler with the correct arguments: the focused UI element, the game, and the graphics window.

The handler invocation passes p_ui_manager->p_ui_element__focused as the first argument. Since detect_focus_in__ui_manager calls set_p_ui_element_as__focused_in__ui_manager to set p_ui_manager->p_ui_element__focused to the same value it returns, this is equivalent to passing p_ui_element__focused directly. This matches the pattern used in poll_ui_manager__update_for__drag, which also passes p_ui_manager->p_ui_element__focused to its handler.

Implementation Correctness:
Type compatibility — the m_ui_held_handler field is of type m_UI_Held, which is defined as:
    typedef void (*m_UI_Held)(
            UI_Element *p_this_ui_element,
            Game *p_game,
            Graphics_Window *p_gfx_window);
The invocation passes:
    - p_ui_manager->p_ui_element__focused (UI_Element *) → matches UI_Element *p_this_ui_element
    - p_game (Game *) → matches Game *p_game
    - p_graphics_window (Graphics_Window *) → matches Graphics_Window *p_gfx_window
All types match exactly. No implicit conversions or truncation.

Undefined behavior — no broken pointer arithmetic, no null dereference (p_ui_element__focused is checked before use), no type punning, no out-of-bounds access.

Validation — no validation is performed on the three pointer parameters. This is appropriate for the function's role as a low-level polling function; validation is the caller's responsibility, consistent with the rest of the ui_manager module.

Side Effects:
1. detect_focus_in__ui_manager may set p_ui_manager->p_ui_element__focused and may set the input mode to INPUT_MODE__NORMAL on the game's input.
2. If the element is being dragged, poll_ui_manager__update_for__drag is invoked, which has its own observable side effects (invoking the dragged handler).
3. If a held handler exists, m_ui_held_handler is invoked, which may mutate game state, UI elements, or graphics state depending on the handler's implementation.
