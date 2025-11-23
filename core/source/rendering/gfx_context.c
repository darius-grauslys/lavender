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

Sprite_Manager *allocate_sprite_manager_from__gfx_context(
        Gfx_Context *p_gfx_context,
        Graphics_Window *p_gfx_window__owning_the__sprite_manager) {

    if (get_p_sprite_manager_from__graphics_window(
                p_gfx_window__owning_the__sprite_manager)) {
        debug_error("allocate_sprite_manager_from__gfx_context, p_gfx_window__owning_the__sprite_manager already has a sprite_manager.");
        return 0;
    }

    for (Index__u32 index_of__sprite_manager = 0;
            index_of__sprite_manager
            < MAX_QUANTITY_OF__SPRITE_MANAGERS;
            index_of__sprite_manager++) {
        Sprite_Manager **p_ptrM_sprite_manager =
            &p_gfx_context->PM_sprite_managers[
                index_of__sprite_manager];

        if (*p_ptrM_sprite_manager)
            continue;

        *p_ptrM_sprite_manager = malloc(sizeof(Sprite_Manager));
        if (!*p_ptrM_sprite_manager) {
            debug_error("allocate_sprite_manager_from__gfx_context, failed to allocate sprite_manager.");
            return 0;
        }
        
        initialize_sprite_manager(*p_ptrM_sprite_manager);
        (*p_ptrM_sprite_manager)->uuid_of__owning_graphics_window =
            GET_UUID_P(p_gfx_window__owning_the__sprite_manager);
        // This "share" seems confusing here, but
        // ownership is expressed in the line above.
        share_sprite_manager_with__graphics_window(
                p_gfx_window__owning_the__sprite_manager, 
                (*p_ptrM_sprite_manager));
        return *p_ptrM_sprite_manager;
    }

    debug_error("allocate_sprite_manager_from__gfx_context, maximum quantity of sprite_managers reached.");
    return 0;
}

void release_sprite_manager_from__gfx_context(
        Gfx_Context *p_gfx_context,
        Sprite_Manager *p_sprite_manager,
        Graphics_Window *p_graphics_window__owning_this__sprite_manager) {
#ifndef NDEBUG
    if (!p_gfx_context) {
        debug_error("release_sprite_manager_from__gfx_context, p_gfx_context == 0.");
        return;
    }
    if (!p_sprite_manager) {
        debug_error("release_sprite_manager_from__gfx_context, p_sprite_manager == 0.");
        return;
    }
#endif

    if (!is_graphics_window__owning_this__sprite_manager(
                p_graphics_window__owning_this__sprite_manager, 
                p_sprite_manager)) {
        // fail silently.
        return;
    }

    for (Index__u32 index_of__sprite_manager = 0;
            index_of__sprite_manager 
            < MAX_QUANTITY_OF__SPRITE_MANAGERS;
            index_of__sprite_manager++) {
        Sprite_Manager **p_ptrM_sprite_manager =
            &p_gfx_context->PM_sprite_managers[
                index_of__sprite_manager];

        if (*p_ptrM_sprite_manager
                == p_sprite_manager) {
            *p_ptrM_sprite_manager = 0;
            goto pM_validate__pass;
        }
    }
    debug_error("release_sprite_manager_from__gfx_context, p_sprite_manager was not allocated with this gfx_context.");
    return;
pM_validate__pass:

    free(p_sprite_manager);
}
