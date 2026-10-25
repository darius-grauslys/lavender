# Function Review: dispatch_game_action_to__server

## 1. Header
- **Function name**: `dispatch_game_action_to__server`
- **File of origin**: `core/include/game.h`

## 2. Semantic
A thin dispatch wrapper that resolves the local client (server-side client slot 0 representing the local player) and forwards the game action to the Game's installed `m_game_action_handler__dispatch` callback, returning its boolean result.

## 3. Pre-conditions
1. `p_game` must be a non-null pointer to an initialized Game object. It is dereferenced directly (no null guard) to read `p_game->m_game_action_handler__dispatch` and to pass as the dispatch handler's first argument.
2. `p_game->m_game_action_handler__dispatch` must be non-null (installed by `begin_multiplayer_for__game` / default hooks). Calling through a NULL function pointer is undefined behavior; no guard is performed here.
3. `p_game_action` must be a non-null, valid pointer to a `Game_Action`. `Game_Action` is an opaque struct type; the caller is responsible for its validity. It is forwarded to the handler without validation.
4. The local client may legitimately be NULL: `get_p_local_client_by__from__game` returns NULL when `p_game->pM_ptr_array_of__clients` is NULL (no client pool allocated, e.g. a non-client/server-only context). Whether a NULL `Client*` is acceptable is the dispatch handler's contract, not this wrapper's.
5. `p_game->pM_ptr_array_of__clients` is not dereferenced directly by this wrapper (`get_p_local_client_by__from__game` guards it internally), so no additional constraint is required; the first client slot `[0]` is simply used when present.

## 4. Post-conditions
1. Returns the `bool` result produced by `p_game->m_game_action_handler__dispatch(p_game, local_client, p_game_action)`.
2. Any mutation of game state, the client, or the action is performed by the dispatch handler (a callee); this function itself leaves no state it directly owns (it only reads the handler field and the local-client pointer).

## 5. Correctness Verdict
**Correct**

## 6. Semantic Alignment
The implementation fulfills its intent exactly: it resolves the local client via `get_p_local_client_by__from__game` (the server-side client slot 0 representing the local player) and delegates `(game, local_client, action)` to the Game's `m_game_action_handler__dispatch` callback, returning its result. There is no computation to drift from — it is a pure lookup-and-dispatch delegation, dispatching exactly what was asked with no reordering, no omission, and no extra transformation. The difference from its sibling `dispatch_game_action` is the client source (local slot 0 vs. uuid lookup), which correctly encodes the "to the server/local player" intent.

## 7. Implementation Correctness
- **Type compatibility**: every type lines up exactly. `p_game` is `Game*` matching the handler's first parameter; the `Client*` returned by `get_p_local_client_by__from__game` matches the handler's second parameter `Client*`; `p_game_action` is `Game_Action*` matching the handler's third parameter. The field `m_game_action_handler__dispatch` has type `m_Game_Action_Handler = bool (*)(Game *, Client *, Game_Action *)` (defines.h:2535), and the call's three arguments match that signature, with the boolean return propagated directly. No implicit conversions or truncation.
- **Undefined behavior**: none within this function itself. No pointer arithmetic; no null dereference of `p_game_action` or the returned client (both are merely passed through, not dereferenced here). The only dereferences are `p_game->m_game_action_handler__dispatch` (covered by the non-null-handler pre-condition) and the call to `get_p_local_client_by__from__game` (which guards `pM_ptr_array_of__clients` internally and returns NULL when absent). `get_p_local_client_by__from__game` may return NULL, which is forwarded to the handler without validation — acceptable for a thin dispatch wrapper whose handler owns the NULL-Client contract.
- **Validation**: none is performed here (no check that the handler is set, no null client guard, no action validation). This matches the codebase pattern — `dispatch_game_action` and `receive_game_action` are identical thin wrappers — and validation is the caller's / handler's responsibility at this layer.

## 8. Side Effects
No direct side effects of its own. The function reads `p_game->m_game_action_handler__dispatch` and invokes it; any state changes produced by the dispatch handler are callee side effects and out of scope for this review.
