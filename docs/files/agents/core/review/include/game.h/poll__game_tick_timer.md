poll__game_tick_timer — core/source/game.c

Returns the number of elapsed game ticks since the last `reset__game_tick_timer` call, by refreshing the per-frame elapsed time, adding it to the F20 tick accumulator, and right-shifting by 15 to convert from 2^20 sub-units-per-second to 32 ticks-per-second granularity. Declared in core/include/game.h.

Pre-conditions:
1. `p_game` must be a non-null pointer to a valid `Game` object.
2. `p_game` must point to writable memory — this is required because the function calls `poll_elapsed_time__u32F20_of__game(p_game)`, which mutates `p_game->time_elapsed__u32F20` (unlike a pure read-only getter).
3. `tick_accumilator__u32F20` must have been initialized to a meaningful value. `initialize_game()` zero-inits the `Game` struct; `reset__game_tick_timer` (game.c:641) preserves only the sub-tick remainder after each frame, so the accumulator stays bounded (< 2^15 sub-units) at every call.
4. `time__seconds__u32` and `time__nanoseconds__u32` are passed to `PLATFORM_get_time_elapsed` by the callee; their prior state must be valid per the platform layer (set by prior `PLATFORM_get_time_elapsed` calls or zero-initialized).

Post-conditions:
1. Returns a `Quantity__u32` (uint32_t) equal to `(p_game->tick_accumilator__u32F20 + p_game->time_elapsed__u32F20) >> 15`.
2. `p_game->time_elapsed__u32F20` is mutated — the platform-reported elapsed time for the current poll is added to it (side effect of the `poll_elapsed_time__u32F20_of__game` call).
3. `p_game->tick_accumilator__u32F20` is NOT modified by this function (only `reset__game_tick_timer` modifies it).
4. `tick_accumilator__u32F20` and all other `Game` fields except `time_elapsed__u32F20` are left unchanged.

Correctness Verdict: Correct

Semantic Alignment:
The implementation matches the engine's documented tick-timing semantics (agents/core/modules/engine.md:12: "poll__game_tick_timer() returns (tick_accumilator + time_elapsed) >> 15 (32 ticks/sec)"). It refreshes `time_elapsed__u32F20` via `poll_elapsed_time__u32F20_of__game`, then adds the F20 accumulator and right-shifts by 15, converting the fixed-point accumulator (2^20 sub-units/sec) to tick granularity (2^5 = 32 ticks/sec). The `(void)` cast discarding the callee's return value is intentional: the purpose of the call is its side effect (accumulating platform elapsed time), not its return value. This differs from the pure read-only `get_elapsed_ticks__u32F20_of__game` (game.h:413) which queries only the persisted accumulator without refreshing elapsed time — consistent with the Lavender "poll" (side-effecting read) vs "get" (pure read) naming convention. The implementation fulfills its semantic intent.

Implementation Correctness:
Type compatibility — `tick_accumilator__u32F20` and `time_elapsed__u32F20` are both `u32F20` (typedef uint32_t, defines_weak.h:43); the expression `(u32F20 + u32F20) >> 15` yields uint32_t; the return type is `Quantity__u32` (typedef uint32_t, defines_weak.h:49). The underlying types match exactly — no implicit conversions or truncation.
Undefined behavior — no pointer arithmetic, no null dereference (null-checking is the caller's responsibility, consistent with all `game.c` functions), no type punning, no out-of-bounds access. The right-shift amount 15 is within [0, 31] for a uint32_t left operand, and the left operand is unsigned, so the shift is well-defined per the C standard.
Validation — no validation is needed; this is a low-level struct accessor consistent with the engine's conventions. The caller is responsible for ensuring `p_game` is valid.
Overflow — the sum `tick_accumilator__u32F20 + time_elapsed__u32F20` cannot overflow uint32_t in practice: `reset__game_tick_timer` keeps the accumulator below 2^15 sub-units (one tick), and `time_elapsed__u32F20` is zeroed after each reset and accumulates only a single frame's platform-reported time (far below UINT32_MAX / 2^20 ≈ 4096 seconds per frame).

Side Effects:
1. Mutates `p_game->time_elapsed__u32F20` — adds the platform-reported elapsed time for the current poll (via the `poll_elapsed_time__u32F20_of__game` call whose return value is discarded with `(void)`).
2. Does not modify `p_game->tick_accumilator__u32F20` or any other `Game` field.
3. The only other observable effect is the discarded return value and the computed return value; no global state is touched.
