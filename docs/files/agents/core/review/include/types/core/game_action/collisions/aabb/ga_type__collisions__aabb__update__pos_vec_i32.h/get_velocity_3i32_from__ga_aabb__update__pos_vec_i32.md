# get_velocity_3i32_from__ga_aabb__update__pos_vec_i32

## File of Origin
core/include/types/core/game_action/collisions/aabb/ga_type__collisions__aabb__update__pos_vec_i32.h

## Semantic
Retrieves the velocity component (a `Vector__3i32`) stored in the payload of a `Game_Action` whose union payload is interpreted as a `GA_AABB__Update__PosVec_I32`.

## Pre-conditions
1. `p_game_action` must be a non-null pointer to a valid `Game_Action` instance.
2. The `_ga_payload_union` member of the pointed-to `Game_Action` must currently hold a `GA_AABB__Update__PosVec_I32` payload (i.e., the caller is responsible for ensuring the union is populated with the correct type before calling this accessor).

## Post-conditions
1. Returns a copy of the `velocity__3i32` field (of type `Vector__3i32`) from the `GA_AABB__Update__PosVec_I32` payload.
2. The original `Game_Action` and its payload are not modified.

## Correctness Verdict
Correct

## Semantic Alignment
The implementation fulfills its semantic intent. The function uses the `GET_P_GAME_ACTION_PAYLOAD_AS_P` macro to cast the `_ga_payload_union` to a `GA_AABB__Update__PosVec_I32*` pointer, then accesses the `->velocity__3i32` member and returns it by value. The struct `GA_AABB__Update__PosVec_I32` has exactly two fields — `position__3i32` and `velocity__3i32` — both of type `Vector__3i32`. The function correctly accesses the intended field without any omission or reordering.

## Implementation Correctness
- **Type compatibility**: The return type `Vector__3i32` matches the type of the `velocity__3i32` field exactly. No implicit conversions or truncation occur.
- **Undefined behavior**: No null dereference is guarded against (no null check on `p_game_action`), but this is consistent with the codebase pattern — all sibling accessor functions (`get_position_3i32_from__ga_aabb__update__pos_vec_i32`, `get_p_position_3i32_from__ga_aabb__update__pos_vec_i32`, `get_p_velocity_3i32_from__ga_aabb__update__pos_vec_i32`) follow the same convention of relying on the caller to provide a valid pointer. No pointer arithmetic beyond the union cast is performed. No out-of-bounds access occurs.
- **Validation**: No validation is performed within this function; this is appropriate for a lightweight accessor. Validation of the game action kind and payload type is the caller's responsibility, consistent with the engine's design pattern.

## Side Effects
No side effects. This is a pure accessor function that reads from the `Game_Action` payload union and returns a copy of the velocity field by value. No state is mutated.
