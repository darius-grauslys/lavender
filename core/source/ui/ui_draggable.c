#include "collisions/hitbox_aabb.h"
#include "collisions/hitbox_aabb_manager.h"
#include "defines.h"
#include "defines_weak.h"
#include "game.h"
#include "ui/ui_element.h"
#include "vectors.h"
#include <ui/ui_draggable.h>

void initialize_ui_element_as__draggable(
        UI_Element *p_ui_draggable,
        Quantity__u8 width__u8,
        Quantity__u8 height__u8,
        Vector__3i32 position__3i32,
        m_UI_Dragged m_ui_dragged_handler) {
    initialize_ui_element(
            p_ui_draggable, 
            p_ui_draggable->p_parent,
            p_ui_draggable->p_child,
            p_ui_draggable->p_next,
            UI_Element_Kind__Draggable, 
            p_ui_draggable->ui_flags);
    set_ui_element__dragged_handler(
            p_ui_draggable, 
            m_ui_dragged_handler);
    set_ui_element__dropped_handler(
            p_ui_draggable, 
            m_ui_draggable__dropped_handler__default);
}

void m_ui_draggable__dragged_handler__default(
        UI_Element *p_this_draggable,
        Game *p_game) {
    Vector__3i32 position =
        p_game->input.cursor__3i32;

    Hitbox_AABB *p_hitbox_aabb =
        get_p_hitbox_aabb_by__uuid_u32_from__hitbox_aabb_manager(
                get_p_hitbox_aabb_manager_from__game(p_game), 
                GET_UUID_P(p_this_draggable));

    if (!p_hitbox_aabb) {
        debug_error("m_ui_draggable__dragged_handler__default, missing hitbox component.");
        set_ui_element_as__disabled(p_this_draggable);
        return;
    }

    position.x__i32 -= 
        get_width_u32_of__hitbox_aabb(p_hitbox_aabb) >> 1;
    position.y__i32 -= 
        get_height_u32_of__hitbox_aabb(p_hitbox_aabb) >> 1;

    set_position_3i32_of__ui_element(
            get_p_hitbox_aabb_manager_from__game(p_game),
            p_this_draggable, 
            position);
}

void m_ui_draggable__dropped_handler__default(
        UI_Element *p_this_draggable,
        Game *p_game) {
    if (!p_this_draggable->p_parent) {
        return;
    }

    set_position_3i32_of__ui_element(
            get_p_hitbox_aabb_manager_from__game(p_game),
            p_this_draggable, 
            get_position_3i32_from__p_ui_element(
                get_p_hitbox_aabb_manager_from__game(p_game),
                p_this_draggable->p_parent));
}
