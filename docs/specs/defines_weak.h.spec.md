# Specification: core/include/defines_weak.h

## Overview

Provides forward declarations, base type aliases, utility macros, and
lightweight type definitions for the entire engine. This file is included
before `defines.h` to break circular dependencies and allow headers to
reference types without pulling in full definitions.

Every struct, enum, and typedef in `defines.h` should have a
corresponding forward declaration or lightweight definition here.

## Dependencies

- `<stdint.h>`, `<stdbool.h>`, `<stddef.h>`
- `types/implemented/*.h` (for platform-overridable enums)

## Key Contents

### Base Type Aliases

| Alias | Underlying Type | Description |
|-------|-----------------|-------------|
| `i64` | `int64_t` | 64-bit signed integer. |
| `i32` | `int32_t` | 32-bit signed integer. |
| `i16` | `int16_t` | 16-bit signed integer. |
| `i8` | `int8_t` | 8-bit signed integer. |
| `u64` | `uint64_t` | 64-bit unsigned integer. |
| `u32` | `uint32_t` | 32-bit unsigned integer. |
| `u16` | `uint16_t` | 16-bit unsigned integer. |
| `u8` | `uint8_t` | 8-bit unsigned integer. |

### Utility Macros

| Macro | Expansion | Description |
|-------|-----------|-------------|
| `BIT(n)` | `((1U) << (n))` | Single bit at position `n`. |
| `BIT__u64(n)` | `((1U) << ((u64)(n)))` | 64-bit single bit. |
| `NEXT_BIT(symbol)` | `(symbol << 1)` | Next bit after `symbol`. Used for flag chains. |
| `MASK(n)` | `((u32)BIT(n) - 1)` | Bitmask of `n` low bits. |
| `MASK__u64(n)` | `((u64)(BIT__u64(n) - 1))` | 64-bit bitmask. |
| `_STRING(x)` | `#x` | Stringification helper. |
| `STRING(x)` | `_STRING(x)` | Stringification with macro expansion. |

### Forward Declarations

All major engine structs are forward-declared here:

- `Entity`, `Game`, `World`, `Process`, `Process_Manager`
- `Input`, `Item`, `Item_Stack`, `Inventory`
- `Texture`, `Sprite`, `Scene`, `Scene_Manager`
- `Camera`, `Chunk`, `Tile`, `Global_Space`, `Local_Space`
- `Graphics_Window`, `UI_Element`, `UI_Manager`
- `TCP_Socket`, `TCP_Socket_Manager`, `IPv4_Address`
- `PLATFORM_*` types (file system, audio, gfx, texture, sprite)
- `Serialized_Field` and its aliases (`Serialized_Entity_Ptr`, etc.)
- `Game_Action`, `Serialization_Request`
- `Date_Time`, `Font_Letter`, `Font`, `Typer`

### Lightweight Type Definitions

Types small enough to define without circular dependency issues are
fully defined here:

- `Vector__3i32`, `Vector__3i32F4`, `Vector__3i32F20`
- `Vector__3i16`, `Vector__3i16F4`, `Vector__3i16F8`
- `Timer__u8`, `Timer__u16`, `Timer__u32`
- `Tile_Logic_Record`
- All `Process_Status_Kind`, `Process_Kind` enums
- `TCP_Socket_State` enum
- All `PLATFORM_*_Error` enums
- `IO_Access_Kind`, `Lavender_Type`
- `UI_Tile_Map_Size`, `UI_Tile_Kind`, `UI_Sprite_Kind`, `UI_Element_Kind`

### Function Pointer Typedefs

- `m_Entity_Handler`
- `m_Entity_Serialization_Handler`
- `m_Entity_Deserialization_Handler`

## Agentic Workflow

### Role in the Engine

`defines_weak.h` exists to break circular `#include` dependencies. It
provides just enough type information for headers to declare function
signatures and struct fields that use pointers to other engine types,
without requiring the full definitions.

### When to Include

Include `defines_weak.h` when:

- A header only needs type names for pointer declarations or function
  signatures.
- You want to avoid pulling in `platform.h` and all concrete definitions.

Include `defines.h` when:

- You need to access struct fields, `sizeof`, or use concrete type
  definitions.

### Synchronization with defines.h

**Every** new type, enum, or typedef added to `defines.h` **must** have
a corresponding forward declaration added to `defines_weak.h`. Failure
to do so will cause compilation errors in headers that include only
`defines_weak.h`.

### Extension Points

Like `defines.h`, extensible enums use the pattern:

    #include <types/implemented/entity_kind.h>
    #ifndef DEFINE_ENTITY_KIND
    typedef enum Entity_Kind { ... } Entity_Kind;
    #endif

The `types/implemented/*.h` headers can define `DEFINE_ENTITY_KIND` to
override the default enum with a project-specific version.

### Preconditions

- Must be includable without any other engine headers (only depends on
  standard library headers and `types/implemented/*.h`).

### Error Handling

None. This file is purely declarations and definitions with no runtime
behavior.
