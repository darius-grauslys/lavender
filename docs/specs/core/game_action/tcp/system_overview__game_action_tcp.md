# 1. System Overview: TCP Game Action Handshake and Delivery

## 1.1. Purpose

The TCP game action subsystem manages the multiplayer connection lifecycle
and provides fragmented payload delivery over TCP. It encompasses the
full handshake sequence (connect begin, connect, accept/reject) and the
multi-packet delivery mechanism used to transfer large data structures
between client and server.

## 1.2. Architecture

### 1.2.1. Handshake Action Kinds

| Kind | Initiator | Description |
|------|-----------|-------------|
| `Game_Action_Kind__TCP_Connect__Begin` | Client | Initiates a TCP connection to a server with an IPv4 address and session token. |
| `Game_Action_Kind__TCP_Connect` | Server | Confirms the connection and communicates the session token. |
| `Game_Action_Kind__TCP_Connect__Accept` | Server | Accepts the client's connection. |
| `Game_Action_Kind__TCP_Connect__Reject` | Server | Rejects the client's connection. |
| `Game_Action_Kind__TCP_Disconnect` | Either | Terminates the connection. |

### 1.2.2. Delivery Action Kind

| Kind | Initiator | Description |
|------|-----------|-------------|
| `Game_Action_Kind__TCP_Delivery` | Either | Carries a single payload fragment for multi-packet data transfer. |

## 1.3. Connection Handshake Sequence

### 1.3.1. Normal Flow (Accepted)

    Client                              Server
      |                                   |
      |-- TCP_Connect__Begin ------------>|
      |   (IPv4_Address, Session_Token)   |
      |                                   |-- (validates credentials)
      |                                   |
      |<------------ TCP_Connect ---------|
      |   (Session_Token confirmation)    |
      |                                   |
      |<-------- TCP_Connect__Accept -----|
      |                                   |
      |   [Connection established]        |
      |   [Client can send game actions]  |

### 1.3.2. Rejected Flow

    Client                              Server
      |                                   |
      |-- TCP_Connect__Begin ------------>|
      |   (IPv4_Address, Session_Token)   |
      |                                   |-- (validates credentials)
      |                                   |
      |<-------- TCP_Connect__Reject -----|
      |                                   |
      |   [Connection refused]            |
      |   [Server cleans up socket]       |

### 1.3.3. Disconnection

    Either side                         Other side
      |                                   |
      |-- TCP_Disconnect ---------------->|
      |                                   |
      |   [Connection terminated]         |

## 1.4. Handshake Details

### 1.4.1. TCP_Connect__Begin (Client → Server)

The client initiates the connection by providing:

- `ga_kind__tcp_connect__begin__ipv4_address` (`IPv4_Address`): The
  server's address and port.
- `ga_kind__tcp_connect__begin__session_token` (`Session_Token`): The
  client's authentication token.

The client UUID is passed as 0 because the server has not yet assigned
a UUID. This is functionally correct — the server assigns the UUID
during acceptance.

Preconditions:
- The game must have multiplayer initialized (`begin_multiplayer_for__game`).
- The `IPv4_Address` must have valid IP bytes and port.

### 1.4.2. TCP_Connect (Server → Client)

The server responds with a session token confirmation:

- `ga_kind__tcp_connect__session_token` (`Identifier__u64`): The session
  token confirming the connection.

This step occurs between `TCP_Connect__Begin` and the final
accept/reject decision.

### 1.4.3. TCP_Connect__Accept (Server → Client)

The server accepts the connection. No kind-specific payload fields —
the client UUID in the header identifies the accepted client.

Preconditions:
- The client must have an active TCP connection.
- The `Client` struct must be allocated with a valid UUID.

Postconditions:
- The client is informed of acceptance and can begin sending game actions.

### 1.4.4. TCP_Connect__Reject (Server → Client)

The server rejects the connection. No kind-specific payload fields —
the client UUID in the header identifies the rejected client.

Postconditions:
- The client is informed of rejection.
- The server should clean up the client's TCP socket after dispatch.

## 1.5. Multi-Packet Delivery

### 1.5.1. Purpose

`Game_Action` instances are sized to fit within a single `TCP_Packet`.
When data larger than a single packet must be transmitted (e.g. `Chunk`
data, `Entity` data), the `TCP_Delivery` action provides fragmented
transfer.

### 1.5.2. Payload Sizing

    GA_KIND__TCP_DELIVERY__PAYLOAD_SIZE_IN__BYTES =
        sizeof(TCP_Packet)
        - sizeof(_Game_Action_Header)
        - sizeof(uint64_t)

