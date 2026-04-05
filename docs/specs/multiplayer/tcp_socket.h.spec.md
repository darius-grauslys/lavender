# Specification: core/include/multiplayer/tcp_socket.h

## Overview

Provides initialization, lifecycle management, data transmission, and
state queries for individual `TCP_Socket` instances. A `TCP_Socket`
wraps a platform-provided `PLATFORM_TCP_Socket` with a packet queue,
connection state machine, and UUID-based identity for pool management.

This is the per-connection building block of the multiplayer system.
`TCP_Socket_Manager` allocates and manages collections of these sockets.

## Dependencies

- `defines.h` (for `TCP_Socket`, `TCP_Socket_State`, `TCP_Socket_Flags__u8`,
  `TCP_Packet`, `IPv4_Address`, `Identifier__u32`, `Quantity__u32`,
  `PLATFORM_TCP_Socket`, `PLATFORM_TCP_Context`, `u8`, `i32`)
- `defines_weak.h` (forward declarations)

## Types

### TCP_Socket (struct)

    typedef struct TCP_Socket_t {
        Serialization_Header _serialization_header;
        TCP_Packet queue_of__tcp_packet[MAX_QUANTITY_OF__TCP_PACKETS_PER__SOCKET];
        Quantity__u16 packet_size__entries[MAX_QUANTITY_OF__TCP_PACKETS_PER__SOCKET];
        IPv4_Address tcp_socket__address;
        PLATFORM_TCP_Socket *p_PLATFORM_tcp_socket;
        Index__u32 index_of__enqueue_begin;
        Quantity__u32 quantity_of__received_packets;
        TCP_Socket_State tcp_socket__state_of;
        TCP_Socket_Flags__u8 tcp_socket_flags__u8;
    } TCP_Socket;

| Field | Type | Description |
|-------|------|-------------|
| `_serialization_header` | `Serialization_Header` | UUID and struct size for pool lookup via hashing. |
| `queue_of__tcp_packet` | `TCP_Packet[MAX_QUANTITY_OF__TCP_PACKETS_PER__SOCKET]` | Circular buffer of received packets. Default capacity: `BIT(8)` (256). |
| `packet_size__entries` | `Quantity__u16[MAX_QUANTITY_OF__TCP_PACKETS_PER__SOCKET]` | Size of each corresponding packet in the queue. |
| `tcp_socket__address` | `IPv4_Address` | Remote endpoint address. |
| `p_PLATFORM_tcp_socket` | `PLATFORM_TCP_Socket*` | Platform-specific socket handle. |
| `index_of__enqueue_begin` | `Index__u32` | Start index of the circular packet queue. |
| `quantity_of__received_packets` | `Quantity__u32` | Number of packets currently in the queue. |
| `tcp_socket__state_of` | `TCP_Socket_State` | Current connection state. |
| `tcp_socket_flags__u8` | `TCP_Socket_Flags__u8` | Behavioral flags. |

### TCP_Socket_State (enum)

    typedef enum TCP_Socket_State {
        TCP_Socket_State__None = 0,
        TCP_Socket_State__Disconnected,
        TCP_Socket_State__Connecting,
        TCP_Socket_State__Connected,
        TCP_Socket_State__Authenticating,
        TCP_Socket_State__Authenticated,
        TCP_Socket_State__Unknown
    } TCP_Socket_State;

| Value | Description |
|-------|-------------|
| `None` | Initial/unset state. |
| `Disconnected` | Socket is not connected. |
| `Connecting` | Connection attempt in progress. |
| `Connected` | TCP connection established. |
| `Authenticating` | Session token validation in progress. |
| `Authenticated` | Session validated, ready for game actions. |
| `Unknown` | Sentinel/invalid value. |

### TCP_Packet (struct)

    typedef struct TCP_Packet_t {
        u8 tcp_packet_bytes[MAX_SIZE_OF__TCP_PACKET];
    } TCP_Packet;

| Field | Type | Description |
|-------|------|-------------|
| `tcp_packet_bytes` | `u8[MAX_SIZE_OF__TCP_PACKET]` | Raw byte payload. Default size: `BIT(9)` (512 bytes). Must be a power of 2. |

### TCP_Socket_Flags__u8 (u8)

| Flag | Bit | Description |
|------|-----|-------------|
| `TCP_SOCKET_FLAG__IS_MANUALLY_DRIVEN` | 0 | When set, the socket is skipped during automatic polling and must be driven externally. |

### TCP_DELIVERY Macro

    #define TCP_DELIVERY(type, name) \
        union { \
            type name; \
            TCP_Packet tcp_packet; \
        }

Convenience macro for overlaying a typed struct with a `TCP_Packet` for
zero-copy transmission.

### TCP Error Constants

| Constant | Value | Description |
|----------|-------|-------------|
| `TCP_ERROR__DESTINATION_OVERFLOW` | -1 | Destination buffer has run out of space. |
| `TCP_ERROR__QUEUE_FULL` | -2 | Socket queue is full; read contents before acquiring more. |

## Functions

### Initialization

| Function | Signature | Description |
|----------|-----------|-------------|
| `initialize_tcp_socket` | `(TCP_Socket*, IPv4_Address, Identifier__u32 uuid) -> void` | Initializes a socket with the given address and UUID. Sets up the packet queue and connection state. |
| `initialize_tcp_socket_as__deallocated` | `(TCP_Socket*) -> void` | Marks the socket as deallocated and available for reuse. |

