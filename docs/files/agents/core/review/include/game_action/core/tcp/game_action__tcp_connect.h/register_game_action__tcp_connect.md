register_game_action__tcp_connect — core/source/game_action/core/tcp/game_action__tcp_connect.c, lines 146-164

Registers the TCP_Connect game action logic entry in the game action logic table, configuring it as an inbound-only, process-driven, local action with maximum priority.

Pre-conditions:
1. p_game_action_logic_table must be a non-null pointer to a valid, initialized Game_Action_Logic_Table.
2. Game_Action_Kind__TCP_Connect must be a valid enum value less than Game_Action_Kind__Unknown, so that get_p_game_action_logic_entry_by__game_action_kind returns a non-null pointer to a writable Game_Action_Logic_Entry within the table's game_action_logic_entries array.

Post-conditions:
1. The Game_Action_Logic_Entry at index Game_Action_Kind__TCP_Connect in p_game_action_logic_table is fully initialized with all nine of its fields set.
2. m_process_of__game_action__outbound is set to 0 (null) — no outbound processing is registered.
3. m_process_of__game_action__inbound is set to m_process__game_action__tcp_connect__inbound.
4. game_action_flags__outbound is set to GAME_ACTION_FLAGS__OUTBOUND_SANITIZE (= GAME_ACTION_FLAGS__NONE = 0).
5. game_action_flags__outbound_mask is set to GAME_ACTION_FLAG_MASK__OUTBOUND_SANITIZE (= GAME_ACTION_FLAGS__BIT_IS_ALLOCATED).
6. game_action_flags__inbound is set to GAME_ACTION_FLAGS__INBOUND_SANITIZE | GAME_ACTION_FLAGS__BIT_IS_WITH_PROCESS | GAME_ACTION_FLAGS__BIT_IS_PROCESSED_ON_INVOCATION_OR_RESPONSE | GAME_ACTION_FLAGS__BIT_IS_LOCAL.
7. game_action_flags__inbound_mask is set to GAME_ACTION_FLAG_MASK__INBOUND_SANITIZE (= GAME_ACTION_FLAGS__BIT_IS_ALLOCATED | GAME_ACTION_FLAGS__BIT_IS_IN_OR__OUT_BOUND).
8. process_flags_of__game_action__outbound is set to 0 (PROCESS_FLAGS__NONE).
9. process_flags_of__game_action__inbound is set to PROCESS_FLAGS__NONE (0).
10. process_priority__u8 is set to PROCESS_PRIORITY__0_MAXIMUM (0).

Correctness Verdict: Correct

Semantic Alignment:
The function correctly registers the TCP_Connect game action as an inbound-only action. The configuration is semantically appropriate:
- No outbound process is registered (0), meaning this action is not dispatched outbound from the local side.
- The inbound process is set to m_process__game_action__tcp_connect__inbound, which handles incoming TCP connection requests on the server.
- The inbound flags include BIT_IS_WITH_PROCESS (indicating a process is associated), BIT_IS_PROCESSED_ON_INVOCATION_OR_RESPONSE (indicating the process runs when invoked or in response), and BIT_IS_LOCAL (indicating the action is not sent over TCP, appropriate for the initial connection handshake).
- The outbound sanitize flags are set to NONE with a mask of BIT_IS_ALLOCATED, meaning outbound sanitization only clears the allocated bit.
- The inbound sanitize mask preserves both BIT_IS_ALLOCATED and BIT_IS_IN_OR__OUT_BOUND, with inbound flags setting BIT_IS_IN_OR__OUT_BOUND plus the process and local flags.
- Maximum priority (PROCESS_PRIORITY__0_MAXIMUM) is appropriate for a connection-handling action that should be processed promptly.

All ten arguments are passed in the correct order matching the initialize_game_action_logic_entry signature, and all argument types are compatible with their respective parameter types.

Implementation Correctness:
Type compatibility — all arguments match their parameter types exactly. The Game_Action_Logic_Entry pointer from get_p_game_action_logic_entry_by__game_action_kind is a valid pointer type. Game_Action_Flags (uint8_t) parameters receive uint8_t flag values. Process_Priority__u8 receives PROCESS_PRIORITY__0_MAXIMUM (defined as 0, a uint8_t-compatible value). m_Process function pointer parameters receive either 0 (null) or the correct function pointer. Process_Flags__u8 parameters receive 0/ PROCESS_FLAGS__NONE (both 0). No implicit conversions or truncation.
Undefined behavior — no pointer arithmetic, no null dereference (assuming pre-conditions hold), no type punning, no out-of-bounds access. If p_game_action_logic_table is valid and Game_Action_Kind__TCP_Connect is a valid enum value, get_p_game_action_logic_entry_by__game_action_kind returns a valid pointer.
Validation — the function performs no validation itself, which is appropriate for a registration function. It is the caller's responsibility to ensure p_game_action_logic_table is valid. The get_p_game_action_logic_entry_by__game_action_kind helper returns null for out-of-bounds kinds, but dereferencing that null would be the caller's responsibility to prevent.

Side Effects:
Mutates the Game_Action_Logic_Entry at index Game_Action_Kind__TCP_Connect within the Game_Action_Logic_Table pointed to by p_game_action_logic_table, initializing all nine fields to the specified flag and function pointer values.
