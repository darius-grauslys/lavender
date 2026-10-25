subtract_p_vectors__3i32F4 — core/include/vectors.h

In-place subtraction of two fixed-point 3D vectors with 4-bit fractional precision.

Pre-conditions:
1. p_vector_one__target must be a non-null pointer to a writable Vector__3i32F4 object.
2. p_vector_two must be a non-null pointer to a valid (readable) Vector__3i32F4 object.
3. Both pointers must not alias the same memory (i.e., p_vector_one__target != p_vector_two); if they did, the subtraction would zero every component, which is semantically incorrect for a general subtraction operation.

Post-conditions:
1. p_vector_one__target is mutated: each of its components (x__i32F4, y__i32F4, z__i32F4) is reduced by the corresponding component of p_vector_two.
2. p_vector_two is unchanged.
3. The function returns void.

Correctness Verdict: Correct

Semantic Alignment:
The implementation correctly performs component-wise subtraction of p_vector_two from p_vector_one__target. Each of the three struct fields (x__i32F4, y__i32F4, z__i32F4) is handled identically and correctly via the -= operator. The result matches the semantic intent of subtracting one 3D fixed-point vector from another in-place. All three struct fields are covered — no member is omitted. This is consistent with the non-pointer counterpart subtract_vectors__3i32F4 which performs the same computation and returns a new vector.

Implementation Correctness:
Type compatibility — both parameters are Vector__3i32F4 * (pointer to struct), and the struct fields accessed (x__i32F4, y__i32F4, z__i32F4) are of type i32F4 (int32_t). The -= operator operates on matching types. No implicit conversions or truncation occur.
Undefined behavior — no pointer arithmetic, no null dereference (pre-conditions require non-null pointers), no type punning, no out-of-bounds access. The struct has exactly three fields and all three are accessed.
No validation is performed — this is a low-level inline helper. Validation of pointer non-nullness and non-aliasing is the caller's responsibility, consistent with the pattern used throughout vectors.h.

Side Effects:
p_vector_one__target is mutated: its x__i32F4, y__i32F4, and z__i32F4 fields are each decremented by the corresponding field of p_vector_two. No other memory is modified. p_vector_two is read but not modified.
