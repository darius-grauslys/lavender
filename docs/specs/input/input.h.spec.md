# Specification: core/include/input/input.h

## Overview

Provides initialization, polling, and query utilities for the `Input`
struct — the engine's unified input abstraction. The `Input` struct
captures three states of each input button (pressed, held, released)
per frame, along with cursor position and a writing buffer for text
entry.

Input polling is platform-dependent (`PLATFORM_poll_input`), but all
query functions are platform-independent and implemented as `static
inline` helpers in this header.

## Dependencies

- `defines.h` (for `Input`, `Input_Flags__u32`, `Input_Mode__u8`,
  `Input_Code__u32`, `Vector__3i32`, `Game`)
- `defines_weak.h` (forward declarations)
- `platform_defaults.h` (for `INPUT_FORWARD`, `INPUT_LEFT`, etc.,
  `INPUT_NONE`, `INPUT_CLICK`,
  `MAX_QUANTITY_OF__SYMBOLS_IN__INPUT_WRITING_BUFFER`)
- `vectors.h` (for `initialize_3i32_vector`, `is_vectors_3i32__equal`)

## Types

### Input (struct)

Defined in `defines.h`:

    typedef struct Input_t {
        Input_Flags__u32 input_flags__pressed;
        Input_Flags__u32 input_flags__held;
        Input_Flags__u32 input_flags__released;
        Input_Flags__u32 input_flags__pressed_old;
        Vector__3i32 cursor__3i32;
        Vector__3i32 cursor__old__3i32;
        unsigned char writing_buffer[
            MAX_QUANTITY_OF__SYMBOLS_IN__INPUT_WRITING_BUFFER];
        unsigned char last_symbol;
        Index__u8 index_of__writing_buffer__read;
        Index__u8 index_of__writing_buffer__write;
        Input_Mode__u8 input_mode__u8;
    } Input;

| Field | Type | Description |
|-------|------|-------------|
| `input_flags__pressed` | `Input_Flags__u32` | Bitmask of buttons pressed this frame (rising edge). |
| `input_flags__held` | `Input_Flags__u32` | Bitmask of buttons held this frame (sustained). |
| `input_flags__released` | `Input_Flags__u32` | Bitmask of buttons released this frame (falling edge). |
| `input_flags__pressed_old` | `Input_Flags__u32` | Previous frame's pressed flags. Not used by all platforms. |
| `cursor__3i32` | `Vector__3i32` | Current cursor/touch position. |
| `cursor__old__3i32` | `Vector__3i32` | Previous frame's cursor position. Used for drag detection. |
| `writing_buffer` | `unsigned char[]` | Circular buffer for text entry characters. Size is `MAX_QUANTITY_OF__SYMBOLS_IN__INPUT_WRITING_BUFFER` (default: `BIT(3)` = 8). |
| `last_symbol` | `unsigned char` | Most recently written character. |
| `index_of__writing_buffer__read` | `Index__u8` | Read index into the circular writing buffer. |
| `index_of__writing_buffer__write` | `Index__u8` | Write index into the circular writing buffer. |
| `input_mode__u8` | `Input_Mode__u8` | Current input mode (normal, writing, etc.). |

### Input_Flags__u32 (u32)

A bitmask where each bit corresponds to a logical input button. The
default bit assignments are defined in `platform_defaults.h` (guarded
by `#ifndef PLATFORM_INPUT`) and can be overridden by platform backends.

| Logical Input | Code Macro | Flag Macro | Default Bit |
|---------------|------------|------------|-------------|
| None | `INPUT_CODE_NONE` (0) | `INPUT_NONE` (0) | — |
| Forward | `INPUT_CODE_FORWARD` (1) | `INPUT_FORWARD` | BIT(0) |
| Left | `INPUT_CODE_LEFT` (2) | `INPUT_LEFT` | BIT(1) |
| Right | `INPUT_CODE_RIGHT` (3) | `INPUT_RIGHT` | BIT(2) |
| Backward | `INPUT_CODE_BACKWARD` (4) | `INPUT_BACKWARD` | BIT(3) |
| Game Settings | `INPUT_CODE_GAME_SETTINGS` (5) | `INPUT_GAME_SETTINGS` | BIT(4) |
| Lockon | `INPUT_CODE_LOCKON` (6) | `INPUT_LOCKON` | BIT(5) |
| Use | `INPUT_CODE_USE` (7) | `INPUT_USE` | BIT(6) |
| Use Secondary | `INPUT_CODE_USE_SECONDARY` (8) | `INPUT_USE_SECONDARY` | BIT(7) |
| Examine | `INPUT_CODE_EXAMINE` (9) | `INPUT_EXAMINE` | BIT(8) |
| Consume | `INPUT_CODE_CONSUME` (10) | `INPUT_CONSUME` | BIT(9) |
| Turn Right | `INPUT_CODE_TURN_RIGHT` (11) | `INPUT_TURN_RIGHT` | BIT(10) |
| Turn Left | `INPUT_CODE_TURN_LEFT` (12) | `INPUT_TURN_LEFT` | BIT(11) |
| Click | `INPUT_CODE_CLICK` (13) | `INPUT_CLICK` | BIT(12) |

