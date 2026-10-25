# Planning: timer.h — Incorrect Modules

**Review source:** `agents/core/review/include/timer.h/incorrect_modules.md`

**Source files reviewed (read-only):**
- `core/include/timer.h`
- `core/include/defines_weak.h`
- `core/include/numerics.h`
- `core/include/game.h`
- `core/source/game.c`

---

## 1. Problem Identification

### poll_timer_u32 (timer.h:45)

**Defect:** Off-by-one via dead-code post-decrement in a Short-Circuit `||` expression.

The implementation `return (is_timer_u32__elapsed(timer__u32) || timer__u32->remaining__u32-- == 0)` uses post-decrement on the right-hand side. Due to Short-Circuit evaluation, the RHS is only reached when `remaining__u32 != 0`. The post-decrement returns the *pre-decrement* value, which is non-zero by construction of the guard. Therefore `remaining__u32-- == 0` is always `false` — the RHS is dead code. The timer reports elapsed one tick late (e.g., `start__u32 = 5` requires 6 polls to return `true` instead of 5).

**Secondary defect:** The debug message labels `remaining__u32` as "elapsed" — a Surface-form leakage. `remaining__u32` is the countdown value; elapsed is `start__u32 - remaining__u32`.

### poll_timer_u16 (timer.h:177)

**Defect:** Identical off-by-one pattern to `poll_timer_u32`, applied to `uint16_t` fields. The post-decrement in the RHS of `||` is dead code; the timer reports elapsed one tick late. Same debug message terminology error.

### progress_timer__u32 (timer.h:107)

**Defect:** Division by zero (undefined behavior) when `start__u32 == 0`. The wrap-around path executes `quantity_of__ticks__u32 %= p_timer__u32->start__u32`, which divides by zero if the timer was initialized via `initialize_timer_u32_as__unused` (which sets `start__u32 = 0`). No Precondition guard exists.

**Secondary defect:** The final subtraction `remaining__u32 -= quantity_of__ticks__u32` uses raw unsigned subtraction instead of the existing `subtract_u32__no_overflow` helper (numerics.h:295), creating a potential underflow path inconsistent with sibling functions (`poll_timer_by__this_duration_u32` uses the safe helper).

---

## 2. Impact Assessment

### Direct callers

No `.c` file in `core/source/`, `sdl/source/`, `no_gui/source/`, or `nds/source/` directly invokes `poll_timer_u16`, `poll_timer_u32`, or `progress_timer__u32`. These are `static inline` functions in a header; they are only instantiated in translation units that both include `timer.h` *and* call them.

### Indirect exposure via includes

- **`core/include/game.h`** (line 17) includes `<timer.h>`. Any translation unit including `game.h` has these inline functions available.
- **`core/source/game.c`** (line 39) includes `<timer.h>` directly. It currently uses `loop_timer_u32` (correct), `initialize_timer_u32`, and a custom `poll__game_tick_timer` — none of which call the broken functions.
- **`core/include/defines_weak.h`** defines the `Timer__u32`, `Timer__u16`, `Timer__u8` structs used by these functions.
- **`core/include/defines.h`** embeds `Timer__u32` fields in the `Game` struct (lines 2570–2572) and other structs (line 320: `timer_for__audio`).

### Coupled assumptions invalidated by correction

1. **Off-by-one correction (poll_timer_u16/u32):** If any caller has adapted to the one-tick-late behavior (e.g., compensating by polling an extra time, or initializing with `start - 1`), correcting the function will break that compensation. No such adaptation was found in the codebase, but the de facto contract of "returns true one tick after remaining reaches zero" may be assumed by external or future callers.

2. **Division-by-zero guard (progress_timer__u32):** Adding a guard for `start__u32 == 0` changes the function from "UB on invalid input" to "defined behavior on invalid input." Any caller that currently triggers the UB path (by passing a zero-initialized timer with ticks > remaining) will now get a defined result instead of undefined behavior. This is strictly an improvement but changes observable behavior in that edge case.

