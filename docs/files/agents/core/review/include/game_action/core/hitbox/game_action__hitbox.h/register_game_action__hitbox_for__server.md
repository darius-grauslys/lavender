register_game_action__hitbox_for__server — core/source/game_action/core/hitbox/game_action__hitbox.c

Registers the Game_Action_Kind__Hitbox entry in the server-side Game_Action_Logic_Table, configuring an outbound process handler with critical priority and invocation/response processing.

Pre-conditions:
1. p_game_action_logic_table must be a non-null pointer to a valid Game_Action_Logic_Table.
2. The table must have been initialized (e.g., via initialize_game_action_logic_table) so that all entries are zeroed.
3. Game_Action_Kind__Hitbox must be a valid enum value less than Game_Action_Kind__Unknown (guaranteed by the enum definition).

Post-conditions:
1. The Game_Action_Logic_Entry at index Game_Action_Kind__Hitbox in the table is mutated with the following values:
   - m_process_of__game_action__outbound = m_process__game_action__hitbox
   - m_process_of__game_action__inbound = 0 (null)
   - game_action_flags__outbound = GAME_ACTION_FLAGS__OUTBOUND_SANITIZE | GAME_ACTION_FLAGS__BIT_IS_PROCESSED_ON_INVOCATION_OR_RESPONSE
   - game_action_flags__outbound_mask = GAME_ACTION_FLAG_MASK__OUTBOUND_SANITIZE
   - game_action_flags__inbound = GAME_ACTION_FLAGS__INBOUND_SANITIZE
   - game_action_flags__inbound_mask = GAME_ACTION_FLAG_MASK__INBOUND_SANITIZE
   - process_flags_of__game_action__outbound = PROCESS_FLAG__IS_CRITICAL
   - process_flags_of__game_action__inbound = 0
   - process_priority__u8 = PROCESS_PRIORITY__0_MAXIMUM

Correctness Verdict: Incorrect

Semantic Alignment:
The function correctly sets up the hitbox game action for server-side outbound processing. The outbound process handler (m_process__game_action__hitbox) is properly assigned, and the flags indicate that the action should be processed on invocation or response. The inbound side is correctly left as null since the server does not process inbound hitbox actions.

However, the function is missing the GAME_ACTION_FLAGS__BIT_IS_WITH_PROCESS flag in the outbound flags. This flag is consistently included in all other registration functions across the codebase whenever a process handler is set and GAME_ACTION_FLAGS__BIT_IS_PROCESSED_ON_INVOCATION_OR_RESPONSE is used. For example:
- register_game_action__world__load_world sets: GAME_ACTION_FLAGS__OUTBOUND_SANITIZE | GAME_ACTION_FLAGS__BIT_IS_WITH_PROCESS | GAME_ACTION_FLAGS__BIT_IS_PROCESSED_ON_INVOCATION_OR_RESPONSE | GAME_ACTION_FLAGS__BIT_IS_LOCAL
- register_game_action__entity__spawn_for__client sets: GAME_ACTION_FLAGS__INBOUND_SANITIZE | GAME_ACTION_FLAGS__BIT_IS_WITH_PROCESS | GAME_ACTION_FLAGS__BIT_IS_PROCESSED_ON_INVOCATION_OR_RESPONSE | GAME_ACTION_FLAGS__BIT_IS_LOCAL
- register_game_action__tcp_connect sets: GAME_ACTION_FLAGS__INBOUND_SANITIZE | GAME_ACTION_FLAGS__BIT_IS_WITH_PROCESS | GAME_ACTION_FLAGS__BIT_IS_PROCESSED_ON_INVOCATION_OR_RESPONSE | GAME_ACTION_FLAGS__BIT_IS_LOCAL

The inline helper functions (initialize_game_action_logic_entry_as__process__out, initialize_game_action_logic_entry_as__process__in, initialize_game_action_logic_entry_as__process__out_and_in) also all include GAME_ACTION_FLAGS__BIT_IS_WITH_PROCESS when a process handler is provided.

Without GAME_ACTION_FLAGS__BIT_IS_WITH_PROCESS, the dispatch_game_action_for__client function will NOT allocate a dedicated Process for this game action. Instead, it falls into the else-if branch that runs the process handler inline using a stack-allocated Process. This means:
- The game action is not copied/allocated in the game action manager
- The process executes immediately during dispatch rather than being queued
- PROCESS_FLAG__IS_CRITICAL is effectively ignored since no dedicated Process is allocated through the process manager

This is a semantic deviation from the intended pattern. The same issue exists in register_game_action__hitbox_for__client, which also omits GAME_ACTION_FLAGS__BIT_IS_WITH_PROCESS from its inbound flags despite setting an inbound process handler.

Implementation Correctness:
Type compatibility — all parameter types match the target function signature exactly. The get_p_game_action_logic_entry_by__game_action_kind function returns Game_Action_Logic_Entry*, which matches the first parameter of initialize_game_action_logic_entry. All flag constants are of type Game_Action_Flags (uint8_t), and all process/priority/flag parameters match their respective types. No implicit conversions or truncation.

Undefined behavior — no broken pointer arithmetic, no null dereference, no type punning, no out-of-bounds access. The function does not check the return value of get_p_game_action_logic_entry_by__game_action_kind for null, but this is consistent with all other registration functions in the codebase and is acceptable given that Game_Action_Kind__Hitbox is a compile-time constant known to be valid.

Validation — no validation is needed beyond what is already provided. The function follows the same pattern as all other registration functions.

Side Effects:
The function mutates the Game_Action_Logic_Entry at index Game_Action_Kind__Hitbox within the provided Game_Action_Logic_Table. This is the only observable side effect. No other state is modified.
