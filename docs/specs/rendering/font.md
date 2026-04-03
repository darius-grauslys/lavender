# Font Specification

## File
`core/include/rendering/font/font.h`

## Purpose
Defines operations on `Font` — a lookup table mapping ASCII character codes
to `Font_Letter` glyph descriptors, paired with a texture atlas.

## Dependencies
| Header | Purpose |
|--------|---------|
| `defines.h` | `Font`, `Font_Letter`, `Font_Flags`, `Texture` |

## Types

### `Font` (defined in `defines.h`)
