#include "rendering/graphics_window_manager.h"
#include "defines.h"
#include "defines_weak.h"
#include "game.h"
#include "platform.h"
#include "rendering/gfx_context.h"
#include "rendering/graphics_window.h"
#include "rendering/sprite_context.h"
#include "rendering/sprite_manager.h"
#include "rendering/texture.h"
#include "serialization/hashing.h"
#include "serialization/identifiers.h"
#include "serialization/serialization_header.h"
#include "sort/heap_sort__opaque.h"
#include "ui/ui_context.h"
#include "ui/ui_manager.h"
#include "ui/ui_tile_map.h"
#include "ui/ui_tile_map_manager.h"
#include "util/bitmap/bitmap.h"
#include "world/camera.h"
#include "world/world.h"

void sort_graphic_windows_in__graphic_window_manager(
        Graphics_Window_Manager *p_graphics_window_manager);

static inline
Graphics_Window *get_p_graphics_window_by__index_from__manager(
        Graphics_Window_Manager *p_graphics_window_manager,
        Index__u32 index_of__graphics_window) {
    if (MAX_QUANTITY_OF__GRAPHICS_WINDOWS <=
            index_of__graphics_window) {
        debug_error("get_p_graphics_window_by__index_from__manager, index out of range: %d/%d",
                index_of__graphics_window,
                MAX_QUANTITY_OF__GRAPHICS_WINDOWS);
        return 0;
    }
    return &p_graphics_window_manager->graphics_windows[
        index_of__graphics_window];
}

static inline
Graphics_Window *get_p_graphics_window_by__sorted_index_from__manager(
        Graphics_Window_Manager *p_graphics_window_manager,
        Index__u32 index_of__graphics_window) {
    if (MAX_QUANTITY_OF__GRAPHICS_WINDOWS <=
            index_of__graphics_window) {
        debug_error("get_p_graphics_window_by__index_from__manager, index out of range: %d/%d",
                index_of__graphics_window,
                MAX_QUANTITY_OF__GRAPHICS_WINDOWS);
        return 0;
    }
    return p_graphics_window_manager->ptr_array_of__sorted_graphic_windows[
        index_of__graphics_window];
}

static inline
Graphics_Window **get_next_available_p_ptr_graphics_window_from__sorted_list(
        Graphics_Window_Manager *p_graphics_window_manager) {
    for (Index__u32 index_of__p_ptr_graphics_window = 0;
            index_of__p_ptr_graphics_window
            < MAX_QUANTITY_OF__GRAPHICS_WINDOWS;
            index_of__p_ptr_graphics_window++) {
        if (p_graphics_window_manager->ptr_array_of__sorted_graphic_windows[
                index_of__p_ptr_graphics_window] == 0) {
            return &p_graphics_window_manager
                ->ptr_array_of__sorted_graphic_windows[
                index_of__p_ptr_graphics_window];
        }
    }
    debug_error("get_next_available_p_ptr_graphics_window_from__sorted_list, failed to find free slot.");
    return 0;
}

static inline
Graphics_Window **get_sorted_slot_of__graphics_window_from__sorted_list(
        Graphics_Window_Manager *p_graphics_window_manager,
        Graphics_Window *p_graphics_window) {
    for (Index__u32 index_of__p_ptr_graphics_window = 0;
            index_of__p_ptr_graphics_window
            < MAX_QUANTITY_OF__GRAPHICS_WINDOWS;
            index_of__p_ptr_graphics_window++) {
        if (p_graphics_window_manager->ptr_array_of__sorted_graphic_windows[
                index_of__p_ptr_graphics_window]
                == p_graphics_window) {
            return &p_graphics_window_manager
                ->ptr_array_of__sorted_graphic_windows[
                index_of__p_ptr_graphics_window];
        }
    }
    debug_error("get_sorted_slot_of__graphics_window_from__sorted_list, failed to find graphics window slot in sorted list.");
    return 0;
}

void initialize_graphics_window_manager(
        Graphics_Window_Manager *p_graphics_window_manager) {
    initialize_serialization_header__contiguous_array(
            (Serialization_Header *)
                p_graphics_window_manager->graphics_windows, 
                MAX_QUANTITY_OF__GRAPHICS_WINDOWS, 
                sizeof(Graphics_Window));
    initialize_repeatable_psuedo_random(
            &p_graphics_window_manager->randomizer,
            (u32)(u64)p_graphics_window_manager);
}

