clear_log__system — core/include/game.h

Clears the system log of a Game instance by resetting the Log struct to its initial conditions, then delegates to the platform backend to clear the platform-level system log display.

Pre-conditions:
1. p_game must be a non-null pointer to a valid, writable Game object. The function dereferences p_game without null-checking (via get_p_log__system_from__game), so a null p_game produces undefined behavior.
2. The Game struct's log__system member must be a valid Log struct (it is a direct embedded member, not a pointer, so it is always present when p_game is valid).
3. The backend must provide an implementation of PLATFORM_clear_log__system(Game *) that accepts p_game (or gracefully handles a null PLATFORM_gfx_context).
4. The platform-level system log rendering state must be in a state that permits clearing (e.g., not mid-render). This is the caller's responsibility to ensure.

Post-conditions:
1. The p_game->log__system Log struct is mutated to its initial conditions: all 32 messages are re-initialized, p_oldest_message is set to NULL, and p_next_message is set to point to messages[0].
2. The platform backend is invoked with p_game to clear the platform-level system log display/rendering state. The return value of PLATFORM_clear_log__system is intentionally discarded.

Correctness Verdict: Correct

Semantic Alignment:
The function correctly fulfills its semantic intent. It first clears the core Log struct (via clear_log -> initialize_log) and then calls the platform-specific counterpart to clear the backend's representation. This mirrors the pattern used by the sibling functions clear_log__global and clear_log__local, ensuring consistency across all three log types. No semantic drift is present.

Lavender-specific note: Although the function name says "clear", it delegates to clear_log -> initialize_log, which is a Lavender-style initialization (pool cleanup / reset to default state), NOT RAII resource acquisition.

Implementation Correctness:
- Type compatibility — p_game is passed as Game * to both get_p_log__system_from__game (which accepts Game * and returns Log *) and PLATFORM_clear_log__system (which accepts Game *). Types match exactly with no implicit conversions or truncation. The return type of PLATFORM_clear_log__system (bool) is discarded, which is intentional and consistent with the sibling functions.
- Undefined behavior — no pointer arithmetic, no type punning, no out-of-bounds access within this function. The only dereference is &p_game->log__system inside get_p_log__system_from__game, which is safe as long as p_game is non-null (a caller responsibility). The initialize_log callee iterates over messages[0..31] using a strict less-than comparison (index < MESSAGE_MAX_QUANTITY_OF), so no out-of-bounds access occurs there.
- Validation — no validation is performed, which is appropriate for this thin inline wrapper. This follows the established Lavender convention: simple accessor/wrapper functions in game.h do not validate p_game. Callers are responsible for passing a valid Game pointer.

Side Effects:
1. Mutates p_game->log__system: all 32 messages within the Log's messages array are reset, p_oldest_message is set to NULL, and p_next_message is set to point to messages[0] (via initialize_log called through clear_log).
2. Invokes PLATFORM_clear_log__system(p_game), which performs a platform-dependent side effect to clear the platform-level system log display/rendering state (return value discarded).
