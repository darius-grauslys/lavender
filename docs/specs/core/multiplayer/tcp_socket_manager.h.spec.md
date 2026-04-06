# 1. Specification: core/include/multiplayer/tcp_socket_manager.h

## 1.1 Overview

Provides pool management, connection lifecycle orchestration, and polling
for `TCP_Socket` instances. The `TCP_Socket_Manager` is the central
coordinator for all multiplayer TCP connections, managing a fixed-size
pool of `TCP_Socket` objects and delegating platform-specific operations
to `PLATFORM_TCP_*` functions.

The manager supports both client and server roles through its pluggable
`m_Poll_TCP_Socket_Manager` callback, which is set during initialization
to either a client or server polling strategy.

## 1.2 Dependencies

- `defines.h` (for `TCP_Socket_Manager`, `TCP_Socket`, `IPv4_Address`,
  `Identifier__u32`, `Index__u16`, `Quantity__u32`, `PLATFORM_TCP_Socket`,
  `PLATFORM_TCP_Context`, `Serialization_Header`)
- `defines_weak.h` (forward declarations)
- `platform_defaults.h` (for `MAX_QUANTITY_OF__TCP_SOCKETS`)
- `serialization/hashing.h` (for `dehash_identitier_u32_in__contigious_array`)
- `serialization/serialization_header.h` (for `is_serialized_struct__deallocated`)

## 1.3 Types

### 1.3.1 TCP_Socket_Manager (struct)

    typedef struct TCP_Socket_Manager_t {
        TCP_Socket tcp_sockets[MAX_QUANTITY_OF__TCP_SOCKETS];
        TCP_Socket *ptr_array_of__tcp_sockets[MAX_QUANTITY_OF__TCP_SOCKETS];
        PLATFORM_TCP_Context *p_PLATFORM_tcp_context;
        m_Poll_TCP_Socket_Manager m_poll_tcp_socket_manager;
        PLATFORM_TCP_Socket *p_PLATFORM_tcp_socket__pending_connection;
        IPv4_Address ipv4__pending_connection;
        Quantity__u32 quantity_of__connections;
    } TCP_Socket_Manager;

| Field | Type | Description |
|-------|------|-------------|
| `tcp_sockets` | `TCP_Socket[MAX_QUANTITY_OF__TCP_SOCKETS]` | Fixed-size pool of socket instances. Default: 1 slot. |
| `ptr_array_of__tcp_sockets` | `TCP_Socket*[MAX_QUANTITY_OF__TCP_SOCKETS]` | Pointer array for sorted/indexed access to active sockets. |
| `p_PLATFORM_tcp_context` | `PLATFORM_TCP_Context*` | Platform-specific TCP context for socket operations. |
| `m_poll_tcp_socket_manager` | `m_Poll_TCP_Socket_Manager` | Pluggable polling callback (client or server strategy). |
| `p_PLATFORM_tcp_socket__pending_connection` | `PLATFORM_TCP_Socket*` | Holds a platform socket for a pending inbound connection (server mode). |
| `ipv4__pending_connection` | `IPv4_Address` | Address of the pending inbound connection. |
| `quantity_of__connections` | `Quantity__u32` | Number of currently active connections. |

### 1.3.2 m_Poll_TCP_Socket_Manager (function pointer)

    typedef void (*m_Poll_TCP_Socket_Manager)(
            TCP_Socket_Manager *p_tcp_socket_manager,
            Game *p_game);

The polling callback invoked each frame to drive socket I/O and
connection management. The implementation determines whether the
manager operates as a client or server.

## 1.4 Functions

### 1.4.1 Initialization

| Function | Signature | Description |
|----------|-----------|-------------|
| `initialize_tcp_socket_manager` | `(TCP_Socket_Manager*, m_Poll_TCP_Socket_Manager) -> void` | Initializes the socket pool, clears all sockets as deallocated, and sets the polling callback. |

