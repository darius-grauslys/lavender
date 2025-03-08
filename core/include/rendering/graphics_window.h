#ifndef GRAPHICS_WINDOW_H
#define GRAPHICS_WINDOW_H

#include "defines_weak.h"
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

static inline
void set_p_ui_manager_of__graphics_window(
        Graphics_Window *p_graphics_window,
        UI_Manager *p_ui_manager) {
#ifndef NDEBUG
    if (p_graphics_window->p_ui_manager) {
        debug_warning("set_p_ui_manager_of__graphics_window, p_graphics_window->p_ui_manager != 0. Leaking?");
    }
#endif
    p_graphics_window
        ->p_ui_manager = p_ui_manager;
}

static inline
bool is_graphics_window_with__ui_manager(
        Graphics_Window *p_graphics_window) {
    return p_graphics_window->p_ui_manager;
}

static inline
bool is_graphics_window_in_need_of__composition(
        Graphics_Window *p_gfx_window) {
    return p_gfx_window->graphics_window__flags
        & GRAPHICS_WINDOW__FLAG__COMPOSE__DIRTY
        ;
}

static inline
void set_graphics_window_as__in_need_of__composition(
        Graphics_Window *p_gfx_window) {
    p_gfx_window->graphics_window__flags |=
        GRAPHICS_WINDOW__FLAG__COMPOSE__DIRTY
        ;
}

static inline
void set_graphics_window_as__no_longer_needing__composition(
        Graphics_Window *p_gfx_window) {
    p_gfx_window->graphics_window__flags &=
        ~GRAPHICS_WINDOW__FLAG__COMPOSE__DIRTY
        ;
}

static inline
Camera *get_p_camera_from__graphics_window(
        Graphics_Window *p_graphics_window) {
    return p_graphics_window->p_camera;
}

static inline
void set_p_camera_of__graphics_window(
        Graphics_Window *p_graphics_window,
        Camera *p_camera) {
    p_graphics_window->p_camera = p_camera;
}

static inline
bool is_graphics_window__allocated(
        Graphics_Window *p_graphics_window) {
    return (bool)p_graphics_window->p_PLATFORM_gfx_window;
}

static inline
Vector__3i32 get_origin_3i32_of__graphics_window(
        Graphics_Window *p_graphics_window) {
    return p_graphics_window->origin_of__gfx_window;
}

static inline
Vector__3i32 get_position_3i32_of__graphics_window(
        Graphics_Window *p_graphics_window) {
    return p_graphics_window->position_of__gfx_window;
}

static inline
void set_position_3i32_of__graphics_window(
        Graphics_Window *p_graphics_window,
        Vector__3i32 position_of__gfx_window__3i32) {
    p_graphics_window->position_of__gfx_window =
        position_of__gfx_window__3i32;
}

static inline
Vector__3i32 get_position_maximum_3i32_of__graphics_window(
        Graphics_Window *p_graphics_window) {
    return p_graphics_window->position_of__gfx_window__maximum;
}

static inline
Vector__3i32 get_position_minimum_3i32_of__graphics_window(
        Graphics_Window *p_graphics_window) {
    return p_graphics_window->position_of__gfx_window__minimum;
}

static inline
Graphics_Window *get_p_child_of__graphics_window(
        Graphics_Window *p_graphics_window) {
    return p_graphics_window->p_child__graphics_window;
}

static inline
bool is_graphics_window_possessing__a_child(
        Graphics_Window *p_graphics_window) {
    return (bool)get_p_child_of__graphics_window(
            p_graphics_window);
}

static inline
bool is_graphics_window_a__child_of__this_graphics_window(
        Graphics_Window *p_graphics_window__child,
        Graphics_Window *p_graphics_window__parent) {
    return p_graphics_window__parent
        ->p_child__graphics_window =
        p_graphics_window__child;
}

static inline
bool is_graphics_window_of__this_kind(
        Graphics_Window *p_graphics_window,
        Graphics_Window_Kind the_kind_of__graphics_window) {
    return p_graphics_window->the_kind_of__window
        == the_kind_of__graphics_window;
}

static inline
bool is_graphics_window__rendering_world(
        Graphics_Window *p_gfx_window) {
    return p_gfx_window->graphics_window__flags
        & GRAPHICS_WINDOW__FLAG__IS_RENDERING_WORLD
        ;
}

static inline
void set_graphics_window_as__rendering_world(
        Graphics_Window *p_gfx_window) {
    p_gfx_window->graphics_window__flags |=
        GRAPHICS_WINDOW__FLAG__IS_RENDERING_WORLD
        ;
}

static inline
void set_graphics_window_as__NOT_rendering_world(
        Graphics_Window *p_gfx_window) {
    p_gfx_window->graphics_window__flags &=
        ~GRAPHICS_WINDOW__FLAG__IS_RENDERING_WORLD
        ;
}

#endif
