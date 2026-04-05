# System Overview: Multiplayer System

## Purpose

The multiplayer system provides TCP-based networking for client-server
multiplayer sessions. It manages socket lifecycle, connection handshakes,
packet-based data transfer, session authentication, and per-client game
state isolation. The system is designed around a cooperative polling model
that integrates with the engine's process-based task scheduler, enabling
multiplayer I/O on single-core hardware without preemptive threading.

## Architecture

### Ownership Hierarchy

    Game
    ├── Session_Token                         (local player authentication)
    │   ├── Identifier__u64 player_uuid
    │   └── Identifier__u64 session_token
    │
    ├── Game_Action_Logic_Table               (dispatch rules for all game actions)
    │   └── Game_Action_Logic_Entry[Game_Action_Kind__Unknown]
    │       ├── m_Process inbound handler
    │       ├── m_Process outbound handler
    │       ├── Game_Action_Flags (inbound/outbound + masks)
    │       └── Process_Priority__u8
    │
    ├── TCP_Socket_Manager *pM_tcp_socket_manager
    │   ├── TCP_Socket[MAX_QUANTITY_OF__TCP_SOCKETS]  (connection pool)
    │   │   ├── Serialization_Header (UUID-based lookup)
    │   │   ├── TCP_Packet queue[]                    (circular receive buffer)
    │   │   ├── IPv4_Address                          (remote endpoint)
    │   │   ├── PLATFORM_TCP_Socket*                  (platform handle)
    │   │   ├── TCP_Socket_State                      (connection state machine)
    │   │   └── TCP_Socket_Flags__u8                  (manually driven, etc.)
    │   ├── PLATFORM_TCP_Context*                     (platform networking context)
    │   ├── m_Poll_TCP_Socket_Manager                 (client or server strategy)
    │   └── PLATFORM_TCP_Socket* pending_connection   (server: awaiting accept/reject)
    │
    ├── Client *pM_clients                            (per-client state pool)
    │   ├── Game_Action_Manager inbound               (received actions from network)
    │   ├── Game_Action_Manager outbound              (actions to send over network)
    │   ├── Local_Space_Manager                       (client's loaded chunk region)
    │   ├── Input                                     (client's input state)
    │   └── Client_Flags__u16                         (active, loaded, saving, etc.)
    │
    ├── m_Game_Action_Handler dispatch                (outbound action routing)
    ├── m_Game_Action_Handler receive                 (inbound action routing)
    ├── m_Game_Action_Handler resolve                 (action resolution)
    │
    └── Game_Flags__u32
        └── GAME_FLAG__IS_SERVER_OR__CLIENT           (role discriminator)

### Why This Split?

The `TCP_Socket_Manager` is owned by `Game` (not `World`) because
networking persists across world loads/unloads. A player's connection
must survive world transitions. Similarly, `Client` state is owned by
`Game` because client sessions are independent of which world is loaded.

The `Game_Action_Logic_Table` is also at the `Game` level because game
action dispatch rules are global — they define how every kind of game
action is processed regardless of world state.

## Roles: Server and Client

The multiplayer system supports two roles, determined by
`GAME_FLAG__IS_SERVER_OR__CLIENT` in `Game.game_flags__u32`:

### Server (Host)

- Opens a listening socket via `open_server_socket_on__tcp_socket_manager__ipv4`.
- Polls for inbound connections via `poll_tcp_socket_manager_for__pending_connections`.
- Accepts or rejects connections via `accept_pending_connection` / `reject_pending_connection`.
- Manages multiple `Client` instances, one per connected player.
- Uses `m_poll_tcp_socket_manager_as__server__default` as the polling strategy.
- Is the authoritative source for world state.

### Client

- Opens an outbound connection via `open_socket_on__tcp_socket_manager__ipv4`.
- Polls for connection completion via `poll_tcp_socket_for__connection`.
- Maintains a single connection to the server.
- Uses `m_poll_tcp_socket_manager_as__client__default` as the polling strategy.
- Receives world state updates from the server.

### Single-Player

When `Game.max_quantity_of__clients == 0`, the game operates in
single-player mode. The `TCP_Socket_Manager` is not used, and the
game reads input directly from `Game.input` instead of per-client
`Client.input_of__client`.

## Connection Handshake

### Client-Initiated Connection

    [Client]                                    [Server]
       |                                           |
       |  Game_Action_Kind__TCP_Connect__Begin      |
       |  (IPv4_Address, Session_Token)             |
       | ----------------------------------------> |
       |                                           |
       |           PLATFORM_tcp_connect(...)        |
       |           poll_tcp_socket_for__connection() |
       |                                           |
       |                    PLATFORM_tcp_poll_accept(...)
       |                    poll_tcp_socket_manager_for__pending_connections(...)
       |                                           |
       |  Game_Action_Kind__TCP_Connect__Accept     |
       |  OR Game_Action_Kind__TCP_Connect__Reject  |
       | <---------------------------------------- |
       |                                           |

### Session Token Validation

During the handshake, the client sends its `Session_Token` containing:

- `player_uuid` (64-bit): The player's account identifier.
- `session_token` (64-bit): The session authentication token.

The server validates the session token and compresses the 64-bit
`player_uuid` to a 32-bit entity UUID via XOR-folding
(`get_uuid_u32_of__session_token_player_uuid_u64`). The compressed
UUID is branded with `Lavender_Type__Player` for use in the entity
system.

**Collision risk:** The 64-to-32-bit compression is lossy. The server
must detect and handle UUID collisions during player entity allocation.

### Socket State Transitions During Handshake

    TCP_Socket_State__None
        → (initialize_tcp_socket)
    TCP_Socket_State__Connecting
        → (poll_tcp_socket_for__connection succeeds)
    TCP_Socket_State__Connected
        → (session token sent/received)
    TCP_Socket_State__Authenticating
        → (session token validated)
    TCP_Socket_State__Authenticated

If connection fails at any point, the socket transitions to
`TCP_Socket_State__Disconnected`.

## Game Action Transport

### Game Action as Network Message

All multiplayer communication is expressed as `Game_Action` structs.
The `Game_Action` union overlays with `TCP_Packet` for zero-copy
transmission via the `TCP_DELIVERY` macro:

    TCP_DELIVERY(Game_Action, game_action);
    // Equivalent to:
    // union { Game_Action game_action; TCP_Packet tcp_packet; };

### Multiplayer Game Action Kinds

| Kind | Direction | Description |
|------|-----------|-------------|
| `Game_Action_Kind__TCP_Connect__Begin` | Client → Server | Initiates connection with IPv4 address and session token. |
| `Game_Action_Kind__TCP_Connect` | Bidirectional | Connection in progress (carries session token u64). |
| `Game_Action_Kind__TCP_Connect__Accept` | Server → Client | Connection accepted. |
| `Game_Action_Kind__TCP_Connect__Reject` | Server → Client | Connection rejected. |
| `Game_Action_Kind__TCP_Disconnect` | Bidirectional | Connection terminated. |
| `Game_Action_Kind__TCP_Delivery` | Bidirectional | Generic data payload delivery (fragmented). |

### Inbound / Outbound Flow

Each `Client` has two `Game_Action_Manager` instances:

- **Inbound:** Actions received from the network, awaiting processing.
- **Outbound:** Actions generated locally, awaiting transmission.

The flow for a received packet:

    PLATFORM_tcp_recieve(...)
        → receive_bytes_over__tcp_socket(...)
        → enqueue in TCP_Socket.queue_of__tcp_packet
        → m_poll_tcp_socket_manager dequeues packet
        → interpret as Game_Action
        → enqueue in Client.game_action_manager__inbound
        → m_game_action_handler__receive processes action

The flow for a sent action:

    Game logic generates Game_Action
        → enqueue in Client.game_action_manager__outbound
        → m_game_action_handler__dispatch routes action
        → send_bytes_over__tcp_socket(...)
        → PLATFORM_tcp_send(...)

### Game Action Flag Sanitization

The `Game_Action_Logic_Entry` includes inbound and outbound flag masks
that sanitize game action flags during dispatch:

- `game_action_flags__inbound_mask` / `game_action_flags__inbound`:
  Applied to received actions to prevent clients from spoofing flags.
- `game_action_flags__outbound_mask` / `game_action_flags__outbound`:
  Applied to sent actions to ensure correct flag state.

The sanitization constants are:

    GAME_ACTION_FLAG_MASK__INBOUND_SANITIZE =
        IS_ALLOCATED | IS_IN_OR__OUT_BOUND
    GAME_ACTION_FLAGS__INBOUND_SANITIZE =
        IS_IN_OR__OUT_BOUND

    GAME_ACTION_FLAG_MASK__OUTBOUND_SANITIZE =
        IS_ALLOCATED
    GAME_ACTION_FLAGS__OUTBOUND_SANITIZE =
        NONE

### Game Action Logic Table

The `Game_Action_Logic_Table` maps each `Game_Action_Kind` to:

- Inbound and outbound process handlers (`m_Process`).
- Flag masks for sanitization.
- Process priority and flags for scheduling.

This table is the central dispatch configuration for all game actions,
both local and networked.

### TCP Delivery Fragmentation

Large payloads that exceed `TCP_Packet` size are fragmented using the
`TCP_DELIVERY` system:

- `GA_KIND__TCP_DELIVERY__PAYLOAD_SIZE_IN__BYTES`: Maximum payload per
  packet, computed as `sizeof(TCP_Packet) - sizeof(_Game_Action_Header) - sizeof(uint64_t)`.
- `TCP_PAYLOAD_BITMAP__QUANTITY_OF__PAYLOADS(type)`: Number of packets
  needed to transmit a given type.
- `ga_kind__tcp_delivery__packet_index`: Index of this fragment within
  the sequence.
- Bitmap tracking (`pM_packet_bitmap` on `Serialization_Request`)
  tracks which fragments have arrived.

**Critical constraint:** `MAX_SIZE_OF__TCP_PACKET` must be a power of 2
(`BIT(n)`). The delivery system relies on `MASK(n)` logic derived from
the size. Non-power-of-2 values will cause delivery failures for all
TCP-transported data (global spaces, inventories, entities, etc.).

## Socket Lifecycle

### TCP_Socket States

    [Deallocated] → initialize_tcp_socket → [None]
                                               ↓
                                     bind_tcp_socket
                                               ↓
                                          [Connecting]
                                               ↓
                                 poll_tcp_socket_for__connection
                                       ↓              ↓
                                 [Connected]     [Disconnected]
                                       ↓              ↓
                              [Authenticating]   unbind + dealloc
                                       ↓
                              [Authenticated]
                                       ↓
                                 send/receive
                                       ↓
                                 close_socket
                                       ↓
                                 [Deallocated]

### Manually Driven Sockets

Sockets with `TCP_SOCKET_FLAG__IS_MANUALLY_DRIVEN` set are skipped
during the automatic poll loop. This is used for:

- Server listening sockets (driven by the server polling strategy).
- Sockets in mid-handshake (driven by a dedicated `Process`).

The flag is set via `set_tcp_socket_as__manually_driven` and cleared
via `set_tcp_socket_as__automatically_driven`.

### UUID-Based Lookup

Sockets are stored in a contiguous pool and looked up by UUID via
`dehash_identitier_u32_in__contigious_array`, providing O(1)
average-case lookup:

    TCP_Socket *p_socket =
        get_p_tcp_socket_for__this_uuid(p_manager, uuid);

## Client Management

### Client Pool

The `Game` maintains a pool of `Client` instances (`pM_clients`) with
a pointer array (`pM_ptr_array_of__clients`) for indexed access. The
pool size is determined by `max_quantity_of__clients`. The
`index_to__next_client_in__pool` tracks the next available slot.

### Client Flags

| Flag | Bit | Description |
|------|-----|-------------|
| `CLIENT_FLAG__IS_ACTIVE` | 0 | Client slot is in use. |
| `CLIENT_FLAG__IS_LOADED` | 1 | Client's world data has been loaded. |
| `CLIENT_FLAG__IS_FAILED_TO_LOAD` | 2 | Client load failed. |
| `CLIENT_FLAG__IS_SAVING` | 3 | Client data is being serialized. |
| `CLIENT_FLAG__IS_FRESH` | 4 | Client is newly connected, not yet fully initialized. |

### Per-Client World View

Each `Client` owns a `Local_Space_Manager` that tracks which chunks
are loaded for that client. This enables the server to send only
relevant world data to each client based on their position.

The `Local_Space_Manager` dimensions are configured by:

- `LOCAL_SPACE_MANAGER__WIDTH` (default: 8)
- `LOCAL_SPACE_MANAGER__HEIGHT` (default: 8)
- `LOCAL_SPACE_MANAGER__DEPTH` (default: 1)

These must be at least as large as the rendering dimensions
(`GFX_CONTEXT__RENDERING_WIDTH__IN_CHUNKS`, etc.).

### Client Serialization

The `Game` provides process handlers for client persistence:

- `m_process__serialize_client`: Saves client state.
- `m_process__deserialize_client`: Loads client state.
- `m_process__create_client`: Creates a new client from scratch.

These are `m_Process` callbacks integrated with the process scheduler.

## Platform Integration

The multiplayer system delegates all socket I/O to platform functions:

| Platform Function | Purpose |
|-------------------|---------|
| `PLATFORM_tcp_begin` | Initialize platform TCP context. Returns `PLATFORM_TCP_Context*`. |
| `PLATFORM_tcp_end` | Shut down platform TCP context. |
| `PLATFORM_tcp_connect` | Initiate outbound connection. Returns `PLATFORM_TCP_Socket*`. |
| `PLATFORM_tcp_poll_connect` | Poll connection progress. Returns `TCP_Socket_State`. |
| `PLATFORM_tcp_server` | Create listening socket on port. Returns `PLATFORM_TCP_Socket*`. |
| `PLATFORM_tcp_poll_accept` | Check for inbound connections. Returns `PLATFORM_TCP_Socket*`. |
| `PLATFORM_tcp_close_socket` | Close a platform socket. Returns `bool` (true on error). |
| `PLATFORM_tcp_send` | Send bytes. Returns `i32` (bytes sent, -1 on error). |
| `PLATFORM_tcp_recieve` | Receive bytes. Returns `i32` (bytes received, or `TCP_ERROR__XXX`). |

All platform functions operate on opaque `PLATFORM_TCP_Context` and
`PLATFORM_TCP_Socket` types, allowing the core multiplayer logic to
remain platform-independent.

## Capacity Constraints

| Resource | Pool Size | Determined By |
|----------|-----------|---------------|
| `TCP_Socket` | `MAX_QUANTITY_OF__TCP_SOCKETS` | Platform default (1). |
| `TCP_Packet` (per socket) | `MAX_QUANTITY_OF__TCP_PACKETS_PER__SOCKET` | Platform default (`BIT(8)` = 256). |
| `TCP_Packet` byte size | `MAX_SIZE_OF__TCP_PACKET` | Platform default (`BIT(9)` = 512). Must be power of 2. |
| `Client` | `max_quantity_of__clients` | Set at game initialization. Upper bound: `MAX_QUANTITY_OF__CLIENTS` (4). |
| `Game_Action` (per client) | `MAX_QUANTITY_OF__GAME_ACTIONS` | Per inbound/outbound manager (512). |
| `Global_Space` | `QUANTITY_OF__GLOBAL_SPACE` | `VOLUME_OF__LOCAL_SPACE_MANAGER * MAX_QUANTITY_OF__CLIENTS`. |

## Relationship Summary

| Concern | Managed By |
|---------|------------|
| Socket pool and connection lifecycle | `TCP_Socket_Manager` |
| Per-socket packet queue and I/O | `TCP_Socket` |
| Platform socket operations | `PLATFORM_TCP_*` functions |
| Client/server polling strategy | `m_Poll_TCP_Socket_Manager` callback |
| Per-client game action queues | `Client` (via `Game_Action_Manager`) |
| Game action dispatch and routing | `Game_Action_Logic_Table` + `m_Game_Action_Handler` |
| Game action flag sanitization | `Game_Action_Logic_Entry` flag masks |
| Session authentication | `Session_Token` |
| UUID compression (64→32 bit) | `get_uuid_u32_of__session_token_player_uuid_u64` |
| Multiplayer role determination | `Game.game_flags__u32` + `is_host` / `is_in_multiplayer_game` |
| Address parsing | `IPv4_Address` + `populate_ipv4_address` |
| Client persistence | `m_process__serialize_client` / `m_process__deserialize_client` / `m_process__create_client` |

The `TCP_Socket.Serialization_Header.uuid` is the bridge between the
socket pool and the rest of the engine: it allows game actions, clients,
and processes to reference specific connections by UUID without holding
direct pointers to pool-managed sockets.
