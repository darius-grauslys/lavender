# m_process__game_action__tcp_connect__begin

**File of origin:** `core/source/game_action/core/tcp/game_action__tcp_begin_connect.c`

## Semantic

This function is the main process handler for the TCP connect-begin action. It drives the TCP socket state machine through the connection and authentication handshake phases. Depending on the current socket state, it either dispatches a connect game action (to initiate authentication), receives and evaluates authentication responses (accept/reject), or finalizes the connection by setting the socket as automatically driven.

## Pre-conditions

1. `p_this_process` must be non-null and its `p_process_data` must point to a valid `Game_Action` of kind `TCP_Connect__Begin`.
2. `p_game` must be non-null and must have a valid `TCP_Socket_Manager` initialized.
3. The session token embedded in the `Game_Action` must correspond to a UUID for which a `TCP_Socket` has already been opened (via `m_process__game_action__tcp_connect__begin__init`).
4. The socket retrieved by `get_p_tcp_socket_for__this_uuid` may be null if no socket exists for the given UUID — **the function does not guard against this**.

## Post-conditions

1. If the socket is in `Authenticated` state: the socket is set as automatically driven and the process is marked complete.
2. If the socket is in `Authenticating` state:
   - If no bytes are received: the process does nothing (breaks), leaving the socket in `Authenticating` state.
   - If an `Accept` response is received: the socket state is set to `Authenticated`, then **immediately overwritten to `Connected`** (bug — see Correctness Verdict), the socket is set as automatically driven, and the process is marked complete.
   - If a `Reject` response is received: the socket is closed via the TCP socket manager and the process is marked as failed.
   - If any other game action kind is received: the process does nothing (breaks).
3. If the socket is in `Connected` state: a connect game action is dispatched and the socket state is set to `Authenticating`.
4. If the socket is in `Disconnected` or `Unknown` state: the socket is closed and the process is marked as failed.
5. If the socket is in any other state (e.g., `None`, `Connecting`): the process does nothing (falls through to `default: break`).

## Correctness Verdict

**Incorrect**

### Bug: State overwritten from `Authenticated` to `Connected` in Accept case

In the `TCP_Connect__Accept` branch (lines 65–73), the socket state is set to `TCP_Socket_State__Authenticated` and then immediately overwritten to `TCP_Socket_State__Connected`:

```c
set_state_of__tcp_socket(p_tcp_socket, TCP_Socket_State__Authenticated);
set_tcp_socket_as__automatically_driven(p_tcp_socket);
set_state_of__tcp_socket(p_tcp_socket, TCP_Socket_State__Connected);
complete_process(p_this_process);
```

The final state of the socket is `Connected`, not `Authenticated`. This is semantically incorrect:

- `Connected` is the **initial** state for a socket that has a TCP connection but has not yet begun authentication (the `Connected` case in the switch dispatches the connect action to move to `Authenticating`).
- `Authenticated` is the state that indicates authentication has completed successfully.

By leaving the socket in `Connected` state, the socket appears as if it has not yet started the authentication process. If the process were to run again (or if other code inspects the socket state), the `Connected` case would re-dispatch the connect game action, potentially creating an infinite loop or duplicate connection attempts.

The `set_state_of__tcp_socket(p_tcp_socket, TCP_Socket_State__Connected)` call on line 71 should be removed; the socket should remain in `Authenticated` state.

## Semantic Alignment

The implementation does **not** fulfill the semantic intent. The TCP state machine is designed to progress through `Connected` → `Authenticating` → `Authenticated`. The `Accept` response correctly transitions the socket to `Authenticated`, but the subsequent overwrite to `Connected` breaks this progression and leaves the socket in an incorrect state.

## Implementation Correctness

### Null pointer dereference: `p_tcp_socket` not checked

`get_p_tcp_socket_for__this_uuid` can return `0` (null) if the socket for the given UUID is deallocated or does not exist. The function `m_process__game_action__tcp_connect__begin` dereferences `p_tcp_socket` immediately via `get_state_of__tcp_socket(p_tcp_socket)` without any null check, which would cause undefined behavior.

### Unchecked return value: `get_latest__delivery_from__tcp_socket`

In the `Authenticating` case, `get_latest__delivery_from__tcp_socket` returns a `bool` indicating whether a packet was successfully retrieved, but the return value is not checked. If it returns `false` (no packets in the queue despite `receive_bytes_over__tcp_socket` returning non-zero — an edge case), the `delivery` union would be uninitialized, and `get_kind_of__game_action(&delivery.ga_response)` would read uninitialized memory.

### Missing null checks in `m_process__game_action__tcp_connect__begin__init`

In the init function:
- `get_p_client_by__uuid_from__game` can return null if the client does not exist. `GET_UUID_P(p_client)` would then dereference a null pointer.
- `open_socket_on__tcp_socket_manager__ipv4` can return null if socket allocation fails. `set_tcp_socket_as__manually_driven(p_tcp_socket)` would then dereference a null pointer.

Neither return value is checked.

## Side Effects

- **State mutation of `TCP_Socket`**: The socket's state is modified via `set_state_of__tcp_socket` (with the buggy overwrite in the Accept case), and its flags are modified via `set_tcp_socket_as__automatically_driven` or `set_tcp_socket_as__manually_driven`.
- **Socket closure**: In the `Reject`, `Disconnected`, and `Unknown` cases, the socket is closed via `close_socket_on__tcp_socket_manager__ipv4`, which removes it from the socket manager and deallocates it.
- **Process status mutation**: The process status is set to `Complete` or `Fail` via `complete_process` or `fail_process`.
- **Game action dispatch**: In the `Connected` case, `dispatch_game_action__connect` is called, which sends a connect game action to the server.
- **No side effects on `p_game` directly** (only through the TCP socket manager and game action dispatch).
