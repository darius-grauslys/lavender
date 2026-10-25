initialize_ui_element_as__text_box_with__const_c_str — core/source/ui/ui_text_box.c

Composes a Lavender-style initialization of a UI_Element as a text box by first delegating to the text initialization (buffer allocation, font/typer setup, text handlers) and then overlaying text box-specific handlers (clicked, compose, typed).

Pre-conditions:
1. p_ui_text_box must be a non-null pointer to a writable UI_Element object.
2. p_font must be a non-null pointer to a valid Font object (passed through to typer initialization).
3. p_text__const_c_str must be a non-null pointer to a readable char buffer of at least size_of__text bytes.
4. size_of__text must be greater than 0 (malloc(0) is implementation-defined and would produce a zero-length buffer).
5. p_ui_text_box->pM_char_buffer must be NULL (the delegated text init checks this and early-returns if already set, which would skip buffer allocation but still set text box handlers).
6. p_ui_text_box->ui_flags must already contain the desired flags prior to the call; the delegated initialize_ui_element reads and preserves them via memset-then-restore.

Post-conditions:
1. p_ui_text_box is mutated: its kind is set to UI_Element_Kind__Text (via delegated initialize_ui_element), its pM_char_buffer is heap-allocated and filled with a copy of p_text__const_c_str, size_of__char_buffer is set to size_of__text, index_of__cursor_in__char_buffer is zeroed, and the Typer is initialized with p_font.
2. The compose handler is overwritten with m_ui_element__compose_handler__text_box (which internally calls the text compose handler).
3. The clicked handler is set to m_ui_element__clicked_handler__text_box.
4. The typed handler is set to m_ui_element__typed_handler__text_box.
5. The dispose and transformed handlers retain their values from the text initialization (m_ui_element__dispose_handler__text and m_ui_element__transformed_handler__text respectively).

Correctness Verdict: Correct

Semantic Alignment:
The function correctly fulfills its semantic intent: it initializes a UI_Element as a text box by composing two initialization steps. The delegated initialize_ui_element_as__text_with__const_c_str sets up the text buffer, typer, and text-level handlers. Then initialize_ui_text_box__default_handlers overrides the compose handler with the text box variant (which internally calls the text compose handler) and adds the clicked and typed handlers specific to text boxes. The text box compose handler correctly chains non-recursive composition, text composition, and recursive-only composition, so overwriting the text compose handler is intentional and correct.

Note on Lavender initialization semantics: This function performs initialization in the Lavender sense (setting a struct to its initial conditions for reuse from a pool), not in the RAII sense. The malloc of the char buffer is part of setting up the text element's initial state, not coupling resource acquisition with object lifetime. The element can later be disposed of via the dispose handler, which frees the buffer.

Note on UI element kind: The element's the_kind_of_ui_element__this_is field is set to UI_Element_Kind__Text (not UI_Element_Kind__Text_Box) because the delegated text initialization hardcodes UI_Element_Kind__Text. The enum value UI_Element_Kind__Text_Box exists but is never referenced anywhere in the codebase. Since no code branches on this specific kind for text boxes, this does not cause a functional defect, but it is a semantic misalignment — the element is kind-tagged as Text while being configured with text box handlers.

Implementation Correctness:
Type compatibility — all parameters are forwarded with matching types: UI_Element* → UI_Element*, Font* → Font*, const char* → const char*, Quantity__u32 → Quantity__u32. No implicit conversions or truncation.
Undefined behavior — no pointer arithmetic, no null dereference (assuming pre-conditions hold), no type punning, no out-of-bounds access within this function. The delegated text initialization handles malloc failure and early-return gracefully.
Validation — this function performs no validation itself; it delegates entirely to the two sub-functions. The re-initialization guard in the text init (checking pM_char_buffer) is the only validation, and it is appropriate for this function's role as a composition wrapper. Null-checking of p_ui_text_box and p_font is the caller's responsibility, consistent with the codebase pattern.

Side Effects:
Mutates the UI_Element struct pointed to by p_ui_text_box: allocates a heap buffer (pM_char_buffer), copies text into it, initializes the Typer with the given font, sets the element kind to UI_Element_Kind__Text, and sets/overrides multiple handler function pointers (compose, clicked, typed) as well as the dispose and transformed handlers from the text initialization.
