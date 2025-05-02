#include "collisions/hitbox_aabb.h"
#include "collisions/hitbox_aabb_manager.h"
#include "debug/debug.h"
#include "defines.h"
#include "defines_weak.h"
#include "input/input.h"
#include "platform_defines.h"
#include "rendering/graphics_window.h"
#include "serialization/hashing.h"
#include "serialization/serialization_header.h"
#include "types/implemented/graphics_window_kind.h"
#include "ui/ui_tile_map.h"
#include "world/world.h"
#include <ui/ui_element.h>
#include <ui/ui_manager.h>
#include <vectors.h>
#include <game.h>

bool does_ui_manager_have__focused_ui_element(
        UI_Manager *p_ui_manager) {
    if (p_ui_manager->p_ui_element__focused
            && is_ui_element__focused(
                p_ui_manager->p_ui_element__focused)) {
        return true;
    }
    p_ui_manager->p_ui_element__focused = 0;
    return false;
}

UI_Element *get_p_ui_element__focused_of__ui_manager(
        UI_Manager *p_ui_manager) {
    if (p_ui_manager->p_ui_element__focused
            && !is_ui_element__focused(
                p_ui_manager->p_ui_element__focused)) {
        p_ui_manager->p_ui_element__focused = 0;
    }
    return p_ui_manager->p_ui_element__focused;
}

static inline
void set_p_ui_element_as__focused_in__ui_manager(
        UI_Manager *p_ui_manager,
        UI_Element *p_ui_element) {
    p_ui_manager->p_ui_element__focused =
        p_ui_element;
}

static inline
void drop_ui_element_focus_for__ui_manager(
        UI_Manager *p_ui_manager) {
    if (p_ui_manager->p_ui_element__focused) {
        set_ui_element_as__NOT_focused(
                p_ui_manager
                ->p_ui_element__focused);
    }
    p_ui_manager
        ->p_ui_element__focused = 0;
}

static inline
UI_Element *get_ui_parent_or__child_with__clicked_handler(
        UI_Element *p_ui_parent) {
    if (!p_ui_parent)
        return 0;
    if (does_ui_element_have__clicked_handler(p_ui_parent))
        return p_ui_parent;
    if (!does_ui_element_have__child(p_ui_parent))
        return 0;
    if (does_ui_element_have__clicked_handler(
                get_child_of__ui_element(p_ui_parent)))
        return p_ui_parent->p_child;
    return 0;
}

static inline
UI_Element *get_ui_parent_or__child_with__dragged_handler(
        UI_Element *p_ui_parent) {
    if (!p_ui_parent)
        return 0;
    if (does_ui_element_have__dragged_handler(p_ui_parent))
        return p_ui_parent;
    if (!does_ui_element_have__child(p_ui_parent)) {
        return 0;
    }
    if (does_ui_element_have__dragged_handler(
                get_child_of__ui_element(p_ui_parent)))
        return p_ui_parent->p_child;
    return 0;
}

static inline
UI_Element *get_ui_parent_or__child_with__held_handler(
        UI_Element *p_ui_parent) {
    if (!p_ui_parent)
        return 0;
    if (does_ui_element_have__held_handler(p_ui_parent))
        return p_ui_parent;
    if (!does_ui_element_have__child(p_ui_parent))
        return 0;
    if (does_ui_element_have__held_handler(
                get_child_of__ui_element(p_ui_parent)))
        return p_ui_parent->p_child;
    return 0;
}

static inline
UI_Element *get_ui_parent_or__child_with__receive_drop_handler(
        UI_Element *p_ui_parent) {
    if (!p_ui_parent)
        return 0;
    if (does_ui_element_have__receive_drop_handler(p_ui_parent))
        return p_ui_parent;
    if (!does_ui_element_have__child(p_ui_parent))
        return 0;
    if (does_ui_element_have__receive_drop_handler(
                get_child_of__ui_element(p_ui_parent)))
        return p_ui_parent->p_child;
    return 0;
}

