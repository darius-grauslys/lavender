PLATFORM_render_sprite — core/include/platform.h, line 117

Renders a sprite onto a graphics window at the given 3D position, delegating to the platform-specific rendering backend.

Pre-conditions:
1. p_gfx_context must be a non-null pointer to a valid, initialized Gfx_Context with a non-null PLATFORM_gfx_context sub-pointer.
2. p_gfx_window must be a non-null pointer to a valid Graphics_Window that has been opened/prepared for rendering.
3. p_sprite must be a non-null pointer to a valid Sprite object that has been previously allocated and initialized (including a valid PLATFORM_Sprite sub-struct and texture).
4. position_of__sprite__3i32F4 is any valid Vector__3i32F4 (32-bit fixed-point with 4 fractional bits per component); no range constraint is imposed by the function.

Post-conditions:
1. The sprite p_sprite is drawn onto the graphics window p_gfx_window at the screen-space position derived from position_of__sprite__3i32F4, subject to the platform backend's coordinate and rendering semantics.
2. The function returns void; no return value to inspect.
3. The input structs (p_gfx_context, p_gfx_window, p_sprite) and position_of__sprite__3i32F4 are not mutated by the canonical implementations.

Correctness Verdict: Correct

Semantic Alignment:
The function's semantic intent is to abstract away platform-specific sprite rendering behind a single platform-independent call. All canonical implementations (SDL, test template, no_gui) conform to the header signature exactly and fulfill this intent: the SDL implementation delegates to the f_SDL_Render_Sprite function pointer stored in the graphics sub-context wrapper, which has the identical parameter signature; the template and no_gui implementations are no-ops (appropriate for headless/test environments). The NDS implementation diverges in parameter types (PLATFORM_Graphics_Window *, Sprite_Wrapper *) but operates on a separate internal sprite path; this does not affect the correctness of the header-level declaration under review.

Implementation Correctness:
- Type compatibility: The SDL function-pointer typedef f_SDL_Render_Sprite (sdl_defines.h:165) has parameter types matching the header exactly — Gfx_Context *, Graphics_Window *, Sprite *, Vector__3i32F4 — so the delegation involves no implicit conversions or truncation. Vector__3i32F4 is a 12-byte struct (3 x i32F4) passed by value, which is acceptable.
- Undefined behavior: No pointer arithmetic, no type punning, no out-of-bounds array access occur in the canonical implementations. The SDL path chains pointer dereferences (p_gfx_context->p_PLATFORM_gfx_context->SDL_gfx_sub_context__wrapper.f_SDL_render_sprite) which could null-deref, but null-checking of these low-level context pointers is the caller's responsibility — consistent with the engine's convention. No broken pointer arithmetic.
- Validation: No validation is performed in release builds; a debug-only (NDEBUG-guarded) check verifies that the SDL render function pointer is non-null before invocation. This is appropriate for a low-level platform abstraction; the caller (sprite_manager.c:318, render_sprites) is responsible for providing valid inputs.
- No off-by-one or bounds issues: The function is a pure delegation; neither the SDL, template, nor no_gui implementation performs array indexing.

Side Effects:
- Renders the sprite to the target graphics window's framebuffer/OAM, modifying GPU state or video memory as a draw effect (the primary observable side effect).
- In the NDS backend, the side effect is writing to OAM (Object Attribute Memory) via oamSetXY, which is a hardware mutation.
- Does NOT mutate p_gfx_context, p_gfx_window, p_sprite, or position_of__sprite__3i32F4 in any reviewed implementation.
- Does NOT allocate memory or acquire any resources (no resource acquisition / not RAII).
