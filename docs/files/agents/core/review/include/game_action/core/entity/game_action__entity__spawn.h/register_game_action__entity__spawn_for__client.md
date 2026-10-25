# register_game_action__entity__spawn_for__client

**File of origin:** `core/source/game_action/core/entity/game_action__entity__spawn.c`

## Semantic

Registers the `Game_Action_Logic_Entry` for `Game_Action_Kind__Entity__Spawn` on the client side, configuring it to handle inbound (server→client) entity spawn actions with a local process handler and no outbound processing.

## Pre-conditions

1. `p_game_action_logic_table` must be non-null and initialized (caller's responsibility — consistent with all other registration functions in the codebase).
2. `Game_Action_Kind__Entity__Spawn` must be a valid `Game_Action_Kind` enum value (it is; defined in `defines_weak.h`).
3. The `Game_Action_Logic_Table` must have been zero-initialized or otherwise prepared so that `get_p_game_action_logic_entry_by__game_action_kind` returns a valid, writable `Game_Action_Logic_Entry*`.

## Post-conditions

1. The `Game_Action_Logic_Entry` at index `Game_Action_Kind__Entity__Spawn` in the table is fully initialized with the following configuration:
   - **Outbound**: No flags (`GAME_ACTION_FLAGS__OUTBOUND_SANITIZE` = `0`), mask = `BIT_IS_ALLOCATED`, no outbound process handler (`0`), no outbound process flags (`0`).
   - **Inbound**: Flags = `BIT_IS_IN_OR__OUT_BOUND | BIT_IS_WITH_PROCESS | BIT_IS_PROCESSED_ON_INVOCATION_OR_RESPONSE | BIT_IS_LOCAL`, mask = `BIT_IS_ALLOCATED | BIT_IS_IN_OR__OUT_BOUND`.
   - **Process priority**: `PROCESS_PRIORITY__0_MAXIMUM`.
   - **Inbound process handler**: `m_process__game_action__entity__spawn__inbound_client`.
   - **Inbound process flags**: `PROCESS_FLAGS__NONE`.
2. When a client receives an entity spawn game action, the inbound sanitization will set `BIT_IS_LOCAL`, causing the dispatch/receive/resolve handlers in `game.c` to treat the action as local (processed locally, not forwarded over TCP).

## Correctness Verdict

**Correct**

## Semantic Alignment

The implementation fulfills the semantic intent of registering a client-side handler for inbound entity spawn actions.

The function correctly:
- Sets **no outbound process** (`0`), because the client does not initiate entity spawns — it only receives them from the server. This is consistent with the server registration (`register_game_action__entity__spawn_for__server`), which uses `initialize_game_action_logic_entry_as__broadcast__server` to set up the outbound (server→client broadcast) process and leaves the inbound process as `0`.
- Sets the **inbound process** to `m_process__game_action__entity__spawn__inbound_client`, which correctly handles received spawn actions by checking for corrupted local entity data, releasing stale entities, and dispatching a follow-up `game_action__entity__get` to fetch the entity data from the server.
- Sets `BIT_IS_WITH_PROCESS` and `BIT_IS_PROCESSED_ON_INVOCATION_OR_RESPONSE`, matching the `initialize_game_action_logic_entry_as__process__in` helper pattern — indicating the inbound action has an associated process that is dispatched immediately upon receipt.
- Sets `BIT_IS_LOCAL`, a deliberate addition beyond the `initialize_game_action_logic_entry_as__process__in` pattern. This ensures that once the client receives a spawn action, it is marked as local and will not be forwarded to other clients over TCP. This is semantically correct because entity spawns are server-authoritative — the client should process them locally and not relay them. This is consistent with the `m_game_action_handler__receive__multiplayer` and `m_game_action_handler__dispatch__multiplayer` functions in `game.c`, which route local actions through the singleplayer handlers.

**Comparison with other client registrations:**
- `register_game_action__hitbox_for__client` does NOT set `BIT_IS_LOCAL` (hitbox actions are client-initiated and may need to be forwarded).
- `register_game_action__input_for__client` does NOT set `BIT_IS_LOCAL` (input actions are client-initiated).
- `register_game_action__entity__spawn_for__client` correctly sets `BIT_IS_LOCAL` because spawn actions are server-initiated and should not be forwarded by the client.

## Implementation Correctness

- **Argument count**: The call passes exactly 10 arguments to `initialize_game_action_logic_entry`, which accepts 10 parameters. ✓
- **Type compatibility**: All argument types match the parameter types exactly:
  - Arg 1: `Game_Action_Logic_Entry *` (returned by `get_p_game_action_logic_entry_by__game_action_kind`) ✓
  - Arg 2: `Game_Action_Flags` (`GAME_ACTION_FLAGS__OUTBOUND_SANITIZE`) ✓
  - Arg 3: `Game_Action_Flags` (`GAME_ACTION_FLAG_MASK__OUTBOUND_SANITIZE`) ✓
  - Arg 4: `Game_Action_Flags` (bitwise OR of flags) ✓
  - Arg 5: `Game_Action_Flags` (`GAME_ACTION_FLAG_MASK__INBOUND_SANITIZE`) ✓
  - Arg 6: `Process_Priority__u8` (`PROCESS_PRIORITY__0_MAXIMUM`) ✓
  - Arg 7: `m_Process` (`0` / NULL) ✓
  - Arg 8: `Process_Flags__u8` (`0`) ✓
  - Arg 9: `m_Process` (`m_process__game_action__entity__spawn__inbound_client`) ✓
  - Arg 10: `Process_Flags__u8` (`PROCESS_FLAGS__NONE`) ✓
- **No implicit conversions or truncation**: All values are of the correct type. `0` is used as a null `m_Process` function pointer, which is valid in C. ✓
- **Undefined behavior**: No broken pointer arithmetic, no null dereference (the function delegates to `initialize_game_action_logic_entry` which dereferences the entry pointer — this is safe because `Game_Action_Kind__Entity__Spawn` is a valid enum value and `get_p_game_action_logic_entry_by__game_action_kind` performs bounds checking), no type punning, no out-of-bounds access. ✓
- **Validation**: The function does not perform null-checking on `p_game_action_logic_table`, which is consistent with all other registration functions in the codebase (e.g., `register_game_action__hitbox_for__client`, `register_game_action__input_for__client`). This is the caller's responsibility. ✓
- **Function signature**: `m_process__game_action__entity__spawn__inbound_client` has the signature `void(Process*, Game*)`, which matches the `m_Process` typedef exactly. ✓
- **No initialization (Lavender semantics)**: This function is not an "init"/"initialize" function in the Lavender sense. It is a registration function that configures a `Game_Action_Logic_Entry` with flags and process handlers. It does not perform resource acquisition (RAII) — it writes configuration values into an existing struct. ✓

## Side Effects

- **Mutates** the `Game_Action_Logic_Entry` stored at index `Game_Action_Kind__Entity__Spawn` within the `Game_Action_Logic_Table` pointed to by `p_game_action_logic_table`. All fields of the entry are set (no fields left uninitialized).
- No other side effects. Does not allocate memory, does not call other processes, does not modify any global state.
