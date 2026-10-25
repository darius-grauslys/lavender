initialize_ui_element_as__button — core/source/ui/ui_button.c

Resets a UI_Element to its initial conditions as a Button by delegating to initialize_ui_element for base struct cleanup, then sets the clicked handler, toggleable state, and toggled state.

Pre-conditions:
1. p_ui_button must be a non-null pointer to a writable UI_Element object.
2. p_ui_button->p_parent, p_ui_button->p_child, and p_ui_button->p_next are read before initialization to preserve existing linkage; they may be NULL or valid UI_Element pointers. Callers relying on pool-reuse semantics expect these to retain their prior values.
3. p_ui_button->ui_flags is read before initialization to preserve existing UI flags; it must be a valid UI_Flags__u16 value.
4. m_ui_button__clicked_handler may be NULL (type is a function pointer); if non-NULL it must conform to the m_UI_Clicked signature.
5. is_toggleable_or__non_toggleable and is_toggled_or__not_toggled are bool values with no range constraints.

Post-conditions:
1. p_ui_button is mutated: all fields except Serialization_Header are zeroed via initialize_ui_element's memset, then parent/child/next pointers and ui_flags are restored from pre-existing values, the element kind is set to UI_Element_Kind__Button, and default dispose/compose/transformed handlers are installed.
2. m_ui_clicked_handler is set to m_ui_button__clicked_handler (which may be NULL).
3. ui_button_flags is configured: the UI_BUTTON_FLAGS__BIT_IS_TOGGLEABLE bit reflects is_toggleable_or__non_toggleable, and the UI_BUTTON_FLAGS__BIT_IS_TOGGLED bit reflects is_toggled_or__not_toggled.

Correctness Verdict: Correct

Semantic Alignment:
The function fulfills Lavender's initialization semantics — it cleans up the struct to initial conditions (via initialize_ui_element's memset) rather than performing RAII resource acquisition. This is consistent with pool-reuse patterns where a UI_Element is reset and returned to/reused from a free pool. The function preserves existing parent/child/next linkage and ui_flags, which is the expected behavior for re-initialization of pool elements.

The toggleable/toggled configuration is correctly applied: set_ui_button_as__toggleable_or__non_toggleable is called first (which, when setting non-toggleable, also clears the toggled bit via set_ui_button_as__non_toggleable → set_ui_button_as__untoggled), and then set_ui_button_as__toggled_or__not_toggled is called second to explicitly set the final toggled state. The second call overrides any intermediate state from the first, ensuring the final toggled bit matches is_toggled_or__not_toggled regardless of the toggleable setting.

Implementation Correctness:
Type compatibility — every parameter type matches its target exactly: UI_Element * → UI_Element *, m_UI_Clicked → m_UI_Clicked, bool → bool (for both toggleable and toggled parameters). The enum UI_Element_Kind__Button is correctly passed as enum UI_Element_Kind. No implicit conversions or truncation occur.
No undefined behavior — no broken pointer arithmetic, no null dereference (p_ui_button is required to be non-null), no type punning, no out-of-bounds access. The memset in initialize_ui_element operates within the bounds of sizeof(UI_Element) - sizeof(Serialization_Header), which is safe.
Validation — no validation is performed, which is appropriate for this low-level initialization function. The caller is responsible for ensuring p_ui_button is valid and that any linkage data being preserved is correct.

Side Effects:
Mutates the UI_Element struct pointed to by p_ui_button: zeroes all fields except Serialization_Header, restores parent/child/next/ui_flags from pre-existing values, sets kind to Button, installs default dispose/compose/transformed handlers, sets the clicked handler, and configures ui_button_flags for toggleable and toggled state. No other memory or global state is affected.
