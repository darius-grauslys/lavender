#ifndef UI_ELEMENT_H
#define UI_ELEMENT_H

#include "collisions/hitbox_aabb.h"
#include "collisions/hitbox_aabb_manager.h"
#include "defines_weak.h"
#include "numerics.h"
#include "platform.h"
#include "serialization/identifiers.h"
#include "serialization/serialization_header.h"
#include "vectors.h"
#include <defines.h>

void initialize_ui_element(
        UI_Element *p_ui_element,
        UI_Element *p_ui_element__parent,
        UI_Element *p_ui_element__child,
        UI_Element *p_ui_element__next,
        enum UI_Element_Kind kind_of_ui_element,
        UI_Flags__u16 ui_flags);

void m_ui_element__dispose_handler__default(
        UI_Element *p_this_ui_element,
        Game *p_game,
        Graphics_Window *p_graphics_window);

void allocate_hitbox_for__ui_element(
        Game *p_game,
        Graphics_Window *p_graphics_window,
        UI_Element *p_ui_element,
        Quantity__u32 width_of__hitbox__u32,
        Quantity__u32 height_of__hitbox__u32,
        Vector__3i32 position_of__hitbox__3i32);

void set_positions_of__ui_elements_in__succession(
        Game *p_game,
        Graphics_Window *p_graphics_window,
        UI_Element *p_ui_element__succession_collection,
        Vector__3i32 starting_position__3i32,
        i32 x__stride,
        Quantity__u32 quantity_of__elements_per_row,
        i32 y__stride);

void set_position_3i32_of__ui_element(
        Game *p_game,
        Graphics_Window *p_graphics_window,
        UI_Element *p_ui_element,
        Vector__3i32 position__3i32);

void set_ui_element__size(
        Game *p_game,
        Graphics_Window *p_graphics_window,
        UI_Element *p_ui_element,
        Quantity__u32 width, Quantity__u32 height);

void set_ui_element__hitbox(
        Game *p_game,
        Graphics_Window *p_graphics_window,
        UI_Element *p_ui_element,
        Quantity__u32 width, 
        Quantity__u32 height,
        Vector__3i32 position__3i32);

void set_ui_element__sprite(
        UI_Element *p_ui_element,
        Sprite *p_sprite);

void release_ui_element__PLATFORM_sprite(
        Gfx_Context *p_gfx_context,
        UI_Element *p_ui_element);

void set_ui_tile_span_of__ui_element(
        UI_Element *p_ui_element,
        UI_Tile_Span *p_ui_tile_span);

const UI_Tile_Span *get_ui_tile_span_of__ui_element(
        Hitbox_AABB_Manager *p_hitbox_aabb_manager,
        Graphics_Window *p_graphics_window,
        UI_Element *p_ui_element,
        Quantity__u32 *p_width_in__tiles,
        Quantity__u32 *p_height_in__tiles,
        Index__u32 *p_index_x__u32, 
        Index__u32 *p_index_y__u32);

void m_ui_element__compose_handler__default(
        UI_Element *p_ui_element,
        Game *p_game,
        Graphics_Window *p_graphics_window);

void m_ui_element__compose_handler__default_non_recursive(
        UI_Element *p_ui_element,
        Game *p_game,
        Graphics_Window *p_graphics_window);

void m_ui_element__compose_handler__default_only_recursive(
        UI_Element *p_ui_element,
        Game *p_game,
        Graphics_Window *p_graphics_window);

void m_ui_element__transformed_handler__default(
        UI_Element *p_this_ui_element,
        Hitbox_AABB *p_hitbox_aabb,
        Game *p_game,
        Graphics_Window *p_graphics_window);

bool does_ui_element_have__sprite(
        Sprite_Manager *p_sprite_manager,
        UI_Element *p_ui_element);

void set_child_of__ui_element(
        UI_Element *p_ui_element,
        UI_Element *p_ui_element__child);

void set_parent_of__ui_element(
        UI_Element *p_ui_element,
        UI_Element *p_ui_element__parent);

void update_ui_element_origin__relative_to__recursively(
        Game *p_game,
        UI_Element *p_ui_element,
        Vector__3i32 position__old__3i32,
        Vector__3i32 position__new__3i32);

