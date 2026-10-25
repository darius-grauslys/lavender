register_game_action__entity__get_for__client — core/source/game_action/core/entity/game_action__entity__get.c

Registers the Game_Action_Logic_Entry for Game_Action_Kind__Entity__Get on the client side by initializing its flags, process handlers, and priority.

Pre-conditions:
1. p_game_action_logic_table must be a non-null pointer to a writable Game_Action_Logic_Table.
2. The entry for Game_Action_Kind__Entity__Get within the table must have been zero-initialized (e.g., via initialize_game_action_logic_table) so that get_p_game_action_logic_entry_by__game_action_kind returns a valid pointer.

Post-conditions:
1. The Game_Action_Logic_Entry at index Game_Action_Kind__Entity__Get within p_game_action_logic_table is mutated to hold the specified outbound/inbound flags, masks, process handlers, process flags, and priority.
2. After return, the entry's outbound process is m_process__game_action__entity__get__outbound_client__init with PROCESS_FLAGS__NONE, and the inbound process is 0 (NULL) with process flags 0.

Correctness Verdict: Incorrect

Semantic Alignment:
The function is intended to configure the client-side logic entry for the Entity__Get game action. On the client, the outbound direction sends the entity-get request and also handles receiving the response (the outbound process m_process__game_action__entity__get__outbound_client__init mutates into a TCP receiver). The inbound direction on the client has no dedicated process function.

The outbound and inbound flags are incorrectly swapped relative to the server version. The server registration (register_game_action__entity__get_for__server) correctly places BIT_IS_WITH_PROCESS and BIT_IS_PROCESSED_ON_INVOCATION_OR_RESPONSE on the inbound flags (where a process exists) and leaves the outbound flags as plain GAME_ACTION_FLAGS__OUTBOUND_SANITIZE (where no process exists). The client registration does the opposite: it places these process-related flags on the inbound flags (where the process is NULL) and leaves the outbound flags without them (where a process does exist).

Consequence: When the client receives an inbound game action for Entity__Get (e.g., a response from the server), santize_game_action__inbound applies the inbound flags including BIT_IS_WITH_PROCESS. Then in receive_game_action_for__client, is_game_action__with_process returns true, causing dispatch_game_action_process__inbound to be called. That function retrieves the inbound process (which is NULL) and passes it to dispatch_game_action_process, which logs "m_process__game_action == 0" and returns 0 (NULL), causing the inbound action to fail. The outbound direction has a process but lacks the BIT_IS_WITH_PROCESS flag, so is_game_action__with_process will return false for outbound actions, meaning the outbound process m_process__game_action__entity__get__outbound_client__init may not be dispatched when it should be.

The fix is to swap the process-related flags (BIT_IS_WITH_PROCESS | BIT_IS_PROCESSED_ON_INVOCATION_OR_RESPONSE) from the inbound flags to the outbound flags, matching the server's pattern in reverse:
- Outbound flags should be: GAME_ACTION_FLAGS__OUTBOUND_SANITIZE | GAME_ACTION_FLAGS__BIT_IS_WITH_PROCESS | GAME_ACTION_FLAGS__BIT_IS_PROCESSED_ON_INVOCATION_OR_RESPONSE
- Inbound flags should be: GAME_ACTION_FLAGS__INBOUND_SANITIZE

Implementation Correctness:
Type compatibility — all parameter types match the initialize_game_action_logic_entry signature exactly. No implicit conversions or truncation.
No undefined behavior in this function itself — no pointer arithmetic, no null dereference, no out-of-bounds access. The pointer returned by get_p_game_action_logic_entry_by__game_action_kind is passed directly to initialize_game_action_logic_entry.
No validation is needed at this level — this is a registration function called during setup, and the caller is responsible for providing a valid table pointer.

Side Effects:
Mutates the Game_Action_Logic_Entry at index Game_Action_Kind__Entity__Get within p_game_action_logic_table, overwriting all fields (process handlers, flags, masks, priority, process flags).
