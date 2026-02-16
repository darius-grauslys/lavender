#ifndef GRAPHICS_WINDOW_MANAGER_H
#define GRAPHICS_WINDOW_MANAGER_H

#include "defines.h"
#include "defines_weak.h"
#include "serialization/hashing.h"
#include "serialization/identifiers.h"

void initialize_graphics_window_manager(
        Graphics_Window_Manager *p_graphics_window_manager);

Graphics_Window *allocate_graphics_window_with__uuid_from__graphics_window_manager(
        Gfx_Context *p_gfx_context,
        Graphics_Window_Manager *p_graphics_window_manager,
        Identifier__u32 uuid__u32,
        Texture_Flags texture_flags_for__gfx_window);

void set_graphics_window_as__parent_to__this_graphics_window(
        Graphics_Window_Manager *p_graphics_window_manager,
        Graphics_Window *p_graphics_window__parent,
        Graphics_Window *p_graphics_window__child);

void release_graphics_window_from__graphics_window_manager(
        Game *p_game,
        Graphics_Window *p_graphics_window);

Graphics_Window *get_p_graphics_window_by__uuid_from__graphics_window_manager(
        Graphics_Window_Manager *p_graphics_window_manager,
        Identifier__u32 uuid__u32);

Quantity__u8 get_graphics_windows_from__graphics_window_manager(
        Graphics_Window_Manager *p_graphics_window_manager,
        Graphics_Window **p_ptr_array__graphics_windows,
        Quantity__u8 max_quantity_of__windows,
        Graphics_Window_Kind the_kind_of__graphics_window);

bool is_graphics_window_a__descendant_of__this_graphics_window(
        Graphics_Window_Manager *p_graphics_window_manager,
        Graphics_Window *p_graphics_window__child,
        Graphics_Window *p_graphics_window__potential_ancestor);

void compose_graphic_windows_in__graphics_window_manager(
        Game *p_game);

void render_graphic_windows_in__graphics_window_manager(
        Game *p_game);

Quantity__u32 get_index_in_ptr_array_of__gfx_window_and__quantity_of__descendants(
        Graphics_Window_Manager *p_graphics_window_manager,
        Graphics_Window *p_graphics_window,
        Quantity__u32 *p_quantity_of__children__u32);

///
/// If there are more windows that pointer slots in the ptr buffer
/// the quantity_of__overflowed_windows will be set to a non-zero number.
///
/// Returns False only of the windows couldn't be allocated.
///
bool allocate_or_get__platform_provided_graphics_windows(
        Gfx_Context *p_gfx_context,
        Graphics_Window_Manager *p_graphics_window_manager,
        Graphics_Window **ptr_array_of__graphics_windows,
        Quantity__u32 quantity_of__ptrs_in_buffer__u32,
        Quantity__u32 *p_quantity_of__overflowed_windows__u32,
        Index__u32 offset_of__graphics_window);

bool setup_platform_provided_graphics_windows(
        Gfx_Context *p_gfx_context);

///
/// This call will auto-increment the itterator.
///
Graphics_Window *itterate_platform_graphics_windows(
        Gfx_Context *p_gfx_context,
        Index__u32 *p_index_itterator__u32);

Graphics_Window *get_default_platform_graphics_window(
        Gfx_Context *p_gfx_context);

Graphics_Window *get_graphics_window__p_parent(
        Graphics_Window_Manager *p_graphics_window_manager,
        Graphics_Window *p_graphics_window);

Graphics_Window *get_graphics_window__p_root_parent(
        Graphics_Window_Manager *p_graphics_window_manager,
        Graphics_Window *p_graphics_window,
        Quantity__u32 *p_OUT_depth_to_search);

static inline
bool is_graphics_window_a__parent(
        Graphics_Window_Manager *p_graphics_window_manager,
        Graphics_Window *p_graphics_window) {
    Quantity__u32 quantity_of__chilren = 0;
    (void)get_index_in_ptr_array_of__gfx_window_and__quantity_of__descendants(
            p_graphics_window_manager, 
            p_graphics_window, 
            &quantity_of__chilren);
    return quantity_of__chilren;
}

static inline
bool is_graphics_window_with__parent(
        Graphics_Window *p_graphics_window) {
    return p_graphics_window 
        && !is_identifier_u32__invalid(p_graphics_window->graphics_window__parent__uuid);
}

static inline
Graphics_Window *allocate_graphics_window_from__graphics_window_manager(
        Gfx_Context *p_gfx_context,
        Graphics_Window_Manager *p_graphics_window_manager,
        Texture_Flags texture_flags_for__gfx_window) {
    return allocate_graphics_window_with__uuid_from__graphics_window_manager(
            p_gfx_context,
            p_graphics_window_manager,
            get_next_available__random_uuid_in__contiguous_array(
                (Serialization_Header*)p_graphics_window_manager
                    ->graphics_windows, 
                MAX_QUANTITY_OF__GRAPHICS_WINDOWS, 
                &p_graphics_window_manager->randomizer),
            texture_flags_for__gfx_window);
}

static inline
Graphics_Window *get_p_graphics_window_by__index_in_ptr_array_from__manager(
        Graphics_Window_Manager *p_graphics_window_manager,
        Index__u32 index_of__graphics_window) {
    return p_graphics_window_manager
        ->ptr_array_of__sorted_graphic_windows[index_of__graphics_window];
}

#endif
