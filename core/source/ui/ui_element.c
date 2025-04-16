#include "collisions/hitbox_aabb.h"
#include "collisions/hitbox_aabb_manager.h"
#include "debug/debug.h"
#include "defines.h"
#include "defines_weak.h"
#include "platform.h"
#include "platform_defaults.h"
#include "rendering/gfx_context.h"
#include "rendering/sprite.h"
#include "rendering/sprite_manager.h"
#include "serialization/serialization_header.h"
#include "ui/ui_button.h"
#include "ui/ui_draggable.h"
#include "ui/ui_slider.h"
#include "ui/ui_tile_map.h"
#include <ui/ui_element.h>
#include <vectors.h>
#include <game.h>
#include <wctype.h>

void initialize_ui_element(
        UI_Element *p_ui_element,
        UI_Element *p_ui_element__parent,
        UI_Element *p_ui_element__child,
        UI_Element *p_ui_element__next,
        enum UI_Element_Kind kind_of_ui_element,
        UI_Flags__u16 ui_flags) {
    initialize_serialization_header_for__deallocated_struct(
            (Serialization_Header*)p_ui_element,
            sizeof(UI_Element));
    p_ui_element->p_parent = p_ui_element__parent;
    p_ui_element->p_child = p_ui_element__child;
    p_ui_element->p_next = p_ui_element__next;
    p_ui_element->the_kind_of_ui_element__this_is =
        kind_of_ui_element;
    p_ui_element->ui_flags = ui_flags;
    p_ui_element->m_ui_clicked_handler = 0;
    p_ui_element->m_ui_dragged_handler = 0;
    p_ui_element->m_ui_receive_drop_handler = 0;
    p_ui_element->m_ui_held_handler = 0;
    p_ui_element->m_ui_render_handler = 0;
    p_ui_element->m_ui_dispose_handler = 
        m_ui_element__dispose_handler__default;
}

void m_ui_element__dispose_handler__default(
        UI_Element *p_this_ui_element,
        Game *p_game) {
    set_ui_element_as__deallocated(p_this_ui_element);
    if (does_ui_element_have__child(p_this_ui_element)) {
        UI_Element *p_child =
            get_child_of__ui_element(p_this_ui_element);
        if (does_ui_element_have__dispose_handler(p_child)) {
            p_child->m_ui_dispose_handler(
                    p_child,
                    p_game);
        }
    }
    if (does_ui_element_have__sprite(
                get_p_sprite_manager_from__game(p_game),
                p_this_ui_element)) {
        Sprite *p_sprite =
            get_p_sprite_by__uuid_from__sprite_manager(
                    get_p_sprite_manager_from__game(p_game), 
                    GET_UUID_P(p_this_ui_element));
        if (p_sprite) {
            release_sprite_from__sprite_manager(
                    get_p_gfx_context_from__game(p_game), 
                    get_p_sprite_manager_from__game(p_game), 
                    p_sprite);
        }
    }
    p_this_ui_element->p_parent = 0;
    p_this_ui_element->p_child = 0;
    p_this_ui_element->p_next = 0;
}

void m_ui_element__dispose_handler__default_collection(
        UI_Element *p_this_ui_element,
        Game *p_game) {
    m_ui_element__dispose_handler__default(
            p_this_ui_element, 
            p_game);
    UI_Element *p_next =
        get_next__ui_element(p_this_ui_element);
    if (!p_next) return;

    do {
        UI_Element *p_disposing_element = p_next;
        p_next = get_next__ui_element(p_next);
        if (does_ui_element_have__dispose_handler(p_disposing_element)) {
            p_disposing_element->m_ui_dispose_handler(
                    p_disposing_element, 
                    p_game);
        }
    } while (p_next);
}

void set_positions_of__ui_elements_in__succession(
        Hitbox_AABB_Manager *p_hitbox_aabb_manager,
        UI_Element *p_ui_element__succession_collection,
        Vector__3i32 starting_position__3i32,
        i32 x__stride,
        Quantity__u32 quantity_of__elements_per_row,
        i32 y__stride) {
    Index__u32 index_of__current_ui_element = 0;
    Vector__3i32 current_position__3i32 = 
        starting_position__3i32;
    do {
        set_position_3i32_of__ui_element(
                p_hitbox_aabb_manager,
                p_ui_element__succession_collection, 
                current_position__3i32);
        if (++index_of__current_ui_element
                == quantity_of__elements_per_row) {
            index_of__current_ui_element = 0;
            current_position__3i32.y__i32 += y__stride;
            current_position__3i32.x__i32 =
                starting_position__3i32.x__i32;
        } else {
            current_position__3i32.x__i32 += x__stride;
        }
    } while (
            iterate_to_next__ui_element(
                &p_ui_element__succession_collection)
            && p_ui_element__succession_collection);
}

