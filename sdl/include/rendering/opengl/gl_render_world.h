#ifndef GL_RENDER_WORLD_H
#define GL_RENDER_WORLD_H

#include "defines_weak.h"

void GL_compose_world(
        Gfx_Context *p_gfx_context,
        Graphics_Window **p_ptr_array_of__gfx_windows,
        World *p_world,
        PLATFORM_Texture **p_ptr_array_of__PLATFORM_textures,
        Quantity__u32 quantity_of__gfx_windows,
        f_Tile_Render_Kernel f_tile_render_kernel);

#endif
