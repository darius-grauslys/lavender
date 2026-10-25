# Client — Per-Player Multiplayer State and Action Management

**Sources:** `core/source/client.c` + `core/include/client.h`

## Surface Concerns

The client module manages **per-player state** in multiplayer contexts. Each connected player is a `Client` struct with two independent game action managers (inbound and outbound), a local spatial partitioning grid, and per-client input state. Layer: L2 (engine services). Called from `game.c` (pool management, game-action dispatch/receive/resolve handlers, broadcast) and the multiplayer layer (via the `receive_game_action` pipeline).

- **Client pool** — Managed by `game.c`: `allocate_client_pool_for__game()` sizes the pool to at most `MAX_QUANTITY_OF__TCP_SOCKETS` (default 1) clients, and `allocate_client_from__game()` adds remote clients by UUID; `MAX_QUANTITY_OF__CLIENTS` (4) is the hard cap. Client 0 (local player) is always at index 0.
- **Per-client action managers** — Each client owns two `Game_Action_Manager` instances (512 slots each): inbound for actions received from others, outbound for dispatched actions used in request/response linking. Actions are copied into these pools when the `WITH_PROCESS` flag is set, ensuring they survive the TCP receive callback.
- **Local space spatial partitioning** — Each client manages an 8×8×1 grid of local spaces for spatial partitioning. The center tracks the client's hitbox position; scrolling triggers local space transitions when the global center differs. Used by `broadcast_game_action` to determine reachability.
- **Save/load/create hooks** — The module defines process handlers for serialization (`m_process__serialize_client__default`) and deserialization (`m_process__deserialize_client__default`), installed by default in `initialize_game`. The `m_process__create_client` hook is game-installed (0 by default) and runs game-defined per-client setup. All operations are filesystem-wrapped processes. Clients are serialized as their AABB hitbox data only.
- **Client state flags** — Bitwise flags track: active (connected), loaded (world data loaded), saving (mid-save), failed_to_load, fresh (defined, unused). `set_client_as__active()` resets to fresh connection state. `set_client_as__failed_to_load()` clears all flags.
- **Per-client dispatch and receive** — `dispatch_game_action_for__client()` sanitizes, allocates outbound copies when needed, runs handlers, and sends over TCP (skipping self-send on server/client). `receive_game_action_for__client()` resolves responses against the outbound manager, allocates inbound copies for `WITH_PROCESS` actions, and runs inbound handlers inline.

## Public API Surface

### Key Types

**`Client`** — defined in `defines.h`. Key members:
- `Serialization_Header _serialization_header` — UUID identity (32-bit hash).
- `Game_Action_Manager game_action_manager__inbound` — received actions pool.
- `Game_Action_Manager game_action_manager__outbound` — dispatched actions pool.
- `Local_Space_Manager local_space_manager` — per-client spatial partitioning.
- `Input input_of__client` — per-client input state.
- `client_flags__u16` — status flags: `CLIENT_FLAG__IS_ACTIVE`, `CLIENT_FLAG__IS_LOADED`, `CLIENT_FLAG__IS_FAILED_TO_LOAD`, `CLIENT_FLAG__IS_SAVING`, `CLIENT_FLAG__IS_FRESH` (unused), `CLIENT_FLAGS__NONE`.

### Key Functions

- `void initialize_client(Client *p_client, Identifier__u32 uuid__u32, Global_Space_Vector__3i32 global_space_vector__3i32);`
- `bool dispatch_game_action_for__client(Client *p_client, Game *p_game, TCP_Socket_Manager *p_tcp_socket_manager, Game_Action *p_game_action);` — returns false on dispatch failure.
- `Process *teleport_client(Game *p_game, Client *p_client, Vector__3i32F4 position__3i32F4);` — returns a process or 0 on failure.
- `bool receive_game_action_for__client(Client *p_client, Game *p_game, Game_Action *p_game_action);` — returns false on failure or when the action resolves a pending response.
- `bool release_game_action_from__client(Client *p_client, Game_Action *p_game_action);` — returns false if action not found.
- `Game_Action *allocate_game_action_from__client(Client *p_client, Game_Action_Flags game_action_flags);` — declared, no core implementation.
- `void set_entity_of__client(Client *p_client, Entity *p_entity);` — declared, no core implementation.
- `void m_process__deserialize_client__default(Process *p_this_process, Game *p_game);`
- `void m_process__serialize_client__default(Process *p_this_process, Game *p_game);`
- `static inline void set_client_as__active(Client *p_client);` / `bool is_client__active(Client *p_client);`
- `static inline bool is_client__loaded(Client *p_client);` / `void set_client_as__loaded(Client *p_client);`
- `static inline bool is_client__saving(Client *p_client);` / `void set_client_as__saving(Client *p_client);`
- `static inline bool is_client__failed_to_load(Client *p_client);` / `void set_client_as__failed_to_load(Client *p_client);`

## Key Files Table

| File | Role |
|------|------|
| `core/source/client.c` | Client init, dispatch/receive/release, save/load processes, teleport |
| `core/include/client.h` | Dispatch/receive/release API, teleport, save/load process handlers, state inlines |
| `core/include/defines.h` | Client struct, client flag definitions |
| `core/source/game.c` | Client pool management, dispatch handler processes, broadcast |
| `core/include/game.h` | Client pool API, dispatch handlers, inline getters |