void initialize_ui_manager(
        UI_Manager *p_ui_manager) {
#ifndef NDEBUG
    if (!p_ui_manager) {
        debug_error("initialize_ui_manager, p_ui_manager == 0.");
        return;
    }
#endif
    memset(p_ui_manager,
            0,
            sizeof(UI_Manager));
    initialize_serialization_header__contiguous_array(
            (Serialization_Header *)
            p_ui_manager->ui_elements, 
            MAX_QUANTITY_OF__UI_ELEMENTS, 
            sizeof(UI_Element));
    p_ui_manager->p_ptr_of__ui_element__latest_in_ptr_array =
        p_ui_manager->ptr_array_of__ui_elements;
}

UI_Element *get_p_ui_element_by__uuid_from__ui_manager(
        UI_Manager *p_ui_manager,
        Identifier__u32 uuid__u32) {
    return (UI_Element*)dehash_identitier_u32_in__contigious_array(
            (Serialization_Header *)p_ui_manager->ui_elements, 
            MAX_QUANTITY_OF__UI_ELEMENTS, 
            uuid__u32);
}

UI_Element *get_highest_priority_ui_element_thats__under_this_ui_element(
        UI_Manager *p_ui_manager,
        Hitbox_AABB_Manager *p_hitbox_aabb_manager,
        UI_Element *p_ui_element__above) {
    Vector__3i32 vector_of__element_above__3i32 =
        get_position_3i32_from__p_ui_element(
                p_hitbox_aabb_manager, 
                p_ui_element__above);
    for (Index__u32 index_of__ui_element = 0;
            index_of__ui_element
            < MAX_QUANTITY_OF__UI_ELEMENTS;
            index_of__ui_element++) {
        UI_Element *p_ui_element =
            p_ui_manager->ptr_array_of__ui_elements[index_of__ui_element];
        if (!p_ui_element)
            break;
        if (p_ui_element == p_ui_element__above)
            continue;
        if (!is_ui_element__enabled(p_ui_element)) {
            continue;
        }

        Hitbox_AABB *p_hitbox_aabb =
            get_p_hitbox_aabb_by__uuid_u32_from__hitbox_aabb_manager(
                    p_hitbox_aabb_manager, 
                    GET_UUID_P(p_ui_element));

        if (!p_hitbox_aabb) {
            continue;
        }

        if (is_vector_3i32_inside__hitbox(
                    vector_of__element_above__3i32,
                    p_hitbox_aabb)) {
            return p_ui_element;
        }
    }
    return 0;
}

UI_Element *get_highest_priority_ui_element_thats__under_the_cursor(
        UI_Manager *p_ui_manager,
        Game *p_game) {
    Vector__3i32 cursor_position =
        (is_input__click_released(&p_game->input))
        ? p_game->input.cursor__old__3i32
        : p_game->input.cursor__3i32;
        ;
    for (Index__u32 index_of__ui_element=0;
            index_of__ui_element
            < MAX_QUANTITY_OF__UI_ELEMENTS;
            index_of__ui_element++) {
        UI_Element *p_ui_element =
            p_ui_manager->ptr_array_of__ui_elements[index_of__ui_element];
        if (!p_ui_element)
            break;
        if (!is_ui_element__enabled(p_ui_element)) {
            continue;
        }
        if (is_ui_element__non_interactive(p_ui_element)) {
            continue;
        }

        Hitbox_AABB *p_hitbox_aabb =
            get_p_hitbox_aabb_by__uuid_u32_from__hitbox_aabb_manager(
                    get_p_hitbox_aabb_manager_from__world(
                        get_p_world_from__game(p_game)), 
                    GET_UUID_P(p_ui_element));

        if (!p_hitbox_aabb)
            return 0;

        //TODO: look into why using cursor old.
        if (is_vector_3i32_inside__hitbox(
                    cursor_position,
                    p_hitbox_aabb)) {
            return p_ui_element;
        }
    }
    return 0;
}

UI_Element *detect_focus_in__ui_manager(
        UI_Manager *p_ui_manager, 
        Game *p_game) {
    UI_Element *p_ui_element__focused =
        get_p_ui_element__focused_of__ui_manager(p_ui_manager);
    if (!p_ui_element__focused
            || !is_ui_element__focused(p_ui_element__focused)) {
        p_ui_element__focused =
            get_highest_priority_ui_element_thats__under_the_cursor(
                    p_ui_manager, 
                    p_game);
    }
    if (!p_ui_element__focused)
        return 0;
    set_p_ui_element_as__focused_in__ui_manager(
            p_ui_manager, 
            p_ui_element__focused);
    return p_ui_element__focused;
}

