# Function Review: register_game_action__tcp_connect__reject

## File of Origin
`core/source/game_action/core/tcp/game_action__tcp_connect__reject.c`

## Semantic
Registers the `Game_Action_Kind__TCP_Connect__Reject` entry in the provided `Game_Action_Logic_Table` as a message-type entry, meaning it carries no process handlers and only sanitizes flags on inbound and outbound paths.

## Pre-conditions
1. `p_game_action_logic_table` must be a non-null pointer to a valid, initialized `Game_Action_Logic_Table`.
2. The `Game_Action_Kind__TCP_Connect__Reject` enum value (4) must be less than `Game_Action_Kind__Unknown` (15), which is guaranteed by the enum definition, ensuring `get_p_game_action_logic_entry_by__game_action_kind` returns a valid pointer.

## Post-conditions
1. The `Game_Action_Logic_Entry` at index `Game_Action_Kind__TCP_Connect__Reject` in `p_game_action_logic_table->game_action_logic_entries` is fully initialized with all fields set to message-type defaults:
   - `m_process_of__game_action__outbound` = 0 (no process handler)
   - `m_process_of__game_action__inbound` = 0 (no process handler)
   - `game_action_flags__outbound` = `GAME_ACTION_FLAGS__OUTBOUND_SANITIZE`
   - `game_action_flags__outbound_mask` = `GAME_ACTION_FLAG_MASK__OUTBOUND_SANITIZE`
   - `game_action_flags__inbound` = `GAME_ACTION_FLAGS__INBOUND_SANITIZE`
   - `game_action_flags__inbound_mask` = `GAME_ACTION_FLAG_MASK__INBOUND_SANITIZE`
   - `process_flags_of__game_action__outbound` = 0
   - `process_flags_of__game_action__inbound` = 0
   - `process_priority__u8` = `PROCESS_PRIORITY__MINIMUM`

## Correctness Verdict
**Correct**

## Semantic Alignment
The implementation fulfills the semantic intent. A TCP Connect Reject is a simple rejection message sent by the server to deny a connection attempt. It does not require custom process handlers, so initializing it as a message-type entry (no process functions, only flag sanitization) is appropriate. This is consistent with the pattern used by other register functions in the codebase — for example, `register_game_action__tcp_connect` uses `initialize_game_action_logic_entry` directly with process handlers and specific flags, whereas `register_game_action__tcp_connect__reject` correctly uses the `initialize_game_action_logic_entry_as__message` convenience wrapper since no processing is needed.

## Implementation Correctness
- **Type compatibility**: The parameter `p_game_action_logic_table` is `Game_Action_Logic_Table *`, matching the expected type of `get_p_game_action_logic_entry_by__game_action_kind`. The returned `Game_Action_Logic_Entry *` matches the expected type of `initialize_game_action_logic_entry_as__message`. No implicit conversions or truncation occur.
- **Undefined behavior**: No broken pointer arithmetic, null dereference, type punning, or out-of-bounds access. The `get_p_game_action_logic_entry_by__game_action_kind` function performs bounds checking via `the_kind_of__game_action >= Game_Action_Kind__Unknown`, and since `Game_Action_Kind__TCP_Connect__Reject` is a compile-time constant with value 4 (well below `Game_Action_Kind__Unknown` = 15), the returned pointer is always valid. The null check in the callee is never triggered for this specific kind.
- **Validation**: The function does not perform a null check on the return value of `get_p_game_action_logic_entry_by__game_action_kind`. However, this is not a practical concern because the kind is a compile-time constant guaranteed to be in-bounds. This is consistent with the codebase convention where other register functions (e.g., `register_game_action__tcp_connect`) also do not check the return value.
- **Struct initialization completeness**: All 9 fields of `Game_Action_Logic_Entry` are assigned via the underlying `initialize_game_action_logic_entry` call. No member is omitted and no reordering occurs.

## Side Effects
The function mutates the `Game_Action_Logic_Entry` at index `Game_Action_Kind__TCP_Connect__Reject` within the provided `Game_Action_Logic_Table`, overwriting all fields with message-type defaults. No other memory is affected.
