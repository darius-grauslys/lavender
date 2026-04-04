# Sprite Manager Specification

## File
`core/include/rendering/sprite_manager.h`

## Purpose
Manages a pool of `Sprite` instances associated with a single
`Graphics_Window`. Provides allocation, deallocation, lookup, and batch
rendering of sprites.

## Dependencies
| Header | Purpose |
|--------|---------|
| `defines.h` | `Sprite_Manager`, `Sprite`, `Gfx_Context`, `Graphics_Window` |
| `defines_weak.h` | Forward declarations |
| `rendering/sprite.h` | `Sprite` operations |
| `types/implemented/sprite_animation_group_kind.h` | `Sprite_Animation_Group_Kind` |
| `types/implemented/sprite_animation_kind.h` | `Sprite_Animation_Kind` |

## Types

### `Sprite_Manager` (defined in `defines.h`)
