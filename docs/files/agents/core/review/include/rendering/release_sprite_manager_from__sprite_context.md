# Release Sprite Manager From Sprite Context

## 1. Header

**Function name:** `release_sprite_manager_from__sprite_context`
**File of origin:** `core/source/rendering/sprite_context.c` (lines 82-103)

## 2. Semantic

Releases a single `Sprite_Manager` slot from the `Sprite_Context`'s contiguous pool: after verifying the manager belongs to this context's array, it marks the slot as deallocated so it can be returned to the free pool for reuse.

## 3. Pre-conditions

1. `p_sprite_manager` must be non-null (checked unconditionally, lines 91-94).
2. `p_sprite_context` should be non-null (checked only under `#ifndef NDEBUG`, lines 86-90; treated as caller responsibility in release per codebase convention).
3. `p_sprite_context->pM_sprite_managers` must be a valid, allocated contiguous array of `Sprite_Manager` structs (i.e. `is_sprite_managers_allocated_in__sprite_context(p_sprite_context)` should hold). **This is NOT validated by the function.**
4. `p_sprite_manager` must point to an element within the `p_sprite_context->pM_sprite_managers` array (or one-past-the-end), allocated via `allocate_sprite_manager_from__sprite_context`.

## 4. Post-conditions

1. If all checks pass, `p_sprite_manager->_serialization_header` is reset to the deallocated sentinel (`uuid = IDENTIFIER__UNKNOWN__u32`, `size_of__struct = sizeof(Sprite_Manager)`), making the slot available for reuse by `allocate_sprite_manager_from__sprite_context`.
2. If any check fails, the function returns early with a `debug_error` and the manager's state is left unchanged.
3. **The member resources allocated by `allocate_sprite_manager__members` (`pM_pool_of__sprites` and `pM_sprite_render_records`) are NOT freed** -- they are leaked (see Implementation Correctness, Issue 4).

## 5. Correctness Verdict

**Incorrect**

## 6. Semantic Alignment

The implementation partially fulfills the semantic intent. The happy-path behavior (marking a valid manager slot as deallocated) works correctly, and `initialize_serialization_header_for__deallocated_struct` correctly sets the deallocated header (Lavender-style pool cleanup, not RAII). However:

- The verification step is broken: the bounds check does not catch every invalid pointer (Issue 1), so a `p_sprite_manager` that does NOT belong to this context can pass the check and be incorrectly marked as deallocated.
- The release is incomplete: the function does not free the member resources (`pM_pool_of__sprites`, `pM_sprite_render_records`) that the allocate counterpart allocated, violating the semantic assumption that "releasing" a resource returns all of its sub-resources. The counterpart `release_sprite_from__sprite_manager` frees its platform resource before marking deallocated; this function does not follow that pattern.

## 7. Implementation Correctness

- **Issue 1 (critical -- lower-bound check gap / undefined behavior):** The bounds check is:
  ```c
  if (p_sprite_manager - p_sprite_context->pM_sprite_managers
          >= p_sprite_context->max_quantity_of__sprite_managers)
  ```
  `p_sprite_manager - p_sprite_context->pM_sprite_managers` yields a signed `ptrdiff_t`. `max_quantity_of__sprite_managers` is `Quantity__u8` (`uint8_t`), which the usual arithmetic conversions (C11 6.3.1.8) promote to signed `ptrdiff_t` (since `ptrdiff_t` has higher rank and can represent all `uint8_t` values). A pointer that lies *before* the array start produces a *negative* `ptrdiff_t`; e.g. `-1 >= 0` is false, so the check passes and `initialize_serialization_header_for__deallocated_struct` writes to memory *before* the array -- undefined behavior (out-of-bounds write). The codebase already demonstrates the correct pattern in `release_game_action_from__game_action_manager` (see `core/source/game_action/game_action_manager.c:87-94`), where the difference is first stored in a `u32`, so a negative result wraps to a large unsigned value that is correctly caught:
  ```c
  u32 index = p_game_action - p_game_action_manager->game_actions;
  if (index >= MAX_QUANTITY_OF__GAME_ACTIONS) { ... }
  ```
  (This correct pattern is in `core/source/game_action/game_action_manager.c`, lines 87-94.)
  Fix: cast the difference to an unsigned type (e.g. `u32`) before comparing, or explicitly verify `p_sprite_manager >= p_sprite_context->pM_sprite_managers` as a lower-bound guard before the upper-bound check.