UI_Element *detect_focus__strictly_under_cursor_in__ui_manager(
        UI_Manager *p_ui_manager, 
        Game *p_game) {
    UI_Element *p_ui_element__focused =
        detect_focus_in__ui_manager(
                p_ui_manager, 
                p_game);
    if (!p_ui_element__focused)
        return 0;
    if (!is_vector_3i32_inside__hitbox(
                get_p_input_from__game(p_game)
                ->cursor__3i32, 
                get_p_hitbox_aabb_of__ui_element(
                    get_p_hitbox_aabb_manager_from__game(p_game),
                    p_ui_element__focused))) {
        drop_ui_element_focus_for__ui_manager(p_ui_manager);
        p_ui_element__focused =
            detect_focus_in__ui_manager(
                    p_ui_manager, 
                    p_game);
        if (!p_ui_element__focused)
            return 0;
    }
    return p_ui_element__focused;
}

void update_ui_manager_origin__relative_to(
        Game *p_game,
        UI_Manager *p_ui_manager,
        Vector__3i32 position__old__3i32,
        Vector__3i32 position__new__3i32) {
    for (Index__u32 index_of__ui_element = 0;
            index_of__ui_element
            < MAX_QUANTITY_OF__UI_ELEMENTS;
            index_of__ui_element++) {
        UI_Element *p_ui_element =
            get_p_ui_element_by__index_from__ui_manager(
                    p_ui_manager, index_of__ui_element);

        if (!p_ui_element)
            break;
        if (!is_ui_element__enabled(p_ui_element))
            continue;

        update_ui_element_origin__relative_to(
                p_game,
                p_ui_element,
                position__old__3i32,
                position__new__3i32);
    }
}

void poll_ui_manager__update_for__drag(
        Game *p_game,
        Graphics_Window *p_graphics_window,
        UI_Manager *p_ui_manager) {
    UI_Element *p_ui_element__focused =
        detect_focus_in__ui_manager(
                p_ui_manager, 
                p_game);
    if (!p_ui_element__focused)
        return;
    if (!does_ui_element_have__dragged_handler(
                p_ui_element__focused)) {
        p_ui_element__focused =
            detect_focus__strictly_under_cursor_in__ui_manager(
                    p_ui_manager, 
                    p_game);
        if (!p_ui_element__focused
                || !does_ui_element_have__dragged_handler(
                    p_ui_element__focused)) {
            return;
        }
    }
    if (is_ui_element__being_held(
                p_ui_element__focused)) {
        set_ui_element_as__being_dragged(
                p_ui_element__focused);
    }
    p_ui_element__focused
        ->m_ui_dragged_handler(
                p_ui_manager
                ->p_ui_element__focused,
                p_game,
                p_graphics_window);
}

void poll_ui_manager__update_for__held(
        Game *p_game,
        Graphics_Window *p_graphics_window,
        UI_Manager *p_ui_manager) {
    UI_Element *p_ui_element__focused =
        detect_focus_in__ui_manager(
                p_ui_manager, 
                p_game);
    if (!p_ui_element__focused)
        return;
    if (is_ui_element__being_dragged(
                p_ui_element__focused)) {
        poll_ui_manager__update_for__drag(
                p_game,
                p_graphics_window,
                p_ui_manager);
        return;
    }
    if (!does_ui_element_have__held_handler(
                p_ui_element__focused)) {
        return;
    }
    p_ui_element__focused
        ->m_ui_held_handler(
                p_ui_manager
                ->p_ui_element__focused,
                p_game,
                p_graphics_window);
}

