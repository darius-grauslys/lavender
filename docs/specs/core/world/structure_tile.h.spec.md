# Specification: core/include/world/structure_tile.h

## Overview

Defines `Structure_Tile` — a helper struct describing tiles that may have
walls, stairs, or windows. Used during structure generation to determine
which features a tile position should have.

## Dependencies

None (self-contained).

## Types

### Structure_Tile (struct)

    typedef struct Structure_Tile_t {
        bool has_walls;
        bool has_stairs;
        bool has_windows;
    } Structure_Tile;

| Field | Type | Description |
|-------|------|-------------|
| `has_walls` | `bool` | True if this tile position has walls. |
| `has_stairs` | `bool` | True if this tile position has stairs. |
| `has_windows` | `bool` | True if this tile position has windows. |

## Functions

None.

## Header Guard

`STRUCTURE_TILE_H`
