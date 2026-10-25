# register_game_actions__offline

**File of origin:** `core/source/game_action/implemented/game_action_registrar.c`

## Semantic

Registers all game action kinds required for offline (single-player) mode into the provided `Game_Action_Logic_Table`. Each call delegates to a per-action-kind registration function that initializes the corresponding `Game_Action_Logic_Entry` slot in the table's `game_action_logic_entries` array.

## Pre-conditions

1. `p_game_action_logic_table` must be a valid, non-null pointer to a `Game_Action_Logic_Table`. The function dereferences it without a null check (consistent with the codebase convention—validation is the caller's responsibility).
2. `p_game_action_logic_table` should have been initialized via `initialize_game_action_logic_table()` (which memsets the struct to zero) prior to calling this function, so that entries start in a clean state before registration overwrites specific slots.

## Post-conditions

1. The `game_action_logic_entries` array of `*p_game_action_logic_table` has its slots for the following `Game_Action_Kind` values initialized with appropriate process handlers, flags, priorities, and masks:
   - `Game_Action_Kind__Global_Space__Store`
   - `Game_Action_Kind__Global_Space__Resolve`
   - `Game_Action_Kind__Global_Space__Request`
   - `Game_Action_Kind__World__Load_Client`
   - `Game_Action_Kind__World__Load_World`
   - `Game_Action_Kind__Hitbox` (via `register_game_action__hitbox_for__offline`, which delegates to the server variant)
   - Input actions are intentionally not registered (via `register_game_action__input_for__offline`, which is a no-op)
2. All other entries in the table remain in their prior state (zeroed if the table was properly initialized beforehand).
3. The function returns `void`.

## Correctness Verdict

**Correct**

## Semantic Alignment

The implementation faithfully fulfills its semantic intent: registering the set of game actions appropriate for offline mode. The function correctly delegates to each per-kind registration function without any logic errors.

Notable observations:
- `register_game_action__input_for__offline` is a no-op (documented in its header as "not needed as input is driven locally"). This is semantically correct—offline mode does not relay inputs over the network.
- `register_game_action__hitbox_for__offline` delegates to `register_game_action__hitbox_for__server`, which is semantically correct since offline mode behaves like a server for hitbox processing.
- `register_game_action__global_space__resolve` is shared across offline, client, and server modes, which is appropriate since resolution logic is identical in all modes.
- The `debug_warning` call within the `GEN-OFFLINE-BEGIN` / `GEN-OFFLINE-END` markers is a placeholder indicating auto-generated code; it is a side effect but does not affect correctness.

## Implementation Correctness

- **Type compatibility:** The parameter `Game_Action_Logic_Table *p_game_action_logic_table` matches the expected type in every callee function. No implicit conversions or truncation.
- **Undefined behavior:** No null dereference, no out-of-bounds array access, no type punning, no broken pointer arithmetic. The `get_p_game_action_logic_entry_by__game_action_kind` inline helper performs a bounds check (`the_kind_of__game_action >= Game_Action_Kind__Unknown`) before indexing into the array, and all registered `Game_Action_Kind` values are valid enum members below `Game_Action_Kind__Unknown`.
- **Validation:** No null check on `p_game_action_logic_table` is performed. This is consistent with the codebase convention (all other `register_game_action__*` functions follow the same pattern), placing the responsibility on the caller.

## Side Effects

1. **Mutation of `*p_game_action_logic_table`:** The function writes to specific slots in the `game_action_logic_entries` array of the table, initializing `Game_Action_Logic_Entry` structs with process handlers, flags, priorities, and masks for each registered game action kind.
2. **Debug output:** The `debug_warning("register_game_actions__offline, impl.")` call produces a warning-level log message (side effect of I/O).