Graphics_Window *allocate_graphics_window_with__uuid_from__graphics_window_manager(
        Gfx_Context *p_gfx_context,
        Graphics_Window_Manager *p_graphics_window_manager,
        Identifier__u32 uuid__u32,
        Texture_Flags texture_flags_for__gfx_window) {
    Graphics_Window *p_graphics_window__available = 
        (Graphics_Window*)get_next_available__allocation_in__contiguous_array(
                (Serialization_Header *)p_graphics_window_manager
                    ->graphics_windows, 
                MAX_QUANTITY_OF__GRAPHICS_WINDOWS, 
                uuid__u32);

    if (!p_graphics_window__available) {
        debug_error("allocate_graphics_window_with__graphics_window_manager, graphics window limit reached.");
        return 0;
    }

    Graphics_Window **p_ptr_sorted_graphics_window_slot =
        get_next_available_p_ptr_graphics_window_from__sorted_list(
                p_graphics_window_manager);

    if (!p_ptr_sorted_graphics_window_slot) {
        debug_abort("allocate_graphics_window_with__uuid_from__graphics_window_manager, could not find free sorted entry.");
        return 0;
    }

    PLATFORM_Graphics_Window *p_PLATFORM_gfx_window =
        PLATFORM_allocate_gfx_window(
                p_gfx_context, 
                texture_flags_for__gfx_window);

    if (!p_PLATFORM_gfx_window) {
        debug_error("allocate_graphics_window_with__graphics_window_manager, failed to allocate PLATFORM_gfx_window.");
        DEALLOCATE_P(p_graphics_window__available);
        return 0;
    }

    initialize_graphics_window(
            p_graphics_window__available);
    ALLOCATE_P(
            p_graphics_window__available, 
            uuid__u32);

    p_graphics_window__available
        ->width_of__graphics_window__u32 =
        get_length_of__texture_flag__width(texture_flags_for__gfx_window);
    p_graphics_window__available
        ->height_of__graphics_window__u32 =
        get_length_of__texture_flag__height(texture_flags_for__gfx_window);

    p_graphics_window__available
        ->p_PLATFORM_gfx_window = 
        p_PLATFORM_gfx_window;
    
    p_graphics_window__available
        ->graphics_window__flags =
        texture_flags_for__gfx_window;

    set_graphics_window_as__enabled(
            p_graphics_window__available);

    *p_ptr_sorted_graphics_window_slot =
        p_graphics_window__available;

    sort_graphic_windows_in__graphic_window_manager(
            p_graphics_window_manager);

    return p_graphics_window__available;
}

static inline
bool is_graphics_window_kind_NOT_in__bounds(
        Graphics_Window_Kind the_kind_of__graphics_window) {
    bool failure = the_kind_of__graphics_window
            >= Graphics_Window_Kind__Unknown;
    if (failure) {
        debug_error("is_graphics_window_kind_NOT_in__bounds, the_kind_of__graphics_window_to__allocate out of range: %d/%d.",
                the_kind_of__graphics_window,
                Graphics_Window_Kind__Unknown);
    }
    return failure;
}

static inline
bool is_graphics_window_NOT_from__this_graphics_window_manager(
        Graphics_Window_Manager *p_graphics_window_manager,
        Graphics_Window *p_graphics_window) {
    Index__u32 index = p_graphics_window - p_graphics_window_manager->graphics_windows;

    bool failure = index >= MAX_QUANTITY_OF__GRAPHICS_WINDOWS;

    if (failure) {
        debug_error("is_graphics_window_NOT_from__this_graphics_window_manager, provided graphics_window is not from this graphics_window_manager.");
    }

    return failure;
}

void set_graphics_window_as__parent_to__this_graphics_window(
        Graphics_Window_Manager *p_graphics_window_manager,
        Graphics_Window *p_graphics_window__parent,
        Graphics_Window *p_graphics_window__child) {
    if (is_graphics_window_NOT_from__this_graphics_window_manager(
                p_graphics_window_manager, 
                p_graphics_window__child)) {
        debug_error("set_graphics_window_as__parent_to__this_graphics_window, p_graphics_window__child is not from this graphics_window_manager.");
        return;
    }
    if (is_graphics_window_NOT_from__this_graphics_window_manager(
                p_graphics_window_manager, 
                p_graphics_window__parent)) {
        debug_error("set_graphics_window_as__parent_to__this_graphics_window, p_graphics_window__parent is not from this graphics_window_manager.");
        return;
    }

    if (p_graphics_window__parent == p_graphics_window__child) {
        debug_error("set_graphics_window_as__parent_to__this_graphics_window, p_graphics_window__child cannot become it's own parent.");
        return; 
    }

    for (Index__u32 index_of__graphics_window = 0;
            index_of__graphics_window
            < MAX_QUANTITY_OF__GRAPHICS_WINDOWS;
            index_of__graphics_window++) {
        Graphics_Window *p_graphics_window =
            get_p_graphics_window_by__index_from__manager(
                    p_graphics_window_manager, 
                    index_of__graphics_window);

        if (is_graphics_window_a__child_of__this_graphics_window(
                    p_graphics_window__child, 
                    p_graphics_window__parent)) {
            debug_error("set_graphics_window_as__parent_to__this_graphics_window, child is already assigned to another parent.");
            return;
        }
    }

    p_graphics_window__child->graphics_window__parent__uuid =
        GET_UUID_P(p_graphics_window__parent);

    sort_graphic_windows_in__graphic_window_manager(
            p_graphics_window_manager);
}

