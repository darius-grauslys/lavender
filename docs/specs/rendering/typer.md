# Typer Specification

## File
`core/include/rendering/font/typer.h`

## Purpose
Defines operations on `Typer` — a text layout engine that renders character
strings into either a `Texture` or a `PLATFORM_Graphics_Window` using a
`Font`. The typer maintains a bounding box, cursor position, and line
spacing for text wrapping.

## Dependencies
| Header | Purpose |
|--------|---------|
| `defines_weak.h` | Forward declarations |
| `defines.h` | `Typer`, `Font`, `Font_Letter`, `Hitbox_AABB`, `Texture`, `PLATFORM_Graphics_Window` |
| `collisions/core/aabb/hitbox_aabb.h` | `set_hitbox_aabb__position_with__3i32`, `set_size_of__hitbox_aabb` |
| `vectors.h` | `Vector__3i32`, `get_vector__3i32` |

## Types

### `Typer` (defined in `defines.h`)
