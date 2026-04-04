# System Overview: Game Action Dispatch and Processing

## Purpose

The game action system is the engine's primary command/event mechanism.
Whenever a state modifying interaction occurs, the implementation of that 
exchange must be implemented as a game action if that state modification is
observable by game clients. An example where a state modification is to be
implemented as a game action is when a component of an entity is updated. 
A counter example of this is when the component of a ui element is modified
on a client's local game engine instance.

All significant state mutations — entity spawning, hitbox updates, chunk
loading, input relay, TCP handshake steps — are expressed as `Game_Action`
instances that flow through a centralized dispatch pipeline. This pipeline
supports three runtime modes (offline, client, server) and provides
flag-based sanitization, process-based asynchronous execution, and
multi-packet TCP delivery for large payloads.

## Architecture

### Data Hierarchy

    Game
    +-- Game_Action_Logic_Table
    |   +-- Game_Action_Logic_Entry[0..Game_Action_Kind__Unknown-1]
    |       +-- m_Process  m_process_of__game_action__outbound
    |       +-- m_Process  m_process_of__game_action__inbound
    |       +-- Game_Action_Flags  (sanitization flags + masks)
    |       +-- Process_Flags__u8  (outbound + inbound)
    |       +-- Process_Priority__u8
    |
    +-- Process_Manager
    |   +-- Process[0..N]
    |       +-- void *p_process_data  --> Game_Action*
    |
    +-- Client[0..M]
        +-- Game_Action_Manager (inbound)
        |   +-- Game_Action[0..MAX_QUANTITY_OF__GAME_ACTIONS-1]
        +-- Game_Action_Manager (outbound)
            +-- Game_Action[0..MAX_QUANTITY_OF__GAME_ACTIONS-1]

### Key Types

| Type | Role |
|------|------|
| `Game_Action` | Tagged union carrying a header (UUID, client UUID, flags, kind) and a kind-specific payload. Sized to fit within a `TCP_Packet`. |
| `Game_Action_Kind` | Enum discriminator selecting the active payload union member. |
| `Game_Action_Flags` | 8-bit flags controlling allocation, direction (inbound/outbound), process attachment, locality, broadcast, and error state. |
| `Game_Action_Logic_Table` | Array of `Game_Action_Logic_Entry` indexed by `Game_Action_Kind`. Central dispatch table. |
| `Game_Action_Logic_Entry` | Per-kind configuration: inbound/outbound process handlers, sanitization flags and masks, process priority and flags. |
| `Game_Action_Manager` | UUID-hashed pool of `Game_Action` slots. Each `Client` owns two: inbound and outbound. |
| `Game_Action_Registrar` | Implemented hook that populates the logic table for offline, client, or server mode. |
| `Process` | Asynchronous execution unit. When a game action has `IS_WITH_PROCESS`, a `Process` is allocated with the game action as `p_process_data`. |

### Limits

| Macro | Default | Description |
|-------|---------|-------------|
| `MAX_QUANTITY_OF__GAME_ACTIONS` | 512 | Maximum game actions per `Game_Action_Manager`. |
| `Game_Action_Kind__Unknown` | (enum bound) | Array size for the logic table. |

## Dispatch Pipeline

### Overview

    1. Create Game_Action on stack
    2. initialize_game_action(...)
    3. Kind-specific initializer (e.g. initialize_game_action_for__hitbox)
    4. dispatch_game_action(p_game, client_uuid, &ga)
       or dispatch_game_action_to__server(p_game, &ga)
    5. Game.m_game_action_handler__dispatch is invoked
    6. Logic table lookup by Game_Action_Kind
    7. Sanitize flags (outbound)
    8. If IS_WITH_PROCESS: allocate Process via Process_Manager
    9. Process runs m_process handler with Game_Action as p_process_data

### Detailed Steps

#### Step 1–3: Creation and Initialization

A game action is created on the stack and initialized in two phases:

    Game_Action ga;
    initialize_game_action(&ga);
    initialize_game_action_for__hitbox(&ga, target_uuid,
        position, velocity, acceleration, Hitbox_Kind__AABB);

The generic `initialize_game_action` zeroes the struct. The kind-specific
initializer sets the `Game_Action_Kind` discriminator and populates the
payload union fields.

