# UI Tile Map Manager Specification

## File
`core/include/ui/ui_tile_map_manager.h`

## Purpose
Manages pools of `UI_Tile_Map__Small`, `UI_Tile_Map__Medium`, and
`UI_Tile_Map__Large` instances. Provides allocation and deallocation of tile
maps by size category, returning `UI_Tile_Map__Wrapper` handles.

## Dependencies
| Header       | Purpose                                                  |
|--------------|----------------------------------------------------------|
| `defines.h`  | `UI_Tile_Map_Manager`, `UI_Tile_Map__Wrapper`, size enums |

## Types

### `UI_Tile_Map_Manager` (defined in `defines.h`)
