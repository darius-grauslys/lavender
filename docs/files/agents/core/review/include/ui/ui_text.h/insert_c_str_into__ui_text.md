insert_c_str_into__ui_text — core/source/ui/ui_text.c

Inserts (overwrites) a C string into a UI text element's char buffer at a specified index, clamping the copy to fit within the buffer, and advances the cursor to the position after the inserted text.

Pre-conditions:
1. p_ui_manager must be a non-null pointer to a valid UI_Manager.
2. p_ui_text must be a non-null pointer to a UI_Element that has been initialized as a text element (UI_Element_Kind__Text), with pM_char_buffer allocated and size_of__char_buffer set.
3. p_text__const_c_str must be a non-null pointer to a valid C string source.
4. size_of__text is any Quantity__u32; if larger than available buffer space, it is clamped.
5. index_to__insert_at must be less than p_ui_text->size_of__char_buffer; otherwise the function returns early with an error.

Post-conditions:
1. The UI manager is marked as dirty (UI_MANAGER_FLAG__IS_DIRTY is set).
2. Up to min(size_of__text, size_of__char_buffer - index_to__insert_at) bytes are written into p_ui_text->pM_char_buffer starting at index_to__insert_at via strncpy.
3. p_ui_text->index_of__cursor_in__char_buffer is set to index_to__insert_at + clamp (the full clamped length, not the actual number of bytes copied by strncpy).
4. If index_to__insert_at >= size_of__char_buffer, the function returns early with no mutation of the buffer or cursor.

Correctness Verdict: Incorrect

Semantic Alignment:
The function's intent is to insert a string into the text buffer at a given position and update the cursor accordingly. The bounds check and clamp calculation correctly prevent out-of-bounds writes. However, there are two semantic issues:

1. The function uses strncpy instead of memcpy (unlike the sibling function append_c_str_into__ui_text which uses memcpy). strncpy stops copying at the first null byte in the source and pads the remainder with null bytes up to the count. This means if size_of__text is larger than the actual string length, strncpy will pad the buffer with null bytes beyond the actual text, potentially overwriting existing content. The cursor is still advanced by the full clamp value, not the actual number of meaningful bytes copied.

2. The function name "insert" implies inserting text at a position (shifting existing content), but the implementation simply overwrites bytes at the specified index without shifting. This is consistent with append_c_str_into__ui_text's behavior, but the naming is misleading.

Implementation Correctness:
- Type compatibility: All parameter types match their usage. Quantity__u32 for size_of__text matches the u32 arithmetic. Index__u32 for index_to__insert_at matches the u32 comparison. No implicit conversions or truncation.
- Undefined behavior: No out-of-bounds access due to the bounds check and clamp. However, there are no null pointer checks for p_ui_manager, p_ui_text, p_text__const_c_str, or p_ui_text->pM_char_buffer. If any of these are null, the function will dereference a null pointer, causing undefined behavior.
- Validation: The bounds check for index_to__insert_at is appropriate, but null pointer validation is missing for all pointer parameters. This is the caller's responsibility in some contexts, but the function directly dereferences p_ui_manager and p_ui_text without checks, making null dereference possible.

Side Effects:
- Marks the UI manager as dirty by setting UI_MANAGER_FLAG__IS_DIRTY.
- Mutates p_ui_text->pM_char_buffer (via strncpy, potentially padding with null bytes).
- Mutates p_ui_text->index_of__cursor_in__char_buffer to index_to__insert_at + clamp.
