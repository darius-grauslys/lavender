# 1. Graphics Context Helpers Specification

## 1.1 File
`core/include/rendering/gfx_context_helpers.h`

## 1.2 Purpose
Provides convenience `static inline` functions for common multi-step
graphics context operations at the Lavender CORE level — specifically
allocating a `Graphics_Window` together with a `UI_Manager` and/or
sprite pool in a single call.

**WARNING:** This file contains stale references to
`allocate_sprite_pool_from__sprite_manager` and
`get_p_sprite_manager_from__gfx_context` which do not match current API
signatures. The sprite pool functions reference a `Sprite_Pool` type that
no longer exists. This file may not compile and should be considered
**unstable/deprecated** until updated.

## 1.3 Dependencies
| Header | Purpose |
|--------|---------|
| `defines_weak.h` | Forward declarations |
| `defines.h` | All core types |
| `game.h` | `Game`, `get_p_gfx_context_from__game` |
| `rendering/gfx_context.h` | `Gfx_Context` accessors |
| `rendering/graphics_window.h` | `Graphics_Window` operations |
| `rendering/graphics_window_manager.h` | Window allocation |
| `rendering/sprite_manager.h` | Sprite manager operations |

## 1.4 Functions

### 1.4.1 `GFX_CONTEXT_allocate_graphics_window_with__ui_manager`
