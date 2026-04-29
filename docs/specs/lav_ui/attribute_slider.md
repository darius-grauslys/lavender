# `<slider>` — Slider Initialization

## Overview

The `<slider>` element initializes the current UI element as a slider. It allocates a hitbox, sets a tile span, configures the sliding range and drag handler, and creates a child button element with a sprite for the slider thumb. It must appear as a child of `<allocate_ui>`.

## 1. Attributes

| Attribute | Required | Default | Description |
|---|---|---|---|
| `x` | No | `0` | Horizontal position in pixels from parent context. |
| `y` | No | `0` | Vertical position in pixels from parent context. |
| `width` | Yes | — | Width of the slider hitbox in pixels. |
| `height` | Yes | — | Height of the slider hitbox in pixels. |
| `spanning_width` | No | `"0"` | Horizontal span range of the slider in pixels. |
| `spanning_height` | No | `"0"` | Vertical span range of the slider in pixels. |
| `spanning_depth` | No | `"0"` | Depth span (unused in 2D). |
| `span` | Yes | — | C function name that populates a `UI_Tile_Span` struct. Example: `"get_ui_tile_span_for__ag_slider__vertical"`. |
| `m_Dragged_Handler` | No | `"m_ui_slider__dragged_handler__default"` | C function name for the drag handler callback. |
| `snapped_x_or__y` | No | `"true"` | Whether the slider snaps to axis. |
| `color` | No | `"55,55,55"` | RGB color for visual editor preview. |
| `size_of__texture` | No | `"8x8"` | Texture size for the slider thumb sprite. Format: `"WxH"`. Also determines the thumb button hitbox size. |
| `name_of__texture` | No | `"MISSING_TEXTURE_NAME"` | Aliased texture name for the slider thumb sprite. |
| `index_of__sprite_frame` | No | `"0"` | Initial sprite frame index for the thumb. |

## 2. Generated C Output

### 2.1. Hitbox and Tile Span

```c
allocate_hitbox_for__ui_element(p_game, p_gfx_window, <name>, <w>, <h>, get_vector__3i32(...));
UI_Tile_Span ui_tile_span__<name>;
<span>(&ui_tile_span__<name>);
set_ui_tile_span_of__ui_element(<name>, &ui_tile_span__<name>);
```

### 2.2. Slider Initialization

```c
initialize_ui_element_as__slider(
    <name>,
    get_vector__3i32(<spanning_width>, <spanning_height>, <spanning_depth>),
    <m_Dragged_Handler>,
    <snapped_x_or__y>);
```

### 2.3. Thumb Button (Auto-Generated Child)

A child `UI_Element` is automatically allocated, given a texture/sprite, hitbox, and parented to the slider.

## 3. Example

```xml
<allocate_ui name="p_slider">
    <slider x="228" y="132" width="16" height="80"
        spanning_height="176"
        span="get_ui_tile_span_for__ag_slider__vertical"
        m_Dragged_Handler="m_ui_slider__dragged_handler__gfx_window__default"
        size_of__texture="16x16"
        name_of__texture="name_of__texture__ui_sprites__16x16"/>
</allocate_ui>
```
