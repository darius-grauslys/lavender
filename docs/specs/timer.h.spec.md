# Specification: core/include/timer.h

## Overview

Provides countdown timer utilities at three widths (8-bit, 16-bit, 32-bit).
Each timer tracks a starting value and a remaining value, supporting
initialization, reset, polling (decrement-and-check), looping, elapsed
time queries, and duration-based polling.

Timers are used throughout the engine for animation timing, process
scheduling, audio timing, UI notifications, and game tick management.

## Dependencies

- `defines.h` (for `Timer__u8`, `Timer__u16`, `Timer__u32`,
  `Quantity__u8`, `Quantity__u16`, `Quantity__u32`)
- `defines_weak.h`
- `numerics.h` (for `subtract_u32__no_overflow`, `subtract_u16__no_overflow`)

## Types

### Timer__u32

    typedef struct Timer__u32_t {
        uint32_t remaining__u32;
        uint32_t start__u32;
    } Timer__u32;

### Timer__u16

    typedef struct Timer__u16_t {
        uint16_t remaining__u16;
        uint16_t start__u16;
    } Timer__u16;

### Timer__u8

    typedef struct Timer__u8_t {
        uint8_t remaining__u8;
        uint8_t start__u8;
    } Timer__u8;

All three timer types share the same pattern: a `start` value (the
initial countdown) and a `remaining` value (the current countdown).

## Functions

### Construction (static inline)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `get_timer__u8` | `(u8 start) -> Timer__u8` | `Timer__u8` | Returns a timer initialized to `start`. |
| `get_timer__u16` | `(u16 start) -> Timer__u16` | `Timer__u16` | Returns a timer initialized to `start`. |
| `get_timer__u32` | `(u32 start) -> Timer__u32` | `Timer__u32` | Returns a timer initialized to `start`. |

### Initialization (static inline)

| Function | Signature | Description |
|----------|-----------|-------------|
| `initialize_timer_u8` | `(Timer__u8*, u8 start) -> void` | Sets both `start` and `remaining` to `start`. |
| `initialize_timer_u16` | `(Timer__u16*, Quantity__u16 start) -> void` | Sets both `start` and `remaining` to `start`. |
| `initialize_timer_u32` | `(Timer__u32*, Quantity__u32 start) -> void` | Sets both `start` and `remaining` to `start`. |
| `initialize_timer_u8_as__unused` | `(Timer__u8*) -> void` | Sets both fields to 0. |
| `initialize_timer_u16_as__unused` | `(Timer__u16*) -> void` | Sets both fields to 0. |
| `initialize_timer_u32_as__unused` | `(Timer__u32*) -> void` | Sets both fields to 0. |

### Reset (static inline)

| Function | Signature | Description |
|----------|-----------|-------------|
| `reset_timer_u8` | `(Timer__u8*) -> void` | Sets `remaining` back to `start`. |
| `reset_timer_u16` | `(Timer__u16*) -> void` | Sets `remaining` back to `start`. |
| `reset_timer_u32` | `(Timer__u32*) -> void` | Sets `remaining` back to `start`. |

### Elapsed Check (static inline)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `is_timer_u8__elapsed` | `(Timer__u8*) -> bool` | `bool` | True if `remaining == 0`. |
| `is_timer_u16__elapsed` | `(Timer__u16*) -> bool` | `bool` | True if `remaining == 0`. |
| `is_timer_u32__elapsed` | `(Timer__u32*) -> bool` | `bool` | True if `remaining == 0`. |

### Polling (static inline)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `poll_timer_u8` | `(Timer__u8*) -> bool` | `bool` | Decrements `remaining` by 1. Returns true if elapsed. Debug builds check for `remaining > start`. |
| `poll_timer_u16` | `(Timer__u16*) -> bool` | `bool` | Decrements `remaining` by 1. Returns true if elapsed. Debug builds check for `remaining > start`. |
| `poll_timer_u32` | `(Timer__u32*) -> bool` | `bool` | Decrements `remaining` by 1. Returns true if elapsed. Debug builds check for `remaining > start`. |

### Duration-Based Polling (static inline)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `poll_timer_by__this_duration_u16` | `(Timer__u16*, u16 duration) -> bool` | `bool` | Subtracts `duration` from `remaining` (no overflow). Returns true if elapsed. |
| `poll_timer_by__this_duration_u32` | `(Timer__u32*, u32 duration) -> bool` | `bool` | Subtracts `duration` from `remaining` (no overflow). Returns true if elapsed. |

### Looping (static inline)

| Function | Signature | Description |
|----------|-----------|-------------|
| `loop_timer_u8` | `(Timer__u8*) -> void` | Resets to `start` when elapsed, then decrements. |
| `loop_timer_u16` | `(Timer__u16*) -> void` | Resets to `start` when elapsed, then decrements. |
| `loop_timer_u32` | `(Timer__u32*) -> void` | Resets to `start` when elapsed, then decrements. |

### Progress (static inline)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `progress_timer__u32` | `(Timer__u32*, Quantity__u32 ticks) -> bool` | `bool` | Advances the timer by `ticks`. Returns true if the timer wrapped (elapsed and reset). Handles ticks larger than `start`. |

### Elapsed Time Query (static inline)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `get_time_elapsed_from__timer_u8` | `(Timer__u8*) -> Quantity__u8` | `Quantity__u8` | Returns `start - remaining`. |
| `get_time_elapsed_from__timer_u16` | `(Timer__u16*) -> Quantity__u16` | `Quantity__u16` | Returns `start - remaining`. |
| `get_time_elapsed_from__timer_u32` | `(Timer__u32*) -> Quantity__u32` | `Quantity__u32` | Returns `start - remaining`. |

## Agentic Workflow

### Timer Model

All timers are **countdown** timers. They start at a value and decrement
toward zero. "Elapsed" means `remaining == 0`.

    [Initialized: remaining = start]
         |
    poll_timer (remaining--)
         |
    [remaining == 0] -> elapsed!
         |
    reset_timer (remaining = start)

### When to Use Each Width

| Width | Range | Use Case |
|-------|-------|----------|
| `Timer__u8` | 0–255 | Animation frames, short delays. |
| `Timer__u16` | 0–65535 | UI notifications, medium delays. |
| `Timer__u32` | 0–4294967295 | Game ticks, wall clock, long processes. |

### Looping vs Polling

- `poll_timer_*`: One-shot. Returns true when elapsed. Must be manually
  reset.
- `loop_timer_*`: Auto-resets when elapsed. Useful for repeating events
  (animation cycles, periodic spawns).

### Preconditions

- Timer must be initialized before use.
- `poll_timer_*`: `remaining` should not exceed `start`. Debug builds
  emit `debug_error` if this invariant is violated.
- `progress_timer__u32`: `start` must be greater than 0 to avoid
  division by zero in the modulo operation.

### Postconditions

- After `initialize_timer_*`: `remaining == start`.
- After `reset_timer_*`: `remaining == start`.
- After `poll_timer_*` returning true: `remaining == 0`.
- After `loop_timer_*`: `remaining` is decremented, wrapping to `start`
  if it was 0.

### Error Handling

- Debug builds emit `debug_error` if `remaining > start` during polling
  (indicates corruption or misuse).
- No error handling in release builds.
