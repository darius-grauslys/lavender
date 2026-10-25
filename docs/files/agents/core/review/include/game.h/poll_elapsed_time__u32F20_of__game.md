poll_elapsed_time__u32F20_of__game — core/source/game.c

Accumulates platform-reported elapsed time into the Game's elapsed time field and returns the updated total.

Pre-conditions:
1. p_game must be a non-null pointer to a valid, initialized Game struct.
2. p_game->time__seconds__u32 must be a properly initialized Timer__u32 (initialized in initialize_game with initialize_timer_u32).
3. p_game->time__nanoseconds__u32 must be a properly initialized Timer__u32 (initialized in initialize_game with initialize_timer_u32).
4. p_game->time_elapsed__u32F20 must be a valid u32F20 accumulator (initialized to 0 in initialize_game).

Post-conditions:
1. p_game->time_elapsed__u32F20 is incremented by the value returned from PLATFORM_get_time_elapsed, which represents the elapsed time since the last poll.
2. The return value is the updated p_game->time_elapsed__u32F20.
3. The internal platform timers (time__seconds__u32 and time__nanoseconds__u32) are updated by PLATFORM_get_time_elapsed to reflect the consumption of elapsed time.

Correctness Verdict: Correct

Semantic Alignment:
The function fulfills its semantic intent: it polls the platform for elapsed time and accumulates it into the game's elapsed time field. The "poll" prefix (as opposed to "init") indicates this is a query-and-accumulate operation, consistent with other "poll" functions in the engine (e.g., poll__game_tick_timer, poll_multiplayer, poll_input). This is NOT an initialization function; it does not reset or clean up the struct to initial conditions.

The computation correctly adds the platform-reported elapsed time to the accumulator and returns the result. The function is called by poll__game_tick_timer and its result is used in tick accumulation logic. reset__game_tick_timer resets time_elapsed__u32F20 to 0 after each frame, establishing the expected poll-reset cycle.

Implementation Correctness:
Type compatibility — PLATFORM_get_time_elapsed returns u32F20, which matches the type of p_game->time_elapsed__u32F20 (u32F20). The function parameters are Timer__u32 *, which matches p_game->time__seconds__u32 and p_game->time__nanoseconds__u32 (both Timer__u32). No implicit conversions or truncation.
No undefined behavior — no pointer arithmetic, no null dereference (caller responsibility), no type punning, no out-of-bounds access. The function dereferences p_game, which is expected to be non-null per the engine's convention (consistent with other functions in game.c that do not null-check p_game).
No validation is performed — this is consistent with the engine's pattern where low-level functions assume a valid Game pointer. The caller is responsible for ensuring p_game is initialized.

Side Effects:
Mutates p_game->time_elapsed__u32F20 by accumulating elapsed time from the platform. Additionally, PLATFORM_get_time_elapsed may update the internal state of p_game->time__seconds__u32 and p_game->time__nanoseconds__u32 timers to consume the elapsed time so it is not double-counted on subsequent polls.
