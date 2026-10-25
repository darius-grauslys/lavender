# Function Review: `register_game_action__world__load_world`

**File of origin:** `core/source/game_action/core/world/game_action__world__load_world.c`

---

## Semantic

Registers the `Game_Action_Kind__World__Load_World` entry in a `Game_Action_Logic_Table` by initializing its logic entry with outbound process configuration (local, critical, maximum priority), plus appropriate outbound/inbound flag masks. No inbound process handler is registered.

---

## Pre-conditions

1. `p_game_action_logic_table` must be non-null and point to a valid, initialized `Game_Action_Logic_Table`. The function does not perform a null check; this is consistent with the codebase convention where all registration functions assume a valid table.
2. The `Game_Action_Logic_Table` must have been initialized (e.g., via `initialize_game_action_logic_table`) so that its `game_action_logic_entries` array is in a usable state.

---

## Post-conditions

1. The `Game_Action_Logic_Entry` at index `Game_Action_Kind__World__Load_World` in `p_game_action_logic_table` is fully initialized with:
   - **Outbound flags:** `GAME_ACTION_FLAGS__OUTBOUND_SANITIZE | GAME_ACTION_FLAGS__BIT_IS_WITH_PROCESS | GAME_ACTION_FLAGS__BIT_IS_PROCESSED_ON_INVOCATION_OR_RESPONSE | GAME_ACTION_FLAGS__BIT_IS_LOCAL`
   - **Outbound mask:** `GAME_ACTION_FLAG_MASK__OUTBOUND_SANITIZE` (i.e., `GAME_ACTION_FLAGS__BIT_IS_ALLOCATED`)
   - **Inbound flags:** `GAME_ACTION_FLAGS__INBOUND_SANITIZE` (i.e., `GAME_ACTION_FLAGS__BIT_IS_IN_OR__OUT_BOUND`)
   - **Inbound mask:** `GAME_ACTION_FLAG_MASK__INBOUND_SANITIZE` (i.e., `GAME_ACTION_FLAGS__BIT_IS_ALLOCATED | GAME_ACTION_FLAGS__BIT_IS_IN_OR__OUT_BOUND`)
   - **Process priority:** `PROCESS_PRIORITY__0_MAXIMUM` (0, highest priority)
   - **Outbound process handler:** `m_process__game_action__world__load_world`
   - **Outbound process flags:** `PROCESS_FLAG__IS_CRITICAL`
   - **Inbound process handler:** `0` (none)
   - **Inbound process flags:** `0`

---

## Correctness Verdict

**Correct**

---

## Semantic Alignment

The implementation correctly fulfills its intent. The `World__Load_World` action is configured as a local, outbound-only processed action with maximum priority and a critical process flag. This is semantically appropriate:

- `GAME_ACTION_FLAGS__BIT_IS_LOCAL` indicates the action is handled locally (not forwarded over the network).
- `GAME_ACTION_FLAGS__BIT_IS_WITH_PROCESS` and `GAME_ACTION_FLAGS__BIT_IS_PROCESSED_ON_INVOCATION_OR_RESPONSE` indicate the action is dispatched as a process immediately upon invocation.
- `PROCESS_FLAG__IS_CRITICAL` marks the process as critical, consistent with world-loading being a critical operation.
- No inbound process handler is set (`0, 0`), which is appropriate because this action is outbound/local-only — there is no inbound response handler needed.

This pattern is consistent with the sibling function `register_game_action__world__load_client` (in `game_action__world__load_client.c`), which uses the same outbound flags and `PROCESS_FLAG__IS_CRITICAL` for its outbound process.

The `Game_Action_Kind__World__Load_World` enum value is a valid index (less than `Game_Action_Kind__Unknown`), so `get_p_game_action_logic_entry_by__game_action_kind` will return a valid non-null pointer to the entry in the table's `game_action_logic_entries` array.

---

## Implementation Correctness

- **Type compatibility:** All arguments are passed with types matching the `initialize_game_action_logic_entry` signature exactly:
  - The first argument (lookup result) is `Game_Action_Logic_Entry *`, matching the first parameter.
  - `Game_Action_Flags` values are passed for all flag/mask parameters (`Game_Action_Flags` is `uint8_t`).
  - `Process_Priority__u8` (`PROCESS_PRIORITY__0_MAXIMUM` = 0) matches the priority parameter.
  - `m_process__game_action__world__load_world` has the signature `void(Process*, Game*)`, which matches the `m_Process` typedef (`void (*m_Process)(Process *p_this_process, Game *p_game)`).
  - `Process_Flags__u8` values (`PROCESS_FLAG__IS_CRITICAL`, `0`) match the process flags parameters.
- **No undefined behavior:** No null pointer dereference occurs because the enum value `Game_Action_Kind__World__Load_World` is valid. No out-of-bounds array access occurs. No implicit conversions or truncation.
- **Validation:** The function does not validate `p_game_action_logic_table` for null, but this is the established convention across all registration functions in this codebase (e.g., `register_game_action__world__load_client`, `register_game_action__tcp_connect`). Validation is the caller's responsibility.

---

## Side Effects

Mutates the `Game_Action_Logic_Entry` at index `Game_Action_Kind__World__Load_World` within the `Game_Action_Logic_Table` pointed to by `p_game_action_logic_table`. No other side effects.
