initialize_ui_element — core/source/ui/ui_element.c

Resets a UI_Element struct to its initial/default state by zeroing all fields except the Serialization_Header, then assigns parent/child/next pointers, element kind, flags, and default dispose/compose/transformed handlers. This is Lavender-style initialization (pool cleanup / reset to initial conditions), NOT RAII resource acquisition.

Pre-conditions:
1. p_ui_element must be a non-null pointer to a writable UI_Element object.
2. p_ui_element__parent, p_ui_element__child, p_ui_element__next may be NULL — they are linked-list/tree pointers and null is a valid sentinel.
3. kind_of_ui_element is any valid enum UI_Element_Kind value.
4. ui_flags is any valid UI_Flags__u16 value (e.g. UI_FLAGS__BIT_IS_ENABLED, etc.).
5. The Serialization_Header at the start of p_ui_element is assumed to be already initialized — it is preserved and not touched by this function.

Post-conditions:
1. All fields of p_ui_element except _serialization_header are zeroed by memset.
2. p_parent is set to p_ui_element__parent.
3. p_child is set to p_ui_element__child.
4. p_next is set to p_ui_element__next.
5. the_kind_of_ui_element__this_is is set to kind_of_ui_element.
6. ui_flags is set to ui_flags, with the UI_FLAGS__BIT_IS_USING__SPRITE_OR_UI_TILE_SPAN bit cleared (due to set_ui_element__compose_handler defaulting to ui_tile_span mode — see Side Effects).
7. m_ui_dispose_handler is set to m_ui_element__dispose_handler__default.
8. m_ui_compose_handler is set to m_ui_element__compose_handler__default.
9. m_ui_transformed_handler is set to m_ui_element__transformed_handler__default.
10. m_ui_clicked_handler, m_ui_dragged_handler, m_ui_dropped_handler, m_ui_receive_drop_handler, m_ui_held_handler, and m_ui_typed_handler remain NULL (zeroed by memset — these are optional event handlers not set by default).
11. ui_tile_span is zeroed.
12. The kind-specific union (UI_Button, UI_Draggable, UI_Slider, UI_Text/UI_Text_Box, UI_Window) is zeroed.
13. ui_element_data is zeroed.

Correctness Verdict: Correct

Semantic Alignment:
This function performs Lavender-style initialization — it resets the struct to initial conditions (cleaning up for pool reuse), NOT RAII resource acquisition. The memset preserves the Serialization_Header (which contains size_of__struct and uuid) and zeroes everything else. All struct fields are accounted for: the three pointer links (p_parent, p_child, p_next), the kind enum (the_kind_of_ui_element__this_is), the flags (ui_flags), and the three default lifecycle handlers (dispose, compose, transformed) are explicitly set; the optional event handlers (clicked, dragged, dropped, receive_drop, held, typed) are intentionally left null. The ui_tile_span, kind-specific union, and ui_element_data are zeroed. The function does not acquire any resources (no allocation, no sprite/hitbox registration).

Implementation Correctness:
Type compatibility — every parameter type matches its target field type exactly: UI_Element* → UI_Element*, enum UI_Element_Kind → enum UI_Element_Kind, UI_Flags__u16 → UI_Flags__u16. No implicit conversions or truncation.
No undefined behavior — the memset correctly offsets by sizeof(Serialization_Header) to preserve the header, and zeroes sizeof(UI_Element) - sizeof(Serialization_Header) bytes. The pointer arithmetic (u8*)p_ui_element + sizeof(Serialization_Header) is valid within the struct. The parent/child/next pointers are only assigned, never dereferenced, so null values are safe.
Validation — no null check on p_ui_element. This is consistent with the codebase pattern for low-level struct initializers (e.g., initialize_audio_effect) where the caller is responsible for providing a valid pointer. The caller (typically a UI manager pool allocator) is expected to provide a valid writable pointer.

Side Effects:
Mutates p_ui_element: zeroes all fields except _serialization_header, then sets p_parent, p_child, p_next, the_kind_of_ui_element__this_is, ui_flags, m_ui_dispose_handler, m_ui_compose_handler, and m_ui_transformed_handler. Additionally, set_ui_element__compose_handler (an inline helper) clears the UI_FLAGS__BIT_IS_USING__SPRITE_OR_UI_TILE_SPAN bit in ui_flags, defaulting the element to ui_tile_span rendering mode. No external resources are acquired or released.
