# Specification: core/include/collisions/hitbox.h

## Overview

Provides flag manipulation utilities for the `Hitbox_Flags__u8` type — a
compact bitfield that tracks the runtime state of any hitbox regardless of
its concrete type (AABB, AAABBB, etc.).

These are the lowest-level building blocks for hitbox state management. They
are consumed by concrete hitbox types (e.g. `Hitbox_AABB`) which wrap them
in type-specific inline accessors.

## Dependencies

- `defines.h` (for `Hitbox_Flags__u8`, `HITBOX_FLAG__IS_DIRTY`,
  `HITBOX_FLAG__IS_ACTIVE`)

## Types

### Hitbox_Flags__u8 (typedef u8)

Defined in `defines.h`:

    typedef u8 Hitbox_Flags__u8;

| Flag | Bit | Description |
|------|-----|-------------|
| `HITBOX_FLAG__IS_ACTIVE` | 0 | If set, the hitbox is participating in collision detection. |
| `HITBOX_FLAG__IS_DIRTY` | 1 | If set, the hitbox's spatial data has been modified since last poll. |

| Constant | Value | Description |
|----------|-------|-------------|
| `HITBOX_FLAGS__NONE` | 0 | No flags set. |

## Functions

All functions in this header are `static inline`.

### Dirty Flag Management

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `is_hitbox_flags__dirty` | `(Hitbox_Flags__u8*) -> bool` | `bool` | Returns true if `HITBOX_FLAG__IS_DIRTY` is set. |
| `set_hitbox_flags_as__dirty` | `(Hitbox_Flags__u8*) -> bool` | `bool` | Sets `HITBOX_FLAG__IS_DIRTY`. Returns the resulting flags. |
| `set_hitbox_flags_as__not_dirty` | `(Hitbox_Flags__u8*) -> bool` | `bool` | Clears `HITBOX_FLAG__IS_DIRTY`. Returns the resulting flags. |

### Active Flag Management

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `is_hitbox_flags__active` | `(Hitbox_Flags__u8*) -> bool` | `bool` | Returns true if `HITBOX_FLAG__IS_ACTIVE` is set. |
| `set_hitbox_flags_as__active` | `(Hitbox_Flags__u8*) -> bool` | `bool` | Sets `HITBOX_FLAG__IS_ACTIVE`. Returns the resulting flags. |
| `set_hitbox_flags_as__disabled` | `(Hitbox_Flags__u8*) -> bool` | `bool` | Clears `HITBOX_FLAG__IS_ACTIVE`. Returns the resulting flags. |

## Agentic Workflow

### Flag Lifecycle

    [HITBOX_FLAGS__NONE]
        |
        set_hitbox_flags_as__active
        |
    [IS_ACTIVE]
        |
        (position/velocity/acceleration modified)
        set_hitbox_flags_as__dirty
        |
    [IS_ACTIVE | IS_DIRTY]
        |
        (collision resolver polls and processes)
        set_hitbox_flags_as__not_dirty
        |
    [IS_ACTIVE]
        |
        set_hitbox_flags_as__disabled
        |
    [HITBOX_FLAGS__NONE]

### Usage Pattern

These functions operate on a `Hitbox_Flags__u8*` pointer, not on a concrete
hitbox struct. Concrete hitbox types (e.g. `Hitbox_AABB`) provide their own
inline wrappers that extract the flags pointer from the struct:

    // In hitbox_aabb.h:
    static inline
    bool is_hitbox_aabb__dirty(Hitbox_AABB *p_hitbox_aabb) {
        return is_hitbox_flags__dirty(&p_hitbox_aabb->hitbox_aabb_flags__u8);
    }

This indirection allows the same flag logic to be reused across all hitbox
manager types without code duplication.

### Dirty Flag Convention

The dirty flag is the primary mechanism for change detection in the collision
system:

1. **Writers** (position setters, velocity appliers, acceleration setters)
   call `set_hitbox_flags_as__dirty` after modifying spatial data.
2. **Readers** (collision resolver, movement poller) check
   `is_hitbox_flags__dirty` to determine if work is needed.
3. **Consumers** call `set_hitbox_flags_as__not_dirty` after processing.

This avoids redundant collision checks for stationary hitboxes.

### Preconditions

- All functions require a non-null `Hitbox_Flags__u8*`. No null checks are
  performed; passing null is undefined behavior.

### Postconditions

- After `set_hitbox_flags_as__dirty`: `is_hitbox_flags__dirty` returns true.
- After `set_hitbox_flags_as__not_dirty`: `is_hitbox_flags__dirty` returns
  false.
- After `set_hitbox_flags_as__active`: `is_hitbox_flags__active` returns
  true.
- After `set_hitbox_flags_as__disabled`: `is_hitbox_flags__active` returns
  false.

### Error Handling

- No error handling is performed. These are raw bitfield operations.
