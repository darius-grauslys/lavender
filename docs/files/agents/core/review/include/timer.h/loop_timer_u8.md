# Function Review: loop_timer_u8

## 1. Header
- **Function name:** `loop_timer_u8`
- **File of origin:** `core/include/timer.h`

## 2. Semantic
Advances a `Timer__u8` countdown timer by one tick. When the timer has reached zero (elapsed), it reloads `remaining__u8` from `start__u8` before decrementing, creating a looping/autoreload countdown cycle.

## 3. Pre-conditions
1. `timer__u8` must be non-null.
2. `timer__u8->start__u8` must be greater than 0. A `start` value of 0 represents the "unused" state (see `initialize_timer_u8_as__unused`) and is not a valid configuration for a looping timer. Calling this function on an unused timer causes unsigned underflow on `remaining__u8`.

## 4. Post-conditions
1. `timer__u8->remaining__u8` is decremented by 1.
2. If `remaining__u8` was 0 before the call, it is first reloaded to `start__u8`, then decremented to `start__u8 - 1`.
3. If `remaining__u8` was non-zero before the call, it is simply decremented by 1.
4. `timer__u8->start__u8` is never modified.

## 5. Correctness Verdict
**Correct**

## 6. Semantic Alignment
The implementation faithfully fulfills the semantic intent of a looping countdown timer. The logic is:

```c
if (timer__u8->remaining__u8 == 0)
    timer__u8->remaining__u8 = timer__u8->start__u8;
timer__u8->remaining__u8--;
```

When the timer expires (`remaining == 0`), it reloads from `start` and then decrements, so the timer cycles: `start → start-1 → ... → 1 → 0 → start-1 → start-2 → ... → 0 → ...`. The timer never holds the value `start` after a reload (it immediately decrements), which is consistent with the `loop_timer_u32` and `loop_timer_u16` implementations. This is an intentional design pattern across all timer widths in this header.

The function is **not** an RAII-style initialization function — it is a tick/advance function. It does not acquire resources; it mutates the timer's countdown state.

## 7. Implementation Correctness
- **Type compatibility:** All field accesses use `uint8_t` members of `Timer__u8`. The parameter `Timer__u8 *timer__u8` is a pointer to the correct type. No implicit conversions or truncation.
- **Undefined behavior:** No null pointer dereference (pre-condition requires non-null). No out-of-bounds access. No type punning. The only potential issue is unsigned integer underflow when `start__u8 == 0` (a pre-condition violation, not a code bug).
- **Validation:** No validation is performed inside the function. This is consistent with the codebase's design philosophy for inline timer functions — validation is the caller's responsibility, and debug-mode assertions are only present in `poll_timer_u8`/`poll_timer_u32` (which check `remaining > start`), not in `loop_timer_*` functions.

## 8. Side Effects
- **Mutates** `timer__u8->remaining__u8` (decremented by 1, or reloaded from `start__u8` then decremented if it was 0).
- Does **not** modify `timer__u8->start__u8`.
- Does **not** produce any I/O or call any external functions.
- No return value (void).
