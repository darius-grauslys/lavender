subtract_vectors__3i32 — core/include/vectors.h, lines 533-541

Subtracts two 3-component vectors of 32-bit signed integers, returning a new vector where each component is the difference of the corresponding components (vector_one - vector_two).

Pre-conditions:
1. vector_one is a valid Vector__3i32 value (no constraints on individual component values).
2. vector_two is a valid Vector__3i32 value (no constraints on individual component values).
3. Both parameters are passed by value, so no pointer or null checks are required.

Post-conditions:
1. A new Vector__3i32 is returned with x__i32 = vector_one.x__i32 - vector_two.x__i32, y__i32 = vector_one.y__i32 - vector_two.y__i32, z__i32 = vector_one.z__i32 - vector_two.z__i32.
2. Neither input parameter is modified (passed by value).

Correctness Verdict: Correct

Semantic Alignment:
The implementation correctly performs component-wise subtraction of vector_two from vector_one. Each of the three struct fields (x__i32, y__i32, z__i32) is assigned exactly once in the returned compound literal, with no reordering or omission. This matches the semantic intent of vector subtraction and is consistent with the sibling functions add_vectors__3i32, subtract_vectors__3i32F4, and subtract_vectors__3i32F20.

Implementation Correctness:
Type compatibility — all field accesses use the int32_t (Signed_Index__i32) members of Vector__3i32. The subtraction operands and the compound literal initializer are all of the same type (int32_t), so no implicit conversions or truncation occur.
Undefined behavior — no pointer arithmetic, no null dereference, no type punning, no out-of-bounds access. The function operates entirely on value parameters.
No validation is needed — this is a low-level pure computation function. Validation of vector values (e.g., overflow checking) is the caller's responsibility, consistent with the pattern used by the sibling add/subtract vector functions.

Side Effects:
No side effects. The function is pure: it reads its two value parameters and returns a newly constructed Vector__3i32 without modifying any external state or the input parameters.
