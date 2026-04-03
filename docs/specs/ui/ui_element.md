# UI Element Specification

## File
`core/include/ui/ui_element.h`

## Purpose
Defines the core operations on `UI_Element` — the fundamental building block
of the UI system. A `UI_Element` is a polymorphic UI node that can act as a
button, slider, draggable, drop zone, text field, text box, window element,
or logical grouping. Elements form a tree via `p_parent`/`p_child` pointers
and a linked list via `p_next` pointers.

Each element has event handler function pointers (clicked, dragged, dropped,
held, typed, transformed, composed, disposed) and is identified by a
`Serialization_Header` UUID. Spatial data (position, size) is stored in an
externally-managed `Hitbox_AABB` looked up by UUID.

## Dependencies
| Header | Purpose |
|--------|---------|
| `defines.h` | `UI_Element`, `UI_Flags__u16`, handler typedefs, all core types |
| `defines_weak.h` | Forward declarations |
| `collisions/core/aabb/hitbox_aabb.h` | `Hitbox_AABB` position/size accessors |
| `collisions/core/aabb/hitbox_aabb_manager.h` | UUID-based hitbox lookup |
| `numerics.h` | Fixed-point arithmetic helpers |
| `platform.h` | Platform function signatures |
| `serialization/identifiers.h` | UUID utilities |
| `serialization/serialization_header.h` | `GET_UUID_P`, `IS_DEALLOCATED_P` macros |
| `vectors.h` | `Vector__3i32`, `Vector__3i32F4` operations |

## Types

### `UI_Element` (defined in `defines.h`)
