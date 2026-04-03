# UI Tile Map Specification

## File
`core/include/ui/ui_tile_map.h`

## Purpose
Manages rectangular grids of `UI_Tile_Raw` values that back the visual
composition of UI windows. Tile maps come in three size categories (Small,
Medium, Large) and are accessed through a uniform `UI_Tile_Map__Wrapper`
abstraction.

## Dependencies
| Header              | Purpose                                          |
|---------------------|--------------------------------------------------|
| `defines.h`         | All tile map types and flag macros                |
| `defines_weak.h`    | Forward declarations                             |
| `platform_defaults.h` | Default tile map dimension macros              |
| `platform_defines.h`  | Platform-specific overrides                    |

## Compile-Time Configuration (from `platform_defaults.h`)
| Macro                                  | Default | Description                          |
|----------------------------------------|---------|--------------------------------------|
| `UI_TILE_MAP__SMALL__MAX_QUANTITY_OF`  | 32      | Max number of small tile maps        |
| `UI_TILE_MAP__SMALL__WIDTH`            | 8       | Width of small tile maps in tiles    |
| `UI_TILE_MAP__SMALL__HEIGHT`           | 8       | Height of small tile maps in tiles   |
| `UI_TILE_MAP__MEDIUM__MAX_QUANTITY_OF` | 16      | Max number of medium tile maps       |
| `UI_TILE_MAP__MEDIUM__WIDTH`           | 16      | Width of medium tile maps in tiles   |
| `UI_TILE_MAP__MEDIUM__HEIGHT`          | 16      | Height of medium tile maps in tiles  |
| `UI_TILE_MAP__LARGE__MAX_QUANTITY_OF`  | 8       | Max number of large tile maps        |
| `UI_TILE_MAP__LARGE__WIDTH`            | 32      | Width of large tile maps in tiles    |
| `UI_TILE_MAP__LARGE__HEIGHT`           | 32      | Height of large tile maps in tiles   |

## Types

### `UI_Tile_Map_Size` (defined in `defines_weak.h`)
