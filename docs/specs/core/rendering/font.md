# 1. Font Specification

## 1.1 File
`core/include/rendering/font/font.h`

## 1.2 Purpose
Defines operations on `Font` — a lookup table mapping ASCII character codes
to `Font_Letter` glyph descriptors, paired with a texture atlas.

## 1.3 Dependencies
| Header | Purpose |
|--------|---------|
| `defines.h` | `Font`, `Font_Letter`, `Font_Flags`, `Texture` |

## 1.4 Types

### 1.4.1 `Font` (defined in `defines.h`)
