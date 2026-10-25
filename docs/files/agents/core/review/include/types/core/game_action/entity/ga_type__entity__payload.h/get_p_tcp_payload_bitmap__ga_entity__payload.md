get_p_tcp_payload_bitmap__ga_entity__payload — core/include/types/core/game_action/entity/ga_type__entity__payload.h

Returns a pointer to the `tcp_payload_bitmap` field within the `GA_Entity__Payload` member of the `Game_Action`'s payload union.

Pre-conditions:
1. `p_game_action` must be a non-null pointer to a valid, writable `Game_Action` object.
2. The `_ga_payload_union` member must be interpreted as (or contain) a `GA_Entity__Payload` variant; i.e., the caller must ensure the game action's payload type is `GA_Entity__Payload`. This is the caller's responsibility — no runtime type checking is performed.

Post-conditions:
1. Returns a `u8 *` pointer to the `tcp_payload_bitmap` array inside the `GA_Entity__Payload` struct, obtained by casting the `_ga_payload_union` to `GA_Entity__Payload *` and accessing the `tcp_payload_bitmap` field.
2. No mutation of the `Game_Action` or any other state occurs.

Correctness Verdict: Correct

Semantic Alignment:
The function correctly retrieves a pointer to the `tcp_payload_bitmap` field of the `GA_Entity__Payload` struct embedded in the `_ga_payload_union`. The macro `GET_P_GAME_ACTION_PAYLOAD_AS_P(p_game_action, GA_Entity__Payload)` casts `&p_game_action->_ga_payload_union` to `GA_Entity__Payload *`, and then `->tcp_payload_bitmap` accesses the `u8` array field. The `tcp_payload_bitmap` field is declared via the `TCP_PAYLOAD_BITMAP` macro as `u8 tcp_payload_bitmap[TCP_PAYLOAD_BITMAP__QUANTITY_OF__PAYLOADS(GA_Entity__Payload)]`, which is an array of `u8`. Since arrays decay to `u8 *` when accessed as a member through `->`, the return type `u8 *` is correct. The implementation matches the semantic intent exactly.

Implementation Correctness:
Type compatibility — `p_game_action` is `Game_Action *`, matching the macro parameter; the macro returns `GA_Entity__Payload *`, and `->tcp_payload_bitmap` yields `u8 *` (array-to-pointer decay), which matches the return type `u8 *`. No implicit conversions or truncation.
Undefined behavior — the only concern would be if `p_game_action` is null or if the union is not actually holding a `GA_Entity__Payload` variant, but both are caller responsibilities. The function itself performs no pointer arithmetic, no null dereference, no type punning, and no out-of-bounds access.
Validation — no validation is performed, which is appropriate for a low-level accessor. The caller is responsible for ensuring `p_game_action` is valid and that the payload type is correct.

Side Effects:
No side effects. The function is a pure accessor — it reads the address of a struct field and returns it without modifying any state.
