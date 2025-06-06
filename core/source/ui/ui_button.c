#include "debug/debug.h"
#include "defines.h"
#include "defines_weak.h"
#include "types/implemented/graphics_window_kind.h"
#include "ui/ui_element.h"
#include <ui/ui_button.h>

void initialize_ui_element_as__button(
        UI_Element *p_ui_button,
        m_UI_Clicked m_ui_button__clicked_handler,
        bool is_toggleable_or__non_toggleable,
        bool is_toggled_or__not_toggled) {
    initialize_ui_element(
            p_ui_button, 
            p_ui_button->p_parent,
            p_ui_button->p_child,
            p_ui_button->p_next,
            UI_Element_Kind__Button, 
            p_ui_button->ui_flags);
    set_ui_element__clicked_handler(
            p_ui_button, 
            m_ui_button__clicked_handler);
    set_ui_button_as__toggleable_or__non_toggleable(
            p_ui_button, 
            is_toggleable_or__non_toggleable);
    set_ui_button_as__toggled_or__not_toggled(
            p_ui_button, 
            is_toggled_or__not_toggled);
}

void m_ui_button__clicked_handler__default(
        UI_Element *p_this_button,
        Game *p_game,
        Graphics_Window *p_graphics_window) {
    debug_info__verbose("Button clicked %p, is toggled: %b", 
            p_this_button, is_ui_button__toggled(p_this_button));
}

void m_ui_button__held_handler__default(
        UI_Element *p_this_button,
        Game *p_game,
        Graphics_Window *p_graphics_window) {
}