### 1.4.2 Connection Management

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `accept_socket_on__tcp_socket_manager__ipv4` | `(TCP_Socket_Manager*, PLATFORM_TCP_Socket*, IPv4_Address, Identifier__u32 uuid) -> TCP_Socket*` | `TCP_Socket*` | Accepts an already-established platform socket (from server accept) into the pool. Returns the allocated `TCP_Socket`, or null on failure. |
| `open_socket_on__tcp_socket_manager__ipv4` | `(TCP_Socket_Manager*, IPv4_Address, Identifier__u32 uuid) -> TCP_Socket*` | `TCP_Socket*` | Opens a new outbound connection to the given address. Allocates a `TCP_Socket` from the pool and initiates a platform connect via `PLATFORM_tcp_connect`. Returns null on failure. |
| `open_server_socket_on__tcp_socket_manager__ipv4` | `(TCP_Socket_Manager*, Identifier__u32 uuid, Index__u16 port) -> TCP_Socket*` | `TCP_Socket*` | Opens a server (listening) socket on the given port via `PLATFORM_tcp_server`. Returns null on failure. |
| `close_socket_on__tcp_socket_manager__ipv4` | `(TCP_Socket_Manager*, TCP_Socket*) -> void` | `void` | Closes the given socket, releases platform resources via `unbind_tcp_socket`, and returns the slot to the pool. |

### 1.4.3 Pending Connection Handling (Server Mode)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `poll_tcp_socket_manager_for__pending_connections` | `(TCP_Socket_Manager*, TCP_Socket *p_server_socket, IPv4_Address *p_ipv4) -> PLATFORM_TCP_Socket*` | `PLATFORM_TCP_Socket*` | Checks for new inbound connections on the server socket via `PLATFORM_tcp_poll_accept`. Returns a `PLATFORM_TCP_Socket` if a connection is pending, null otherwise. Populates `p_ipv4` with the connecting client's address. |
| `reject_pending_connection` | `(TCP_Socket_Manager*) -> void` | `void` | Rejects and closes the pending inbound connection via `PLATFORM_tcp_close_socket`. Clears `p_PLATFORM_tcp_socket__pending_connection`. |
| `accept_pending_connection` | `(TCP_Socket_Manager*, Identifier__u32 uuid) -> TCP_Socket*` | `TCP_Socket*` | Accepts the pending inbound connection into the pool with the given UUID. Delegates to `accept_socket_on__tcp_socket_manager__ipv4`. Returns the allocated `TCP_Socket`, or null if acceptance failed. Clears `p_PLATFORM_tcp_socket__pending_connection`. |

### 1.4.4 Queries (static inline)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `get_p_tcp_socket_for__this_uuid` | `(TCP_Socket_Manager*, Identifier__u32 uuid) -> TCP_Socket*` | `TCP_Socket*` | Looks up a socket by UUID via `dehash_identitier_u32_in__contigious_array`. Returns null if not found or deallocated. |
| `get_p_PLATFORM_tcp_context_from__tcp_socket_manager` | `(TCP_Socket_Manager*) -> PLATFORM_TCP_Context*` | `PLATFORM_TCP_Context*` | Returns the platform TCP context. |
| `get_quantity_of__active_tcp_sockets` | `(TCP_Socket_Manager*) -> Quantity__u32` | `Quantity__u32` | Returns the number of active connections. |

## 1.5 Agentic Workflow

### 1.5.1 Initialization Flow

    PLATFORM_tcp_begin(p_game)
        → returns PLATFORM_TCP_Context*

    initialize_tcp_socket_manager(p_tcp_socket_manager, m_poll_callback)
        → clears all TCP_Socket slots as deallocated
        → sets m_poll_tcp_socket_manager to client or server strategy