#### Step 4: Dispatch Entry Point

Two dispatch paths exist:

- `dispatch_game_action(p_game, client_uuid, &ga)` — sends to a specific
  client (used by server).
- `dispatch_game_action_to__server(p_game, &ga)` — sends to the server
  (used by client or offline).

Both invoke function pointers on `Game`:
- `m_game_action_handler__dispatch` for outbound actions.
- `m_game_action_handler__receive` for inbound actions.
- `m_game_action_handler__resolve` for resolution.

#### Step 5–6: Logic Table Lookup

The dispatch handler retrieves the `Game_Action_Logic_Entry`:

    Game_Action_Logic_Entry *p_entry =
        get_p_game_action_logic_entry_by__game_action_kind(
            &game.game_action_logic_table,
            get_kind_of__game_action(&ga));

Returns NULL if the kind is out of range (`>= Game_Action_Kind__Unknown`).

#### Step 7: Flag Sanitization

Before processing, the entry sanitizes the game action's flags:

    santize_game_action__outbound(p_entry, &ga);

Sanitization applies:

    ga.flags = (ga.flags & mask) | forced_flags;

This prevents spoofed flags (e.g. a client claiming an action is a
broadcast when the server disallows it).

#### Step 8–9: Process Dispatch

If the entry specifies `IS_WITH_PROCESS`, a `Process` is allocated:

    Process *p_process = dispatch_game_action_process__outbound(
        &game.game_action_logic_table,
        &game.process_manager,
        &ga);

The process stores the game action as `p_process_data`. The registered
`m_Process` handler casts it back:

    Game_Action *p_game_action =
        (Game_Action*)p_this_process->p_process_data;
    Identifier__u32 client_uuid = GA_UUID_SOURCE(p_game_action);

The process runs on the next `Process_Manager` poll cycle.

## Registration

### Three Runtime Modes

The `Game_Action_Registrar` provides three entry points:

| Function | Mode | Description |
|----------|------|-------------|
| `register_game_actions__offline` | Single-player | Actions processed locally. Some kinds (e.g. input) are no-ops. |
| `register_game_actions__client` | Multiplayer client | Actions relayed to server. Responses handled on receipt. |
| `register_game_actions__server` | Multiplayer server | Actions processed authoritatively. May broadcast results. |

Each calls kind-specific `register_game_action__*` functions that populate
the logic table entries with appropriate handlers, flags, and priorities.

### Registration Sequence

    initialize_game_action_logic_table(&game.game_action_logic_table);
    register_game_actions__offline(&game.game_action_logic_table);
    // or: register_game_actions__client / register_game_actions__server

### Entry Configuration Variants

| Convenience Initializer | Outbound | Inbound | Description |
|------------------------|----------|---------|-------------|
| `initialize_game_action_logic_entry_as__process__out_and_in` | Process | Process | Both directions processed. |
| `initialize_game_action_logic_entry_as__process__out` | Process | — | Only outbound processed. |
| `initialize_game_action_logic_entry_as__process__in` | — | Process | Only inbound processed. |
| `initialize_game_action_logic_entry_as__react__out` | Reactive | — | Outbound processed without IS_WITH_PROCESS flag. |
| `initialize_game_action_logic_entry_as__react__in` | — | Reactive | Inbound processed without IS_WITH_PROCESS flag. |
| `initialize_game_action_logic_entry_as__message` | — | — | Pure passthrough, no processing. |
| `initialize_game_action_logic_entry_as__broadcast__server` | Broadcast | — | Server-side broadcast. |
| `initialize_game_action_logic_entry_as__message_response` | — | Response | Inbound processed as response. |

## Game Action Kinds by Domain

### TCP Handshake

| Kind | Direction | Description |
|------|-----------|-------------|
| `TCP_Connect__Begin` | Client → Server | Initiates connection with IPv4 address and session token. |
| `TCP_Connect` | Server → Client | Confirms connection with session token. |
| `TCP_Connect__Accept` | Server → Client | Accepts the client's connection. |
| `TCP_Connect__Reject` | Server → Client | Rejects the client's connection. |
| `TCP_Disconnect` | Either | Terminates the connection. |
| `TCP_Delivery` | Either | Carries a payload fragment for multi-packet transfer. |

