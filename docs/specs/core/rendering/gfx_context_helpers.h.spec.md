# 1. Specification: core/include/rendering/gfx_context_helpers.h

## 1.1 Overview

Provides convenience `static inline` functions for common multi-step
graphics context operations — specifically allocating a `Graphics_Window`
together with a `UI_Manager` and/or sprite pool in a single call.

**WARNING:** This file contains stale references to
`allocate_sprite_pool_from__sprite_manager` and
`get_p_sprite_manager_from__gfx_context` which do not match current API
signatures. The sprite pool functions reference a `Sprite_Pool` type that
no longer exists. Functions using sprite pools may not compile and should
be considered **unstable/deprecated** until updated.

## 1.2 Dependencies

- `defines_weak.h` (forward declarations)
- `defines.h` (for all core types)
- `game.h` (for `Game`, `get_p_gfx_context_from__game`)
- `rendering/gfx_context.h` (for `Gfx_Context` accessors)
- `rendering/graphics_window.h` (for `Graphics_Window` operations)
- `rendering/graphics_window_manager.h` (for window allocation)
- `rendering/sprite_manager.h` (for sprite manager operations)

## 1.3 Functions

All functions are `static inline`.

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `GFX_CONTEXT_allocate_graphics_window_with__ui_manager` | `(Game*, Identifier__u32, Texture_Flags) -> Graphics_Window*` | `Graphics_Window*` | Allocates a graphics window and a UI manager for it. On failure, cleans up partial allocations. Returns null on failure. |
| `GFX_CONTEXT_allocate_graphics_window_with__ui_manager_and__sprite_pool` | `(Game*, Identifier__u32, Texture_Flags) -> Graphics_Window*` | `Graphics_Window*` | Allocates a graphics window with both a UI manager and a sprite pool. **WARNING:** references `allocate_sprite_pool_from__sprite_manager` which does not exist in the current API. |
| `GFX_CONTEXT_allocate_graphics_window_with__sprite_pool` | `(Game*, Identifier__u32, Texture_Flags) -> Graphics_Window*` | `Graphics_Window*` | Allocates a graphics window with a sprite pool only. **WARNING:** same stale API reference as above. |

## 1.4 Agentic Workflow

### 1.4.1 Deprecation Notice

Only `GFX_CONTEXT_allocate_graphics_window_with__ui_manager` is functional.
The sprite pool variants reference a removed API. Prefer using
`allocate_sprite_manager_for__graphics_window` (from `graphics_window.h`)
directly after window allocation.

### 1.4.2 Error Handling

- All functions call `debug_error` on allocation failure and clean up partial allocations before returning null.

## 1.5 Header Guard

`GRAPHICS_CONTEXT_HELPERS_H`
