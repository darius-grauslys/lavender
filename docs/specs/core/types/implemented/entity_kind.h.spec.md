# 1 Specification: core/include/types/implemented/entity_kind.h

## 1.1 Overview

Template header that defines the `Entity_Kind` enum — the set of entity
types available in the game (players, NPCs, projectiles, etc.). This file
is copied to the game project directory by `tools/lav_new_project` and is
meant to be extended by the engine user.

## 1.2 Template Behavior

This file resides in `core/include/types/implemented/` and is copied to
the game project's corresponding `types/implemented/` directory by the
`lav_new_project` script. If `DEFINE_ENTITY_KIND` is not defined after the
`#include`, `defines_weak.h` falls back to a built-in default.

## 1.3 Dependencies

None (self-contained).

## 1.4 Types

### 1.4.1 Entity_Kind (enum)

    typedef enum Entity_Kind {
        Entity_Kind__None = 0,
        Entity_Kind__Unknown
    } Entity_Kind;

| Value | Description |
|-------|-------------|
| `Entity_Kind__None` | No entity / sentinel. |
| `Entity_Kind__Unknown` | End-of-enum sentinel. Used for array sizing in `Entity_Manager.entity_functions[]`. |

## 1.5 Injection Mechanism

In `defines_weak.h`:

    #include <types/implemented/entity_kind.h>
    #ifndef DEFINE_ENTITY_KIND
    typedef enum Entity_Kind {
        Entity_Kind__None,
        Entity_Kind__Unknown
    } Entity_Kind;
    #endif

## 1.6 Agentic Workflow

### 1.6.1 Extension Pattern

    typedef enum Entity_Kind {
        Entity_Kind__None = 0,
        Entity_Kind__Player,
        Entity_Kind__Skeleton,
        Entity_Kind__Zombie,
        Entity_Kind__Unknown
    } Entity_Kind;

### 1.6.2 Constraints

- `Entity_Kind__None` must remain first (value 0).
- `Entity_Kind__Unknown` must remain last.
- `Entity_Kind__Unknown` is used for array sizing in
  `Entity_Manager.entity_functions[Entity_Kind__Unknown]`.
- Entity functions are registered per-kind during game initialization.
- The `#define DEFINE_ENTITY_KIND` line must not be removed.

## 1.7 Header Guard

`IMPL_ENTITY_KIND_H`
