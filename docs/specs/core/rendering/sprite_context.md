# 1. Sprite Context Specification

## 1.1 File
`core/include/rendering/sprite_context.h`

## 1.2 Purpose
Manages the collection of `Sprite_Manager` instances and the global
registries of `Sprite_Animation` and `Sprite_Animation_Group_Set` entries.
Provides allocation/deallocation of sprite managers and lookup/registration
of animation definitions.

## 1.3 Dependencies
| Header | Purpose |
|--------|---------|
| `defines.h` | `Sprite_Context`, `Sprite_Manager`, `Sprite_Animation`, `Sprite_Animation_Group_Set` |
| `defines_weak.h` | Forward declarations |
| `serialization/hashing.h` | `dehash_identitier_u32_in__contigious_array` for UUID lookup |

## 1.4 Types

### 1.4.1 `Sprite_Context` (defined in `defines.h`)