The `INPUT_CODE_*` macros are sequential integer identifiers (0–13).
The `INPUT_*` flag macros are bitmask values (each a single bit).
`QUANTITY_OF__INPUTS` (default: 14) defines the total count.

### Input_Mode__u8 (u8)

| Constant | Value | Description |
|----------|-------|-------------|
| `INPUT_MODE__NONE` / `INPUT_MODE__NORMAL` | 0 | Normal gameplay input. |
| `INPUT_MODE__WRITING` | `BIT(1)` | Text entry mode. Input is routed to the writing buffer. |

### ASCII Constants

Defined in `defines_weak.h`:

| Constant | Value | Description |
|----------|-------|-------------|
| `ASCII__CARRIAGE_RETURN` | 13 | Carriage return. |
| `ASCII__LINE_FEED` | 10 | Line feed / newline. |
| `ASCII__ESCAPE` | 27 | Escape key. |
| `ASCII__BACKSPACE` | 8 | Backspace. |
| `ASCII__DELETE` | 127 | Delete. |
| `ASCII_LAVENDER__UP_ARROW` | 128 | Engine-specific: up arrow. |
| `ASCII_LAVENDER__DOWN_ARROW` | 129 | Engine-specific: down arrow. |
| `ASCII_LAVENDER__LEFT_ARROW` | 130 | Engine-specific: left arrow. |
| `ASCII_LAVENDER__RIGHT_ARROW` | 131 | Engine-specific: right arrow. |

Note: The `ASCII_LAVENDER__*` constants are **not** standard ASCII.
They use values 128–131 which are outside the 7-bit ASCII range. These
are safe to use only within the engine's input and UI systems.

## Functions

### Initialization

| Function | Signature | Description |
|----------|-----------|-------------|
| `initialize_input` | `(Input*) -> void` | Initializes all input state to zero/default. |

### Polling

| Function | Signature | Description |
|----------|-----------|-------------|
| `poll_input` | `(Game*, Input*) -> void` | Polls platform input and updates the `Input` struct. **Do not call directly** — called by `manage_game__post_render` in `game.c` each frame. Internally calls `PLATFORM_poll_input`. |

### Writing Buffer

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `poll_input_for__writing` | `(Input*) -> unsigned char` | `unsigned char` | Dequeues and returns the next character from the circular writing buffer. |
| `buffer_input_for__writing` | `(Input*, char) -> void` | `void` | Enqueues a character into the circular writing buffer. |
| `get_last_symbol_of__input_for__writing` | `(Input*) -> unsigned char` | `unsigned char` | Returns `last_symbol` without consuming it from the buffer. (static inline) |

### Clear (static inline)

| Function | Signature | Description |
|----------|-----------|-------------|
| `clear_input` | `(Input*) -> void` | Clears pressed, held, and released flags to `INPUT_NONE`. Saves current cursor to `cursor__old__3i32` and zeroes `cursor__3i32`. |

### Button State Queries — Released (static inline)

All return `bool`. Parameter: `(Input*)`.

| Function | Tests |
|----------|-------|
| `is_input__forward_released` | `input_flags__released & INPUT_FORWARD` |
| `is_input__left_released` | `input_flags__released & INPUT_LEFT` |
| `is_input__right_released` | `input_flags__released & INPUT_RIGHT` |
| `is_input__backward_released` | `input_flags__released & INPUT_BACKWARD` |
| `is_input__game_settings_released` | `input_flags__released & INPUT_GAME_SETTINGS` |
| `is_input__lockon_released` | `input_flags__released & INPUT_LOCKON` |
| `is_input__use_released` | `input_flags__released & INPUT_USE` |
| `is_input__use_secondary_released` | `input_flags__released & INPUT_USE_SECONDARY` |
| `is_input__examine_released` | `input_flags__released & INPUT_EXAMINE` |
| `is_input__consume_released` | `input_flags__released & INPUT_CONSUME` |
| `is_input__turn_left_released` | `input_flags__released & INPUT_TURN_LEFT` |
| `is_input__turn_right_released` | `input_flags__released & INPUT_TURN_RIGHT` |
| `is_input__none_released` | `input_flags__released & INPUT_NONE` |
| `is_input__click_released` | `input_flags__released & INPUT_CLICK` |

### Button State Queries — Pressed (static inline)