### Connection

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `poll_tcp_socket_for__connection` | `(TCP_Socket*) -> TCP_Socket_State` | `TCP_Socket_State` | Polls a non-server socket for connection progress. Call repeatedly after opening until a terminal state (`Connected` or `Disconnected`) is returned. Delegates to `PLATFORM_tcp_poll_connect`. |

### Data Transfer

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `send_bytes_over__tcp_socket` | `(TCP_Socket*, u8 *p_bytes, Quantity__u32 length) -> void` | `void` | Sends raw bytes over the socket via `PLATFORM_tcp_send`. |
| `receive_bytes_over__tcp_socket` | `(TCP_Socket*) -> i32` | `i32` | Receives bytes into the socket's packet queue via `PLATFORM_tcp_recieve`. Returns quantity of bytes received, or a `TCP_ERROR__XXX` value on failure. |
| `get_latest__delivery_from__tcp_socket` | `(TCP_Socket*, TCP_Packet *p_out) -> bool` | `bool` | Dequeues the latest packet from the socket's queue into `p_out`. Returns true if a packet was available, false if the queue is empty. |

### Binding

| Function | Signature | Description |
|----------|-----------|-------------|
| `bind_tcp_socket` | `(TCP_Socket*, PLATFORM_TCP_Socket*) -> void` | Associates a platform socket handle with this `TCP_Socket`. |
| `unbind_tcp_socket` | `(PLATFORM_TCP_Context*, TCP_Socket*) -> void` | Disassociates and releases the platform socket handle via `PLATFORM_tcp_close_socket`. |

### Queries (static inline)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `get_p_PLATFORM_tcp_socket_from__tcp_socket` | `(TCP_Socket*) -> PLATFORM_TCP_Socket*` | `PLATFORM_TCP_Socket*` | Returns the bound platform socket. |
| `get_state_of__tcp_socket` | `(TCP_Socket*) -> TCP_Socket_State` | `TCP_Socket_State` | Returns the current connection state. |
| `set_state_of__tcp_socket` | `(TCP_Socket*, TCP_Socket_State) -> void` | `void` | Sets the connection state. |
| `get_tcp_socket_flags_from__tcp_socket` | `(TCP_Socket*) -> TCP_Socket_Flags__u8` | `TCP_Socket_Flags__u8` | Returns the socket's flags. |
| `is_tcp_socket__manually_driven` | `(TCP_Socket*) -> bool` | `bool` | True if `TCP_SOCKET_FLAG__IS_MANUALLY_DRIVEN` is set. |
| `set_tcp_socket_as__manually_driven` | `(TCP_Socket*) -> void` | `void` | Sets the manually driven flag. |
| `set_tcp_socket_as__automatically_driven` | `(TCP_Socket*) -> void` | `void` | Clears the manually driven flag. |

## Agentic Workflow

### Connection Lifecycle

    [Deallocated] --> initialize_tcp_socket --> [None]
                                                  |
                                       bind_tcp_socket (PLATFORM_TCP_Socket)
                                                  |
                                             [Connecting]
                                                  |
                                   poll_tcp_socket_for__connection (repeated)
                                                  |
                                  +-------+-------+-------+
                                  |                       |
                             [Connected]          [Disconnected]
                                  |                       |
                       send/receive loop           unbind_tcp_socket
                                  |                       |
                       unbind_tcp_socket      initialize_tcp_socket_as__deallocated
                                  |                       |
               initialize_tcp_socket_as__deallocated  [Deallocated]
                                  |
                             [Deallocated]

### Packet Queue Model

The `TCP_Socket` maintains a circular buffer of `TCP_Packet` entries
indexed by `index_of__enqueue_begin`. The buffer size
(`MAX_QUANTITY_OF__TCP_PACKETS_PER__SOCKET`) must be a power of 2 to
enable bitmask-based index wrapping.

    receive_bytes_over__tcp_socket(...)
        → PLATFORM_tcp_recieve(...)
        → enqueue into queue_of__tcp_packet[index]
        → increment quantity_of__received_packets

    get_latest__delivery_from__tcp_socket(...)
        → copy from queue_of__tcp_packet[index] to p_out
        → decrement quantity_of__received_packets
        → return true (or false if empty)

### Manually Driven Sockets

When `TCP_SOCKET_FLAG__IS_MANUALLY_DRIVEN` is set, the
`TCP_Socket_Manager` will skip this socket during its automatic poll
loop. This is used for sockets that require special handling (e.g.
server accept sockets, or sockets in a connection handshake driven
by a `Process`).

### Preconditions

- All functions require a non-null `TCP_Socket*`.
- `bind_tcp_socket`: the `PLATFORM_TCP_Socket*` must be a valid,
  platform-allocated socket.
- `send_bytes_over__tcp_socket`: the socket must be in `Connected`
  state or later.
- `receive_bytes_over__tcp_socket`: the socket must be in `Connected`
  state or later.

### Postconditions

- After `initialize_tcp_socket`: socket is initialized with the given
  UUID and address, packet queue is empty, state is `None`.
- After `initialize_tcp_socket_as__deallocated`: socket is marked as
  available for reuse in the pool.
- After `bind_tcp_socket`: `p_PLATFORM_tcp_socket` is non-null.
- After `unbind_tcp_socket`: `p_PLATFORM_tcp_socket` is null, platform
  resources are released.

### Error Handling

- `receive_bytes_over__tcp_socket` returns `TCP_ERROR__DESTINATION_OVERFLOW`
  or `TCP_ERROR__QUEUE_FULL` on failure.
- `get_latest__delivery_from__tcp_socket` returns false if the queue
  is empty.
