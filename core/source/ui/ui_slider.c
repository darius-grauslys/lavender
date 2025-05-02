#include "collisions/hitbox_aabb.h"
#include "defines.h"
#include "defines_weak.h"
#include "game.h"
#include "numerics.h"
#include "platform.h"
#include "rendering/aliased_texture_manager.h"
#include "rendering/gfx_context.h"
#include "rendering/graphics_window_manager.h"
#include "ui/ui_element.h"
#include "vectors.h"
#include <ui/ui_slider.h>
#include "rendering/graphics_window.h"

void initialize_ui_element_as__slider(
        UI_Element *p_ui_slider,
        Vector__3i32 spanning_length__3i32,
        m_UI_Dragged m_ui_dragged_handler,
        bool is_snapped_x_or_y__axis) {
    initialize_ui_element(
            p_ui_slider, 
            p_ui_slider->p_parent,
            p_ui_slider->p_child,
            p_ui_slider->p_next,
            UI_Element_Kind__Slider, 
            p_ui_slider->ui_flags);
    set_ui_element__dragged_handler(
            p_ui_slider, 
            m_ui_dragged_handler);
    set_ui_element__transformed_handler(
            p_ui_slider, 
            m_ui_slider__transformed_handler__default);
    set_ui_element__dispose_handler(
            p_ui_slider, 
            m_ui_slider__dispose_handler__gfx_window__default);

    if (is_snapped_x_or_y__axis) {
        set_ui_element_as__snapped_x_axis(p_ui_slider);
    } else {
        set_ui_element_as__snapped_y_axis(p_ui_slider);
    }

    p_ui_slider
        ->slider__spanning_length__3i32 =
        spanning_length__3i32;
}

void m_ui_slider__dragged_handler__default(
        UI_Element *p_this_draggable,
        Game *p_game,
        Graphics_Window *p_graphics_window) {
    Input *p_input =
        get_p_input_from__game(p_game);
    bool is_snapped_x_or__y_axis =
        is_ui_element__snapped_x_or_y_axis(p_this_draggable);

    Hitbox_AABB *p_hitbox_aabb =
        get_p_hitbox_aabb_of__ui_element(
                get_p_hitbox_aabb_manager_from__game(p_game), 
                p_this_draggable);

    if (!p_hitbox_aabb) {
        debug_error("m_ui_slider__dragged_handler__default, missing hitbox component.");
        set_ui_element_as__disabled(p_this_draggable);
        return;
    }

    i32 cursor_position =
        (is_snapped_x_or__y_axis)
        ? clamp__i32(
                p_input->cursor__3i32.x__i32
                - get_x_i32_from__hitbox(p_hitbox_aabb)
                + (get_width_u32_of__hitbox_aabb(p_hitbox_aabb) >> 1),
                0,
                get_width_u32_of__hitbox_aabb(
                    p_hitbox_aabb))
        : clamp__i32(
                -p_input->cursor__3i32.y__i32
                + get_y_i32_from__hitbox(p_hitbox_aabb)
                + (get_height_u32_of__hitbox_aabb(p_hitbox_aabb) >> 1),
                0,
                get_height_u32_of__hitbox_aabb(
                    p_hitbox_aabb))
        ;

    p_this_draggable
        ->slider__distance__u32 = 
        cursor_position;

    Vector__3i32 spanning_length__3i32 =
        get_ui_slider__spanning_length(
                p_this_draggable);

    m_ui_slider__transformed_handler__default(
            p_this_draggable, 
            p_hitbox_aabb, 
            p_game, 
            p_graphics_window);
}

