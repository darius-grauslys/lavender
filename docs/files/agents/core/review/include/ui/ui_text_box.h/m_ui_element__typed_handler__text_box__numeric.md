m_ui_element__typed_handler__text_box__numeric — core/source/ui/ui_text_box.c, lines 188-206

A typed handler for UI text boxes that restricts input to numeric digits (0-9), first delegating special symbol handling (backspace, delete, escape, arrows) to the shared handler, then filtering non-digit symbols and appending valid digits.

Pre-conditions:
1. p_this_ui_text_box must be a non-null pointer to an initialized UI_Element of kind UI_Text_Box (or compatible), with pM_char_buffer allocated and size_of__char_buffer set appropriately.
2. p_game must be a non-null pointer to a valid Game instance (used to retrieve the UI manager).
3. p_graphics_window must be a non-null pointer to a valid Graphics_Window that has an associated UI_Manager.
4. symbol is an unsigned char representing the typed character (range 0-255).

Post-conditions:
1. If symbol is a special key (carriage return, line feed, escape, backspace, delete, arrow keys), the corresponding special handling is performed and the function returns without appending.
2. If symbol is not a digit ('0' through '9'), the function returns without modifying the text box.
3. If symbol is a digit ('0' through '9'), the digit is appended to p_this_ui_text_box's char buffer (subject to buffer capacity checks in append_symbol_into__ui_text), the cursor index is incremented, and the UI manager is marked dirty.
4. The UI_Element's internal state (pM_char_buffer, index_of__cursor_in__char_buffer) is mutated only when a valid digit is appended.

Correctness Verdict: Correct

Semantic Alignment:
The implementation fulfills the semantic intent of a numeric-only text box typed handler. The function first delegates to handle_special_symbols__text_box to process control characters (backspace, delete, escape, arrows), returning early if any special symbol was consumed. It then filters the remaining symbols to only accept ASCII digits '0' through '9' using the check `symbol < '0' || symbol > '9'`, which correctly includes both boundary characters (unlike the alphanumeric variant which uses strict inequalities `> '0'` and `< '9'`, incorrectly excluding '0' and '9'). Valid digits are appended via append_symbol_into__ui_text_box, which itself performs a buffer-full check. The logic is sound and matches the intended behavior.

Implementation Correctness:
Type compatibility — The symbol parameter is unsigned char, compared against '0' and '9' (int constants). The unsigned char is promoted to int for the comparison, which is safe for all values 0-255. The symbol is then passed to append_symbol_into__ui_text_box which expects char; this implicit unsigned char to char conversion is safe for ASCII digits (48-57). No truncation occurs.
Undefined behavior — No broken pointer arithmetic, no null dereference (null checks are handled by get_p_ui_manager_from__graphics_window in debug builds), no type punning, no out-of-bounds access. The append_symbol_into__ui_text function checks buffer capacity before writing.
Validation — No explicit null checks for p_this_ui_text_box, p_game, or p_graphics_window are performed in this function, which is consistent with the codebase pattern (e.g., the general m_ui_element__typed_handler__text_box also does not perform null checks). Null validation is delegated to get_p_ui_manager_from__graphics_window in debug builds. This is appropriate for the function's role as a handler.

Side Effects:
- Mutates p_this_ui_text_box's char buffer (pM_char_buffer) and cursor index (index_of__cursor_in__char_buffer) when a valid digit is appended.
- Marks the UI manager as dirty (via set_ui_manager_as__dirty called within append_symbol_into__ui_text) when a valid digit is appended.
- May mutate p_this_ui_text_box's focus state (via set_ui_element_as__NOT_focused) when special symbols like carriage return, line feed, or escape are received.
- May mutate p_this_ui_text_box's char buffer and cursor index when backspace or delete special symbols are received.
- No side effects when the symbol is a non-digit, non-special character (early return).
