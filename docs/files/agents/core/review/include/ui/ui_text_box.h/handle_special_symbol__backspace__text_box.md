handle_special_symbol__backspace__text_box — core/source/ui/ui_text_box.c, lines 81-103

Removes the character immediately before the cursor in a text box's char buffer, shifts all subsequent characters left by one position, decrements the cursor index, and null-terminates the final buffer position.

Pre-conditions:
1. p_this_ui_text_box must be a non-null pointer to a valid, initialized UI_Element of kind UI_Element_Kind__Text_Box (or UI_Element_Kind__Text), with its union fields (pM_char_buffer, size_of__char_buffer, index_of__cursor_in__char_buffer) properly set.
2. p_game is passed for API consistency but is not used by this function.
3. index_of__cursor_in__char_buffer must be >= 0 (it is a uint32_t, so always non-negative). If it is 0, the function returns early.
4. size_of__char_buffer must be >= 0. If it is 0, the function returns early.
5. When index_of__cursor_in__char_buffer > 0, the buffer must contain at least one character before the cursor (i.e., cursor-1 must reference a valid character position within the buffer).

Post-conditions:
1. If index_of__cursor_in__char_buffer == 0, no mutation occurs; the function returns immediately.
2. If size_of__char_buffer == 0, no mutation occurs; the function returns immediately.
3. Otherwise:
   a. The character at position (cursor - 1) is removed.
   b. All characters from position (cursor - 1) through (size_of__char_buffer - 2) are shifted left by one position (i.e., each character at index N is overwritten with the character at index N+1).
   c. index_of__cursor_in__char_buffer is decremented by 1.
   d. pM_char_buffer[size_of__char_buffer - 1] is set to 0 (null terminator).
4. size_of__char_buffer is NOT modified; it continues to represent the allocated buffer capacity.

Correctness Verdict: Correct

Semantic Alignment:
The function correctly implements backspace semantics: it deletes the character immediately before the cursor and shifts all subsequent characters left. The cursor is decremented to reflect the removal. The loop bounds are correct — it shifts from (cursor - 1) to (size - 2) inclusive, accessing (cursor) to (size - 1) for the source data, which is within bounds. The null terminator is correctly placed at the last buffer position (size - 1). This is consistent with the buffer model where size_of__char_buffer represents the total allocated capacity, and index_of__cursor_in__char_buffer tracks the insertion point. The function does not modify size_of__char_buffer, which is correct since the buffer capacity does not change when a character is deleted.

Implementation Correctness:
Type compatibility — all field accesses use correct types: index_of__cursor_in__char_buffer is Index__u32, size_of__char_buffer is Quantity__u32, pM_char_buffer is char*, and index_of__char is Index__u32. No implicit conversions or truncation.
No undefined behavior — no null pointer dereference (p_this_ui_text_box is assumed valid by the caller), no out-of-bounds access. The loop condition `index_of__char < size_of__char_buffer - 1` ensures the last access is at index `size_of__char_buffer - 1` (the final valid index). The subtraction `index_of__cursor_in__char_buffer - 1` is safe because it is guarded by the early return when cursor == 0. No type punning.
Validation — the function performs appropriate validation for its role: it guards against cursor == 0 (nothing to backspace) and buffer size == 0 (empty buffer). These guards are consistent with the function's responsibility as a special-symbol handler invoked from handle_special_symbols__text_box.

Side Effects:
Mutates the UI_Element struct pointed to by p_this_ui_text_box:
1. Shifts char buffer contents left by one position starting at (cursor - 1).
2. Decrements index_of__cursor_in__char_buffer by 1.
3. Sets the last byte of pM_char_buffer to 0 (null terminator).
No other observable side effects. The p_game parameter is unused.
