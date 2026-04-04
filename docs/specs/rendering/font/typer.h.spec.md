# Specification: core/include/rendering/font/typer.h

## Overview

Defines operations on `Typer` — a text layout engine that renders character
strings into either a `Texture` or a `PLATFORM_Graphics_Window` using a
`Font`. The typer maintains a bounding box, cursor position, and line
spacing for text wrapping.

## Dependencies

- `defines_weak.h` (forward declarations)
- `defines.h` (for `Typer`, `Font`, `Font_Letter`, `Hitbox_AABB`, `Texture`, `PLATFORM_Graphics_Window`)
- `collisions/core/aabb/hitbox_aabb.h` (for `set_hitbox_aabb__position_with__3i32`, `set_size_of__hitbox_aabb`)
- `vectors.h` (for `Vector__3i32`, `get_vector__3i32`)

## Types

### Typer (struct)

    typedef struct Typer_t {
        Hitbox_AABB text_bounding_box;
        Vector__3i32 cursor_position__3i32;
        Font *p_font;
        union {
            Texture texture_of__typer_target;
            PLATFORM_Graphics_Window *p_PLATFORM_graphics_window__typer_target;
        };
        Quantity__u16 quantity_of__space_in__pixels_between__lines;
        bool is_using_PLATFORM_texture_or__PLATFORM_graphics_window;
    } Typer;

| Field | Type | Description |
|-------|------|-------------|
| `text_bounding_box` | `Hitbox_AABB` | Defines the text area position and dimensions for cursor wrapping. |
| `cursor_position__3i32` | `Vector__3i32` | Current cursor position relative to bounding box origin. |
| `p_font` | `Font*` | The font used for rendering. |
| `texture_of__typer_target` | `Texture` | Render target (union, active when texture mode). |
| `p_PLATFORM_graphics_window__typer_target` | `PLATFORM_Graphics_Window*` | Render target (union, active when graphics window mode). |
| `quantity_of__space_in__pixels_between__lines` | `Quantity__u16` | Line spacing in pixels. |
| `is_using_PLATFORM_texture_or__PLATFORM_graphics_window` | `bool` | `true` = texture target, `false` = graphics window target. |

## Functions

### Initialization

| Function | Signature | Description |
|----------|-----------|-------------|
| `initialize_typer` | `(Typer*, i32 x, i32 y, u32 width, u32 height, u32 spacing, i32 x_cursor, i32 y_cursor) -> void` | Initializes with bounding box position/size, line spacing, and initial cursor. Font is NOT set. |
| `initialize_typer_with__font` | `(Typer*, i32 x, i32 y, u32 width, u32 height, u32 spacing, i32 x_cursor, i32 y_cursor, Font*) -> void` | Calls `initialize_typer` then assigns the font. (static inline) |

### Text Rendering

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `poll_typer_for__cursor_wrapping` | `(Typer*, Font_Letter*) -> bool` | `bool` | Checks if the next character would exceed bounding box width and wraps to next line if needed. Returns `true` if wrapping occurred. |
| `put_c_string_in__typer` | `(Gfx_Context*, Typer*, const char*, Quantity__u32) -> void` | `void` | Renders a string through the typer, calling `PLATFORM_put_char_in__typer` for each character. |

### Position and Size (static inline)

| Function | Signature | Description |
|----------|-----------|-------------|
| `set_typer__position` | `(Typer*, Vector__3i32) -> void` | Sets the bounding box position via `set_hitbox_aabb__position_with__3i32`. |
| `set_typer__bounding_box_size` | `(Typer*, u32 width, u32 height) -> void` | Sets the bounding box dimensions via `set_size_of__hitbox_aabb`. |
| `set_typer__cursor` | `(Typer*, Vector__3i32) -> void` | Sets the cursor position directly. |
| `reset_typer_cursor` | `(Typer*) -> void` | Resets cursor to `(0, 0, 0)`. |

### Cursor Advancement (static inline)

| Function | Signature | Description |
|----------|-----------|-------------|
| `offset_typer_by__font_letter` | `(Typer*, Font_Letter*) -> void` | Advances cursor X by the font letter's width. |

### Font Access (static inline)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `get_p_font_letter_from__typer` | `(Typer*, unsigned char) -> Font_Letter*` | `Font_Letter*` | Returns the `Font_Letter` for the given character from the typer's font. |

### Render Target (static inline)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `set_PLATFORM_texture_target_for__typer` | `(Typer*, Texture) -> void` | `void` | Sets the typer to render into a texture. Sets `is_using_PLATFORM_texture_or__PLATFORM_graphics_window = true`. |
| `set_PLATFORM_graphics_window_target_for__typer` | `(Typer*, PLATFORM_Graphics_Window*) -> void` | `void` | Sets the typer to render into a graphics window. Sets `is_using_PLATFORM_texture_or__PLATFORM_graphics_window = false`. |
| `is_typer_targetting__PLATFORM_texture` | `(Typer*) -> bool` | `bool` | True if rendering to texture. |
| `is_typer_targetting__PLATFORM_graphics_window` | `(Typer*) -> bool` | `bool` | True if rendering to graphics window. |

## Agentic Workflow

### Relationships

- Embedded in `UI_Element` (text union member) for text/text box elements.
- Uses `Font` for glyph lookup (see `font.h`).
- Renders via `PLATFORM_put_char_in__typer` (platform function).
- Bounding box is a `Hitbox_AABB` (see `hitbox_aabb.h`).

### Preconditions

- All functions require non-null `p_typer`.
- `initialize_typer` does NOT set the font — use `initialize_typer_with__font`
  or assign `p_font` manually.

## Header Guard

`TYPER_H`
