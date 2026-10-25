# set_tcp_socket_as__manually_driven

**File of origin:** `core/include/multiplayer/tcp_socket.h`

## Semantic

Sets the `TCP_SOCKET_FLAG__IS_MANUALLY_DRIVEN` bit on the given TCP socket's flags field, marking the socket as manually driven (i.e., it will be skipped during automatic polling and must be driven by some other means).

## Pre-conditions

1. `p_tcp_socket` must be a non-null pointer to a valid, initialized `TCP_Socket` struct.
2. The `tcp_socket_flags__u8` field of the struct must be in a valid state (any prior flag combination is acceptable).

## Post-conditions

1. The `TCP_SOCKET_FLAG__IS_MANUALLY_DRIVEN` bit (bit 0) in `p_tcp_socket->tcp_socket_flags__u8` is set to 1.
2. All other bits in `tcp_socket_flags__u8` remain unchanged (bitwise OR semantics).
3. The function returns `void`; no return value.

## Correctness Verdict

**Correct**

## Semantic Alignment

The implementation correctly fulfills its semantic intent. It uses bitwise OR (`|=`) to set only the `TCP_SOCKET_FLAG__IS_MANUALLY_DRIVEN` flag without disturbing other flags. The flag constant `TCP_SOCKET_FLAG__IS_MANUALLY_DRIVEN` is defined as `BIT(0)` (value 1), which is appropriate for a single-bit flag on a `uint8_t` field. The function is the logical inverse of `set_tcp_socket_as__automatically_driven`, which clears the same bit using `&= ~`.

## Implementation Correctness

- **Type compatibility:** `tcp_socket_flags__u8` is of type `TCP_Socket_Flags__u8`, which is `typedef uint8_t`. The flag `TCP_SOCKET_FLAG__IS_MANUALLY_DRIVEN` is `BIT(0)`, which evaluates to an `int` with value 1. The `|=` operator performs an implicit conversion of the right-hand side to `uint8_t`, which is safe since the value is 1 and fits within the range of `uint8_t`. No truncation or data loss occurs.
- **Undefined behavior:** No broken pointer arithmetic, no null dereference (assumes valid pointer per pre-conditions), no type punning, no out-of-bounds access. The function dereferences `p_tcp_socket` to access a valid struct member.
- **Validation:** No null-check is performed. This is consistent with the codebase's pattern of using `static inline` functions that assume valid inputs from the caller. The responsibility for ensuring a valid pointer lies with the caller, which is appropriate for a low-level inline helper.

## Side Effects

- **Mutates** `p_tcp_socket->tcp_socket_flags__u8` by setting the `TCP_SOCKET_FLAG__IS_MANUALLY_DRIVEN` bit (bit 0).
- No other observable side effects. Does not allocate memory, does not call other functions, does not modify any other state.
