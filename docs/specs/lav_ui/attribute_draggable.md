# `<draggable>` — Draggable Element Initialization

## Overview

The `<draggable>` element initializes the current UI element as a draggable. It allocates a hitbox and sets a drag handler. Typically used as a child of `<alloc_child>` inside a container to create draggable items within drop zones.

## 1. Attributes

| Attribute | Required | Default | Description |
|---|---|---|---|
| `x` | No | `0` | Horizontal offset in pixels from parent context. |
| `y` | No | `0` | Vertical offset in pixels from parent context. |
| `width` | Yes | — | Width of the draggable hitbox in pixels. |
| `height` | Yes | — | Height of the draggable hitbox in pixels. |
| `color` | No | `"55,55,55"` | RGB color for visual editor preview. |
| `m_Dragged_Handler` | No | `"m_ui_draggable__dragged_handler__default"` | C function name for the drag handler callback. |

## 2. Generated C Output

```c
allocate_hitbox_for__ui_element(p_game, p_gfx_window, <p_ui_element>,
    <width>, <height>, get_vector__3i32(<x>, <y>, 0));
initialize_ui_element_as__draggable(
    <p_ui_element>,
    <m_Dragged_Handler>);
```

## 3. Example

```xml
<alloc_child>
    <draggable width="18" height="22" color="196,64,64"/>
</alloc_child>
```
