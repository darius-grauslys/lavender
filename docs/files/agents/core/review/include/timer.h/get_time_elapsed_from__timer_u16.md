# get_time_elapsed_from__timer_u16

**File of origin:** `core/include/timer.h`

## Semantic

Computes the elapsed time of a `Timer__u16` by subtracting the remaining count from the start count, returning the result as a `Quantity__u16`.

## Pre-conditions

1. `timer__u16` must not be `NULL` — the function dereferences the pointer without null-checking.
2. The timer invariant `remaining__u16 <= start__u16` must hold. This invariant is maintained by all other timer operations (`poll_timer_u16`, `poll_timer_by__this_duration_u16`, `reset_timer_u16`, `loop_timer_u16`, `initialize_timer_u16`, `initialize_timer_u16_as__unused`) and is enforced via debug assertions in `poll_timer_u16` and `poll_timer_by__this_duration_u16`.

## Post-conditions

1. Returns a `Quantity__u16` representing the elapsed ticks: `start__u16 - remaining__u16`.
2. The `Timer__u16` struct pointed to by `timer__u16` is not modified — this is a read-only operation.

## Correctness Verdict

**Correct**

## Semantic Alignment

The implementation correctly fulfills the semantic intent. A `Timer__u16` counts down from `start__u16` to zero via `remaining__u16`. The elapsed time is therefore `start__u16 - remaining__u16`, which is exactly what the function computes. This is consistent with the u32 and u8 variants (`get_time_elapsed_from__timer_u32` and `get_time_elapsed_from__timer_u8`).

## Implementation Correctness

- **Type compatibility:** `start__u16` and `remaining__u16` are both `uint16_t`, and `Quantity__u16` is `typedef uint16_t Quantity__u16`. The return type matches exactly — no implicit conversions or truncation.
- **Undefined behavior:** No null dereference if the pointer is valid (caller responsibility, consistent with the codebase's inline function style). No out-of-bounds access. No type punning.
- **Overflow safety:** The subtraction `start__u16 - remaining__u16` cannot underflow in practice because the timer invariant (`remaining__u16 <= start__u16`) is maintained by all mutating timer functions. The codebase provides `subtract_u16__no_overflow` for cases where the invariant cannot be guaranteed, but it is not needed here since the invariant is structurally enforced.
- **Validation:** No null check is performed, which is appropriate for this inline function — it follows the same convention as all other inline timer functions in this header (e.g., `is_timer_u16__elapsed`, `reset_timer_u16`, `poll_timer_u16`), where pointer validity is the caller's responsibility.

## Side Effects

No side effects. The function reads from the `Timer__u16` struct and returns a computed value without modifying any state.
