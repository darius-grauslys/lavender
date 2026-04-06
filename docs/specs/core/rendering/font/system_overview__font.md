# 1. System Overview: Font and Text Rendering

## 1.1 Purpose

The font subsystem provides bitmap font management and text layout. It maps
ASCII character codes to glyph descriptors (`Font_Letter`), manages a pool
of `Font` instances via `Font_Manager`, and provides a `Typer` text layout
engine that renders character strings into either a `Texture` or a
`PLATFORM_Graphics_Window` with cursor wrapping and line spacing.

## 1.2 Architecture

### 1.2.1 Data Hierarchy

    Gfx_Context
    +-- Font_Manager
    |   +-- Font[0..MAX_QUANTITY_OF__FONT-1]
    |       +-- Font_Letter font_lookup_table[256]  (indexed by ASCII code)
    |       |   +-- width_of__font_letter       (4 bits, 0-15 pixels)
    |       |   +-- height_of__font_letter      (4 bits, 0-15 pixels)
    |       |   +-- x__offset_of__font_letter   (4 bits, 0-15 pixels)
    |       |   +-- y__offset_of__font_letter   (4 bits, 0-15 pixels)
    |       |   +-- index_of__character__in_font (16 bits, atlas index)
    |       |
    |       +-- Texture texture_of__font  (font atlas)
    |       +-- Quantity__u8 max_width_of__font_letter
    |       +-- Quantity__u8 max_height_of__font_letter
    |       +-- Font_Flags (IS_ALLOCATED)

    Typer (embedded in UI_Element or standalone)
    +-- Hitbox_AABB text_bounding_box  (defines text area position and dimensions)
    +-- Vector__3i32 cursor_position__3i32
    +-- Font *p_font  --> references Font in Font_Manager
    +-- union {
    |       Texture texture_of__typer_target
    |       PLATFORM_Graphics_Window *p_PLATFORM_graphics_window__typer_target
    |   }
    +-- Quantity__u16 quantity_of__space_in__pixels_between__lines
    +-- bool is_using_PLATFORM_texture_or__PLATFORM_graphics_window

### 1.2.2 Key Types

| Type | Role |
|------|------|
| `Font_Manager` | Fixed-size pool of `Font` instances. Owned by `Gfx_Context`. |
| `Font` | Lookup table mapping ASCII codes (0-255) to `Font_Letter` glyph descriptors, paired with a texture atlas. |
| `Font_Letter` | Compact glyph descriptor: width, height, x/y offsets (4 bits each), and a 16-bit index into the font's texture atlas. |
| `Font_Flags` | Single-bit flag indicating allocation state (`FONT_FLAG__IS_ALLOCATED`). |
| `Typer` | Text layout engine. Maintains a bounding box (as `Hitbox_AABB`), cursor position, font reference, and render target. Handles cursor advancement and line wrapping. |

### 1.2.3 Limits

| Macro | Default | Description |
|-------|---------|-------------|
| `MAX_QUANTITY_OF__FONT` | 8 | Maximum fonts in pool. |
| `FONT_LETTER_MAX_QUANTITY_OF` | 256 | One glyph entry per ASCII code. |
| `FONT_SMALL__MAX_WIDTH` | 4 | Small font max glyph width (pixels). |
| `FONT_SMALL__MAX_HEIGHT` | 6 | Small font max glyph height (pixels). |
| `FONT_LARGE__MAX_WIDTH` | 8 | Large font max glyph width (pixels). |
| `FONT_LARGE__MAX_HEIGHT` | 8 | Large font max glyph height (pixels). |

## 1.3 Glyph Descriptor Layout

Each `Font_Letter` is a compact bitfield structure totaling 32 bits:

    Font_Letter (32 bits total):
    +--------+--------+--------+--------+------------------+
    | width  | height | x_off  | y_off  | atlas_index      |
    | 4 bits | 4 bits | 4 bits | 4 bits | 16 bits          |
    +--------+--------+--------+--------+------------------+

- **Width and height:** glyph dimensions in pixels (0-15).
- **X/Y offset:** rendering offset from cursor position (0-15).
- **Atlas index:** position of the glyph in the font's texture atlas.

The `DECLARE_FONT_LETTER` macro creates `Font_Letter` compound literals
with all dimension values masked to 4 bits via the `MASK(4)` macro.

## 1.4 Font Lifecycle

### 1.4.1 Initialization

    initialize_font_manager(&gfx_context.font_manager)
      -> All Font slots: font_flags cleared (deallocated).
      -> All Font_Letter entries: zeroed.

### 1.4.2 Font Allocation

    Font *p_font = allocate_font_from__font_manager(&font_manager)
      -> Finds first deallocated slot.
      -> Sets FONT_FLAG__IS_ALLOCATED.
      -> Returns Font* or null if pool exhausted.

