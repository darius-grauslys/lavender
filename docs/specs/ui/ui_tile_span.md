# UI Tile Span Specification

## File
`core/include/ui/ui_tile_span.h`

## Purpose
Defines a 9-slice tile pattern (`UI_Tile_Span`) used to compose scalable UI
panels. A tile span describes 4 corner tiles, 4 edge tiles, and 1 fill tile.
When rendered into a tile map region, corners are placed at the extremes,
edges are repeated along borders, and the fill tile covers the interior.

## Dependencies
| Header         | Purpose                                    |
|----------------|--------------------------------------------|
| `defines.h`    | `UI_Tile_Span`, `UI_Tile` struct definitions |
| `defines_weak.h` | Forward declarations                     |

## Types

### `UI_Tile_Span` (defined in `defines.h`)
