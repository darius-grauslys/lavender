set_c_str_of__ui_text_with__pM_c_str — core/source/ui/ui_text.c

Sets the text buffer of a UI_Element (text kind) by taking ownership of a caller-provided char* pointer.

Pre-conditions:
1. p_ui_manager must be a non-null pointer to a valid UI_Manager.
2. p_ui_text must be a non-null pointer to a valid UI_Element of kind UI_Element_Kind__Text (so the pM_char_buffer / size_of__char_buffer union fields are active).
3. pM_text__c_str may be NULL (in which case size_of__text is ignored and the buffer is cleared to zero/NULL).
4. If pM_text__c_str is non-NULL, it must be a valid heap-allocated pointer whose lifetime is transferred to the UI_Element (the function takes ownership and will free it later).
5. size_of__text is any Quantity__u32; only meaningful when pM_text__c_str is non-NULL.

Post-conditions:
1. The UI_Manager is marked dirty (set_ui_manager_as__dirty).
2. Any previously owned pM_char_buffer is freed and the field set to NULL (via free_pM_text_of__ui_text).
3. p_ui_text->pM_char_buffer is set to pM_text__c_str (the transferred pointer).
4. p_ui_text->size_of__char_buffer is set to size_of__text if pM_text__c_str is non-NULL, otherwise 0.

Correctness Verdict: Correct

Semantic Alignment:
The function correctly implements a "take ownership" setter for the text buffer. It frees the old buffer before assigning the new pointer, preventing memory leaks. The null-check on pM_text__c_str ensures that passing NULL safely clears the text. This matches the semantic intent documented in the header comment for initialize_ui_element_as__text_with__pM_c_str: "takes ownership of the pM_c_str pointer."

Implementation Correctness:
Type compatibility — pM_text__c_str (char *) is assigned to pM_char_buffer (char *), which matches exactly. size_of__text (Quantity__u32) is assigned to size_of__char_buffer (Quantity__u32), which also matches exactly. No implicit conversions or truncation.
No undefined behavior — free_pM_text_of__ui_text checks for non-null before calling free and sets the pointer to 0 afterward, so there is no double-free or use-after-free. The new pointer is assigned after the free, so no dangling pointer. No null dereference, no type punning, no out-of-bounds access.
No additional validation is needed within this function — it is a low-level setter; the caller is responsible for ensuring p_ui_manager and p_ui_text are valid and that pM_text__c_str is a heap-allocated pointer when non-NULL.

Side Effects:
1. Marks the UI_Manager as dirty via set_ui_manager_as__dirty.
2. Frees the previous pM_char_buffer if one was held (via free_pM_text_of__ui_text).
3. Mutates p_ui_text->pM_char_buffer and p_ui_text->size_of__char_buffer.
