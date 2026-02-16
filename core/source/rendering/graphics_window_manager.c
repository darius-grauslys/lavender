#include "rendering/graphics_window_manager.h"
#include "debug/debug.h"
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

Graphics_Window *_allocate_graphics_window_from__graphics_window_manager(
        Gfx_Context *p_gfx_context,
        Graphics_Window_Manager *p_graphics_window_manager,
        PLATFORM_Graphics_Window *OPTIONAL_p_PLATFORM_graphics_window,
        Identifier__u32 OPTIONAL_uuid__u32,
        Texture_Flags texture_flags_for__gfx_window) {
    if (is_identifier_u32__invalid(OPTIONAL_uuid__u32)) {
        OPTIONAL_uuid__u32 =
            get_next_available__random_uuid_in__contiguous_array(
                    (Serialization_Header *)p_graphics_window_manager->graphics_windows, 
                    MAX_QUANTITY_OF__GRAPHICS_WINDOWS, 
                    &p_graphics_window_manager->randomizer);
    }

    Graphics_Window *p_graphics_window__available = 
        (Graphics_Window*)get_next_available__allocation_in__contiguous_array(
                (Serialization_Header *)p_graphics_window_manager
                    ->graphics_windows, 
                MAX_QUANTITY_OF__GRAPHICS_WINDOWS, 
                OPTIONAL_uuid__u32);

    if (!p_graphics_window__available) {
        // TODO: this is misleading, a UUID collision could occur and make p_graphics_window__available 0
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
        OPTIONAL_p_PLATFORM_graphics_window;
    if (!p_PLATFORM_gfx_window) { 
        p_PLATFORM_gfx_window =
            PLATFORM_allocate_gfx_window(
                    p_gfx_context, 
                    texture_flags_for__gfx_window);
    }

    if (!p_PLATFORM_gfx_window) {
        debug_error("allocate_graphics_window_with__graphics_window_manager, failed to allocate PLATFORM_gfx_window.");
        DEALLOCATE_P(p_graphics_window__available);
        return 0;
    }

    initialize_graphics_window(
            p_graphics_window__available);
    ALLOCATE_P(
            p_graphics_window__available, 
            OPTIONAL_uuid__u32);

    p_graphics_window__available
        ->width_of__graphics_window__u32 =
        get_length_of__texture_flag__width(texture_flags_for__gfx_window);
    p_graphics_window__available
        ->height_of__graphics_window__u32 =
        get_length_of__texture_flag__height(texture_flags_for__gfx_window);
    set_graphics_window_as__in_need_of__composition(
            p_graphics_window__available);

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

Graphics_Window *allocate_graphics_window_with__uuid_from__graphics_window_manager(
        Gfx_Context *p_gfx_context,
        Graphics_Window_Manager *p_graphics_window_manager,
        Identifier__u32 uuid__u32,
        Texture_Flags texture_flags_for__gfx_window) {
    return _allocate_graphics_window_from__graphics_window_manager(
            p_gfx_context, 
            p_graphics_window_manager, 
            0, 
            uuid__u32, 
            texture_flags_for__gfx_window);
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
    if (!p_graphics_window) {
#ifndef NDEBUG
        debug_error("release_graphics_window_from__graphics_window_manager, p_graphics_window == 0.");
#endif
        return;
    }
    Gfx_Context *p_gfx_context =
        get_p_gfx_context_from__game(p_game);

    release_children_of__graphics_window_from__graphics_window_manager(
            p_game, 
            get_p_graphics_window_manager_from__gfx_context(
                get_p_gfx_context_from__game(p_game)), 
            p_graphics_window);
    
    if (p_graphics_window->p_PLATFORM_gfx_window) {
        PLATFORM_release_gfx_window(
                p_gfx_context, 
                p_graphics_window);
    }
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

/**
 * Default graphics window sort heuristic.
 *
 * Worst case O(TBD) - super super bad
 **/
static Signed_Quantity__i32 f_sort_heuristic__p_graphics_window(
        void *p_context,
        void *pv_graphics_window__one,
        void *pv_graphics_window__two) {
#ifndef NDEBUG
    // TODO: add a safety level to debug flags
    // SAFE0 - most optimized, but least bug resistant.
    // This would be SAFE3 (protect against intrinsic violations)
    if (pv_graphics_window__one == pv_graphics_window__two) {
        debug_warning("Duplicate window found in sorted list!");
        debug_error("f_sort_heuristic__p_graphics_window, intrinsic violation");
        return 0;
    }
#endif
    Graphics_Window_Manager *p_graphics_window_manager =
        (Graphics_Window_Manager*)p_context;

    Graphics_Window *p_graphics_window__one = 
        *(Graphics_Window**)pv_graphics_window__one;
    Graphics_Window *p_graphics_window__two = 
        *(Graphics_Window**)pv_graphics_window__two;

    // Preliminary checks 
    // do null check
    if (!p_graphics_window__two)
        goto two_priority;
    if (!p_graphics_window__one)
        goto one_priority;

    // sort as siblings if applicable.
    if (p_graphics_window__one->graphics_window__parent__uuid
            == p_graphics_window__two->graphics_window__parent__uuid) {
        // They are siblings, sort by Z
        goto sort_by_z;
    }

    // Sort as parent-child if possible.
    if (GET_UUID_P(p_graphics_window__one) 
            == p_graphics_window__two->graphics_window__parent__uuid) {
        goto two_priority;
    }
    if (GET_UUID_P(p_graphics_window__two) 
            == p_graphics_window__one->graphics_window__parent__uuid) {
        goto one_priority;
    }

    bool is_graphics_window_one_a__parent = 
        is_graphics_window_a__parent(
                p_graphics_window_manager, 
                p_graphics_window__one);
    bool is_graphics_window_two_a__parent = 
        is_graphics_window_a__parent(
                p_graphics_window_manager, 
                p_graphics_window__two);

    bool is_graphics_window_one_having_a__parent =
        is_graphics_window_with__parent(p_graphics_window__one);
    bool is_graphics_window_two_having_a__parent =
        is_graphics_window_with__parent(p_graphics_window__two);

    bool is_graphics_window_one__a_root =
        is_graphics_window_one_a__parent
        && !is_graphics_window_one_having_a__parent;
    bool is_graphics_window_two__a_root =
        is_graphics_window_two_a__parent
        && !is_graphics_window_two_having_a__parent;

    bool is_graphics_window_one__a_childless_orphan =
        !is_graphics_window_one_a__parent
        && !is_graphics_window_one_having_a__parent
        ;
    bool is_graphics_window_two__a_childless_orphan =
        !is_graphics_window_two_a__parent
        && !is_graphics_window_two_having_a__parent
        ;

    // First, sort as childless orphans if applicable
    if (is_graphics_window_one__a_childless_orphan
            && is_graphics_window_two__a_childless_orphan) {
        // Sort by z
        goto sort_by_z;
    }

    // Second, sort by root priority if applicable.
    if (is_graphics_window_one__a_root
            && is_graphics_window_two__a_root) {
        // Both are roots, sort by Z
        goto sort_by_z;
    } else if (is_graphics_window_two__a_root
            && !is_graphics_window_one__a_root) {
        // Two is the sole root: one takes priority
        goto one_priority;
    } else if (is_graphics_window_one__a_root
            && !is_graphics_window_two__a_root) {
        // One is the sole root: two takes priority
        goto two_priority;
    }

    // Neither window is a parent of the other, sibling of the other, and
    // neither windows are roots, compare by least disjoint ancestors:
    //     Two least disjoint ancestors is two (grand-*)parents such that both 
    //     share a common parent.
    Graphics_Window *p_graphics_window__disjoint_parent_one = 0;
    Graphics_Window *p_graphics_window__disjoint_parent_two = 0;
    Quantity__u32 depth_of_search__one = (Quantity__u32)-1;
    Quantity__u32 depth_of_search__two = (Quantity__u32)-1;
    while (p_graphics_window__disjoint_parent_one
            == p_graphics_window__disjoint_parent_two) {
        p_graphics_window__disjoint_parent_one =
            get_graphics_window__p_root_parent(
                    p_graphics_window_manager, 
                    p_graphics_window__one, 
                    &depth_of_search__one);
        if (!p_graphics_window__disjoint_parent_one) {
            // Disjoint chain try again
            p_graphics_window__disjoint_parent_one =
                get_graphics_window__p_root_parent(
                        p_graphics_window_manager, 
                        p_graphics_window__one, 
                        &depth_of_search__one);
        }
        p_graphics_window__disjoint_parent_two =
            get_graphics_window__p_root_parent(
                    p_graphics_window_manager, 
                    p_graphics_window__two, 
                    &depth_of_search__two);
        if (!p_graphics_window__disjoint_parent_two) {
            // Disjoint chain try again
            p_graphics_window__disjoint_parent_two =
                get_graphics_window__p_root_parent(
                        p_graphics_window_manager, 
                        p_graphics_window__two, 
                        &depth_of_search__two);
        }
        if (1 <= depth_of_search__one)
            depth_of_search__one--;
        if (1 <= depth_of_search__two)
            depth_of_search__two--;
    }

    // Sort by z on disjoint parents.
    return p_graphics_window__disjoint_parent_one
        ->position_of__gfx_window.z__i32
        - p_graphics_window__disjoint_parent_two
        ->position_of__gfx_window.z__i32
        ;
sort_by_z:
    return p_graphics_window__one->position_of__gfx_window.z__i32
        - p_graphics_window__two->position_of__gfx_window.z__i32;
one_priority:
    return 1;
two_priority:
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

Graphics_Window *get_graphics_window__p_parent(
        Graphics_Window_Manager *p_graphics_window_manager,
        Graphics_Window *p_graphics_window) {
    if (is_identifier_u32__invalid(
                p_graphics_window->graphics_window__parent__uuid)) {
        // trivial case - no parent
        return 0;
    }

    for (Index__u32 index_of__graphics_window = 0;
            index_of__graphics_window < MAX_QUANTITY_OF__GRAPHICS_WINDOWS;
            index_of__graphics_window++) {
        // O(N) trivial search for parent
        Graphics_Window *p_graphics_window__parent_candidate =
            get_p_graphics_window_by__index_from__manager(
                    p_graphics_window_manager, 
                    index_of__graphics_window);
        if (p_graphics_window->graphics_window__parent__uuid
                == GET_UUID_P(p_graphics_window__parent_candidate)) {
            return p_graphics_window__parent_candidate;
        }
    }
    return 0;
}

/**
 * O(TBD) - its bad
 **/
Graphics_Window *get_graphics_window__p_root_parent(
        Graphics_Window_Manager *p_graphics_window_manager,
        Graphics_Window *p_graphics_window,
        Quantity__u32 *p_OUT_depth_to_search) {
    if (!p_graphics_window) {
        *p_OUT_depth_to_search = 0;
        return 0;
    }
    // If depth_to_search is -1, disregard the depth limit.
    Quantity__u32 depth_to_search = *p_OUT_depth_to_search;
    if (!depth_to_search)
        return p_graphics_window; // Go no deeper.

    Quantity__u32 depth_reached = 0;
    Graphics_Window *p_graphics_window__current_parent = p_graphics_window;
    while (p_graphics_window__current_parent) {
        if (!is_graphics_window_with__parent(
                    p_graphics_window__current_parent)) {
            break;
        }
        p_graphics_window__current_parent =
            get_graphics_window__p_parent(
                    p_graphics_window_manager, 
                    p_graphics_window__current_parent);
        if (!p_graphics_window__current_parent) {
            debug_error("get_graphics_window__p_root_parent, broken chain.");
            debug_warning("Orphaning the window!");
            p_graphics_window__current_parent->graphics_window__parent__uuid =
                IDENTIFIER__UNKNOWN__u32;
            // Return 0 to express a broken chain discovery.
            // Callee can invoke this function again to get
            // the new root parent.
            return 0;
        }
        if (depth_to_search != (Quantity__u32)-1) {
            // depth_to_search was not initially unbound.
            if (MAX_QUANTITY_OF__GRAPHICS_WINDOWS >= --depth_to_search)
                // U32 Wrap around occured, do not search any deeper.
                break;
        }
        depth_reached++;
    }
    *p_OUT_depth_to_search = depth_reached;
    return p_graphics_window__current_parent;
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

    for (Index__u32 index_of__graphics_window = 0;
            index_of__graphics_window < MAX_QUANTITY_OF__GRAPHICS_WINDOWS;
            index_of__graphics_window++) {
        Graphics_Window *p_gfx_window =
            get_p_graphics_window_by__sorted_index_from__manager(
                    p_graphics_window__manager, 
                    index_of__graphics_window);

        // render_graphics_window() does this
        // TODO: needed?
        // if (p_gfx_window && p_gfx_window->p_camera) {
        //     if (p_gfx_window->p_camera->m_camera_handler) {
        //         p_gfx_window->p_camera->m_camera_handler(
        //                 p_gfx_window->p_camera,
        //                 p_game,
        //                 p_gfx_window);
        //     }
        // }

        if (!p_gfx_window || !p_gfx_window->f_PLATFORM_render_gfx_window)
            break;

        p_gfx_window->f_PLATFORM_render_gfx_window(
                p_game,
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
        if (!p_gfx_window || !p_gfx_window->f_PLATFORM_compose_gfx_window) {
            break;
        }
        if (!is_graphics_window_in_need_of__composition(
                    p_gfx_window)) {
            continue;
        }

        p_gfx_window->f_PLATFORM_compose_gfx_window(
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

Quantity__u32 get_index_in_ptr_array_of__gfx_window_and__quantity_of__descendants(
        Graphics_Window_Manager *p_graphics_window_manager,
        Graphics_Window *p_graphics_window,
        Quantity__u32 *p_quantity_of__children__u32) {
    Index__u32 index_of__graphics_window = 0;

    for (;index_of__graphics_window < MAX_QUANTITY_OF__GRAPHICS_WINDOWS;
            index_of__graphics_window++) {
        if (p_graphics_window_manager->ptr_array_of__sorted_graphic_windows[
                index_of__graphics_window]
                == p_graphics_window) {
            break;
        }
    }

    Quantity__u32 quantity_of__children = 0;
    for (Index__u32 index_of__child_window = index_of__graphics_window;
            index_of__child_window < MAX_QUANTITY_OF__GRAPHICS_WINDOWS;
            index_of__child_window++) {
        Graphics_Window *p_graphics_window__potential_child = 
            p_graphics_window_manager->ptr_array_of__sorted_graphic_windows[
                    index_of__child_window];
        if (!p_graphics_window__potential_child)
            break;
        if (is_graphics_window_a__descendant_of__this_graphics_window(
                    p_graphics_window_manager,
                    p_graphics_window__potential_child, 
                    p_graphics_window)) {
            quantity_of__children++;
        }
    }

    *p_quantity_of__children__u32 = quantity_of__children;
    return index_of__graphics_window;
}

bool is_graphics_window_a__descendant_of__this_graphics_window(
        Graphics_Window_Manager *p_graphics_window_manager,
        Graphics_Window *p_graphics_window__child,
        Graphics_Window *p_graphics_window__potential_ancestor) {
    if (is_graphics_window_a__child_of__this_graphics_window(
                p_graphics_window__child, 
                p_graphics_window__potential_ancestor)) {
        return true;
    }

    Graphics_Window *p_graphics_window__current_parent =
        p_graphics_window__child;
    for (Index__u32 recursive_decent_limiter = 0;
            recursive_decent_limiter
            <= MAX_QUANTITY_OF__GRAPHICS_WINDOWS;
            recursive_decent_limiter++) {
        if (!is_graphics_window_with__parent(p_graphics_window__current_parent)) {
            return false;
        }
        p_graphics_window__current_parent =
            get_p_parent_of__graphics_window(
                    p_graphics_window_manager, 
                    p_graphics_window__current_parent);
        if (!p_graphics_window__current_parent)
            return false;
        if (p_graphics_window__current_parent
                == p_graphics_window__potential_ancestor) {
            return true;
        }
    }

    debug_warning("This is usually only possible if a CORE intrinsic is violated:");
    debug_error("is_graphics_window_a__descendant_of__this_graphics_window, recursive limit reached.");
    return false;
}

Graphics_Window *get_p_graphics_window_with__this_PLATFORM_graphics_window(
        Graphics_Window_Manager *p_graphics_window_manager,
        PLATFORM_Graphics_Window *p_PLATFORM_graphics_window) {
    for (Index__u32 index_of__graphics_window = 0;
            index_of__graphics_window < MAX_QUANTITY_OF__GRAPHICS_WINDOWS;
            index_of__graphics_window++) {
        Graphics_Window *p_graphics_window =
            get_p_graphics_window_by__index_in_ptr_array_from__manager(
                    p_graphics_window_manager, 
                    index_of__graphics_window);
        if (!p_graphics_window)
            break;
        if (p_graphics_window->p_PLATFORM_gfx_window == p_PLATFORM_graphics_window)
            return p_graphics_window;
    }
    return 0;
}

bool allocate_or_get__platform_provided_graphics_windows(
        Gfx_Context *p_gfx_context,
        Graphics_Window_Manager *p_graphics_window_manager,
        Graphics_Window **ptr_array_of__graphics_windows,
        Quantity__u32 quantity_of__ptrs_in_buffer__u32,
        Quantity__u32 *p_quantity_of__overflowed_windows__u32,
        Index__u32 offset_of__graphics_window) {
    memset(ptr_array_of__graphics_windows, 
            0, 
            sizeof(Graphics_Window*)
            * quantity_of__ptrs_in_buffer__u32);

    PLATFORM_Graphics_Window *ptr_array_of__PLATFORM_graphics_windows[
        quantity_of__ptrs_in_buffer__u32];
    Texture_Flags array_of__texture_flags[
        quantity_of__ptrs_in_buffer__u32];
    Quantity__u32 quantity_of__overflowed_windows_from__platform__u32 = 0;
    Quantity__u32 quantity_of__total_overflowed_windows__u32 = 0;
    do {
        quantity_of__overflowed_windows_from__platform__u32 =
            PLATFORM_get_provided_windows(
                    p_gfx_context, 
                    ptr_array_of__PLATFORM_graphics_windows, 
                    array_of__texture_flags,
                    quantity_of__ptrs_in_buffer__u32, 
                    offset_of__graphics_window
                    + quantity_of__total_overflowed_windows__u32);
        quantity_of__total_overflowed_windows__u32 +=
            quantity_of__overflowed_windows_from__platform__u32;

        for (Index__u32 index_of__graphics_window__u32 = 0;
                index_of__graphics_window__u32 
                < quantity_of__ptrs_in_buffer__u32;
                index_of__graphics_window__u32++ ) {
            PLATFORM_Graphics_Window *p_PLATFORM_graphics_window =
                ptr_array_of__PLATFORM_graphics_windows[index_of__graphics_window__u32];

            if (!p_PLATFORM_graphics_window) {
                break;
            }

            Graphics_Window *p_graphics_window_possessing_this__PLATFORM_graphics_window =
                get_p_graphics_window_with__this_PLATFORM_graphics_window(
                        p_graphics_window_manager, 
                        p_PLATFORM_graphics_window);

            if (p_graphics_window_possessing_this__PLATFORM_graphics_window) {
                goto assign_window;
            }

            p_graphics_window_possessing_this__PLATFORM_graphics_window =
                _allocate_graphics_window_from__graphics_window_manager(
                        p_gfx_context, 
                        p_graphics_window_manager, 
                        p_PLATFORM_graphics_window, 
                        IDENTIFIER__UNKNOWN__u32, 
                        array_of__texture_flags[index_of__graphics_window__u32]);

            if (!p_graphics_window_possessing_this__PLATFORM_graphics_window) {
                debug_error("allocate_or_get__platform_provided_graphics_windows, failed to allocate graphics window.");
                goto error;
            }

assign_window:
            ptr_array_of__graphics_windows[
                index_of__graphics_window__u32] = 
                    p_graphics_window_possessing_this__PLATFORM_graphics_window;
        }
    } while (quantity_of__overflowed_windows_from__platform__u32);

    *p_quantity_of__overflowed_windows__u32 = 
        quantity_of__total_overflowed_windows__u32;
    return true;
error:
    *p_quantity_of__overflowed_windows__u32 = 0;
    return false;
}

bool setup_platform_provided_graphics_windows(
        Gfx_Context *p_gfx_context) {
    Quantity__u32 quantity_of__graphics_windows__overflowed__u32 = 0;
    Graphics_Window *ptr_array_of__graphics_windows[MAX_QUANTITY_OF__GRAPHICS_WINDOWS];
    bool success = allocate_or_get__platform_provided_graphics_windows(
        p_gfx_context,
        get_p_graphics_window_manager_from__gfx_context(p_gfx_context),
        ptr_array_of__graphics_windows,
        MAX_QUANTITY_OF__GRAPHICS_WINDOWS,
        &quantity_of__graphics_windows__overflowed__u32,
        0);

    if (quantity_of__graphics_windows__overflowed__u32) {
        debug_abort("setup_platform_provided_graphics_windows, MAX_QUANTITY_OF__GRAPHICS_WINDOWS < quantity platform requires.");
        return false;
    }

    return success;
}

Graphics_Window *itterate_platform_graphics_windows(
        Gfx_Context *p_gfx_context,
        Index__u32 *p_index_itterator__u32) {
    Quantity__u32 quantity_of__graphics_windows__overflowed__u32 = 0;
    Graphics_Window *ptr_array_of__graphics_windows[1];
    bool success = allocate_or_get__platform_provided_graphics_windows(
        p_gfx_context,
        get_p_graphics_window_manager_from__gfx_context(p_gfx_context),
        ptr_array_of__graphics_windows,
        1,
        &quantity_of__graphics_windows__overflowed__u32,
        (*p_index_itterator__u32)++);

    if (!success) {
        debug_error("itterate_platform_graphics_windows, failed to allocate window.");
        return 0;
    }

    return ptr_array_of__graphics_windows[0];
}

Graphics_Window *get_default_platform_graphics_window(
        Gfx_Context *p_gfx_context) {
    Index__u32 _ittr = 0;
    return itterate_platform_graphics_windows(p_gfx_context, &_ittr);
}
