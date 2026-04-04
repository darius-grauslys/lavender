# Specification: core/include/ui/ui_tile_map.h

## Overview

Manages rectangular grids of `UI_Tile_Raw` values that back the visual
composition of UI windows. Tile maps come in three size categories (Small,
Medium, Large) and are accessed through a uniform `UI_Tile_Map__Wrapper`
abstraction. The wrapper provides size-agnostic access to the underlying
tile data.

## Dependencies

- `defines.h` (for all tile map types and flag macros)
- `defines_weak.h` (forward declarations)
- `platform_defaults.h` (for default tile map dimension macros)
- `platform_defines.h` (platform-specific overrides)

## Types

### UI_Tile_Map_Size (enum)

    typedef enum UI_Tile_Map_Size {
        UI_Tile_Map_Size__None = 0,
        UI_Tile_Map_Size__Small,
        UI_Tile_Map_Size__Medium,
        UI_Tile_Map_Size__Large,
        UI_Tile_Map_Size__Unknown
    } UI_Tile_Map_Size;

### UI_Tile_Map__Flags (u8)

| Flag | Bit | Description |
|------|-----|-------------|
| `UI_TILE_MAP__FLAG__IS_ALLOCATED` | 0 | Tile map is allocated. |

### UI_Tile_Map__Wrapper (struct)

    typedef struct UI_Tile_Map__Wrapper_t {
        UI_Tile_Raw *p_ui_tile_data;
        Quantity__u32 width_of__ui_tile_map;
        Quantity__u32 height_of__ui_tile_map;
        UI_Tile_Map_Size catagory_size_of__ui_tile_map;
    } UI_Tile_Map__Wrapper;

| Field | Type | Description |
|-------|------|-------------|
| `p_ui_tile_data` | `UI_Tile_Raw*` | Pointer to the raw tile data array. |
| `width_of__ui_tile_map` | `Quantity__u32` | Utilized width in tiles. |
| `height_of__ui_tile_map` | `Quantity__u32` | Utilized height in tiles. |
| `catagory_size_of__ui_tile_map` | `UI_Tile_Map_Size` | Which pool the storage came from. |

### UI_Tile_Map__Small / Medium / Large (structs)

Each contains a `UI_Tile_Map__Flags` and a fixed-size `UI_Tile_Raw` array
dimensioned by the corresponding width × height macros.

### Compile-Time Configuration

| Macro | Default | Description |
|-------|---------|-------------|
| `UI_TILE_MAP__SMALL__MAX_QUANTITY_OF` | `32` | Max number of small tile maps. |
| `UI_TILE_MAP__SMALL__WIDTH` | `8` | Width of small tile maps in tiles. |
| `UI_TILE_MAP__SMALL__HEIGHT` | `8` | Height of small tile maps in tiles. |
| `UI_TILE_MAP__MEDIUM__MAX_QUANTITY_OF` | `16` | Max number of medium tile maps. |
| `UI_TILE_MAP__MEDIUM__WIDTH` | `16` | Width of medium tile maps in tiles. |
| `UI_TILE_MAP__MEDIUM__HEIGHT` | `16` | Height of medium tile maps in tiles. |
| `UI_TILE_MAP__LARGE__MAX_QUANTITY_OF` | `8` | Max number of large tile maps. |
| `UI_TILE_MAP__LARGE__WIDTH` | `32` | Width of large tile maps in tiles. |
| `UI_TILE_MAP__LARGE__HEIGHT` | `32` | Height of large tile maps in tiles. |

## Functions

### Initialization

| Function | Signature | Description |
|----------|-----------|-------------|
| `initialize_ui_tile_map__small_as__deallocated` | `(UI_Tile_Map__Small*) -> void` | Marks small tile map as deallocated and zeroes data. |
| `initialize_ui_tile_map__medium_as__deallocated` | `(UI_Tile_Map__Medium*) -> void` | Marks medium tile map as deallocated and zeroes data. |
| `initialize_ui_tile_map__large_as__deallocated` | `(UI_Tile_Map__Large*) -> void` | Marks large tile map as deallocated and zeroes data. |
| `initialize_ui_tile_map__wrapper` | `(UI_Tile_Map__Wrapper*, UI_Tile_Raw*, u32 width, u32 height, UI_Tile_Map_Size) -> void` | Initializes a wrapper to point at existing tile data. |

### Tile Map Operations

