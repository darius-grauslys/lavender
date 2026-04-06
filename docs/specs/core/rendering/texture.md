# 1. Texture Specification

## 1.1 File
`core/include/rendering/texture.h`

## 1.2 Purpose
Provides inline helper functions for querying and mutating `Texture` and
`Texture_Flags` values. Textures are the fundamental image resource type in
the engine, wrapping a platform-specific `PLATFORM_Texture` pointer with
engine-managed flags that encode size, format, render method, visibility,
and read-only state.

## 1.3 Dependencies
| Header | Purpose |
|--------|---------|
| `defines_weak.h` | Forward declarations, `Texture_Flags` typedef |
| `defines.h` | `Texture` struct, all `TEXTURE_FLAG__*` macros |

## 1.4 Types

### 1.4.1 `Texture` (defined in `defines.h`)
