# Aliased Texture Manager Specification

## File
`core/include/rendering/aliased_texture_manager.h`

## Purpose
Manages a pool of `Aliased_Texture` instances, providing allocation,
lookup (by name or UUID), and release of named textures. This is the
primary API for loading and accessing textures by human-readable names
at runtime.

## Dependencies
| Header | Purpose |
|--------|---------|
| `defines.h` | `Aliased_Texture_Manager`, `Aliased_Texture`, `Texture`, `Texture_Flags` |
| `defines_weak.h` | Forward declarations |

## Types

### `Aliased_Texture_Manager` (defined in `defines.h`)
