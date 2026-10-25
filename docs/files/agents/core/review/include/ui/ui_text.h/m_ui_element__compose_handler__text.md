m_ui_element__compose_handler__text — core/source/ui/ui_text.c

Composes (renders) a text UI element by routing its character buffer through the Typer rendering system onto the graphics window's platform rendering target.

Pre-conditions:
1. p_this_ui_element must be a non-null pointer to a properly initialized UI_Element of kind UI_Element_Kind__Text.
2. p_game must be a non-null pointer to a valid Game object.
3. p_graphics_window must be a non-null pointer to a valid Graphics_Window.
4. The UI_Element must have been initialized via one of the initialize_ui_element_as__text_with__* functions, which sets up the Typer (including a non-null p_font), pM_char_buffer, and size_of__char_buffer.
5. p_graphics_window->p_PLATFORM_gfx_window must be valid (the platform graphics window used as the typer render target).
6. The UI_Manager associated with p_graphics_window (via uuid_of__ui_manager) must exist and be non-null; get_p_ui_manager_from__graphics_window may return NULL if the lookup fails, but this is a configuration error outside this function's responsibility.

Post-conditions:
1. The UI_Manager associated with p_graphics_window is marked as dirty (UI_MANAGER_FLAG__IS_DIRTY is set).
2. The Typer's render target is set to p_graphics_window->p_PLATFORM_gfx_window and is_using_PLATFORM_texture_or__PLATFORM_graphics_window is set to false (non-texture mode).
3. The Typer's cursor position is reset to (0, 0, 0).
4. If pM_char_buffer is non-NULL and size_of__char_buffer > 0 and the first character is non-null, the character buffer content is rendered through the typer onto the graphics window. If size_of__char_buffer is 0 or the first character is '\0', put_c_string_in__typer returns early without rendering.

Correctness Verdict: Correct

Semantic Alignment:
The implementation fulfills the semantic intent of a compose handler for text UI elements. It performs the same sequence of operations as other compose handlers in the codebase: marking the UI manager as dirty (consistent with m_ui_element__compose_handler__default_non_recursive and m_ui_element__transformed_handler__text), setting the render target, resetting the cursor, and rendering the text content. The order of operations is correct: the render target must be set before rendering, and the cursor must be reset before putting the string so that rendering starts from the origin.

Implementation Correctness:
Type compatibility — all parameter types match their target function parameter types exactly. get_p_typer_of__ui_text returns Typer* matching set_PLATFORM_graphics_window_target_for__typer and reset_typer_cursor. p_graphics_window->p_PLATFORM_gfx_window is PLATFORM_Graphics_Window* matching the typer target setter. get_p_gfx_context_from__game returns Gfx_Context* matching put_c_string_in__typer's first parameter. p_this_ui_element->pM_char_buffer (char*) is compatible with put_c_string_in__typer's const char* parameter. p_this_ui_element->size_of__char_buffer (Quantity__u32) matches put_c_string_in__typer's Quantity__u32 parameter. No implicit conversions or truncation.
No undefined behavior in the function itself — no pointer arithmetic, no type punning, no out-of-bounds access. The put_c_string_in__typer callee handles null/empty string checks (returns early if max_length is 0 or first char is '\0'). The potential NULL dereference risk in put_c_string_in__typer (if pM_char_buffer is NULL while size_of__char_buffer > 0) is mitigated by the initialization and mutation functions which maintain the invariant that pM_char_buffer is non-NULL whenever size_of__char_buffer > 0. The NULL UI manager risk from get_p_ui_manager_from__graphics_window is consistent with the pattern used in sibling handlers and is a caller/configuration responsibility.
No validation is needed within this function — it is a handler invoked internally during composition where pre-conditions are expected to hold.

Side Effects:
1. Sets UI_MANAGER_FLAG__IS_DIRTY on the UI_Manager associated with the graphics window.
2. Mutates the Typer's p_PLATFORM_graphics_window__typer_target pointer and is_using_PLATFORM_texture_or__PLATFORM_graphics_window flag.
3. Resets the Typer's cursor_position__3i32 to (0, 0, 0).
4. Renders characters to the platform graphics window via PLATFORM_put_char_in__typer (called within put_c_string_in__typer), which advances the typer cursor as each character is placed.
