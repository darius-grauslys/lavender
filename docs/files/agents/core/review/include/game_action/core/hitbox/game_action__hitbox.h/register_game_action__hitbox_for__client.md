register_game_action__hitbox_for__client — core/source/game_action/core/hitbox/game_action__hitbox.c

Configures the Game_Action_Logic_Entry for the Hitbox game action on the client side, registering the hitbox processing function as the inbound handler with immediate-processing semantics.

Pre-conditions:
1. p_game_action_logic_table must be a non-null pointer to an initialized Game_Action_Logic_Table. The caller is responsible for ensuring this; the function does not validate it.
2. The Game_Action_Logic_Table must have been initialized (e.g., via initialize_game_action_logic_table) so that the entries array is valid.
3. Game_Action_Kind__Hitbox must be a valid enum value below Game_Action_Kind__Unknown, which it is.

Post-conditions:
1. The Game_Action_Logic_Entry at index Game_Action_Kind__Hitbox in p_game_action_logic_table is mutated with the following configuration:
   - Outbound process function is set to NULL (0) — the client does not process outbound hitbox actions.
   - Outbound process flags are set to 0.
   - Outbound game action flags are set to GAME_ACTION_FLAGS__OUTBOUND_SANITIZE (0).
   - Outbound game action flag mask is set to GAME_ACTION_FLAG_MASK__OUTBOUND_SANITIZE (BIT(0) = IS_ALLOCATED).
   - Inbound process function is set to m_process__game_action__hitbox — the client processes hitbox actions when received inbound.
   - Inbound process flags are set to PROCESS_FLAG__IS_CRITICAL.
   - Inbound game action flags are set to GAME_ACTION_FLAGS__INBOUND_SANITIZE | GAME_ACTION_FLAGS__BIT_IS_PROCESSED_ON_INVOCATION_OR_RESPONSE (BIT(1) | BIT(3)).
   - Inbound game action flag mask is set to GAME_ACTION_FLAG_MASK__INBOUND_SANITIZE (BIT(0) | BIT(1)).
   - Process priority is set to PROCESS_PRIORITY__0_MAXIMUM.

Correctness Verdict: Correct

Semantic Alignment:
The function correctly configures the hitbox game action for client-side processing. In the Lavender server-authoritative model, the server is the authority for hitbox state (processed as outbound on the server), while the client receives and applies hitbox updates (processed as inbound on the client). The client registration correctly:
- Sets the outbound process to 0/0 (client does not originate hitbox actions).
- Sets the inbound process to m_process__game_action__hitbox with PROCESS_FLAG__IS_CRITICAL (client applies received hitbox state with critical priority).
- Adds GAME_ACTION_FLAGS__BIT_IS_PROCESSED_ON_INVOCATION_OR_RESPONSE to inbound flags, signaling that the client should process the hitbox action immediately upon receipt (on invocation or response), rather than deferring.

This contrasts with the server registration (register_game_action__hitbox_for__server), which sets the hitbox process as the outbound handler without the IS_PROCESSED_ON_INVOCATION_OR_RESPONSE flag, reflecting the server's role as the originator of hitbox state.

Implementation Correctness:
Type compatibility — all arguments match their parameter types exactly:
- m_process__game_action__hitbox is of type m_Process (void (*)(Process*, Game*)) and matches the m_Process parameter type.
- PROCESS_FLAG__IS_CRITICAL is of type Process_Flags__u8 and matches the Process_Flags__u8 parameter type.
- All Game_Action_Flags and masks are of type Game_Action_Flags (uint8_t) and match.
- PROCESS_PRIORITY__0_MAXIMUM is of type Process_Priority__u8 and matches.
No implicit conversions or truncation occur.

Undefined behavior — no null pointer dereference, no broken pointer arithmetic, no type punning, no out-of-bounds access within this function. The call to get_p_game_action_logic_entry_by__game_action_kind could theoretically return NULL if the game action kind were invalid, but Game_Action_Kind__Hitbox is a valid enum value below Game_Action_Kind__Unknown, so the inline check passes. The function does not itself dereference the returned pointer; it passes it to initialize_game_action_logic_entry. If p_game_action_logic_table were NULL, get_p_game_action_logic_entry_by__game_action_kind would dereference NULL, but this is the caller's responsibility and is consistent with the server version's pattern.

Validation — no validation of p_game_action_logic_table is performed, which is appropriate for this low-level registration function and is consistent with the server counterpart. The game action kind validation is handled inside get_p_game_action_logic_entry_by__game_action_kind.

Side Effects:
Mutates the Game_Action_Logic_Entry at index Game_Action_Kind__Hitbox within p_game_action_logic_table->game_action_logic_entries. No other state is modified. No dynamic allocation or deallocation occurs.
