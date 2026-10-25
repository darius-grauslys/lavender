get_p_gsv_3i32_from__ga_global_space__request — core/include/types/core/game_action/global_space/ga_type__global_space__request.h

Returns a pointer to the `gsv_3i32` field of the `GA_Global_Space__Request` payload within a `Game_Action`.

Pre-conditions:
1. `p_game_action` must be a non-null pointer to a valid `Game_Action` whose `_ga_payload_union` is intended to be interpreted as a `GA_Global_Space__Request`.
2. The caller is responsible for ensuring the `Game_Action` payload union actually holds a `GA_Global_Space__Request` (i.e., the action kind matches).

Post-conditions:
1. Returns a valid `Global_Space_Vector__3i32 *` pointing to the `gsv_3i32` member of the `GA_Global_Space__Request` struct obtained by casting `&p_game_action->_ga_payload_union`.

Correctness Verdict: Correct

Semantic Alignment:
The function correctly accesses the `gsv_3i32` field of `GA_Global_Space__Request`. The macro `GET_P_GAME_ACTION_PAYLOAD_AS_P(p_game_action, GA_Global_Space__Request)` expands to `((GA_Global_Space__Request*)&p_game_action->_ga_payload_union)`, and the function takes the address of the `->gsv_3i32` member. The return type `Global_Space_Vector__3i32 *` matches the field type exactly. The computation matches the semantic intent of returning a pointer to the global space vector.

Implementation Correctness:
Type compatibility — the return type `Global_Space_Vector__3i32 *` matches the type of the `gsv_3i32` field in `GA_Global_Space__Request`. No implicit conversions or truncation.
No undefined behavior — no broken pointer arithmetic, no null dereference (the macro performs a cast and member access, not a dereference of `p_game_action` itself), no type punning beyond the union reinterpretation pattern used throughout the codebase, no out-of-bounds access.
No validation is performed — this is consistent with all other accessor functions in this file (e.g., `get_gsv_3i32_from__ga_global_space__request`, `get_p_tcp_payload_bitmap_u8_from__ga_global_space__request`, etc.). Validation of the pointer and payload kind is the caller's responsibility.

Side Effects:
No side effects — the function is a pure accessor that reads the address of a struct field without modifying any state.
