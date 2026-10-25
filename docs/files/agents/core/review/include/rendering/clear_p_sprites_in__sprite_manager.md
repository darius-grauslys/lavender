clear_p_sprites_in__sprite_manager — core/source/rendering/sprite_manager.c

Clears (releases) all allocated sprites in a sprite manager, releasing their platform resources and resetting the render records to an empty state.

Pre-conditions:
1. p_sprite_manager must be a non-null pointer to a valid Sprite_Manager object.
2. p_gfx_context is used to release platform sprites; it may be passed as non-null only if sprites with p_PLATFORM_sprite are present. If p_sprite_manager->pM_pool_of__sprites is NULL (e.g., after initialize_sprite_manager but before allocate_sprite_manager__members), the function returns early with no effect.
3. p_sprite_manager->pM_pool_of__sprites must point to a contiguous array of max_quantity_of__sprites Sprite structs if it is non-null.
4. p_sprite_manager->pM_sprite_render_records must point to a contiguous array of max_quantity_of__sprites Sprite_Render_Record structs if it is non-null.

Post-conditions:
1. Every sprite in the pool that was in an allocated state has its p_PLATFORM_sprite released via PLATFORM_release_sprite (if non-null) and its serialization header reinitialized for deallocated state.
2. p_sprite_render_record__last is reset to point to p_sprite_manager->pM_sprite_render_records (the beginning of the render record array).
3. All Sprite_Render_Record entries are zeroed via memset, so all p_sprite pointers within render records are NULL.
4. Deallocated sprites (already in deallocated state) are skipped and left untouched.

Correctness Verdict: Correct

Semantic Alignment:
The function fulfills its semantic intent: it clears all sprites from the sprite manager. It iterates every slot in the sprite pool, and for each sprite that is allocated (not deallocated), it releases the platform sprite resource and marks the sprite as deallocated via the serialization header — mirroring the per-sprite cleanup logic in release_sprite_from__sprite_manager. After clearing all sprites, it resets the render record array: setting p_sprite_render_record__last back to the base pointer and zeroing all render records. This returns the sprite manager's sprite-related state to a "clean pool" condition consistent with the Lavender initialization pattern (cleaning up a struct to its initial conditions for reuse).

Implementation Correctness:
- Type compatibility — the loop index Quantity__u32 matches max_quantity_of__sprites (also Quantity__u32, both uint32_t). The pointer arithmetic &pM_pool_of__sprites[index_of__sprite] is valid for array indexing. The memset size argument sizeof(Sprite_Render_Record) * max_quantity_of__sprites is computed in size_t (from sizeof) multiplied by uint32_t, which is safe.
- Undefined behavior — no null dereference: p_sprite_manager is validated in debug builds and returns early if NULL. The pM_pool_of__sprites NULL guard prevents iterating into a null array. The p_sprite->p_PLATFORM_sprite check prevents calling PLATFORM_release_sprite with NULL. No broken pointer arithmetic — the loop is bounded by max_quantity_of__sprites and indexes into the pool array.
- Validation — debug-mode null check for p_sprite_manager follows the project convention (matches release_sprite_from__sprite_manager). The early return for NULL pM_pool_of__sprites is an appropriate runtime guard, since the function may be called on a manager that was initialized (memset to zero) but not yet had its members allocated.

Side Effects:
- Releases platform sprite resources for each allocated sprite via PLATFORM_release_sprite (observable: platform-level sprite handles are freed).
- Mutates p_sprite_manager->pM_pool_of__sprites: each allocated Sprite's Serialization_Header uuid is reset to IDENTIFIER__UNKNOWN__u32 (marking the sprite as deallocated). The sprite's other fields are left as-is (matching release_sprite_from__sprite_manager behavior).
- Mutates p_sprite_manager->p_sprite_render_record__last to point back to p_sprite_manager->pM_sprite_render_records.
- Mutates p_sprite_manager->pM_sprite_render_records: all entries are zeroed via memset.
