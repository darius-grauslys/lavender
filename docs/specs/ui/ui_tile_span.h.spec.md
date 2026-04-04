# Specification: core/include/ui/ui_tile_span.h

## Overview

Defines a 9-slice tile pattern (`UI_Tile_Span`) used to compose scalable UI
panels. A tile span describes 4 corner tiles, 4 edge tiles, and 1 fill tile.
When rendered into a tile map region, corners are placed at the extremes,
edges are repeated along borders, and the fill tile covers the interior.

## Dependencies

- `defines.h` (for `UI_Tile_Span`, `UI_Tile` struct definitions)
- `defines_weak.h` (forward declarations)

## Types

### UI_Tile_Span (struct)

    typedef struct UI_Tile_Span_t {
        union {
            UI_Tile ui_tile__corners[4];
            struct {
                UI_Tile ui_tile__corner__top_left;
                UI_Tile ui_tile__corner__top_right;
                UI_Tile ui_tile__corner__bottom_left;
                UI_Tile ui_tile__corner__bottom_right;
            };
        };
        union {
            UI_Tile ui_tile__edges[4];
            struct {
                UI_Tile ui_tile__edge__top;
                UI_Tile ui_tile__edge__right;
                UI_Tile ui_tile__edge__bottom;
                UI_Tile ui_tile__edge__left;
            };
        };
        UI_Tile ui_tile__fill;
    } UI_Tile_Span;

**Layout (9-slice):**

    [corner_TL] [edge_top ...] [corner_TR]
    [edge_left] [fill ....   ] [edge_right]
    [corner_BL] [edge_bottom ] [corner_BR]

## Functions

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `initialize_ui_tile_span_as__empty` | `(UI_Tile_Span*) -> void` | `void` | Initializes all 9 tiles to empty. |
| `initialize_ui_tile_span` | `(UI_Tile_Span*, UI_Tile[4] corners, UI_Tile[4] edges, UI_Tile fill) -> void` | `void` | Initializes with explicit corner, edge, and fill tiles. |
| `get_ui_tile_of__ui_tile_span` | `(const UI_Tile_Span*, u32 width, u32 height, u32 index_x, u32 index_y) -> const UI_Tile*` | `const UI_Tile*` | Returns the appropriate tile for a position within a rectangular region. |

## Agentic Workflow

### 9-Slice Sampling

`get_ui_tile_of__ui_tile_span` determines which tile to return based on
position within the span:
- Corner positions → corner tile.
- Border positions → edge tile.
- Interior positions → fill tile.

### Preconditions

- All functions require non-null `p_ui_tile_span`.
- `get_ui_tile_of__ui_tile_span`: `index_x < width` and `index_y < height`.

### Relationships

- Used by `UI_Element` — each element contains a `UI_Tile_Span ui_tile_span`.
- `generate_ui_span_in__ui_tile_map` (in `ui_tile_map.h`) writes a tile span
  into a tile map region.

## Header Guard

`UI_TILE_SPAN_H`
