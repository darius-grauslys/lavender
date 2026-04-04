# Specification: core/include/types/implemented/entity_data.h

## Overview

Template header that defines the `Entity_Data` struct — the game-specific
data payload embedded in every `Entity`. This file is copied to the game
project directory by `tools/lav_new_project` and is meant to be extended
by the engine user.

## Template Behavior

This file resides in `core/include/types/implemented/` and is copied to
the game project's corresponding `types/implemented/` directory by the
`lav_new_project` script. If `DEFINE_ENTITY_DATA` is not defined after the
`#include`, `defines.h` falls back to a built-in default containing only
`the_kind_of__entity`.

## Dependencies

- `defines_weak.h` (for `Entity_Flags__u32`, `Entity_Kind`)

## Types

### Entity_Data (struct)

    typedef struct Entity_Data_t {
        Entity_Flags__u32   entity_flags;
        Entity_Kind         the_kind_of__entity;
    } Entity_Data;

| Field | Type | Description |
|-------|------|-------------|
| `entity_flags` | `Entity_Flags__u32` | Bitfield of entity state flags. |
| `the_kind_of__entity` | `Entity_Kind` | The entity's kind discriminator. |

## Injection Mechanism

In `defines.h`:

    #include <types/implemented/entity_data.h>
    #ifndef DEFINE_ENTITY_DATA
    typedef struct Entity_Data_t {
        Entity_Kind the_kind_of__entity;
    } Entity_Data;
    #endif

## Agentic Workflow

### Extension Pattern

Add game-specific fields after the required fields:

    typedef struct Entity_Data_t {
        Entity_Flags__u32   entity_flags;
        Entity_Kind         the_kind_of__entity;
        // Game-specific extensions:
        Quantity__u16       health;
        Quantity__u16       mana;
        Sprite              sprite;
        Hitbox_AABB         *p_hitbox;
        Inventory           *p_inventory;
    } Entity_Data;

### Constraints

- The struct is embedded directly in `Entity` (at `entity.entity_data`),
  so its size affects the total `Entity` size and therefore the
  `Entity_Manager` pool memory footprint.
- The `#define DEFINE_ENTITY_DATA` line must not be removed.
- `entity_flags` and `the_kind_of__entity` should be retained for
  compatibility with core engine code that accesses them.

## Header Guard

`IMPL_ENTITY_DATA_H`
