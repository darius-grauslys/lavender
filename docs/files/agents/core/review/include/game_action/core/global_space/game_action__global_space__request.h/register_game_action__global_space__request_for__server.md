register_game_action__global_space__request_for__server — core/source/game_action/core/global_space/game_action__global_space__request__multiplayer.c

Registers the Game_Action_Logic_Entry for Game_Action_Kind__Global_Space__Request in the server-side logic table, configuring outbound and inbound process handlers, flags, masks, process priority, and process flags.

Pre-conditions:
1. p_game_action_logic_table must be a non-null pointer to a writable, initialized Game_Action_Logic_Table.
2. Game_Action_Kind__Global_Space__Request is a valid enum value (between Game_Action_Kind__None and Game_Action_Kind__Unknown), so get_p_game_action_logic_entry_by__game_action_kind will return a valid non-null pointer.

Post-conditions:
1. The Game_Action_Logic_Entry at index Game_Action_Kind__Global_Space__Request within p_game_action_logic_table is fully configured with:
   - Outbound process handler: m_process__game_action__global_space__request__outbound_server
   - Inbound process handler: m_process__game_action__global_space__request__inbound_server__init
   - Outbound flags: GAME_ACTION_FLAGS__OUTBOUND_SANITIZE | GAME_ACTION_FLAGS__BIT_IS_LOCAL (marks the action as local — not sent over TCP)
   - Outbound mask: GAME_ACTION_FLAG_MASK__OUTBOUND_SANITIZE
   - Inbound flags: GAME_ACTION_FLAGS__INBOUND_SANITIZE | GAME_ACTION_FLAGS__BIT_IS_WITH_PROCESS | GAME_ACTION_FLAGS__BIT_IS_PROCESSED_ON_INVOCATION_OR_RESPONSE
   - Inbound mask: GAME_ACTION_FLAG_MASK__INBOUND_SANITIZE
   - Process priority: PROCESS_PRIORITY__0_MAXIMUM
   - Process flags: PROCESS_FLAGS__NONE for both outbound and inbound
2. All nine fields of the Game_Action_Logic_Entry struct are assigned.

Correctness Verdict: Correct

Semantic Alignment:
The function correctly registers the server-side logic entry for the Global_Space__Request game action. The outbound side is marked IS_LOCAL (the server processes the request locally, finding/holding the global space and dispatching a resolve action — it does not send the request over TCP). The inbound side is marked IS_WITH_PROCESS and IS_PROCESSED_ON_INVOCATION_OR_RESPONSE, indicating the server immediately processes incoming requests from clients (initializing the TCP payload bitmap and then running the inbound server process). The outbound process handler (m_process__game_action__global_space__request__outbound_server) finds the global space, marks it as constructing, and dispatches a resolve action. The inbound process handler (m_process__game_action__global_space__request__inbound_server__init) initializes the TCP payload bitmap and delegates to m_process__game_action__global_space__request__inbound_server for actual processing. This is consistent with the server's role in the global space request/resolve lifecycle.

The initialize_game_action_logic_entry function (the callee) assigns all nine fields of the Game_Action_Logic_Entry struct: m_process_of__game_action__outbound, m_process_of__game_action__inbound, game_action_flags__outbound, game_action_flags__outbound_mask, game_action_flags__inbound, game_action_flags__inbound_mask, process_flags_of__game_action__outbound, process_flags_of__game_action__inbound, and process_priority__u8. No field is omitted and no reordering occurs.

This is Lavender-style initialization (configuring struct state), not RAII-style resource acquisition. The function registers/configures the logic entry's state without acquiring external resources.

Implementation Correctness:
Type compatibility — all arguments match their corresponding parameter types exactly:
- Game_Action_Logic_Entry* ← get_p_game_action_logic_entry_by__game_action_kind return type
- Game_Action_Flags ← GAME_ACTION_FLAGS__OUTBOUND_SANITIZE | GAME_ACTION_FLAGS__BIT_IS_LOCAL
- Game_Action_Flags ← GAME_ACTION_FLAG_MASK__OUTBOUND_SANITIZE
- Game_Action_Flags ← GAME_ACTION_FLAGS__INBOUND_SANITIZE | GAME_ACTION_FLAGS__BIT_IS_WITH_PROCESS | GAME_ACTION_FLAGS__BIT_IS_PROCESSED_ON_INVOCATION_OR_RESPONSE
- Game_Action_Flags ← GAME_ACTION_FLAG_MASK__INBOUND_SANITIZE
- Process_Priority__u8 ← PROCESS_PRIORITY__0_MAXIMUM (value 0)
- m_Process ← m_process__game_action__global_space__request__outbound_server (signature: void(Process*, Game*))
- Process_Flags__u8 ← PROCESS_FLAGS__NONE (value 0)
- m_Process ← m_process__game_action__global_space__request__inbound_server__init (signature: void(Process*, Game*))
- Process_Flags__u8 ← PROCESS_FLAGS__NONE (value 0)
No implicit conversions or truncation.

No undefined behavior — no pointer arithmetic, no null dereference (get_p_game_action_logic_entry_by__game_action_kind guarantees a valid pointer for valid enum values), no type punning, no out-of-bounds access.

No validation is needed within this function — it is a low-level registration function. The caller is responsible for ensuring p_game_action_logic_table is valid. This is consistent with the codebase pattern (e.g., register_game_action__global_space__request_for__client follows the same convention).

Side Effects:
Mutates the Game_Action_Logic_Entry at index Game_Action_Kind__Global_Space__Request within p_game_action_logic_table, writing all nine struct fields with the specified process handlers, flags, masks, priority, and process flags. No other state is modified.
