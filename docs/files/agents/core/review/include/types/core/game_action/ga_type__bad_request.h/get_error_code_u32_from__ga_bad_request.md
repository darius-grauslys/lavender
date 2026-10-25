get_error_code_u32_from__ga_bad_request — core/include/types/core/game_action/ga_type__bad_request.h

Retrieves the error code (uint32_t) from a GA_Bad_Request game action's payload union.

Pre-conditions:
1. p_game_action must be a non-null pointer to a valid, initialized Game_Action struct.
2. The _ga_payload_union member of *p_game_action must currently hold a GA_Bad_Request payload (i.e., the game action's kind must be Game_Action_Kind__Bad_Request). Accessing the wrong payload type is undefined behavior and is the caller's responsibility to ensure.

Post-conditions:
1. Returns the value of error_code__u32 (a uint32_t) from the GA_Bad_Request struct accessed through the _ga_payload_union.

Correctness Verdict: Correct

Semantic Alignment:
The function correctly retrieves the single field (error_code__u32) from the GA_Bad_Request struct. The GET_P_GAME_ACTION_PAYLOAD_AS_P macro casts &p_game_action->_ga_payload_union to a GA_Bad_Request* pointer, and the ->error_code__u32 member access reads the correct field. The struct GA_Bad_Request has exactly one field and it is accessed correctly.

Implementation Correctness:
Type compatibility — u32 (defined as typedef uint32_t u32 in defines_weak.h) matches the field type uint32_t error_code__u32 exactly. No implicit conversions or truncation.
No undefined behavior — no pointer arithmetic, no null dereference (assuming pre-conditions are met), no out-of-bounds access. The union access via cast is valid in C; the macro performs a reinterpret_cast of the union address to GA_Bad_Request*, which is the established pattern for accessing typed payloads in this engine.
No validation is performed — this is consistent with the function's role as a low-level accessor. The caller is responsible for ensuring p_game_action is valid and that the payload type matches.

Side Effects:
No side effects — this is a pure read accessor that returns a uint32_t value without modifying any state.
