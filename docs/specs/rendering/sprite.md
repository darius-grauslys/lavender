# Sprite Specification

## File
`core/include/rendering/sprite.h`

## Purpose
Defines operations on `Sprite` — the engine's representation of a renderable
animated image. A sprite wraps a platform-specific `PLATFORM_Sprite`, a
sampling texture, an output texture, animation state, and rendering flags.

## Dependencies
| Header | Purpose |
|--------|---------|
| `defines_weak.h` | Forward declarations |
| `defines.h` | `Sprite`, `Sprite_Flags`, `Sprite_Animation`, all flag macros |
| `platform.h` | `PLATFORM_allocate_sprite`, `PLATFORM_release_sprite` |
| `rendering/texture.h` | `Texture` operations |
| `serialization/serialization_header.h` | `IS_DEALLOCATED_P` macro |
| `types/implemented/sprite_animation_group_kind.h` | `Sprite_Animation_Group_Kind` enum |
| `types/implemented/sprite_animation_kind.h` | `Sprite_Animation_Kind` enum |

## Types

### `Sprite` (defined in `defines.h`)
