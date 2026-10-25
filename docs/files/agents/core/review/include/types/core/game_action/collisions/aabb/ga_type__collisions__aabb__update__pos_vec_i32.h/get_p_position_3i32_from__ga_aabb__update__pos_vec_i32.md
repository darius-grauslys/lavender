# get_p_position_3i32_from__ga_aabb__update__pos_vec_i32

**File of origin:** `core/include/types/core/game_action/collisions/aabb/ga_type__collisions__aabb__update__pos_vec_i32.h`

## Semantic

Returns a pointer to the `position__3i32` field within the `GA_AABB__Update__PosVec_I32` payload of the given `Game_Action`.

## Pre-conditions

1. `p_game_action` must be non-null.
2. The `_ga_payload_union` within `p_game_action` must contain a `GA_AABB__Update__PosVec_I32` payload (i.e., the game action's kind must correspond to this payload type). This is the caller's responsibility to ensure.

## Post-conditions

1. Returns a valid `Vector__3i32 *` pointer to the `position__3i32` field within the payload union of `p_game_action`.
2. The returned pointer remains valid for the lifetime of `p_game_action`.

## Correctness Verdict

Correct

## Semantic Alignment

The function correctly accesses the `position__3i32` field from the `GA_AABB__Update__PosVec_I32` payload. The struct `GA_AABB__Update__PosVec_I32` defines `position__3i32` as a `Vector__3i32` member, and the function returns a pointer to it via the `GET_P_GAME_ACTION_PAYLOAD_AS_P` macro, which casts the payload union to the correct type. The implementation faithfully fulfills its semantic intent of providing pointer-level access to the position field.

## Implementation Correctness

- **Type compatibility:** The macro `GET_P_GAME_ACTION_PAYLOAD_AS_P(p_game_action, GA_AABB__Update__PosVec_I32)` expands to `((GA_AABB__Update__PosVec_I32*)&p_game_action->_ga_payload_union)`, which is then dereferenced with `->position__3i32` to obtain a `Vector__3i32` value, and the address-of operator `&` is applied to yield a `Vector__3i32 *`. This matches the declared return type exactly. No implicit conversions or truncation occur.
- **Undefined behavior:** No null dereference occurs within the function itself (null checking is the caller's responsibility, consistent with the codebase pattern). No out-of-bounds access, no type punning violations (the union is explicitly designed for this access pattern). No broken pointer arithmetic.
- **Validation:** The function does not validate that the game action's kind matches `GA_AABB__Update__PosVec_I32`. This is consistent with the codebase design where payload access functions assume the caller has verified the game action kind. Validation of the game action kind is the caller's responsibility.

## Side Effects

No side effects. This is a pure accessor function that returns a pointer to a field within the game action's payload union without modifying any state.
