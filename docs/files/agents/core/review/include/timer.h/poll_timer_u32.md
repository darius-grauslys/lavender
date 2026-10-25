poll_timer_u32 — core/include/timer.h

Decrements a 32-bit countdown timer by one tick and returns whether the timer has elapsed.

Pre-conditions:
1. timer__u32 must be a non-null pointer to a valid, writable Timer__u32 object.
2. timer__u32->remaining__u32 must be <= timer__u32->start__u32 (enforced via debug check in non-release builds).
3. The timer must have been initialized via initialize_timer_u32, get_timer__u32, or equivalent before polling.

Post-conditions:
1. If timer__u32->remaining__u32 was 0 before the call, the function returns true and remaining__u32 is left unchanged (no decrement).
2. If timer__u32->remaining__u32 was > 0 before the call, remaining__u32 is decremented by 1 and the function returns false.
3. After the timer's remaining__u32 reaches 0, subsequent calls return true without further decrement.

Correctness Verdict: Incorrect

Semantic Alignment:
The function's stated intent (via its name and the || expression) is to return true when the timer has elapsed — i.e., when remaining reaches 0. However, the implementation uses post-decrement (remaining__u32--) in the right-hand side of the || expression, which evaluates the value *before* decrementing. Due to short-circuit evaluation, the right-hand side is only reached when remaining__u32 != 0, so the comparison `remaining__u32-- == 0` always evaluates to false. This means the right-hand side of the || is effectively dead code — it can never produce true.

The practical consequence is an off-by-one error: when remaining__u32 decrements from 1 to 0, the function returns false instead of true. The timer only reports elapsed on the *next* call, one tick later. This contradicts the behavior of the sibling function poll_timer_by__this_duration_u32, which correctly returns true when the timer reaches 0 after subtraction.

The debug message also contains a terminology error: it labels remaining__u32 as "elapsed", which is semantically incorrect (remaining and elapsed are complementary values).

Implementation Correctness:
Type compatibility — the parameter type (Timer__u32 *) matches the struct pointer; field accesses use uint32_t consistently. No implicit conversions or truncation.
Undefined behavior — no null check (consistent with engine convention; caller responsibility). No pointer arithmetic, no type punning, no out-of-bounds access. The post-decrement on a uint32_t is well-defined for values > 0.
The debug format specifier %d is used for uint32_t values, which may be incorrect on platforms where int is 16-bit (should use %u or PRIu32). This is a minor portability concern.
No validation beyond the debug assertion — appropriate for this low-level inline utility, consistent with engine conventions.
The short-circuit evaluation of || prevents underflow: when remaining__u32 == 0, the right-hand side is never evaluated, so the decrement does not occur and no underflow to UINT32_MAX happens. This is correct, but the right-hand side itself is dead code.

Side Effects:
Mutates timer__u32->remaining__u32 by decrementing it by 1 (only when remaining__u32 > 0; no mutation when remaining__u32 == 0). No other side effects.
