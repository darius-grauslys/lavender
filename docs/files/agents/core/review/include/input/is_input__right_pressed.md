is_input__right_pressed — core/include/input/input.h

Checks whether the right-direction input was pressed this frame by testing the INPUT_RIGHT bit in the pressed-inputs bitmask.

Pre-conditions:
1. p_input must be a non-null pointer to a valid Input struct.
2. The Input struct must have been initialized (initialize_input memsets it to zero) before the pressed bitmasks are meaningfully populated.
3. input_flags__pressed is only current after the platform poll layer (PLATFORM_poll_input, invoked via poll_input) has run for the frame.

Post-conditions:
1. Returns true if the INPUT_RIGHT bit (value 4) is set in p_input->input_flags__pressed; returns false otherwise.
2. The Input struct is not modified — no state mutation occurs.

Correctness Verdict: Correct

Semantic Alignment:
The name is_input__right_pressed expresses "was the right input pressed." The implementation tests INPUT_RIGHT against the input_flags__pressed bitmask, which by convention (see the sibling is_input__*__held and is_input__*__released accessors, and poll_input in input.c where input_flags__pressed is referenced alongside input_flags__held and input_flags__released) holds the inputs whose press edge was detected this frame. The computation matches the semantic intent exactly — no semantic drift, no off-by-one.

Implementation Correctness:
- Type compatibility: input_flags__pressed is Input_Flags__u32 (uint32_t). INPUT_RIGHT expands to the macro chain INPUT_LEFT<<1 = INPUT_FORWARD<<2 = (1<<2), an int literal evaluating to 4. The bitwise & performs the usual arithmetic conversions, converting the int operand to uint32_t; the resulting uint32_t is then implicitly converted to bool per C11 §6.3.1.2 (0 -> false, non-zero -> true). No truncation occurs — the result is either 0 or 4, both representable as bool. This implicit conversion is intentional and is the standard, well-defined C idiom for bit-flag testing.
- No undefined behavior: no pointer arithmetic, no null dereference (non-null is a pre-condition), no type punning, no out-of-bounds access. The member access p_input->input_flags__pressed references a field that exists in struct Input (defines.h:1163).
- Validation: none is needed — this is a low-level inline accessor. Ensuring p_input is non-null and that the struct is initialized is the caller's responsibility, consistent with the rest of the is_input__* accessor family.

Side Effects:
No side effects — the function only reads from the pointed-to Input struct and does not modify any state.
