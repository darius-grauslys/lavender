is_input__use_secondary_held — core/include/input/input.h

Returns whether the "use secondary" action flag is currently held.

Pre-conditions:
1. p_input must be a non-null pointer to a valid Input struct.
No constraint is required on the contents of input_flags__held — it may be INPUT_NONE or any combination of input flag bits.

Post-conditions:
1. Returns true when the INPUT_USE_SECONDARY bit is set in p_input->input_flags__held, false otherwise.
2. The pointed-to Input object is not modified.

Correctness Verdict: Correct

Semantic Alignment:
The implementation checks exactly the INPUT_USE_SECONDARY bit within the held flags, which is precisely the semantic intent ("is use secondary held"). The held flags record actions active in both the previous and current frame (input_flags__held = input_flags__pressed_old & input_flags__pressed, see sdl_input.c), so the bit genuinely reflects a key held across frames. Semantic intent is fulfilled.

Implementation Correctness:
Type compatibility — input_flags__held is Input_Flags__u32 (uint32_t) (defines.h:1155, 1164). INPUT_USE_SECONDARY is defined as (INPUT_USE<<1) where INPUT_USE is (INPUT_LOCKON<<1), INPUT_LOCKON is (INPUT_GAME_SETTINGS<<1), and so on down to INPUT_FORWARD which is (1<<0). Following the chain, INPUT_USE_SECONDARY evaluates to the integer 128. The bitwise AND of uint32_t and int promotes the int to uint32_t per the usual arithmetic conversions; the result is uint32_t and is implicitly converted to bool on return (non-zero → true, zero → false). No truncation or precision loss. This is the same deliberate idiom used by every is_input__* accessor in this header.
No undefined behavior — no pointer arithmetic, no null dereference (p_input assumed valid by contract), no type punning, no out-of-bounds access.
No validation is performed or needed — this is a low-level inline query function; ensuring p_input validity is the caller's (poll_input / game loop's) responsibility, matching the role of all sibling accessors.

Side Effects:
No side effects — this is a pure, non-mutating query. The only observable effect is the returned boolean value.
