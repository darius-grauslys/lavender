## 1. Header

- **Function name:** `PLATFORM_project_gfx_window`
- **File of origin:** `core/include/platform.h` (declaration, line 256). Stub implementations: `tests/templates/source/PLATFORM.c` (line 286) and `tests/core/source/PLATFORM.c` (line 286).

## 2. Semantic

Renders/draws a `Graphics_Window`'s buffer via 3D projection. It is a platform abstraction-layer hook invoked alongside the other `PLATFORM_*_gfx_window` rendering stages.

## 3. Pre-conditions

1. `p_game` points to a valid, initialized `Game`. The PLATFORM rendering convention (cf. `SDL_compose_gfx_window`, which dereferences it via `get_p_gfx_context_from__game`) requires it; it is not null-checked and may not be null.
2. `p_gfx_window` points to a valid, prepared `Graphics_Window`. It is not null-checked by the stubs and may not be null.
3. A platform graphics backend that supports 3D projection must be configured for the call to be effective; otherwise the function is satisfied by an empty stub (no-op).

## 4. Post-conditions

1. Returns `void` (no return value).
2. Intended: the gfx window's buffer is projected and rasterized to the window surface.
3. In every currently available implementation (test stubs in `tests/templates/source/PLATFORM.c` and `tests/core/source/PLATFORM.c`), the body is empty, so there is no observable state change — the call is a no-op.

## 5. Correctness Verdict

**Correct**

## 6. Semantic Alignment

The header documents the intent ("renders the window buffer via 3D projection") and the parameter list matches the sibling `PLATFORM_*_gfx_window` functions. However, the semantic intent is *not fulfilled* by any available implementation: the test stubs are empty no-ops and no platform backend (SDL, no_gui, NDS) implements `PLATFORM_project_gfx_window`. The docstring's `TODO: add a LAVENDER_FEATURE__GFX_WINDOW__PROJECTION` and the absence of an SDL implementation are mutually consistent — the projection stage is a declared-but-unimplemented feature. Note: `agents/platform_api.md:378` is inaccurate, claiming an SDL implementation at `sdl_gfx_window.c:128`; line 128 is in fact `PLATFORM_render_gfx_window`.

## 7. Implementation Correctness

- **Type compatibility:** Exact. The stub parameters `Game *p_game` and `Graphics_Window *p_gfx_window` match the declaration in `core/include/platform.h:256`.
- **Undefined behavior:** None. The empty-bodied stubs ignore their parameters; unused parameters in C are not undefined behavior (at most a compile-time `-Wunused-parameter` warning, which does not occur for this codebase's placeholder pattern).
- **Validation:** The stubs perform no validation, which is appropriate for no-op placeholders; the siblings delegate to backend functions that do debug-only validation (e.g., `SDL_compose_gfx_window` guards the function pointer under `#ifndef NDEBUG`), so validation is a backend/caller concern here rather than a stub concern. There are no null dereferences, bad pointer arithmetic, or out-of-bounds access.

## 8. Side Effects

On the available stub implementations: **No side effects.** The function bodies are empty; both parameters are ignored and no global/engine state is read or mutated. (On a future real backend, per the documented semantic, it would rasterize the projected window surface — but no such implementation exists.)
