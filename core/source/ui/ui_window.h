#include "defines.h"
#include "defines_weak.h"
#include "game.h"
#include "rendering/gfx_context.h"
#include "rendering/graphics_window.h"
#include "rendering/graphics_window_manager.h"
#include "ui/ui_element.h"
#include "ui/ui_window.h"
#include "ui/ui_manager.h"

void initialize_ui_element_as__ui_window(
        UI_Element *p_ui_element) {
    initialize_ui_element(
            p_ui_element, 
            0, 
            0, 
            0, 
            UI_Element_Kind__Window, 
            UI_FLAGS__NONE);

    set_ui_element__dropped_handler(
            p_ui_element, 
            m_ui_window__poll_handler__default);
    set_ui_element__dragged_handler(
            p_ui_element, 
            m_ui_window__poll_handler__default);
    set_ui_element__held_handler(
            p_ui_element, 
            m_ui_window__poll_handler__default);
    set_ui_element__clicked_handler(
            p_ui_element, 
            m_ui_window__poll_handler__default);
    set_ui_element__dispose_handler(
            p_ui_element, 
            m_ui_window__dipose_handler__default);
}

Graphics_Window *allocate_graphics_window_for__ui_window(
        Game *p_game,
        UI_Element *p_ui_window,
        Texture_Flags texture_flags_for__graphics_window) {
    p_ui_window->p_ui_window__graphics_window =
        allocate_graphics_window_with__uuid_from__graphics_window_manager(
                get_p_gfx_context_from__game(p_game), 
                get_p_graphics_window_manager_from__gfx_context(
                    get_p_gfx_context_from__game(p_game)), 
                GET_UUID_P(p_ui_window), 
                texture_flags_for__graphics_window);
    if (!p_ui_window->p_ui_window__graphics_window) {
        debug_error("allocate_graphics_window_for__ui_window, failed to allocate p_ui_window__graphics_window.");
        return 0;
    }
    return p_ui_window->p_ui_window__graphics_window;
}

void m_ui_window__poll_handler__default(
        UI_Element *p_this_ui_window,
        Game *p_game,
        Graphics_Window *p_graphics_window) {
    Graphics_Window *p_graphics_window_of__ui_window =
        get_p_graphics_window_of__ui_window(
                p_this_ui_window);
    if (!p_graphics_window_of__ui_window)
        return;
    if (!is_graphics_window_with__ui_manager(
                p_graphics_window_of__ui_window)) {
        return;
    }
    poll_ui_manager__update(
            get_p_ui_manager_from__graphics_window(
                p_graphics_window_of__ui_window), 
            p_game, 
            p_graphics_window_of__ui_window);
}

void m_ui_window__dipose_handler__default(
        UI_Element *p_this_ui_window,
        Game *p_game,
        Graphics_Window *p_graphics_window) {
    m_ui_element__dispose_handler__default(
            p_this_ui_window, 
            p_game, 
            p_graphics_window);

    Graphics_Window *p_graphics_window_of__ui_window =
        get_p_graphics_window_of__ui_window(
                p_this_ui_window);
    if (!p_graphics_window_of__ui_window)
        return;
    
    release_graphics_window_from__graphics_window_manager(
            p_game,
            p_graphics_window_of__ui_window);
}
