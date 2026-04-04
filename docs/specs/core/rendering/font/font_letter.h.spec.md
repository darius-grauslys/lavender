# Specification: core/include/rendering/font/font_letter.h

## Overview

Provides a convenience macro for declaring `Font_Letter` compound literals.
Contains no functions.

## Dependencies

- `defines.h` (for `Font_Letter` struct, `MASK` macro)

## Types

### Font_Letter (struct)

    typedef struct Font_Letter_t {
        Quantity__u8 width_of__font_letter       :4;
        Quantity__u8 height_of__font_letter      :4;
        Quantity__u8 x__offset_of__font_letter   :4;
        Quantity__u8 y__offset_of__font_letter   :4;
        Index__u16 index_of__character__in_font  :16;
    } Font_Letter;

| Field | Type | Description |
|-------|------|-------------|
| `width_of__font_letter` | `u8` (4 bits) | Glyph width in pixels (0-15). |
| `height_of__font_letter` | `u8` (4 bits) | Glyph height in pixels (0-15). |
| `x__offset_of__font_letter` | `u8` (4 bits) | Horizontal offset in pixels (0-15). |
| `y__offset_of__font_letter` | `u8` (4 bits) | Vertical offset in pixels (0-15). |
| `index_of__character__in_font` | `u16` (16 bits) | Index into the font's texture atlas. |

## Macros

### DECLARE_FONT_LETTER

    #define DECLARE_FONT_LETTER(letter, width, height, x__offset, y__offset) \
        (Font_Letter){ \
            width & MASK(4), \
            height & MASK(4), \
            (x__offset & MASK(4)), \
            (y__offset & MASK(4)), \
            letter }

Creates a `Font_Letter` compound literal. All dimension values are masked
to 4 bits (0-15 range).

**Parameters:**
- `letter` — `Index__u16` index of the character in the font texture.
- `width` — glyph width in pixels (0-15).
- `height` — glyph height in pixels (0-15).
- `x__offset` — horizontal offset in pixels (0-15).
- `y__offset` — vertical offset in pixels (0-15).

## Functions

None.

## Agentic Workflow

### Relationships

- `Font_Letter` entries populate `Font.font_lookup_table[]`.
- Used by `Typer` to compute cursor advancement and rendering positions.
- Typically used in font initialization code.

## Header Guard

`FONT_LETTER_H`