All return `bool`. Parameter: `(Input*)`.

| Function | Tests |
|----------|-------|
| `is_input__forward_pressed` | `input_flags__pressed & INPUT_FORWARD` |
| `is_input__left_pressed` | `input_flags__pressed & INPUT_LEFT` |
| `is_input__right_pressed` | `input_flags__pressed & INPUT_RIGHT` |
| `is_input__backward_pressed` | `input_flags__pressed & INPUT_BACKWARD` |
| `is_input__game_settings_pressed` | `input_flags__pressed & INPUT_GAME_SETTINGS` |
| `is_input__lockon_pressed` | `input_flags__pressed & INPUT_LOCKON` |
| `is_input__use_pressed` | `input_flags__pressed & INPUT_USE` |
| `is_input__use_secondary_pressed` | `input_flags__pressed & INPUT_USE_SECONDARY` |
| `is_input__examine_pressed` | `input_flags__pressed & INPUT_EXAMINE` |
| `is_input__consume_pressed` | `input_flags__pressed & INPUT_CONSUME` |
| `is_input__turn_left_pressed` | `input_flags__pressed & INPUT_TURN_LEFT` |
| `is_input__turn_right_pressed` | `input_flags__pressed & INPUT_TURN_RIGHT` |
| `is_input__none_pressed` | `input_flags__pressed & INPUT_NONE` |
| `is_input__click_pressed` | `input_flags__pressed & INPUT_CLICK` |

### Button State Queries — Held (static inline)

All return `bool`. Parameter: `(Input*)`.

| Function | Tests |
|----------|-------|
| `is_input__forward_held` | `input_flags__held & INPUT_FORWARD` |
| `is_input__left_held` | `input_flags__held & INPUT_LEFT` |
| `is_input__right_held` | `input_flags__held & INPUT_RIGHT` |
| `is_input__backward_held` | `input_flags__held & INPUT_BACKWARD` |
| `is_input__game_settings_held` | `input_flags__held & INPUT_GAME_SETTINGS` |
| `is_input__lockon_held` | `input_flags__held & INPUT_LOCKON` |
| `is_input__use_held` | `input_flags__held & INPUT_USE` |
| `is_input__use_secondary_held` | `input_flags__held & INPUT_USE_SECONDARY` |
| `is_input__examine_held` | `input_flags__held & INPUT_EXAMINE` |
| `is_input__consume_held` | `input_flags__held & INPUT_CONSUME` |
| `is_input__turn_left_held` | `input_flags__held & INPUT_TURN_LEFT` |
| `is_input__turn_right_held` | `input_flags__held & INPUT_TURN_RIGHT` |
| `is_input__none_held` | `input_flags__held & INPUT_NONE` |

### Composite Input Queries (static inline)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `is_input__click_held` | `(Input*) -> bool` | `bool` | True if `INPUT_CLICK` is held **and** cursor has not moved (`cursor__3i32` equals `cursor__old__3i32` via `is_vectors_3i32__equal`). Distinguishes a stationary hold from a drag. |
| `is_input__click_dragged` | `(Input*) -> bool` | `bool` | True if `INPUT_CLICK` is held **and** cursor has moved (`cursor__3i32` differs from `cursor__old__3i32`). Distinguishes a drag from a stationary hold. |

### Input Consumption (static inline)

| Function | Signature | Description |
|----------|-----------|-------------|
| `consume_input` | `(Input*, Input_Flags__u32) -> void` | Clears the specified input flag bits from all three state fields (pressed, held, released). Used to prevent input from propagating to lower-priority handlers. |

### Mode Management (static inline)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `get_input_mode_of__input` | `(Input*) -> Input_Mode__u8` | `Input_Mode__u8` | Returns the current input mode. |
| `set_input_mode_of__input` | `(Input*, Input_Mode__u8) -> void` | `void` | Sets the input mode (e.g. switch between normal and writing). |

## Agentic Workflow

### Input Frame Lifecycle

Each frame, the engine processes input in this order (see
`manage_game__post_render` in `game.c`):

    1. poll_input(p_game, p_input)
       -> PLATFORM_poll_input(p_game, p_input)
       -> Platform fills pressed, held, released, cursor
    2. Game systems query input state via is_input__*_pressed/held/released
    3. UI system processes input (click, drag, type)
    4. Remaining input propagates to gameplay systems
    5. (End of frame — next poll_input overwrites state)

Note: `poll_input` is called in `manage_game__post_render`, which runs
after the scene's render pass. This means input is sampled at the end
of each frame and is available for the next frame's logic.

### Three-State Input Model

Every logical button exists in three simultaneous states each frame:

