# Specification: core/include/rendering/font/font.h

## Overview

Defines operations on `Font` — a lookup table mapping ASCII character codes
to `Font_Letter` glyph descriptors, paired with a texture atlas.

## Dependencies

- `defines.h` (for `Font`, `Font_Letter`, `Font_Flags`, `Texture`)

## Types

### Font (struct)

    typedef struct Font_t {
        Font_Letter font_lookup_table[FONT_LETTER_MAX_QUANTITY_OF];
        Texture texture_of__font;
        Quantity__u8 max_width_of__font_letter;
        Quantity__u8 max_height_of__font_letter;
        Font_Flags font_flags;
    } Font;

| Field | Type | Description |
|-------|------|-------------|
| `font_lookup_table` | `Font_Letter[256]` | Glyph descriptors indexed by ASCII code. |
| `texture_of__font` | `Texture` | Font texture atlas. |
| `max_width_of__font_letter` | `Quantity__u8` | Maximum glyph width. |
| `max_height_of__font_letter` | `Quantity__u8` | Maximum glyph height. |
| `font_flags` | `Font_Flags` | Allocation flag. |

### Font_Flags (u8)

| Flag | Bit | Description |
|------|-----|-------------|
| `FONT_FLAG__IS_ALLOCATED` | 0 | Font is allocated. |

### Constants

| Macro | Value | Description |
|-------|-------|-------------|
| `FONT_LETTER_MAX_QUANTITY_OF` | `256` | One entry per ASCII code. |
| `FONT_SMALL__MAX_WIDTH` | `4` | Small font max glyph width. |
| `FONT_SMALL__MAX_HEIGHT` | `6` | Small font max glyph height. |
| `FONT_LARGE__MAX_WIDTH` | `8` | Large font max glyph width. |
| `FONT_LARGE__MAX_HEIGHT` | `8` | Large font max glyph height. |

## Functions

### Initialization

| Function | Signature | Description |
|----------|-----------|-------------|
| `initialize_font__letter` | `(Font_Letter*, u8 width, u8 height, u8 x_offset, u8 y_offset, u16 index) -> void` | Initializes a single font letter. |
| `initialize_font` | `(Font*) -> void` | Initializes a font to empty state with all letters zeroed. |

### Accessors (static inline)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `get_p_font_letter_from__font` | `(Font*, unsigned char) -> Font_Letter*` | `Font_Letter*` | Returns pointer to the `Font_Letter` for the given ASCII character. |
| `is_font__allocated` | `(Font*) -> bool` | `bool` | True if `IS_ALLOCATED` set. |
| `set_font_as__allocated` | `(Font*) -> void` | `void` | Sets `IS_ALLOCATED`. |
| `set_font_as__deallocated` | `(Font*) -> void` | `void` | Clears `IS_ALLOCATED`. |

## Agentic Workflow

### Ownership

Managed by `Font_Manager` (see `font_manager.h`). Referenced by `Typer`
(at `typer.p_font`).

### Preconditions

- All functions require non-null pointers.

## Header Guard

`FONT_H`