void update_ui_element_origin__relative_to(
        Game *p_game,
        UI_Element *p_ui_element,
        Vector__3i32 position__old__3i32,
        Vector__3i32 position__new__3i32);

static inline
Hitbox_AABB *get_p_hitbox_aabb_of__ui_element(
        Hitbox_AABB_Manager *p_hitbox_aabb_manager,
        UI_Element *p_ui_element) {
    return get_p_hitbox_aabb_by__uuid_u32_from__hitbox_aabb_manager(
            p_hitbox_aabb_manager, 
            GET_UUID_P(p_ui_element));
}

static inline
void clamp_p_vector_3i32_to__ui_element(
        Hitbox_AABB_Manager *p_hitbox_aabb_manager,
        UI_Element *p_ui_element,
        Vector__3i32 *p_position__3i32) {
    clamp_p_vector_3i32_to__hitbox(
            get_p_hitbox_aabb_of__ui_element(
                p_hitbox_aabb_manager, 
                p_ui_element), 
            p_position__3i32);
}

static inline 
Signed_Index__i32 get_x_i32_from__p_ui_element(
        Hitbox_AABB_Manager *p_hitbox_aabb_manager,
        UI_Element *p_ui_element) {
    return get_x_i32_from__hitbox(
            get_p_hitbox_aabb_of__ui_element(
                p_hitbox_aabb_manager, 
                p_ui_element));
}
static inline 
Signed_Index__i32 get_y_i32_from__p_ui_element(
        Hitbox_AABB_Manager *p_hitbox_aabb_manager,
        UI_Element *p_ui_element) {
    return get_y_i32_from__hitbox(
            get_p_hitbox_aabb_of__ui_element(
                p_hitbox_aabb_manager, 
                p_ui_element));
}
static inline 
Signed_Index__i32 get_z_i32_from__p_ui_element(
        Hitbox_AABB_Manager *p_hitbox_aabb_manager,
        UI_Element *p_ui_element) {
    return get_z_i32_from__hitbox(
            get_p_hitbox_aabb_of__ui_element(
                p_hitbox_aabb_manager, 
                p_ui_element));
}

static inline 
Vector__3i32 get_position_3i32_from__p_ui_element(
        Hitbox_AABB_Manager *p_hitbox_aabb_manager,
        UI_Element *p_ui_element) {
    return vector_3i32F4_to__vector_3i32(
            get_position_3i32F4_of__hitbox_aabb(
                get_p_hitbox_aabb_of__ui_element(
                    p_hitbox_aabb_manager, 
                    p_ui_element)));
}

static inline 
Vector__3i32F4 get_position_3i32F4_from__p_ui_element(
        Hitbox_AABB_Manager *p_hitbox_aabb_manager,
        UI_Element *p_ui_element) {
    return get_position_3i32F4_of__hitbox_aabb(
            get_p_hitbox_aabb_of__ui_element(
                p_hitbox_aabb_manager, 
                p_ui_element));
}

static inline
Quantity__u32 get_width_from__p_ui_element(
        Hitbox_AABB_Manager *p_hitbox_aabb_manager,
        UI_Element *p_ui_element) {
    return get_width_u32_of__hitbox_aabb(
            get_p_hitbox_aabb_of__ui_element(
                p_hitbox_aabb_manager, 
                p_ui_element));
} 

static inline
Quantity__u32 get_height_from__p_ui_element(
        Hitbox_AABB_Manager *p_hitbox_aabb_manager,
        UI_Element *p_ui_element) {
    return get_height_u32_of__hitbox_aabb(
            get_p_hitbox_aabb_of__ui_element(
                p_hitbox_aabb_manager, 
                p_ui_element));
}

///
/// Logically associate a contiguous collection of
/// UI_Element via p_next pointers. Forming a one-way
/// linked list.
///
static inline
void link_ui_element_to__this_ui_element(
        UI_Element *p_predecessor,
        UI_Element *p_successor) {
    if (p_predecessor == p_successor)
        p_predecessor->p_next = 0;
    p_predecessor->p_next =
        p_successor;
}

static inline
UI_Element *get_next__ui_element(
        UI_Element *p_ui_element) {
    return p_ui_element->p_next;
}

