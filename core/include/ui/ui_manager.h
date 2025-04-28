#ifndef UI_MANAGER_H
#define UI_MANAGER_H

#include "defines_weak.h"
#include "ui/ui_element.h"
#include <defines.h>

void initialize_ui_manager(UI_Manager *p_ui_manager);

void poll_ui_manager__update(
        UI_Manager *p_ui_manager,
        Game *p_game,
        Graphics_Window *p_graphics_window);

void set_ui_element_priority_higher_than__this_ui_element_in__ui_manager(
        UI_Manager *p_ui_manager,
        UI_Element *p_ui_element__higher_priority,
        UI_Element *p_ui_element__lower_priortiy);

///
/// Establish a form of ownership via p_parent.
///
void set_ui_element_as__the_parent_of__this_ui_element(
        UI_Manager *p_ui_manager,
        UI_Element *p_parent,
        UI_Element *p_child);

void swap_ui_element__children(
        UI_Manager *p_ui_manager,
        UI_Element *p_parent__one,
        UI_Element *p_parent__two);

UI_Element *allocate_ui_element_from__ui_manager(
        UI_Manager *p_ui_manager);

UI_Element *allocate_ui_element_from__ui_manager_as__child(
        Game *p_game,
        Graphics_Window *p_graphics_window,
        UI_Manager *p_ui_manager,
        UI_Element *p_parent);

void allocate_many_ui_elements_from__ui_manager(
        UI_Manager *p_ui_manager,
        UI_Element **p_ptr_buffer,
        Quantity__u16 quantity_of__ui_elements_in__ptr_buffer
        );

UI_Element *allocate_many_ui_elements_from__ui_manager_in__succession(
        UI_Manager *p_ui_manager,
        Quantity__u16 quantity_of__ui_elements_to__allocate
        );

UI_Element *allocate_many_ui_elements_from__ui_manager_as__recursive_children(
        UI_Manager *p_ui_manager,
        Quantity__u8 quantity_of__ui_elements_to__allocate
        );

void release__ui_element_from__ui_manager(
        Game *p_game,
        Graphics_Window *p_graphics_window,
        UI_Manager *p_ui_manager,
        UI_Element *p_ui_element);

void release_all__ui_elements_from__ui_manager(
        Game *p_game,
        Graphics_Window *p_graphics_window,
        UI_Manager *p_ui_manager);

UI_Element *get_p_ui_element_by__uuid_from__ui_manager(
        UI_Manager *p_ui_manager,
        Identifier__u32 uuid__u32);

///
/// You will want to call this whenever you're implementing a
/// parent/child UI_Element relationship. OR if one UI is
/// LOGICALLY layered about the other.
///
/// TODO: add helper to change visual layering.
///
void swap_priority_of__ui_elenents_within__ui_manager(
        UI_Manager *p_ui_manager,
        UI_Element *p_ui_element__this,
        UI_Element *p_ui_element__other);

void set_ui_element_priority_higher_than__this_ui_element_in__ui_manager(
        UI_Manager *p_ui_manager,
        UI_Element *p_ui_element__higher_priority,
        UI_Element *p_ui_element__lower_priortiy);

void foreach_ui_element_in__ui_manager(
        UI_Manager *p_ui_manager,
        Game *p_game,
        Graphics_Window *p_gfx_window,
        f_Foreach_UI_Element f_foreach_ui_element);

void render_all_ui_elements_in__ui_manager(
        UI_Manager *p_ui_manager,
        Game *p_game,
        Graphics_Window *p_gfx_window);

void compose_all_ui_elements_in__ui_manager(
        UI_Manager *p_ui_manager,
        Game *p_game,
        Graphics_Window *p_gfx_window);

static inline
bool is_ui_manager__empty(
        UI_Manager *p_ui_manager) {
    return !p_ui_manager->ptr_array_of__ui_elements[0];
}

///
/// NOTE: this should only be used for iterating across ALL UI_Elements BLINDLY.
/// As this function is NOT a reliable means of referencing any specific UI_Element
/// over time. IE, elements in the structure may move around.
///
/// If you need to acquire the same UI_Element, get that UI_Element's UUID and
/// use the corresponding uuid getter.
///
static inline
UI_Element *get_p_ui_element_by__index_from__ui_manager(
        UI_Manager *p_ui_manager,
        Index__u16 index_of__ui_element) {
#ifndef NDEBUG
    if (index_of__ui_element >=
            MAX_QUANTITY_OF__UI_ELEMENTS) {
        debug_abort("get_p_ui_element_by__index_from__ui_manager, index of out bounds: %d", index_of__ui_element);
        return 0;
    }
#endif
    return p_ui_manager->ptr_array_of__ui_elements[index_of__ui_element];
}

static inline
UI_Element *allocate_ui_element_from__ui_manager_in__succession(
        UI_Manager *p_ui_manager,
        UI_Element *p_predecessor) {
    p_predecessor->p_next =
        allocate_ui_element_from__ui_manager(p_ui_manager);
    return p_predecessor->p_next;
}

#endif
