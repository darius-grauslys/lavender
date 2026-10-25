# poll_timer_by__this_duration_u32

## File of Origin
core/include/timer.h

## Semantic
Polls a `Timer__u32` by decrementing its `remaining__u32` field by a caller-specified `duration`, returning whether the timer has elapsed (i.e., `remaining__u32` has reached zero).

## Pre-conditions
1. `timer__u32` must be a non-null pointer to a writable, properly initialized `Timer__u32` struct.
2. `duration` is any `u32` value; there is no range constraint. If `duration` exceeds `remaining__u32`, the subtraction is clamped to zero by `subtract_u32__no_overflow`.
3. In debug builds (`NDEBUG` not defined), `timer__u32->remaining__u32` must not exceed `timer__u32->start__u32`. This invariant is checked at entry and logged via `debug_error` if violated.

## Post-conditions
1. If the timer was already elapsed (`remaining__u32 == 0` at entry), the function returns `true` and does not modify the timer.
2. Otherwise, `timer__u32->remaining__u32` is set to `remaining__u32 - duration`, clamped to a minimum of 0 via `subtract_u32__no_overflow`. The `start__u32` field is not modified.
3. The function returns `true` if `remaining__u32` is now 0 after subtraction, and `false` otherwise.

## Correctness Verdict
Correct

## Semantic Alignment
The implementation fulfills the semantic intent. The function first checks whether the timer is already elapsed and short-circuits with `true`. If not, it safely subtracts the `duration` from `remaining__u32` using `subtract_u32__no_overflow`, which prevents unsigned underflow by clamping to 0 when `duration` exceeds `remaining__u32`. It then returns whether the timer has reached zero. This matches the expected behavior of a duration-based timer poll. The `start__u32` field is left untouched, preserving the timer's configuration.

## Implementation Correctness
- **Type compatibility**: All types match exactly. `timer__u32` is `Timer__u32 *`, matching the parameter. `duration` is `u32` (which is `typedef uint32_t u32`), matching the `u32` parameter of `subtract_u32__no_overflow`. The `remaining__u32` field is `uint32_t`, which is the same underlying type as `u32` and `Quantity__u32`. The return type `bool` is consistent. No implicit conversions or truncation occur.
- **Undefined behavior**: None. No pointer arithmetic, no null dereference (null-checking is the caller's responsibility), no type punning, no out-of-bounds access. The debug-mode invariant check is a read-only validation.
- **Validation**: The debug-only check that `remaining__u32 <= start__u32` is appropriate as a diagnostic for a timer invariant. No runtime validation is needed for `duration` because `subtract_u32__no_overflow` handles all values safely.

## Side Effects
Mutates `timer__u32->remaining__u32` by subtracting `duration` (clamped to 0 via `subtract_u32__no_overflow`). The `start__u32` field is not modified. The function is not a Lavender-style initialization/reset function; it is a polling function that progresses the timer's remaining time.
