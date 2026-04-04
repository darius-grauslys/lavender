# Specification: core/include/rendering/sprite_manager.h

## Overview

Manages a pool of `Sprite` instances associated with a single
`Graphics_Window`. Provides allocation, deallocation, lookup, and batch
rendering of sprites.

## Dependencies

- `defines.h` (for `Sprite_Manager`, `Sprite`, `Gfx_Context`, `Graphics_Window`)
- `defines_weak.h` (forward declarations)
- `rendering/sprite.h` (for `Sprite` operations)
- `types/implemented/sprite_animation_group_kind.h` (for `Sprite_Animation_Group_Kind`)
- `types/implemented/sprite_animation_kind.h` (for `Sprite_Animation_Kind`)

## Types

### Sprite_Manager (struct)

    typedef struct Sprite_Manager_t {
        Serialization_Header _serialization_header;
        Sprite *pM_pool_of__sprites;
        Sprite_Render_Record *pM_sprite_render_records;
        Sprite_Render_Record *p_sprite_render_record__last;
        Quantity__u32 max_quantity_of__sprites;
    } Sprite_Manager;

| Field | Type | Description |
|-------|------|-------------|
| `_serialization_header` | `Serialization_Header` | UUID for pool management. |
| `pM_pool_of__sprites` | `Sprite*` | Heap-allocated array of `Sprite` instances. |
| `pM_sprite_render_records` | `Sprite_Render_Record*` | Heap-allocated render record array. |
| `p_sprite_render_record__last` | `Sprite_Render_Record*` | Points past the last active render record. |
| `max_quantity_of__sprites` | `Quantity__u32` | Maximum sprites this manager can hold. |

### Sprite_Render_Record (struct)

    typedef struct Sprite_Render_Record_t {
        Vector__3i32F4 position__3i32F4;
        Sprite *p_sprite;
    } Sprite_Render_Record;

Used to batch sprite rendering with position data.

## Functions

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `initialize_sprite_manager` | `(Sprite_Manager*) -> void` | `void` | Initializes to empty state. Does not allocate pool. |
| `allocate_sprite_manager__members` | `(Sprite_Manager*, Quantity__u32) -> bool` | `bool` | Heap-allocates sprite pool and render record arrays. Returns `true` on success, `false` on failure. |
| `allocate_sprite_from__sprite_manager` | `(Gfx_Context*, Sprite_Manager*, Graphics_Window*, Identifier__u32, Texture, Texture_Flags) -> Sprite*` | `Sprite*` | Allocates a sprite from the pool with the given UUID, sampling texture, and sprite texture flags. Returns null on failure. |
| `release_sprite_from__sprite_manager` | `(Gfx_Context*, Sprite_Manager*, Sprite*) -> void` | `void` | Releases a sprite back to the pool and frees its `PLATFORM_Sprite`. |
| `get_p_sprite_by__uuid_from__sprite_manager` | `(Sprite_Manager*, Identifier__u32) -> Sprite*` | `Sprite*` | Finds a sprite by UUID. Returns null if not found. |
| `render_sprites_in__sprite_manager` | `(Game*, Sprite_Context*, Sprite_Manager*, Graphics_Window*) -> void` | `void` | Renders all enabled sprites via `PLATFORM_render_sprite`. |

## Agentic Workflow

### Ownership

Managed by `Sprite_Context` (see `sprite_context.h`). Associated with a
`Graphics_Window` via `uuid_of__sprite_manager`. Allocated for a graphics
window via `allocate_sprite_manager_for__graphics_window` (see
`graphics_window.h`).

### Preconditions

- All functions require non-null pointers.
- `allocate_sprite_from__sprite_manager`: pool must have been allocated via `allocate_sprite_manager__members`.

## Header Guard

`SPRITE_POOL_H`
