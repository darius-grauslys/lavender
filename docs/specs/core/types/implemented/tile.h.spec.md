# Specification: core/include/types/implemented/tile.h

## Overview

Template header that defines the `Tile` struct — the per-tile data stored
in every chunk. This file is copied to the game project directory by
`tools/lav_new_project` and is meant to be extended by the engine user.

## Template Behavior

This file resides in `core/include/types/implemented/` and is copied to
the game project's corresponding `types/implemented/` directory by the
`lav_new_project` script. If `DEFINE_TILE` is not defined after the
`#include`, `defines.h` falls back to a built-in default containing only
`the_kind_of__tile`.

## Dependencies

- `defines_weak.h` (for `Tile_Kind`)

## Types

### Tile (struct)

    typedef struct Tile_t {
        Tile_Kind the_kind_of__tile;
    } Tile;

| Field | Type | Description |
|-------|------|-------------|
| `the_kind_of__tile` | `Tile_Kind` | The tile's kind discriminator. |

## Injection Mechanism

In `defines.h`:

    #include <types/implemented/tile.h>
    #ifndef DEFINE_TILE
    typedef struct Tile_t {
        Tile_Kind the_kind_of__tile;
    } Tile;
    #endif

## Agentic Workflow

### Extension Pattern

    typedef struct Tile_t {
        Tile_Kind the_kind_of__tile;
        Tile_Flags__u8 tile_flags;
        u8 tile_metadata;
    } Tile;

### Constraints

- The struct is stored in `Chunk.tiles[CHUNK__QUANTITY_OF__TILES]`, so its
  size directly affects chunk memory footprint. Default chunk has 128 tiles.
- `the_kind_of__tile` should be retained for compatibility with core engine
  code.
- The `#define DEFINE_TILE` line must not be removed.

## Header Guard

`IMPL_TILE_H`
