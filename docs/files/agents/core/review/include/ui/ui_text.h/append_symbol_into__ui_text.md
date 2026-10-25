append_symbol_into__ui_text — core/source/ui/ui_text.c

Writes a single character into the UI text element's char buffer at the current cursor position, then advances the cursor by one.

Pre-conditions:
1. p_ui_manager must be a non-null pointer to a valid UI_Manager.
2. p_ui_text must be a non-null pointer to a UI_Element of kind UI_Element_Kind__Text or UI_Element_Kind__Text_Box (so that the union member containing pM_char_buffer, size_of__char_buffer, and index_of__cursor_in__char_buffer is active).
3. p_ui_text->pM_char_buffer must be non-null (allocated and writable).
4. p_ui_text->size_of__char_buffer must accurately reflect the allocated size of pM_char_buffer.
5. p_ui_text->index_of__cursor_in__char_buffer must be a valid cursor position (0 <= index <= size_of__char_buffer).

Post-conditions:
1. If p_ui_text->index_of__cursor_in__char_buffer >= p_ui_text->size_of__char_buffer (buffer is full), the function returns early with a verbose debug warning. No state is mutated.
2. Otherwise, p_ui_text->pM_char_buffer[index_of__cursor_in__char_buffer] is set to the value of symbol, and p_ui_text->index_of__cursor_in__char_buffer is incremented by 1.
3. The UI_Manager is marked dirty via set_ui_manager_as__dirty(p_ui_manager), signalling that a recomposition is needed.

Correctness Verdict: Correct

Semantic Alignment:
The function writes a symbol at the current cursor position in the char buffer and advances the cursor, matching the semantic intent of "append_symbol_into__ui_text" within this codebase's convention (where "append" means writing at the cursor position, as seen in the related append_c_str_into__ui_text). The bounds check correctly prevents out-of-bounds writes when the buffer is full. The cursor is only advanced after a successful write, ensuring consistency.

Implementation Correctness:
Type compatibility — p_ui_text->pM_char_buffer is char *, indexed by index_of__cursor_in__char_buffer (Index__u32 / uint32_t). The index is used as a subscript into the char array, which is well-defined. symbol (char) is assigned to a char array element — no conversion or truncation.
Undefined behavior — no broken pointer arithmetic, no null dereference (pre-conditions ensure non-null), no type punning, no out-of-bounds access. The bounds check (index >= size_of__char_buffer) guards the write, ensuring the index is always < size_of__char_buffer before dereferencing pM_char_buffer.
Validation — the bounds check is appropriate for the function's role. Null-pointer validation is not performed, which is consistent with the codebase convention (other functions in ui_text.c, such as set_cursor_of__ui_text and append_c_str_into__ui_text, also do not null-check their parameters).

Side Effects:
1. Marks the UI_Manager as dirty (sets UI_MANAGER_FLAG__IS_DIRTY on p_ui_manager->ui_manager_flags__u8).
2. Mutates p_ui_text->pM_char_buffer by writing symbol at the cursor index.
3. Mutates p_ui_text->index_of__cursor_in__char_buffer by incrementing it by 1.