### 1.4.3 Font Population

    initialize_font(p_font)
      -> Zeroes all Font_Letter entries and clears state.

    For each character the font supports:
      initialize_font__letter(
          &p_font->font_lookup_table[ascii_code],
          width, height, x_offset, y_offset, atlas_index)

    Or using the convenience macro:
      p_font->font_lookup_table['A'] =
          DECLARE_FONT_LETTER(atlas_index, width, height, x_offset, y_offset);

    Assign the font's texture atlas:
      p_font->texture_of__font = loaded_texture;
      p_font->max_width_of__font_letter = max_width;
      p_font->max_height_of__font_letter = max_height;

### 1.4.4 Font Release

    release_font_from__font_manager(&font_manager, p_font)
      -> Clears FONT_FLAG__IS_ALLOCATED.
      -> Slot becomes available for reuse.

## 1.5 Typer Lifecycle

### 1.5.1 Initialization

    initialize_typer(
        &typer,
        x, y,                // bounding box position
        width, height,       // bounding box dimensions
        line_spacing,        // pixels between lines
        cursor_x, cursor_y)  // initial cursor position

    Note: initialize_typer does NOT set the font.

    Or with font (static inline wrapper):
      initialize_typer_with__font(
          &typer, x, y, w, h, spacing, cx, cy, p_font)
        -> Calls initialize_typer then assigns p_font.

### 1.5.2 Render Target Assignment

The typer renders into one of two target types, selected via a union:

    Texture target:
      set_PLATFORM_texture_target_for__typer(&typer, texture)
        -> is_using_PLATFORM_texture_or__PLATFORM_graphics_window = true

    Graphics window target:
      set_PLATFORM_graphics_window_target_for__typer(&typer, p_gfx_window)
        -> is_using_PLATFORM_texture_or__PLATFORM_graphics_window = false

    Query target type:
      is_typer_targetting__PLATFORM_texture(&typer)       -> true if texture
      is_typer_targetting__PLATFORM_graphics_window(&typer) -> true if gfx window

### 1.5.3 Text Output

    put_c_string_in__typer(gfx_context, &typer, "Hello", 5)
      -> For each character in the string:

         1. get_p_font_letter_from__typer(&typer, character)
            -> Returns &p_font->font_lookup_table[character]

         2. poll_typer_for__cursor_wrapping(&typer, p_font_letter)
            -> If cursor_x + glyph_width > bounding_box_width:
               -> cursor_x = 0
               -> cursor_y += line_spacing
               -> Returns true (wrapped)
            -> Otherwise returns false

         3. PLATFORM_put_char_in__typer(gfx_context, typer, character)
            -> Platform renders the glyph at cursor position
               into the active render target

         4. offset_typer_by__font_letter(&typer, p_font_letter)
            -> cursor_x += font_letter.width_of__font_letter

### 1.5.4 Cursor Management

    set_typer__cursor(&typer, position)
      -> Sets cursor position directly.

    reset_typer_cursor(&typer)
      -> Resets cursor to (0, 0, 0).

    set_typer__position(&typer, position)
      -> Moves bounding box origin via set_hitbox_aabb__position_with__3i32.

    set_typer__bounding_box_size(&typer, width, height)
      -> Resizes text area via set_size_of__hitbox_aabb.

## 1.6 Integration Points

### 1.6.1 Ownership

- `Font_Manager` is owned by `Gfx_Context` at `gfx_context.font_manager`.
- Accessed via `get_p_font_manager_from__gfx_context`.
- `Typer` instances are typically embedded in `UI_Element` (text/text box
  elements) or created on the stack for one-shot rendering.

### 1.6.2 Dependencies on Other Subsystems

- `Typer` uses `Hitbox_AABB` from the collision system for its bounding box
  geometry. This provides position and dimension storage without requiring
  collision detection.
- `Font` holds a `Texture` for its atlas, which wraps a `PLATFORM_Texture*`
  managed by the `Aliased_Texture_Manager` or allocated directly.

### 1.6.3 Platform Integration

| Platform Function | Purpose |
|-------------------|---------|
| `PLATFORM_put_char_in__typer` | Renders a single glyph at the typer's cursor position into the active render target (texture or graphics window). |

## 1.7 Capacity Constraints

- The `Font_Manager` holds at most `MAX_QUANTITY_OF__FONT` (8) fonts
  simultaneously. Each font consumes a fixed 256-entry lookup table
  regardless of how many characters are actually defined.
- Glyph dimensions are limited to 0-15 pixels per axis due to the 4-bit
  bitfield encoding. The predefined size constants (`FONT_SMALL__MAX_*`,
  `FONT_LARGE__MAX_*`) reflect typical usage within these limits.
- The `Typer` bounding box dimensions and cursor position use full 32-bit
  integer coordinates, so text area size is not constrained by the glyph
  bitfield limits.
