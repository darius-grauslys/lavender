clear_log__local — core/include/game.h

Resets the local game log to its initial empty state and signals the platform layer to clear the corresponding local log display.

Pre-conditions:
1. p_game must be a non-null, valid pointer to a writable Game object.
2. log__local is an inline (embedded) member of Game, so no additional pointer validity check is required beyond p_game being valid.

Post-conditions:
1. p_game->log__local is reset to its initial empty state: all 32 embedded Message slots are re-initialized (title/body buffers zeroed, serialization header set to IDENTIFIER__UNKNOWN__u32, lengths and body index set to 0), p_oldest_message is set to NULL, and p_next_message is set to point to messages[0].
2. The platform layer is notified to clear the local log display via PLATFORM_clear_log__local; however, its bool return value is ignored by this caller, so no success of that platform side effect is guaranteed.

Correctness Verdict: Correct

Semantic Alignment:
The implementation fulfills its semantic intent. It correctly obtains the local Log pointer via get_p_log__local_from__game (which returns &p_game->log__local) and delegates to clear_log, which performs a Lavender-style initialization (pool cleanup) by calling initialize_log — resetting the struct to initial conditions rather than acquiring resources. The platform hook PLATFORM_clear_log__local is then invoked to clear the on-screen local log display, consistent with the sibling clear_log__global and clear_log__system functions.

Lavender-specific note: Although the function name says "clear", it delegates to clear_log -> initialize_log, which is a Lavender-style initialization (pool cleanup / reset to default state), NOT RAII resource acquisition.

Implementation Correctness:
Type compatibility — get_p_log__local_from__game returns Log *, matching clear_log's Log * parameter; p_game is Game *, matching PLATFORM_clear_log__local's Game * parameter. No implicit conversions or truncation.
Undefined behavior — no pointer arithmetic, no null dereference, no type punning, no out-of-bounds access within this function. initialize_log writes to p_log->messages[0] via p_next_message and zeroes p_oldest_message; all are valid because messages is an inline array within the Log struct. Null-checking of p_game is omitted, but this matches the codebase convention for low-level static inline functions where caller responsibility is assumed.
Validation — no validation is performed, which is appropriate for this low-level wrapper; the caller is responsible for ensuring p_game is valid.

Side Effects:
Mutates p_game->log__local (resets all 32 Message slots and the p_oldest_message / p_next_message pointers) and triggers an external platform-level side effect via PLATFORM_clear_log__local (e.g., clearing the on-screen local log display on the active platform).
