# 1. Aliased Texture Manager Specification

## 1.1 File
`core/include/rendering/aliased_texture_manager.h`

## 1.2 Purpose
Manages a pool of `Aliased_Texture` instances, providing allocation,
lookup (by name or UUID), and release of named textures. This is the
primary API for loading and accessing textures by human-readable names
at runtime.

## 1.3 Dependencies
| Header | Purpose |
|--------|---------|
| `defines.h` | `Aliased_Texture_Manager`, `Aliased_Texture`, `Texture`, `Texture_Flags` |
| `defines_weak.h` | Forward declarations |

## 1.4 Types

### 1.4.1 `Aliased_Texture_Manager` (defined in `defines.h`)
