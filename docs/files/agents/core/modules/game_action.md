# Game Action — The Universal State-Mutation Protocol

**Sources:** `core/source/game_action/` + `core/include/game_action/` + `core/include/defines.h`

## Surface Concerns

The game action system is the **only** way the engine's world state changes — every mutation (input, hitbox movement, entity spawning, global space store, world loading, TCP delivery) is expressed as a `Game_Action`. Layer: L2 (engine services). Invoked from `game.c`, `client.c`, and the multiplayer layer.

- **Fixed-capacity action pool** — 512-entry pool per `Game_Action_Manager`, each slot uniquely identifiable by UUID. Allocate, copy, release.
- **Logic table dispatch** — maps action kinds to per-direction (inbound/outbound) handler functions. Dispatching applies sanitization flags, wraps in a Process when configured, and invokes the appropriate handler.
- **Request/response linking** — `uuid_of__game_action__responding_to` ties actions across cycles: TCP Delivery writes payload into the waiting process's `Serialization_Request`; Bad Request sets `BAD_REQUEST` on the original outbound action.
- **TCP delivery with fragmentation** — actions sent over TCP in 512-byte packets. `TCP_Delivery` actions carry the target client UUID and the UUID of the waiting process.
- **Broadcast** — actions flagged `BROADCASTED` are sent to all connected clients whose loaded local space contains the broadcast point, plus the local client.
- **Flag sanitization** — per-kind flag masks (`INBOUND_SANITIZE` / `OUTBOUND_SANITIZE`) strip and set bits on dispatch/receive so actions carry only direction-relevant flags.
- **Three registration modes** — `register_game_actions__offline()`, `__client()`, `__server()` install different subsets of action kinds with their sanitization flags, priorities, and handler pointers into the global logic table.
- **Per-client inbound/outbound pools** — each `Client` owns two `Game_Action_Manager` instances (inbound + outbound), giving 1024 concurrent actions per client.

## Public API Surface

### Key Types

**`Game_Action`** — defined in `defines.h`. Members: `Serialization_Header _serialiation_header`, `uuid_of__client__u32` (origin + TCP target), `uuid_of__game_action__responding_to`, `vector_3i32F4__broadcast_point`, `the_kind_of_game_action__this_action_is` (enum `Game_Action_Kind`), `game_action_flags` (8 bit flags), and injected payload union `_ga_payload_union`.

**`Game_Action_Manager`** — defined in `defines.h`. Members: `Game_Action game_actions[MAX_QUANTITY_OF__GAME_ACTIONS]` (512-entry pool), `Repeatable_Psuedo_Random repeatable_pseudo_random` (seeded PRNG for UUID generation).

**`Game_Action_Logic_Entry`** — defined in `defines.h`. Members: inbound/outbound handler function pointers, inbound/outbound flag masks, process creation flags, and process priority.

**`Game_Action_Logic_Table`** — defined in `defines.h`. Members: indexed array of `Game_Action_Logic_Entry`, one per `Game_Action_Kind`.

### Key Functions

From `game_action.h`:
- `void initialize_game_action(Game_Action *p_game_action);` — zero-init + header setup.
- `static inline void set_the_kind_of__game_action(Game_Action *p_game_action, Game_Action_Kind the_kind_of__game_action);` / `Game_Action_Kind get_kind_of__game_action(Game_Action *p_game_action);`
- `static inline bool is_game_action__allocated(Game_Action *p_game_action);` / `void set_game_action_as__allocated(Game_Action *p_game_action);` / `void set_game_action_as__deallocated(Game_Action *p_game_action);`
- `static inline bool is_game_action__inbound(Game_Action *p_game_action);` / `void set_game_action_as__inbound(Game_Action *p_game_action);` / `void set_game_action_as__outbound(Game_Action *p_game_action);`
- `static inline bool is_game_action__with_process(Game_Action *p_game_action);`
- `static inline bool is_game_action__processed_on__invocation_or__respose(Game_Action *p_game_action);`
- `static inline bool is_game_action__responding_to_another__game_action(Game_Action *p_game_action);`
- `static inline bool is_game_action__local(Game_Action *p_game_action);` / `void set_game_action_as__local(Game_Action *p_game_action);`
- `static inline bool is_game_action__broadcasted(Game_Action *p_game_action);` / `void set_game_action_as__broadcasted(Game_Action *p_game_action);`
- `static inline bool is_game_action__bad_request(Game_Action *p_game_action);` / `void set_game_action_as__bad_request(Game_Action *p_game_action);`
- `#define GA_UUID_SOURCE(game_action)` — returns `game_action->uuid_of__client__u32`.