3. **Safe subtraction adoption:** Switching from raw `-=` to `subtract_u32__no_overflow` in `progress_timer__u32` clamps underflow to 0 instead of wrapping. Under normal conditions (`start__u32 > 0`, modulo applied), the modulo already constrains the value so underflow cannot occur. The change is behavior-preserving for valid inputs and only affects the previously-UB `start__u32 == 0` path.

### Files requiring cascading changes

| File | Reason |
|------|--------|
| `core/include/timer.h` | Primary fix location (all three functions) |
| `core/include/timer.h` (debug messages) | Terminology correction in `poll_timer_u16`/`poll_timer_u32` debug strings |

No other files require changes. The fix is contained within the header.

---

## 3. Resolution Assessment

### poll_timer_u32 — Resolution

**Change:** Replace the dead-code post-decrement expression with an explicit decrement-then-check pattern, mirroring the correct sibling `poll_timer_by__this_duration_u32`:

```c
static bool inline poll_timer_u32(Timer__u32 *timer__u32) {
#ifndef NDEBUG
    if (timer__u32->remaining__u32 > timer__u32->start__u32) {
        debug_error("poll_timer_u32, timer__u32->remaining:%d exceeds start:%d",
                timer__u32->remaining__u32,
                timer__u32->start__u32);
    }
#endif
    if (is_timer_u32__elapsed(timer__u32))
        return true;
    timer__u32->remaining__u32 =
        subtract_u32__no_overflow(
                timer__u32->remaining__u32, 1);
    return timer__u32->remaining__u32 == 0;
}
```

- **Rationale:** Uses `subtract_u32__no_overflow` (consistent with `poll_timer_by__this_duration_u32`), eliminates the dead-code post-decrement, and returns `true` on the exact tick where remaining reaches 0.
- **Debug message:** Correct "elapsed" → "remaining" to fix the Surface-form leakage.
- **Callers:** No caller updates needed (no direct callers found).
- **Tests:** New test required (see §4).

### poll_timer_u16 — Resolution

**Change:** Identical structural fix to `poll_timer_u32`, using `subtract_u16__no_overflow`:

```c
static bool inline poll_timer_u16(Timer__u16 *timer__u16) {
#ifndef NDEBUG
    if (timer__u16->remaining__u16 > timer__u16->start__u16) {
        debug_error("poll_timer_u16, timer__u16->remaining:%d exceeds start:%d",
                timer__u16->remaining__u16,
                timer__u16->start__u16);
    }
#endif
    if (is_timer_u16__elapsed(timer__u16))
        return true;
    timer__u16->remaining__u16 =
        subtract_u16__no_overflow(
                timer__u16->remaining__u16, 1);
    return timer__u16->remaining__u16 == 0;
}
```

- **Note:** `poll_timer_u8` (timer.h:129) has the identical bug pattern but was not flagged in the review. Recommend fixing it in the same pass for consistency (DRY).
- **Callers:** No caller updates needed.
- **Tests:** New test required (see §4).

### progress_timer__u32 — Resolution

**Change:** Add a Precondition guard for `start__u32 == 0` and adopt `subtract_u32__no_overflow`:

```c
static inline
bool progress_timer__u32(
        Timer__u32 *p_timer__u32,
        Quantity__u32 quantity_of__ticks__u32) {
    if (p_timer__u32->start__u32 == 0) {
        return is_timer_u32__elapsed(p_timer__u32);
    }
    if (quantity_of__ticks__u32 > p_timer__u32->remaining__u32) {
        quantity_of__ticks__u32 -= p_timer__u32->remaining__u32;
        if (quantity_of__ticks__u32 > p_timer__u32->start__u32) {
            quantity_of__ticks__u32 %= p_timer__u32->start__u32;
        }
        reset_timer_u32(p_timer__u32);
        p_timer__u32->remaining__u32 =
            subtract_u32__no_overflow(
                    p_timer__u32->remaining__u32,
                    quantity_of__ticks__u32);
        return true;
    }
    p_timer__u32->remaining__u32 =
        subtract_u32__no_overflow(
                p_timer__u32->remaining__u32,
                quantity_of__ticks__u32);
    return false;
}
```

