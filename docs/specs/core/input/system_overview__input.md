# System Overview: Input System

## Purpose

The input system provides a unified, platform-independent abstraction for
capturing and querying user input each frame. It tracks three simultaneous
states for each logical button (pressed, held, released), manages cursor
position for click and drag detection, and provides a circular writing
buffer for text entry. All platform-specific input hardware access is
delegated to a single `PLATFORM_poll_input` function, while all query and
consumption logic is platform-independent.

## Architecture

### Data Hierarchy

    Game
    +-- Input                              (primary input, singleplayer)
    |   +-- Input_Flags__u32 input_flags__pressed     (rising edge this frame)
    |   +-- Input_Flags__u32 input_flags__held         (sustained this frame)
    |   +-- Input_Flags__u32 input_flags__released     (falling edge this frame)
    |   +-- Input_Flags__u32 input_flags__pressed_old  (previous frame pressed)
    |   +-- Vector__3i32 cursor__3i32                  (current cursor position)
    |   +-- Vector__3i32 cursor__old__3i32             (previous cursor position)
    |   +-- unsigned char writing_buffer[8]            (circular text buffer)
    |   +-- unsigned char last_symbol                  (most recent character)
    |   +-- Index__u8 index_of__writing_buffer__read   (read index)
    |   +-- Index__u8 index_of__writing_buffer__write  (write index)
    |   +-- Input_Mode__u8 input_mode__u8              (normal / writing)
    |
    +-- Client_Pool (multiplayer)
        +-- Client[0..N]
            +-- Input input_of__client                 (per-client input)

### Key Types

| Type | Role |
|------|------|
| `Input` | Central input state struct. Holds button state bitmasks, cursor positions, writing buffer, and input mode. Owned by `Game` (singleplayer) or `Client` (multiplayer). |
| `Input_Flags__u32` | 32-bit bitmask where each bit corresponds to a logical input button. Used for pressed, held, and released state fields. |
| `Input_Mode__u8` | Enum-like byte controlling whether input is routed to gameplay (normal) or to the text writing buffer (writing mode). |
| `Input_Code__u32` | Sequential integer identifiers (0–13) for each logical input. Used to map between code indices and bitmask flags. |
| `Vector__3i32` | 3-component signed integer vector used for cursor position tracking. |

### Constants

| Macro | Default | Description |
|-------|---------|-------------|
| `QUANTITY_OF__INPUTS` | 14 | Total number of logical input buttons. |
| `MAX_QUANTITY_OF__SYMBOLS_IN__INPUT_WRITING_BUFFER` | `BIT(3)` = 8 | Size of the circular writing buffer. Must be a power of 2. |
| `INPUT_NONE` | 0 | No input flag set. |
| `INPUT_FORWARD` through `INPUT_CLICK` | `BIT(0)` through `BIT(12)` | Individual input flag bits. |

## Three-State Input Model

Every logical button exists in three simultaneous bitmask fields each frame:

    +-------------------+----------------------------+----------------------------+
    | Frame N-1         | Frame N                    | Frame N+1                  |
    +-------------------+----------------------------+----------------------------+
    | (button not held) | pressed=1, held=1          | pressed=0, held=1          |
    |                   | (rising edge)              | (sustained)                |
    +-------------------+----------------------------+----------------------------+
    |                   | Frame N+2                  |                            |
    |                   | released=1, held=0         |                            |
    |                   | (falling edge)             |                            |
    +-------------------+----------------------------+----------------------------+

- **Pressed**: Button was just pressed this frame (rising edge). Also appears
  in held simultaneously.
- **Held**: Button is currently down (sustained across frames).
- **Released**: Button was just released this frame (falling edge).

The platform backend is responsible for computing these three states from
raw hardware input during `PLATFORM_poll_input`.

## Cursor and Click/Drag Detection