void handle_drop_in__ui_manager(
        Game *p_game,
        Graphics_Window *p_graphics_window,
        UI_Manager *p_ui_manager,
        UI_Element *p_ui_element__focused) {
    if (!p_ui_element__focused)
        return;
    set_ui_element_as__dropped(
            p_ui_element__focused);
    if (!does_ui_element_have__dropped_handler(
                p_ui_element__focused)) {
        drop_ui_element_focus_for__ui_manager(p_ui_manager);
        return;
    }

    UI_Element *p_ui_element__receiving_drop =
        get_highest_priority_ui_element_thats__under_this_ui_element(
            p_ui_manager,
            get_p_hitbox_aabb_manager_from__world(
                get_p_world_from__game(p_game)),
            p_ui_manager->p_ui_element__focused);
    p_ui_element__receiving_drop =
        get_ui_parent_or__child_with__receive_drop_handler(
                p_ui_element__receiving_drop);
    if (p_ui_element__receiving_drop) {
        p_ui_element__receiving_drop
            ->m_ui_receive_drop_handler(
                    p_ui_element__receiving_drop,
                    p_ui_manager->p_ui_element__focused,
                    p_game,
                    p_graphics_window);
    }

    p_ui_element__focused
        ->m_ui_dropped_handler(
                p_ui_manager
                ->p_ui_element__focused,
                p_game,
                p_graphics_window);
}

void poll_ui_manager__update_for__clicked_and_dropped(
        UI_Manager *p_ui_manager,
        Game *p_game,
        Graphics_Window *p_graphics_window) {
    UI_Element *p_ui_element__focused =
        detect_focus__strictly_under_cursor_in__ui_manager(
                p_ui_manager, 
                p_game);
    if (!p_ui_element__focused)
        return;
    if (is_ui_element__being_dragged(
                p_ui_element__focused)) {
        handle_drop_in__ui_manager(
                p_game, 
                p_graphics_window, 
                p_ui_manager, 
                p_ui_element__focused);
        return;
    }
    p_ui_element__focused =
        get_ui_parent_or__child_with__clicked_handler(
                p_ui_element__focused);
    if (!p_ui_element__focused)
        return;
    p_ui_element__focused
        ->m_ui_clicked_handler(
            p_ui_element__focused,
            p_game,
            p_graphics_window);
}

void poll_ui_manager__update_for__input_writing(
        UI_Manager *p_ui_manager,
        Game *p_game,
        Graphics_Window *p_graphics_window) {
    bool has_ui_element__focus =
        does_ui_manager_have__focused_ui_element(p_ui_manager);

    UI_Element *p_ui_element__focused =
        get_p_ui_element__focused_of__ui_manager(p_ui_manager);

    char symbol = poll_input_for__writing(
            get_p_input_from__game(p_game));

    if (!p_ui_element__focused
            || !does_ui_element_have__typed_handler(
                p_ui_element__focused)) {
        set_input_mode_of__input(
                get_p_input_from__game(p_game), 
                INPUT_MODE__NORMAL);
        return;
    }

    if (symbol) {
        get_ui_element__typed_handler(
                p_ui_element__focused)(
                    p_ui_element__focused,
                    p_game,
                    p_graphics_window,
                    symbol);
    }

    if (!is_ui_element__focused(p_ui_element__focused)) {
        set_input_mode_of__input(
                get_p_input_from__game(p_game), 
                INPUT_MODE__NORMAL);
    }
}

void poll_ui_manager__update(
        UI_Manager *p_ui_manager,
        Game *p_game,
        Graphics_Window *p_graphics_window) {
    Input *p_input = &p_game->input;

    switch (get_input_mode_of__input(
                get_p_input_from__game(p_game))) {
        default:
        case INPUT_MODE__NORMAL:
            break;
        case INPUT_MODE__WRITING:
            poll_ui_manager__update_for__input_writing(
                    p_ui_manager, 
                    p_game, 
                    p_graphics_window);
            break;
    }

    if (is_input__click_released(p_input)) {
        poll_ui_manager__update_for__clicked_and_dropped(
                p_ui_manager, 
                p_game,
                p_graphics_window);
        return;
    }

    if (is_input__click_held(p_input)) {
        poll_ui_manager__update_for__held(
                p_game,
                p_graphics_window,
                p_ui_manager);
        return;
    }
    if (is_input__click_dragged(p_input)) {
        poll_ui_manager__update_for__drag(
                p_game,
                p_graphics_window,
                p_ui_manager);
        return;
    }
}

