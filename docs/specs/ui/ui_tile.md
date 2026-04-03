# UI Tile Specification

## File
`core/include/ui/ui_tile.h`

## Purpose
Defines initialization and manipulation operations on individual `UI_Tile`
values — the smallest visual unit in the tile-based UI composition system.
A `UI_Tile` pairs a `UI_Tile_Kind` (10-bit tile index into a tileset) with
`UI_Tile_Flags` (6-bit flags controlling rendering: flipping, scaling).

## Dependencies
| Header       | Purpose                                                    |
|--------------|------------------------------------------------------------|
| `defines.h`  | `UI_Tile`, `UI_Tile_Kind`, `UI_Tile_Flags`, `UI_Tile_Raw` |

## Types

### `UI_Tile` (defined in `defines.h`)
