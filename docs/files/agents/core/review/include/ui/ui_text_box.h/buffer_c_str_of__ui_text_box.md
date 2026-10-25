buffer_c_str_of__ui_text_box — core/include/ui/ui_text_box.h

Inline forwarding wrapper that delegates to buffer_c_str_of__ui_text, allocating a new zero-initialized char buffer of the requested size on the UI_Element (which is treated as a UI text element).

Pre-conditions:
1. p_ui_manager must be a non-null pointer to a valid UI_Manager.
2. p_ui_text_box must be a non-null pointer to a writable UI_Element that is initialized as a text box (i.e., has a valid pM_char_buffer field).
3. size_of__text is any Quantity__u32; a value of 0 is permitted and causes the buffer to be freed with no allocation.

Post-conditions:
1. The UI_Manager is marked dirty (via set_ui_manager_as__dirty in the delegated function).
2. Any previously allocated pM_char_buffer on the UI_Element is freed and its pointer set to NULL (via free_pM_text_of__ui_text in the delegated function).
3. If size_of__text is non-zero, a new char buffer of that size is allocated via malloc, assigned to pM_char_buffer, and zero-initialized via memset.
4. size_of__char_buffer on the UI_Element is set to size_of__text (or 0 if size_of__text is 0).
5. If malloc fails, pM_char_buffer remains NULL and size_of__char_buffer is set to 0 (behavior inherited from buffer_c_str_of__ui_text — note: the delegated function does not check malloc return, but this wrapper simply forwards).

Correctness Verdict: Correct

Semantic Alignment:
The wrapper faithfully forwards all three parameters (p_ui_manager, p_ui_text_box, size_of__text) to buffer_c_str_of__ui_text without modification. The semantic intent — allocating a fresh zeroed char buffer of the given size on the text box element — is fully delegated to the underlying function. No parameter transformation, reordering, or member omission occurs. The wrapper is purely a type-safe inline alias that maps the "text box" naming convention to the shared UI text implementation.

Implementation Correctness:
Type compatibility — all parameter types match the delegated function exactly (UI_Manager * → UI_Manager *, UI_Element * → UI_Element *, Quantity__u32 → Quantity__u32). No implicit conversions or truncation.
Undefined behavior — no pointer arithmetic, no null dereference, no type punning, no out-of-bounds access within this wrapper. The wrapper does not dereference any pointers itself; it relies entirely on the callee.
Validation — no validation is performed in the wrapper. This is consistent with the pattern used by all sibling wrappers in ui_text_box.h (e.g., set_c_str_of__ui_text_box_with__const_c_str, clear_c_str_of__ui_text_box). Validation/null-checking is the callee's responsibility, matching the low-level inline wrapper convention in this codebase.

Side Effects:
Mutates the UI_Element pointed to by p_ui_text_box: frees any existing pM_char_buffer, allocates a new one (if size_of__text > 0), and updates size_of__char_buffer. Also marks the UI_Manager as dirty. These side effects are inherited entirely from the delegated buffer_c_str_of__ui_text function.
