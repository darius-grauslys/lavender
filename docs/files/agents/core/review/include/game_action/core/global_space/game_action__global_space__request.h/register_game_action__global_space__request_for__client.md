register_game_action__global_space__request_for__client — core/source/game_action/core/global_space/game_action__global_space__request__multiplayer.c

Registers the client-side game action logic entry for Game_Action_Kind__Global_Space__Request, configuring it with an outbound-only process handler that polls for global space construction completion.

Pre-conditions:
1. p_game_action_logic_table must be a non-null pointer to a valid, initialized Game_Action_Logic_Table.
2. Game_Action_Kind__Global_Space__Request must be a valid enum value less than Game_Action_Kind__Unknown (it is, as defined in the enum).

Post-conditions:
1. The Game_Action_Logic_Entry at index Game_Action_Kind__Global_Space__Request in p_game_action_logic_table is fully initialized with client-side outbound process configuration.
2. The outbound process handler is set to m_process__game_action__global_space__request__outbound_client__init.
3. The outbound process flags are set to PROCESS_FLAG__IS_CRITICAL.
4. The process priority is set to PROCESS_PRIORITY__0_MAXIMUM.
5. The inbound process handler is set to 0 (null) — no inbound handler is registered for the client side.
6. The inbound process flags are set to PROCESS_FLAGS__NONE.
7. Outbound game action flags are set to GAME_ACTION_FLAGS__OUTBOUND_SANITIZE | GAME_ACTION_FLAGS__BIT_IS_WITH_PROCESS | GAME_ACTION_FLAGS__BIT_IS_PROCESSED_ON_INVOCATION_OR_RESPONSE.
8. Outbound game action mask is set to GAME_ACTION_FLAG_MASK__OUTBOUND_SANITIZE.
9. Inbound game action flags are set to GAME_ACTION_FLAGS__INBOUND_SANITIZE.
10. Inbound game action mask is set to GAME_ACTION_FLAG_MASK__INBOUND_SANITIZE.

Correctness Verdict: Correct

Semantic Alignment:
The function correctly delegates to initialize_game_action_logic_entry_as__process__out, which is the appropriate helper for registering a client-side game action that only requires an outbound process (no inbound process). The outbound handler m_process__game_action__global_space__request__outbound_client__init is the correct init function for the client-side global space request flow, which allocates chunk and collision node resources, sets up TCP payload reception, and then transitions to the run handler m_process__game_action__global_space__request__outbound_client that polls for completion. This aligns with the documented intent: "Only defined for client, poll for the completion of the global_space." The server version (register_game_action__global_space__request_for__server) uses both outbound and inbound handlers, while the client version correctly uses only the outbound handler, as the client does not need to handle inbound requests for this action kind.

Implementation Correctness:
Type compatibility — p_game_action_logic_table is Game_Action_Logic_Table*, which matches the parameter type of get_p_game_action_logic_entry_by__game_action_kind. Game_Action_Kind__Global_Space__Request is a Game_Action_Kind enum value, matching the second parameter. PROCESS_PRIORITY__0_MAXIMUM is a Process_Priority__u8 (defined as 0). m_process__game_action__global_space__request__outbound_client__init is a m_Process function pointer, matching the parameter type. PROCESS_FLAG__IS_CRITICAL is a Process_Flags__u8, matching the parameter type. No implicit conversions or truncation.
No undefined behavior — get_p_game_action_logic_entry_by__game_action_kind returns a pointer into the game_action_logic_entries array of the table. Since Game_Action_Kind__Global_Space__Request is a valid enum value (less than Game_Action_Kind__Unknown), the bounds check in that function passes and a valid pointer is returned. The pointer is then passed to initialize_game_action_logic_entry_as__process__out, which dereferences it to initialize all fields. No null dereference occurs under normal conditions. No pointer arithmetic, no type punning, no out-of-bounds access.
Validation — no validation is performed on the return value of get_p_game_action_logic_entry_by__game_action_kind (i.e., no null check before passing to the initializer). This is consistent with the server version (register_game_action__global_space__request_for__server) and is acceptable because Game_Action_Kind__Global_Space__Request is a compile-time constant valid enum value that cannot trigger the null return path. The caller is responsible for ensuring p_game_action_logic_table is valid.

Side Effects:
Mutates the Game_Action_Logic_Entry at index Game_Action_Kind__Global_Space__Request within the Game_Action_Logic_Table pointed to by p_game_action_logic_table. All fields of the entry are initialized: outbound/inbound process handlers, outbound/inbound game action flags and masks, outbound/inbound process flags, and process priority. No other state is modified.