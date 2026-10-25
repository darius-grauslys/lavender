## 1. Header

- **Function name:** `PLATFORM_project_world`
- **File of origin:** `core/include/platform.h`

## 2. Semantic

Renders world data via 3D projection onto the graphics window's framebuffer.

## 3. Pre-conditions

1. `p_game` must be non-null and point to a valid, initialized `Game` struct.
2. `p_gfx_window` must be non-null and point to a valid, initialized `Graphics_Window` struct whose rendering backend is initialized.
3. The graphics/rendering context must be active (3D projection capability must be available) before invoking this function in a real implementation.

## 4. Post-conditions

1. The projected world data is rendered into `Graphics_Window.p_PLATFORM_gfx_window`'s framebuffer/buffer.
2. Returns `void` (no return value).
3. `p_game` and `p_gfx_window` are read-consumed (state used for rendering; not structurally modified by the projection itself).

## 5. Correctness Verdict

`Incorrect`

## 6. Semantic Alignment

No production implementation exists. The only implementations found are empty stubs (`{}`) in:
- `tests/core/source/PLATFORM.c:290`
- `tests/templates/source/PLATFORM.c:290`

These do nothing and therefore do not fulfill the documented semantic intent of rendering world data via 3D projection.

Additionally:
- The declaration at `platform.h:260` has **no doc comment**, unlike its sibling `PLATFORM_project_gfx_window` (lines 252-255, which is documented "This renders the window buffer (or equivalent thereof) via 3D projection") and `PLATFORM_compose_world` (lines 244-250). This is an inconsistency in the header.
- The documentation in `agents/platform_api.md:380-384` claims an SDL implementation exists at `sdl/source/rendering/sdl_gfx_window.c`, but no such implementation is present — that SDL file only contains `PLATFORM_render_gfx_window` (line 128).
- No no_gui stub exists in `NOT_IMPL.c` (which contains stubs for other `PLATFORM_project_*` / `PLATFORM_compose_*` functions), and no NDS implementation exists.

## 7. Implementation Correctness

- The declaration's parameter types (`Game *p_game`, `Graphics_Window *p_gfx_window`) match the typedef'd function-pointer signature `f_PLATFORM_render_gfx_window` defined in `core/include/defines.h:2478-2480`. This ensures type compatibility with the function-pointer-based dispatch pattern used in the `Graphics_Window` struct (members `f_PLATFORM_compose_gfx_window` and `f_PLATFORM_render_gfx_window` at lines 2491-2492).
- The stub implementations in the test files have correct, compatible signatures — no implicit conversions, truncation, or type mismatches.
- No undefined behavior exists in the empty stubs.
- **Critical defect:** The function is declared in the header but never defined in any production backend (SDL, no_gui/NDS). Any production code that calls `PLATFORM_project_world` would produce a **linker error** (undefined reference). The symbol is unimplemented and cannot be dispatched.
- No input validation is present. This is consistent with the Lavender convention (validation is the caller's responsibility for low-level PLATFORM functions), but since there is no implementation, there is nothing to validate.

## 8. Side Effects

- Stub implementations: No side effects.
- Intended (documented) implementation: Would render to the `Graphics_Window`'s framebuffer (mutation of the window's render target), with potential transient graphics-context state changes (e.g., GPU shader/state binding). These are not realized because no real implementation exists.
- Only the function's own observable effects are described; callee sites are out of scope.
