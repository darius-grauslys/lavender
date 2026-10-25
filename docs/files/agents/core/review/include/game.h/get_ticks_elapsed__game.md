get_ticks_elapsed__game — core/include/game.h

Returns the number of elapsed ticks from the game's tick timer, delegating to `get_time_elapsed_from__timer_u32`.

Pre-conditions:
1. `p_game` must be a non-null pointer to a valid, initialized `Game` object.
2. `p_game->tick__timer_u32` must hold a consistent timer state (`remaining__u32 <= start__u32`), as maintained by the timer lifecycle functions in `timer.h`.

Post-conditions:
1. Returns a `Quantity__u32` (`uint32_t`) equal to `tick__timer_u32.start__u32 - tick__timer_u32.remaining__u32`, i.e. the elapsed tick count.
2. The function does not modify `p_game` or any other observable state.

Correctness Verdict: Correct

Semantic Alignment:
The implementation fulfills its stated intent — it returns the elapsed ticks from the game's tick timer by delegating to `get_time_elapsed_from__timer_u32`, which computes `start__u32 - remaining__u32` (the standard elapsed-time formula for Lavender's countdown timers). The name "get_ticks_elapsed" accurately describes the returned quantity. The source carries a maintainer note (`/// TODO: obsolete, and inaccurate`); this flags that the function may be considered obsolete or its "ticks" labeling misleading by maintainers, but the implementation itself is semantically aligned with its name and purpose.

Implementation Correctness:
- Type compatibility: `p_game` is `Game *`; `&p_game->tick__timer_u32` is `Timer__u32 *`, matching the parameter type of `get_time_elapsed_from__timer_u32(Timer__u32 *)` exactly. The return type `Quantity__u32` (`uint32_t`) matches the callee's return type. No implicit conversions or truncation occur.
- Undefined behavior: For a valid non-null `p_game` there is no null dereference, no pointer arithmetic, no type punning, and no out-of-bounds access. A null `p_game` would cause a null dereference, but this is consistent with the codebase convention for low-level inline accessors (e.g., `set_dispatch_handler_process_for__create_client`) and is the caller's responsibility.
- Validation: No validation is performed or needed — this is a low-level read accessor; ensuring `p_game` points to a properly initialized `Game` is the caller's responsibility.

Side Effects:
No side effects. The function is a pure read accessor: it reads `p_game->tick__timer_u32` and returns a computed value without mutating any state.
