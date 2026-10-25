# poll_timer_u16

## File of Origin
core/include/timer.h

## Semantic
Polls a `Timer__u16` by decrementing its `remaining__u16` field by one tick and returns whether the timer has elapsed (i.e., `remaining__u16` has reached zero).

## Pre-conditions
1. `timer__u16` must be a non-null pointer to a writable, properly initialized `Timer__u16` struct.
2. `timer__u16->start__u16` defines the initial countdown value; `timer__u16->remaining__u16` is the current countdown value and should be <= `start__u16` under normal operation.
3. In debug builds (`NDEBUG` not defined), `timer__u16->remaining__u16` must not exceed `timer__u16->start__u16`. This invariant is checked at entry and logged via `debug_error` if violated.

## Post-conditions
1. If the timer was already elapsed (`remaining__u16 == 0` at entry), the function returns `true` and does not modify `remaining__u16` (short-circuit prevents the post-decrement from executing).
2. If the timer was not yet elapsed (`remaining__u16 > 0` at entry), `remaining__u16` is decremented by 1 and the function returns `false`.
3. The `start__u16` field is never modified.

## Correctness Verdict
Incorrect

## Semantic Alignment
The function's stated intent (via its name and the `||` expression) is to return `true` when the timer has elapsed — i.e., when `remaining__u16` reaches 0. However, the implementation uses post-decrement (`remaining__u16--`) in the right-hand side of the `||` expression. Due to short-circuit evaluation, the right-hand side is only reached when `is_timer_u16__elapsed` returns `false`, which means `remaining__u16 != 0`. When `remaining__u16 != 0`, the comparison `remaining__u16-- == 0` always evaluates to `false` (the non-zero value is compared to 0 before the decrement occurs). Therefore, the right-hand side of the `||` is effectively dead code — it can never produce `true`.

The practical consequence is an off-by-one error: when `remaining__u16` decrements from 1 to 0 (via the post-decrement), the function returns `false` instead of `true`. The timer only reports elapsed on the *next* call, one poll later. For example, a timer initialized with `start__u16 = 5` requires 6 calls to `poll_timer_u16` before returning `true`, rather than the expected 5.

This contradicts the behavior of the sibling function `poll_timer_by__this_duration_u16` (with `duration = 1`), which correctly returns `true` when the timer reaches 0 after subtraction. The same off-by-one pattern exists in `poll_timer_u8` and `poll_timer_u32`.

The debug message also contains a terminology error: it labels `remaining__u16` as "elapsed", which is semantically incorrect. The actual elapsed time is `start__u16 - remaining__u16`; `remaining__u16` is the countdown value, not the elapsed value.

## Implementation Correctness
- **Type compatibility**: The parameter type `Timer__u16 *` matches the struct pointer; field accesses use `uint16_t` consistently (`remaining__u16` and `start__u16` are both `uint16_t`). The return type is `bool`. No implicit conversions or truncation occur in the core logic. The debug format specifier `%d` is used for `uint16_t` values; on most platforms `uint16_t` is promoted to `int` in variadic calls, so this is practically safe, but `PRIu16` or `%u` would be more portable.
- **Undefined behavior**: No broken pointer arithmetic, no null dereference (null-checking is the caller's responsibility per engine convention), no type punning, no out-of-bounds access. The post-decrement on a `uint16_t` is well-defined for values > 0. The short-circuit evaluation of `||` prevents underflow: when `remaining__u16 == 0`, the right-hand side is never evaluated, so the decrement does not occur and no underflow to `UINT16_MAX` happens.
- **Validation**: The debug-only check for `remaining__u16 > start__u16` is appropriate for catching timer invariant violations in debug builds. In release builds (`NDEBUG` defined), no validation is performed, which is consistent with the function's role as a low-level inline timer utility.

## Side Effects
Mutates `timer__u16->remaining__u16` by decrementing it by 1 (only when `remaining__u16 > 0`; no mutation when `remaining__u16 == 0`). The `start__u16` field is not modified. In debug builds, a call to `debug_error` may occur (which may log to console or trigger a core dump depending on backend configuration). No other side effects.