static inline
UI_Element *get_parent_of__ui_element(
        UI_Element *p_ui_element) {
    return p_ui_element->p_parent;
}

static inline
UI_Element *get_child_of__ui_element(
        UI_Element *p_ui_element) {
    return p_ui_element->p_child;
}

static inline
UI_Element *iterate_to_next__ui_element(
        UI_Element * volatile *p_ui_element_ptr) {
    if (!(*p_ui_element_ptr))
        return 0;
    UI_Element *p_iterated_element = *p_ui_element_ptr;
    *p_ui_element_ptr =
        (*p_ui_element_ptr)->p_next;
    return p_iterated_element;
}

static inline 
UI_Element *iterate_to_parent_of__ui_element(
        UI_Element * volatile *p_ui_element_ptr) {
    if (!(*p_ui_element_ptr))
        return 0;
    UI_Element *p_iterated_element = *p_ui_element_ptr;
    *p_ui_element_ptr =
        (*p_ui_element_ptr)->p_parent;
    return p_iterated_element;
}

static inline 
UI_Element *iterate_to_child_of__ui_element(
        UI_Element * volatile *p_ui_element_ptr) {
    if (!(*p_ui_element_ptr))
        return 0;
    UI_Element *p_iterated_element = *p_ui_element_ptr;
    *p_ui_element_ptr =
        (*p_ui_element_ptr)->p_child;
    return p_iterated_element;
}

static inline
bool is_ui_element_of__this_kind(
        UI_Element *p_ui_element,
        enum UI_Element_Kind the_kind_of_ui_element) {
    return p_ui_element->the_kind_of_ui_element__this_is
        == the_kind_of_ui_element;
}

static inline
UI_Flags__u16 get_ui_element__flags(
        UI_Element *p_ui_element) {
    return p_ui_element
        ->ui_flags;
}

static inline
bool is_ui_element__enabled(UI_Element *p_ui_element) {
    return (bool)(p_ui_element->ui_flags & UI_FLAGS__BIT_IS_ENABLED);
}

static inline
bool is_ui_element__focused(UI_Element *p_ui_element) {
    return (bool)(p_ui_element->ui_flags & UI_FLAGS__BIT_IS_FOCUSED);
}

static inline
bool is_ui_element__non_interactive(UI_Element *p_ui_element) {
    return (bool)(p_ui_element->ui_flags & UI_FLAGS__BIT_IS_NON_INTERACTIVE);
}

static inline
bool is_ui_element__in_needing_update(UI_Element *p_ui_element) {
    return (bool)(p_ui_element->ui_flags & UI_FLAGS__BIT_IS_NEEDING_UPDATE);
}

static inline
bool is_ui_element__being_held(UI_Element *p_ui_element) {
    return (bool)(p_ui_element->ui_flags & UI_FLAGS__BIT_IS_BEING_HELD);
}

static inline
bool is_ui_element__being_dragged(UI_Element *p_ui_element) {
    return (bool)(p_ui_element->ui_flags & UI_FLAGS__BIT_IS_BEING_DRAGGED);
}

static inline
bool is_ui_element__snapped_x_or_y_axis(UI_Element *p_ui_element) {
    return (bool)(p_ui_element->ui_flags & UI_FLAGS__BIT_IS_SNAPPED_X_OR_Y_AXIS);
}

static inline
bool is_ui_element__using_sprite_or__ui_tile_span(
        UI_Element *p_ui_element) {
    return p_ui_element->ui_flags
        & UI_FLAGS__BIT_IS_USING__SPRITE_OR_UI_TILE_SPAN
        ;
}

static inline
bool is_ui_element__using_sprite(
        UI_Element *p_ui_element) {
    return is_ui_element__using_sprite_or__ui_tile_span(
            p_ui_element);
}

static inline
bool is_ui_element__using_ui_tile_span(
        UI_Element *p_ui_element) {
    return !is_ui_element__using_sprite_or__ui_tile_span(
            p_ui_element);
}

static inline
bool does_ui_element_have__parent(
        UI_Element *p_ui_element) {
    return p_ui_element && p_ui_element->p_parent;
}

static inline
bool does_ui_element_have__child(
        UI_Element *p_ui_element) {
    return p_ui_element && p_ui_element->p_child;
}

