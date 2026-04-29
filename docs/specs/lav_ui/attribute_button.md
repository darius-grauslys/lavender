# `<button>` — Button Initialization

## Overview

The `<button>` element initializes the current UI element as a button. It sets up click handling, toggleability, hitbox allocation, and visual representation. It must appear as a child of `<allocate_ui>` or `<allocate_ui_container>`.

## 1. Attributes

| Attribute | Required | Default | Description |
|---|---|---|---|
| `x` | No | `0` | Horizontal offset in pixels from parent context. Used for hitbox positioning. |
| `y` | No | `0` | Vertical offset in pixels from parent context. Used for hitbox positioning. |
| `width` | Yes | — | Width of the button hitbox in pixels. |
| `height` | Yes | — | Height of the button hitbox in pixels. |
| `color` | No | `"55,55,55"` | RGB color tuple for visual editor preview. Format: `"R,G,B"`. |
| `m_Clicked_Handler` | No | `"m_ui_button__clicked_handler__default"` | C function name for the click handler callback. |
| `is_toggleable` | No | `"false"` | Whether the button can be toggled. String `"true"` or `"false"`. |
| `is_toggled` | No | `"false"` | Initial toggle state. String `"true"` or `"false"`. |

## 2. Generated C Output

```c
initialize_ui_element_as__button(
    <p_ui_element>,
    <m_Clicked_Handler>,
    <is_toggleable>,
    <is_toggled>);
allocate_hitbox_for__ui_element(
    p_game, p_gfx_window, <p_ui_element>,
    <width>, <height>,
    get_vector__3i32(<computed_x>, <computed_y>, 0));
```

## 3. Example

```xml
<allocate_ui name="p_button_setting__save">
    <button width="104" height="32" color="64,196,64"
        m_Clicked_Handler="m_ui_ag__handler__click__save"/>
</allocate_ui>
```
