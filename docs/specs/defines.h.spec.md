# Specification: core/include/defines.h

## Overview

Central definition file for the entire engine. Contains the definition of
**every** struct, macro, typedef, and enum used in the core engine. This
is the single authoritative source for all engine data types.

Types are organized by primary usage area (audio, collisions, rendering,
entity, world, UI, etc.) and are referenced throughout the codebase via
`#include <defines.h>`.

This file is extremely large by design — it serves as the engine's type
registry, ensuring all types are defined in one place with forward
declarations in `defines_weak.h`.

## Dependencies

- `platform.h` (for `PLATFORM_*` types and function declarations)
- `platform_defaults.h` (for compile-time configuration constants)
- `types/implemented/*.h` (for platform-overridable enum and struct types)
- `util/bitmap/bitmap.h` (for `BITMAP` and `BITMAP_AND_HEAP` macros)
- `<stdbool.h>`, `<stdint.h>`
- `debug/debug.h` (in debug builds)
- `defines_weak.h` (forward declarations)

## Sections

The file is organized into the following sections, each marked with a
`SECTION_<name>` comment:

| Section | Description |
|---------|-------------|
| `SECTION_defines` | Base numeric types, fixed-point types, angles, directions, identifiers, indices, quantities, vectors, random, date/time, rays. |
| `SECTION_serialization` | `Serialization_Header`, `Serialization_Pool`, `Serialized_Field`, `Serialization_Request` and associated flags. |
| `SECTION_audio` | `Audio_Effect`, `Audio_Flags__u8`. |
| `SECTION_collisions` | `Hitbox_AABB`, `Hitbox_Context`, `Hitbox_Manager_*`, `Collision_Node`, `Collision_Node_Pool`. |
| `SECTION_rendering` | `Texture_Flags` bit layout, `Texture`, `Sprite`, `Sprite_Animation`, `Sprite_Manager`, `Sprite_Context`, `Font`, `Typer`, `Log`, `Message`, `Aliased_Texture_Manager`. |
| `SECTION_inventory` | `Item`, `Item_Stack`, `Inventory`, `Inventory_Manager`, `Item_Stack_Manager`. |
| `SECTION_entity` | `Entity`, `Entity_Data`, `Entity_Functions`, `Entity_Manager`, entity flags. |
| `SECTION_input` | `Input`, `Input_Code__u32`, `Input_Flags__u32`. |
| `SECTION_multiplayer` | `Session_Token`, `IPv4_Address`, `TCP_Packet`, `TCP_Socket`, `TCP_Socket_Manager`. |
| `SECTION_process` | `Process`, `Process_Manager`, `Process_Table`. |
| `SECTION_scene` | `Scene`, `Scene_Manager`. |
| `SECTION_sort` | `Sort_Node`, `Sort_List`, `Sort_List_Manager`, `Sort_Data`. |
| `SECTION_ui` | `UI_Element`, `UI_Manager`, `UI_Tile_*`, `UI_Context`. |
| `SECTION_world` | `Camera`, `Chunk`, `Tile`, `Global_Space`, `Local_Space`, `World`, `Region`, `Structure`, `Room`, `Path`, `Game_Action`, `Client`. |
| `SECTION_gfx_window` | `Graphics_Window`, `Graphics_Window_Manager`. |
| `SECTION_core` | `Gfx_Context`, `Game`. |

## Key Type Families

### Fixed-Point Numeric Types

| Type | Base | Fractional Bits | Description |
|------|------|-----------------|-------------|
| `i32F4` | `int32_t` | 4 | Primary position/velocity type. |
| `i32F8` | `int32_t` | 8 | Higher-precision intermediate calculations. |
| `i32F20` | `int32_t` | 20 | Ray casting, high-precision angles. |
| `u32F20` | `uint32_t` | 20 | Unsigned high-precision (time elapsed). |
| `i16F4` | `int16_t` | 4 | Compact position type. |
| `i16F8` | `int16_t` | 8 | Acceleration components. |

### Vector Types

