# Review: GFX_CONTEXT_allocate_graphics_window_with__sprite_pool

- **File of origin:** `core/include/rendering/gfx_context_helpers.h` (lines 85-118)

## Semantic

Allocates a graphics window through the graphics window manager and, on success, allocates a sprite pool from the sprite manager tied to the given uuid; rolls back the window allocation if the sprite pool cannot be allocated. Returns the graphics window pointer (or null on failure).

## Pre-conditions

1. `p_game` is non-null and points to a Game whose `Gfx_Context` is initialized and reachable via `get_p_gfx_context_from__game`.
2. The `Gfx_Context`'s graphics window manager (reachable via `get_p_graphics_window_manager_from__gfx_context`) is initialized and has a free graphics-window slot.
3. The `Gfx_Context`'s sprite subsystem is initialized so the sprite pool can be allocated against `uuid__u32`.
4. `texture_flags_for__gfx_window` is a valid `Texture_Flags` value describing the desired window dimensions/format.
5. `uuid__u32` is a valid `Identifier__u32` to be associated with the sprite pool.

## Post-conditions

1. On success: returns a non-null `Graphics_Window *` that is allocated, enabled, registered in the graphics window manager, marked dirty for composition, and (intended) associated with an allocated sprite pool.
2. On graphics-window allocation failure: returns null; no window was allocated.
3. On sprite-pool allocation failure: returns null; the previously allocated graphics window has been released/rolled back, so there is no net allocation.
4. On success, the returned window has a valid `p_PLATFORM_gfx_window` (`is_graphics_window__allocated` is true).

## Correctness Verdict

Incorrect

## Semantic Alignment

The function's stated intent (allocate a graphics window that owns/uses a sprite pool) is not fulfilled:

- The code calls three symbols that do not exist anywhere in the codebase and cannot be resolved:
  - `Sprite_Pool` — an undeclared type. No `typedef`/`struct Sprite_Pool` exists (the only pool types are `Serialization_Pool`, `Collision_Node_Pool`, `Chunk_Pool`). Used as `Sprite_Pool *p_sprite_pool` at lines 68/103. Compile error: "unknown type name 'Sprite_Pool'".
  - `allocate_sprite_pool_from__sprite_manager` — never declared or defined (only the two call sites at lines 69/104 exist). Compile error (implicit declaration in C99+) and linker error.
  - `get_p_sprite_manager_from__gfx_context` — not defined in `gfx_context.h`. Core only provides `get_p_sprite_context_from__gfx_context` (returns `Sprite_Context *`); a platform-level `SDL_get_p_sprite_manager_from__gfx_context` exists but has a different name and takes `PLATFORM_Gfx_Context *`. Unresolvable symbol mismatch.
- Because the sprite pool is allocated into a local `p_sprite_pool` that is never used to associate the pool with the window (e.g. via the window's `uuid_of__sprite_manager` field), the window would be returned with no registered sprite pool/manager. This diverges from the established pattern (`allocate_sprite_manager_from__sprite_context` + `does_graphics_window_own_a__sprite_manager`, which key the manager to the window's uuid).
- Copy-paste debug messages reference the wrong functions: the graphics-window failure path logs "GFX_CONTEXT_allocate_graphics_window_with__ui_manager" (line 99) and the sprite-pool failure path logs "GFX_CONTEXT_allocate_graphics_window_with__ui_manager_and__sprite_pool" (line 113) — neither matches the actual function name.

Note on Lavender semantics: the "allocate" verb here denotes resource acquisition (allocating a window + pool), which is appropriate and is NOT a Lavender-style "init" (pool cleanup/reset). The init!=RAII distinction therefore does not apply; the function is correctly framed as an allocation entry point.

## Implementation Correctness

- Type compatibility: FAILS. `Sprite_Pool` is undeclared (type-compatibility violation); `allocate_sprite_pool_from__sprite_manager` and `get_p_sprite_manager_from__gfx_context` are undeclared, so parameter/return types cannot be checked. The rollback call `release_graphics_window_from__graphics_window_manager(p_game, p_graphics_window)` does match the declared `void release_graphics_window_from__graphics_window_manager(Game *, Graphics_Window *)` — that single call is type-correct.
- Undefined behavior: The function cannot be compiled as written, so runtime UB is moot. Were the symbols resolved, no out-of-bounds or pointer-arithmetic issues exist in this function body. The rollback ordering (release window after pool failure) is logically sound.
- Validation: Appropriate for a helper — allocation failures are checked and rolled back. `p_game`/`p_gfx_context` are not null-checked (consistent with the sibling helpers in the same file, which also omit them; validation is left to callers).
- The unused result of the sprite-pool allocator means any pool successfully allocated (had the symbol existed) would be orphaned with respect to the window, since nothing records it on the `Graphics_Window`.

## Side Effects

- Allocates and registers a `Graphics_Window` in the graphics window manager (inserts into the contiguous array + sorted ptr array; sets dirty/composition flags; enables the window).
- On sprite-pool failure, releases the allocated window via `release_graphics_window_from__graphics_window_manager` (resets window, deallocates P, clears sorted slot).
- Intended (but uncompilable) side effect: allocates a sprite pool via `allocate_sprite_pool_from__sprite_manager` — does not occur because the symbol is undefined.
- Emits `debug_error` diagnostics on the failure paths.
- Does not otherwise mutate global/static state.
