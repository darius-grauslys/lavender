is_input__left_held — core/source/input/input.c

Returns whether the "left" input is currently held (pressed in both the previous and current frame).

Pre-conditions:
1. p_input must be a non-null pointer to a valid, initialized Input object. This is a Lavender-style query; null-check is intentionally the caller's responsibility (consistent with every sibling is_input__* accessor).
No constraint is required on the contents of input_flags__held — it may be INPUT_NONE or any combination of input flag bits.

Post-conditions:
1. Returns true when the INPUT_LEFT bit is set in p_input->input_flags__held, false otherwise.
2. The pointed-to Input object is not modified.

Correctness Verdict: Correct

Semantic Alignment:
The implementation checks exactly the INPUT_LEFT bit within the held flags, which is precisely the semantic intent ("is left held"). The platform layer (sdl_input.c:371-374) computes input_flags__held as input_flags__pressed_old & input_flags__pressed, and INPUT_LEFT (platform_defaults.h:204) is bound to the A key / SDL_SCANCODE_A, so the held flag genuinely reflects a key held across the previous and current frames. Semantic intent is fulfilled.

Implementation Correctness:
Type compatibility — input_flags__held is Input_Flags__u32 (uint32_t); INPUT_LEFT is the integer constant 2 (int). The bitwise AND promotes the int operand to uint32_t via the usual arithmetic conversions, yielding a uint32_t, which is then implicitly converted to bool for the return. Per the C standard any nonzero scalar converts to _Bool as 1 (true), zero as 0 (false), so this is well-defined with no truncation or data loss. This is the same deliberate idiom used by every is_input__* accessor in this header.
No undefined behavior — no pointer arithmetic, no null dereference (p_input assumed valid by contract), no type punning, no out-of-bounds access.
No validation is performed or needed — this is a low-level inline query function; ensuring p_input validity is the caller's (poll_input / game loop's) responsibility, matching the role of all sibling accessors.

Side Effects:
No side effects — this is a pure, non-mutating query. The only observable effect is the returned boolean value.
