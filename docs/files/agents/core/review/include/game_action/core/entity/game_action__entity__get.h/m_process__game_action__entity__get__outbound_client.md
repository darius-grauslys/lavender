m_process__game_action__entity__get__outbound_client — core/source/game_action/core/entity/game_action__entity__get.c

Sends an entity's Entity_Data to a remote client over TCP, then enables the entity and completes the process. This is the run handler for the outbound (client-side) half of the Entity Get game action.

Pre-conditions:
1. p_this_process must be a non-null pointer to a valid Process whose p_process_data has been mutated by m_process__game_action__entity__get__outbound_client__init into a Serialization_Request*.
2. p_game must be a non-null pointer to a valid Game with an initialized World and Entity_Manager.
3. p_this_process->p_process_data must point to a Serialization_Request whose p_data field points to a valid Game_Action (set up by initialize_process_as__tcp_game_action_payload_receiver in the init function).
4. p_serialization_request->p_data (the Game_Action) must have a valid uuid_of__entity__u32 in its GA_Entity__Payload that corresponds to an allocated Entity (either pre-existing or allocated by the init function).
5. p_game_action->uuid_of__client__u32 must be a valid client identifier for TCP delivery.
6. p_game_action->_serialiation_header.uuid must be a valid game action UUID for responding to.

Post-conditions:
1. If the entity is found: the entity's Entity_Data is sent over TCP to the specified client. The process status is set to Complete (via complete_process) if delivery succeeds or reaches Max_Size_Reached, or Fail (via fail_process) if delivery returns an unexpected error.
2. If the entity is not found: the process status is set to Fail (via fail_process) and the function returns early.
3. If poll_game_action_process__tcp_delivery returns PLATFORM_Write_File_Error__System_Busy: the process remains active (no status change) and the function returns without completing or failing the process.
4. If delivery succeeds (Max_Size_Reached): set_entity_as__enabled is called on p_entity, setting the ENTITY_FLAG__IS_ENABLED bit in entity_data.entity_flags.

Correctness Verdict: Correct

Semantic Alignment:
The function correctly implements the outbound client-side handler for Entity Get. The init function (m_process__game_action__entity__get__outbound_client__init) disables the entity and sets up the process as a TCP payload receiver, transforming p_process_data from a Game_Action* to a Serialization_Request* with p_data pointing to the original Game_Action*. This run handler correctly retrieves both the Serialization_Request and the underlying Game_Action, looks up the entity by UUID, sends the entity data via TCP delivery, and then re-enables the entity upon successful delivery. The overall flow matches the intended semantics: disable entity → receive serialized data → send entity data to client → re-enable entity.

The switch statement correctly handles the PLATFORM_Write_File_Error return values as documented by poll_game_action_process__tcp_delivery: System_Busy means the transfer is still in progress (return early, keep process active), Max_Size_Reached means the transfer is complete (proceed to enable entity and complete), and any other value is an error (fail the process).

Implementation Correctness:
Type compatibility — p_this_process->p_process_data (void*) is cast to Serialization_Request*, which is correct per the documented contract of initialize_process_as__tcp_game_action_payload_receiver. p_serialization_request->p_data (void*) is cast to Game_Action*, which is correct since the init function sets it up via the same mechanism. sizeof(Entity_Data) is passed as Quantity__u32, matching the parameter type. TCP_PAYLOAD_BITMAP__QUANTITY_OF__PAYLOADS(Entity_Data) is cast to u16, matching the Quantity__u16 parameter type.
No undefined behavior — no pointer arithmetic, no null dereference (p_entity is null-checked before use), no type punning, no out-of-bounds access. The entity is looked up via get_p_entity_by__uuid_from__entity_manager which returns a valid pointer or null.
No validation is performed for p_this_process or p_game being null — this is consistent with the codebase pattern where callers are responsible for passing valid pointers, and the Process struct is managed by the Process_Manager.

Side Effects:
1. Mutates p_this_process->the_kind_of_status__this_process_has to Process_Status_Kind__Complete (via complete_process) or Process_Status_Kind__Fail (via fail_process).
2. Mutates p_entity->entity_data.entity_flags by setting ENTITY_FLAG__IS_ENABLED (via set_entity_as__enabled), but only on the success path.
3. Initiates TCP packet delivery to the remote client via poll_game_action_process__tcp_delivery, which has the side effect of sending data over the network.
4. Logs debug messages via debug_error and debug_info.