void release_children_of__graphics_window_from__graphics_window_manager(
        Game *p_game,
        Graphics_Window_Manager *p_graphics_window_manager,
        Graphics_Window *p_graphics_window) {
    for (Index__u32 index_of__graphics_window = 0;
            index_of__graphics_window < MAX_QUANTITY_OF__GRAPHICS_WINDOWS;
            index_of__graphics_window++) {
        Graphics_Window *p_graphics_window__child =
            get_p_graphics_window_by__index_from__manager(
                    p_graphics_window_manager, 
                    index_of__graphics_window);
        if (!p_graphics_window__child 
                || !is_graphics_window__allocated(p_graphics_window__child))
            continue;
        if (!is_graphics_window_a__child_of__this_graphics_window(
                    p_graphics_window__child, 
                    p_graphics_window))
            continue;
        // NOTE: This is potentially recursive.
        release_graphics_window_from__graphics_window_manager(
                p_game, 
                p_graphics_window__child);
    }
}

void release_graphics_window_from__graphics_window_manager(
        Game *p_game,
        Graphics_Window *p_graphics_window) {
    Gfx_Context *p_gfx_context =
        get_p_gfx_context_from__game(p_game);

    release_children_of__graphics_window_from__graphics_window_manager(
            p_game, 
            get_p_graphics_window_manager_from__gfx_context(
                get_p_gfx_context_from__game(p_game)), 
            p_graphics_window);
    
    PLATFORM_release_gfx_window(
            p_gfx_context, 
            p_graphics_window);
    UI_Manager *p_ui_manager =
        get_p_ui_manager_from__graphics_window(
                p_game,
                p_graphics_window);
    if (p_ui_manager) {
        release_p_ui_manager_from__ui_context(
                p_game,
                GET_UUID_P(p_graphics_window));
    }
    Sprite_Manager *p_sprite_manager =
        get_p_sprite_manager_from__graphics_window(
                p_game,
                p_graphics_window);
    if (p_sprite_manager) {
        release_sprite_manager_from__sprite_context(
                get_p_sprite_context_from__gfx_context(p_gfx_context),
                p_sprite_manager);
    }
    if (is_ui_tile_map__wrapper__valid(
                get_ui_tile_map_from__graphics_window(
                    p_graphics_window))) {
        release_ui_tile_map_with__ui_tile_map_manager(
                get_p_ui_tile_map_manager_from__gfx_context(
                    p_gfx_context), 
                get_ui_tile_map_from__graphics_window(
                    p_graphics_window));
    }
    DEALLOCATE_P(p_graphics_window);
    initialize_graphics_window(
            p_graphics_window);

    Graphics_Window **p_ptr_sorted_graphics_window_slot =
        get_sorted_slot_of__graphics_window_from__sorted_list(
                get_p_graphics_window_manager_from__gfx_context(
                    get_p_gfx_context_from__game(p_game)), 
                p_graphics_window);

    *p_ptr_sorted_graphics_window_slot = 0;

    sort_graphic_windows_in__graphic_window_manager(
            get_p_graphics_window_manager_from__gfx_context(p_gfx_context));
}

Quantity__u8 get_graphics_windows_from__graphics_window_manager(
        Graphics_Window_Manager *p_graphics_window_manager,
        Graphics_Window **p_ptr_array__graphics_windows,
        Quantity__u8 max_quantity_of__windows,
        Graphics_Window_Kind the_kind_of__graphics_window) {
    Index__u8 index_of__gfx_window_in__ptr_array = 0;
    if (!max_quantity_of__windows)
        return 0;
    for (Index__u32 index_of__graphics_window = 0;
            index_of__graphics_window
            < MAX_QUANTITY_OF__GRAPHICS_WINDOWS;
            index_of__graphics_window++) {
        Graphics_Window *p_graphics_window =
            get_p_graphics_window_by__index_from__manager(
                    p_graphics_window_manager, 
                    index_of__graphics_window);

        if (!is_graphics_window_of__this_kind(
                    p_graphics_window, 
                    the_kind_of__graphics_window)) {
            continue;
        }

        p_ptr_array__graphics_windows[
            index_of__gfx_window_in__ptr_array++] =
            p_graphics_window;

        if (index_of__gfx_window_in__ptr_array
                >= max_quantity_of__windows) {
            return index_of__graphics_window;
        }
    }
    
    return index_of__gfx_window_in__ptr_array;
}

