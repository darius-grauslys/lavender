PLATFORM_initialize_rendering__game — core/include/platform.h, line 127

Resets the SDL graphics sub-context wrapper's rendering hook to a clean state and delegates to the backend's worldspace-rendering initializer; on non-rendering backends it is a no-op stub. No core implementation exists — this is a platform-dependent function implemented per-backend.

Pre-conditions:
1. `gfx_context` (SDL impl: `p_PLATFORM_gfx_context`) must be a non-null pointer to a writable, backend-allocated `PLATFORM_Gfx_Context`. No null-pointer validation is performed — per codebase convention (low-level platform-backend function), the caller is responsible for passing a valid context.
2. The `SDL_Gfx_Sub_Context__Wrapper` within the context must have been previously initialized via the backend's gfx-context setup (e.g. `SDL_initialize_gfx_context` / `_SDL_link_opengl_3_0`) so that the `f_SDL_initialize_rendering__worldspace` hook is assigned. If the hook is null, calling this function is undefined behavior.
3. The header comment (platform.h lines 123-126) notes "On NDS, this will init both main and sub." — on the NDS backend the function is invoked from `nds_game.c:34` (via `NDS_initialize_gfx_context`) to initialize both the main and sub graphics cores.
4. The function is marked `// TODO: remove` (platform.h line 126), indicating deprecation; downstream reports note rendering init has been inlined into `PLATFORM_initialize_game` for SDL.

Post-conditions:
1. SDL backend: delegates to the backend's `f_SDL_initialize_rendering__worldspace` hook (currently `GL_initialize_rendering__worldspace`), which retrieves the GL sub-context from the `PLATFORM_Gfx_Context`. The OpenGL hook is currently an effective no-op (fetches the sub-context pointer but performs no further setup).
2. SDL/no_gui/test backends: on no_gui the function is not defined separately (rendering init is not applicable). On test stubs it is an empty no-op; the context is left unmodified.
3. Returns `void` (no return value / status code).

Correctness Verdict: Incorrect

Semantic Alignment:
The function's intent — initializing the rendering subsystem for the game — is correctly identified and delegated through the SDL hook mechanism. The hook-delegation pattern itself is sound and consistent with how other SDL sub-context operations are wired (fetch hook from wrapper, assert non-null, call hook). However, the SDL reference implementation contains correctness defects that prevent it from reliably fulfilling its semantic intent (see Implementation Correctness below). On backends where it is a stub/no-op or not defined, the semantics are trivially satisfied.

Semantic classification (Lavender-specific — initialization != RAII):
This function performs RAII-style platform resource setup (initializing the rendering subsystem / graphics context), NOT Lavender-style struct initialization or pool cleanup. This is legitimate and expected at the platform-abstraction layer, as noted in the sibling `PLATFORM_initialize_audio` review: "At the platform-abstraction layer, resource setup is necessary and legitimate; the 'initialization != RAII' principle governs core-engine struct lifecycle, not platform resource setup." The header `platform.h` (lines 13-19) explicitly states these `PLATFORM_*` functions are platform-dependent and "NOT implemented in core." The `// TODO: remove` marker indicates the function is deprecated, with rendering init being moved inline into `PLATFORM_initialize_game`.

Implementation Correctness:
- Type compatibility: parameter `PLATFORM_Gfx_Context *gfx_context` (declaration) / `PLATFORM_Gfx_Context *p_PLATFORM_gfx_context` (SDL impl) — pointer to the same struct type; no conversion issues. The local variable `f_SDL_initialize_rendering__worldspace` (of type `f_SDL_Initialize_Rendering__Worldspace`, a `void (*)(PLATFORM_Gfx_Context *)` function pointer) is assigned from `p_PLATFORM_gfx_context->SDL_gfx_sub_context__wrapper.f_SDL_initialize_rendering__worldspace` (same typedef) and invoked with the same `PLATFORM_Gfx_Context *` argument — types match exactly.
- Undefined behavior — two issues found:
  (a) No null check on `p_PLATFORM_gfx_context` before dereferencing it (sdl_gfx_context.c lines 280-282 and the `SDL_ASSERT_HOST_NULL` macro itself dereference `p_PLATFORM_gfx_context`). If NULL is passed, the behavior is undefined (null pointer dereference). The `SDL_ASSERT_HOST_NULL` macro expands to `(!p_PLATFORM_gfx_context->SDL_gfx_sub_context__wrapper.f_hook)`, which also dereferences `p_PLATFORM_gfx_context` — so it cannot catch a null context.
  (b) The `SDL_ASSERT_HOST_NULL` macro result is discarded: it is used as a standalone statement (`SDL_ASSERT_HOST_NULL(...)` at sdl_gfx_context.c line 284), but the macro only evaluates a boolean expression `(!...->f_hook)` and the result is thrown away. In debug builds, the hook-null condition is computed but no action is taken. In release builds (`NDEBUG` defined), the macro expands to nothing, so the hook is never validated. If the hook is null (e.g. gfx context not fully initialized), line 289 (`f_SDL_initialize_rendering__worldspace(p_PLATFORM_gfx_context)`) dereferences a null function pointer — undefined behavior. The developer likely intended `SDL_DEBUG_ABORT_IF__HOOK_NULL` (which wraps the check in an `if` that warns and returns) instead of `SDL_ASSERT_HOST_NULL`.
- Validation: none is performed — consistent with the low-level platform-backend convention, but the ineffective hook check means a misconfigured context is not caught. The correct macro (`SDL_DEBUG_ABORT_IF__HOOK_NULL`) should be used to abort and return early if the hook is unconfigured.

Side Effects:
- SDL backend: invokes the `f_SDL_initialize_rendering__worldspace` hook (currently `GL_initialize_rendering__worldspace`), which reads the GL sub-context from `p_PLATFORM_gfx_context`. Currently this produces no observable state change (the OpenGL hook fetches the sub-context pointer but does not mutate it or configure any GL state). In a fully implemented backend, this would configure viewport/rendering state for the worldspace.
- SDL backend: the local variable `f_SDL_initialize_rendering__worldspace` is a stack copy of the hook pointer — transient, no persistent side effect.
- no_gui backend: not defined; no side effects.
- Test stubs: empty no-ops; no side effects.
- The function does not modify the `PLATFORM_Gfx_Context` struct itself (it only reads the wrapper's hook and delegates).
