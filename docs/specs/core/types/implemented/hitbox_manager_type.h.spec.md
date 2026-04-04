# Specification: core/include/types/implemented/hitbox_manager_type.h

## Overview

Template header that defines the `Hitbox_Manager_Type` enum — the set of
hitbox manager implementations available. Each type corresponds to a
different collision detection strategy (AABB for 2D, AAABBB for 3D, etc.).
This file is copied to the game project directory by `tools/lav_new_project`
and is meant to be extended by the engine user.

## Template Behavior

This file resides in `core/include/types/implemented/` and is copied to
the game project's corresponding `types/implemented/` directory by the
`lav_new_project` script. If `DEFINE_HITBOX_MANAGER_TYPE` is not defined
after the `#include`, `defines.h` falls back to a built-in default.

## Dependencies

None (self-contained).

## Types

### Hitbox_Manager_Type (enum)

    typedef enum Hitbox_Manager_Type_t {
        Hitbox_Manager_Type__Default,
        Hitbox_Manager_Type__AABB = Hitbox_Manager_Type__Default,
        Hitbox_Manager_Type__AAABBB,
        Hitbox_Manager_Type__Unknown
    } Hitbox_Manager_Type;

| Value | Description |
|-------|-------------|
| `Hitbox_Manager_Type__Default` | Alias for the default hitbox manager type. |
| `Hitbox_Manager_Type__AABB` | 2D axis-aligned bounding box manager. Assigned as default. |
| `Hitbox_Manager_Type__AAABBB` | 3D axis-aligned bounding box manager. Omit if not using 3D. |
| `Hitbox_Manager_Type__Unknown` | End-of-enum sentinel. Used for array sizing. |

## Injection Mechanism

In `defines.h`:

    #include <types/implemented/hitbox_manager_type.h>
    #ifndef DEFINE_HITBOX_MANAGER_TYPE
    typedef enum Hitbox_Manager_Type_t { ... } Hitbox_Manager_Type;
    #endif

## Agentic Workflow

### Extension Pattern

Reassign `Default` to a different type if needed:

    Hitbox_Manager_Type__Default,
    Hitbox_Manager_Type__AAABBB = Hitbox_Manager_Type__Default,
    Hitbox_Manager_Type__AABB,
    Hitbox_Manager_Type__Unknown

### Constraints

- `Hitbox_Manager_Type__AABB` is required by core for UI hitbox management.
- `Hitbox_Manager_Type__Unknown` must remain last.
- `Hitbox_Manager_Type__Unknown` is used for array sizing in
  `Hitbox_Context.hitbox_manager_instance__invocation_table[]` and
  `Hitbox_Context.hitbox_manager_registration_records[]`.
- Core does not assume what is default — it uses types explicitly.
- The `#define DEFINE_HITBOX_MANAGER_TYPE` line must not be removed.

## Header Guard

`IMPL_HITBOX_MANAGER_TYPE_H`
