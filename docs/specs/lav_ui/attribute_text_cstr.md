# `<text_cstr>` — Static Text Element Initialization

## Overview

The `<text_cstr>` element initializes the current UI element as a static text label using a constant C string. It sets a font, text content, a centered transform handler, and allocates a hitbox. It must appear as a child of `<allocate_ui>`, `<allocate_ui_container>`, or `<alloc_child>`.

## 1. Attributes

| Attribute | Required | Default | Description |
|---|---|---|---|
| `x` | No | `0` | Horizontal offset in pixels from parent context. |
| `y` | No | `0` | Vertical offset in pixels from parent context. |
| `width` | Yes | — | Width of the text element hitbox in pixels. |
| `height` | Yes | — | Height of the text element hitbox in pixels. |
| `color` | No | `"55,55,55"` | RGB color for visual editor preview. |
| `text` | Yes | — | The constant C string to display. |
| `font` | Yes | — | C expression that returns a `Font *`. |
| `transform_handler` | No | `"m_ui_element__transformed_handler__text__centered"` | C function name for the transform handler callback. |

## 2. Generated C Output

```c
initialize_ui_element_as__text_with__const_c_str(
    <p_ui_element>,
    <font>,
    <text>,
    strnlen(<text>, 32));
set_ui_element__transformed_handler(
    <p_ui_element>,
    <transform_handler>);
allocate_hitbox_for__ui_element(
    p_game, p_gfx_window, <p_ui_element>,
    <width>, <height>,
    get_vector__3i32(<x>, <y>, 0));
```

## 3. Required Config Signature

```xml
<ui_func_signature for="text_cstr" c_signatures="initialize_ui_element_as__text_with__const_c_str"/>
```

## 4. Example

```xml
<allocate_ui name="p_label__title">
    <text_cstr width="104" height="32" text="\"Settings\""
        font="get_AG_font__large()"/>
</allocate_ui>
```

```xml
<alloc_child>
    <text_cstr width="80" height="24" text="\"Resume\"" font="get_AG_font__large()"
        transform_handler="m_ui_element__transformed_handler__text__centered"/>
</alloc_child>
```
