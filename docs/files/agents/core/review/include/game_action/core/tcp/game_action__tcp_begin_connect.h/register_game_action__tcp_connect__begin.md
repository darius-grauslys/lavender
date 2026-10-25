register_game_action__tcp_connect__begin — core/source/game_action/core/tcp/game_action__tcp_begin_connect.c

Registers the TCP Connect Begin game action in the game action logic table by initializing its logic entry with appropriate flags, process handlers, and priority.

Pre-conditions:
1. p_game_action_logic_table must be a non-null pointer to a writable Game_Action_Logic_Table object.
2. Game_Action_Kind__TCP_Connect__Begin must be a valid enum value less than Game_Action_Kind__Unknown (it is; the enum defines it as value 2).

Post-conditions:
1. The Game_Action_Logic_Entry at index Game_Action_Kind__TCP_Connect__Begin in the table is fully initialized with:
   - Outbound flags: GAME_ACTION_FLAGS__OUTBOUND_SANITIZE | BIT_IS_WITH_PROCESS | BIT_IS_PROCESSED_ON_INVOCATION_OR_RESPONSE | BIT_IS_LOCAL
   - Outbound mask: GAME_ACTION_FLAG_MASK__OUTBOUND_SANITIZE (BIT(0), i.e. IS_ALLOCATED)
   - Inbound flags: GAME_ACTION_FLAGS__INBOUND_SANITIZE (BIT(1), i.e. IS_IN_OR__OUT_BOUND)
   - Inbound mask: GAME_ACTION_FLAG_MASK__INBOUND_SANITIZE (BIT(0) | BIT(1))
   - Process priority: PROCESS_PRIORITY__0_MAXIMUM (0)
   - Outbound process handler: m_process__game_action__tcp_connect__begin__init
   - Outbound process flags: PROCESS_FLAGS__NONE (0)
   - Inbound process handler: 0 (null)
   - Inbound process flags: 0

Correctness Verdict: Correct

Semantic Alignment:
The function correctly configures the TCP Connect Begin action as a client-side, local-only, process-based game action. The outbound handler is set to m_process__game_action__tcp_connect__begin__init, which opens a TCP socket and begins the connection handshake. The inbound handler is null and inbound flags are minimal (only INBOUND_SANITIZE), because this is a local-only action (marked with BIT_IS_LOCAL) that does not require inbound message processing. This matches the expected pattern: the companion function register_game_action__tcp_connect (in game_action__tcp_connect.c) uses the inverse configuration — local inbound with process, null outbound — confirming that Begin and Connect serve opposite roles in the connection handshake.

Implementation Correctness:
Type compatibility — every argument matches its parameter type exactly: PROCESS_PRIORITY__0_MAXIMUM is 0 (Process_Priority__u8), m_process__game_action__tcp_connect__begin__init is of type m_Process (void(*)(Process*, Game*)), PROCESS_FLAGS__NONE is 0 (Process_Flags__u8), and the literal 0 for the inbound handler and inbound process flags are valid null/zero values for their respective types. No implicit conversions or truncation occur.
No undefined behavior — get_p_game_action_logic_entry_by__game_action_kind performs a bounds check (the_kind_of__game_action >= Game_Action_Kind__Unknown returns 0), and Game_Action_Kind__TCP_Connect__Begin is a valid index within the table array. No pointer arithmetic, no null dereference, no type punning, no out-of-bounds access.
Validation — the function does not null-check p_game_action_logic_table, but this is consistent with the codebase convention for registration functions (see register_game_action__tcp_connect and all similar registration functions). The caller is responsible for providing a valid table.

Side Effects:
Mutates the Game_Action_Logic_Entry at index Game_Action_Kind__TCP_Connect__Begin within the provided Game_Action_Logic_Table. No other side effects.