| Type | Components | Description |
|------|------------|-------------|
| `Vector__3i32` | `x__i32, y__i32, z__i32` | Integer 3D vector. Also aliased as `Chunk_Vector__3i32`, `Tile_Vector__3i32`, `Global_Space_Vector__3i32`. |
| `Vector__3i32F4` | `x__i32F4, y__i32F4, z__i32F4` | Fixed-point 3D vector (4-bit fractional). Primary position type. |
| `Vector__3i32F20` | `x__i32F20, y__i32F20, z__i32F20` | High-precision 3D vector. Used in ray casting. |
| `Vector__3i16F8` | `x__i16F8, y__i16F8, z__i16F8` | Compact acceleration vector. |
| `Vector__3u8` | `x__u8, y__u8, z__u8` | Unsigned byte vector. Local tile coordinates. |

### Identifier and Index Types

| Type | Width | Sentinel | Description |
|------|-------|----------|-------------|
| `Identifier__u32` | 32 | `IDENTIFIER__UNKNOWN__u32` | Primary UUID type. |
| `Identifier__u16` | 16 | `IDENTIFIER__UNKNOWN__u16` | Compact UUID. |
| `Index__u32` | 32 | `INDEX__UNKNOWN__u32` | Array index. |
| `Index__u16` | 16 | `INDEX__UNKNOWN__u16` | Compact array index. |
| `Index__u8` | 8 | `INDEX__UNKNOWN__u8` | Byte-sized index. |

## Agentic Workflow

### Role in the Engine

`defines.h` is the **type registry** for the entire engine. Every
subsystem includes it (directly or transitively) to access type
definitions. It is the single source of truth for:

- All struct layouts
- All enum definitions
- All flag constants
- All compile-time limits (`MAX_QUANTITY_OF__*`)

### Include Order

    platform_defines.h  (backend-specific PLATFORM_* structs)
         |
    platform_defaults.h (compile-time constants with defaults)
         |
    platform.h          (PLATFORM_* function declarations)
         |
    defines_weak.h      (forward declarations)
         |
    defines.h           (full type definitions)

### Extending defines.h

When adding a new type:

1. Add the full definition in the appropriate `SECTION_*` block.
2. Add a forward declaration in `defines_weak.h`.
3. If the type is platform-overridable, create a
   `types/implemented/<type>.h` header with a `#define DEFINE_<TYPE>`
   guard.

### Platform-Overridable Types

Several types can be overridden by platform implementations via
`types/implemented/*.h` headers:

- `Entity_Data`, `Entity_Functions`, `Entity_Kind`
- `Tile`, `Tile_Kind`
- `Item_Data`, `Item_Kind`
- `UI_Element_Data`, `UI_Element_Kind`
- `Scene_Kind`, `Graphics_Window_Kind`
- `Sprite_Kind`, `Sprite_Animation_Kind`, `Sprite_Animation_Group_Kind`
- `Audio_Effect_Kind`, `Audio_Stream_Kind`
- `Chunk_Generator_Kind`
- `Hitbox_Manager_Type`

The pattern is:

    #include <types/implemented/entity_kind.h>
    #ifndef DEFINE_ENTITY_KIND
    typedef enum Entity_Kind { ... } Entity_Kind;
    #endif

### Naming Conventions

| Pattern | Meaning |
|---------|---------|
| `*__u8`, `*__u16`, `*__u32` | Unsigned integer of specified width. |
| `*__i32`, `*__i16` | Signed integer of specified width. |
| `*F4`, `*F8`, `*F20` | Fixed-point with N fractional bits. |
| `*_Flags__uN` | Bitfield flags type. |
| `m_*` | Method/handler function pointer (invoked by the engine). |
| `f_*` | Function pointer (user-provided callback). |
| `pM_*` | Managed pointer (allocated/freed by a manager). |
| `p_*` | Non-owning pointer. |
| `pV_*` | Void/opaque pointer. |

### Preconditions

- `platform_defines.h` must exist and define `PLATFORM_DEFINES_H`.
  Without it, compilation fails with `#error`.
- All `types/implemented/*.h` headers must exist, even if they only
  contain the default definitions.

### Error Handling

- Missing platform defines trigger a `#error` at compile time.
- `PROCESS_MAX_PRIORITY_LEVEL` is validated at compile time to be
  in range `[1, 255]`.
- No runtime error handling in this file (it is purely definitions).