The input system tracks two cursor positions per frame:

    cursor__old__3i32  <--  saved from previous frame's cursor__3i32
    cursor__3i32       <--  populated by PLATFORM_poll_input

These two positions enable distinguishing between stationary holds and drags:

| Query Function | Condition | Meaning |
|----------------|-----------|---------|
| `is_input__click_held` | `INPUT_CLICK` held AND `cursor__3i32 == cursor__old__3i32` | Stationary hold (no movement). |
| `is_input__click_dragged` | `INPUT_CLICK` held AND `cursor__3i32 != cursor__old__3i32` | Drag gesture (cursor moved while held). |

Cursor comparison uses `is_vectors_3i32__equal` from the vector utilities.

## Writing Buffer

Text entry uses a power-of-2 sized circular buffer with separate read and
write indices:

    writing_buffer[0] [1] [2] [3] [4] [5] [6] [7]
                   ^                   ^
                   read                write

    buffer_input_for__writing(p_input, 'A')
        -> writing_buffer[write] = 'A'
        -> write = (write + 1) & (BUFFER_SIZE - 1)

    poll_input_for__writing(p_input)
        -> ch = writing_buffer[read]
        -> read = (read + 1) & (BUFFER_SIZE - 1)
        -> return ch

The `last_symbol` field provides non-consuming peek access to the most
recently written character via `get_last_symbol_of__input_for__writing`.

Writing mode is activated by setting `input_mode__u8` to
`INPUT_MODE__WRITING`. When in this mode, the platform backend routes
keyboard/character input into the writing buffer via
`buffer_input_for__writing` instead of (or in addition to) setting
button flags.

## Lifecycle

### 1. Initialization

    initialize_input(p_input);
        -> All flag fields set to INPUT_NONE (0).
        -> Both cursor vectors set to origin (0, 0, 0).
        -> Writing buffer zeroed, read/write indices set to 0.
        -> input_mode__u8 set to INPUT_MODE__NORMAL (0).

### 2. Per-Frame Polling

Called once per frame in `manage_game__post_render`:

    poll_input(p_game, p_input);
        -> Internally calls PLATFORM_poll_input(p_game, p_input).
        -> Platform reads hardware state and populates:
            - input_flags__pressed  (rising edges)
            - input_flags__held     (sustained buttons)
            - input_flags__released (falling edges)
            - cursor__3i32          (current cursor/touch position)
        -> cursor__old__3i32 is preserved from the previous frame.

### 3. Query Phase

Game systems and UI query input state using static inline helpers:

    if (is_input__use_pressed(p_input)) {
        // Handle use action on rising edge
    }
    if (is_input__click_dragged(p_input)) {
        // Handle drag gesture
    }

### 4. Consumption

When a system handles an input, it consumes it to prevent propagation:

    consume_input(p_input, INPUT_USE);
        -> Clears INPUT_USE from pressed, held, and released simultaneously.
        -> Downstream systems will no longer see INPUT_USE this frame.

### 5. Clear

    clear_input(p_input);
        -> Saves cursor__3i32 into cursor__old__3i32.
        -> Zeroes cursor__3i32.
        -> Clears pressed, held, and released flags to INPUT_NONE.

## Integration with UI System

The UI system is a primary consumer of input state. The `UI_Manager` queries
input to determine which `UI_Element` is focused and dispatches input events
to element handlers:

    UI_Manager
        -> Queries is_input__click_pressed / is_input__click_held /
           is_input__click_dragged / is_input__click_released
        -> Dispatches to UI_Element handlers:
            - m_ui_clicked_handler   (on click press)
            - m_ui_dragged_handler   (on drag)
            - m_ui_dropped_handler   (on click release after drag)
            - m_ui_receive_drop_handler (on receiving a dropped element)
        -> Consumes input after handling to prevent gameplay systems
           from responding to UI interactions.

## Integration with Multiplayer

In multiplayer mode, each `Client` maintains its own `Input` struct:

    Client
    +-- Input input_of__client

