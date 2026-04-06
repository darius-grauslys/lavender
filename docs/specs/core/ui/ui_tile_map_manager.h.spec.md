# 12 Specification: core/include/ui/ui_tile_map_manager.h

## 12.1 Overview

Manages pools of `UI_Tile_Map__Small`, `UI_Tile_Map__Medium`, and
`UI_Tile_Map__Large` instances. Provides allocation and deallocation of tile
maps by size category, returning `UI_Tile_Map__Wrapper` handles for
size-agnostic access.

## 12.2 Dependencies

- `defines.h` (for `UI_Tile_Map_Manager`, `UI_Tile_Map__Wrapper`, size enums)

## 12.3 Types

### 12.3.1 UI_Tile_Map_Manager (struct)

    typedef struct UI_Tile_Map_Manager_t {
        UI_Tile_Map__Large ui_tile_maps__large[UI_TILE_MAP__LARGE__MAX_QUANTITY_OF];
        UI_Tile_Map__Medium ui_tile_maps__medium[UI_TILE_MAP__MEDIUM__MAX_QUANTITY_OF];
        UI_Tile_Map__Small ui_tile_maps__small[UI_TILE_MAP__SMALL__MAX_QUANTITY_OF];
    } UI_Tile_Map_Manager;

| Field | Type | Description |
|-------|------|-------------|
| `ui_tile_maps__large` | `UI_Tile_Map__Large[]` | Pool of large tile maps. |
| `ui_tile_maps__medium` | `UI_Tile_Map__Medium[]` | Pool of medium tile maps. |
| `ui_tile_maps__small` | `UI_Tile_Map__Small[]` | Pool of small tile maps. |

## 12.4 Functions

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `initialize_ui_tile_map_manager` | `(UI_Tile_Map_Manager*) -> void` | `void` | Initializes all tile maps in all pools as deallocated. |
| `allocate_ui_tile_map_with__ui_tile_map_manager` | `(UI_Tile_Map_Manager*, UI_Tile_Map_Size) -> UI_Tile_Map__Wrapper` | `UI_Tile_Map__Wrapper` | Allocates a tile map from the matching pool. Returns invalid wrapper (null data) if exhausted. |
| `release_ui_tile_map_with__ui_tile_map_manager` | `(UI_Tile_Map_Manager*, UI_Tile_Map__Wrapper*) -> void` | `void` | Returns a tile map to its pool. Sets wrapper data pointer to null. |

## 12.5 Agentic Workflow

### 12.5.1 Ownership

Owned by `Gfx_Context` (at `gfx_context.ui_tile_map_manager`).
`Graphics_Window` allocation uses this manager to obtain tile map backing
storage.

### 12.5.2 Preconditions

- `allocate_ui_tile_map_with__ui_tile_map_manager`: size must be `Small`, `Medium`, or `Large`.
- `release_ui_tile_map_with__ui_tile_map_manager`: wrapper must have been allocated from this manager.

## 12.6 Header Guard

`UI_TILE_MAP_MANAGER_H`
