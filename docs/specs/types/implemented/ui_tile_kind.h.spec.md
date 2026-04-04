# Specification: core/include/types/implemented/ui_tile_kind.h

## Overview

Template header that defines the `UI_Tile_Kind` enum — the set of UI tile
types available for tile-based UI composition. This file is copied to the
game project directory by `tools/lav_new_project` and is meant to be
extended by the engine user.

## Template Behavior

This file resides in `core/include/types/implemented/` and is copied to
the game project's corresponding `types/implemented/` directory by the
`lav_new_project` script. If `DEFINE_UI_TILE_KIND` is not defined after
the `#include`, `defines_weak.h` falls back to a built-in default.

## Dependencies

None (self-contained).

## Types

### UI_Tile_Kind (enum)

    typedef enum UI_Tile_Kind {
        UI_Tile_Kind__None,
        UI_Tile_Kind__Unknown
    } UI_Tile_Kind;

| Value | Description |
|-------|-------------|
| `UI_Tile_Kind__None` | No tile / empty sentinel. |
| `UI_Tile_Kind__Unknown` | End-of-enum sentinel. |

## Injection Mechanism

In `defines_weak.h`:

    #include <types/implemented/ui_tile_kind.h>
    #ifndef DEFINE_UI_TILE_KIND
    typedef enum UI_Tile_Kind { ... } UI_Tile_Kind;
    #endif

## Agentic Workflow

### Extension Pattern

    typedef enum UI_Tile_Kind {
        UI_Tile_Kind__None,
        UI_Tile_Kind__Window_Border_TL,
        UI_Tile_Kind__Window_Border_T,
        UI_Tile_Kind__Window_Border_TR,
        UI_Tile_Kind__Window_Fill,
        UI_Tile_Kind__Unknown
    } UI_Tile_Kind;

### Constraints

- `UI_Tile_Kind__None` must remain first.
- `UI_Tile_Kind__Unknown` must remain last.
- `UI_Tile_Kind` is stored as a 10-bit bitfield in `UI_Tile`, so the
  maximum number of kinds is 1024.
- The `#define DEFINE_UI_TILE_KIND` line must not be removed.

## Header Guard

`IMPL_UI_TILE_KIND_H`