static inline
bool does_ui_element_have__next(
        UI_Element *p_ui_element) {
    return p_ui_element && p_ui_element->p_next;
}

static inline
void set_ui_element_as__focused(
        UI_Element *p_ui_element) {
    p_ui_element->ui_flags |=
        UI_FLAGS__BIT_IS_FOCUSED;
}

static inline
void set_ui_element_as__NOT_focused(
        UI_Element *p_ui_element) {
    p_ui_element->ui_flags &=
        ~UI_FLAGS__BIT_IS_FOCUSED;
}

static inline
void set_ui_element_as__being_dragged(
        UI_Element *p_ui_element) {
    p_ui_element->ui_flags |=
        UI_FLAGS__BIT_IS_BEING_DRAGGED;
}

static inline
void set_ui_element_as__NOT_being_dragged(
        UI_Element *p_ui_element) {
    p_ui_element->ui_flags &=
        ~UI_FLAGS__BIT_IS_BEING_DRAGGED;
}

static inline
void set_ui_element_as__being_held(
        UI_Element *p_ui_element) {
    p_ui_element->ui_flags |=
        UI_FLAGS__BIT_IS_BEING_HELD;
}

static inline
void set_ui_element_as__dropped(
        UI_Element *p_ui_element) {
    p_ui_element->ui_flags &=
        ~UI_FLAGS__BIT_IS_BEING_HELD
        & ~UI_FLAGS__BIT_IS_BEING_DRAGGED;
}

static inline
void set_ui_element_as__using_sprite(
        UI_Element *p_ui_element) {
    p_ui_element->ui_flags |=
        UI_FLAGS__BIT_IS_USING__SPRITE_OR_UI_TILE_SPAN
        ;
}

static inline
void set_ui_element_as__using_ui_tile_span(
        UI_Element *p_ui_element) {
    p_ui_element->ui_flags &=
        ~UI_FLAGS__BIT_IS_USING__SPRITE_OR_UI_TILE_SPAN
        ;
}

static inline
void set_ui_element_as__snapped_x_axis(
        UI_Element *p_ui_element) {
    p_ui_element->ui_flags |=
        UI_FLAGS__BIT_IS_SNAPPED_X_OR_Y_AXIS;
}

static inline
void set_ui_element_as__snapped_y_axis(
        UI_Element *p_ui_element) {
    p_ui_element->ui_flags &=
        ~UI_FLAGS__BIT_IS_SNAPPED_X_OR_Y_AXIS;
}

static inline
void set_ui_element__snapped_state(
        UI_Element *p_ui_slider,
        bool is_snapped_x_or_y__axis) {
    if (is_snapped_x_or_y__axis) {
        set_ui_element_as__snapped_x_axis(p_ui_slider);
    } else {
        set_ui_element_as__snapped_y_axis(p_ui_slider);
    }
}

static inline
void set_ui_element_as__enabled(
        UI_Element *p_ui_element) {
    p_ui_element->ui_flags |=
        UI_FLAGS__BIT_IS_ENABLED;
}

static inline
void set_ui_element_as__disabled(
        UI_Element *p_ui_element) {
    p_ui_element->ui_flags &=
        ~UI_FLAGS__BIT_IS_ENABLED;
}

///
/// Different from disabled.
/// Disabled will prevent composing.
/// Non-interactive will prevent user interaction
/// but still allow for composing.
///
/// Use this if you want to overlay a bunch of UIs
/// with some composing-only UI (such as a background.)
///
static inline
void set_ui_element_as__non_interactive(
        UI_Element *p_ui_element) {
    p_ui_element->ui_flags |=
        UI_FLAGS__BIT_IS_NON_INTERACTIVE;
}

static inline
void set_ui_element_as__interactive(
        UI_Element *p_ui_element) {
    p_ui_element->ui_flags &=
        ~UI_FLAGS__BIT_IS_NON_INTERACTIVE;
}

static inline
void set_ui_element__dispose_handler(
        UI_Element *p_ui_element,
        m_UI_Dispose m_ui_dispose_handler) {
    p_ui_element->m_ui_dispose_handler =
        m_ui_dispose_handler;
}

