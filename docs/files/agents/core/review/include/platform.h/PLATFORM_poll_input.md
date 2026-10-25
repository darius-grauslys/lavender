# PLATFORM_poll_input

## 1. Header
- **Function name:** `PLATFORM_poll_input`
- **File of origin:** `core/include/platform.h` (declaration, line 352). Concrete reference implementation reviewed: `sdl/source/input/sdl_input.c` (line 315). Other implementations exist in `no_gui/source/NOT_IMPL.c` (empty stub) and `nds/source/input/nds_input.c`.

## 2. Semantic
Polls the current platform input state and updates the `Input` struct, deriving pressed/held/released transition flags and the cursor position for the current frame.

## 3. Pre-conditions
1. `p_game` must be a valid, non-null pointer to an initialized `Game` struct; it is dereferenced in writing mode via `SDL_poll_input__writing` and `get_elapsed_time__u32F20_of__game`.
2. `p_input` must be a valid, non-null pointer to an `Input` struct whose `input_flags__pressed` holds the previous frame's pressed bits (used for transition detection); if uninitialized, `pressed` is still correctly recomputed, but `held`/`released` will be garbage.
3. `p_input->input_flags__pressed_old` need not be pre-initialized; the function overwrites it unconditionally before use.
4. The SDL subsystem (video) must be initialized so `SDL_GetKeyboardState` and `SDL_GetMouseState` return valid data (implies the SDL build target, not the `no_gui` stub).
5. `p_input->input_mode__u8` must be set to either `INPUT_MODE__NORMAL` (0) or `INPUT_MODE__WRITING` (bit 1); the function switches behavior on this value.

## 4. Post-conditions
1. `input_flags__pressed_old` is set to the value `input_flags__pressed` held on entry (the prior frame's pressed bits), saved before the current flags are cleared.
2. `input_flags__pressed` reflects the current frame's active input bindings: keyboard bindings in `INPUT_MODE__NORMAL`, and mouse button bindings. In `INPUT_MODE__WRITING`, keyboard bindings do not contribute.
3. `input_flags__held` = `input_flags__pressed_old & input_flags__pressed` (bits that were pressed in the prior frame and remain pressed now).
4. `input_flags__released` = `(~input_flags__pressed) & input_flags__pressed_old` (bits pressed in the prior frame but no longer pressed now).
5. `cursor__3i32` is set to the current mouse cursor position (x, y from `SDL_GetMouseState`; z left at 0).
6. `cursor__old__3i32` holds the cursor position captured at the start of the call (the prior frame's position).
7. If `input_mode__u8 == INPUT_MODE__WRITING`, `SDL_poll_input__writing(p_game, p_input)` has been invoked.

## 5. Correctness Verdict
Correct

## 6. Semantic Alignment
The implementation fulfills the semantic intent of a single-frame input poll. The ordering is correct: the prior `input_flags__pressed` is saved into `pressed_old` (line 320-321) before `clear_input` zeroes the live flags, so the transition computation at the end (lines 371-379) compares the genuine prior frame against the freshly-sampled frame. `clear_input` only zeroes `held`/`pressed`/`released`/`cursor` and does not touch `pressed_old`, preserving the saved prior state. The held/released bitwise formulas are the standard frame-transition identities and match the field semantics (pressed = currently down, held = down across the boundary, released = down-then-up).

## 7. Implementation Correctness
- **Type compatibility:** Clean. `SDL_GetKeyboardState` returns `const u8 *`; indexed by `sdl_scancode`; results assigned to `u32` flags — no truncation. `SDL_GetMouseState` returns `u32`; masked against `sdl_mouse_button` and assigned to `u32 flags` — no truncation. `cursor__3i32.x__i32`/`y__i32` are `i32`, matching `SDL_GetMouseState`'s `int *` parameters (no conversion issue on the target ABI).
- **Undefined behavior:** No null dereference is guarded, but both pointers are contractually non-null (pre-conditions 1-2); dereferencing them is intentional, not a latent bug. `SDL_GetKeyboardState`/`SDL_GetMouseState` are SDL library entry points assumed initialized per pre-condition 4. The `for` index is `Index__u8` ranging over `SDL_QUANTITY_OF__INPUTS`; provided that bound is `< 256`, comparison is safe, and the binding table access `__SDL_INPUT_BINDINGS[index]` is in-range by construction. The `continue` on the `default` switch case and the explicit `INPUT_MODE__NORMAL`/`INPUT_MODE__WRITING` enumeration are exhaustive over the documented modes.
- **Validation:** Appropriate for a low-level platform layer; no internal validation is expected (consistent with the rest of the `PLATFORM_*` layer, which trusts callers). Note this is a platform abstraction: in the `no_gui` stub the body is empty, so consumers must not rely on input mutation for non-interactive builds — but that is a build-target contract, not a defect in this function.
- **No off-by-one, no type punning, no out-of-bounds** in the reviewed path.

## 8. Side Effects
- Mutates `p_input->input_flags__pressed`, `input_flags__pressed_old`, `input_flags__held`, `input_flags__released`, `cursor__3i32`, and `cursor__old__3i32`.
- Resets (zeroes) `input_flags__pressed`, `input_flags__held`, and `input_flags__released` as an intermediate step via `clear_input` before recomputing them.
- Calls `SDL_GetKeyboardState`, `SDL_GetMouseState`, and `get_input_mode_of__input` (all read-only observers with respect to `p_input`).
- In writing mode, invokes `SDL_poll_input__writing(p_game, p_input)`, which may mutate writing-buffer state (`writing_buffer`, `last_symbol`, read index, hold/write timers) and read `p_game` timing state.
- No observable effects on `p_game` outside of the writing-mode callee.