UI_Element *allocate_ui_element_from__ui_manager(
        UI_Manager *p_ui_manager) {
    if (p_ui_manager->p_ptr_of__ui_element__latest_in_ptr_array
            - p_ui_manager->ptr_array_of__ui_elements
            >= MAX_QUANTITY_OF__UI_ELEMENTS) {
        debug_error("allocate_ui_element_from__ui_manager, failed to allocate ui_element (full).");
    }

    UI_Element *p_ui_element =
        (UI_Element*)allocate_serialization_header_with__uuid_branding(
                (Serialization_Header *)p_ui_manager->ui_elements, 
                MAX_QUANTITY_OF__UI_ELEMENTS, 
                &p_ui_manager->randomizer, 
                GET_UUID_BRANDING(
                    Lavender_Type__UI_Element, 
                    0b111111 & p_ui_manager->ui_manager__allocation_index));

#ifndef NDEBUG
    if (!p_ui_element) {
        debug_error("allocate_ui_element_from__ui_manager, failed to allocate ui_element.");
        return 0;
    }
#endif

    *p_ui_manager->p_ptr_of__ui_element__latest_in_ptr_array = p_ui_element;
    p_ui_manager->p_ptr_of__ui_element__latest_in_ptr_array++;

    initialize_ui_element(
            p_ui_element, 
            0, 
            0, 
            0, 
            UI_Element_Kind__None, 
            UI_FLAGS__NONE);

    set_ui_element_as__enabled(p_ui_element);

    return p_ui_element;
}

UI_Element *allocate_ui_element_from__ui_manager_as__child(
        Game *p_game,
        Graphics_Window *p_graphics_window,
        UI_Manager *p_ui_manager,
        UI_Element *p_parent) {
    UI_Element *p_child =
        allocate_ui_element_from__ui_manager(p_ui_manager);
    set_ui_element_as__the_parent_of__this_ui_element(
            p_ui_manager,
            p_parent, 
            p_child);
    set_position_3i32_of__ui_element(
            p_game,
            p_graphics_window,
            p_child, 
            get_position_3i32_from__p_ui_element(
                get_p_hitbox_aabb_manager_from__game(
                    p_game),
                p_parent));
    return p_child;
}

void allocate_many_ui_elements_from__ui_manager(
        UI_Manager *p_ui_manager,
        UI_Element **p_ptr_buffer,
        Quantity__u16 quantity_of__ui_elements_in__ptr_buffer
        ) {
    if (quantity_of__ui_elements_in__ptr_buffer
            > MAX_QUANTITY_OF__UI_ELEMENTS) {
        return;
    }
    for (Quantity__u8 buffer_index=0;
            buffer_index<quantity_of__ui_elements_in__ptr_buffer;
            buffer_index++) {
        p_ptr_buffer[buffer_index] =
            allocate_ui_element_from__ui_manager(p_ui_manager);
    }
}

UI_Element *allocate_many_ui_elements_from__ui_manager_in__succession(
        UI_Manager *p_ui_manager,
        Quantity__u16 quantity_of__ui_elements_to__allocate
        ) {
    if (quantity_of__ui_elements_to__allocate == 0)
        return 0;
    UI_Element *p_head = allocate_ui_element_from__ui_manager(
            p_ui_manager);
    UI_Element *p_current = p_head;

    for (Quantity__u8 quantity_of__ui_elements__allocated = 1;
            quantity_of__ui_elements__allocated < 
                quantity_of__ui_elements_to__allocate;
            quantity_of__ui_elements__allocated++) {
        p_current->p_next =
            allocate_ui_element_from__ui_manager(p_ui_manager);
        p_current = p_current->p_next;
    }
    return p_head;
}

UI_Element **get_p_ptr_ui_element_from__ptr_array_in__ui_manager(
        UI_Manager *p_ui_manager,
        UI_Element *p_ui_element) {
    for (Index__u16 index_of__ptr = 0;
            index_of__ptr < MAX_QUANTITY_OF__UI_ELEMENTS;
            index_of__ptr++) {
        UI_Element **p_ptr_ui_element =
            &p_ui_manager->ptr_array_of__ui_elements[index_of__ptr];
        if (!*p_ptr_ui_element)
            return 0;
        if (*p_ptr_ui_element == p_ui_element)
            return p_ptr_ui_element;
    }
    return 0;
}

