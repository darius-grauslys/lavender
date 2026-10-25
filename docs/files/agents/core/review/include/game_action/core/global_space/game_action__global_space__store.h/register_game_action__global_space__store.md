register_game_action__global_space__store — core/source/game_action/core/global_space/game_action__global_space__store.c

Registers the game action logic entry for Game_Action_Kind__Global_Space__Store into the provided game action logic table, configuring its outbound process handler, flags, and priority.

Pre-conditions:
1. p_game_action_logic_table must be a non-null pointer to a fully initialized Game_Action_Logic_Table.
2. Game_Action_Kind__Global_Space__Store must be a valid enum value less than Game_Action_Kind__Unknown (it is, so get_p_game_action_logic_entry_by__game_action_kind will not return null).

Post-conditions:
1. The Game_Action_Logic_Entry at index Game_Action_Kind__Global_Space__Store in p_game_action_logic_table is fully initialized with the specified flags, process handler, and priority.
2. The entry's outbound process handler is set to m_process__game_action__global_space__store.
3. The entry's inbound process handler is set to null (0).
4. The entry's outbound process flags are set to PROCESS_FLAG__IS_CRITICAL.
5. The entry's inbound process flags are set to 0.
6. The entry's process priority is set to PROCESS_PRIORITY__0_MAXIMUM.
7. The entry's outbound flags are set to GAME_ACTION_FLAGS__OUTBOUND_SANITIZE | GAME_ACTION_FLAGS__BIT_IS_WITH_PROCESS | GAME_ACTION_FLAGS__BIT_IS_PROCESSED_ON_INVOCATION_OR_RESPONSE | GAME_ACTION_FLAGS__BIT_IS_LOCAL.
8. The entry's outbound sanitize mask is set to GAME_ACTION_FLAG_MASK__OUTBOUND_SANITIZE.
9. The entry's inbound flags are set to GAME_ACTION_FLAGS__INBOUND_SANITIZE.
10. The entry's inbound sanitize mask is set to GAME_ACTION_FLAG_MASK__INBOUND_SANITIZE.

Correctness Verdict: Correct

Semantic Alignment:
The function correctly registers the global space store game action by initializing all fields of the Game_Action_Logic_Entry struct via initialize_game_action_logic_entry. The configuration is semantically appropriate for a local, process-driven game action:
- GAME_ACTION_FLAGS__BIT_IS_LOCAL: the action is local and will not be transmitted over TCP.
- GAME_ACTION_FLAGS__BIT_IS_WITH_PROCESS: the action is associated with a process handler.
- GAME_ACTION_FLAGS__BIT_IS_PROCESSED_ON_INVOCATION_OR_RESPONSE: the process runs immediately upon dispatch.
- The outbound process handler (m_process__game_action__global_space__store) is set, while the inbound handler is null, consistent with a local-only action.
- PROCESS_PRIORITY__0_MAXIMUM and PROCESS_FLAG__IS_CRITICAL ensure the serialization process runs at the highest priority and is treated as critical.
- The outbound and inbound sanitize masks are set to the standard masks (GAME_ACTION_FLAG_MASK__OUTBOUND_SANITIZE and GAME_ACTION_FLAG_MASK__INBOUND_SANITIZE), consistent with the pattern used by other registration functions (e.g., register_game_action__global_space__resolve).

Implementation Correctness:
Type compatibility — all arguments match their parameter types exactly:
- Game_Action_Logic_Entry* from get_p_game_action_logic_entry_by__game_action_kind matches the first parameter of initialize_game_action_logic_entry.
- Game_Action_Flags (uint8_t) for all flag arguments; the bitwise-OR of BIT(2)|BIT(3)|BIT(5) fits within uint8_t.
- Process_Priority__u8 (uint8_t) for PROCESS_PRIORITY__0_MAXIMUM (value 0).
- m_Process function pointer for m_process__game_action__global_space__store; its signature (void(Process*, Game*)) matches the m_Process typedef exactly.
- Process_Flags__u8 (uint8_t) for PROCESS_FLAG__IS_CRITICAL (BIT(0) = 1) and 0 for both inbound handler and flags.
No implicit conversions or truncation occur.

Undefined behavior — no pointer arithmetic, no null dereference (the table pointer is assumed valid per caller responsibility, consistent with codebase conventions), no type punning, no out-of-bounds access.

Validation — no validation is performed on p_game_action_logic_table. This is consistent with the codebase pattern for registration functions; null-checking is the caller's responsibility. The kind parameter (Game_Action_Kind__Global_Space__Store) is a valid enum constant, so get_p_game_action_logic_entry_by__game_action_kind will not return null.

Side Effects:
Mutates the Game_Action_Logic_Entry at index Game_Action_Kind__Global_Space__Store within p_game_action_logic_table, fully configuring it for the global space store action. No other side effects.
