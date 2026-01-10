#include "collisions/hitbox_aabb.h"
#include "collisions/hitbox_aabb_manager.h"
#include "debug/debug.h"
#include "defines.h"
#include "defines_weak.h"
#include "platform.h"
#include "platform_defaults.h"
#include "platform_defines.h"
#include "rendering/gfx_context.h"
#include "rendering/graphics_window.h"
#include "rendering/sprite.h"
#include "rendering/sprite_manager.h"
#include "rendering/sprite_pool.h"
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

    memset(((u8*)p_ui_element
                + sizeof(Serialization_Header)),
            0,
            sizeof(UI_Element)
            - sizeof(Serialization_Header));

    p_ui_element->p_parent = p_ui_element__parent;
    p_ui_element->p_child = p_ui_element__child;
    p_ui_element->p_next = p_ui_element__next;
    p_ui_element->the_kind_of_ui_element__this_is =
        kind_of_ui_element;

    p_ui_element->ui_flags = ui_flags;

    set_ui_element__dispose_handler(
            p_ui_element, 
            m_ui_element__dispose_handler__default);
    set_ui_element__compose_handler(
            p_ui_element, 
            m_ui_element__compose_handler__default);
    set_ui_element__transformed_handler(
            p_ui_element, 
            m_ui_element__transformed_handler__default);
}

void m_ui_element__dispose_handler__default(
        UI_Element *p_this_ui_element,
        Game *p_game,
        Graphics_Window *p_graphics_window) {
    if (does_ui_element_have__child(p_this_ui_element)) {
        UI_Element *p_child =
            get_child_of__ui_element(p_this_ui_element);
        if (does_ui_element_have__dispose_handler(p_child)) {
            p_child->m_ui_dispose_handler(
                    p_child,
                    p_game,
                    p_graphics_window);
        }
    }
    if (does_ui_element_have__next(
                p_this_ui_element)) {
        UI_Element *p_next =
            get_next__ui_element(p_this_ui_element);
        if (does_ui_element_have__dispose_handler(p_next)) {
            p_next->m_ui_dispose_handler(
                    p_next,
                    p_game,
                    p_graphics_window);
        }
    }
    
    p_this_ui_element->p_parent = 0;
    p_this_ui_element->p_child = 0;
    p_this_ui_element->p_next = 0;

    Hitbox_AABB *p_hitbox_aabb =
        get_p_hitbox_aabb_by__uuid_u32_from__hitbox_aabb_manager(
                get_p_hitbox_aabb_manager_from__game(p_game), 
                GET_UUID_P(p_this_ui_element));
    if (p_hitbox_aabb) {
        release_hitbox_aabb_from__hitbox_aabb_manager(
                p_game,
                get_p_hitbox_aabb_manager_from__game(p_game), 
                p_hitbox_aabb);
    }

    Sprite_Pool *p_sprite_pool =
        get_p_sprite_pool_from__graphics_window(
                p_game,
                p_graphics_window);
    if (!p_sprite_pool)
        return;
    if (does_ui_element_have__sprite(
                p_sprite_pool,
                p_this_ui_element)) {
        Sprite *p_sprite =
            get_p_sprite_by__uuid_from__sprite_pool(
                    p_sprite_pool,
                    GET_UUID_P(p_this_ui_element));
        if (p_sprite) {
            release_sprite_from__sprite_pool(
                    get_p_gfx_context_from__game(p_game), 
                    p_sprite_pool,
                    p_sprite);
        }
    }
}

// TODO: remove
void m_ui_element__dispose_handler__default_collection(
        UI_Element *p_this_ui_element,
        Game *p_game,
        Graphics_Window *p_graphics_window) {
    m_ui_element__dispose_handler__default(
            p_this_ui_element, 
            p_game,
            p_graphics_window);
    UI_Element *p_next =
        get_next__ui_element(p_this_ui_element);
    if (!p_next) return;

    do {
        UI_Element *p_disposing_element = p_next;
        p_next = get_next__ui_element(p_next);
        if (does_ui_element_have__dispose_handler(p_disposing_element)) {
            p_disposing_element->m_ui_dispose_handler(
                    p_disposing_element, 
                    p_game,
                    p_graphics_window);
        }
    } while (p_next);
}

