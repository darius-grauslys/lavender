allocate_world_for__game — core/source/game.c

Allocates a single `World` via `malloc(sizeof(World))` and stores it in `p_game->pM_world`; if a world is already allocated, it logs an error and returns without modifying state.

Pre-conditions:
1. `p_game` must be a non-null pointer to a writable `Game` object. The function dereferences it unconditionally — `get_p_world_from__game(p_game)` reads `p_game->pM_world`, and `p_game->pM_world = ...` writes it — with no null check of its own. This is consistent with the codebase's low-level convention (see the `initialize_audio_effect` review) that ensuring a valid pointer is the caller's responsibility.
2. `p_game->pM_world` is either null (world not yet allocated — the expected pre-condition) or non-null (world already allocated — the function detects this, logs, and no-ops).

Post-conditions:
1. If `p_game->pM_world` was already non-null on entry: `debug_error` is called and the function returns early; `p_game->pM_world` is left unchanged (still points to the previously allocated `World`).
2. Otherwise: `p_game->pM_world` is set to the result of `malloc(sizeof(World))`. The allocated memory is uninitialized (`malloc`, not `calloc`) and holds indeterminate bytes.
3. The function does NOT guarantee `p_game->pM_world` is non-null after return: if `malloc` fails it returns NULL and `p_game->pM_world` is set to NULL (see Implementation Correctness / Validation).
4. No world initialization is performed by this function. Per Lavender's "Initialization != RAII" principle, allocation is decoupled from initialization; the caller is expected to subsequently call `initialize_world(p_game, get_p_world_from__game(p_game))` (as the code generator in `mod_scene.py` does) to populate the world's fields before use.

Correctness Verdict: Correct

Semantic Alignment:
The implementation faithfully fulfills the documented intent — "allocates the world (no-op if already allocated)" (core/modules/engine.md). The double-allocation guard works: `get_p_world_from__game` is truthy when `pM_world` is non-null, which triggers the error log and early return with no mutation. When unallocated, the single `malloc(sizeof(World))` assignment performs exactly the allocation the name promises. The function deliberately performs no world initialization, and `initialize_world` (core/source/world/world.c) is a separate, caller-driven step (the codegen in mod_scene.py always emits the two calls in sequence), so the absence of field assignment here is by design, not an omission. The semantic intent is fully aligned with the implementation.

Implementation Correctness:
- Type compatibility — `Game::pM_world` is declared `World *` (core/include/defines.h:2551); `malloc` returns `void *`, which implicitly and safely converts to `World *`. `sizeof(World)` is the correct operand for the pointed-to type. No truncation, no signed/unsigned mismatch, no conversion surprises.
- Undefined behavior — Under the implicit contract that `p_game` is non-null (the caller's responsibility per codebase convention), there is no null dereference, no broken pointer arithmetic, no type punning, and no out-of-bounds access. The `debug_error` call (core/source/debug/debug.c:64) prints the message and triggers `PLATFORM_coredump()` but explicitly "keeps going" (it does not abort); the subsequent `return;` is well-defined. The only deferred hazard is a `malloc` failure yielding a NULL `pM_world`, which is not UB within this function itself but causes a NULL dereference later when `initialize_world`/`manage_world` dereference `get_p_world_from__game(p_game)`.
- Validation — The function validates the "already allocated" state and rejects it, but does NOT check `malloc`'s return value. This is a defensive gap: because the function returns `void`, the caller has no way to detect allocation failure. The sibling `begin_multiplayer_for__game` (core/source/game.c:258) does check its `malloc` and `debug_abort`s on failure, setting a precedent; the `allocate_*` family (`allocate_client_pool_for__game` and this function) consistently omit this check. For a function whose explicit role is memory allocation, verifying success is arguably its own responsibility rather than the caller's — a `debug_abort` (or a boolean return mirroring `allocate_client_pool_for__game`) would make the failure observable and prevent the later NULL dereference.

Side Effects:
Mutates `p_game->pM_world`: either leaves it unchanged (already-allocated path — early return after logging), or overwrites it with a freshly `malloc`'d, uninitialized `World`. In the already-allocated path it also emits an error message to the debug log via `debug_error`. No other state is modified.
