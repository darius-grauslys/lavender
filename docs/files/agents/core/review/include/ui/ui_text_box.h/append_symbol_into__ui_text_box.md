append_symbol_into__ui_text_box — core/include/ui/ui_text_box.h

A thin inline wrapper that delegates to `append_symbol_into__ui_text`, forwarding the UI manager, element, and character symbol without modification.

Pre-conditions:
1. p_ui_manager must be a non-null pointer to a valid UI_Manager (needed to mark it dirty).
2. p_ui_text_box must be a non-null pointer to a valid UI_Element configured as a text box (i.e., it must have a valid pM_char_buffer, size_of__char_buffer, and index_of__cursor_in__char_buffer).
3. symbol is any char value; no range constraint.

Post-conditions:
1. If the text box's char buffer is full (cursor >= buffer size), the function returns early with a debug warning; no mutation occurs.
2. Otherwise, the UI_Manager is marked as dirty (set_ui_manager_as__dirty is called).
3. The symbol is written at the current cursor position in pM_char_buffer, and index_of__cursor_in__char_buffer is incremented by 1.

Correctness Verdict: Correct

Semantic Alignment:
The wrapper correctly forwards all three parameters to `append_symbol_into__ui_text` without any transformation, reordering, or omission. The delegation matches the semantic intent of appending a single character to a text box's buffer. No mismatch between intent and implementation.

Implementation Correctness:
Type compatibility — all parameter types match exactly: UI_Manager* → UI_Manager*, UI_Element* → UI_Element*, char → char. No implicit conversions or truncation.
No undefined behavior in the wrapper itself — no pointer arithmetic, no null dereference, no type punning. The wrapper performs no direct memory access; it delegates entirely to the callee.
No validation is needed at this wrapper level — this is a thin forwarding function. Validation (buffer-full check) is performed by the callee (`append_symbol_into__ui_text`).

Side Effects:
The wrapper itself has no direct side effects — it only calls the delegated function. The observable side effects (marking the UI manager dirty, writing to the char buffer, incrementing the cursor) are all produced by `append_symbol_into__ui_text`, which is outside this function's own implementation scope.
