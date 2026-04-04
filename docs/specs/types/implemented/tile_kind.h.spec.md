# Specification: core/include/types/implemented/tile_kind.h

## Overview

Template header that defines the `Tile_Kind` enum — the set of tile types
available in the game world. This file is copied to the game project
directory by `tools/lav_new_project` and is meant to be extended by the
engine user.

## Template Behavior

This file resides in `core/include/types/implemented/` and is copied to
the game project's corresponding `types/implemented/` directory by the
`lav_new_project` script. If `DEFINE_TILE_KIND` is not defined after the
`#include`, `defines_weak.h` falls back to a built-in default.

## Dependencies

None (self-contained).

## Types

### Tile_Kind (enum)

    typedef enum Tile_Kind {
        Tile_Kind__None = 0,
        Tile_Kind__Unknown
    } Tile_Kind;

| Value | Description |
|-------|-------------|
| `Tile_Kind__None` | No tile / empty sentinel. |
| `Tile_Kind__Unknown` | End-of-enum sentinel. Used for array sizing. |

## Injection Mechanism

In `defines_weak.h`:

    #include <types/implemented/tile_kind.h>
    #ifndef DEFINE_TILE_KIND
    typedef enum Tile_Kind { ... } Tile_Kind;
    #endif

## Agentic Workflow

### Extension Pattern

    typedef enum Tile_Kind {
        Tile_Kind__None = 0,
        Tile_Kind__Grass,
        Tile_Kind__Stone,
        Tile_Kind__Water,
        Tile_Kind__Lava,
        Tile_Kind__Unknown
    } Tile_Kind;

### Constraints

- `Tile_Kind__None` must remain first (value 0).
- `Tile_Kind__Unknown` must remain last.
- `Tile_Kind__Unknown` is used for array sizing in
  `Tile_Logic_Table_Data.tile_logic_record__tile_kind[Tile_Kind__Unknown]`.
- Tile logic records are registered per-kind via `register_tile_logic_tables`
  (see `world/implemented/tile_logic_table_registrar.h`).
- The `#define DEFINE_TILE_KIND` line must not be removed.

## Header Guard

`IMPL_TILE_KIND_H`