void set_position_3i32_of__ui_element(
        Hitbox_AABB_Manager *p_hitbox_aabb_manager,
        UI_Element *p_ui_element,
        Vector__3i32 position__3i32) {
    Vector__3i32 vector_of__child_relative_to__parent =
        VECTOR__3i32__0_0_0;
    Hitbox_AABB *p_hitbox_aabb =
        get_p_hitbox_aabb_of__ui_element(
                p_hitbox_aabb_manager, 
                p_ui_element);
    if (does_ui_element_have__child(p_ui_element)) {
        vector_of__child_relative_to__parent =
            subtract_vectors__3i32(
                position__3i32, 
                vector_3i32F4_to__vector_3i32(
                    get_position_3i32F4_of__hitbox_aabb(
                        p_hitbox_aabb)));
    }
    set_hitbox__position_with__3i32(
            p_hitbox_aabb, 
            position__3i32);
    if (does_ui_element_have__child(p_ui_element)) {
        set_position_3i32_of__ui_element(
                p_hitbox_aabb_manager,
                p_ui_element->p_child,
                add_vectors__3i32(
                    vector_of__child_relative_to__parent, 
                    get_position_3i32_from__p_ui_element(
                        p_hitbox_aabb_manager,
                        p_ui_element)));
    }
}

void release_ui_element__sprite(
        Gfx_Context *p_gfx_context,
        UI_Element *p_ui_element) {
#ifndef NDEBUG
    if (!does_ui_element_have__sprite(
                get_p_sprite_manager_from__gfx_context(
                    p_gfx_context),
                p_ui_element)) {
        debug_error("release_ui_element__PLATFORM_sprite, p_PLATFORM_sprite is null.");
        return;
    }
#endif

    Sprite *p_sprite =
        get_p_sprite_by__uuid_from__sprite_manager(
                get_p_sprite_manager_from__gfx_context(p_gfx_context), 
                GET_UUID_P(p_ui_element));

    if (p_sprite) {
        release_sprite_from__sprite_manager(
                p_gfx_context, 
                get_p_sprite_manager_from__gfx_context(p_gfx_context), 
                p_sprite);
    }
}

void set_ui_tile_span_of__ui_element(
        UI_Element *p_ui_element,
        UI_Tile_Span *p_ui_tile_span) {
    set_ui_element_as__using_ui_tile_span(
            p_ui_element);
    p_ui_element->ui_tile_span =
        *p_ui_tile_span;
}

const UI_Tile_Span *get_ui_tile_span_of__ui_element(
        Hitbox_AABB_Manager *p_hitbox_aabb_manager,
        UI_Element *p_ui_element,
        Quantity__u32 *p_width_in__tiles,
        Quantity__u32 *p_height_in__tiles,
        Index__u32 *p_index_x__u32, 
        Index__u32 *p_index_y__u32) {
    if (is_ui_element__using_sprite(
            p_ui_element)) {
        *p_width_in__tiles = 0;
        *p_height_in__tiles = 0;
        *p_index_x__u32 = 0;
        *p_index_y__u32 = 0;
        return 0;
    }

    Hitbox_AABB *p_hitbox_aabb =
        get_p_hitbox_aabb_by__uuid_u32_from__hitbox_aabb_manager(
                p_hitbox_aabb_manager, 
                GET_UUID_P(p_ui_element));

    if (!p_hitbox_aabb) {
        return 0;
    }

    *p_width_in__tiles = 
        p_hitbox_aabb
        ->width__quantity_u32
        / UI_TILE__WIDTH_IN__PIXELS;
    *p_height_in__tiles =
        p_hitbox_aabb
        ->height__quantity_u32
        / UI_TILE__HEIGHT_IN__PIXELS;

    *p_index_x__u32 = 
        (p_hitbox_aabb
        ->position__3i32F4
        .x__i32F4
        / UI_TILE__WIDTH_IN__PIXELS)
        - (*p_width_in__tiles >> 1);
    *p_index_y__u32 =
        (p_hitbox_aabb
        ->position__3i32F4
        .y__i32F4
        / UI_TILE__HEIGHT_IN__PIXELS)
        - (*p_height_in__tiles >> 1);

    return &p_ui_element->ui_tile_span;
}

void m_ui_render__element__tile_span(
        Hitbox_AABB_Manager *p_hitbox_aabb_manager,
        UI_Element *p_ui_element,
        PLATFORM_Graphics_Window *p_PLATFORM_gfx_window,
        Game *p_game) {
    Quantity__u32 width_of__ui_tile_span; 
    Quantity__u32 height_of__ui_tile_span;
    Index__u32 index_x__u32; 
    Index__u32 index_y__u32;
    const UI_Tile_Span *p_const_ui_tile_span =
        get_ui_tile_span_of__ui_element(
                p_hitbox_aabb_manager,
                p_ui_element,
                &width_of__ui_tile_span,
                &height_of__ui_tile_span,
                &index_x__u32,
                &index_y__u32);

    debug_error("m_ui_render__element__tile_span, impl");
}

bool does_ui_element_have__sprite(
        Sprite_Manager *p_sprite_manager,
        UI_Element *p_ui_element) {
    return get_p_sprite_by__uuid_from__sprite_manager(
            p_sprite_manager, 
            GET_UUID_P(p_ui_element));
}
