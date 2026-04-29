# `<background>` (UI Element) — Background Element Initialization

## Overview

The `<background>` element (when used as a child of `<allocate_ui>` inside the `<ui>` tree, not to be confused with `<background>` inside `<config>`) initializes the current UI element as a background. This is a platform-specific element (SDL) that renders a background region.

**Note:** This is distinct from the `<background>` element inside `<config>`, which declares image layers for the visual editor.

## 1. Attributes

| Attribute | Required | Default | Description |
|---|---|---|---|
| `x` | No | `0` | Horizontal offset in pixels. |
| `y` | No | `0` | Vertical offset in pixels. |
| `width` | Yes | — | Width in pixels. |
| `height` | Yes | — | Height in pixels. |
| `p_gfx_window` | No | `"0"` | Pointer to a graphics window, or `0` for none. |

## 2. Generated C Output

```c
SDL_initialize_ui_element_as__background(
    <p_ui_element>,
    <width>, <height>,
    get_vector__3i32(<x>, <y>, 0),
    <p_gfx_window>);
```

## 3. Required Config Signature

```xml
<ui_func_signature for="background" c_signatures="SDL_initialize_ui_element_as__background"/>
```

## 4. Example

This element type is not commonly used directly in XML. It is available for platform-specific background rendering needs.
