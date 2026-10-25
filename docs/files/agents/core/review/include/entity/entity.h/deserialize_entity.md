deserialize_entity — core/source/entity/entity.c

Deserializes an Entity from a file by reading its Serialization_Header and Entity_Data, sanitizing its function table against the entity manager, and delegating further kind-specific deserialization to the registered handler.

Pre-conditions:
1. p_game must be a non-null pointer to an initialized Game (used to obtain the file system context, entity manager, and world via the game's getters).
2. p_serialization_request must be a non-null, active Serialization_Request whose file-backed union member (p_file_handler) is a valid open handle for reading; the request must already be activated with a file handler (not the tcp/io union layout).
3. p_entity must be a non-null pointer to writable, properly aligned Entity storage large enough to receive a Serialization_Header and an Entity_Data; writes go directly into p_entity->_serialization_header (the first member of Entity) and p_entity->entity_data.
4. The file stream underlying p_serialization_request->p_file_handler must be positioned at the start of a serialized Entity record (Serialization_Header immediately followed by Entity_Data).

Post-conditions:
1) On return with PLATFORM_Read_File_Error__None and no deserialize handler: p_entity->_serialization_header is populated from the file (uuid copied verbatim; size_of__struct overwritten to sizeof(Entity)), p_entity->entity_data is populated verbatim (entity_flags and the_kind_of__entity), and p_entity->entity_functions has been sanitized so each non-null function pointer from the entity manager's registered table for the_kind_of__entity is copied into the matching slot.
2) The read cursor of p_serialization_request->p_file_handler has advanced by at least sizeof(Serialization_Header) + sizeof(Entity_Data); when a deserialize handler is present it may advance further.
3) On header read failure: the function returns the PLATFORM_Read_File_Error; p_entity->_serialization_header.size_of__struct has nonetheless been set to sizeof(Entity) defensively, and entity_data is left untouched.
4) On entity_data read failure: the function returns the error; _serialization_header is fully populated and entity_data may be partially written.

Correctness Verdict: Correct

Semantic Alignment:
The implementation fulfills the deserialization intent. It reads the on-disk Serialization_Header then Entity_Data into the entity in order, refreshes the function table from the entity manager via sanitize_entity_functions based on the deserialized the_kind_of__entity, and delegates any kind-specific deserialization (and additional field reads) to m_entity_deserialize_handler when it is non-null. The trailing "precaution" reasserts size_of__struct = sizeof(Entity) on the no-handler path, reflecting that the engine treats its local sizeof(Entity) as authoritative rather than the value stored in the file. The fields this function owns (_serialization_header and entity_data) are both populated; entity_functions is populated via sanitize rather than direct assignment, which is the intended mechanism.

Implementation Correctness:
Type compatibility — quantity_of__bytes_read is Quantity__u32 and is initialized from sizeof(Serialization_Header) / sizeof(Entity_Data) (size_t → uint32_t). In practice these sizes (8 bytes each) fit in uint32_t and this matches the codebase-wide pattern (e.g. the ALLOCATE_P macro and serialize_entity), so there is no truncation risk. The (u8 *)&p_entity->_serialization_header and (u8 *)&p_entity->entity_data arguments match PLATFORM_read_file's u8 *destination parameter. p_serialization_request->p_file_handler is void * and matches the void *p_file_handler parameter. get_p_PLATFORM_file_system_context_from__game returns PLATFORM_File_System_Context *, matching the first parameter. All return paths yield PLATFORM_Read_File_Error (error, PLATFORM_Read_File_Error__None, and the m_Entity_Deserialization_Handler return value, whose typedef returns PLATFORM_Read_File_Error), matching the declared return type.
Undefined behavior — None in normal operation. No pointer arithmetic beyond the struct-address-to-byte-pointer cast (well defined, the standard serialization idiom); object representation reads/writes via u8* do not constitute type punning. No out-of-bounds access on p_entity's own fields. The function dereferences p_game, p_serialization_request, and p_entity without null checks; this is intentional (caller responsibility) and consistent with sibling functions such as serialize_entity.
Validation — Validation is intentionally minimal and deferred to the caller / trusted file, matching the engine's low-level serialization convention. One assumption worth noting: sanitize_entity_functions indexes entity_manager->entity_functions[the_kind_of__entity]; the deserialize path does not bounds-check the_kind_of__entity before this indexing, so a corrupted/truncated file with an out-of-range kind could cause an out-of-bounds read. This matches the established pattern (the same call site exists in entity_manager.c without validation), so it is not a defect, but it relies on the input being well-formed.

Side Effects:
- Advances the read cursor of p_serialization_request->p_file_handler by sizeof(Serialization_Header) + sizeof(Entity_Data) (plus any bytes consumed by the deserialize handler when present).
- Mutates p_entity: overwrites p_entity->_serialization_header (forcing size_of__struct to sizeof(Entity)), overwrites p_entity->entity_data, and overwrites selected p_entity->entity_functions slots via sanitize_entity_functions.
- On read failures, emits a log message via debug_error.
- When m_entity_deserialize_handler is non-null, transfers control to it; any additional reads and further mutations of the entity and game state performed by that handler are outside this function's own observable scope.