void render_graphics_window(
        Game *p_game,
        Gfx_Context *p_gfx_context,
        Graphics_Window *p_gfx_window) {
    Sprite_Manager *p_sprite_manager =
        get_p_sprite_manager_from__graphics_window(
                p_game,
                p_gfx_window);

    if (p_gfx_window->p_camera
            && p_gfx_window->p_camera->m_camera_handler) {
        p_gfx_window->p_camera->m_camera_handler(
                p_gfx_window->p_camera,
                p_game,
                p_gfx_window);
    }

    if (p_sprite_manager) {
        render_sprites_in__sprite_manager(
                p_game,
                get_p_sprite_context_from__gfx_context(p_gfx_context),
                p_sprite_manager, 
                p_gfx_window);
    }

    PLATFORM_render_gfx_window(
            p_gfx_context, 
            p_gfx_window);
}

static Signed_Quantity__i32 f_sort_heuristic__p_graphics_window(
        void *p_context,
        void *pv_graphics_window__one,
        void *pv_graphics_window__two) {
    Graphics_Window_Manager *p_graphics_window_manager =
        (Graphics_Window_Manager*)p_context;

    Graphics_Window **p_ptr_graphics_window__one = 
        (Graphics_Window**)pv_graphics_window__one;
    Graphics_Window **p_ptr_graphics_window__two = 
        (Graphics_Window**)pv_graphics_window__two;

    if (!*p_ptr_graphics_window__one)
        return 1;
    else if (!*p_ptr_graphics_window__two)
        return -1;

    Graphics_Window *p_graphics_window__one = 
        *(Graphics_Window**)pv_graphics_window__one;
    Graphics_Window *p_graphics_window__two = 
        *(Graphics_Window**)pv_graphics_window__two;

    // The parent MUST come after the child.
    if (is_graphics_window_a__child_of__this_graphics_window(
                p_graphics_window__one, 
                p_graphics_window__two)) {
        return -1;
    } else if (is_graphics_window_a__child_of__this_graphics_window(
                p_graphics_window__two, 
                p_graphics_window__one)) {
        return 1;
    }

    if (p_graphics_window__one->graphics_window__parent__uuid
        // if both windows share a parent, sort by respective priority.
            == p_graphics_window__two->graphics_window__parent__uuid) {
        return p_graphics_window__one->origin_of__gfx_window.z__i32 
            - p_graphics_window__two->origin_of__gfx_window.z__i32
            ;
    } else {
        // otherwise sort by parent (if present, else self) priority.
        Graphics_Window *p_parent_of__one_or__one =
            (is_identifier_u32__invalid(p_graphics_window__one->graphics_window__parent__uuid))
            ? p_graphics_window__one
            : get_p_graphics_window_by__uuid_from__graphics_window_manager(
                    p_graphics_window_manager, 
                    p_graphics_window__one->graphics_window__parent__uuid);

        Graphics_Window *p_parent_of__two_or__two =
            (is_identifier_u32__invalid(p_graphics_window__two->graphics_window__parent__uuid))
            ? p_graphics_window__two
            : get_p_graphics_window_by__uuid_from__graphics_window_manager(
                    p_graphics_window_manager, 
                    p_graphics_window__two->graphics_window__parent__uuid);

        return p_parent_of__one_or__one->origin_of__gfx_window.z__i32
            - p_parent_of__two_or__two->origin_of__gfx_window.z__i32
            ;
    }

    return -1;
}

void f_sort_swap__graphics_window(
        void *p_context,
        void *pv_graphics_window__one,
        void *pv_graphics_window__two) {
    Graphics_Window **p_ptr_graphics_window__one = 
        (Graphics_Window**)pv_graphics_window__one;
    Graphics_Window **p_ptr_graphics_window__two = 
        (Graphics_Window**)pv_graphics_window__two;

    Graphics_Window *p_temporary =
        *p_ptr_graphics_window__one;

    *p_ptr_graphics_window__one =
        *p_ptr_graphics_window__two;

    *p_ptr_graphics_window__two =
        p_temporary;
}

