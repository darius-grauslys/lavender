get_p_log__global_from__game — core/include/game.h

Returns a pointer to the global Log component embedded in the given Game.

Pre-conditions:
1. p_game must be a non-null pointer to a valid, fully-constructed Game object. The function dereferences p_game (member access `&p_game->log__global`), so a NULL p_game is undefined behavior.
2. No other parameter constraints — the function takes a single argument.

Post-conditions:
1. Returns a valid `Log *` referring to the `log__global` member of the Game pointed to by p_game. The pointer is the in-place address of an embedded (not heap-allocated) field, so it remains valid for the lifetime of the Game object.
2. No state is read or written by this function; the returned pointer grants mutable access to log__global to subsequent callers.

Correctness Verdict: Correct

Semantic Alignment:
The function's purpose is to expose the global log of a Game. Returning `&p_game->log__global` directly fulfills that intent. The Game struct declares `Log log__global` as a member (defines.h:2557), so the returned pointer is well-typed and refers to the correct subobject. No semantic drift or missing field.

Implementation Correctness:
Type compatibility — the return type `Log *` matches the type of `&p_game->log__global` exactly (Log field → Log *). The parameter `Game *` matches the struct containing the field. No implicit conversions or truncation.
Undefined behavior — the only hazard is dereferencing p_game when it is NULL; for a NULL pointer, `&p_game->log__global` is undefined behavior. There is no pointer arithmetic, no type punning, no array/out-of-bounds access.
Validation — no validation is performed and none is warranted for a low-level `static inline` accessor of this class; ensuring p_game is valid is the caller's responsibility, consistent with sibling accessors in this header (e.g. `get_p_log__local_from__game`, `get_p_log__local_from__game`).

Side Effects:
No side effects — the function is a pure accessor. It performs no reads of field contents and no writes of any kind; its sole observable effect is computing and returning an address derived from the input pointer.