UI_Element *allocate_many_ui_elements_from__ui_manager_as__recursive_children(
        UI_Manager *p_ui_manager,
        Quantity__u8 quantity_of__ui_elements_to__allocate
        ) {
    if (quantity_of__ui_elements_to__allocate == 0)
        return 0;
    UI_Element *p_parent = allocate_ui_element_from__ui_manager(
            p_ui_manager);
    UI_Element *p_current = p_parent;

    for (Quantity__u8 quantity_of__ui_elements__allocated = 1;
            quantity_of__ui_elements__allocated < 
                quantity_of__ui_elements_to__allocate;
            quantity_of__ui_elements__allocated++) {
        p_current->p_child =
            allocate_ui_element_from__ui_manager(p_ui_manager);
        p_current = p_current->p_child;
    }
    return p_parent;
}

void release__ui_element_from__ui_manager(
        Game *p_game,
        Graphics_Window *p_graphics_window,
        UI_Manager *p_ui_manager,
        UI_Element *p_ui_element) {
#ifndef NDEBUG
    if (!p_ui_manager) {
        debug_error("release__ui_element_from__ui_manager, p_ui_manager == 0.");
        return;
    }
    if (!p_ui_element) {
        debug_error("release__ui_element_from__ui_manager, p_ui_element == 0.");
        return;
    }
    if (!p_game) {
        debug_error("release__ui_element_from__ui_manager, p_game == 0.");
        return;
    }
    if (p_ui_element - p_ui_manager->ui_elements
            >= MAX_QUANTITY_OF__UI_ELEMENTS) {
        debug_error("release__ui_element_from__ui_manager, p_ui_element is not allocated with this manager.");
        return;
    }
#endif
    if (p_ui_element->m_ui_dispose_handler
            && !IS_DEALLOCATED_P(p_ui_element)) {
        // the second clause of the if statement
        // is in the case of a p_next->m_ui_dispose_handler
        // invocation chain.
        p_ui_element->m_ui_dispose_handler(
                p_ui_element,
                p_game,
                p_graphics_window);
    }

    set_ui_element_as__disabled(p_ui_element);

    DEALLOCATE_P(p_ui_element);
    UI_Element **p_ptr_ui_element =
        get_p_ptr_ui_element_from__ptr_array_in__ui_manager(
                p_ui_manager, 
                p_ui_element);

#ifndef NDEBUG
    if (!p_ptr_ui_element) {
        debug_error("release__ui_element_from__ui_manager, intrinsic violated.");
        return;
    }
#endif

    p_ui_manager->p_ptr_of__ui_element__latest_in_ptr_array--;
    *p_ptr_ui_element =
        *p_ui_manager->p_ptr_of__ui_element__latest_in_ptr_array;
    *p_ui_manager->p_ptr_of__ui_element__latest_in_ptr_array = 0;
}

void release_all__ui_elements_from__ui_manager(
        Game *p_game,
        Graphics_Window *p_graphics_window,
        UI_Manager *p_ui_manager) {
    while(!is_ui_manager__empty(p_ui_manager)) {
        release__ui_element_from__ui_manager(
                p_game, 
                p_graphics_window,
                p_ui_manager,
                get_p_ui_element_by__index_from__ui_manager(
                    p_ui_manager, 
                    0));
    }
}

Quantity__u16 get_ui_element__priority(
        UI_Manager *p_ui_manager,
        UI_Element *p_ui_element) {
    UI_Element **p_ptr_ui_element =
        get_p_ptr_ui_element_from__ptr_array_in__ui_manager(
                p_ui_manager, 
                p_ui_element);
    return p_ptr_ui_element
        - p_ui_manager->ptr_array_of__ui_elements;
}

void swap_priority_of__ui_elenents_within__ui_manager(
        UI_Manager *p_ui_manager,
        UI_Element *p_ui_element__this,
        UI_Element *p_ui_element__other) {
    UI_Element **p_ptr_ui_element__this = 
        get_p_ptr_ui_element_from__ptr_array_in__ui_manager(
                p_ui_manager, p_ui_element__this);
    UI_Element **p_ptr_ui_element__other =
        get_p_ptr_ui_element_from__ptr_array_in__ui_manager(
                p_ui_manager, p_ui_element__other);

    *p_ptr_ui_element__this =
        p_ui_element__other;
    *p_ptr_ui_element__other =
        p_ui_element__this;
}

