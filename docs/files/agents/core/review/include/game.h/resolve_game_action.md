# resolve_game_action

**File of origin:** `core/include/game.h`

## Semantic

Resolves a game action for a specific client by looking up the client via its UUID and delegating to the game's registered `m_game_action_handler__resolve` handler function pointer. Returns the handler's boolean result indicating success or failure.

## Pre-conditions

1. `p_game` must be non-null. The function dereferences `p_game` to access `m_game_action_handler__resolve` without null-checking; a null `p_game` causes undefined behavior.
2. `p_game->m_game_action_handler__resolve` must be a non-null function pointer. If uninitialized, calling through it is undefined behavior.
3. `uuid_of__client__u32` should correspond to a valid, allocated client in the game's client pool. If no client matches the UUID, `get_p_client_by__uuid_from__game` returns NULL; this NULL is passed through to the handler without validation.
4. `p_game_action` should be non-null and point to a valid `Game_Action` struct. No null-checking is performed on this parameter within the function.
5. The client pool (`p_game->pM_clients`) must be allocated; otherwise `get_p_client_by__uuid_from__game` returns NULL and logs a debug warning.

## Post-conditions

1. Returns a `bool` — the result of invoking `p_game->m_game_action_handler__resolve(p_game, p_client, p_game_action)`, where `p_client` is the result of `get_p_client_by__uuid_from__game(p_game, uuid_of__client__u32)`.
2. No direct mutation of `Game` state occurs within this function itself; any side effects are produced by the handler to which it delegates.
3. If the client lookup fails (returns NULL), the handler receives a NULL `Client *` — the behavior in that case is entirely determined by the handler implementation.

## Correctness Verdict

**Correct**

## Semantic Alignment

The implementation correctly fulfills its semantic intent as a thin dispatch wrapper. It performs a client UUID lookup and forwards the game, resolved client pointer, and action to the `m_game_action_handler__resolve` function pointer. This is consistent with the sibling functions `dispatch_game_action` and `receive_game_action`, which follow the identical pattern using `m_game_action_handler__dispatch` and `m_game_action_handler__receive` respectively. No computation or struct initialization is performed, so there is no risk of semantic drift in field assignment or reordering.

## Implementation Correctness

- **Type compatibility:** All types match exactly. `p_game` (`Game *`) matches the handler's first parameter (`Game *p_this_game`). `get_p_client_by__uuid_from__game` returns `Client *`, matching the handler's second parameter (`Client *p_client`). `p_game_action` (`Game_Action *`) matches the handler's third parameter (`Game_Action *p_game_action`). The return type `bool` matches the handler's return type. No implicit conversions or truncation occur.
- **Undefined behavior:** No null dereference of `p_game` or `p_game->m_game_action_handler__resolve` occurs if the caller upholds the pre-conditions. Passing a potentially NULL `Client *` to the handler is not itself undefined behavior — it is a valid pointer value that the handler may choose to handle or reject.
- **Validation:** Validation of the client lookup result (NULL check) and of `p_game_action` is intentionally deferred to the handler implementation. This is consistent with the sibling dispatch functions (`dispatch_game_action`, `receive_game_action`), all of which follow the same no-check pattern. The function's role is purely as an inline dispatcher, so this level of validation is appropriate for its role.

## Side Effects

No direct side effects from this function itself. It does not modify any `Game` state or any other observable state. It reads `p_game->m_game_action_handler__resolve` and calls `get_p_client_by__uuid_from__game`, then delegates entirely to the handler function pointer. Any side effects (e.g., game state mutation, logging, network I/O) are produced by the handler to which this function delegates — those are out of scope for this review.
