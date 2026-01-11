#ifndef GRAPHICS_WINDOW_H
#define GRAPHICS_WINDOW_H

#include "defines_weak.h"
#include "game.h"
#include "rendering/gfx_context.h"
#include "rendering/graphics_window_manager.h"
#include "rendering/sprite_context.h"
#include "rendering/sprite_manager.h"
#include "serialization/serialization_header.h"
#include "types/implemented/graphics_window_kind.h"
#include "ui/ui_context.h"
#include "vectors.h"
#include <defines.h>

void initialize_graphics_window(
        Graphics_Window *p_graphics_window);

void initialize_graphics_window_as__allocated(
        Graphics_Window *p_graphics_window,
        PLATFORM_Graphics_Window *p_PLATFORM_gfx_window,
        Graphics_Window_Kind the_kind_of__graphics_window);

void update_graphics_window__ui_tiles(
        Graphics_Window *p_gfx_window,
        const UI_Tile_Raw *p_ui_tiles,
        Quantity__u32 size_of__p_ui_tiles);

void set_graphics_window__ui_tile_map(
        Graphics_Window *p_gfx_window,
        UI_Tile_Map__Wrapper ui_tile_map_wrapper);

UI_Manager *allocate_ui_manager_for__graphics_window(
        Gfx_Context *p_gfx_context,
        Graphics_Window *p_graphics_window,
        Quantity__u16 max_quantity_of__ui_elements);

void allocate_sprite_pool_for__graphics_window(
        Gfx_Context *p_gfx_context,
        Graphics_Window *p_graphics_window,
        Quantity__u32 max_quantity_of__sprites_in__sprite_pool);

void set_position_3i32_of__graphics_window(
        Game *p_game,
        Graphics_Window *p_graphics_window,
        Vector__3i32 position_of__gfx_window__3i32);

void set_position_3i32_of__graphics_window__relative_to(
        Game *p_game,
        Graphics_Window *p_graphics_window,
        Vector__3i32 position__old__3i32,
        Vector__3i32 position__new__3i32);

Sprite *allocate_p_sprite_from__graphics_window(
        Game *p_game,
        Graphics_Window *p_graphics_window,
        Identifier__u32 uuid__u32, 
        Texture texture_to__sample_by__sprite,
        Texture_Flags texture_flags_for__sprite);

static inline
bool is_graphics_window__allocating_a_sprite_pool(
        Graphics_Window *p_graphics_window) {
    return p_graphics_window->graphics_window__sprite_manager__allocation_scheme
        == Graphics_Window__Sprite_Manager__Allocation_Scheme__Is_Allocating
        ;
}

static inline
bool is_graphics_window__using_parent_sprite_manager(
        Graphics_Window *p_graphics_window) {
    return p_graphics_window->graphics_window__sprite_manager__allocation_scheme
        == Graphics_Window__Sprite_Manager__Allocation_Scheme__Is_Using_Parent_Pool
        ;
}

static inline
UI_Tile_Map__Wrapper get_ui_tile_map_from__graphics_window(
        Graphics_Window *p_graphics_window) {
#ifndef NDEBUG
    if (!p_graphics_window) {
        debug_error("get_ui_tile_map_from__graphics_window, p_gfx_window == 0.");
        return (UI_Tile_Map__Wrapper){0};
    }
#endif
    return p_graphics_window->ui_tile_map__wrapper;
}

static inline
UI_Manager *get_p_ui_manager_from__graphics_window(
        Game *p_game,
        Graphics_Window *p_graphics_window) {
#ifndef NDEBUG
    if (!p_game) {
        debug_error("get_p_ui_manager_from__graphics_window, p_game == 0.");
        return 0;
    }
    if (!p_graphics_window) {
        debug_error("get_p_ui_manager_from__graphics_window, p_gfx_window == 0.");
        return 0;
    }
#endif
    return get_p_ui_manager_by__uuid_from__ui_context(
            get_p_ui_context_from__gfx_context(
                get_p_gfx_context_from__game(p_game)), 
            GET_UUID_P(p_graphics_window));
}

static inline
bool is_graphics_window_with__ui_manager(
        Game *p_game,
        Graphics_Window *p_graphics_window) {
#ifndef NDEBUG
    if (!p_game) {
        debug_error("get_p_ui_manager_from__graphics_window, p_game == 0.");
        return 0;
    }
    if (!p_graphics_window) {
        debug_error("is_graphics_window_with__ui_manager, p_gfx_window == 0.");
        return false;
    }
#endif
    return get_p_ui_manager_from__graphics_window(
            p_game, 
            p_graphics_window) 
        != 0
        ;
}

