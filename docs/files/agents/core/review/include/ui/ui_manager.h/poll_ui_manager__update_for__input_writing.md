poll_ui_manager__update_for__input_writing — core/source/ui/ui_manager.c

Routes text input (writing mode) to the focused UI element's typed handler, and transitions input mode back to NORMAL when focus is lost.

Pre-conditions:
1. p_ui_manager must be a non-null pointer to a fully initialized UI_Manager (members allocated via allocate_ui_manager__members).
2. p_game must be a non-null pointer to an initialized Game with a valid Input subsystem.
3. p_graphics_window must be a non-null pointer to a valid Graphics_Window.
4. The caller (poll_ui_manager__update) must only invoke this function when the input mode is INPUT_MODE__WRITING.

Post-conditions:
1. If no focused UI element exists, or the focused UI element has no typed handler: the input mode is set to INPUT_MODE__NORMAL and the function returns early. The focused element pointer in p_ui_manager may be cleared to 0 as a side effect of does_ui_manager_have__focused_ui_element / get_p_ui_element__focused_of__ui_manager.
2. If a non-zero symbol was polled from the input writing buffer and the focused UI element has a typed handler: the typed handler is invoked with the focused UI element, p_game, p_graphics_window, and the symbol. The symbol is consumed from the input writing buffer as a side effect of poll_input_for__writing.
3. If the focused UI element is no longer focused after processing (e.g., the typed handler unfocused it): the input mode is set to INPUT_MODE__NORMAL.

Correctness Verdict: Correct

Semantic Alignment:
The implementation correctly fulfills its semantic intent. Text input is routed to the focused UI element's typed handler when one exists, and input mode transitions back to NORMAL when there is no valid target or when focus is lost after processing. The logic flow (check focus → poll symbol → invoke handler → check focus again) matches the intended behavior.

Semantic note on initialization: This function does not perform initialization in either the Lavender pool-cleanup sense or the RAII sense. It is a polling/update function that delegates to other functions for state management.

Implementation Correctness:
Type compatibility — The local variable `char symbol` stores the return value of `poll_input_for__writing`, which returns `unsigned char`. This is an implicit conversion from unsigned char to char. On platforms where char is signed, values above 127 would be stored as negative values, but the round-trip conversion (unsigned char → char → unsigned char when passed to the m_UI_Typed handler) preserves the original value. While not a correctness issue, it is a minor type mismatch that could be improved by declaring `symbol` as `unsigned char`.

Undefined behavior — No undefined behavior detected. No null pointer dereferences (p_ui_element__focused is checked before use; the typed handler is verified non-null via does_ui_element_have__typed_handler before being retrieved and invoked). No out-of-bounds access. No type punning.

Validation — The function performs no null checks on p_ui_manager, p_game, or p_graphics_window. This is consistent with other internal polling functions in the same file (e.g., poll_ui_manager__update_for__drag, poll_ui_manager__update_for__held). Validation is the responsibility of the caller (poll_ui_manager__update) and higher-level game initialization.

Dead code — The variable `bool has_ui_element__focus` is computed via `does_ui_manager_have__focused_ui_element(p_ui_manager)` but is never read. The side effect of this call (clearing p_ui_manager->p_ui_element__focused to 0 when the element is no longer focused) is still useful, but the subsequent call to `get_p_ui_element__focused_of__ui_manager` performs the same side effect, making the first call's return value redundant. This is a code quality issue (dead variable) but does not affect correctness.

Side Effects:
1. May clear p_ui_manager->p_ui_element__focused to 0 (via does_ui_manager_have__focused_ui_element and get_p_ui_element__focused_of__ui_manager) when the focused UI element is no longer focused.
2. Consumes a character from the input writing buffer (via poll_input_for__writing), which reads from index_of__writing_buffer__read, stores it as last_symbol, clears the buffer slot, and advances the read index with wraparound.
3. May invoke the focused UI element's m_ui_typed_handler callback, which can mutate the UI element, game state, and graphics window (out of scope to trace callee internals).
4. May set the input mode of p_game's Input to INPUT_MODE__NORMAL via set_input_mode_of__input.
