# Texture Specification

## File
`core/include/rendering/texture.h`

## Purpose
Provides inline helper functions for querying and mutating `Texture` and
`Texture_Flags` values. Textures are the fundamental image resource type in
the engine, wrapping a platform-specific `PLATFORM_Texture` pointer with
engine-managed flags that encode size, format, render method, visibility,
and read-only state.

## Dependencies
| Header | Purpose |
|--------|---------|
| `defines_weak.h` | Forward declarations, `Texture_Flags` typedef |
| `defines.h` | `Texture` struct, all `TEXTURE_FLAG__*` macros |

## Types

### `Texture` (defined in `defines.h`)
