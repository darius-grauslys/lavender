# loop_timer_u16

**File of origin:** `core/include/timer.h`

## Semantic

Decrements a 16-bit timer's remaining count; if the timer has expired (remaining == 0), it reloads the remaining value from the start value before decrementing, producing a periodic/looping timer.

## Pre-conditions

1. `timer__u16` must be non-null (it is dereferenced directly without null checks).
2. The timer must have been previously initialized (e.g., via `initialize_timer_u16`), so that `start__u16` holds a meaningful period. If `start__u16` is 0, the reload will set `remaining__u16` to 0 and the subsequent decrement will wrap to `0xFFFF` (unsigned underflow), which is a degenerate case the caller must avoid.

## Post-conditions

1. If `remaining__u16` was 0 upon entry, it is reloaded to `start__u16` and then decremented by 1, resulting in `remaining__u16 == start__u16 - 1`.
2. If `remaining__u16` was non-zero upon entry, it is decremented by 1, resulting in `remaining__u16 == (original remaining) - 1`.
3. `start__u16` is unchanged.
4. The function returns `void`; all effects are observed through the mutated `Timer__u16` struct.

## Correctness Verdict

**Correct**

## Semantic Alignment

The implementation faithfully realizes the "loop timer" semantic: when the countdown reaches zero, the timer is reloaded from its start value and continues decrementing, creating a periodic countdown loop. This is consistent with the identical `loop_timer_u8` and `loop_timer_u32` implementations in the same header. The logic is straightforward and matches the documented intent of a looping timer.

## Implementation Correctness

- **Type compatibility:** The parameter is `Timer__u16 *`, and `remaining__u16` / `start__u16` are both `uint16_t`. The decrement operator `--` on a `uint16_t` is well-defined (wraps on underflow). No implicit conversions or truncation occur.
- **Undefined behavior:** No null pointer dereference (caller responsibility), no out-of-bounds access, no type punning. The unsigned decrement is well-defined per the C standard.
- **Validation:** This is a low-level inline timer utility; null-checking or start-value validation would be the caller's responsibility, consistent with the rest of the timer API (e.g., `poll_timer_u16`, `reset_timer_u16` all follow the same pattern).

## Side Effects

- Mutates `timer__u16->remaining__u16` (and conditionally reloads it from `timer__u16->start__u16`).
- Does not modify `timer__u16->start__u16`.
- No other observable side effects (no I/O, no global state, no memory allocation).
