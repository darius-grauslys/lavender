# Specification: core/include/rendering/sprite_context.h

## Overview

Manages the collection of `Sprite_Manager` instances and the global
registries of `Sprite_Animation` and `Sprite_Animation_Group_Set` entries.
Provides allocation/deallocation of sprite managers and lookup/registration
of animation definitions.

## Dependencies

- `defines.h` (for `Sprite_Context`, `Sprite_Manager`, `Sprite_Animation`, `Sprite_Animation_Group_Set`)
- `defines_weak.h` (forward declarations)
- `serialization/hashing.h` (for `dehash_identitier_u32_in__contigious_array`)

## Types

### Sprite_Context (struct)

    typedef struct Sprite_Context_t {
        Sprite_Animation sprite_animations[Sprite_Animation_Kind__Unknown];
        Sprite_Manager *pM_sprite_managers;
        Sprite_Animation_Group_Set sprite_animation_groups[
            Sprite_Animation_Group_Kind__Unknown];
        Quantity__u8 max_quantity_of__sprite_managers;
    } Sprite_Context;

| Field | Type | Description |
|-------|------|-------------|
| `sprite_animations` | `Sprite_Animation[]` | Global registry indexed by `Sprite_Animation_Kind`. |
| `pM_sprite_managers` | `Sprite_Manager*` | Heap-allocated array of `Sprite_Manager` instances. |
| `sprite_animation_groups` | `Sprite_Animation_Group_Set[]` | Global registry indexed by `Sprite_Animation_Group_Kind`. |
| `max_quantity_of__sprite_managers` | `Quantity__u8` | Maximum sprite managers in pool. |

## Functions

### Initialization and Memory

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `initialize_sprite_context` | `(Sprite_Context*) -> void` | `void` | Initializes to empty state. Does not allocate sprite managers. |
| `allocate_sprite_managers_from__sprite_context` | `(Sprite_Context*, Quantity__u8) -> bool` | `bool` | Heap-allocates the sprite manager pool. Returns `true` on success. |
| `release_sprite_managers_from__sprite_context` | `(Sprite_Context*) -> void` | `void` | Frees the sprite manager pool. |

### Sprite Manager Allocation

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `allocate_sprite_manager_from__sprite_context` | `(Sprite_Context*, Identifier__u32, Quantity__u32) -> Sprite_Manager*` | `Sprite_Manager*` | Allocates a `Sprite_Manager` with the given UUID and sprite capacity. Returns null on failure. |
| `release_sprite_manager_from__sprite_context` | `(Sprite_Context*, Sprite_Manager*) -> void` | `void` | Releases a sprite manager back to the pool. |

### Queries (static inline)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `is_sprite_managers_allocated_in__sprite_context` | `(Sprite_Context*) -> bool` | `bool` | True if `pM_sprite_managers` is non-null. |
| `get_p_sprite_manager_by__uuid_from__sprite_context` | `(Sprite_Context*, Identifier__u32) -> Sprite_Manager*` | `Sprite_Manager*` | Looks up a sprite manager by UUID via `dehash_identitier_u32_in__contigious_array`. |

### Animation Registration (static inline)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `register_sprite_animation_into__sprite_context` | `(Sprite_Context*, Sprite_Animation_Kind, Sprite_Animation) -> void` | `void` | Registers an animation definition at the given kind index. Debug bounds-checked. |
| `get_sprite_animation_from__sprite_context` | `(Sprite_Context*, Sprite_Animation_Kind) -> Sprite_Animation` | `Sprite_Animation` | Returns the animation definition by value. Debug bounds-checked. |

### Animation Group Registration (static inline)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `register_sprite_animation_group_into__sprite_context` | `(Sprite_Context*, Sprite_Animation_Group_Kind, Sprite_Animation_Group_Set) -> void` | `void` | Registers an animation group set. Debug bounds-checked. |
| `get_sprite_animation_group_from__sprite_context` | `(Sprite_Context*, Sprite_Animation_Group_Kind) -> Sprite_Animation_Group_Set` | `Sprite_Animation_Group_Set` | Returns by value. Debug bounds-checked. |
| `get_p_sprite_animation_group_from__sprite_context` | `(Sprite_Context*, Sprite_Animation_Group_Kind) -> Sprite_Animation_Group_Set*` | `Sprite_Animation_Group_Set*` | Returns pointer for mutation. Debug bounds-checked. |

## Agentic Workflow

### Ownership

Owned by `Gfx_Context` (at `gfx_context.sprite_context`). Accessed via
`get_p_sprite_context_from__gfx_context`. Animation registry populated by
`register_sprite_animations` (see `implemented/sprite_animation_registrar.h`).

### Preconditions

- All functions require non-null `p_sprite_context`.
- Registration functions: kind must be less than `*__Unknown`.

### Error Handling

- Debug builds call `debug_error` on null pointers and out-of-bounds kind values.

## Header Guard

`SPRITE_CONTEXT_H`
