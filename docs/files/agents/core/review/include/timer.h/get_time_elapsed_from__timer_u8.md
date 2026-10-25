get_time_elapsed_from__timer_u8 — core/include/timer.h, lines 150-153

Computes the elapsed time of a Timer__u8 by subtracting its remaining count from its start value.

Pre-conditions:
1. timer__u8 must be a non-null pointer to a valid Timer__u8 struct.
2. timer__u8->start__u8 must hold the initial countdown value (set during initialization).
3. timer__u8->remaining__u8 must be <= timer__u8->start__u8 under normal operation; if remaining exceeds start, the unsigned subtraction will underflow, producing a large incorrect value.

Post-conditions:
1. Returns a Quantity__u8 (uint8_t) equal to timer__u8->start__u8 - timer__u8->remaining__u8, representing the elapsed ticks.
2. The Timer__u8 struct pointed to by timer__u8 is not modified.

Correctness Verdict: Correct

Semantic Alignment:
The function correctly computes elapsed time as start - remaining, which is the standard formula for a countdown timer: the amount of time that has passed equals the original duration minus what is still left. This is semantically consistent with the analogous get_time_elapsed_from__timer_u32 (lines 83-86) and get_time_elapsed_from__timer_u16 (lines 215-218) functions in the same header, which use the identical pattern: start__uX - remaining__uX. The implementation matches the semantic intent precisely.

Implementation Correctness:
Type compatibility — the parameter is Timer__u8 *, and both start__u8 and remaining__u8 are uint8_t fields, so the subtraction is between two uint8_t values, which are promoted to int for the arithmetic and then converted back to uint8_t for the return type Quantity__u8 (also uint8_t). No implicit conversions or truncation issues arise.
No undefined behavior — no pointer arithmetic, no null dereference (caller must ensure non-null), no type punning, no out-of-bounds access. The subtraction is unsigned arithmetic, which is well-defined in C (wraps modulo 256), though the result may be semantically incorrect if remaining > start.
Validation — no validation is performed, which is appropriate for a low-level inline query function. The debug-only invariant checks in related functions (e.g., poll_timer_u8) catch the remaining > start condition in debug builds. Null-checking and invariant enforcement are the caller's responsibility, consistent with the pattern used across all timer functions in this header.

Side Effects:
No side effects — the function is a pure read/query. It does not modify the Timer__u8 struct or any other state.
