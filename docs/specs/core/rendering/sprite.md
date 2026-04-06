# 1. Sprite Specification

## 1.1 File
`core/include/rendering/sprite.h`

## 1.2 Purpose
Defines operations on `Sprite` — the engine's representation of a renderable
animated image. A sprite wraps a platform-specific `PLATFORM_Sprite`, a
sampling texture, an output texture, animation state, and rendering flags.

## 1.3 Dependencies
| Header | Purpose |
|--------|---------|
| `defines_weak.h` | Forward declarations |
| `defines.h` | `Sprite`, `Sprite_Flags`, `Sprite_Animation`, all flag macros |
| `platform.h` | `PLATFORM_allocate_sprite`, `PLATFORM_release_sprite` |
| `rendering/texture.h` | `Texture` operations |
| `serialization/serialization_header.h` | `IS_DEALLOCATED_P` macro |
| `types/implemented/sprite_animation_group_kind.h` | `Sprite_Animation_Group_Kind` enum |
| `types/implemented/sprite_animation_kind.h` | `Sprite_Animation_Kind` enum |

## 1.4 Types

### 1.4.1 `Sprite` (defined in `defines.h`)
