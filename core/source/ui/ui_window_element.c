#include "ui/ui_window_element.h"
#include "collisions/hitbox_aabb.h"
#include "debug/debug.h"
#include "defines_weak.h"
#include "game.h"
#include "rendering/gfx_context.h"
#include "rendering/graphics_window.h"
#include "rendering/graphics_window_manager.h"
#include "serialization/serialization_header.h"
#include "ui/ui_context.h"
#include "ui/ui_manager.h"
#include "ui/ui_element.h"
#include "vectors.h"

void _m_ui_window_element__update(
        UI_Element *p_this_ui_element,
        Game *p_game,
        Graphics_Window *p_gfx_window) {
    Graphics_Window *p_graphics_window =
        get_p_graphics_window_by__uuid_from__graphics_window_manager(
                get_p_graphics_window_manager_from__gfx_context(
                    get_p_gfx_context_from__game(p_game)), 
                GET_UUID_P(p_this_ui_element));
#ifndef NDEBUG
    if (!p_graphics_window) {
        debug_warning("The ui element has been disabled.");
        debug_error("_m_ui_window_element__clicked_handler, p_graphics_window == 0.");
        set_ui_element_as__disabled(p_this_ui_element);
        return;
    }
#endif

    UI_Manager *p_ui_manager =
        get_p_ui_manager_from__graphics_window(
                p_game, 
                p_graphics_window);

#ifndef NDEBUG
    if (!p_ui_manager) {
        debug_warning("The ui element has been disabled.");
        debug_error("_m_ui_window_element__clicked_handler, p_ui_manager == 0.");
        set_ui_element_as__disabled(p_this_ui_element);
        return;
    }
#endif

    poll_ui_manager__update(
            p_ui_manager,
            p_game,
            p_graphics_window);
}

void _m_ui_window_element__transformed_handler(
        UI_Element *p_this_ui_element,
        Hitbox_AABB *p_hitbox_aabb,
        Vector__3i32 position_NEW_of__hitbox__3i32,
        Game *p_game,
        Graphics_Window *p_gfx_window) {
    Graphics_Window *p_graphics_window =
        get_p_graphics_window_by__uuid_from__graphics_window_manager(
                get_p_graphics_window_manager_from__gfx_context(
                    get_p_gfx_context_from__game(p_game)), 
                GET_UUID_P(p_this_ui_element));
    if (!p_graphics_window) {
        debug_warning("The ui element has been disabled.");
        debug_error("_m_ui_window_element__clicked_handler, p_graphics_window == 0.");
        set_ui_element_as__disabled(p_this_ui_element);
        return;
    }
    set_position_3i32_of__graphics_window(
            p_game, 
            p_graphics_window, 
            position_NEW_of__hitbox__3i32);
}
void initialize_ui_element_as__window_element_and__open_window(
        UI_Element *p_ui_window_element,
        Game *p_game,
        Graphics_Window_Kind the_kind_of__graphics_window_to__open,
        Identifier__u32 uuid_of__parent_window__u32) {
    Graphics_Window *p_graphics_window =
        open_ui_window_with__this_uuid_and__parent_uuid(
                p_game, 
                the_kind_of__graphics_window_to__open,
                GET_UUID_P(p_ui_window_element),
                uuid_of__parent_window__u32);
    initialize_ui_element(
            p_ui_window_element, 
            p_ui_window_element->p_parent,
            p_ui_window_element->p_child,
            p_ui_window_element->p_next,
            UI_Element_Kind__Button, 
            p_ui_window_element->ui_flags);
    if (!p_graphics_window) {
        debug_error("initialize_ui_element_as__window_element_and__open_window, p_graphics_window == 0.");
        return;
    }
    set_ui_element__clicked_handler(
            p_ui_window_element, 
            _m_ui_window_element__update);
    set_ui_element__dragged_handler(
            p_ui_window_element, 
            _m_ui_window_element__update);
    set_ui_element__dropped_handler(
            p_ui_window_element, 
            _m_ui_window_element__update);
    set_ui_element__held_handler(
            p_ui_window_element, 
            _m_ui_window_element__update);
    set_ui_element__transformed_handler(
            p_ui_window_element, 
            _m_ui_window_element__transformed_handler);
}
