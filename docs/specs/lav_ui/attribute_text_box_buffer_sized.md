# `<text_box>` — Text Box Element Initialization

## Overview

The `<text_box>` element initializes the current UI element as a text box with an allocated text buffer. It sets a font, buffer size, a centered transform handler, allocates a hitbox, and applies a tile span for bordered rendering. It must appear as a child of `<allocate_ui>`, `<allocate_ui_container>`, or `<alloc_child>`.

## 1. Attributes

| Attribute | Required | Default | Description |
|---|---|---|---|
| `x` | No | `0` | Horizontal offset in pixels from parent context. |
| `y` | No | `0` | Vertical offset in pixels from parent context. |
| `width` | Yes | — | Width of the text box hitbox in pixels. |
| `height` | Yes | — | Height of the text box hitbox in pixels. |
| `color` | No | `"55,55,55"` | RGB color for visual editor preview. |
| `buffer_size` | Yes | — | Size of the text buffer to allocate, in bytes. |
| `font` | Yes | — | C expression that returns a `Font *`. |
| `span` | Yes | — | C function name that populates a `UI_Tile_Span` struct for bordered rendering. |
| `transform_handler` | No | `"m_ui_element__transformed_handler__text__centered"` | C function name for the transform handler callback. |

## 2. Generated C Output

```c
initialize_ui_element_as__text_box_with__buffer_size(
    <p_ui_element>,
    <font>,
    <buffer_size>);
set_ui_element__transformed_handler(
    <p_ui_element>,
    <transform_handler>);
allocate_hitbox_for__ui_element(
    p_game, p_gfx_window, <p_ui_element>,
    <width>, <height>,
    get_vector__3i32(<x>, <y>, 0));
UI_Tile_Span ui_tile_span__<p_ui_element>;
<span>(&ui_tile_span__<p_ui_element>);
set_ui_tile_span_of__ui_element(
    <p_ui_element>,
    &ui_tile_span__<p_ui_element>);
```

## 3. Required Config Signature

```xml
<ui_func_signature for="text_box" c_signatures="initialize_ui_element_as__text_box_with__buffer_size"/>
```

## 4. Example

```xml
<allocate_ui name="p_text_box__chat">
    <text_box width="120" height="32" buffer_size="128"
        font="get_AG_font__large()"
        span="get_ui_tile_span_for__ag_text_box"/>
</allocate_ui>
```

```xml
<allocate_ui_container size="4" stride__y="28">
    <text_box width="96" height="24" buffer_size="64"
        font="get_AG_font__large()/>
</allocate_ui_container>
```
