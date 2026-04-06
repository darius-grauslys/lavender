# 1. Specification: core/include/game_action/core/tcp/game_action__tcp_delivery.h

## 1.1. Overview

Provides initialization, registration, and dispatch for the
`Game_Action_Kind__TCP_Delivery` game action. This action is the
engine's mechanism for transmitting arbitrary payloads over TCP by
splitting them into packet-sized chunks. Each delivery carries a
payload fragment and a packet index for reassembly.

## 1.2. Dependencies

- `defines.h` (for `Game_Action`, `Game_Action_Logic_Table`,
  `TCP_Packet`, `_Game_Action_Header`)
- `game.h` (for `dispatch_game_action`)
- `platform.h` (for TCP platform functions)

## 1.3. Game_Action_Kind

`Game_Action_Kind__TCP_Delivery`

## 1.4. Payload Fields

| Field | Type | Description |
|-------|------|-------------|
| `ga_kind__tcp_delivery__payload` | `u8[GA_KIND__TCP_DELIVERY__PAYLOAD_SIZE_IN__BYTES]` | The payload fragment for this packet. |
| `ga_kind__tcp_delivery__packet_index` | `Quantity__u16` | Index of this fragment in the reassembly sequence. |

### 1.4.1. Payload Size Calculation

    GA_KIND__TCP_DELIVERY__PAYLOAD_SIZE_IN__BYTES =
        sizeof(TCP_Packet)
        - sizeof(_Game_Action_Header)
        - sizeof(uint64_t)

This ensures the delivery action fits within a single `TCP_Packet`.

### 1.4.2. Payload Bitmap Macros

For tracking which fragments have been received:

| Macro | Description |
|-------|-------------|
| `TCP_PAYLOAD_BITMAP__QUANTITY_OF__PAYLOADS(type)` | Number of delivery packets needed to transmit `type`. |
| `TCP_PAYLOAD_BITMAP__QUANTITY_OF__BYTES(type)` | Byte size of the bitmap needed to track all fragments. |
| `TCP_PAYLOAD_BITMAP(type, name)` | Declares a bitmap array for tracking fragments of `type`. |
| `TCP_PAYLOAD_BIT(index)` | Bit position within a bitmap byte for fragment `index`. |
| `TCP_PAYLOAD_BYTE(index)` | Byte index within the bitmap for fragment `index`. |

## 1.5. Functions

### 1.5.1. Registration

| Function | Signature | Description |
|----------|-----------|-------------|
| `register_game_action__tcp_delivery` | `(Game_Action_Logic_Table*) -> void` | Registers the TCP delivery action kind. |

### 1.5.2. Initialization

| Function | Signature | Description |
|----------|-----------|-------------|
| `initialize_game_action_for__tcp_delivery` | `(Game_Action*, Identifier__u32 client_uuid, Identifier__u32 response_uuid, u8* payload, u32 payload_bytes, Index__u16 packet_index) -> void` | Initializes a delivery action with the payload fragment, target client, response UUID, and packet index. |

### 1.5.3. Dispatch (static inline)

| Function | Signature | Description |
|----------|-----------|-------------|
| `dispatch_game_action__tcp_delivery` | `(Game*, Identifier__u32 client_uuid, Identifier__u32 response_uuid, u8* payload, u32 payload_bytes, Index__u16 packet_index) -> void` | Creates and dispatches a delivery action. |

## 1.6. Agentic Workflow

### 1.6.1. Multi-Packet Transfer Pattern

To send a large struct (e.g. `Chunk`) over TCP:

1. Calculate the number of packets needed:
   `TCP_PAYLOAD_BITMAP__QUANTITY_OF__PAYLOADS(Chunk)`
2. For each fragment index, call `dispatch_game_action__tcp_delivery`
   with the appropriate slice of the source data.
3. The receiver uses a `Serialization_Request` with `pM_packet_bitmap`
   to track which fragments have arrived.
4. Once all fragments are received, the data is reassembled.

### 1.6.2. Relationship to Serialization_Request

The `Serialization_Request` in TCP mode tracks delivery reassembly:
- `p_tcp_packet_destination`: destination buffer for reassembled data.
- `pM_packet_bitmap`: bitmap of received fragments.
- `quantity_of__tcp_packets__anticipated`: total expected fragments.

### 1.6.3. Preconditions

- The payload pointer must be valid and contain at least
  `quantity_of__bytes_in__payload` bytes.
- `packet_index` must be less than the total number of anticipated packets.

### 1.6.4. Postconditions

- A single delivery fragment is dispatched to the target client.
- The receiver's serialization request bitmap is updated upon receipt.

### 1.6.5. Important Notes

- The `uuid_of__game_action__responding_to` field is used to correlate
  delivery fragments with the original request that triggered the transfer.
- This is the only game action kind that uses the response UUID field
  for fragment correlation rather than actual response semantics.
