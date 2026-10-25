is_input__consume_released — core/include/input/input.h

Tests whether the consume button is in the released state for this frame.

Pre-conditions:
1. p_input must be a non-null pointer to a valid (initialized) Input object.
2. input_flags__released holds this frame's release bitmask as populated by poll_input; its value is arbitrary otherwise.

Post-conditions:
1. Returns true if and only if the INPUT_CONSUME bit is set in p_input->input_flags__released; returns false otherwise.
2. The Input struct is not mutated.

Correctness Verdict: Correct

Semantic Alignment:
The implementation reads exactly the INPUT_CONSUME bit from the released flag set, matching the function's name and intent (a single-bit query). No extra bits are inspected and no state is altered.

Implementation Correctness:
Type compatibility — input_flags__released is Input_Flags__u32 (uint32_t) and INPUT_CONSUME is a bit-shift macro; the bitwise AND yields uint32_t, which is contextually converted to bool on return. No implicit conversion or truncation occurs. Type-wise this matches every sibling *_released accessor (e.g. is_input__forward_released) exactly.
Undefined behavior — p_input is dereferenced without a null check, but this is consistent with the engine's convention for low-level inline accessors (see the initialize_audio_effect review where the caller is responsible for validity). There is no pointer arithmetic, no out-of-bounds access, no type punning.
Validation — none is needed; this is a leaf inline query and the caller (e.g. scene__game.c:131) is responsible for passing a valid Input pointer. The existing test is_input__consume_released__returns_true_when_set confirms the expected true-on-set behavior.

Side Effects:
No side effects — the function performs a read-only access to p_input->input_flags__released.
