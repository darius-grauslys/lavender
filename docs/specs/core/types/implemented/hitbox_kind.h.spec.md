# Specification: core/include/types/implemented/hitbox_kind.h

## Overview

Template header that defines the `Hitbox_Kind` enum — the set of hitbox
types used for collision detection. This file is copied to the game project
directory by `tools/lav_new_project` and is meant to be extended by the
engine user.

## Template Behavior

This file resides in `core/include/types/implemented/` and is copied to
the game project's corresponding `types/implemented/` directory by the
`lav_new_project` script. If `DEFINE_HITBOX_KIND` is not defined after the
`#include`, `defines.h` falls back to a built-in default.

## Dependencies

None (self-contained).

## Types

### Hitbox_Kind (enum)

    typedef enum Hitbox_Kind {
        Hitbox_Kind__Opaque,
        Hitbox_Kind__AABB,
        Hitbox_Kind__Unknown
    } Hitbox_Kind;

| Value | Description |
|-------|-------------|
| `Hitbox_Kind__Opaque` | Opaque pointer hitbox, abstracts to any other hitbox type. Least performant. |
| `Hitbox_Kind__AABB` | Axis-aligned bounding box. Most common for 2D physics. |
| `Hitbox_Kind__Unknown` | End-of-enum sentinel. |

## Injection Mechanism

In `defines.h`:

    #include <types/implemented/hitbox_kind.h>

This file is included directly without a fallback guard — it is always
expected to be present.

## Agentic Workflow

### Extension Pattern

    typedef enum Hitbox_Kind {
        Hitbox_Kind__Opaque,
        Hitbox_Kind__AABB,
        Hitbox_Kind__AAABBB,
        Hitbox_Kind__Ball,
        Hitbox_Kind__Sphere,
        Hitbox_Kind__Unknown
    } Hitbox_Kind;

### Constraints

- `Hitbox_Kind__Opaque` and `Hitbox_Kind__AABB` are used by core and must
  remain present.
- `Hitbox_Kind__Unknown` must remain last.
- Used by `Game_Action_Kind__Hitbox` for hitbox type discrimination in
  game actions.
- The `#define DEFINE_HITBOX_KIND` line must not be removed.

## Header Guard

`HITBOX_KIND_H`