- **Guard:** `start__u32 == 0` short-circuits to the elapsed check, eliminating the division-by-zero UB. A zero-start timer is always "elapsed" (remaining is also 0 per `initialize_timer_u32_as__unused`), so returning `is_timer_u32__elapsed(...)` is semantically correct.
- **Safe subtraction:** Both subtraction sites now use `subtract_u32__no_overflow`, consistent with the rest of the timer module. Under valid conditions (`start__u32 > 0`), the modulo already bounds `quantity_of__ticks__u32 < start__u32`, so the clamp-to-zero in `subtract_u32__no_overflow` never activates — behavior is preserved for valid inputs.
- **Callers:** No caller updates needed.
- **Tests:** New test required for the `start__u32 == 0` Boundary Condition (see §4).

---

## 4. Test Verification Checklist

### Existing test coverage

No dedicated timer test file exists. The `tests/test_suite_game.c` file does not reference `poll_timer_u16`, `poll_timer_u32`, or `progress_timer__u32`. No existing assertions are invalidated by the fix.

### Required new tests

A new test suite (e.g., `core/source/test_suite_timer.c` + `core/include/test_suite_timer.h`) should cover:

| Test | Strategy | What it verifies |
|------|----------|-----------------|
| `poll_timer_u32` returns `true` on exactly the Nth call for `start__u32 = N` | Golden-file Test (deterministic sequence) | Off-by-one is fixed; Postcondition 2 holds |
| `poll_timer_u32` with `start__u32 = 1` returns `true` on first call | Boundary Condition | Minimal timer elapses in one tick |
| `poll_timer_u32` with already-elapsed timer returns `true` without mutation | Round Trip Check (idempotent poll) | Frame Condition: no mutation when elapsed |
| `poll_timer_u16` same sequence as u32 variant | Equivalence Check (u16 vs u32 behavior) | Type-parametric consistency |
| `progress_timer__u32` with `start__u32 == 0` does not crash | Fuzzing / Boundary Condition | Division-by-zero UB eliminated |
| `progress_timer__u32` wrap-around: ticks > remaining, ticks ≤ start | Property Based Testing | Invariant: `remaining ∈ [0, start]` holds after call |
| `progress_timer__u32` wrap-around: ticks > start (modulo path) | Property Based Testing | Conservation Law: total elapsed = ticks mod start + (start - remaining_before) |
| `poll_timer_by__this_duration_u32` with `duration = 1` matches `poll_timer_u32` | Differential Testing | Equivalence between the two poll strategies at unit duration |

### Blast radius for tests

- **Impact: Low.** No existing tests assert on the broken behavior. New tests are additive.
- **Phased approach: Not needed.** All three fixes are independent and can be tested in a single new test file.

---

## 5. Blast Radius Summary

| Dimension | Assessment |
|-----------|-----------|
| Files changed | 1 (`core/include/timer.h`) + 1 new test file (optional) |
| Behavior-preserving for current callers? | Yes — no current caller invokes the broken functions |
| Phased approach needed? | No — all fixes are local to one header, independent of each other |
| De facto contracts invalidated? | None found. The one-tick-late behavior is not compensated for anywhere in the codebase. |
| Risk level | **Low.** The fix corrects a latent bug in unused (or rarely-used) inline functions. No production code path is affected by the behavioral change. |

### Recommended execution order

1. Fix `poll_timer_u32` (and `poll_timer_u8` for consistency, though not flagged).
2. Fix `poll_timer_u16`.
3. Fix `progress_timer__u32` (add guard + safe subtraction).
4. Correct debug message terminology in all poll functions.
5. Add test suite.
