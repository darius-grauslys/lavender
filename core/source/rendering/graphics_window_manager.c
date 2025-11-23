#include "rendering/graphics_window_manager.h"
#include "defines.h"
#include "defines_weak.h"
#include "game.h"
#include "platform.h"
#include "rendering/gfx_context.h"
#include "rendering/graphics_window.h"
#include "rendering/sprite_manager.h"
#include "rendering/texture.h"
#include "serialization/hashing.h"
#include "serialization/serialization_header.h"
#include "ui/ui_context.h"
#include "ui/ui_manager.h"
#include "ui/ui_tile_map.h"
#include "ui/ui_tile_map_manager.h"
#include "util/bitmap/bitmap.h"
#include "world/camera.h"
#include "world/world.h"

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
        (Graphics_Window*)allocate_serialization_header_with__this_uuid(
                (Serialization_Header *)p_graphics_window_manager
                    ->graphics_windows, 
                MAX_QUANTITY_OF__GRAPHICS_WINDOWS, 
                uuid__u32);

    if (!p_graphics_window__available) {
        debug_error("allocate_graphics_window_with__graphics_window_manager, graphics window limit reached.");
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

    if (is_graphics_window_possessing__a_child(
                p_graphics_window__parent)) {
        debug_error("set_graphics_window_as__parent_to__this_graphics_window, parent already possesses a child.");
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

    p_graphics_window__parent->p_child__graphics_window =
        p_graphics_window__child;
}

void release_graphics_window_from__graphics_window_manager(
        Game *p_game,
        Graphics_Window *p_graphics_window) {
    Gfx_Context *p_gfx_context =
        get_p_gfx_context_from__game(p_game);

    if (is_graphics_window_possessing__a_child(
                p_graphics_window)) {
        release_graphics_window_from__graphics_window_manager(
                p_game,
                p_graphics_window);
    }
    
    PLATFORM_release_gfx_window(
            p_gfx_context, 
            p_graphics_window);
    UI_Manager *p_ui_manager =
        get_p_ui_manager_from__graphics_window(
                p_graphics_window);
    if (p_ui_manager) {
        release_p_ui_manager_from__ui_context(
                p_game,
                get_p_ui_context_from__gfx_context(p_gfx_context), 
                p_graphics_window,
                p_ui_manager);
    }
    Sprite_Manager *p_sprite_manager =
        get_p_sprite_manager_from__graphics_window(
                p_graphics_window);
    if (p_sprite_manager) {
        release_sprite_manager_from__gfx_context(
                p_gfx_context,
                p_sprite_manager,
                p_graphics_window);
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
                p_sprite_manager, 
                p_gfx_window);
    }

    PLATFORM_render_gfx_window(
            p_gfx_context, 
            p_gfx_window);
}

void render_graphic_windows_in__graphics_window_manager(
        Game *p_game) {
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

        if (is_graphics_window_possessing__a_child(
                    p_gfx_window)) {
            set_bit_in__bitmap(
                    bitmap__gfx_windows__visited, 
                    MAX_QUANTITY_OF__GRAPHICS_WINDOWS, 
                    p_gfx_window->p_child__graphics_window
                    - p_graphics_window__manager->graphics_windows, 
                    true);
            render_graphics_window(
                    p_game,
                    p_gfx_context, 
                    p_gfx_window);
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

    BITMAP(bitmap__gfx_windows__visited, MAX_QUANTITY_OF__GRAPHICS_WINDOWS);
    memset(
            bitmap__gfx_windows__visited, 
            0, 
            sizeof(bitmap__gfx_windows__visited));

    for (Index__u32 index_of__graphics_window = 0;
            index_of__graphics_window 
            < MAX_QUANTITY_OF__GRAPHICS_WINDOWS;
            index_of__graphics_window++) {
        Graphics_Window *p_gfx_window =
            get_p_graphics_window_by__index_from__manager(
                    p_graphics_window__manager, 
                    index_of__graphics_window);
        if (!is_graphics_window__allocated(
                    p_gfx_window)) {
            continue;
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
        if (is_bit_set_in__bitmap(
                    bitmap__gfx_windows__visited, 
                    MAX_QUANTITY_OF__GRAPHICS_WINDOWS, 
                    index_of__graphics_window)) {
            continue;
        }

        PLATFORM_compose_gfx_window(
                p_gfx_context, 
                p_gfx_window);
        compose_all_ui_elements_in__ui_manager(
                get_p_ui_manager_from__graphics_window(
                    p_gfx_window),
                p_game,
                p_gfx_window);

        if (is_graphics_window_possessing__a_child(
                    p_gfx_window)) {
            set_bit_in__bitmap(
                    bitmap__gfx_windows__visited, 
                    MAX_QUANTITY_OF__GRAPHICS_WINDOWS, 
                    p_gfx_window->p_child__graphics_window
                    - p_graphics_window__manager->graphics_windows, 
                    true);
            PLATFORM_compose_gfx_window(
                    p_gfx_context, 
                    p_gfx_window->p_child__graphics_window);
        }
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