| Function | Signature | Description |
|----------|-----------|-------------|
| `generate_ui_span_in__ui_tile_map` | `(UI_Tile_Map__Wrapper*, const UI_Tile_Span*, u32 width, u32 height, u32 x, u32 y) -> void` | Writes a 9-slice tile span into a rectangular region. |
| `set_ui_tile_map__wrapper__utilized_size` | `(UI_Tile_Map__Wrapper*, u32 width, u32 height) -> void` | Sets utilized dimensions, clamping to allocation limits. |
| `fill_ui_tile_map` | `(UI_Tile_Map__Wrapper*, UI_Tile) -> void` | Fills entire tile map with a single tile. |
| `fill_ui_tile_map_in__this_region` | `(UI_Tile_Map__Wrapper*, UI_Tile, u32 x_start, u32 y_start, u32 width, u32 height) -> void` | Fills a rectangular sub-region. |
| `copy_into_ui_tile_map` | `(UI_Tile_Map__Wrapper*, const UI_Tile_Raw*, u32 offset, u32 length) -> void` | Copies raw tile data at the given offset. |

### Flag Management (static inline)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `is_ui_tile_map_flags__allocated` | `(UI_Tile_Map__Flags) -> bool` | `bool` | True if `IS_ALLOCATED` set. |
| `set_ui_tile_map_flags_as__allocated` | `(UI_Tile_Map__Flags*) -> void` | `void` | Sets `IS_ALLOCATED`. |
| `set_ui_tile_map_flags_as__deallocated` | `(UI_Tile_Map__Flags*) -> void` | `void` | Clears `IS_ALLOCATED`. |

### Validation (static inline)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `is_ui_tile_map__wrapper_with__data` | `(UI_Tile_Map__Wrapper*) -> bool` | `bool` | True if `p_ui_tile_data` is non-null. |
| `is_ui_tile_map__wrapper_with__valid_size_catagory` | `(UI_Tile_Map__Wrapper*) -> bool` | `bool` | True if size category is between `None` (exclusive) and `Unknown` (exclusive). |
| `is_ui_tile_map__wrapper_with__valid_size` | `(UI_Tile_Map__Wrapper*) -> bool` | `bool` | True if width > 0, height > 0, and size category is valid. |
| `is_ui_tile_map__wrapper__valid` | `(UI_Tile_Map__Wrapper*) -> bool` | `bool` | True if has data and valid size. |

### Construction (static inline)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `get_ui_tile_map__wrapper` | `(UI_Tile_Raw*, UI_Tile_Map__Flags*, u32 width, u32 height, UI_Tile_Map_Size) -> UI_Tile_Map__Wrapper` | `UI_Tile_Map__Wrapper` | Constructs a wrapper by value. Note: `p_ui_tile_map__flags` is accepted but not stored. |
| `ui_tile_map__small_to__ui_tile_map_wrapper` | `(UI_Tile_Map__Small*) -> UI_Tile_Map__Wrapper` | `UI_Tile_Map__Wrapper` | Creates wrapper from small tile map. |
| `ui_tile_map__medium_to__ui_tile_map_wrapper` | `(UI_Tile_Map__Medium*) -> UI_Tile_Map__Wrapper` | `UI_Tile_Map__Wrapper` | Creates wrapper from medium tile map. |
| `ui_tile_map__large_to__ui_tile_map_wrapper` | `(UI_Tile_Map__Large*) -> UI_Tile_Map__Wrapper` | `UI_Tile_Map__Wrapper` | Creates wrapper from large tile map. |

### Accessors (static inline)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `get_catagory_size_of__p_ui_tile_map__wrapper` | `(UI_Tile_Map__Wrapper*) -> UI_Tile_Map_Size` | `UI_Tile_Map_Size` | Returns size category. |
| `get_width_of__p_ui_tile_map__wrapper` | `(UI_Tile_Map__Wrapper*) -> Quantity__u32` | `Quantity__u32` | Returns width. |
| `get_height_of__p_ui_tile_map__wrapper` | `(UI_Tile_Map__Wrapper*) -> Quantity__u32` | `Quantity__u32` | Returns height. |

## Agentic Workflow

### Usage Pattern

`Graphics_Window` contains a `UI_Tile_Map__Wrapper` for its backing tile
data. `UI_Tile_Map_Manager` pools tile maps of each size category.
`PLATFORM_compose_gfx_window` reads the tile map to render UI.
`generate_ui_span_in__ui_tile_map` bridges `UI_Tile_Span` → tile map.

### Preconditions

- All functions require non-null pointers.
- `generate_ui_span_in__ui_tile_map`: region must fit within the tile map dimensions.

## Header Guard

`UI_TILE_MAP_H`