static inline
void set_ui_element__clicked_handler(
        UI_Element *p_ui_element,
        m_UI_Clicked m_ui_clicked_handler) {
    p_ui_element->m_ui_clicked_handler =
        m_ui_clicked_handler;
}

static inline
void set_ui_element__dragged_handler(
        UI_Element *p_ui_element,
        m_UI_Dragged m_ui_dragged_handler) {
    p_ui_element->m_ui_dragged_handler =
        m_ui_dragged_handler;
}

static inline
void set_ui_element__dropped_handler(
        UI_Element *p_ui_element,
        m_UI_Dropped m_ui_dropped_handler) {
    p_ui_element->m_ui_dropped_handler =
        m_ui_dropped_handler;
}

static inline
void set_ui_element__receive_drop_handler(
        UI_Element *p_ui_element,
        m_UI_Receive_Drop m_ui_receive_drop_handler) {
    p_ui_element->m_ui_receive_drop_handler =
        m_ui_receive_drop_handler;
}

static inline
void set_ui_element__held_handler(
        UI_Element *p_ui_element,
        m_UI_Held m_ui_held_handler) {
    p_ui_element->m_ui_held_handler =
        m_ui_held_handler;
}

static inline
void set_ui_element__typed_handler(
        UI_Element *p_ui_element,
        m_UI_Typed m_ui_typed_handler) {
    p_ui_element->m_ui_typed_handler =
        m_ui_typed_handler;
}

static inline
void set_ui_element__transformed_handler(
        UI_Element *p_ui_element,
        m_UI_Transformed m_ui_transformed_handler) {
    p_ui_element->m_ui_transformed_handler =
        m_ui_transformed_handler;
}

static inline
void set_ui_element__compose_handler(
        UI_Element *p_ui_element,
        m_UI_Compose m_ui_compose_handler) {
    set_ui_element_as__using_ui_tile_span(
            p_ui_element);
    p_ui_element->m_ui_compose_handler =
        m_ui_compose_handler;
}

static inline
bool does_ui_element_have__dispose_handler(
        UI_Element *p_ui_element) {
    return p_ui_element && p_ui_element->m_ui_dispose_handler;
}

static inline
bool does_ui_element_have__clicked_handler(
        UI_Element *p_ui_element) {
    return p_ui_element && p_ui_element->m_ui_clicked_handler;
}

static inline
bool does_ui_element_have__dragged_handler(
        UI_Element *p_ui_element) {
    return p_ui_element && p_ui_element->m_ui_dragged_handler;
}

static inline
bool does_ui_element_have__dropped_handler(
        UI_Element *p_ui_element) {
    return p_ui_element && p_ui_element->m_ui_dropped_handler;
}

static inline
bool does_ui_element_have__receive_drop_handler(
        UI_Element *p_ui_element) {
    return p_ui_element && p_ui_element->m_ui_receive_drop_handler;
}

static inline
bool does_ui_element_have__held_handler(
        UI_Element *p_ui_element) {
    return p_ui_element && p_ui_element->m_ui_held_handler;
}

static inline
bool does_ui_element_have__typed_handler(
        UI_Element *p_ui_element) {
    return p_ui_element && p_ui_element->m_ui_typed_handler;
}

static inline
bool does_ui_element_have__transformed_handler(
        UI_Element *p_ui_element) {
    return p_ui_element && p_ui_element->m_ui_transformed_handler;
}

static inline
m_UI_Typed get_ui_element__typed_handler(
        UI_Element *p_ui_element) {
    return p_ui_element
        ->m_ui_typed_handler;
}

static inline
m_UI_Transformed get_ui_element__transformed_handler(
        UI_Element *p_ui_element) {
    return p_ui_element
        ->m_ui_transformed_handler;
}

static inline
m_UI_Compose get_ui_element__compose_handler(
        UI_Element *p_ui_element) {
    return p_ui_element
        ->m_ui_compose_handler;
}

static inline
bool does_ui_element_have__compose_handler(
        UI_Element *p_ui_element) {
    return 
        is_ui_element__using_ui_tile_span(p_ui_element)
        && get_ui_element__compose_handler(
            p_ui_element);
}

static inline
const UI_Tile_Span *get_ui_element__p_ui_tile_span(
        UI_Element *p_ui_element) {
    return &p_ui_element
        ->ui_tile_span;
}

#endif