### 1.5.2 Server Lifecycle

    open_server_socket_on__tcp_socket_manager__ipv4(manager, uuid, port)
        → PLATFORM_tcp_server(context, port)
        → allocates TCP_Socket from pool
        → binds PLATFORM_TCP_Socket to TCP_Socket

    [Each frame: m_poll_tcp_socket_manager invoked]
        → poll_tcp_socket_manager_for__pending_connections(manager, server_socket, &ipv4)
            → PLATFORM_tcp_poll_accept(...)
            → if pending: store in p_PLATFORM_tcp_socket__pending_connection

        → [Game logic decides to accept or reject]
            → accept_pending_connection(manager, uuid)
                → accept_socket_on__tcp_socket_manager__ipv4(...)
                → increments quantity_of__connections
            OR
            → reject_pending_connection(manager)
                → PLATFORM_tcp_close_socket(...)

        → [For each active socket: receive/send data]

    close_socket_on__tcp_socket_manager__ipv4(manager, socket)
        → unbind_tcp_socket(...)
        → decrements quantity_of__connections

### 1.5.3 Client Lifecycle

    open_socket_on__tcp_socket_manager__ipv4(manager, ipv4, uuid)
        → PLATFORM_tcp_connect(context, &ipv4)
        → allocates TCP_Socket from pool
        → binds PLATFORM_TCP_Socket to TCP_Socket

    [Each frame: m_poll_tcp_socket_manager invoked]
        → poll_tcp_socket_for__connection(socket)
            → PLATFORM_tcp_poll_connect(...)
            → returns TCP_Socket_State

        → [Once connected: receive/send data]

    close_socket_on__tcp_socket_manager__ipv4(manager, socket)
        → unbind_tcp_socket(...)
        → decrements quantity_of__connections

### 1.5.4 UUID-Based Lookup

Sockets are stored in a contiguous pool and looked up by UUID using
hash-based search via `dehash_identitier_u32_in__contigious_array`.
This provides O(1) average-case lookup:

    TCP_Socket *p_socket =
        get_p_tcp_socket_for__this_uuid(p_manager, uuid);
    if (!p_socket) {
        // socket not found or deallocated
    }

### 1.5.5 Preconditions

- `initialize_tcp_socket_manager`: `p_tcp_socket_manager` must be non-null.
  `m_poll_tcp_socket_manager` should be a valid polling callback.
- `open_socket_on__tcp_socket_manager__ipv4`: pool must have available slots.
- `open_server_socket_on__tcp_socket_manager__ipv4`: pool must have available slots.
- `accept_pending_connection`: a pending connection must exist
  (`p_PLATFORM_tcp_socket__pending_connection` is non-null).
- `close_socket_on__tcp_socket_manager__ipv4`: the socket must be a valid,
  allocated socket from this manager's pool.

### 1.5.6 Postconditions

- After `initialize_tcp_socket_manager`: all socket slots are deallocated,
  `quantity_of__connections` is 0, polling callback is set.
- After `open_socket_on__tcp_socket_manager__ipv4` (success): a new
  `TCP_Socket` is allocated with the given UUID and address, platform
  connect is initiated.
- After `open_server_socket_on__tcp_socket_manager__ipv4` (success): a new
  `TCP_Socket` is allocated with the given UUID, platform server socket
  is bound.
- After `accept_pending_connection` (success): the pending platform socket
  is bound to a pool slot, `quantity_of__connections` is incremented,
  `p_PLATFORM_tcp_socket__pending_connection` is cleared.
- After `reject_pending_connection`: the pending platform socket is closed,
  `p_PLATFORM_tcp_socket__pending_connection` is cleared.
- After `close_socket_on__tcp_socket_manager__ipv4`: the socket slot is
  deallocated, platform resources are released, `quantity_of__connections`
  is decremented.

### 1.5.7 Error Handling

- Functions returning `TCP_Socket*` return null on allocation failure or
  platform-level errors.
- `accept_pending_connection` returns null if the pool is full or the
  platform socket binding fails.
