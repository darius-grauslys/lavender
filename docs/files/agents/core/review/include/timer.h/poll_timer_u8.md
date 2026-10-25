poll_timer_u8 — core/include/timer.h

Polls (decrements) a u8 timer and returns whether it has elapsed.

Pre-conditions:
1. timer__u8 must be a non-null pointer to a valid Timer__u8 struct.
2. timer__u8->start__u8 defines the initial countdown value; timer__u8->remaining__u8 is the current countdown value and should be <= start__u8 under normal operation.

Post-conditions:
1. If timer__u8->remaining__u8 was already 0 (elapsed), returns true and does not modify remaining__u8.
2. If timer__u8->remaining__u8 was non-zero, decrements remaining__u8 by 1 and returns false.
3. The struct field timer__u8->start__u8 is never modified.

Correctness Verdict: Correct

Semantic Alignment:
The function correctly implements a countdown poll: it decrements the remaining counter each call and returns true only when the timer has fully elapsed (remaining == 0). The short-circuit evaluation of `||` ensures that when the timer is already elapsed, the post-decrement is not executed, preserving remaining__u8 at 0. The debug check `remaining__u8 > start__u8` catches an invalid state where the countdown value exceeds its original bound. The debug message text ("elapsed exceeds limit") is slightly misleading but the check itself is correct for detecting corrupted timer state.

Implementation Correctness:
Type compatibility — timer__u8 is a pointer to Timer__u8, and all field accesses (remaining__u8, start__u8) are uint8_t, consistent with the struct definition. No implicit conversions or truncation.
No undefined behavior — no pointer arithmetic, no null dereference (caller must ensure non-null), no type punning, no out-of-bounds access. The post-decrement on an unsigned 8-bit value is safe as long as remaining is not expected to go below 0 (it stops at 0 via the elapsed check).
Validation — the debug-only check for remaining > start is appropriate for catching logic errors in debug builds. In release builds (NDEBUG defined), no validation is performed, which is consistent with the function's role as a low-level inline timer poll.

Side Effects:
Mutates timer__u8->remaining__u8 (decrements it by 1 when the timer is not yet elapsed). Does not modify timer__u8->start__u8. No other side effects.
