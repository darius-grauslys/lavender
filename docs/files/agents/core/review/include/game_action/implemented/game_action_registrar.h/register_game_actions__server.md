# register_game_actions__server

**File of origin:** `core/source/game_action/implemented/game_action_registrar.c`

## Semantic

Registers all server-relevant game action logic entries into the provided `Game_Action_Logic_Table` by delegating to individual per-action registration functions. Each call invokes `initialize_game_action_logic_entry` to populate the corresponding entry with its inbound/outbound process handlers, flags, masks, and process priority.

## Pre-conditions

1. `p_game_action_logic_table` must be a valid, non-null pointer to a `Game_Action_Logic_Table`.
2. The `Game_Action_Logic_Table` should have been previously zero-initialized (e.g., via `initialize_game_action_logic_table`) so that unregistered entries default to zeroed/empty state.
3. The `Game_Action_Logic_Entry` slots for each registered `Game_Action_Kind` must be within bounds of the `game_action_logic_entries` array (indexed by `Game_Action_Kind` enum values).

## Post-conditions

1. After the function returns, the `Game_Action_Logic_Table` will have all server-relevant `Game_Action_Logic_Entry` slots fully initialized with their respective inbound/outbound process handlers, game action flags, flag masks, process flags, and process priority.
2. Each registered entry's fields are all assigned by `initialize_game_action_logic_entry` — no struct member is left unassigned.
3. Entries for game action kinds not registered by this function remain in their prior (zeroed) state.

## Correctness Verdict

**Correct**

## Semantic Alignment

The function fulfills its semantic intent: it registers the complete set of game actions required for a server context. The registrations include:

- **TCP networking**: `tcp_connect`, `tcp_connect__begin`, `tcp_connect__accept`, `tcp_connect__reject`, `tcp_delivery` — all shared with the client registration, as the server must handle connection establishment and packet delivery.
- **Bad request handling**: `bad_request` — shared with the client, as the server must handle malformed requests.
- **Global space management**: `global_space__store` (server-specific, as the server persists world data), `global_space__resolve` (shared with client and offline), `global_space__request_for__server` (server-specific request handling).
- **World loading**: `world__load_client` and `world__load_world` — shared with offline, as the server loads clients and world data.
- **Hitbox and input**: `hitbox_for__server` and `input_for__server` — server-specific handlers.

This set is distinct from the offline and client registrations, correctly reflecting the server's unique responsibilities (storing global spaces, handling server-specific requests, loading clients/worlds, and server-side hitbox/input processing). The `debug_warning` call within the `GEN-SERVER-BEGIN`/`GEN-SERVER-END` code-generation marker block is consistent with the pattern used in `register_game_actions__offline` and `register_game_actions__client`.

## Implementation Correctness

- **Type compatibility**: The parameter `Game_Action_Logic_Table *p_game_action_logic_table` is passed directly to each individual registration function, all of which expect `Game_Action_Logic_Table *`. Types match exactly with no implicit conversions or truncation.
- **Undefined behavior**: No broken pointer arithmetic, no null dereference, no type punning, and no out-of-bounds access. The `get_p_game_action_logic_entry_by__game_action_kind` inline helper performs a bounds check (`the_kind_of__game_action >= Game_Action_Kind__Unknown`) before indexing into the array, preventing out-of-bounds access.
- **Validation**: No null check is performed on `p_game_action_logic_table`. This is consistent with the codebase pattern — all registration functions (`register_game_action__bad_request`, `register_game_action__tcp_connect`, etc.) and the sibling functions `register_game_actions__offline` and `register_game_actions__client` likewise do not validate the pointer. Validation is the caller's responsibility, and the table is expected to be valid at this call site.
- **Struct initialization completeness**: `initialize_game_action_logic_entry` assigns all 9 fields of `Game_Action_Logic_Entry` (`m_process_of__game_action__outbound`, `m_process_of__game_action__inbound`, `game_action_flags__outbound`, `game_action_flags__outbound_mask`, `game_action_flags__inbound`, `game_action_flags__inbound_mask`, `process_flags_of__game_action__outbound`, `process_flags_of__game_action__inbound`, `process_priority__u8`). No member is omitted and no reordering occurs.

## Side Effects

- **Mutates** the `Game_Action_Logic_Table` pointed to by `p_game_action_logic_table` by initializing its `game_action_logic_entries` array slots via calls to `initialize_game_action_logic_entry` through each individual registration function.
- Calls `debug_warning("register_game_actions__server, impl.")` as a code-generation marker within the `GEN-SERVER-BEGIN`/`GEN-SERVER-END` block. This is a deliberate placeholder consistent with the pattern used in the offline and client variants.
