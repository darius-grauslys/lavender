allocate_sprite_from__sprite_manager — core/source/rendering/sprite_manager.c

Allocates a Sprite from the sprite manager's pool, initializes its texture and platform sprite, and registers it in the render records array.

Pre-conditions:
1. p_gfx_context must be a non-null pointer to a valid Gfx_Context.
2. p_sprite_manager must be a non-null pointer to a valid, initialized Sprite_Manager with an allocated pool (pM_pool_of__sprites) and render records (pM_sprite_render_records).
3. p_gfx_window must be a non-null pointer to a valid Graphics_Window with a valid p_PLATFORM_gfx_window.
4. uuid__u32 must be a valid Identifier__u32 (not IDENTIFIER__UNKNOWN__u32).
5. texture_to__sample_by__sprite is a Texture value (passed by value); it provides the sampling texture reference.
6. texture_flags_for__sprite is a Texture_Flags value specifying platform texture properties.
7. The sprite pool must have at least one available (deallocated) slot; otherwise allocation fails.
8. p_sprite_manager->p_sprite_render_record__last must not have exceeded the bounds of pM_sprite_render_records (i.e., the number of allocated render records must not exceed max_quantity_of__sprites).

Post-conditions:
1. On success (non-null return):
   - A Sprite is allocated from the pool, with its serialization header set to mark it as allocated with the given uuid__u32.
   - p_sprite->texture_for__sprite_to__sample is set to texture_to__sample_by__sprite.
   - p_sprite->texture_of__sprite is allocated via PLATFORM_allocate_texture.
   - p_sprite->p_PLATFORM_sprite is allocated via PLATFORM_allocate_sprite.
   - The sprite is registered in the next available slot of pM_sprite_render_records (p_sprite_render_record__last is incremented).
   - The sprite is marked as enabled (SPRITE_FLAG__BIT_IS_ENABLED is set).
   - A pointer to the allocated Sprite is returned.
2. On failure (null return):
   - If pool allocation fails: no sprite is allocated; a debug error is logged.
   - If PLATFORM_allocate_texture fails: the sprite is deallocated from the pool (DEALLOCATE_P), but p_sprite->p_PLATFORM_sprite is NOT released because it was never allocated — this is a bug (see Implementation Correctness).
   - If PLATFORM_allocate_sprite fails: the texture is released via PLATFORM_release_texture, and the sprite is deallocated from the pool (DEALLOCATE_P).

Correctness Verdict: Incorrect

Semantic Alignment:
The function's semantic intent is to allocate a Sprite from the manager's pool, set up its texture and platform sprite, register it for rendering, and enable it. The implementation mostly fulfills this intent, but there are two significant issues:

1. **Error path bug in PLATFORM_allocate_texture failure**: When PLATFORM_allocate_texture fails, the code calls PLATFORM_release_sprite on p_sprite->p_PLATFORM_sprite. However, at this point in the function, p_sprite->p_PLATFORM_sprite has NOT yet been allocated — it is either uninitialized memory (from a previously deallocated pool slot that wasn't fully zeroed) or contains a stale pointer from a prior allocation. Calling PLATFORM_release_sprite on an invalid or stale pointer is undefined behavior. The correct behavior would be to NOT call PLATFORM_release_sprite in this error path, since no platform sprite was allocated yet.

2. **No bounds check on p_sprite_render_record__last**: The function unconditionally writes to p_sprite_manager->p_sprite_render_record__last and then increments it, without checking whether this would exceed the allocated bounds of pM_sprite_render_records. If the caller allocates more sprites than max_quantity_of__sprites, this results in an out-of-bounds write. The function should check that p_sprite_render_record__last < pM_sprite_render_records + max_quantity_of__sprites before writing.

Implementation Correctness:
- Type compatibility: All parameter types match their target fields exactly. Texture is passed by value and assigned to p_sprite->texture_for__sprite_to__sample (type Texture). No implicit conversions or truncation.
- Undefined behavior: 
  - The PLATFORM_allocate_texture failure path calls PLATFORM_release_sprite on p_sprite->p_PLATFORM_sprite, which is uninitialized/stale at that point. This is undefined behavior — releasing a pointer that was never allocated or that points to already-freed memory.
  - No bounds check on p_sprite_render_record__last before writing and incrementing, which can cause an out-of-bounds write if the render record pool is exhausted.
- Validation: The debug-mode null checks for p_sprite_manager and uuid__u32 are appropriate. However, there is no validation that p_gfx_context or p_gfx_window are non-null, which could lead to null dereference in release builds. Additionally, there is no check that the sprite pool has available slots before attempting allocation (though get_next_available__allocation_in__contiguous_array handles this by returning null).
- The ALLOCATE_P macro is correctly used to mark the sprite as allocated with the given UUID.
- The error handling for PLATFORM_allocate_sprite failure is correct: it releases the already-allocated texture and deallocates the sprite.

Side Effects:
1. Mutates p_sprite_manager->p_sprite_render_record__last (writes a Sprite_Render_Record and increments the pointer).
2. Mutates the allocated Sprite in the pool: sets its serialization header (via ALLOCATE_P), texture_for__sprite_to__sample, texture_of__sprite, p_PLATFORM_sprite, and sprite_flags__u8 (enables it).
3. Allocates platform resources: a platform texture (via PLATFORM_allocate_texture) and a platform sprite (via PLATFORM_allocate_sprite).
4. On failure paths: may deallocate the sprite (DEALLOCATE_P) and/or release platform resources (PLATFORM_release_sprite, PLATFORM_release_texture).
