# PLATFORM_release_all__sprites

**File of origin:** `core/include/platform.h`

## Semantic
Releases all platform-level sprite resources associated with the given `PLATFORM_Gfx_Context`. This is a batch cleanup operation, intended to free all sprites managed by the platform layer at once (e.g., clearing an OAM table on NDS, or flushing a sprite buffer in OpenGL).

## Pre-conditions
1. `p_PLATFORM_gfx_context` must be non-null.
2. `p_PLATFORM_gfx_context` must be a valid, initialized platform graphics context.
3. The platform backend must have previously allocated sprites via `PLATFORM_allocate_sprite` on this context (or equivalent platform-specific allocation).

## Post-conditions
1. All platform-level sprite resources associated with `p_PLATFORM_gfx_context` are released/freed.
2. The `PLATFORM_Gfx_Context` is left in a state where it can re-allocate sprites (i.e., the sprite management structures are reset to their initial/empty state).
3. No `PLATFORM_Sprite` resources remain allocated under this context.

## Correctness Verdict
**Cannot be determined.** No implementation found in the core codebase. This function is declared in `core/include/platform.h` (line 109) but has no implementation in `./core`. It is a platform-specific function that must be implemented by the backend (e.g., NDS, SDL/OpenGL). The review file notes "no implementation found."

## Semantic Alignment
The declaration aligns with the Lavender pattern of batch operations on `PLATFORM_Gfx_Context`. The function name `PLATFORM_release_all__sprites` clearly indicates a bulk release of all sprites, which is distinct from the singular `PLATFORM_release_sprite` that releases a single sprite. The parameter `PLATFORM_Gfx_Context *p_PLATFORM_gfx_context` is appropriate for a batch operation that operates on the platform context rather than individual sprites. No implementation is available to verify the semantic alignment of the actual logic.

## Implementation Correctness
No implementation exists in the core codebase to evaluate. This is a platform abstraction function — the implementation is expected to reside in the platform backend (e.g., `platform_defines.h` and associated `.c` files for the target platform). The declaration itself is syntactically correct and type-safe.

## Side Effects
- Releases/frees all platform sprite resources managed by the given `PLATFORM_Gfx_Context`.
- Resets the platform's internal sprite management state (e.g., OAM pointers, sprite counts, buffer indices) to their initial/empty values.
- Does not directly modify the core `Sprite_Manager` or `Sprite_Context` structures; those remain the responsibility of core code (e.g., `clear_p_sprites_in__sprite_manager`).