- The local player's input is polled via `PLATFORM_poll_input` as normal.
- Remote client inputs are received via game actions over TCP and written
  into the corresponding client's `input_of__client`.
- When `max_quantity_of__clients == 0` in `Game`, the engine uses
  `Game.input` directly (singleplayer path).
- When clients are active, `get_p_input_from__game(p_game)` returns the
  appropriate per-client input.

## Input Frame Lifecycle Summary

    +-----------------------------------------------------------------+
    | manage_game__post_render (once per frame)                       |
    |                                                                 |
    |  1. poll_input(p_game, p_input)                                |
    |     +-> PLATFORM_poll_input(p_game, p_input)                   |
    |         +-> Reads hardware, fills pressed/held/released/cursor  |
    |                                                                 |
    |  2. Game systems query: is_input__*_pressed/held/released      |
    |                                                                 |
    |  3. UI system processes input (click, drag, type)              |
    |     +-> consume_input() for handled inputs                     |
    |                                                                 |
    |  4. Remaining input propagates to gameplay systems             |
    |     +-> consume_input() for handled inputs                     |
    |                                                                 |
    |  5. End of frame — next poll_input overwrites state            |
    +-----------------------------------------------------------------+

## Platform Implementation Requirements

When implementing a new platform backend, the following must be provided:

1. **`PLATFORM_poll_input(Game*, Input*)`** — Reads hardware input and
   populates the three flag fields (`input_flags__pressed`,
   `input_flags__held`, `input_flags__released`) and cursor position
   (`cursor__3i32`). The platform is responsible for computing
   pressed/held/released transitions from raw hardware state.

2. Optionally, the platform may override the default input flag/code
   macros by defining `PLATFORM_INPUT` before `platform_defaults.h` is
   included, then providing its own `INPUT_CODE_*`, `INPUT_*`, and
   `QUANTITY_OF__INPUTS` definitions.

3. When `input_mode__u8` is `INPUT_MODE__WRITING`, the platform should
   route character input into the writing buffer via
   `buffer_input_for__writing(p_input, symbol)`.

## Capacity Constraints

- The writing buffer holds at most
  `MAX_QUANTITY_OF__SYMBOLS_IN__INPUT_WRITING_BUFFER` (default 8)
  characters. If the producer (platform) writes faster than the consumer
  (UI text box) reads, older characters will be overwritten.
- `Input_Flags__u32` supports up to 32 logical input buttons. The default
  configuration uses bits 0–12 (13 buttons), leaving bits 13–31 available
  for platform-specific or game-specific extensions.
- There is exactly one `Input` per `Game` (singleplayer) or one per
  `Client` (multiplayer).

## Preconditions

- All functions require `p_input` to be non-null. No debug guards are
  present in the static inline functions — the caller is responsible for
  null checks.
- `poll_input` should only be called once per frame (in
  `manage_game__post_render`).
- `buffer_input_for__writing` should only be called by the platform input
  polling implementation when `input_mode__u8` is `INPUT_MODE__WRITING`.

## Postconditions

- After `initialize_input`: all flags are zero, cursor is at origin,
  writing buffer is empty, mode is `INPUT_MODE__NORMAL`.
- After `clear_input`: all three flag fields are `INPUT_NONE`,
  `cursor__old__3i32` is set to the previous `cursor__3i32`,
  `cursor__3i32` is zeroed.
- After `consume_input(p_input, flags)`: the specified bits are cleared
  from pressed, held, and released fields.

## Error Handling

No error reporting is performed by input functions. All query functions
return `false` / `0` for invalid or zero input. There are no `debug_abort`
or `debug_error` calls in the input header.

## Thread Safety

Input operations are **not** thread-safe. The engine's cooperative
scheduling model ensures all input operations occur on a single thread.
`poll_input` is called exactly once per frame before any systems read
input state.
