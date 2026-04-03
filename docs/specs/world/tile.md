# Tile Specification

## File
`core/include/world/tile.h`

## Purpose
Provides inline helper functions for querying and mutating `Tile` and
`Tile_Flags__u8` values. Tiles are the atomic world-building unit — each
chunk contains a fixed grid of tiles.

## Dependencies
| Header | Purpose |
|--------|---------|
| `defines_weak.h` | `Tile_Flags__u8`, `Tile_Kind`, flag macros |
| `defines.h` | `Tile` struct |

## Types

### `Tile` (defined in `defines.h` or `types/implemented/tile.h`)
