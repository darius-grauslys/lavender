# `<drop_zone>` — Drop Zone Initialization

## Overview

The `<drop_zone>` element initializes the current UI element as a drop zone that can receive draggable elements. It allocates a hitbox and sets a receive-drop handler. Commonly used inside `<allocate_ui_container>` for inventory/equipment slots.

## 1. Attributes

| Attribute | Required | Default | Description |
|---|---|---|---|
| `x` | No | `0` | Horizontal offset in pixels from parent context. |
| `y` | No | `0` | Vertical offset in pixels from parent context. |
| `width` | Yes | — | Width of the drop zone hitbox in pixels. |
| `height` | Yes | — | Height of the drop zone hitbox in pixels. |
| `color` | No | `"55,55,55"` | RGB color for visual editor preview. |
| `m_Receive_Drop_Handler` | No | `"m_ui_drop_zone__receive_drop_handler__default"` | C function name for the handler invoked when a draggable is dropped onto this zone. |

## 2. Generated C Output

```c
allocate_hitbox_for__ui_element(p_game, p_gfx_window, <p_ui_element>,
    <width>, <height>, get_vector__3i32(<x>, <y>, 0));
initialize_ui_element_as__drop_zone(
    <p_ui_element>,
    <m_Receive_Drop_Handler>);
```

## 3. Example

```xml
<allocate_ui_container size="3" stride__x="24">
    <drop_zone width="23" height="27" color="55,55,96"
        m_Receive_Drop_Handler="m_ui_drop_zone__receive_drop_handler__inventory_slot"/>
</allocate_ui_container>
```