static inline
Sprite_Manager *get_p_sprite_manager_from__graphics_window(
        Game *p_game,
        Graphics_Window *p_graphics_window) {
#ifndef NDEBUG
    if (!p_graphics_window) {
        debug_error("get_p_sprite_manager_from__graphics_window, p_gfx_window == 0.");
        return 0;
    }
#endif
    return get_p_sprite_manager_by__uuid_from__sprite_context(
            get_p_sprite_context_from__gfx_context(
                get_p_gfx_context_from__game(p_game)), 
            GET_UUID_P(p_graphics_window));
}

static inline
bool is_graphics_window_in_need_of__composition(
        Graphics_Window *p_gfx_window) {
#ifndef NDEBUG
    if (!p_gfx_window) {
        debug_error("is_graphics_window_in_need_of__composition, p_gfx_window == 0.");
        return false;
    }
#endif
    return p_gfx_window->graphics_window__flags
        & GRAPHICS_WINDOW__FLAG__COMPOSE__DIRTY
        ;
}

static inline
void set_graphics_window_as__in_need_of__composition(
        Graphics_Window *p_gfx_window) {
#ifndef NDEBUG
    if (!p_gfx_window) {
        debug_error("set_graphics_window_as__in_need_of__composition, p_gfx_window == 0.");
        return;
    }
#endif
    p_gfx_window->graphics_window__flags |=
        GRAPHICS_WINDOW__FLAG__COMPOSE__DIRTY
        ;
}

static inline
void set_graphics_window_as__no_longer_needing__composition(
        Graphics_Window *p_gfx_window) {
#ifndef NDEBUG
    if (!p_gfx_window) {
        debug_error("set_graphics_window_as__no_longer_needing__composition, p_gfx_window == 0.");
        return;
    }
#endif
    p_gfx_window->graphics_window__flags &=
        ~GRAPHICS_WINDOW__FLAG__COMPOSE__DIRTY
        ;
}

static inline
Camera *get_p_camera_from__graphics_window(
        Graphics_Window *p_graphics_window) {
#ifndef NDEBUG
    if (!p_graphics_window) {
        debug_error("get_p_camera_from__graphics_window, p_gfx_window == 0.");
        return 0;
    }
#endif
    return p_graphics_window->p_camera;
}

static inline
void set_p_camera_of__graphics_window(
        Graphics_Window *p_graphics_window,
        Camera *p_camera) {
#ifndef NDEBUG
    if (!p_graphics_window) {
        debug_error("set_p_camera_of__graphics_window, p_gfx_window == 0.");
        return;
    }
#endif
    p_graphics_window->p_camera = p_camera;
}

static inline
bool is_graphics_window__allocated(
        Graphics_Window *p_graphics_window) {
    return (bool)(p_graphics_window && p_graphics_window->p_PLATFORM_gfx_window);
}

static inline
Vector__3i32 get_origin_3i32_of__graphics_window(
        Graphics_Window *p_graphics_window) {
#ifndef NDEBUG
    if (!p_graphics_window) {
        debug_error("get_origin_3i32_of__graphics_window, p_gfx_window == 0.");
        return VECTOR__3i32__OUT_OF_BOUNDS;
    }
#endif
    return p_graphics_window->origin_of__gfx_window;
}

static inline
Vector__3i32 get_position_3i32_of__graphics_window(
        Graphics_Window *p_graphics_window) {
#ifndef NDEBUG
    if (!p_graphics_window) {
        debug_error("get_position_3i32_of__graphics_window, p_gfx_window == 0.");
        return VECTOR__3i32__OUT_OF_BOUNDS;
    }
#endif
    return p_graphics_window->position_of__gfx_window;
}

static inline
Vector__3i32 get_position_maximum_3i32_of__graphics_window(
        Graphics_Window *p_graphics_window) {
#ifndef NDEBUG
    if (!p_graphics_window) {
        debug_error("get_position_maximum_3i32_of__graphics_window, p_gfx_window == 0.");
        return VECTOR__3i32__OUT_OF_BOUNDS;
    }
#endif
    return p_graphics_window->position_of__gfx_window__maximum;
}

static inline
Vector__3i32 get_position_minimum_3i32_of__graphics_window(
        Graphics_Window *p_graphics_window) {
#ifndef NDEBUG
    if (!p_graphics_window) {
        debug_error("get_position_minimum_3i32_of__graphics_window, p_gfx_window == 0.");
        return VECTOR__3i32__OUT_OF_BOUNDS;
    }
#endif
    return p_graphics_window->position_of__gfx_window__minimum;
}

static inline
Graphics_Window *get_p_parent_of__graphics_window(
        Graphics_Window_Manager *p_graphics_window_manager,
        Graphics_Window *p_graphics_window) {
#ifndef NDEBUG
    if (!p_graphics_window) {
        debug_error("get_p_parent_of__graphics_window, p_gfx_window == 0.");
        return 0;
    }
#endif
    return get_p_graphics_window_by__uuid_from__graphics_window_manager(
            p_graphics_window_manager, 
            p_graphics_window->graphics_window__parent__uuid);
}

