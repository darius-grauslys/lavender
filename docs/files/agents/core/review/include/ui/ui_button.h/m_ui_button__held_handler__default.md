m_ui_button__held_handler__default — core/source/ui/ui_button.c

Default no-op handler invoked when a UI button is held (pressed and maintained).

Pre-conditions:
1. p_this_button must be a non-null pointer to a valid UI_Element of kind UI_Element_Kind__Button.
2. p_game may be any valid Game pointer (unused in this default implementation).
3. p_graphics_window may be any valid Graphics_Window pointer (unused in this default implementation).

Post-conditions:
1. No state is mutated. The function returns void with no observable effect.

Correctness Verdict: Correct

Semantic Alignment:
The function is a default handler conforming to the m_UI_Held function pointer signature (typedef in defines.h: `void (*m_UI_Held)(UI_Element *p_this_ui_element, Game *p_game, Graphics_Window *p_gfx_window)`). As a default handler, a no-op body is a valid design choice — it provides a safe, inert default that callers can override with a custom handler via `set_ui_element__held_handler`. The empty body does not violate any semantic contract; the held event simply has no default behavior.

Implementation Correctness:
Type compatibility — all three parameter types match the m_UI_Held typedef exactly (UI_Element *, Game *, Graphics_Window *). No implicit conversions.
Undefined behavior — none. The function does not dereference p_this_button, p_game, or p_graphics_window, so there is no risk of null dereference or invalid memory access. The unused parameters are intentionally left unreferenced, which is standard C practice for default handler stubs.
Validation — no validation is needed or expected. This is a handler invoked by the engine's UI event dispatch system; the caller is responsible for ensuring p_this_button is valid before invocation.

Side Effects:
No side effects.