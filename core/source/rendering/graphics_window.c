#include "rendering/graphics_window.h"
#include "defines.h"
#include "defines_weak.h"
#include "rendering/gfx_context.h"
#include "serialization/serialization_header.h"
#include "ui/ui_context.h"
#include "ui/ui_tile_map.h"
#include "ui/ui_manager.h"
#include "vectors.h"

void initialize_graphics_window(
        Graphics_Window *p_graphics_window) {
    memset((u8*)p_graphics_window + sizeof(Serialization_Header),
            0,
            sizeof(Graphics_Window) - sizeof(Serialization_Header));
}

void initialize_graphics_window_as__allocated(
        Graphics_Window *p_graphics_window,
        PLATFORM_Graphics_Window *p_PLATFORM_gfx_window,
        Graphics_Window_Kind the_kind_of__graphics_window) {
    p_graphics_window->p_PLATFORM_gfx_window = 
        p_PLATFORM_gfx_window;
    p_graphics_window->p_child__graphics_window = 0;
    p_graphics_window->origin_of__gfx_window =
        VECTOR__3i32__0_0_0;
    p_graphics_window->position_of__gfx_window =
        VECTOR__3i32__0_0_0;
    p_graphics_window->position_of__gfx_window__maximum =
        VECTOR__3i32__0_0_0;
    p_graphics_window->position_of__gfx_window__minimum =
        VECTOR__3i32__0_0_0;
    p_graphics_window->priority_of__window =
        0;
    p_graphics_window->the_kind_of__window =
        the_kind_of__graphics_window;
    p_graphics_window->graphics_window__flags =
        GRAPHICS_WINDOW__FLAGS__NONE;
}

void update_graphics_window__ui_tiles(
        Graphics_Window *p_gfx_window,
        const UI_Tile_Raw *p_ui_tiles,
        Quantity__u32 size_of__p_ui_tiles) {
    if (!is_ui_tile_map__wrapper__valid(
                p_gfx_window->ui_tile_map__wrapper)) {
        debug_error("update_graphics_window__ui_tiles, p_gfx_window lacks ui_tile_map data.");
        return;
    }
    memcpy(
            p_gfx_window
                ->ui_tile_map__wrapper
                .p_ui_tile_data,
            p_ui_tiles,
            size_of__p_ui_tiles);
    set_graphics_window_as__in_need_of__composition(p_gfx_window);
}

void set_graphics_window__ui_tile_map(
        Graphics_Window *p_gfx_window,
        UI_Tile_Map__Wrapper ui_tile_map_wrapper) {
    if (is_ui_tile_map__wrapper__valid(
                p_gfx_window->ui_tile_map__wrapper)) {
        debug_warning("set_graphics_window__ui_tile_map, ui_tile_map already assigned.");
    }

    p_gfx_window->ui_tile_map__wrapper =
        ui_tile_map_wrapper;
}

void allocate_ui_manager_for__graphics_window(
        Gfx_Context *p_gfx_context,
        Graphics_Window *p_graphics_window) {
    p_graphics_window->p_ui_manager =
        allocate_p_ui_manager_from__ui_context(
                get_p_ui_context_from__gfx_context(p_gfx_context));
}

void allocate_sprite_manager_for__graphics_window(
        Gfx_Context *p_gfx_context,
        Graphics_Window *p_graphics_window) {
    p_graphics_window->p_sprite_manager =
        allocate_sprite_manager_from__gfx_context(
                p_gfx_context);
}

void set_position_3i32_of__graphics_window(
        Game *p_game,
        Graphics_Window *p_graphics_window,
        Vector__3i32 position_of__gfx_window__3i32) {
#ifndef NDEBUG
    if (!p_graphics_window) {
        debug_error("set_position_3i32_of__graphics_window, p_gfx_window == 0.");
        return;
    }
#endif
    if (is_graphics_window_with__ui_manager(
                p_graphics_window)) {
        update_ui_manager_origin__relative_to(
                p_game,
                get_p_ui_manager_from__graphics_window(
                    p_graphics_window),
                get_position_3i32_of__graphics_window(
                    p_graphics_window),
                position_of__gfx_window__3i32);
    }
    p_graphics_window->position_of__gfx_window =
        position_of__gfx_window__3i32;
}

