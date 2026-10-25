# Input — Game-action-oriented input flags, cursor, and writing buffer

**Sources:** `core/source/input/input.c` + `core/include/input/input.h`

## Surface Concerns

The input module translates raw hardware state into game-action-oriented flags. It does not contain any platform-specific code — the backend fills raw state via `PLATFORM_poll_input`, and the core module samples those flags to dispatch `Game_Action` events. The `Input` struct is defined in `defines.h`; it is embedded in `Game` (`Input input`) for single-player and in `Client` (`Input input_of__client`) per connected client.

Layer: L1 (core services). Called from `manage_game__post_render` in `game.c` once per frame, and from the UI system for writing input.

- **Input flag model** — three per-frame flag fields (`input_flags__pressed`, `_held`, `_released`) capture transient and persistent input states. Each action flag occupies one bit of `Input_Flags__u32`. A single previous-frame snapshot, `input_flags__pressed_old`, is kept for edge detection (not used by all platforms).
- **Cursor tracking** — `cursor__3i32` / `cursor__old__3i32` pair updated by the backend. Click vs. drag detection compares the pair via `is_vectors_3i32__equal()`.
- **Writing buffer** — fixed 8-character circular buffer with separate read/write indices. Filled from the backend during writing mode; consumed character-by-character by UI text fields.
- **Input mode** — `INPUT_MODE__NORMAL` (0) and `INPUT_MODE__WRITING` (bit 1) gate keyboard input. Writing mode enables character accumulation into the writing buffer.
- **Game-action bridge** — `poll_input()` is the only core module that directly triggers `Game_Action` events. This is the engine's sole state-mutation entry point for player intent. Dispatched only in multiplayer mode (when `p_game->pM_clients` is non-NULL); single-player scenes must handle input polling separately.

## Public API Surface

### Key Types

**`Input`** — defined in `defines.h`. Key members:
- `Input_Flags__u32 input_flags__pressed` — flags set this frame, not last. Transient, consumed by `consume_input()`.
- `Input_Flags__u32 input_flags__held` — flags set this frame AND last frame. Persistent while held.
- `Input_Flags__u32 input_flags__released` — flags set last frame, not this frame. Transient, consumed by `consume_input()`.
- `Input_Flags__u32 input_flags__pressed_old` — previous-frame snapshot of pressed flags (the only `*_old` field; not used by all platforms).
- `Vector__3i32 cursor__3i32`, `cursor__old__3i32` — current and previous cursor position.
- `unsigned char writing_buffer[MAX_QUANTITY_OF__SYMBOLS_IN__INPUT_WRITING_BUFFER]` — 8-slot circular text buffer.
- `unsigned char last_symbol` — the most recent symbol written by `buffer_input_for__writing`.
- `Index__u8 index_of__writing_buffer__read`, `index_of__writing_buffer__write` — circular buffer pointers.
- `Input_Mode__u8 input_mode__u8` — `INPUT_MODE__NORMAL` or `INPUT_MODE__WRITING`.

**Input flags** (directional/action flags, defined in `platform_defaults.h`):
`INPUT_FORWARD`, `INPUT_LEFT`, `INPUT_RIGHT`, `INPUT_BACKWARD`, `INPUT_GAME_SETTINGS`, `INPUT_LOCKON`, `INPUT_USE`, `INPUT_USE_SECONDARY`, `INPUT_EXAMINE`, `INPUT_CONSUME`, `INPUT_TURN_RIGHT`, `INPUT_TURN_LEFT`, `INPUT_CLICK`. Each occupies one bit; `INPUT_NONE` is 0 for clearing.

### Key Functions

- `void initialize_input(Input *p_input);` — zeroes the entire struct.
- `void poll_input(Game *p_game, Input *p_input);` — bridges input flags to `Game_Action` dispatch via `dispatch_game_action__input`.
- `unsigned char poll_input_for__writing(Input *p_input);` — returns next character from writing buffer, advancing read index; returns 0 when empty.
- `void buffer_input_for__writing(Input *p_input, char symbol);` — appends character to writing buffer at write index, and records it in `last_symbol`.
- `unsigned char get_last_symbol_of__input_for__writing(Input *p_input);` — returns `last_symbol`.
- `static inline void clear_input(Input *p_input);` / `static inline void consume_input(Input *p_input, Input_Flags__u32 input_flags);` — reset and flag-consuming helpers.
- `static inline Input_Mode__u8 get_input_mode_of__input(Input *p_input);` / `static inline void set_input_mode_of__input(Input *p_input, Input_Mode__u8 input_mode__u8);` — mode getters/setters.
- Multiple flag-check helpers (`*_pressed`, `*_held`, `*_released` variants for each flag, including `none` and `click`) plus `is_input__click_dragged()` for cursor-based drag detection.

### Writing buffer constants

`MAX_QUANTITY_OF__SYMBOLS_IN__INPUT_WRITING_BUFFER = 8` (bit shift 3). Buffer wraps via `& MASK(3)`.

## Key Files Table

| File | Role |
|------|------|
| `core/source/input/input.c` | `initialize_input`, `poll_input`, writing buffer operations |
| `core/include/input/input.h` | `clear_input`, `consume_input`, flag-check helpers + drag check, mode helpers |