void allocate_hitbox_for__ui_element(
        Game *p_game,
        Graphics_Window *p_graphics_window,
        UI_Element *p_ui_element,
        Quantity__u32 width_of__hitbox__u32,
        Quantity__u32 height_of__hitbox__u32,
        Vector__3i32 position_of__hitbox__3i32) {
    Hitbox_AABB *p_hitbox_aabb = 
        allocate_hitbox_aabb_from__hitbox_aabb_manager(
                get_p_hitbox_aabb_manager_from__game(p_game),
                GET_UUID_P(p_ui_element));

    set_size_of__hitbox_aabb(
            p_hitbox_aabb, 
            width_of__hitbox__u32, 
            height_of__hitbox__u32);

    set_hitbox__position_with__3i32(
            p_hitbox_aabb, 
            position_of__hitbox__3i32);

    if (!does_ui_element_have__transformed_handler(
                p_ui_element)) {
        return;
    }
    get_ui_element__transformed_handler(
            p_ui_element)(
                p_ui_element,
                p_hitbox_aabb,
                p_game,
                p_graphics_window);
}

void set_positions_of__ui_elements_in__succession(
        Game *p_game,
        Graphics_Window *p_graphics_window,
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
                p_game,
                p_graphics_window,
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
        Game *p_game,
        Graphics_Window *p_graphics_window,
        UI_Element *p_ui_element,
        Vector__3i32 position__3i32) {
    Vector__3i32 vector_of__child_relative_to__parent =
        VECTOR__3i32__0_0_0;
    Hitbox_AABB *p_hitbox_aabb =
        get_p_hitbox_aabb_of__ui_element(
                get_p_hitbox_aabb_manager_from__game(
                    p_game), 
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

    if (does_ui_element_have__transformed_handler(
                p_ui_element)) {
        p_ui_element->m_ui_transformed_handler(
                p_ui_element,
                p_hitbox_aabb,
                p_game,
                p_graphics_window);
    }

    if (!does_ui_element_have__child(p_ui_element)) {
        return;
    }

    set_position_3i32_of__ui_element(
            p_game,
            p_graphics_window,
            p_ui_element->p_child,
            add_vectors__3i32(
                vector_of__child_relative_to__parent, 
                get_position_3i32_of__hitbox_aabb(
                    p_hitbox_aabb)));
}

void set_ui_element__size(
        Game *p_game,
        Graphics_Window *p_graphics_window,
        UI_Element *p_ui_element,
        Quantity__u32 width, Quantity__u32 height) {
    Hitbox_AABB *p_hitbox_aabb =
        get_p_hitbox_aabb_of__ui_element(
                get_p_hitbox_aabb_manager_from__game(
                    p_game), 
                p_ui_element);
    set_size_of__hitbox_aabb(
            p_hitbox_aabb,
            width, 
            height);
    if (does_ui_element_have__transformed_handler(
                p_ui_element)) {
        p_ui_element->m_ui_transformed_handler(
                p_ui_element,
                p_hitbox_aabb,
                p_game,
                p_graphics_window);
    }
}

void set_ui_element__hitbox(
        Game *p_game,
        Graphics_Window *p_graphics_window,
        UI_Element *p_ui_element,
        Quantity__u32 width, 
        Quantity__u32 height,
        Vector__3i32 position__3i32) {
    Hitbox_AABB *p_hitbox_aabb =
        get_p_hitbox_aabb_of__ui_element(
                get_p_hitbox_aabb_manager_from__game(
                    p_game),
                p_ui_element);
    if (!p_hitbox_aabb) {
        debug_error("set_ui_element__hitbox, p_ui_element lacks hitbox.");
        return;
    }
    initialize_hitbox_as__allocated(
            p_hitbox_aabb, 
            GET_UUID_P(p_hitbox_aabb), 
            width, 
            height, 
            vector_3i32_to__vector_3i32F4(
                position__3i32));
    if (does_ui_element_have__transformed_handler(
                p_ui_element)) {
        p_ui_element->m_ui_transformed_handler(
                p_ui_element,
                p_hitbox_aabb,
                p_game,
                p_graphics_window);
    }
}

void release_ui_element__sprite(
        Game *p_game,
        Graphics_Window *p_graphics_window,
        UI_Element *p_ui_element) {
    Sprite_Pool *p_sprite_pool =
        get_p_sprite_pool_from__graphics_window(
                p_game,
                p_graphics_window);
#ifndef NDEBUG
    if (!does_ui_element_have__sprite(
                p_sprite_pool,
                p_ui_element)) {
        debug_error("release_ui_element__PLATFORM_sprite, p_PLATFORM_sprite is null.");
        return;
    }
#endif

    Sprite *p_sprite =
        get_p_sprite_by__uuid_from__sprite_pool(
                p_sprite_pool,
                GET_UUID_P(p_ui_element));

    if (p_sprite) {
        release_sprite_from__sprite_pool(
                get_p_gfx_context_from__game(p_game), 
                p_sprite_pool,
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
    if (!does_ui_element_have__compose_handler(
                p_ui_element)) {
        set_ui_element__compose_handler(
                p_ui_element, 
                m_ui_element__compose_handler__default);
    }
}

const UI_Tile_Span *get_ui_tile_span_of__ui_element(
        Hitbox_AABB_Manager *p_hitbox_aabb_manager,
        Graphics_Window *p_graphics_window,
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
        >> UI_TILE__WIDTH_AND__HEIGHT__BIT_SHIFT
        ;
    *p_height_in__tiles =
        p_hitbox_aabb
        ->height__quantity_u32
        >> UI_TILE__WIDTH_AND__HEIGHT__BIT_SHIFT
        ;

    *p_index_x__u32 = 
        ((get_x_i32_from__hitbox(p_hitbox_aabb)
          - p_graphics_window->position_of__gfx_window.x__i32
          + (p_graphics_window->width_of__graphics_window__u32 >> 1))
        >> UI_TILE__WIDTH_AND__HEIGHT__BIT_SHIFT)
        - (*p_width_in__tiles >> 1);
    *p_index_y__u32 =
        ((get_y_i32_from__hitbox(p_hitbox_aabb)
          - p_graphics_window->position_of__gfx_window.y__i32
          + (p_graphics_window->height_of__graphics_window__u32 >> 1))
        >> UI_TILE__WIDTH_AND__HEIGHT__BIT_SHIFT)
        - (*p_height_in__tiles >> 1);

    return &p_ui_element->ui_tile_span;
}

void m_ui_element__transformed_handler__default(
        UI_Element *p_this_ui_element,
        Hitbox_AABB *p_hitbox_aabb,
        Game *p_game,
        Graphics_Window *p_graphics_window) {
    if (does_ui_element_have__child(
                p_this_ui_element)) {
        set_position_3i32_of__ui_element(
                p_game, 
                p_graphics_window, 
                get_child_of__ui_element(p_this_ui_element), 
                get_position_3i32_of__hitbox_aabb(
                    p_hitbox_aabb));
    }
}

void m_ui_element__compose_handler__default(
        UI_Element *p_ui_element,
        Game *p_game,
        Graphics_Window *p_graphics_window) {
    Hitbox_AABB_Manager *p_hitbox_aabb_manager =
        get_p_hitbox_aabb_manager_from__game(p_game);
    Quantity__u32 width_of__ui_tile_span; 
    Quantity__u32 height_of__ui_tile_span;
    Index__u32 index_x__u32; 
    Index__u32 index_y__u32;
    const UI_Tile_Span *p_const_ui_tile_span =
        get_ui_tile_span_of__ui_element(
                p_hitbox_aabb_manager,
                p_graphics_window,
                p_ui_element,
                &width_of__ui_tile_span,
                &height_of__ui_tile_span,
                &index_x__u32,
                &index_y__u32);

    generate_ui_span_in__ui_tile_map(
            get_ui_tile_map_from__graphics_window(
                p_graphics_window),
            p_const_ui_tile_span,
            width_of__ui_tile_span,
            height_of__ui_tile_span,
            index_x__u32,
            index_y__u32);

    if (!does_ui_element_have__child(
                p_ui_element)) {
        return;
    }

    UI_Element *p_ui_element__child =
        get_child_of__ui_element(p_ui_element);

    if (!does_ui_element_have__compose_handler(
                p_ui_element__child)) {
        return;
    }

    p_ui_element__child->m_ui_compose_handler(
            p_ui_element__child,
            p_game,
            p_graphics_window);
}

void m_ui_element__compose_handler__default_non_recursive(
        UI_Element *p_ui_element,
        Game *p_game,
        Graphics_Window *p_graphics_window) {
    Hitbox_AABB_Manager *p_hitbox_aabb_manager =
        get_p_hitbox_aabb_manager_from__game(p_game);
    Quantity__u32 width_of__ui_tile_span; 
    Quantity__u32 height_of__ui_tile_span;
    Index__u32 index_x__u32; 
    Index__u32 index_y__u32;
    const UI_Tile_Span *p_const_ui_tile_span =
        get_ui_tile_span_of__ui_element(
                p_hitbox_aabb_manager,
                p_graphics_window,
                p_ui_element,
                &width_of__ui_tile_span,
                &height_of__ui_tile_span,
                &index_x__u32,
                &index_y__u32);

    generate_ui_span_in__ui_tile_map(
            get_ui_tile_map_from__graphics_window(
                p_graphics_window),
            p_const_ui_tile_span,
            width_of__ui_tile_span,
            height_of__ui_tile_span,
            index_x__u32,
            index_y__u32);
}

void m_ui_element__compose_handler__default_only_recursive(
        UI_Element *p_ui_element,
        Game *p_game,
        Graphics_Window *p_graphics_window) {
    if (!does_ui_element_have__child(
                p_ui_element)) {
        return;
    }

    UI_Element *p_ui_element__child =
        get_child_of__ui_element(p_ui_element__child);

    if (!does_ui_element_have__compose_handler(
                p_ui_element__child)) {
        return;
    }

    p_ui_element__child->m_ui_compose_handler(
            p_ui_element__child,
            p_game,
            p_graphics_window);
}

bool does_ui_element_have__sprite(
        Sprite_Pool *p_sprite_pool,
        UI_Element *p_ui_element) {
    return get_p_sprite_by__uuid_from__sprite_pool(
            p_sprite_pool, 
            GET_UUID_P(p_ui_element));
}

void set_child_of__ui_element(
        UI_Element *p_ui_element,
        UI_Element *p_ui_element__child) {
    if (p_ui_element__child == p_ui_element) {
        // this would cause unchecked infinite loops!
        debug_error("set_child_of__ui_element, cannot set self as child.");
        return;
    }
    p_ui_element->p_child =
        p_ui_element__child;
}

void set_parent_of__ui_element(
        UI_Element *p_ui_element,
        UI_Element *p_ui_element__parent) {
    if (p_ui_element__parent == p_ui_element) {
        // this would cause unchecked infinite loops!
        debug_error("set_parent_of__ui_element, cannot set self as parent.");
        return;
    }
    p_ui_element->p_parent =
        p_ui_element__parent;
}


void update_ui_element_origin__relative_to__recursively(
        Game *p_game,
        UI_Element *p_ui_element,
        Vector__3i32 position__old__3i32,
        Vector__3i32 position__new__3i32) {
#ifndef NDEBUG
    if (!p_ui_element) {
        debug_error("update_ui_element_origin__relative_to__recursively, p_ui_element == 0.");
        return;
    }
#endif
    update_ui_element_origin__relative_to(
            p_game,
            p_ui_element, 
            position__old__3i32, 
            position__new__3i32);
    if (does_ui_element_have__child(
                p_ui_element)) {
        update_ui_element_origin__relative_to__recursively(
                p_game,
                get_child_of__ui_element(p_ui_element), 
                position__old__3i32, 
                position__new__3i32);
    }
    if (does_ui_element_have__next(
                p_ui_element)) {
        update_ui_element_origin__relative_to__recursively(
                p_game,
                get_next__ui_element(p_ui_element), 
                position__old__3i32, 
                position__new__3i32);
    }
}

void update_ui_element_origin__relative_to(
        Game *p_game,
        UI_Element *p_ui_element,
        Vector__3i32 position__old__3i32,
        Vector__3i32 position__new__3i32) {
#ifndef NDEBUG
    if (!p_ui_element) {
        debug_error("update_ui_element_origin__relative_to, p_ui_element == 0.");
        return;
    }
#endif
    Hitbox_AABB *p_hitbox_aabb =
        get_p_hitbox_aabb_of__ui_element(
                get_p_hitbox_aabb_manager_from__game(p_game), 
                p_ui_element);

    if (!p_hitbox_aabb) {
        return;
    }

    Vector__3i32 position_final__3i32 =
        add_vectors__3i32(
                subtract_vectors__3i32(
                    get_position_3i32_of__hitbox_aabb(
                        p_hitbox_aabb),
                    position__old__3i32),
                position__new__3i32);

    set_hitbox__position_with__3i32(
            p_hitbox_aabb, 
            position_final__3i32);
}
