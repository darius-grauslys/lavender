# `<ui>` — Root UI Element Container

## Overview

The `<ui>` element is the second child of `<root>` and serves as the entry point for all UI element declarations. It configures the generated C function's starting state: element ID offset, optional tile map setup, and positional layering. All child elements of `<ui>` are processed sequentially to produce the body of the generated `allocate_ui_for__<filename>()` function.

## 1. Attributes

| Attribute | Required | Default | Description |
|---|---|---|---|
| `offset_of__ui_index` | No | `0` | Starting number for sequential UI element ID assignment. Used to chain multiple generated UI files so their IDs don't collide. For example, if a HUD uses IDs 0–2, the next window sets this to `3`. |
| `ui_position` | No | Not set | Comma-separated `"x,y,z"` offset applied to the graphics window. The `z` component controls layering when multiple generated UIs are composited together. Generates: `set_position_3i32_of__graphics_window(p_game, p_gfx_window, get_vector__3i32(x,y,z));` |
| `ui_tile_map__size` | No | `"UI_Tile_Map_Size__None"` | Size class for the UI tile map allocation. Valid values: `UI_Tile_Map_Size__Small`, `UI_Tile_Map_Size__Medium`, `UI_Tile_Map_Size__Large`. Default to `__Large` when a tile map is needed. The actual pixel dimensions of each size class are configured externally and are not a concern in this context. |
| `ui_tile_map` | No | Not set | **((TO BE EXTENDED IN FUNCTIONALITY))** Name of the tile map data array used by the UI editor. When set, generates a `copy_into_ui_tile_map()` call. Requires `ui_tile_map__size` to also be set. |
| `ui_tile_map__length` | No | `"0"` | **((TO BE EXTENDED IN FUNCTIONALITY))** Length of the tile map data array. Used alongside `ui_tile_map`. |
| `ui_tile_map__offset` | No | `"0"` | Byte offset into the tile map data for partial copies. |
| `ui_tile_map__aliased_texture` | No | Not set | **((TO BE EXTENDED IN FUNCTIONALITY))** Alias name for the texture used by the tile map. When set, generates `get_uuid_of__aliased_texture()` and `set_graphics_window__ui_tile_map__texture()` calls. Requires `ui_tile_map__size` to also be set. |

## 2. Generated Function Signature

The `<ui>` element produces a function with this signature:

```c
bool allocate_ui_for__<source_name>(
    Gfx_Context *p_gfx_context,
    Graphics_Window *p_gfx_window,
    Game *p_game,
    UI_Manager *p_ui_manager,
    Identifier__u16 index_of__ui_element_offset__u16);
```

Where `<source_name>` is derived from the XML filename (without extension).

## 3. Generated Preamble

Before processing child elements, the function body declares these local variables:

```c
UI_Element *p_ui_iterator = 0;
UI_Element *p_ui_iterator_previous_previous = 0;
UI_Element *p_ui_iterator_previous = 0;
UI_Element *p_ui_iterator_child = 0;
```

## 4. Child Elements

All direct children of `<ui>` are processed in document order. Valid children are any element with a matching `<ui_func_signature>` entry in `<config>`: `<group>`, `<grid>`, `<allocate_ui>`, `<allocate_ui_container>`, `<code>`, etc.

## 5. Header File Output

The generated `.h` file contains:

- Include guard based on the source filename.
- `#include <defines.h>`
- The function prototype for `allocate_ui_for__<source_name>`.
- `#define` constants for every named UI element (see `name` attribute on `<allocate_ui>`, `<allocate_ui_container>`, `<grid>`, `<group>`).
