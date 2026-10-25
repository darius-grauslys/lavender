m_process__game_action__global_space__request__inbound_server — core/source/game_action/core/global_space/game_action__global_space__request__multiplayer.c

Routes the chunk data of a resolved global space back to the requesting client via TCP, polling until all TCP packets are delivered.

Pre-conditions:
1. p_this_process must be a non-null pointer to a valid Process whose p_process_data is a non-null Game_Action of kind Game_Action_Kind__Global_Space__Request.
2. p_game must be a non-null pointer to a valid Game.
3. p_game_action->uuid_of__client__u32 must reference a valid, connected client (i.e., get_p_client_by__uuid_from__game must return non-null).
4. The global space referenced by the GSV in the game action must have been resolved (chunk allocated and data populated) by the time the global space is no longer in the constructing state.
5. The TCP payload bitmap in the game action must have been zero-initialized by the corresponding __init function.

Post-conditions:
1. If the global space is not found (null or local space inactive), a bad_request game action is dispatched (error code 0) and the process is failed.
2. If the global space is deconstructing, a bad_request game action is dispatched (error code 1) and the process is failed.
3. If the global space is still constructing, the process returns without completing or failing; it will be retried on subsequent process ticks.
4. If poll_game_action_process__tcp_delivery returns PLATFORM_Write_File_Error__Max_Size_Reached, all packets have been sent and the process is completed.
5. If poll_game_action_process__tcp_delivery returns PLATFORM_Write_File_Error__System_Busy, one packet was sent; the process returns without completing and will be retried.
6. If poll_game_action_process__tcp_delivery returns any other value, the process is failed.

Correctness Verdict: Correct

Semantic Alignment:
The function correctly implements the inbound server handler for a global space request. It verifies the global space exists and is in a valid state, then polls TCP delivery of the chunk data. The switch statement correctly maps Max_Size_Reached to completion, System_Busy to retry, and the default case to failure. The constructing-state early-return is appropriate for a polling function that waits for async resolve to finish.

Implementation Correctness:
Type compatibility — parameter types match function signatures exactly. The cast (u16)TCP_PAYLOAD_BITMAP__QUANTITY_OF__PAYLOADS(Chunk) is safe as the quantity is small. The (u8*)&p_global_space->p_chunk->chunk_data cast is valid since chunk_data is a union member of Chunk.
Undefined behavior — two potential null dereferences exist:
  a) p_client is not checked for null before being passed to get_p_local_space_manager_from__client. While get_p_local_space_manager_from__client returns 0 for null p_client, the subsequent get_p_local_space_from__local_space_manager(0, ...) dereferences the null Local_Space_Manager pointer (accessing p_local_space_manager->p_local_space__south_west), causing undefined behavior. This can occur if the client has disconnected.
  b) p_global_space->p_chunk is not checked for null before accessing p_chunk->chunk_data. While the resolve function should set p_chunk before clearing the constructing flag, there is no explicit guarantee, and using get_p_chunk_from__global_space() would be safer and consistent with the engine's accessor pattern.
Validation — the missing null check on p_client is a validation gap. Other callers of get_p_client_by__uuid_from__game in the codebase (e.g., dispatch_handler_process_to__create_client, dispatch_handler_process_to__load_client) do check for null. The function's role as an inbound handler justifies defensive validation here.
Dead code — p_global_space_manager is computed but never used; the function obtains the global space through the client's local space instead.

Side Effects:
1. May dispatch a bad_request game action (via dispatch_game_action__bad_request) when the global space is missing or deconstructing.
2. Mutates the TCP payload bitmap within the game action (via poll_game_action_process__tcp_delivery, which sets bits in the bitmap as packets are sent).
3. May fail or complete the process (via fail_process / complete_process).
4. Sends TCP packets to the client (via dispatch_game_action__tcp_delivery, called internally by poll_game_action_process__tcp_delivery).
