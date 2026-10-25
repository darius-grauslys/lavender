PLATFORM_release_sprite — core/include/platform.h, line 105

Implementations reviewed:
- SDL: sdl/source/rendering/sdl_sprite_manager.c:122
- NDS: nds/source/rendering/sprite_manager.c:216
- no_gui: stub, no_gui/source/NOT_IMPL.c:84
- tests: tests/core/source/PLATFORM.c:212

## Semantic
Frees the platform-specific backend sprite resource and returns the sprite to its free pool. Per Lavender semantics, "release" is pool cleanup (mark deallocated / remove from active pool), NOT RAII resource teardown alone.

## Pre-conditions
1. `p_gfx_context` is non-null and points to a valid, fully-initialized `Gfx_Context`.
2. `p_PLATFORM_sprite` is non-null and points to a valid `PLATFORM_Sprite` that is currently allocated (i.e. not already released; a double release is undefined / a logic error by the caller).

## Post-conditions
1. The platform-specific backend sprite resource is disposed (SDL: `f_SDL_release_sprite` frees the SDL sprite; NDS: the bound texture is released via `PLATFORM_release_texture`).
2. The sprite is marked deallocated and removed from the active sprite pool (SDL: `SDL_release_sprite_from__sprite_manager`; NDS: `set_sprite_flags_as__deallocated`).
3. `p_gfx_context` state no longer considers `p_PLATFORM_sprite` active.

## Correctness Verdict
Incorrect

## Semantic Alignment
The declared intent ("free the backend sprite and return it to the free pool") is sound, and the *behavior* of the SDL and NDS implementations matches that intent (free backend resource + mark deallocated/remove from pool). Semantic intent is therefore correct in spirit. See Implementation Correctness, however, where the NDS definition breaks the declared contract.

## Implementation Correctness
The header (core/include/platform.h:105) declares the first parameter as the core wrapper type:

    void PLATFORM_release_sprite(Gfx_Context *p_gfx_context, PLATFORM_Sprite *p_PLATFORM_sprite);

Signature conformance across implementations:
- SDL (sdl_sprite_manager.c:122): CONFORMS — takes `Gfx_Context *p_gfx_context` and dereferences `p_gfx_context->p_PLATFORM_gfx_context->...`.
- no_gui / tests: CONFORM — both take `Gfx_Context *`.
- NDS (nds/source/rendering/sprite_manager.c:216): DOES NOT CONFORM — defines the first parameter as `PLATFORM_Gfx_Context *p_PLATFORM_gfx_context`.

`Gfx_Context` (core/include/defines.h:2524) and `PLATFORM_Gfx_Context` (e.g. nds/include/nds_defines.h:229; sdl/include/sdl_defines.h:270) are distinct struct types. `Gfx_Context` merely holds a `PLATFORM_Gfx_Context *p_PLATFORM_gfx_context` member; it is not layout-compatible with any `PLATFORM_Gfx_Context_t` definition.

This is an incompatible-declaration / type-compatibility defect:
- It is a constraint violation under C11 6.7.6.3p15 (compatible declarations required); a conforming compiler must emit a diagnostic when both the header declaration and the NDS definition are visible in one translation unit.
- At link/runtime, the core shared caller core/source/rendering/sprite_manager.c:111 invokes `PLATFORM_release_sprite(p_gfx_context, ...)` with a `Gfx_Context *`, per the header. On an NDS build the definition reinterprets that `Gfx_Context *` as a `PLATFORM_Gfx_Context *`, reading unrelated fields (e.g. `NDS_texture_manager`, `nds_sprite_manager`) from the wrong memory layout — undefined behavior (null/garbage dereference, wrong texture release, corrupted flags).
- Even excluding the cross-TU call, the NDS translation unit itself sees two incompatible declarations of the same function, which is a hard constraint violation.

No other validation or off-by-one issues were found in the conforming (SDL) path. The NDS body itself (release bound texture + set flags as deallocated) is otherwise behaviorally correct given a properly-typed context pointer.

## Side Effects
- Frees/disposes the platform backend sprite resource (SDL sprite disposal; NDS bound texture release via `PLATFORM_release_texture`).
- Mutates platform gfx-context state: sprite manager pool and sprite allocation flags are updated to reflect deallocation.
- No return value.
- Out-of-scope: side effects of any further function calls reached from within platform sprite/texture managers are not traced here.
