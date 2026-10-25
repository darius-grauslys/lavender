PLATFORM_allocate_sprite — core/include/platform.h, line 99

Allocates a backend sprite resource bound to a core Sprite, returning a pointer to the allocated PLATFORM_Sprite (or NULL on failure).

Pre-conditions:
1. p_gfx_context must be a non-null pointer to an initialized Gfx_Context.
2. p_gfx_window must be a valid (non-null) Graphics_Window pointer; it is passed through to the platform sprite allocator.
3. p_sprite must be a non-null, writable pointer to a Sprite struct; the function writes p_sprite->p_PLATFORM_sprite.
4. texture_flags_for__sprite is a Texture_Flags (uint32_t) value with no range constraint.

Post-conditions:
1. On success: returns a non-null PLATFORM_Sprite * bound to the core Sprite.
2. On success: p_sprite->p_PLATFORM_sprite is set to the allocated PLATFORM_Sprite.
3. On failure: returns NULL (0); p_sprite->p_PLATFORM_sprite may be partially set or NULL depending on which allocation step failed.

Correctness Verdict: Incorrect

Semantic Alignment:
The header contract is semantically sound: allocate a backend sprite, bind it to the core Sprite, and return a pointer (NULL on failure). The SDL implementation (sdl/source/rendering/sdl_sprite_manager.c:77), the no_gui stub (no_gui/source/NOT_IMPL.c:78), and the test stub (tests/core/source/PLATFORM.c:206) all conform precisely to the declared 4-parameter signature and fulfill this intent.

However, the NDS implementation (nds/source/rendering/sprite_manager.c:88) defines PLATFORM_allocate_sprite with a completely incompatible 2-parameter signature:
   PLATFORM_Sprite *PLATFORM_allocate_sprite(
       PLATFORM_Gfx_Context *p_PLATFORM_gfx_context,
       Sprite_Allocation_Specification *p_sprite_allocation_specification)
This does NOT match the contract declared in core/include/platform.h (which the NDS source file includes at line 5). The NDS build (nds/Makefile:67) compiles BOTH the NDS sources and the shared core sources (CFILES := $(CFILES_NDS) $(CFILES_CORE)). The shared core file core/source/rendering/sprite_manager.c (line 119) calls PLATFORM_allocate_sprite with four arguments matching the header. The function contract therefore cannot be upheld: the declared intent is fulfilled by three implementations but violated by the NDS one.

Implementation Correctness:
Type compatibility — the header declaration is internally type-consistent (Texture_Flags is uint32_t, Gfx_Context/Graphics_Window/Sprite are forward-declared structs, return is PLATFORM_Sprite *). No implicit conversions in the declaration itself.
Undefined behavior — the NDS definition conflicts with the declaration seen via platform.h (a C constraint violation / conflicting-types). The core call site passes four arguments to a function expecting two, so the callee reads p_PLATFORM_gfx_context and p_sprite_allocation_specification from register/stack slots that actually hold p_gfx_context and p_gfx_window, yielding null or garbage pointers and dereferencing them.
Validation — the header exposes no validation; per the guide this is appropriate for a low-level platform entry point — validation is the caller's responsibility. The core caller (core/source/rendering/sprite_manager.c:119) does null-check the returned pointer. The broken NDS path is the defect.
Additional note — the static inline caller NDS_allocate_sprite__8x8_on__oam_main (nds/include/rendering/nds_sprite_manager.h:82) is missing a return statement despite declaring a PLATFORM_Sprite * return type, but that is a caller-site defect, not part of this function's body.

Side Effects:
- Mutates p_sprite: writes p_sprite->p_PLATFORM_sprite to point at the newly allocated PLATFORM_Sprite.
- Allocates/consumes a backend sprite pool slot from the graphics context's sprite manager (e.g., SDL sprite manager, or NDS OAM sprite array).
- On the graphics-pointer allocation path: allocates a PLATFORM_Texture via PLATFORM_allocate_texture and copies source gfx data into it.
- On the SDL path: invokes the gfx sub-context allocator (f_SDL_allocate_sprite) which uploads sprite/pixel data, and calls SDL_initialize_sprite (Lavender-style clear-to-default of the sprite's rendering state).
- On failure of an inner allocation, releases the partially allocated sprites back to the manager pool.
- The no_gui and test stubs have no side effects (return NULL immediately).
