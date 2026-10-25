receive_bytes_over__tcp_socket — core/source/multiplayer/tcp_socket.c, lines 97-133

## Semantic

Receives incoming TCP data from a socket's platform handle into a circular queue of fixed-size packet buffers, incrementing a received-packet counter for each buffer that receives data. Returns the total quantity of bytes received, or a `TCP_ERROR__XXX` code on failure.

## Pre-conditions

1. `p_tcp_socket` must be non-null and point to a valid, initialized `TCP_Socket`.
2. `p_tcp_socket->p_PLATFORM_tcp_socket` must be non-null and refer to a valid, connected platform-level TCP socket.
3. The socket must be in a connected state (`TCP_Socket_State__Connected` or similar) so that `PLATFORM_tcp_recieve` can operate.
4. The receive queue must have at least one free slot (i.e., `quantity_of__received_packets < MAX_QUANTITY_OF__TCP_PACKETS_PER__SOCKET`). If this is not satisfied, the function returns `TCP_ERROR__QUEUE_FULL` immediately.

## Post-conditions

1. For each `PLATFORM_tcp_recieve` call that returns a positive byte count, `p_tcp_socket->quantity_of__received_packets` is incremented by one.
2. Received bytes are written into `p_tcp_socket->queue_of__tcp_packet` at the slot indexed by `(index_of__enqueue_begin + quantity_of__received_packets) & (MAX_QUANTITY_OF__TCP_PACKETS_PER__SOCKET - 1)`.
3. The return value is `i32`: either the total bytes received, or a `TCP_ERROR__XXX` negative code.

## Correctness Verdict

**Incorrect**

## Semantic Alignment

The implementation does **not** fulfill the semantic intent documented in both the header comment and the function's own contract. The header states:

```
/// Returns the quantity of bytes received.
/// Returns a TCP_ERROR__XXX otherwise.
```

However, the return statement computes:

```c
return MAX_SIZE_OF__TCP_PACKET
    * p_tcp_socket->quantity_of__received_packets;
```

This returns the **maximum possible** bytes (assuming every packet buffer is completely filled), **not** the actual number of bytes received. Each call to `PLATFORM_tcp_recieve` may return fewer bytes than `MAX_SIZE_OF__TCP_PACKET` (partial packets are common in TCP). The correct return value should be the **sum** of all `quantity_received` values from each `PLATFORM_tcp_recieve` call, accumulated across the loop.

Additionally, the `packet_size__entries` array — which exists precisely to track the actual byte count per packet (via the `get_size_of__tcp_packet` / `set_size_of__tcp_packet` helpers) — is **never updated** during reception. This means consumers of the queue (e.g., `get_latest__delivery_from__tcp_socket`) have no way to know how many bytes were actually received in each packet slot, defeating the purpose of that metadata field.

## Implementation Correctness

1. **Swallowed error code (Incorrect):** When `PLATFORM_tcp_recieve` returns `TCP_ERROR__DESTINATION_OVERFLOW` (-1), the function logs an error and returns `0`. However, `0` is a valid "no bytes received" result. The function should return `TCP_ERROR__DESTINATION_OVERFLOW` to properly propagate the error, allowing the caller to distinguish between "no data" and "overflow error" as documented.

2. **Missing null checks (Incorrect):** Unlike `poll_tcp_socket_for__connection` in the same file, this function performs no null check on `p_tcp_socket` or `p_platform_tcp_socket`. If either is null, `can_tcp_socket__receive_more_packets` or `PLATFORM_tcp_recieve` will dereference a null pointer, causing undefined behavior.

3. **Type compatibility:** The `quantity_received` variable is `i32`, matching the return type of `PLATFORM_tcp_recieve`. The `switch` correctly handles the negative error codes (`TCP_ERROR__DESTINATION_OVERFLOW` = -1) and the zero case. No implicit conversions or truncation issues.

4. **Pointer arithmetic / bounds:** The index computation `p_tcp_socket->index_of__enqueue_begin + p_tcp_socket->quantity_of__received_packets` is passed to `get_p_tcp_packet_by__index_from__queue_of__tcp_socket`, which applies a bitmask `& (MAX_QUANTITY_OF__TCP_PACKETS_PER__SOCKET - 1)`. Since `MAX_QUANTITY_OF__TCP_PACKETS_PER__SOCKET` is `BIT(8)` (a power of 2), the bitmask correctly wraps the index. The `can_tcp_socket__receive_more_packets` guard ensures `quantity_of__received_packets` does not exceed the queue capacity, preventing out-of-bounds writes. No undefined behavior from pointer arithmetic.

5. **Loop termination:** The `do-while` loop terminates when `PLATFORM_tcp_recieve` returns 0 (no more data available) or when the queue fills up (via `break`). This is correct.

## Side Effects

- **Mutates** `p_tcp_socket->quantity_of__received_packets` (incremented for each packet that receives a positive byte count).
- **Writes** received bytes into `p_tcp_socket->queue_of__tcp_packet` buffer slots.
- Does **not** update `p_tcp_socket->packet_size__entries` (this is a bug — see Semantic Alignment).
- Does **not** modify `p_tcp_socket->index_of__enqueue_begin` (that is the responsibility of `get_latest__delivery_from__tcp_socket`).
- Calls `debug_error(...)` on error conditions, which may produce log output.
