# Tile Logic Table Specification

## File
`core/include/world/tile_logic_table.h`

## Purpose
Manages the logic properties associated with tile kinds — passability,
sight blocking, ground presence, and tile height. The table maps `Tile_Kind`
values to `Tile_Logic_Record` entries, enabling efficient per-tile physics
and collision queries.

## Dependencies
| Header | Purpose |
|--------|---------|
| `defines.h` | `Tile_Logic_Table`, `Tile_Logic_Record`, `Tile` |
| `defines_weak.h` | Forward declarations, flag macros |

## Types

### `Tile_Logic_Record` (defined in `defines_weak.h` or `types/implemented/tile_logic_record.h`)
