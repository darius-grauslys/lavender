m_entity_deserialization_handler__default — core/source/entity/entity.c

Default deserialization handler that reads an entity's optional hitbox and inventory components from a serialization stream, allocating each by the entity's UUID, and marks the entity as enabled on success. It is installed by `f_entity_initializer__default` (entity_manager.c:37) and invoked by `deserialize_entity` (entity.c:200) after the entity's serialization header and `Entity_Data` (including `entity_flags`) have already been read from the file.

Pre-conditions:
1. `p_this_entity` must be a non-null pointer to a valid, allocated `Entity` whose `Serialization_Header` has already been read so that `GET_UUID_P(p_this_entity)` yields a valid UUID.
2. `p_game` must be a non-null pointer to a valid `Game` with an initialized hitbox context, inventory manager, and platform file system context.
3. `p_PLATFORM_file_system_context` is unused by this handler; the actual file system context is derived from `p_game` via `get_p_PLATFORM_file_system_context_from__game(p_game)`, matching the serialization handler's behavior.
4. `p_world` must be a non-null pointer to a valid `World` with a valid UUID, used to locate the world's `Hitbox_AABB_Manager`.
5. `p_serialization_request` must be a non-null pointer to a valid `Serialization_Request` whose `p_file_handler` is open and positioned at the start of this entity's hitbox/inventory payload.
6. `p_this_entity->entity_data.entity_flags` must already contain the correct `ENTITY_FLAG__IS_WITH_HITBOX__SERIALIZATION` and/or `ENTITY_FLAG__IS_WITH_INVENTORY__SERIALIZATION` bits, as these are set during serialization and restored by `deserialize_entity` before calling this handler.

Post-conditions:
On success (returns `PLATFORM_Read_File_Error__None`):
1. If `ENTITY_FLAG__IS_WITH_HITBOX__SERIALIZATION` was set, a `Hitbox_AABB` has been allocated from the world's hitbox AABB manager (keyed by the entity's UUID) and `sizeof(Hitbox_AABB)` bytes of binary data have been read from the file into that allocation.
2. If `ENTITY_FLAG__IS_WITH_INVENTORY__SERIALIZATION` was set, an `Inventory` has been allocated from the game's inventory manager (keyed by the entity's UUID) and fully deserialized from the file via `deserialize_inventory`.
3. The `ENTITY_FLAG__IS_ENABLED` bit is set on `p_this_entity->entity_data.entity_flags` (via `set_entity_as__enabled`).

On failure (returns a non-`None` `PLATFORM_Read_File_Error`):
1. The entity is left in a partially deserialized state; components allocated before the failure remain allocated but may be incomplete.
2. The `ENTITY_FLAG__IS_ENABLED` bit is NOT set, because the function returns before reaching `set_entity_as__enabled`.

Correctness Verdict: Correct

Semantic Alignment:
The implementation faithfully fulfills the semantic intent. Each component flag gates the allocation-and-read of the corresponding component, exactly mirroring `m_entity_serialization_handler__default`, which sets those same flags when the components exist and writes `sizeof(Hitbox_AABB)` bytes directly for the hitbox and delegates inventory writing to `serialize_inventory`. The read size for the hitbox (`sizeof(Hitbox_AABB)`) matches the write size, and the inventory deserialization is delegated to the matching `deserialize_inventory` callee, preserving the serialization/deserialization symmetry. The final `set_entity_as__enabled` call appropriately activates the entity only after all requested components have been loaded.

Implementation Correctness:
Type compatibility — `quantity_of__bytes_read` is `Quantity__u32` (uint32_t) and is passed as `Quantity__u32 *` to `PLATFORM_read_file`'s `p_length_of__data_to_read` parameter, which matches exactly. The `Hitbox_AABB *` is cast to `u8 *` for `PLATFORM_read_file`'s `destination` parameter, matching the `u8 *` type. All return statements use `PLATFORM_Read_File_Error` values, matching the function's declared return type. `GET_UUID_P(p_this_entity)` casts `Entity *` to `Serialization_Header *`; since `Serialization_Header` is the first member of `Entity`, this is well-defined.

Undefined behavior — No broken pointer arithmetic. The `GET_UUID_P` macro relies on the first-member layout of `Entity` (struct type-punning via first-member pointer), which is the codebase's established and safe pattern. No null dereferences within this function's own logic — the handler assumes valid input pointers from the caller (`deserialize_entity`), consistent with the serialization handler's own lack of null-checking. No out-of-bounds access. `sizeof(Hitbox_AABB)` (a `size_t`) is implicitly narrowed to `Quantity__u32` when assigned to `quantity_of__bytes_read`; this is safe in practice because `Hitbox_AABB` is a small struct, but is a technically implicit conversion worth noting.

Validation — The handler performs no null checks on its own parameters, relying on `deserialize_entity` to ensure valid input. This is consistent with the codebase's pattern and the serialization handler's behavior. Allocation failures from `allocate_hitbox_aabb_from__hitbox_aabb_manager` and `allocate_p_inventory_using__this_uuid_in__inventory_manager` are checked and cause an early return of `PLATFORM_Read_File_Error__Unknown`. IO errors from `PLATFORM_read_file` and `deserialize_inventory` are checked and propagated to the caller.

Side Effects:
1. Mutates `p_this_entity` on the success path: sets the `ENTITY_FLAG__IS_ENABLED` bit in `p_this_entity->entity_data.entity_flags` via `set_entity_as__enabled`.
2. Mutates the world's hitbox manager: allocates a `Hitbox_AABB` entry (via `allocate_hitbox_aabb_from__hitbox_aabb_manager`) and populates it with data read from the file, when the hitbox flag is set.
3. Mutates the game's inventory manager: allocates an `Inventory` entry (via `allocate_p_inventory_using__this_uuid_in__inventory_manager`) and populates it via `deserialize_inventory`, when the inventory flag is set.
4. Performs file I/O: reads from `p_serialization_request->p_file_handler` via `PLATFORM_read_file` (hitbox) and `deserialize_inventory` (inventory), advancing the file position.
5. Emits debug log messages via `debug_error` on allocation or IO failure paths.
