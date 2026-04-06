# 1. Graphics Window Specification

## 1.1 File
`core/include/rendering/graphics_window.h`

## 1.2 Purpose
Defines operations on `Graphics_Window` — the engine's abstraction for a
renderable surface that can contain UI elements, sprites, tile maps, and
world rendering. Graphics windows form a parent-child hierarchy and can
own or share `UI_Manager`, `Sprite_Manager`, and hitbox manager instances.

## 1.3 Dependencies
| Header | Purpose |
|--------|---------|
| `defines_weak.h` | Forward declarations |
| `defines.h` | `Graphics_Window`, all sub-component types |
| `game.h` | `Game` type, `get_p_gfx_context_from__game`, `get_p_hitbox_context_from__game` |
| `rendering/gfx_context.h` | `Gfx_Context` accessors |
| `rendering/graphics_window_manager.h` | Manager operations, parent lookup |
| `rendering/sprite_context.h` | `Sprite_Context` accessors, sprite manager lookup |
| `rendering/sprite_manager.h` | `Sprite_Manager` operations |
| `serialization/identifiers.h` | `is_identifier_u32__invalid`, `IDENTIFIER__UNKNOWN__u32` |
| `serialization/serialization_header.h` | `GET_UUID_P`, `IS_DEALLOCATED_P` |
| `types/implemented/graphics_window_kind.h` | `Graphics_Window_Kind` enum |
| `types/implemented/hitbox_manager_type.h` | `Hitbox_Manager_Type` enum |
| `ui/ui_context.h` | `UI_Context` accessors, `get_p_ui_manager_by__uuid_from__ui_context` |
| `vectors.h` | `Vector__3i32`, `VECTOR__3i32__OUT_OF_BOUNDS` |
| `collisions/hitbox_context.h` | `Hitbox_Context` accessors, hitbox manager lookup |

## 1.4 Types

### 1.4.1 `Graphics_Window` (defined in `defines.h`)
