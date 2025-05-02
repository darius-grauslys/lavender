#ifndef UI_WINDOW_H
#define UI_WINDOW_H

#include "defines.h"
#include "defines_weak.h"
#include "types/implemented/ui_element_kind.h"
#include "ui/ui_element.h"

void initialize_ui_element_as__ui_window(
        UI_Element *p_ui_element);

Graphics_Window *allocate_graphics_window_for__ui_window(
        Game *p_game,
        UI_Element *p_ui_window,
        Texture_Flags texture_flags_for__graphics_window);

void m_ui_window__poll_handler__default(
        UI_Element *p_this_ui_window,
        Game *p_game,
        Graphics_Window *p_graphics_window);

void m_ui_window__dipose_handler__default(
        UI_Element *p_ui_element,
        Game *p_game,
        Graphics_Window *p_graphics_window);

static inline
Graphics_Window *get_p_graphics_window_of__ui_window(
        UI_Element *p_ui_element) {
#ifndef NDEBUG
    if (!p_ui_element) {
        debug_error("get_p_graphics_window_of__ui_window, p_ui_element == 0.");
        return 0;
    }
    if (!is_ui_element_of__this_kind(
                p_ui_element, 
                UI_Element_Kind__Window)) {
        debug_error("get_p_graphics_window_of__ui_window, p_ui_element is not a UI_Element_Kind__Window.");
        return 0;
    }
#endif
    return p_ui_element->p_ui_window__graphics_window;
}

#endif
