# Specification: core/include/rendering/gfx_context.h

## Overview

Provides initialization and `static inline` accessor functions for
`Gfx_Context` — the top-level graphics state container that aggregates all
rendering subsystems.

## Dependencies

- `defines.h` (for `Gfx_Context` and all sub-component types)
- `defines_weak.h` (forward declarations)

## Types

### Gfx_Context (struct)

    typedef struct Gfx_Context_t {
        Graphics_Window_Manager graphics_window_manager;
        Aliased_Texture_Manager aliased_texture_manager;
        UI_Context ui_context;
        UI_Tile_Map_Manager ui_tile_map_manager;
        Font_Manager font_manager;
        PLATFORM_Gfx_Context *p_PLATFORM_gfx_context;
        Sprite_Context sprite_context;
    } Gfx_Context;

| Field | Type | Description |
|-------|------|-------------|
| `graphics_window_manager` | `Graphics_Window_Manager` | Window pool and priority ordering. |
| `aliased_texture_manager` | `Aliased_Texture_Manager` | Named texture pool. |
| `ui_context` | `UI_Context` | UI manager pool and window record registry. |
| `ui_tile_map_manager` | `UI_Tile_Map_Manager` | Tile map pool (small/medium/large). |
| `font_manager` | `Font_Manager` | Font pool. |
| `p_PLATFORM_gfx_context` | `PLATFORM_Gfx_Context*` | Platform-specific graphics context. |
| `sprite_context` | `Sprite_Context` | Sprite manager pool and animation registries. |

## Functions

### Initialization

| Function | Signature | Description |
|----------|-----------|-------------|
| `initialize_gfx_context` | `(Gfx_Context*) -> void` | Initializes all sub-components: graphics window manager, aliased texture manager, UI context, UI tile map manager, font manager, and sprite context. |

### Accessors (static inline)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `get_p_PLATFORM_gfx_context_from__gfx_context` | `(Gfx_Context*) -> PLATFORM_Gfx_Context*` | `PLATFORM_Gfx_Context*` | Returns `p_PLATFORM_gfx_context`. |
| `get_p_aliased_texture_manager_from__gfx_context` | `(Gfx_Context*) -> Aliased_Texture_Manager*` | `Aliased_Texture_Manager*` | Returns `&aliased_texture_manager`. |
| `get_p_ui_context_from__gfx_context` | `(Gfx_Context*) -> UI_Context*` | `UI_Context*` | Returns `&ui_context`. |
| `get_p_ui_tile_map_manager_from__gfx_context` | `(Gfx_Context*) -> UI_Tile_Map_Manager*` | `UI_Tile_Map_Manager*` | Returns `&ui_tile_map_manager`. |
| `get_p_graphics_window_manager_from__gfx_context` | `(Gfx_Context*) -> Graphics_Window_Manager*` | `Graphics_Window_Manager*` | Returns `&graphics_window_manager`. |
| `get_p_font_manager_from__gfx_context` | `(Gfx_Context*) -> Font_Manager*` | `Font_Manager*` | Returns `&font_manager`. |
| `get_p_sprite_context_from__gfx_context` | `(Gfx_Context*) -> Sprite_Context*` | `Sprite_Context*` | Returns `&sprite_context`. |

## Agentic Workflow

### Ownership

Owned by `Game` (at `game.gfx_context`). Accessed via
`get_p_gfx_context_from__game` (see `game.h`). Contains all rendering
subsystem managers.

### Preconditions

- All functions require non-null `p_gfx_context`.

## Header Guard

`GFX_CONTEXT_H`
