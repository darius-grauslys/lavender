set_cursor_of__ui_text — core/source/ui/ui_text.c

Clamps the cursor index to a valid range within the character buffer, or sets it to the requested position if already valid.

Pre-conditions:
1. p_ui_text must be a non-null pointer to a writable UI_Element that is of kind UI_Element_Kind__Text (i.e., the UI_Text union member is active).
2. p_ui_text->size_of__char_buffer reflects the allocated size of p_ui_text->pM_char_buffer.
3. index_of__cursor_in__c_str__u32 is any Index__u32 (uint32_t) value; no upper bound is required by the caller since the function clamps.

Post-conditions:
1. p_ui_text->index_of__cursor_in__char_buffer is set to either index_of__cursor_in__c_str__u32 (if it is less than size_of__char_buffer) or to size_of__char_buffer - 1 (if index_of__cursor_in__c_str__u32 >= size_of__char_buffer).

Correctness Verdict: Incorrect

Semantic Alignment:
The implementation intends to clamp the cursor index so it never exceeds the buffer bounds. However, when size_of__char_buffer is 0, the expression size_of__char_buffer - 1 causes an unsigned integer underflow (uint32_t), wrapping to UINT32_MAX (4294967295). This places the cursor at an invalid position far beyond any buffer. The semantic intent is to keep the cursor in a valid range, but the code fails when the buffer has zero size. A correct implementation would need to handle the zero-size case, e.g., by setting the cursor to 0 when size_of__char_buffer is 0.

Implementation Correctness:
Type compatibility — parameter type Index__u32 matches the field type Index__u32 exactly. No implicit conversions or truncation.
Undefined behavior — unsigned integer underflow occurs when size_of__char_buffer is 0. The subtraction (size_of__char_buffer - 1) wraps to UINT32_MAX. While unsigned integer wraparound is defined behavior in C, it produces an invalid cursor index that can lead to downstream undefined behavior in callers. For example, append_c_str_into__ui_text computes (size_of__char_buffer - index_of__cursor_in__char_buffer), which would also underflow, potentially causing a buffer over-read or over-write in the subsequent memcpy.
Validation — no null check on p_ui_text; this is consistent with the codebase's convention where null-checking is the caller's responsibility for low-level UI functions.

Side Effects:
Mutates p_ui_text->index_of__cursor_in__char_buffer. No other observable side effects (no allocation, no I/O, no modification of other fields).