From `game_action_manager.h`:
- `void initialize_game_action_manager(Game_Action_Manager *p_game_action_manager);`
- `static inline Game_Action *allocate_game_action_from__game_action_manager(Game_Action_Manager *p_game_action_manager);` — random-UUID allocation; returns NULL on failure.
- `Game_Action *allocate_game_action_with__this_uuid_from__game_action_manager(Game_Action_Manager *p_game_action_manager, Identifier__u32 uuid);` — returns action or NULL.
- `static inline Game_Action *allocate_as__copy_of__game_action_from__game_action_manager(Game_Action_Manager *p_game_action_manager, Game_Action *p_game_action);`
- `Game_Action *allocate_as__copy_of__game_action_with__this_uuid_from__manager(Game_Action_Manager *p_game_action_manager, Game_Action *p_game_action_to__copy, Identifier__u32 uuid);` — returns copy or NULL.
- `bool release_game_action_from__game_action_manager(Game_Action_Manager *p_game_action_manager, Game_Action *p_game_action);`
- `Game_Action *get_p_game_action_by__uuid_from__game_action_manager(Game_Action_Manager *p_game_action_manager, Identifier__u32 uuid);`

From `game_action_logic_table.h`:
- `void initialize_game_action_logic_table(Game_Action_Logic_Table *p_game_action_logic_table);`
- `Process *dispatch_game_action_process(Process_Manager *p_process_manager, Game_Action *p_game_action, m_Process m_process__game_action, Process_Priority__u8 process_priority__u8, Process_Flags__u8 process_flags__u8);` — returns process or 0 (no handler / allocation failure).
- `Process *dispatch_game_action_process__outbound(Game_Action_Logic_Table *, Process_Manager *, Game_Action *);` — returns process or 0.
- `Process *dispatch_game_action_process__inbound(Game_Action_Logic_Table *, Process_Manager *, Game_Action *);` — returns process or 0.
- `m_Process get_m_process__outbound_for__this_game_action_kind(Game_Action_Logic_Table *, Game_Action_Kind);`
- `m_Process get_m_process__inbound_for__this_game_action_kind(Game_Action_Logic_Table *, Game_Action_Kind);`

From `game_action_logic_entry.h`:
- `void initialize_game_action_logic_entry(Game_Action_Logic_Entry *p_entry, Game_Action_Flags flags__outbound, Game_Action_Flags flags__outbound_mask, Game_Action_Flags flags__inbound, Game_Action_Flags flags__inbound_mask, Process_Priority__u8, m_Process m_process__outbound, Process_Flags__u8 process_flags__outbound, m_Process m_process__inbound, Process_Flags__u8 process_flags__inbound);`
- `void santize_game_action__inbound(Game_Action_Logic_Entry *, Game_Action *);` / `void santize_game_action__outbound(Game_Action_Logic_Entry *, Game_Action *);` — load-bearing typo `santize`. Masks out then sets the direction's flags.
- `static inline void initialize_game_action_logic_entry_as__process__out_and_in / __process__out / __process__in / __react__out / __react__in / __message / __broadcast__server / __message_response(...);` — registration convenience variants presetting the sanitization flags.

## Key Files Table

| File | Role |
|------|------|
| `core/source/game_action/game_action.c` | Zero-init + header setup |
| `core/source/game_action/game_action_manager.c` | Pool allocation/release, UUID-based lookup |
| `core/source/game_action/game_action_logic_table.c` | Logic table init, dispatch by kind |
| `core/source/game_action/game_action_logic_entry.c` | Logic entry init, sanitization |
| `core/source/game_action/implemented/game_action_registrar.c` | Three registration functions (offline/client/server) |
| `core/include/game_action/game_action.h` | Game_Action type, flags, inline utilities |
| `core/include/game_action/game_action_manager.h` | Pool API |
| `core/include/game_action/game_action_logic_table.h` | Logic table API, dispatch functions |
| `core/include/game_action/game_action_logic_entry.h` | Logic entry init helpers |
| `core/include/defines.h` | Game_Action, Manager, Logic_Entry, Logic_Table structs |
