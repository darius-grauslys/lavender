# get_p_position_3i32F4_from__ga_aabb__update__pos_vec_i32F4

**File of origin:** `core/include/types/core/game_action/collisions/aabb/ga_type__collisions__aabb__update__pos_vec_i32F4.h`

## Semantic
Returns a pointer to the `position__3i32F4` field within the `GA_AABB__Update__PosVec_I32F4` payload of a given `Game_Action`. This is an accessor function that provides mutable access to the position component of an AABB collision update action.

## Pre-conditions
1. `p_game_action` must be a non-null pointer to a valid `Game_Action` struct.
2. The `Game_Action`'s payload union (`_ga_payload_union`) must be initialized as (or interpreted as) a `GA_AABB__Update__PosVec_I32F4` type. The macro `GET_P_GAME_ACTION_PAYLOAD_AS_P` performs an unchecked cast, so the caller is responsible for ensuring type compatibility.
3. The `Game_Action` must have its `_ga_payload_union` populated, though no runtime validation of this is performed by the function.

## Post-conditions
1. Returns a valid `Vector__3i32F4 *` pointer to the `position__3i32F4` field within the payload union of `p_game_action`.
2. The returned pointer references internal data of `p_game_action`; no copy is made.
3. No side effects are produced; the function does not modify any state.

## Correctness Verdict
Correct

## Semantic Alignment
The implementation correctly fulfills its semantic intent: it casts the payload union of the `Game_Action` to a `GA_AABB__Update__PosVec_I32F4 *` and returns a pointer to the `position__3i32F4` member. The struct layout is well-defined, and the field access is direct and unambiguous. There is no reordering or omission of fields in this accessor; it simply exposes an existing field.

## Implementation Correctness
- **Type compatibility:** The macro `GET_P_GAME_ACTION_PAYLOAD_AS_P` casts `p_game_action->_ga_payload_union` to `(GA_AABB__Update__PosVec_I32F4 *)`. This is a type-punning operation via a union, which is explicitly supported by the engine's design (the `_ga_payload_union` is intended to hold various game action payload types). The return type `Vector__3i32F4 *` matches the field type exactly.
- **Undefined behavior:** The macro performs an unchecked cast. If the actual payload type differs from `GA_AABB__Update__PosVec_I32F4`, this results in undefined behavior. However, this is by design — the engine relies on callers to ensure correct payload typing, consistent with a tagged union pattern where the tag (Game_Action_Kind) is checked externally.
- **Null dereference:** If `p_game_action` is null, dereferencing it inside the macro will cause undefined behavior. This is acceptable for an inline accessor; validation is the caller's responsibility.
- **Validation:** No validation is performed within this function. This is appropriate for a low-level inline accessor; callers must ensure pre-conditions are met.

## Side Effects
No side effects. The function is a pure accessor that returns a pointer to internal data without modifying any state.
