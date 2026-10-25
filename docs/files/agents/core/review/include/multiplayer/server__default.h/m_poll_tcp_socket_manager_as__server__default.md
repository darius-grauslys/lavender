# Function Review: m_poll_tcp_socket_manager_as__server__default

**File of origin:** `core/source/multiplayer/server__default.c`

## Semantic

Polls a TCP socket manager for pending incoming connections and processes received game action packets from all active client sockets. In a server context, it accepts new connections on the server socket, handles them, and then iterates through all client sockets to receive and dispatch inbound game actions.

## Pre-conditions

1. `p_tcp_socket_manager` must be non-null and properly initialized (via `initialize_tcp_socket_manager`).
2. `p_game` must be non-null and properly initialized.
3. `p_tcp_socket_manager->ptr_array_of__tcp_sockets` must contain at least two entries: index 0 for the server socket and index 1 for the auth socket.
4. `p_tcp_socket_manager->ptr_array_of__tcp_sockets[0]` (the server socket) must be non-null — checked only in debug builds via `debug_abort`.
5. `p_tcp_socket_manager->ptr_array_of__tcp_sockets[1]` (the auth socket) is not validated for non-null; a null auth socket will cause the client loop to terminate immediately (the `*p_ptr_tcp_socket__client` null check in the while condition handles this gracefully).
6. The `m_poll_tcp_socket_manager` function pointer in the `TCP_Socket_Manager` struct must point to this function (though it is not directly invoked within the function itself).

## Post-conditions

1. Any pending incoming TCP connection is detected via `poll_tcp_socket_manager_for__pending_connections` and handled via `handle_pending_connection`, which reads an initial `TCP_DELIVERY(Game_Action, ga_connect)` packet and dispatches a connect game action if applicable.
2. All client TCP sockets (indices 1 through `MAX_QUANTITY_OF__TCP_SOCKETS - 1` in `ptr_array_of__tcp_sockets`) have `receive_bytes_over__tcp_socket` called on them to pull in any pending bytes.
3. All queued `TCP_Packet`s from each client socket are dequeued via `get_latest__delivery_from__tcp_socket` and dispatched via `receive_game_action` with the client's UUID.
4. The function returns `void`; no return value is produced.

## Correctness Verdict

**Incorrect**

## Semantic Alignment

The implementation generally aligns with the semantic intent of polling a TCP socket manager in a server context. The function correctly:
- Retrieves the server and auth sockets from the pointer array.
- Polls for pending connections and handles them.
- Iterates through client sockets (starting at index 1, skipping the server socket at index 0) to receive bytes and dispatch game actions.

However, there are critical bugs that cause the semantics to fail in practice (see Implementation Correctness below).

## Implementation Correctness

### Bug 1: Null pointer dereference on `p_client`

After calling `get_p_client_by__uuid_from__game(p_game, GET_UUID_P(p_tcp_socket__client))`, the returned `p_client` pointer is used without a null check. If no client exists for the given UUID, `p_client` will be NULL, and the subsequent call `GET_UUID_P(p_client)` dereferences the null pointer, causing **undefined behavior**.

The line:
```c
receive_game_action(
        p_game,
        GET_UUID_P(p_client),  // <-- p_client may be NULL here
        &deliver.game_action);
```

This should be guarded with a null check on `p_client` before using it.

### Bug 2: Incorrect error handling for `receive_bytes_over__tcp_socket`

`receive_bytes_over__tcp_socket` can return:
- `0` — no bytes received (disconnected or no data)
- `TCP_ERROR__QUEUE_FULL` (`-2`) — the socket's packet queue is full
- A positive value — bytes received

The code checks `if (!receive_bytes_over__tcp_socket(...))` which treats both `0` and negative return values (like `-2`) as "skip this socket." However, a queue-full condition (`-2`) is an error that should be logged or handled differently, not silently ignored. Treating it as "no data" means the socket's packet queue could overflow without any diagnostic.

### Bug 3: Potential out-of-bounds access with `MAX_QUANTITY_OF__TCP_SOCKETS`

The function accesses `ptr_array_of__tcp_sockets[0]` (server) and `ptr_array_of__tcp_sockets[1]` (auth), requiring at least 2 entries. However, `MAX_QUANTITY_OF__TCP_SOCKETS` defaults to `1` in `platform_defaults.h`. If a platform does not override this value, the access to `ptr_array_of__tcp_sockets[1]` is an out-of-bounds read. While this is likely a configuration concern rather than a code bug (platforms are expected to override), the debug assertion does not catch this — it only checks `p_tcp_socket__server` for null, not that the array is large enough.

## Side Effects

1. **Reads from network sockets**: Calls `PLATFORM_tcp_recieve` (indirectly via `receive_bytes_over__tcp_socket`) and `PLATFORM_tcp_poll_accept` (via `handle_pending_connection` and `poll_tcp_socket_manager_for__pending_connections`) to receive data from client sockets and detect pending connections.
2. **Mutates TCP socket internal state**: `receive_bytes_over__tcp_socket` increments `quantity_of__received_packets` on each `TCP_Socket` it processes. `get_latest__delivery_from__tcp_socket` decrements `quantity_of__received_packets` and zeroes out dequeued `TCP_Packet` entries.
3. **Dispatches game actions**: Calls `receive_game_action`, which may create, modify, or process `Game_Action` objects within the game's action managers.
4. **May trigger connection handling side effects**: `handle_pending_connection` calls `receive_game_action__connect`, which may add or modify client state in the game.
5. **No heap allocation or file I/O**: The function does not allocate memory or perform file operations.
