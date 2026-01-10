#include "defines.h"
#include "defines_weak.h"
#include "game.h"
#include "rendering/graphics_window.h"
#include "ui/ui_element.h"
#include "ui/ui_manager.h"
#include "vectors.h"
#include <ui/ui_drop_zone.h>

void initialize_ui_element_as__drop_zone(
        UI_Element *p_ui_drop_zone,
        m_UI_Receive_Drop m_ui_receive_drop_handler) {
    initialize_ui_element(
            p_ui_drop_zone, 
            p_ui_drop_zone->p_parent,
            p_ui_drop_zone->p_child,
            p_ui_drop_zone->p_next,
            UI_Element_Kind__Drop_Zone, 
            p_ui_drop_zone->ui_flags);
    set_ui_element__receive_drop_handler(
            p_ui_drop_zone, 
            m_ui_receive_drop_handler);
}

void m_ui_drop_zone__receive_drop_handler__default(
        UI_Element *p_this_drop_zone,
        UI_Element *p_ui_element__dropped,
        Game *p_game,
        Graphics_Window *p_graphics_window) {
    if (!p_ui_element__dropped)
        return;

    UI_Manager *p_ui_manager =
        get_p_ui_manager_from__graphics_window(
                p_game,
                p_graphics_window);

#ifndef NDEBUG
    if (!p_ui_manager) {
        debug_error("m_ui_drop_zone__receive_drop_handler__default, p_ui_manager == 0.");
        return;
    }
#endif

    UI_Element *p_ui_element__former_parent_of__dropped =
        p_ui_element__dropped->p_parent;
    if (does_ui_element_have__parent(p_ui_element__dropped)) {
        swap_ui_element__children(
                p_ui_manager, 
                p_this_drop_zone, 
                p_ui_element__dropped->p_parent);
    } else {
        set_ui_element_as__the_parent_of__this_ui_element(
                p_ui_manager, 
                p_this_drop_zone, 
                p_ui_element__dropped);
        set_position_3i32_of__ui_element(
                p_game, 
                p_graphics_window, 
                p_ui_element__dropped, 
                get_position_3i32_from__p_ui_element(
                    get_p_hitbox_aabb_manager_from__game(p_game), 
                    p_this_drop_zone));
    }
    if (!p_ui_element__former_parent_of__dropped)
        return;
    if (does_ui_element_have__dropped_handler(
                p_ui_element__former_parent_of__dropped
                ->p_child)) {
        p_ui_element__former_parent_of__dropped
            ->p_child
            ->m_ui_dropped_handler(
                    p_ui_element__former_parent_of__dropped
                    ->p_child,
                    p_game,
                    p_graphics_window);
    }
    if (does_ui_element_have__receive_drop_handler(
                p_ui_element__former_parent_of__dropped)) {
        p_ui_element__former_parent_of__dropped
            ->m_ui_receive_drop_handler(
                    p_ui_element__former_parent_of__dropped,
                    0,
                    p_game,
                    p_graphics_window);
    }
}