void m_ui_slider__transformed_handler__default(
        UI_Element *p_this_ui_element,
        Hitbox_AABB *p_hitbox_aabb,
        Game *p_game,
        Graphics_Window *p_graphics_window) {
    if (!does_ui_element_have__child(p_this_ui_element)) {
        return; 
    }

    if (is_ui_element__snapped_x_or_y_axis(p_this_ui_element)) {
        set_position_3i32_of__ui_element(
                p_game, 
                p_graphics_window, 
                get_child_of__ui_element(p_this_ui_element), 
                add_vectors__3i32(
                    get_position_3i32_of__hitbox_aabb(p_hitbox_aabb), 
                    get_vector__3i32(
                        p_this_ui_element
                        ->slider__distance__u32
                        + (get_width_u32_of__hitbox_aabb(p_hitbox_aabb) >> 1),
                        0, 0)));
        return;
    }

    set_position_3i32_of__ui_element(
            p_game, 
            p_graphics_window, 
            get_child_of__ui_element(p_this_ui_element), 
            add_vectors__3i32(
                get_position_3i32_of__hitbox_aabb(p_hitbox_aabb), 
                get_vector__3i32(
                    0,
                    (get_height_u32_of__hitbox_aabb(p_hitbox_aabb) >> 1)
                    - p_this_ui_element
                    ->slider__distance__u32,
                    0)));
}

void m_ui_slider__dragged_handler__gfx_window__default(
        UI_Element *p_this_draggable,
        Game *p_game,
        Graphics_Window *p_graphics_window) {

    bool is_snapped_x_or_y__axis =
        is_ui_element__snapped_x_or_y_axis(p_this_draggable);

    Vector__3i32 spanning_length__3i32 =
        get_ui_slider__spanning_length(
                p_this_draggable);

    i32 spanning_length =
        (is_snapped_x_or_y__axis)
        ? spanning_length__3i32.x__i32
        : spanning_length__3i32.y__i32
        ;

    i32 offset = 
        get_offset_from__ui_slider_percentage(
                get_p_hitbox_aabb_manager_from__game(
                    p_game),
                p_this_draggable, 
                spanning_length);

    Vector__3i32 position__old__3i32 =
        get_vector__3i32(
                is_snapped_x_or_y__axis
                ? offset
                : 0,
                is_snapped_x_or_y__axis
                ? 0
                : offset,
                0);

    m_ui_slider__dragged_handler__default(
            p_this_draggable, 
            p_game, 
            p_graphics_window);

    offset = 
        get_offset_from__ui_slider_percentage(
                get_p_hitbox_aabb_manager_from__game(
                    p_game),
                p_this_draggable, 
                spanning_length);

    Vector__3i32 position__new__3i32 =
        get_vector__3i32(
                is_snapped_x_or_y__axis
                ? offset
                : 0,
                is_snapped_x_or_y__axis
                ? 0
                : offset,
                0);
    
    Graphics_Window *p_graphics_window__owned_by__slider =
        get_p_graphics_window_by__uuid_from__graphics_window_manager(
                get_p_graphics_window_manager_from__gfx_context(
                    get_p_gfx_context_from__game(p_game)), 
                GET_UUID_P(p_this_draggable));

    set_position_3i32_of__graphics_window__relative_to(
            p_game,
            p_graphics_window__owned_by__slider, 
            position__old__3i32,
            position__new__3i32);
}

void m_ui_slider__dispose_handler__gfx_window__default(
        UI_Element *p_this_draggable,
        Game *p_game,
        Graphics_Window *p_graphics_window) {
    m_ui_element__dispose_handler__default(
            p_this_draggable, 
            p_game, 
            p_graphics_window);

    Graphics_Window *p_graphics_window__owned_by__this_slider =
        get_p_graphics_window_by__uuid_from__graphics_window_manager(
                get_p_graphics_window_manager_from__gfx_context(
                    get_p_gfx_context_from__game(p_game)), 
                GET_UUID_P(p_this_draggable));

    if (!p_graphics_window__owned_by__this_slider) {
        return;
    }

    release_graphics_window_from__graphics_window_manager(
            p_game, 
            p_graphics_window__owned_by__this_slider);
}