### Global Space (Chunk Management)

| Kind | Direction | Description |
|------|-----------|-------------|
| `Global_Space__Request` | Client → Server | Requests chunk load/generation at coordinates. |
| `Global_Space__Resolve` | Server → Client | Signals chunk is ready. |
| `Global_Space__Store` | Client → Server | Requests chunk serialization to disk. |

### Entity

| Kind | Direction | Description |
|------|-----------|-------------|
| `Entity__Spawn` | Either (+ broadcast) | Requests entity creation of a given kind. |
| `Entity__Get` | Client → Server | Requests entity data synchronization. |

### Hitbox

| Kind | Direction | Description |
|------|-----------|-------------|
| `Hitbox__Set_Position` | Client → Server | Updates hitbox position, velocity, acceleration with collision node migration. |

### Input

| Kind | Direction | Description |
|------|-----------|-------------|
| `Input` | Client → Server | Transmits player input state. No-op in offline mode. |

### World

| Kind | Direction | Description |
|------|-----------|-------------|
| `World__Load_World` | Client → Server | Requests world initialization for a client. |
| `World__Load_Client` | Client → Server | Requests client persistent data load from disk. |

### Error

| Kind | Direction | Description |
|------|-----------|-------------|
| `Bad_Request` | Server → Client | Rejects an invalid or unauthorized action with an error code. |

## Multi-Packet Transfer via TCP_Delivery

Large data structures (e.g. `Chunk`, `Entity` data) cannot fit in a single
`TCP_Packet`. The `TCP_Delivery` game action provides fragmented transfer:

### Payload Sizing

    GA_KIND__TCP_DELIVERY__PAYLOAD_SIZE_IN__BYTES =
        sizeof(TCP_Packet)
        - sizeof(_Game_Action_Header)
        - sizeof(uint64_t)

Each delivery action carries one fragment of this size.

### Fragment Tracking

The receiver uses a `Serialization_Request` with a bitmap to track
which fragments have arrived:

    TCP_PAYLOAD_BITMAP__QUANTITY_OF__PAYLOADS(type)  // total fragments
    TCP_PAYLOAD_BITMAP__QUANTITY_OF__BYTES(type)     // bitmap byte count
    TCP_PAYLOAD_BITMAP(type, name)                   // declares bitmap array

### Correlation

The `uuid_of__game_action__responding_to` header field correlates delivery
fragments with the original request (e.g. a `Global_Space__Request` or
`Entity__Get`).

### Transfer Flow

    1. Sender calculates fragment count for the data type.
    2. For each fragment index:
       dispatch_game_action__tcp_delivery(p_game, client_uuid,
           response_uuid, payload_slice, slice_size, packet_index)
    3. Receiver updates bitmap on each fragment receipt.
    4. Once all fragments received, data is reassembled.

## Error Handling

### Bad Request Pattern

When a received game action cannot be fulfilled:

    if (!can_fulfill_request) {
        dispatch_game_action__bad_request(
            p_game, p_game_action, error_code);
    }

The bad request action:
- Sets `IS_BAD_REQUEST` flag.
- Carries an application-defined error code.
- References the original action's UUID via `uuid_of__game_action__responding_to`.
- Is dispatched back to the originating client.

### Process Failure

Process handlers call `fail_process` on error and `complete_process` on
success. Failed processes do not retry automatically.

### Null Safety

- `is_game_action__allocated` is null-safe (returns false for NULL).
- `get_p_game_action_logic_entry_by__game_action_kind` returns NULL for
  out-of-range kinds.
- Allocation functions return NULL when pools are exhausted.

## Capacity Constraints

- Each `Game_Action_Manager` holds `MAX_QUANTITY_OF__GAME_ACTIONS` (512)
  slots. Allocation returns NULL when full.
- Each `Client` has two managers (inbound + outbound), for a total of
  1024 game action slots per client.
- The `Game_Action_Logic_Table` has exactly `Game_Action_Kind__Unknown`
  entries. Kinds at or beyond this value are rejected.
- `Game_Action` is sized to fit within a `TCP_Packet`, ensuring every
  action can be transmitted as a single network packet (except for
  `TCP_Delivery` which carries fragments of larger data).