| State | Field | Meaning |
|-------|-------|---------|
| Pressed | `input_flags__pressed` | Button was just pressed this frame (rising edge). |
| Held | `input_flags__held` | Button is currently down (sustained). |
| Released | `input_flags__released` | Button was just released this frame (falling edge). |

A button that is pressed for one frame will appear in `pressed` and
`held` simultaneously. On the next frame (if still held), it will
appear only in `held`. On the frame it is released, it appears in
`released`.

### Click vs. Drag Detection

The engine distinguishes between a stationary click-hold and a drag
using cursor position comparison:

    if (is_input__click_held(p_input)) {
        // Cursor has NOT moved — stationary hold
    }
    if (is_input__click_dragged(p_input)) {
        // Cursor HAS moved — drag gesture
    }

Both functions require `INPUT_CLICK` to be in the held state. The
distinction is made by comparing `cursor__3i32` to `cursor__old__3i32`
via `is_vectors_3i32__equal`.

### Input Consumption Pattern

When a UI element or system handles an input, it should consume it
to prevent lower-priority systems from also responding:

    if (is_input__use_pressed(p_input)) {
        // Handle the action...
        consume_input(p_input, INPUT_USE);
        // Downstream systems will no longer see INPUT_USE
    }

`consume_input` clears the specified bits from all three state fields
(pressed, held, released) simultaneously.

### Writing Mode Pattern

Text entry uses a circular buffer and a separate input mode:

    // Switch to writing mode
    set_input_mode_of__input(p_input, INPUT_MODE__WRITING);

    // Platform routes keyboard input to the writing buffer
    // via buffer_input_for__writing(p_input, symbol)

    // UI text box polls for characters:
    unsigned char ch = poll_input_for__writing(p_input);
    if (ch) {
        // Process character (append to text, handle backspace, etc.)
    }

    // Return to normal mode
    set_input_mode_of__input(p_input, INPUT_MODE__NORMAL);

The `last_symbol` field provides peek-like access to the most recent
character without consuming it from the buffer.

The writing buffer is a power-of-2 sized circular buffer (default size
8, controlled by `MAX_QUANTITY_OF__SYMBOLS_IN__INPUT_WRITING_BUFFER__BIT_SHIFT`).
Read and write indices wrap using the buffer size as a mask.

### Client Input in Multiplayer

In multiplayer mode, each `Client` has its own `Input` struct:

    typedef struct Client_t {
        ...
        Input input_of__client;
        ...
    } Client;

The local player's input is polled via `PLATFORM_poll_input`. Remote
client inputs are received via game actions over TCP.

When `max_quantity_of__clients == 0` in `Game`, the engine uses
`Game.input` directly. Otherwise, it uses the per-client input from
the client pool.

### Relationship to Game

The `Game` struct contains a top-level `Input` field:

    typedef struct Game_t {
        Input input;
        ...
    } Game;

This is the primary input struct used in singleplayer. In multiplayer,
the per-client `input_of__client` fields are used instead. The
`poll_input` call in `manage_game__post_render` always targets
`get_p_input_from__game(p_game)`.

### Platform Implementation Requirements

When implementing a new backend, the following must be provided:

1. **`PLATFORM_poll_input(Game*, Input*)`** — Reads hardware input
   and populates the three flag fields and cursor position. The
   platform is responsible for computing pressed/held/released
   transitions from raw hardware state.

Optionally, the platform may override the default input macros by
defining `PLATFORM_INPUT` before `platform_defaults.h` is included,
then providing its own `INPUT_CODE_*`, `INPUT_*`, and
`QUANTITY_OF__INPUTS` definitions.

### Preconditions

- All functions require `p_input` to be non-null. No debug guards
  are present in the `static inline` functions — the caller is
  responsible for null checks.
- `poll_input` should only be called by `game.c` once per frame
  (in `manage_game__post_render`).
- `buffer_input_for__writing` should only be called by the platform
  input polling implementation when `input_mode__u8` is
  `INPUT_MODE__WRITING`.

### Postconditions

- After `initialize_input`: all flags are zero, cursor is at origin,
  writing buffer is empty, mode is `INPUT_MODE__NORMAL`.
- After `clear_input`: all three flag fields are `INPUT_NONE`,
  `cursor__old__3i32` is set to the previous `cursor__3i32`,
  `cursor__3i32` is zeroed.
- After `consume_input(p_input, flags)`: the specified bits are
  cleared from pressed, held, and released fields.

### Error Handling

No error reporting is performed by input functions. All query functions
return `false` / `0` for invalid or zero input. There are no
`debug_abort` or `debug_error` calls in this header.

### Thread Safety

Input operations are **not** thread-safe. The engine's cooperative
scheduling model (see `process.h` specification) ensures all input
operations occur on a single thread. `poll_input` is called exactly
once per frame before any systems read input state.