void set_position_3i32_of__graphics_window__relative_to(
        Game *p_game,
        Graphics_Window *p_graphics_window,
        Vector__3i32 position__old__3i32,
        Vector__3i32 position__new__3i32) {
#ifndef NDEBUG
    if (!p_graphics_window) {
        debug_error("set_position_3i32_of__graphics_window, p_gfx_window == 0.");
        return;
    }
#endif
    if (is_graphics_window_with__ui_manager(
                p_graphics_window)) {
        update_ui_manager_origin__relative_to(
                p_game,
                get_p_ui_manager_from__graphics_window(
                    p_graphics_window),
                position__old__3i32,
                position__new__3i32);
    }
    subtract_p_vectors__3i32(
            &p_graphics_window
            ->position_of__gfx_window, 
            &position__old__3i32);

    add_p_vectors__3i32(
            &p_graphics_window
            ->position_of__gfx_window, 
            &position__new__3i32);
}

/* TODO: pulled from SDL back end, needed?
    switch (get_texture_flags__size(
                texture_flags)) {
        default:
            debug_error("SDL_allocate_gfx_window, unknown texture size.");
            break;
        case TEXTURE_FLAG__SIZE_8x8:
        case TEXTURE_FLAG__SIZE_8x16:
        case TEXTURE_FLAG__SIZE_8x32:
        case TEXTURE_FLAG__SIZE_16x8:
        case TEXTURE_FLAG__SIZE_16x16:
        case TEXTURE_FLAG__SIZE_16x32:
        case TEXTURE_FLAG__SIZE_32x16:
        case TEXTURE_FLAG__SIZE_32x32:
        case TEXTURE_FLAG__SIZE_32x64:
        case TEXTURE_FLAG__SIZE_64x64:
            p_PLATFORM_gfx_window
                ->SDL_graphics_window__ui_tile_map__wrapper =
                allocate_ui_tile_map_with__ui_tile_map_manager(
                        SDL_get_p_ui_tile_map_manager_from__PLATFORM_gfx_context(
                            p_PLATFORM_gfx_context), 
                        UI_Tile_Map_Size__Small);
            break;
        case TEXTURE_FLAG__SIZE_128x128:
            p_PLATFORM_gfx_window
                ->SDL_graphics_window__ui_tile_map__wrapper =
                allocate_ui_tile_map_with__ui_tile_map_manager(
                        SDL_get_p_ui_tile_map_manager_from__PLATFORM_gfx_context(
                            p_PLATFORM_gfx_context), 
                        UI_Tile_Map_Size__Medium);
            break;
        case TEXTURE_FLAG__SIZE_256x256:
        case TEXTURE_FLAG__SIZE_256x512:
        case TEXTURE_FLAG__SIZE_512x256:
        case TEXTURE_FLAG__SIZE_512x512:
            p_PLATFORM_gfx_window
                ->SDL_graphics_window__ui_tile_map__wrapper =
                allocate_ui_tile_map_with__ui_tile_map_manager(
                        SDL_get_p_ui_tile_map_manager_from__PLATFORM_gfx_context(
                            p_PLATFORM_gfx_context), 
                        UI_Tile_Map_Size__Large);
            break;
    }

    set_ui_tile_map__wrapper__utilized_size(
            &p_PLATFORM_gfx_window
            ->SDL_graphics_window__ui_tile_map__wrapper, 
            get_length_of__texture_flag__width(
                texture_flags)
            / TILE_WIDTH__IN_PIXELS, 
            get_length_of__texture_flag__height(
                texture_flags)
            / TILE_WIDTH__IN_PIXELS);
 */
