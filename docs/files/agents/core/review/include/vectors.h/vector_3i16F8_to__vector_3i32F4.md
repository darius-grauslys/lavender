vector_3i16F8_to__vector_3i32F4 — core/include/vectors.h, lines 332-343

Converts a Vector__3i16F8 (three int16_t components with 8 fractional bits each) into a Vector__3i32F4 (three int32_t components with 4 fractional bits each) by right-shifting each component by 4 bits.

Pre-conditions:
1. No pointer parameters; the function receives a Vector__3i16F8 by value.
2. No null-pointer or validity constraints — the input is a value type.

Post-conditions:
1. Returns a Vector__3i32F4 whose x, y, and z fields are the i16F8 components of the input right-shifted by FRACTIONAL_PERCISION_4__BIT_SIZE (4 bits), effectively converting from 8 fractional bits to 4 fractional bits.
2. The original Vector__3i16F8 input is not modified (passed by value).

Correctness Verdict: Correct

Semantic Alignment:
The function correctly converts from i16F8 (8 fractional bits) to i32F4 (4 fractional bits). The shift amount is 4, which equals the difference in fractional precision (8 - 4 = 4). For a value stored as real_value * 2^8, right-shifting by 4 yields real_value * 2^4, which is the correct representation in i32F4. The struct initializer assigns all three fields (x__i32F4, y__i32F4, z__i32F4) in the correct order, matching the Vector__3i32F4 struct definition. The inverse function vector_3i32F4_to__vector_3i16F8 uses a corresponding left-shift by 4, confirming the pair is symmetric.

Implementation Correctness:
Type compatibility — i16F8 is int16_t; under C integer promotion it is promoted to int before the shift, and the result (int) is stored in i32F4 (int32_t). On platforms where int is 32 bits (the only platforms where int32_t exists), there is no truncation.
Undefined behavior — no undefined behavior. Right-shifting a negative signed integer is implementation-defined (not undefined) per the C standard. The codebase provides ARITHMETRIC_R_SHIFT for portable arithmetic right shifts, but vector conversion functions (e.g., vector_3i32F4_to__vector_3u8) consistently use raw >> operators. This is a codebase-wide pattern, not a defect specific to this function.
Validation — no validation is needed; this is a pure computation with value-type parameters.

Side Effects:
No side effects. The function is pure — it takes a value-type input and returns a new value without modifying any global state or the input.
