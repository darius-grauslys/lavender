# 1. Sprite Manager Specification

## 1.1 File
`core/include/rendering/sprite_manager.h`

## 1.2 Purpose
Manages a pool of `Sprite` instances associated with a single
`Graphics_Window`. Provides allocation, deallocation, lookup, and batch
rendering of sprites.

## 1.3 Dependencies
| Header | Purpose |
|--------|---------|
| `defines.h` | `Sprite_Manager`, `Sprite`, `Gfx_Context`, `Graphics_Window` |
| `defines_weak.h` | Forward declarations |
| `rendering/sprite.h` | `Sprite` operations |
| `types/implemented/sprite_animation_group_kind.h` | `Sprite_Animation_Group_Kind` |
| `types/implemented/sprite_animation_kind.h` | `Sprite_Animation_Kind` |

## 1.4 Types

### 1.4.1 `Sprite_Manager` (defined in `defines.h`)
