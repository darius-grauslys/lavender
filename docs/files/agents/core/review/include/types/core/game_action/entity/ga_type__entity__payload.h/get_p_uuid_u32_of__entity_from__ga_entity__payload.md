get_p_uuid_u32_of__entity_from__ga_entity__payload — core/include/types/core/game_action/entity/ga_type__entity__payload.h

Returns a pointer to the `uuid_of__entity__u32` field of the `GA_Entity__Payload` payload within a `Game_Action`.

Pre-conditions:
1. `p_game_action` must be a non-null pointer to a valid, accessible `Game_Action` struct.
2. The caller is responsible for ensuring that the `_ga_payload_union` is currently holding the `GA_Entity__Payload` variant (union type safety is the caller's responsibility; this is an unchecked union access).

Post-conditions:
1. Returns a non-null pointer to the `uuid_of__entity__u32` field (`Identifier__u32`, i.e. `uint32_t`) within the `GA_Entity__Payload` struct, reinterpreted through `p_game_action->_ga_payload_union`.
2. The returned pointer points to memory within the `Game_Action` struct — no copy is made.

Correctness Verdict: Correct

Semantic Alignment:
The implementation correctly accesses the `uuid_of__entity__u32` field of the `GA_Entity__Payload` struct. The macro `GET_P_GAME_ACTION_PAYLOAD_AS_P(p_game_action, GA_Entity__Payload)` expands to `((GA_Entity__Payload*)&p_game_action->_ga_payload_union)`, casting the address of the union to a `GA_Entity__Payload*`. The `->uuid_of__entity__u32` accesses the target field, and the leading `&` takes its address, producing an `Identifier__u32*`. This matches the semantic intent of returning a pointer to the entity UUID field.

Implementation Correctness:
Type compatibility — the return type `Identifier__u32 *` matches the type of `&uuid_of__entity__u32` exactly (the field is declared as `Identifier__u32 uuid_of__entity__u32`). No implicit conversions or truncation.
No undefined behavior — no pointer arithmetic, no out-of-bounds access. The macro performs a valid cast of the union's address. The only UB risk would arise if the caller passes a null pointer or if the union is not holding the `GA_Entity__Payload` variant, but that is the caller's responsibility.
No validation is needed — this is a low-level inline accessor. Validation of `p_game_action` and union variant is the caller's responsibility.

Side Effects:
No side effects — this is a pure accessor function. It does not modify any state; it only returns a pointer into the `Game_Action` struct.
