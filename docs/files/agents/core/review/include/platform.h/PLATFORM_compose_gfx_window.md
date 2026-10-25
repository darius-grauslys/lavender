# PLATFORM_compose_gfx_window

- **Function name:** `PLATFORM_compose_gfx_window`
- **File of origin:** `core/include/platform.h` (declaration, line 229)

## Semantic

Per-window platform backend hook that composes (renders) a graphics window's
tile buffer into the active backend. It is invoked by
`f_graphics_window__default_compose` (in
`core/source/rendering/graphics_window.c:512`) for each window flagged
`GRAPHICS_WINDOW__FLAG__COMPOSE__DIRTY`, after the dirty flag has already been
cleared by the caller. The header doc comment states it "renders the window
buffer (or equivalent there of) via tiles."

## Pre-conditions

1. `p_game` is non-null; used to resolve the `Gfx_Context` / gfx sub-context.
2. `p_gfx_window` is non-null and refers to a valid, initialized `Graphics_Window`.
3. The active backend's gfx sub-context and compose callback have been set up
   (the SDL backend debug-aborts in builds with `NDEBUG` undefined if
   `f_SDL_compose_gfx_window == 0`).

## Post-conditions

1. The window's backing tile buffer is rendered/composed into its texture for the
   active backend (SDL); this matches the documented "renders the window buffer
   ... via tiles" intent.
2. This function does **not** clear `GRAPHICS_WINDOW__FLAG__COMPOSE__DIRTY` —
   that is done by the caller `f_graphics_window__default_compose` before
   dispatching into this hook, and the dispatch loop in
   `core/source/rendering/graphics_window_manager.c:761` only calls the hook
   when the window is flagged dirty.
3. `no_gui` backend: no state change (empty no-op stub).

## Correctness Verdict

Correct

## Semantic Alignment

The header declaration and its doc comment are consistent with the primary
implementation. The SDL backend (`sdl/source/rendering/sdl_gfx_window.c:104`)
forwards to `SDL_compose_gfx_window`, which dispatches through the gfx
sub-context's `f_SDL_compose_gfx_window` callback — i.e., the actual tile
rendering is performed by the backend, matching the documented intent.

Initialization note: `compose` here means rendering/composition, not
initialization; the Lavender "initialization != RAII" caveat is therefore not
applicable (no resource acquisition or struct reset occurs).

## Implementation Correctness

- **Type compatibility:** The header signature
  `void PLATFORM_compose_gfx_window(Game *, Graphics_Window *)` matches the SDL
  implementation and both test stubs (`tests/core/source/PLATFORM.c:270`,
  `tests/templates/source/PLATFORM.c:270`), which all use `Game *` as the first
  parameter.
- **Defect (cross-backend type mismatch):** The `no_gui/source/NOT_IMPL.c:46`
  stub declares the first parameter as `Gfx_Context *p_gfx_context` rather than
  the header-declared `Game *`. This violates prototype type compatibility. It
  is not a C constraint violation at compile time only because `NOT_IMPL.c`
  includes `defines.h` and not `platform.h` (so no conflicting declaration is
  visible in that translation unit), and the body is a no-op so the mismatched
  pointer is never dereferenced. It should nonetheless be corrected to `Game *`
  for consistency and to avoid latent linkage/UB issues if the declaration
  becomes visible alongside the definition.
- **Undefined behavior:** None in the reviewed declaration / forwarding path —
  no null dereference, out-of-bounds access, or type punning. The SDL backend
  guards the function-pointer dispatch in debug builds.
- **Validation:** None performed within the function itself — appropriate, since
  validation is the caller's responsibility
  (`compose_graphic_windows_in__graphics_window_manager` checks `p_gfx_window`
  and the function pointer before dispatch).

## Side Effects

- **SDL backend:** invokes the gfx sub-context's `f_SDL_compose_gfx_window`
  callback via `SDL_compose_gfx_window`, which renders the window's tile buffer
  to its backing texture (observable: GPU / window texture state).
- **`no_gui` backend:** no side effects (empty stub).

(Callees are not traced beyond their documented contract, per the review
scope.)
