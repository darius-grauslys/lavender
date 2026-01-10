#include "rendering/gfx_context.h"
#include "defines.h"
#include "defines_weak.h"
#include "platform_defaults.h"
#include "rendering/aliased_texture_manager.h"
#include "rendering/font/font_manager.h"
#include "rendering/graphics_window.h"
#include "rendering/graphics_window_manager.h"
#include "rendering/sprite_manager.h"
#include "ui/ui_context.h"
#include "ui/ui_tile_map_manager.h"

void initialize_gfx_context(
        Gfx_Context *p_gfx_context) {
    memset(p_gfx_context,
            0,
            sizeof(Gfx_Context));
    initialize_graphics_window_manager(
            get_p_graphics_window_manager_from__gfx_context(p_gfx_context));
    initialize_aliased_texture_manager(
            get_p_aliased_texture_manager_from__gfx_context(p_gfx_context));
    initialize_ui_context(
            get_p_ui_context_from__gfx_context(p_gfx_context));
    initialize_ui_tile_map_manager(
            get_p_ui_tile_map_manager_from__gfx_context(p_gfx_context));
    initialize_font_manager(
            get_p_font_manager_from__gfx_context(p_gfx_context));
}

