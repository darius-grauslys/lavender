m_process__dispose_handler__tcp__default — core/source/process/tcp_game_action_process.c

Disposes a TCP game-action process by resolving any pending game action held in the serialization request's p_data, then releasing the serialization request back to the platform.

Pre-conditions:
1. p_process must be non-null and point to a valid Process whose p_process_data points to a Serialization_Request (set up by set_game_action_process_as__tcp_payload_receiver).
2. p_game must be non-null and point to a valid, initialized Game with a valid p_PLATFORM_file_system_context.
3. p_process->p_process_data must be non-null and must point to a valid Serialization_Request (guaranteed when this handler is set via set_game_action_process_as__tcp_payload_receiver).
4. p_serialization_request->p_data may be NULL or may point to a valid Game_Action; if non-null it is treated as a Game_Action.

Post-conditions:
1. If p_serialization_request->p_data was non-null, resolve_game_action is invoked with the game action's source UUID and the action itself, and p_serialization_request->p_data is set to 0.
2. PLATFORM_release_serialization_request is called to release the serialization request back to the platform's free pool.
3. p_process->p_process_data is not directly modified by this function (the caller, release_process_from__process_manager, re-initializes the process as an empty process afterward).

Correctness Verdict: Correct

Semantic Alignment:
The implementation fulfills its semantic intent as a dispose handler for TCP game action processes. When a TCP payload-receiving process is disposed, the handler checks whether a game action was received (p_data non-null). If so, it resolves that game action through the game's action resolution mechanism, then nulls p_data to prevent any double-resolution. Finally, it releases the serialization request back to the platform. This matches the documented contract in tcp_game_action_process.h, which states that p_process_data points to a serialization_request and that the serialization_request's p_data holds the former contents of p_process_data (which may be a Game_Action).

Implementation Correctness:
Type compatibility — p_process->p_process_data is void * and is cast to Serialization_Request *, which is valid C. p_serialization_request->p_data is void * and is cast to Game_Action * for resolve_game_action and to access uuid_of__client__u32 via the GA_UUID_SOURCE macro; these casts are consistent with the documented usage where p_data holds a Game_Action.
Undefined behavior — no broken pointer arithmetic, no type punning through unions (casts are through void *). The null check on p_serialization_request->p_data prevents dereferencing a null pointer before accessing the Game_Action fields. No out-of-bounds access.
Validation — no null checks on p_process or p_game are performed within this function. However, this is consistent with the codebase pattern: the caller (release_process_from__process_manager in process_manager.c) guards with does_process_have__dispose_handler, which has debug-mode null checks, and p_game is passed from the process manager's caller. The function is only installed as a dispose handler via set_game_action_process_as__tcp_payload_receiver, which guarantees p_process_data points to a valid Serialization_Request. No additional validation is needed at this level.

Side Effects:
1. Conditionally invokes resolve_game_action, which may mutate game state (dispatching the game action's logic).
2. Sets p_serialization_request->p_data to 0 after resolving the game action.
3. Calls PLATFORM_release_serialization_request, which releases the serialization request (and any associated TCP packet bitmap) back to the platform's allocation pool.
