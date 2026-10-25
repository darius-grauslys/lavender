# register_game_action__bad_request

**File of origin:** `core/source/game_action/core/game_action__bad_request.c`

## Semantic

Registers the `Game_Action_Kind__Bad_Request` entry in the game action logic table by initializing its `Game_Action_Logic_Entry` with appropriate flags, process priority, and inbound/outbound process handlers.

## Pre-conditions

1. `p_game_action_logic_table` must be a non-null pointer to an initialized `Game_Action_Logic_Table` (i.e., its `game_action_logic_entries` array must be valid and accessible).
2. `Game_Action_Kind__Bad_Request` must be a valid index within the `game_action_logic_entries` array (it is an enum value less than `Game_Action_Kind__Unknown`).

## Post-conditions

1. The `Game_Action_Logic_Entry` at index `Game_Action_Kind__Bad_Request` is fully initialized with all 9 fields set:
   - `m_process_of__game_action__outbound` = null (no outbound processing)
   - `m_process_of__game_action__inbound` = `m_process__game_action__bad_request__inbound`
   - `game_action_flags__outbound` = `GAME_ACTION_FLAGS__OUTBOUND_SANITIZE` (= `GAME_ACTION_FLAGS__NONE`, i.e. 0)
   - `game_action_flags__outbound_mask` = `GAME_ACTION_FLAG_MASK__OUTBOUND_SANITIZE` (= `GAME_ACTION_FLAGS__BIT_IS_ALLOCATED`)
   - `game_action_flags__inbound` = `GAME_ACTION_FLAGS__INBOUND_SANITIZE` (= `GAME_ACTION_FLAGS__BIT_IS_IN_OR__OUT_BOUND`)
   - `game_action_flags__inbound_mask` = `GAME_ACTION_FLAG_MASK__INBOUND_SANITIZE` (= `GAME_ACTION_FLAGS__BIT_IS_ALLOCATED | GAME_ACTION_FLAGS__BIT_IS_IN_OR__OUT_BOUND`)
   - `process_flags_of__game_action__outbound` = `PROCESS_FLAGS__NONE`
   - `process_flags_of__game_action__inbound` = `PROCESS_FLAGS__NONE`
   - `process_priority__u8` = `PROCESS_PRIORITY__0_MAXIMUM` (maximum priority)

## Correctness Verdict

Correct

## Semantic Alignment

The function correctly fulfills its purpose of registering the bad request game action in the logic table. It uses the raw `initialize_game_action_logic_entry` API directly (rather than a convenience wrapper like `initialize_game_action_logic_entry_as__process__in`) because the bad request action has a custom configuration: no outbound process handler (null), an inbound process handler, and maximum priority. This is semantically appropriate since a bad request is a server-side response that needs to be processed promptly inbound but requires no outbound processing. The outbound flags are set to `GAME_ACTION_FLAGS__NONE` (no special outbound behavior), and the inbound flags set the `BIT_IS_IN_OR__OUT_BOUND` bit, which is the standard sanitize pattern. The inbound process handler `m_process__game_action__bad_request__inbound` has the correct `m_Process` signature (`void (*)(Process *, Game *)`).

## Implementation Correctness

- **Type compatibility:** All arguments match their target parameter types exactly:
  - `Game_Action_Logic_Entry *` ← return of `get_p_game_action_logic_entry_by__game_action_kind(...)` ✓
  - `Game_Action_Flags` ← `GAME_ACTION_FLAGS__OUTBOUND_SANITIZE` ✓
  - `Game_Action_Flags` ← `GAME_ACTION_FLAG_MASK__OUTBOUND_SANITIZE` ✓
  - `Game_Action_Flags` ← `GAME_ACTION_FLAGS__INBOUND_SANITIZE` ✓
  - `Game_Action_Flags` ← `GAME_ACTION_FLAG_MASK__INBOUND_SANITIZE` ✓
  - `Process_Priority__u8` ← `PROCESS_PRIORITY__0_MAXIMUM` ✓
  - `m_Process` ← `0` (null function pointer, valid for "no outbound process") ✓
  - `Process_Flags__u8` ← `PROCESS_FLAGS__NONE` ✓
  - `m_Process` ← `m_process__game_action__bad_request__inbound` ✓
  - `Process_Flags__u8` ← `PROCESS_FLAGS__NONE` ✓
- **No undefined behavior:** No pointer arithmetic, no null dereference, no type punning, no out-of-bounds access within this function. The function delegates to `get_p_game_action_logic_entry_by__game_action_kind` which performs bounds checking on `Game_Action_Kind__Bad_Request` against `Game_Action_Kind__Unknown`.
- **Validation:** No additional validation is needed — this is a registration function. The null-check on `p_game_action_logic_table` is the caller's responsibility, consistent with the codebase pattern (e.g., `register_game_action__tcp_delivery` follows the same convention).

## Side Effects

Mutates the `Game_Action_Logic_Entry` at index `Game_Action_Kind__Bad_Request` within the provided `Game_Action_Logic_Table`, writing all 9 fields of the struct via the delegated `initialize_game_action_logic_entry` call.
