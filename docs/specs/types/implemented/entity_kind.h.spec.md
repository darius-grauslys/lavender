# Specification: core/include/types/implemented/entity_kind.h

## Overview

Template header that defines the `Entity_Kind` enum — the set of entity
types available in the game (players, NPCs, projectiles, etc.). This file
is copied to the game project directory by `tools/lav_new_project` and is
meant to be extended by the engine user.

## Template Behavior

This file resides in `core/include/types/implemented/` and is copied to
the game project's corresponding `types/implemented/` directory by the
`lav_new_project` script. If `DEFINE_ENTITY_KIND` is not defined after the
`#include`, `defines_weak.h` falls back to a built-in default.

## Dependencies

None (self-contained).

## Types

### Entity_Kind (enum)

    typedef enum Entity_Kind {
        Entity_Kind__None = 0,
        Entity_Kind__Unknown
    } Entity_Kind;

| Value | Description |
|-------|-------------|
| `Entity_Kind__None` | No entity / sentinel. |
| `Entity_Kind__Unknown` | End-of-enum sentinel. Used for array sizing in `Entity_Manager.entity_functions[]`. |

## Injection Mechanism

In `defines_weak.h`:

    #include <types/implemented/entity_kind.h>
    #ifndef DEFINE_ENTITY_KIND
    typedef enum Entity_Kind {
        Entity_Kind__None,
        Entity_Kind__Unknown
    } Entity_Kind;
    #endif

## Agentic Workflow

### Extension Pattern

    typedef enum Entity_Kind {
        Entity_Kind__None = 0,
        Entity_Kind__Player,
        Entity_Kind__Skeleton,
        Entity_Kind__Zombie,
        Entity_Kind__Unknown
    } Entity_Kind;

### Constraints

- `Entity_Kind__None` must remain first (value 0).
- `Entity_Kind__Unknown` must remain last.
- `Entity_Kind__Unknown` is used for array sizing in
  `Entity_Manager.entity_functions[Entity_Kind__Unknown]`.
- Entity functions are registered per-kind during game initialization.
- The `#define DEFINE_ENTITY_KIND` line must not be removed.

## Header Guard

`IMPL_ENTITY_KIND_H`
