get_p_payload_u8_from__ga_tcp_connect__delivery — core/include/types/core/game_action/tcp/ga_type__tcp__connect_delivery.h

## Semantic

Returns a pointer to the `payload` byte array within the `GA_TCP_Connect__Delivery` struct, which is type-punned from the `_ga_payload_union` member of a `Game_Action`. This allows callers to read or write raw payload bytes for a TCP connect-delivery game action.

## Pre-conditions

1. `p_game_action` must be non-null.
2. The caller must ensure that the `Game_Action` was initialized with the `GA_TCP_Connect__Delivery` variant — i.e., the `_ga_payload_union` member actually holds a `GA_TCP_Connect__Delivery` struct. The function does not verify the `the_kind_of_game_action__this_action_is` discriminator; it is the caller's responsibility to ensure type correctness before invoking this accessor.

## Post-conditions

1. On success, returns a valid `u8*` pointer to the beginning of the `payload` array within the `GA_TCP_Connect__Delivery` struct. The returned pointer points to an array of `GA_KIND__TCP_DELIVERY__PAYLOAD_SIZE_IN__BYTES` bytes.
2. If pre-conditions are violated (e.g., null pointer or wrong union variant), behavior is undefined.

## Correctness Verdict

**Correct**

## Semantic Alignment

The implementation faithfully fulfills its semantic intent. It uses the `GET_P_GAME_ACTION_PAYLOAD_AS_P` macro to cast `&p_game_action->_ga_payload_union` to a `GA_TCP_Connect__Delivery*`, then accesses the `->payload` field and returns its address. This is consistent with the pattern used by all sibling accessor functions in the same header file (e.g., `get_packet_index_u16_from__ga_tcp_connect__delivery`, `get_p_packet_index_u16_from__ga_tcp_connect__delivery`). The return type (`u8*`) matches the declared type of the `payload` field (`u8 payload[...]`).

## Implementation Correctness

- **Type compatibility**: The macro `GET_P_GAME_ACTION_PAYLOAD_AS_P(p_game_action, GA_TCP_Connect__Delivery)` expands to `((GA_TCP_Connect__Delivery*)&p_game_action->_ga_payload_union)`. This is a pointer cast, not a value copy, so no truncation or conversion occurs. The return type `u8*` is directly the address of the `payload` array member, which is correct.
- **Undefined behavior**: The function performs type punning via a pointer cast on the union member `_ga_payload_union`. In C, accessing a union through a different type than was last written is technically implementation-defined/undefined behavior under strict aliasing rules. However, this is an established and consistent pattern throughout the Lavender codebase for all game action payload accessors, and the `Game_Action` struct uses a union specifically designed for this purpose. The function itself introduces no additional UB beyond what the macro already does.
- **Null dereference**: If `p_game_action` is null, `&p_game_action->_ga_payload_union` dereferences a null pointer, causing undefined behavior. However, this is consistent with the codebase convention — all inline accessor functions in this module assume non-null inputs and do not perform validation. Validation is the caller's responsibility.
- **No out-of-bounds access**: The function returns a pointer to the `payload` array; it does not index into it, so there is no risk of off-by-one or out-of-bounds access within this function itself.

## Side Effects

No side effects. This is a pure accessor function that reads from the `Game_Action` struct and returns a pointer to an internal field. It does not modify any state, allocate memory, or invoke any external operations.