void sort_graphic_windows_in__graphic_window_manager(
        Graphics_Window_Manager *p_graphics_window_manager) {
    heap_sort__opaque(
            p_graphics_window_manager,
            &p_graphics_window_manager->ptr_array_of__sorted_graphic_windows, 
            sizeof(Graphics_Window*), 
            MAX_QUANTITY_OF__GRAPHICS_WINDOWS, 
            f_sort_heuristic__p_graphics_window, 
            f_sort_swap__graphics_window);
}

void render_graphic_windows_in__graphics_window_manager(
        Game *p_game) {
    /*
     * From the Lavender CORE context, we assume that the backend operates off
     * of framebuffers, and sub-buffers which are processed before hand, and 
     * rendered as textures onto the main (parent) buffer.
     *
     * If the backend doesn't use framebuffers, we entrust the backend to
     * work around our static assumption.
     *
     * This means, that a parent must be ordered AFTER its children.
     */

    Gfx_Context * p_gfx_context =
        get_p_gfx_context_from__game(p_game);
    Graphics_Window_Manager *p_graphics_window__manager = 
        get_p_graphics_window_manager_from__gfx_context(
                p_gfx_context);

    BITMAP(bitmap__gfx_windows__visited, MAX_QUANTITY_OF__GRAPHICS_WINDOWS);
    memset(
            bitmap__gfx_windows__visited, 
            0, 
            sizeof(bitmap__gfx_windows__visited));

    for (Index__u32 index_of__graphics_window = MAX_QUANTITY_OF__GRAPHICS_WINDOWS - 1;
            index_of__graphics_window 
            < MAX_QUANTITY_OF__GRAPHICS_WINDOWS;
            index_of__graphics_window--) {
        Graphics_Window *p_gfx_window =
            get_p_graphics_window_by__index_from__manager(
                    p_graphics_window__manager, 
                    index_of__graphics_window);
        if (!is_graphics_window__allocated(
                    p_gfx_window)) {
            continue;
        }
        if (is_bit_set_in__bitmap(
                    bitmap__gfx_windows__visited, 
                    MAX_QUANTITY_OF__GRAPHICS_WINDOWS, 
                    index_of__graphics_window)) {
            continue;
        }

        render_graphics_window(
                p_game,
                p_gfx_context, 
                p_gfx_window);
    }
}

void compose_graphic_windows_in__graphics_window_manager(
        Game *p_game) {
    Gfx_Context * p_gfx_context =
        get_p_gfx_context_from__game(p_game);
    Graphics_Window_Manager *p_graphics_window__manager = 
        get_p_graphics_window_manager_from__gfx_context(
                p_gfx_context);

    for (Index__u32 index_of__graphics_window = 0;
            index_of__graphics_window 
            < MAX_QUANTITY_OF__GRAPHICS_WINDOWS;
            index_of__graphics_window++) {
        Graphics_Window *p_gfx_window =
            get_p_graphics_window_by__sorted_index_from__manager(
                    p_graphics_window__manager, 
                    index_of__graphics_window);
        if (!p_gfx_window) {
            break;
        }
        if (!is_graphics_window_in_need_of__composition(
                    p_gfx_window)) {
            // --- TODO: remove this, and
            // only compose the world if updates have been made.
            // if (!is_graphics_window__rendering_world(
            //             p_gfx_window)) {
            //     continue;
            // }
            // ---
        }
        set_graphics_window_as__no_longer_needing__composition(
                p_gfx_window);

        PLATFORM_compose_gfx_window(
                p_gfx_context, 
                p_gfx_window);
        compose_all_ui_elements_in__ui_manager(
                get_p_ui_manager_from__graphics_window(
                    p_game,
                    p_gfx_window),
                p_game,
                p_gfx_window);
    }
}

Graphics_Window *get_p_graphics_window_by__uuid_from__graphics_window_manager(
        Graphics_Window_Manager *p_graphics_window_manager,
        Identifier__u32 uuid__u32) {
#ifndef NDEBUG
    if (!p_graphics_window_manager) {
        debug_error("get_p_graphics_window_by__uuid_from__graphics_window_manager, p_graphics_window_manager == 0.");
        return 0;
    }
#endif
    Graphics_Window *p_graphics_window =
        (Graphics_Window*)dehash_identitier_u32_in__contigious_array(
                (Serialization_Header *)p_graphics_window_manager
                    ->graphics_windows, 
                MAX_QUANTITY_OF__GRAPHICS_WINDOWS, 
                uuid__u32);
    
#ifndef NDEBUG
    if (!p_graphics_window) {
        debug_error("get_p_graphics_window_by__uuid_from__graphics_window_manager, failed to find graphics_window.");
        return 0;
    }
#endif

    return p_graphics_window;
}
