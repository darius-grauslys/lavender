register_game_action__input_for__server — core/source/game_action/core/input/game_action__input.c

Registers the server-side game action logic entry for `Game_Action_Kind__Input` in the provided logic table, configuring it with local outbound flags, inbound sanitization, maximum process priority, and the server-side inbound input processing handler.

Pre-conditions:
1. `p_game_action_logic_table` must be a non-null pointer to a valid, initialized `Game_Action_Logic_Table`.
2. The `Game_Action_Kind__Input` enum value must be within bounds (i.e., less than `Game_Action_Kind__Unknown`) so that `get_p_game_action_logic_entry_by__game_action_kind` returns a valid entry pointer rather than null.

Post-conditions:
1. The `Game_Action_Logic_Entry` at index `Game_Action_Kind__Input` in the table is fully initialized with the following configuration:
   - Outbound flags: `GAME_ACTION_FLAGS__OUTBOUND_SANITIZE | GAME_ACTION_FLAGS__BIT_IS_LOCAL` (input is local on the server, not relayed over TCP).
   - Outbound mask: `GAME_ACTION_FLAG_MASK__OUTBOUND_SANITIZE` (only sanitizes the `IS_ALLOCATED` bit on outbound).
   - Inbound flags: `GAME_ACTION_FLAGS__INBOUND_SANITIZE` (marks as inbound/bound).
   - Inbound mask: `GAME_ACTION_FLAG_MASK__INBOUND_SANITIZE` (sanitizes `IS_ALLOCATED` and `IS_IN_OR__OUT_BOUND` bits on inbound).
   - Process priority: `PROCESS_PRIORITY__0_MAXIMUM`.
   - Outbound process handler: `0` (null — server does not process outbound input actions).
   - Outbound process flags: `PROCESS_FLAGS__NONE`.
   - Inbound process handler: `m_process__game_action__input__inbound_server`.
   - Inbound process flags: `PROCESS_FLAGS__NONE`.

Correctness Verdict: Correct

Semantic Alignment:
The function correctly fulfills its semantic intent of registering the server-side logic entry for input game actions. The outbound flags include `GAME_ACTION_FLAGS__BIT_IS_LOCAL` to prevent the server from relaying its own input actions over TCP, which is consistent with the server's role of driving client input state locally. The inbound handler `m_process__game_action__input__inbound_server` is correctly wired to process incoming input game actions by looking up the client via UUID and copying the input into the client's input struct. The parameter ordering matches the `initialize_game_action_logic_entry` signature exactly.

Implementation Correctness:
Type compatibility — all arguments match their corresponding parameter types in `initialize_game_action_logic_entry`:
   - The first argument (entry pointer) is `Game_Action_Logic_Entry*`, matching the parameter type.
   - Flag arguments are `Game_Action_Flags` (uint8_t), matching the `Game_Action_Flags` typedef.
   - `PROCESS_PRIORITY__0_MAXIMUM` is used for `Process_Priority__u8`.
   - `0` is used for the outbound `m_Process` (function pointer), which is valid as null.
   - `PROCESS_FLAGS__NONE` (0) is used for `Process_Flags__u8`.
   - `m_process__game_action__input__inbound_server` is of type `m_Process`, matching the parameter.
No implicit conversions or truncation occur.
No undefined behavior — no pointer arithmetic, no null dereference (the entry pointer returned by `get_p_game_action_logic_entry_by__game_action_kind` is assumed valid per pre-condition 2), no type punning, no out-of-bounds access.
No validation is performed within this function — it is the caller's responsibility to ensure the logic table is valid and that `Game_Action_Kind__Input` is a valid index. This is appropriate for a registration function.

Side Effects:
The function mutates the `Game_Action_Logic_Entry` at index `Game_Action_Kind__Input` within the provided `Game_Action_Logic_Table`, initializing all of its fields via `initialize_game_action_logic_entry`. No other state is modified.
