m_ui_element__compose_handler__text_box — core/source/ui/ui_text_box.c, lines 231-247

Composes a text box UI element by orchestrating three sequential compose phases: the box's own tile span (background/border), the text content (rendered into the typer), and any child UI elements (recursively).

Pre-conditions:
1. p_this_ui_element must be a non-null pointer to a valid UI_Element that has been initialized as a text box (i.e., initialized via one of the initialize_ui_element_as__text_box_with__* functions, which sets the compose handler, allocates a char buffer, and initializes a typer with a font).
2. p_game must be a non-null pointer to a valid Game object (used to retrieve the UI manager and gfx context).
3. p_gfx_window must be a non-null pointer to a valid Graphics_Window (used to retrieve the UI manager, UI tile map, hitbox manager, and sprite manager).
4. The UI_Element must have its m_ui_compose_handler set to this function (ensured during text box initialization via set_ui_element__compose_handler).

Post-conditions:
1. The UI element's own tile span is composed into the UI tile map and gfx window (via m_ui_element__compose_handler__default_non_recursive).
2. The text content (pM_char_buffer) is rendered into the element's typer, and the UI manager is marked dirty (via m_ui_element__compose_handler__text).
3. Any child UI elements are recursively composed (via m_ui_element__compose_handler__default_only_recursive).
4. The UI manager is marked as dirty (done by the callees).

Correctness Verdict: Correct

Semantic Alignment:
The implementation fulfills the semantic intent of a text box compose handler. A text box is a UI element that renders a background/span with text inside it, and may have child elements. The three compose phases are invoked in the correct order: box background first, then text content, then recursive children. This mirrors the structure of m_ui_element__compose_handler__default (which does non-recursive then recursive), with the text compose phase inserted in between — exactly what is needed for a text box. The order is semantically correct: the box must be composed before the text is rendered into it, and children should be composed last.

Type compatibility — all three callee functions accept (UI_Element *, Game *, Graphics_Window *), and the function passes p_this_ui_element (UI_Element *), p_game (Game *), and p_gfx_window (Graphics_Window *) to each. Parameter types match exactly; the only difference is the local parameter name (p_gfx_window vs p_graphics_window), which has no effect on correctness. No implicit conversions or truncation occur.
No undefined behavior in the function under review itself — no pointer arithmetic, no null dereference, no type punning, no out-of-bounds access. The function does not dereference any pointers directly; it delegates entirely to the three callees.
No validation is needed in this function — this is consistent with the engine's pattern where compose handlers are invoked through function pointers from the UI manager's compose loop, and the caller is responsible for ensuring valid pointers. The callees themselves also do not perform null checks (e.g., m_ui_element__compose_handler__default_non_recursive calls get_p_ui_manager_from__graphics_window(p_game, p_graphics_window) without null checks), so this function follows the established convention.

Note: The callee m_ui_element__compose_handler__default_only_recursive (the third step) contains a use-before-initialization bug — it reads the local variable p_ui_element__child before assigning it (get_child_of__ui_element(p_ui_element__child) should be get_child_of__ui_element(p_ui_element)). This is a defect in that callee, not in this function, and means the recursive child composition step may exhibit undefined behavior. This should be tracked separately when reviewing m_ui_element__compose_handler__default_only_recursive.

Side Effects:
- Mutates the UI tile map: generates the element's UI span into the tile map (via default_non_recursive).
- Mutates the typer: renders the char buffer text into the typer and resets the typer cursor (via text compose handler).
- Marks the UI manager as dirty (via callees).
- Recursively composes child UI elements, which may have their own side effects (via default_only_recursive).