Each `TCP_Delivery` action carries exactly one fragment of this size.

### 1.5.3. Fragment Tracking with Bitmaps

The receiver tracks which fragments have arrived using a bitmap:

| Macro | Description |
|-------|-------------|
| `TCP_PAYLOAD_BITMAP__QUANTITY_OF__PAYLOADS(type)` | Number of delivery packets needed to transmit `type`. |
| `TCP_PAYLOAD_BITMAP__QUANTITY_OF__BYTES(type)` | Byte size of the bitmap needed to track all fragments. |
| `TCP_PAYLOAD_BITMAP(type, name)` | Declares a bitmap array for tracking fragments of `type`. |
| `TCP_PAYLOAD_BIT(index)` | Bit position within a bitmap byte for fragment `index`. |
| `TCP_PAYLOAD_BYTE(index)` | Byte index within the bitmap for fragment `index`. |

### 1.5.4. Delivery Payload Fields

| Field | Type | Description |
|-------|------|-------------|
| `ga_kind__tcp_delivery__payload` | `u8[PAYLOAD_SIZE]` | The payload fragment. |
| `ga_kind__tcp_delivery__packet_index` | `Quantity__u16` | Index of this fragment in the reassembly sequence. |

### 1.5.5. Fragment Correlation

The `uuid_of__game_action__responding_to` header field correlates delivery
fragments with the original request that triggered the transfer. This is
the only game action kind that uses the response UUID field for fragment
correlation rather than actual response semantics.

### 1.5.6. Transfer Flow

    Sender                              Receiver
      |                                   |
      | Calculate fragment count for type |
      |                                   |
      |-- TCP_Delivery (index=0) -------->|  bitmap[0] |= BIT(0)
      |-- TCP_Delivery (index=1) -------->|  bitmap[0] |= BIT(1)
      |-- TCP_Delivery (index=2) -------->|  bitmap[0] |= BIT(2)
      |   ...                             |  ...
      |-- TCP_Delivery (index=N-1) ------>|  bitmap[...] |= BIT(N-1)
      |                                   |
      |                                   |  All bits set -> reassemble

### 1.5.7. Integration with Serialization_Request

The `Serialization_Request` in TCP mode tracks delivery reassembly:

- `p_tcp_packet_destination`: destination buffer for reassembled data.
- `pM_packet_bitmap`: bitmap of received fragments.
- `quantity_of__tcp_packets__anticipated`: total expected fragments.

### 1.5.8. Consumers

The following game action kinds use `TCP_Delivery` for multi-packet
transfer:

| Consumer | Data Transferred |
|----------|-----------------|
| `Global_Space__Request` | Chunk data (server → client in multiplayer). |
| `Entity__Get` | Entity data (server → client). |

## 1.6. Lifecycle

### 1.6.1. Initialization

    initialize_game_action_logic_table(&game.game_action_logic_table);

    // For server mode:
    register_game_actions__server(&game.game_action_logic_table);
    // Internally calls:
    //   register_game_action__tcp_connect__begin(...)
    //   register_game_action__tcp_connect(...)
    //   register_game_action__tcp_connect__accept(...)
    //   register_game_action__tcp_connect__reject(...)
    //   register_game_action__tcp_delivery(...)

### 1.6.2. Client Connects

    // Client side:
    dispatch_game_action__connect__begin(
        p_game, ipv4_address, session_token);

    // Server receives, validates, then:
    dispatch_game_action__connect__accept(p_game, p_client);
    // or:
    dispatch_game_action__connect__reject(p_game, p_client);

### 1.6.3. Data Transfer

    // Server sends chunk data to client:
    for (Index__u16 i = 0; i < fragment_count; i++) {
        dispatch_game_action__tcp_delivery(
            p_game, client_uuid, request_uuid,
            &chunk_bytes[i * PAYLOAD_SIZE],
            PAYLOAD_SIZE, i);
    }

### 1.6.4. Disconnection

    // Either side:
    // TCP_Disconnect game action is dispatched.
    // Connection is terminated and resources cleaned up.

## 1.7. Error Handling

- If the server rejects a connection, `TCP_Connect__Reject` is sent and
  the server cleans up the socket.
- If a delivery fragment references an unknown request UUID, the receiver
  may issue a `Bad_Request`.
- If the `Process_Manager` is full when dispatching a TCP action, the
  dispatch returns NULL.
