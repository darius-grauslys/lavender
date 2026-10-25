# handle_pending_connection

**File of origin:** `core/source/multiplayer/server__default.c`

## Semantic

Receives incoming TCP data from a pending client connection socket, interprets the received bytes as a `Game_Action` (via a `TCP_DELIVERY` union), and dispatches it to the appropriate game action handler based on the action kind. If the action is a TCP connect request, it extracts the session token and invokes `receive_game_action__connect`.

## Pre-conditions

1. `p_game` must be a valid, non-null pointer to an initialized `Game` struct.
2. `p_PLATFORM_tcp_socket` may be null (in which case the function returns early without receiving any data); if non-null, it must be a valid, open `PLATFORM_TCP_Socket` from which data can be received.
3. The `TCP_DELIVERY(Game_Action, ga_connect)` macro must be used to declare a variable named `delivery` (see Correctness Verdict below — the current code is missing this declaration).
4. `PLATFORM_tcp_recieve` must return the number of bytes received into the delivery buffer, or a `TCP_ERROR__XXX` value (negative) on error.

## Post-conditions

1. If `p_PLATFORM_tcp_socket` is null or `PLATFORM_tcp_recieve` returns 0 or a negative error value, the function returns immediately with no side effects.
2. If data was received, the function inspects the `Game_Action_Kind` field of the received `Game_Action`:
   - For `Game_Action_Kind__TCP_Connect`: calls `receive_game_action__connect(p_game, session_token)` with the session token extracted from the `GA_TCP_Connect__Begin` payload.
   - For any other kind: falls through to the `default` case, which does nothing (a `// TODO: timeout` comment suggests future timeout handling).
3. No return value; the function is `void`.

## Correctness Verdict

**Incorrect**

### Critical Bug: Undeclared variable `delivery`

The function declares:
```c
TCP_DELIVERY(Game_Action, ga_connect);
```

The `TCP_DELIVERY` macro (defined in `core/include/multiplayer/tcp_socket.h`) expands to:
```c
union {
    Game_Action ga_connect;
    TCP_Packet tcp_packet;
}
```

This is an **anonymous union type definition** — it does **not** declare a variable. The semicolon at the end makes it an empty declaration. The variable `delivery` is subsequently used in three places:

- `(u8*)&delivery` — passed to `PLATFORM_tcp_recieve`
- `sizeof(delivery)` — size of the buffer
- `&delivery.ga_connect` — passed to `get_kind_of__game_action` and `get_session_token_from__ga_tcp_connect__begin`

Since `delivery` is never declared, this code will **not compile**. The correct usage should be:
```c
TCP_DELIVERY(Game_Action, ga_connect) delivery;
```

which would expand to:
```c
union {
    Game_Action ga_connect;
    TCP_Packet tcp_packet;
} delivery;
```

### Type Mismatch: Implicit narrowing of session token

The function calls:
```c
receive_game_action__connect(
    p_game, 
    get_session_token_from__ga_tcp_connect__begin(
        &delivery.ga_connect).session_token
);
```

- `get_session_token_from__ga_tcp_connect__begin` returns a `Session_Token` struct (defined in `defines.h`), whose `.session_token` field is of type `Identifier__u64` (`uint64_t`).
- `receive_game_action__connect` (declared in `core/include/game_action/core/tcp/game_action__tcp_connect.h`) accepts `Identifier__u32` (`uint32_t`).

This produces an **implicit narrowing conversion** from `uint64_t` to `uint32_t`, which can silently truncate session tokens whose values exceed 32 bits. The `receive_game_action__connect` implementation itself contains a `#warning u32 sess token` and a `// TODO Why is a u32 session token being used here` comment, confirming this is a known unresolved issue.

## Semantic Alignment

The implementation's intent is to receive a TCP delivery, interpret it as a `Game_Action`, and dispatch based on the action kind. The semantic intent is sound, but the implementation fails to compile due to the undeclared `delivery` variable. Additionally, the type mismatch in the session token parameter means that even if the code compiled, it could lose data on session tokens exceeding 32 bits. The `default` case's `// TODO: timeout` indicates incomplete handling of unrecognized action kinds, but this does not violate the function's core semantic intent.

## Implementation Correctness

- **Type compatibility**: The `PLATFORM_tcp_recieve` call passes `(u8*)&delivery` and `sizeof(delivery)`, which are correct for receiving raw bytes into the union buffer. However, `delivery` is undeclared (see Critical Bug above). The `receive_game_action__connect` call passes an `Identifier__u64` where `Identifier__u32` is expected — an implicit narrowing conversion that may cause data loss.
- **Undefined behavior**: If the `delivery` variable were properly declared, the union is not zero-initialized before `PLATFORM_tcp_recieve` is called. If `PLATFORM_tcp_recieve` returns fewer bytes than `sizeof(delivery)`, the unread portion of the union would contain indeterminate values. Accessing `get_kind_of__game_action(&delivery.ga_connect)` on partially-filled data could read garbage. However, this is a common pattern in the codebase's TCP handling and may be acceptable if `PLATFORM_tcp_recieve` is expected to always fill the entire buffer or return an error.
- **Validation**: The null check for `p_PLATFORM_tcp_socket` is appropriate and prevents a null pointer dereference in `PLATFORM_tcp_recieve`. The `if (!quantity_received)` check correctly handles both the "no data" case (return value 0) and error cases (negative return values from `PLATFORM_tcp_recieve`). The `p_game` pointer is not validated, but it is always passed from a valid caller context in `m_poll_tcp_socket_manager_as__server__default`.

## Side Effects

1. `PLATFORM_tcp_recieve` is called, which reads data from the platform TCP socket into the `delivery` buffer (if `p_PLATFORM_tcp_socket` is non-null).
2. If a `Game_Action_Kind__TCP_Connect` action is received, `receive_game_action__connect` is called, which allocates a `Game_Action` on the stack, initializes it, and passes it to `receive_game_action` — this may enqueue a process in the game's process manager, potentially allocating a client and accepting the pending TCP connection.
3. No direct mutation of `p_game` or `p_PLATFORM_tcp_socket` occurs within this function itself; mutations are delegated to `receive_game_action__connect` and downstream handlers.
