#include "rendering/sdl_render_world.h"
#include "defines.h"
#include "defines_weak.h"
#include "rendering/gfx_context.h"
#include "sdl_defines.h"
#include "world/world.h"

void PLATFORM_compose_world(
        Gfx_Context *p_gfx_context,
        Graphics_Window **p_ptr_array_of__gfx_windows,
        Local_Space_Manager *p_local_space_manager,
        PLATFORM_Texture **p_ptr_array_of__PLATFORM_textures,
        Quantity__u32 quantity_of__gfx_windows,
        f_Tile_Render_Kernel f_tile_render_kernel) {
    f_SDL_Compose_World f_SDL_compose_world =
        p_gfx_context
        ->p_PLATFORM_gfx_context
        ->SDL_gfx_sub_context__wrapper
        .f_SDL_compose_world;

    if (!f_SDL_compose_world) {
        debug_error("SDL::PLATFORM_compose_world, f_SDL_compose_world == 0.");
        return;
    }

    f_SDL_compose_world(
            p_gfx_context,
            p_ptr_array_of__gfx_windows,
            p_local_space_manager,
            p_ptr_array_of__PLATFORM_textures,
            quantity_of__gfx_windows,
            f_tile_render_kernel);
}
