register_game_action__entity__get_for__server — core/source/game_action/core/entity/game_action__entity__get.c

Registers the server-side game action logic entry for the Entity_Get action kind by configuring its inbound process handler, flags, and priority.

Pre-conditions:
1. p_game_action_logic_table must be a non-null pointer to a writable Game_Action_Logic_Table.
2. Game_Action_Kind__Entity__Get must be a valid enum value less than Game_Action_Kind__Unknown (guaranteed by get_p_game_action_logic_entry_by__game_action_kind).
3. The game action logic entry for Game_Action_Kind__Entity__Get must be allocated within the logic table's fixed-size array (always true for valid enum indices).

Post-conditions:
1. The Game_Action_Logic_Entry for Game_Action_Kind__Entity__Get is mutated to configure:
   - Outbound flags: GAME_ACTION_FLAGS__OUTBOUND_SANITIZE (resets to none on outbound sanitization).
   - Outbound mask: GAME_ACTION_FLAG_MASK__OUTBOUND_SANITIZE.
   - Inbound flags: GAME_ACTION_FLAGS__INBOUND_SANITIZE | GAME_ACTION_FLAGS__BIT_IS_WITH_PROCESS | GAME_ACTION_FLAGS__BIT_IS_PROCESSED_ON_INVOCATION_OR_RESPONSE.
   - Inbound mask: GAME_ACTION_FLAG_MASK__INBOUND_SANITIZE.
   - Process priority: PROCESS_PRIORITY__0_MAXIMUM (maximum priority).
   - Outbound process handler: 0 (null, server does not process outbound for this action).
   - Outbound process flags: 0.
   - Inbound process handler: m_process__game_action__entity__get__inbound_server__init.
   - Inbound process flags: PROCESS_FLAGS__NONE.

Correctness Verdict: Correct

Semantic Alignment:
The function correctly configures the server-side logic entry for the Entity_Get game action. On the server, this action is processed inbound — the server receives an entity get request from a client and responds with the entity data. The inbound process handler (m_process__game_action__entity__get__inbound_server__init) is correctly set, and the outbound process handler is correctly null (the server does not initiate outbound entity get processing). The flags correctly indicate that this action is with a process (GAME_ACTION_FLAGS__BIT_IS_WITH_PROCESS) and is processed on invocation or response (GAME_ACTION_FLAGS__BIT_IS_PROCESSED_ON_INVOCATION_OR_RESPONSE). This is consistent with the client-side registration function register_game_action__entity__get_for__client, which sets the outbound process handler instead and leaves the inbound process handler null.

Implementation Correctness:
Type compatibility — all arguments match their parameter types exactly:
  - Game_Action_Logic_Entry* from get_p_game_action_logic_entry_by__game_action_kind matches Game_Action_Logic_Entry*.
  - GAME_ACTION_FLAGS__OUTBOUND_SANITIZE and GAME_ACTION_FLAGS__INBOUND_SANITIZE match Game_Action_Flags (uint8_t).
  - GAME_ACTION_FLAG_MASK__OUTBOUND_SANITIZE and GAME_ACTION_FLAG_MASK__INBOUND_SANITIZE match Game_Action_Flags.
  - PROCESS_PRIORITY__0_MAXIMUM (value 0) matches Process_Priority__u8 (uint8_t).
  - 0 matches m_Process (function pointer) and Process_Flags__u8 (uint8_t).
  - m_process__game_action__entity__get__inbound_server__init matches m_Process.
  - PROCESS_FLAGS__NONE (value 0) matches Process_Flags__u8.
No implicit conversions or truncation.
No undefined behavior — no pointer arithmetic, no null dereference, no type punning, no out-of-bounds access. The entry pointer is guaranteed non-null by get_p_game_action_logic_entry_by__game_action_kind for valid enum values.
No additional validation is needed — this is a registration function that configures a pre-allocated struct entry. The caller is responsible for ensuring p_game_action_logic_table is valid.

Side Effects:
Mutates the Game_Action_Logic_Entry struct for Game_Action_Kind__Entity__Get within the logic table, setting all nine fields (inbound/outbound process handlers, inbound/outbound flags, inbound/outbound masks, process priority, and process flags).
