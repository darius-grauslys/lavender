m_entity_serialization_handler__default — core/source/entity/entity.c

Serializes an Entity to the active file handler by writing its Serialization_Header, Entity_Data (with presence flags set for hitbox/inventory), and conditionally the Hitbox_AABB and Inventory if the entity owns them.

Pre-conditions:
1. p_entity_self must be a non-null pointer to a valid Entity. It is dereferenced directly via GET_UUID_P to read its UUID, and its entity_data.entity_flags are read/written without a null guard.
2. p_game must be a non-null pointer to a valid Game. It is used to derive the hitbox context, inventory manager, and file system context.
3. p_world must be a non-null pointer to a valid World. GET_UUID_P(p_world) is called to select the per-world hitbox AABB manager.
4. p_serialization_request must be a non-null pointer to an active Serialization_Request whose p_file_handler is a valid open file handle. p_file_handler is dereferenced by PLATFORM_write_file with no null check.
5. p_PLATFORM_file_system_context is passed in but never referenced by this function (see Implementation Correctness). No constraint is imposed on it by the function body.
6. The entity's hitbox and inventory lookups return either a valid pointer or null; both outcomes are handled. p_hitbox_aabb_manager is NOT null-checked before being passed to get_p_hitbox_aabb_by__uuid_u32_from__hitbox_aabb_manager (unlike the dispose/enable/disable handlers which guard this in debug builds). If that getter dereferences a null context, it would be undefined behavior; correctness relies on the game always providing a valid hitbox context.

Post-conditions:
1. If the entity has an associated Hitbox_AABB, ENTITY_FLAG__IS_WITH_HITBOX__SERIALIZATION is set in p_entity_self->entity_data.entity_flags. If no hitbox exists, the flag is left in whatever state it previously held (the function ORs the bit in but never clears it).
2. If the entity has an associated Inventory, ENTITY_FLAG__IS_WITH_INVENTORY__SERIALIZATION is set in p_entity_self->entity_data.entity_flags. As above, the flag is only set, never cleared.
3. The file stream (p_serialization_request->p_file_handler) receives, in order: sizeof(Serialization_Header) bytes (the _serialization_header member), then sizeof(Entity_Data) bytes (the entity_data member, including the freshly-set flags), then sizeof(Hitbox_AABB) bytes if a hitbox exists, then the serialized inventory bytes if an inventory exists.
4. The Entity_Functions member is intentionally not written (it holds function pointers that are reconstructed on deserialization via sanitize_entity_functions based on entity kind).
5. Returns PLATFORM_Write_File_Error__None on success, otherwise returns the first PLATFORM_Write_File_Error encountered and stops writing further components. On a mid-stream failure, the file is left partially written and the in-memory flags may already have been mutated.

Correctness Verdict: Correct

Semantic Alignment:
The implementation fulfills the serialization intent: it writes the header, the entity data (with presence flags), the hitbox (when present), and the inventory (when present), mirroring what the deserialization handler (m_entity_deserialization_handler__default) expects to read back using those same flags. The Entity_Functions member is correctly omitted from the byte stream since function pointers must not be persisted.

Two nuances are worth flagging:
- Flag clearing: the presence flags are set via |= but never cleared. For a clean entity (e.g., one just memset to zero by initialize_entity) this is harmless, but re-serializing an entity whose hitbox/inventory was removed after a prior serialization would leave a stale flag claiming the data is present, causing the deserializer to attempt reading non-existent bytes. This latent mismatch depends on the caller ensuring a clean flag state before each serialization.
- The Entity_Data written reflects whatever flags were in memory plus the OR'd-in bits, so the streamed data is self-consistent with what was actually written to the file.

Implementation Correctness:
Type compatibility — all casts and sizeof operands are consistent: (u8*)p_entity_self matches the u8 buffer parameter of PLATFORM_write_file; sizeof(Serialization_Header) and sizeof(Entity_Data) are the correct struct sizes; ENTITY_FLAG__IS_WITH_HITBOX__SERIALIZATION and ENTITY_FLAG__IS_WITH_INVENTORY__SERIALIZATION are u32 bit flags matching Entity_Flags__u32, so the |= on entity_flags is type-safe with no truncation.
No out-of-bounds or type-punning — writing sizeof(Serialization_Header) bytes from the base of the Entity struct safely captures exactly the first _serialization_header member (it is the first declared field), and writing from &p_entity_self->entity_data captures exactly Entity_Data.
Undefined behavior risk — p_entity_self, p_game, p_world, and p_serialization_request->p_file_handler are all dereferenced with no null checks. This is acceptable as a low-level handler where null-safety is the caller's (serialize_entity) responsibility, but it differs from the dispose/enable/disable handlers which debug-assert the hitbox manager. The missing null check on p_hitbox_aabb_manager is the most notable deviation.
Dead parameter — p_PLATFORM_file_system_context is accepted but unused; every PLATFORM_write_file call re-derives the context from p_game via get_p_PLATFORM_file_system_context_from__game(p_game). This is not a correctness bug (the values agree) but is a redundancy in the API signature.
Validation — no argument validation is performed, which is appropriate for this internal serialization handler; the caller (serialize_entity) gates invocation on a non-null m_entity_serialize_handler and is expected to have activated the serialization request.

Side Effects:
Mutates p_entity_self->entity_data.entity_flags (sets the hitbox/inventory serialization presence bits when those components exist). Performs IO writes to the file handle owned by p_serialization_request (header, entity data, hitbox, and inventory bytes), which is the primary observable effect of the function. The Hitbox_AABB and Inventory objects themselves are read-only from this function's perspective (not mutated).