static inline
bool is_graphics_window_a__child_of__this_graphics_window(
        Graphics_Window *p_graphics_window__child,
        Graphics_Window *p_graphics_window__parent) {
#ifndef NDEBUG
    if (!p_graphics_window__child) {
        debug_error("is_graphics_window_a__child_of__this_graphics_window, p_graphics_window__child == 0.");
        return false;
    }
    if (!p_graphics_window__parent) {
        debug_error("is_graphics_window_a__child_of__this_graphics_window, p_graphics_window__parent == 0.");
        return false;
    }
#endif
    return p_graphics_window__child->graphics_window__parent__uuid
        == GET_UUID_P(p_graphics_window__parent)
        ;
}

static inline
Graphics_Window_Kind get_kind_of__p_graphics_window(
        Graphics_Window *p_graphics_window) {
    return p_graphics_window->the_kind_of__window;
}

static inline
bool is_graphics_window_of__this_kind(
        Graphics_Window *p_graphics_window,
        Graphics_Window_Kind the_kind_of__graphics_window) {
#ifndef NDEBUG
    if (!p_graphics_window) {
        debug_error("is_graphics_window_of__this_kind, p_gfx_window == 0.");
        return false;
    }
#endif
    return get_kind_of__p_graphics_window(p_graphics_window)
        == the_kind_of__graphics_window;
}

static inline
bool is_graphics_window__enabled(
        Graphics_Window *p_gfx_window) {
#ifndef NDEBUG
    if (!p_gfx_window) {
        debug_error("is_graphics_window__enabled, p_gfx_window == 0.");
        return false;
    }
#endif
    return p_gfx_window->graphics_window__flags
        & GRAPHICS_WINDOW__FLAG__IS_ENABLED
        ;
}

static inline
void set_graphics_window_as__enabled(
        Graphics_Window *p_gfx_window) {
#ifndef NDEBUG
    if (!p_gfx_window) {
        debug_error("set_graphics_window_as__enabled, p_gfx_window == 0.");
        return;
    }
#endif
    p_gfx_window->graphics_window__flags |=
        GRAPHICS_WINDOW__FLAG__IS_ENABLED
        ;
}

static inline
void set_graphics_window_as__disabled(
        Graphics_Window *p_gfx_window) {
#ifndef NDEBUG
    if (!p_gfx_window) {
        debug_error("set_graphics_window_as__disabled, p_gfx_window == 0.");
        return;
    }
#endif
    p_gfx_window->graphics_window__flags &=
        ~GRAPHICS_WINDOW__FLAG__IS_ENABLED
        ;
}

static inline
bool is_graphics_window__rendering_world(
        Graphics_Window *p_gfx_window) {
#ifndef NDEBUG
    if (!p_gfx_window) {
        debug_error("is_graphics_window__rendering_world, p_gfx_window == 0.");
        return false;
    }
#endif
    return p_gfx_window->graphics_window__flags
        & GRAPHICS_WINDOW__FLAG__IS_RENDERING_WORLD
        ;
}

static inline
void set_graphics_window_as__rendering_world(
        Graphics_Window *p_gfx_window) {
#ifndef NDEBUG
    if (!p_gfx_window) {
        debug_error("set_graphics_window_as__rendering_world, p_gfx_window == 0.");
        return;
    }
#endif
    p_gfx_window->graphics_window__flags |=
        GRAPHICS_WINDOW__FLAG__IS_RENDERING_WORLD
        ;
}

static inline
void set_graphics_window_as__NOT_rendering_world(
        Graphics_Window *p_gfx_window) {
#ifndef NDEBUG
    if (!p_gfx_window) {
        debug_error("set_graphics_window_as__NOT_rendering_world, p_gfx_window == 0.");
        return;
    }
#endif
    p_gfx_window->graphics_window__flags &=
        ~GRAPHICS_WINDOW__FLAG__IS_RENDERING_WORLD
        ;
}

static inline
void set_graphics_window__ui_tile_map__texture(
        Graphics_Window *p_gfx_window,
        Identifier__u32 uuid__u32) {
#ifndef NDEBUG
    if (!p_gfx_window) {
        debug_error("set_graphics_window__ui_tile_map__texture, p_gfx_window == 0.");
        return;
    }
#endif
    p_gfx_window->ui_tile_map__texture__uuid =
        uuid__u32;
}

static inline
Identifier__u32 get_uuid_of__ui_tile_map__texture_from__gfx_window(
        Graphics_Window *p_gfx_window) {
#ifndef NDEBUG
    if (!p_gfx_window) {
        debug_error("get_uuid_of__ui_tile_map__texture_from__gfx_window, p_gfx_window == 0.");
        return IDENTIFIER__UNKNOWN__u32;
    }
#endif
    return p_gfx_window->ui_tile_map__texture__uuid;
}

#endif
