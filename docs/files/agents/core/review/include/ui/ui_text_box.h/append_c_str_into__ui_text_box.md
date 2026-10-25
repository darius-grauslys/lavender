append_c_str_into__ui_text_box — core/include/ui/ui_text_box.h

Delegates to append_c_str_into__ui_text to append a C-string into the text box's internal char buffer at the cursor position, with bounds clamping.

Pre-conditions:
1. p_ui_manager must be a non-null pointer to a valid UI_Manager.
2. p_ui_text_box must be a non-null pointer to a valid UI_Element of kind UI_Text_Box (or UI_Text), with pM_char_buffer allocated and size_of__char_buffer > 0.
3. p_text__const_c_str must be a non-null pointer to a valid C-string (or at least a buffer of size_of__text bytes). The function does not require null-termination since size is provided explicitly.
4. size_of__text is any Quantity__u32 (uint32_t); the actual number of bytes copied is clamped to the remaining space in the buffer.

Post-conditions:
1. The UI_Manager is marked as dirty (ui_manager_flags__u8 |= UI_MANAGER_FLAG__IS_DIRTY).
2. Up to (size_of__char_buffer - index_of__cursor_in__char_buffer) bytes from p_text__const_c_str are copied into pM_char_buffer starting at index_of__cursor_in__char_buffer via memcpy.
3. The index_of__cursor_in__char_buffer is NOT advanced after the append — this is a semantic gap inherited from the underlying append_c_str_into__ui_text function, but it is not the responsibility of this wrapper.

Correctness Verdict: Correct

Semantic Alignment:
The wrapper is a pure pass-through that delegates all four parameters (p_ui_manager, p_ui_text_box, p_text__const_c_str, size_of__text) to append_c_str_into__ui_text. No parameters are dropped, reordered, or transformed. The delegation preserves the semantic intent of appending a C-string into the text box. The underlying function correctly clamps the copy size to prevent buffer overflow and marks the UI manager as dirty.

Implementation Correctness:
Type compatibility — all parameter types match exactly: UI_Manager* → UI_Manager*, UI_Element* → UI_Element*, const char* → const char*, Quantity__u32 (uint32_t) → Quantity__u32 (uint32_t). The min__u32 function takes u32 parameters, and Quantity__u32 is typedef'd to uint32_t which is the same as u32 — no implicit conversion or truncation.
No undefined behavior — no broken pointer arithmetic, no null dereference (caller responsibility), no type punning, no out-of-bounds access (clamp__u32 ensures memcpy stays within buffer bounds).
Validation — the function performs no null-check validation on its parameters; this is consistent with the Lavender engine's pattern where validation is the caller's responsibility (see append_symbol_into__ui_text which also does not validate, and set_c_str_of__ui_text_with__const_c_str which does not validate p_ui_manager or p_ui_text).

Side Effects:
1. Marks the UI_Manager as dirty by setting UI_MANAGER_FLAG__IS_DIRTY.
2. Writes up to clamp__u32 bytes into p_ui_text_box->pM_char_buffer via memcpy.
3. Does NOT modify index_of__cursor_in__char_buffer (cursor position is not advanced after append).
