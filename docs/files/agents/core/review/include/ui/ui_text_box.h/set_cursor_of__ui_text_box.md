set_cursor_of__ui_text_box — core/include/ui/ui_text_box.h

Delegates to set_cursor_of__ui_text, forwarding both the UI_Element pointer and the cursor index unchanged.

Pre-conditions:
1. p_ui_text_box must be a non-null pointer to a valid, initialized UI_Element of kind UI_Text_Box (or UI_Text, since text boxes and text share the same union layout in UI_Element).
2. The UI_Element's char_buffer must have been allocated and size_of__char_buffer must be greater than 0 (enforced by the callee).
3. index_of__cursor_in__c_str__u32 is any Index__u32 value (uint32_t). If it exceeds or equals size_of__char_buffer, the callee clamps it to size_of__char_buffer - 1.

Post-conditions:
1. The UI_Element pointed to by p_ui_text_box is mutated: its index_of__cursor_in__char_buffer field is set to the requested index, clamped to at most size_of__char_buffer - 1.

Correctness Verdict: Correct

Semantic Alignment:
The function correctly fulfills its intent as a thin inline wrapper around set_cursor_of__ui_text. The UI_Element struct uses a union where both UI_Text and UI_Text_Box share the same layout (Typer, pM_char_buffer, size_of__char_buffer, index_of__cursor_in__char_buffer), so passing a UI_Text_Box's UI_Element* to set_cursor_of__ui_text (which expects a UI_Text's UI_Element*) is semantically valid. The actual bounds-clamping logic resides in the callee, which is the appropriate location.

Implementation Correctness:
Type compatibility — both parameters match the callee's signature exactly: UI_Element * → UI_Element *, Index__u32 → Index__u32. No implicit conversions or truncation occur.
No undefined behavior — the wrapper performs no pointer arithmetic, no null dereference, no type punning, and no out-of-bounds access. It simply forwards parameters.
No validation is performed in the wrapper — this is appropriate for a low-level inline forwarding function. Validation (bounds clamping) is the responsibility of the callee (set_cursor_of__ui_text), which correctly handles out-of-range indices.

Side Effects:
The function mutates the UI_Element pointed to by p_ui_text_box by setting its index_of__cursor_in__char_buffer field (via the callee set_cursor_of__ui_text). No other state is modified.