- **Issue 2 (undefined behavior -- pointer subtraction of unrelated pointers):** Per C11 6.5.6p9, pointer subtraction is defined only when both pointers point into the same array object (or one past the last element). When `p_sprite_manager` does not point into `p_sprite_context->pM_sprite_managers`, the subtraction itself is undefined behavior -- the guard is built on a UB foundation. (This pattern also appears in `release_game_action_from__game_action_manager`, so it is a codebase-wide convention; in that case the unsigned storage at least catches the lower-bound case in practice.)

- **Issue 3 (undefined behavior -- missing allocation check):** Unlike `allocate_sprite_manager_from__sprite_context` (which checks `is_sprite_managers_allocated_in__sprite_context` before touching `pM_sprite_managers`), this release function never verifies that `p_sprite_context->pM_sprite_managers` is non-null before dereferencing it in the pointer subtraction. If the managers array was never allocated or already freed (`pM_sprite_managers == NULL`), then `p_sprite_manager - NULL` is undefined behavior (NULL is not a valid array element). The allocate counterpart validates this precondition; the release counterpart does not.

- **Issue 4 (memory leak -- incomplete release):** `allocate_sprite_manager_from__sprite_context` calls `allocate_sprite_manager__members`, which `malloc`s `pM_pool_of__sprites` and `pM_sprite_render_records` (sprite_manager.c:40,47). This release function marks the manager slot as deallocated but never `free`s those member pools. When the slot is subsequently re-allocated, `initialize_sprite_manager` zeroes the pointers (losing the old addresses) and `malloc` overwrites them -- the old allocations are leaked (sprite_manager.c:38-40). `release_sprite_managers_from__sprite_context` (sprite_context.c:39-47) only `free`s the `pM_sprite_managers` array itself and also does not free each manager's member pools. By contrast, `release_sprite_from__sprite_manager` (sprite_manager.c:150-198) frees its platform resource (`p_PLATFORM_sprite` via `PLATFORM_release_sprite`) before marking deallocated. This function should likewise `free` `pM_pool_of__sprites` and `pM_sprite_render_records` before marking the manager deallocated. (Assumes the sprite pool is empty of live sprites; callers are expected to release individual sprites first, as the call site in graphics_window.c:373 implies a window teardown.)

- **Issue 5 (cosmetic -- wrong debug messages):** All three `debug_error` calls (lines 87, 92, 97) report `"release_sprite_from__sprite_context, ..."` instead of `"release_sprite_manager_from__sprite_context, ..."`. This is a copy-paste error that misleads debugging.

- **Issue 6 (type narrowing -- convention, not a bug):** `sizeof(Sprite_Manager)` is `size_t` (64-bit), implicitly narrowed to `Quantity__u32` (`uint32_t`) when passed to `initialize_serialization_header_for__deallocated_struct`. For this struct (Serialization_Header + 3 pointers + 1 u32 = ~36 bytes) the value is well within `uint32` range, so no truncation occurs. This is a codebase-wide convention (also seen in hitbox_aabb.h, aliased_texture.c, game_action.c, etc.).

## 8. Side Effects

1. **Mutates:** `p_sprite_manager->_serialization_header` -- its `uuid` is set to `IDENTIFIER__UNKNOWN__u32` and `size_of__struct` to `sizeof(Sprite_Manager)`, marking the slot deallocated and available for reuse by `allocate_sprite_manager_from__sprite_context`. This is the only intended side effect.
2. **Leaked side effect (missing):** The `malloc`'d pools `pM_pool_of__sprites` and `pM_sprite_render_records` (allocated in the corresponding `allocate_sprite_manager__members` call) are never freed in this path. If the caller subsequently re-allocates the slot, the old pools are leaked (their addresses are overwritten). If the caller destroys the whole array via `release_sprite_managers_from__sprite_context`, the per-manager pools are also leaked.
3. No other observable state is modified -- no global state, no file I/O, no callbacks invoked (unlike `release_entity_from__entity_manager` which calls a dispose handler). The function does not free `p_sprite_context->pM_sprite_managers` (that is the job of `release_sprite_managers_from__sprite_context`).
