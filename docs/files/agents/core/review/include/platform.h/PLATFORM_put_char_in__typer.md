# PLATFORM_put_char_in__typer

**Function name:** `PLATFORM_put_char_in__typer`
**File of origin:** `core/include/platform.h`

## Semantic

Renders a single font glyph (indexed by `letter`) onto the typer's target
texture/graphics-window at the current cursor position, and advances or wraps
the cursor. The `letter` value (`unsigned char`) is used directly as an index
into the font's 256-entry `font_lookup_table`.

## Pre-conditions

1. `p_gfx_context` must be non-null and point to an initialized `Gfx_Context`.
   The SDL backend dereferences it to reach
   `p_gfx_context->p_PLATFORM_gfx_context`.
2. `p_typer` must be non-null and initialized; its `p_font` member must be
   non-null.
3. `p_typer->p_font` must contain a valid `Font_Letter` at index `letter`.
   `FONT_LETTER_MAX_QUANTITY_OF` is 256 and `letter` is `unsigned char`
   (range 0–255), so every value is an in-bounds index — the font simply must
   be populated for the glyph in question.
4. The typer's target must be configured: either a `PLATFORM_Texture` with
   allocated pixel memory (`gfx` / `width`) or a
   `PLATFORM_Graphics_Window`, selected by
   `is_using_PLATFORM_texture_or__PLATFORM_graphics_window`.
5. The caller is responsible for any cursor-wrapping checks before invoking
   this function (see `put_c_string_in__typer` in
   `core/source/rendering/font/typer.c:139`).

## Post-conditions

1. The glyph for `letter` is rendered onto the typer's target at the current
   cursor position (`p_typer->cursor_position__3i32`).
2. `p_typer->cursor_position__3i32` may be advanced or wrapped, depending on
   the backend implementation.
3. For no-op backends (no_gui, test stubs): no observable state change.

## Correctness Verdict

Correct

## Semantic Alignment

The header declaration correctly specifies a function taking a high-level
`Gfx_Context *` (the wrapper that owns `p_PLATFORM_gfx_context`), a `Typer *`,
and an `unsigned char letter`. This is consistent with the sole caller,
`put_c_string_in__typer` (`core/source/rendering/font/typer.c:139`), which
passes a `Gfx_Context *`. The semantic intent — "put a character in the
typer" — is upheld by the declaration. The SDL, no_gui, and test backends all
honor this contract; the NDK backend does not (see Implementation Correctness).

## Implementation Correctness

- **Type compatibility:** The canonical declaration matches three of four
  backends (SDL, no_gui, test stubs) which all use
  `Gfx_Context *p_gfx_context`.
- **NDS backend discrepancy** (`nds/source/rendering/font/nds_typer.c:10`):
  the first parameter is declared as `PLATFORM_Gfx_Context *` instead of
  `Gfx_Context *`, conflicting with the prototype visible through
  `#include <platform.h>`. This is a type-compatibility violation and would
  produce a "conflicting types" diagnostic. The parameter is never used by the
  NDK body (it operates solely on `p_typer`), so there is no runtime
  dereferencing of the wrong type, but the mismatch remains.
- **Undefined symbol in NDK backend:** the body calls `move_typer_cursor()`
  (`nds_typer.c:109`). A search of the entire codebase finds no declaration or
  definition of this function anywhere, indicating the NDK backend is
  out of sync (likely a refactor renamed `move_typer_cursor` to
  `offset_typer_by__font_letter`, defined in
  `core/include/rendering/font/typer.h:78`). This backend will not link as
  written.
- **Out-of-bounds:** `letter` (`unsigned char`, 0–255) is always an in-bounds
  index into the 256-entry `font_lookup_table`. No out-of-bounds access.
- **Null dereference / validation:** the NDK body dereferences
  `p_typer->p_font` and `p_typer->p_PLATFORM_texture__typer_target` with no
  null checks; per the function's role, these are pre-conditions the caller
  must satisfy. The SDL backend performs a debug-mode null check on its
  function-pointer field.

## Side Effects

- Mutates the pixel memory of the typer's target texture
  (`p_typer->texture_of__typer_target.gfx`) by writing glyph pixels
  (NDS / SDL backends).
- May mutate `p_typer->cursor_position__3i32` (cursor advance/wrap). The NDK
  backend does this via the (undefined) `move_typer_cursor`; the high-level
  caller `put_c_string_in__typer` also advances the cursor separately via
  `offset_typer_by__font_letter` — note a potential double-advancement if the
  NDK backend were fixed without removing the caller's advance.
- SDL backend invokes a platform function pointer
  (`f_SDL_put_char_in__typer`) retrieved from
  `p_gfx_context->p_PLATFORM_gfx_context`.
- no_gui / test backends: no side effects (empty bodies).