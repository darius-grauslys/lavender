get_raw_uuid_u32_of__player_from__game_session_token — core/include/game.h, lines 314-317

Composes two calls to extract the raw u32 player identifier from a Game's session token: it retrieves the Session_Token from the Game and compresses its player UUID from u64 to u32.

Pre-conditions:
1. p_game must be a non-null pointer to a valid (initialized) Game object.
2. The Game's session_token field must hold a meaningful value (i.e., the Game has been initialized and the session token is set).

Post-conditions:
1. Returns an Identifier__u32 representing the raw compressed player UUID.
2. The returned value may differ from the uuid determined through TCP connection, as the server may assign its own u32 uuid during u64->u32 uuid compression (per the doc comment on lines 307-312).
3. No state is mutated; the Game and its session_token are read but not modified.

Correctness Verdict: Correct

Semantic Alignment:
The implementation fulfills the semantic intent. It calls get_session_token_from__game(p_game) to obtain the Game's Session_Token (which returns p_game->session_token), then passes that Session_Token to get_uuid_u32_of__session_token_player_uuid_u64, which compresses the player_uuid (a u64) to a branded u32 Identifier. The delegation chain matches the function's stated purpose exactly.

Implementation Correctness:
Type compatibility — p_game is Game *; get_session_token_from__game accepts Game * and returns Session_Token; get_uuid_u32_of__session_token_player_uuid_u64 accepts Session_Token (by value) and returns Identifier__u32. Every type matches exactly with no implicit conversions or truncation at this level.
No undefined behavior — this is a pure read-and-delegate function. There is no pointer arithmetic, no null dereference within this function (the non-null requirement on p_game is a pre-condition), no type punning, and no out-of-bounds access.
No validation is needed — this is a low-level inline accessor that composes two other accessors. The caller is responsible for ensuring p_game is valid, consistent with the codebase convention that low-level accessors defer validation to callers.

Side Effects:
No side effects — the function performs only reads (accessing p_game->session_token via get_session_token_from__game) and computation delegated to get_uuid_u32_of__session_token_player_uuid_u64. No state is mutated.
