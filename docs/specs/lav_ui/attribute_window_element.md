# `<window_element>` — Sub-Window Element Initialization

## Overview

The `<window_element>` element initializes the current UI element as a window element that opens a sub-window (e.g., an equipment panel or inventory column embedded within a larger UI). It sets the window kind, parent window UUID, positional offset for the sub-window, and allocates a hitbox.

## 1. Attributes

| Attribute | Required | Default | Description |
|---|---|---|---|
| `x` | No | `0` | Horizontal position in pixels from parent context. Used for hitbox. |
| `y` | No | `0` | Vertical position in pixels from parent context. Used for hitbox. |
| `width` | Yes | — | Width of the element hitbox in pixels. |
| `height` | Yes | — | Height of the element hitbox in pixels. |
| `window_kind` | No | `"Graphics_Window_Kind__Unknown"` | The C enum value identifying which window type to open. Example: `"UI_Window_Kind__Inventory_Column"`. |
| `offset_window__x` | No | `0` | Horizontal offset for the sub-window's position. |
| `offset_window__y` | No | `0` | Vertical offset for the sub-window's position. |
| `offset_window__z` | No | `0` | Depth offset for the sub-window's position. |
| `layer` | No | Not set | If provided, associates this element with a background layer in the visual editor, adjusting the background's offset. |
| `color` | No | `"55,55,55"` | RGB color for visual editor preview. |

## 2. Generated C Output

```c
initialize_ui_element_as__window_element_and__open_window(
    <p_ui_element>,
    p_game,
    <window_kind>,
    GET_UUID_P(p_gfx_window),
    get_vector__3i32(<offset_window__x>, <offset_window__y>, <offset_window__z>));
allocate_hitbox_for__ui_element(p_game, p_gfx_window, <p_ui_element>,
    <width>, <height>, get_vector__3i32(<x>, <y>, 0));
```

## 3. Required Config Signature

```xml
<ui_func_signature for="window_element" c_signatures="initialize_ui_element_as__window_element_and__open_window"/>
```

## 4. Example

```xml
<allocate_ui name="p_equipment_window">
    <window_element x="20" y="36" width="52" height="96"
        offset_window__x="46" offset_window__y="180"
        layer="1" window_kind="UI_Window_Kind__Equipment"/>
</allocate_ui>
```
