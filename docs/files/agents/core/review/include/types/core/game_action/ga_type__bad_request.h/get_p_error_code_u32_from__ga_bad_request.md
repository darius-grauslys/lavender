# get_p_error_code_u32_from__ga_bad_request

**File of origin:** `core/include/types/core/game_action/ga_type__bad_request.h`

## Semantic

Returns a pointer to the `error_code__u32` field within the `GA_Bad_Request` payload union of a `Game_Action`.

## Pre-conditions

1. `p_game_action` must be non-null.
2. The caller must ensure that the `Game_Action`'s payload union is currently holding a `GA_Bad_Request` payload (i.e., the game action kind corresponds to a bad request). Accessing the payload as `GA_Bad_Request` when it holds a different type is undefined behavior.

## Post-conditions

1. Returns a valid `u32*` pointer to the `error_code__u32` field within the `GA_Bad_Request` struct embedded in `p_game_action->_ga_payload_union`.
2. The returned pointer remains valid for the lifetime of the `Game_Action` object.
3. No state is modified; the function is a pure accessor.

## Correctness Verdict

**Correct**

## Semantic Alignment

The implementation fulfills the semantic intent. The function uses the `GET_P_GAME_ACTION_PAYLOAD_AS_P` macro to cast the `_ga_payload_union` field of `Game_Action` to a `GA_Bad_Request*`, then takes the address of the `error_code__u32` member. The `GA_Bad_Request` struct contains exactly one field (`uint32_t error_code__u32`), and the function correctly accesses it. The return type `u32*` is type-compatible with `uint32_t*` (since `u32` is a typedef for `uint32_t`).

## Implementation Correctness

- **Type compatibility:** The macro `GET_P_GAME_ACTION_PAYLOAD_AS_P(p_game_action, type)` expands to `((type*)&p_game_action->_ga_payload_union)`. With `type = GA_Bad_Request`, this yields a `GA_Bad_Request*`. Accessing `->error_code__u32` yields a `uint32_t`, and taking its address yields a `uint32_t*`, which is returned as `u32*`. Since `u32` is defined as `typedef uint32_t u32`, the types are identical — no implicit conversion or truncation occurs.
- **Undefined behavior:** No null dereference, no out-of-bounds access, no type punning beyond the union access (which is the intended design of the `_ga_payload_union`). The function does not validate that `p_game_action` is non-null, but this is consistent with the codebase's pattern where null-checking is the caller's responsibility for inline accessors.
- **Validation:** No validation is performed, which is appropriate for this low-level inline accessor. The caller is responsible for ensuring the payload type matches.

## Side Effects

No side effects. This is a pure accessor function that reads from and returns a pointer into the `Game_Action`'s payload union without modifying any state.