void set_ui_element_priority_higher_than__this_ui_element_in__ui_manager(
        UI_Manager *p_ui_manager,
        UI_Element *p_ui_element__higher_priority,
        UI_Element *p_ui_element__lower_priortiy) {
    Quantity__u8 priority_of__former =
        get_ui_element__priority(
                p_ui_manager, 
                p_ui_element__higher_priority);
    Quantity__u8 priority_of__later =
        get_ui_element__priority(
                p_ui_manager, 
                p_ui_element__lower_priortiy);
    if (priority_of__former <= priority_of__later)
        return;
    swap_priority_of__ui_elenents_within__ui_manager(
            p_ui_manager, 
            p_ui_element__higher_priority, 
            p_ui_element__lower_priortiy);
}

void set_ui_element_as__the_parent_of__this_ui_element(
        UI_Manager *p_ui_manager,
        UI_Element *p_parent,
        UI_Element *p_child) {
    if (!p_parent) {
        debug_abort("set_ui_element_as__the_parent_of__this_ui_element, p_parent is null.");
        return;
    }

    if (p_parent == p_child) {
        debug_warning("set_ui_element_as__the_parent_of__this_ui_element, p_parent == p_child.");
        p_parent->p_parent = 0;
        return;
    }

    if (p_parent->p_child)
        p_parent->p_child->p_parent = 0;
    p_parent->p_child =
        p_child;


    if (p_child) {
        if (p_child->p_parent)
            p_child->p_parent->p_child = 0;
        p_child->p_parent =
            p_parent;
        set_ui_element_priority_higher_than__this_ui_element_in__ui_manager(
                p_ui_manager, 
                p_parent, 
                p_child);
    }
}

void swap_ui_element__children(
        UI_Manager *p_ui_manager,
        UI_Element *p_parent__one,
        UI_Element *p_parent__two) {

    UI_Element *p_child__one =
        (p_parent__one)
        ? p_parent__one->p_child
        : 0
        ;
    UI_Element *p_child__two =
        (p_parent__two)
        ? p_parent__two->p_child
        : 0
        ;

    if (p_parent__one) {
        set_ui_element_as__the_parent_of__this_ui_element(
                p_ui_manager, 
                p_parent__one, 
                p_child__two);
    }
    if (p_parent__two) {
        set_ui_element_as__the_parent_of__this_ui_element(
                p_ui_manager, 
                p_parent__two, 
                p_child__one);
    }
}

void foreach_ui_element_in__ui_manager(
        UI_Manager *p_ui_manager,
        Game *p_game,
        Graphics_Window *p_gfx_window,
        f_Foreach_UI_Element f_foreach_ui_element) {
    for (Index__u32 index_of__ui_element = 0;
            index_of__ui_element
            < MAX_QUANTITY_OF__UI_ELEMENTS;
            index_of__ui_element++) {
        UI_Element *p_ui_element =
            get_p_ui_element_by__index_from__ui_manager(
                    p_ui_manager, 
                    index_of__ui_element);

        if (!IS_DEALLOCATED_P(p_ui_element)) {
            f_foreach_ui_element(
                    p_ui_manager,
                    p_game,
                    p_gfx_window,
                    p_ui_element);
        }
    }
}

static void f_compose_ui_element_callback__ui_manager(
        UI_Manager *p_ui_manager,
        Game *p_game,
        Graphics_Window *p_gfx_window,
        UI_Element *p_ui_element) {
    if (!p_ui_element
            || !is_ui_element__enabled(p_ui_element)) {
        return;
    }
    if (!does_ui_element_have__compose_handler(
                p_ui_element)) {
        return;
    }

    p_ui_element->m_ui_compose_handler(
            p_ui_element,
            p_game,
            p_gfx_window);
}

void compose_all_ui_elements_in__ui_manager(
        UI_Manager *p_ui_manager,
        Game *p_game,
        Graphics_Window *p_gfx_window) {
#ifndef NDEBUG
    if (!p_ui_manager) {
        debug_error("compose_all_ui_elements_in__ui_manager, p_ui_manager == 0.");
        return;
    }
    if (!p_game) {
        debug_error("compose_all_ui_elements_in__ui_manager, p_game == 0.");
        return;
    }
    if (!p_gfx_window) {
        debug_error("compose_all_ui_elements_in__ui_manager, p_gfx_window == 0.");
        return;
    }
#endif
    foreach_ui_element_in__ui_manager(
            p_ui_manager, 
            p_game,
            p_gfx_window,
            f_compose_ui_element_callback__ui_manager);
}
