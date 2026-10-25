is_vectors_3i32__equal — core/include/vectors.h

Compares two 3D integer vectors component-wise for equality.

Pre-conditions:
1. vector_1 is a valid Vector__3i32 (passed by value, so always valid).
2. vector_2 is a valid Vector__3i32 (passed by value, so always valid).
3. No null-pointer constraints apply — both parameters are passed by value, not by pointer.

Post-conditions:
1. Returns true if and only if all three components (x__i32, y__i32, z__i32) of vector_1 are equal to the corresponding components of vector_2.
2. Returns false if any single component differs.
3. Neither input vector is modified — the function is non-mutating.

Correctness Verdict: Correct

Semantic Alignment:
The implementation fulfills the semantic intent of comparing two 3D integer vectors for equality. All three struct fields (x__i32, y__i32, z__i32) are compared using the == operator, with logical AND chaining. No field is omitted or reordered. The function correctly delegates to direct field comparison, consistent with the pattern used by the sibling functions is_vectors_3i32F4__equal and is_vectors_3i32F20__equal.

Implementation Correctness:
Type compatibility — both parameters are Vector__3i32, and each field accessed (x__i32, y__i32, z__i32) is of type Signed_Index__i32 (int32_t). The == operator is well-defined for int32_t. No implicit conversions or truncation occur.
No undefined behavior — no pointer arithmetic, no null dereference, no type punning, no out-of-bounds access. Both parameters are passed by value, eliminating null-pointer risk.
No validation is needed — this is a pure comparison function operating on value types. Validation of vector contents (e.g., out-of-bounds checks) is the caller's responsibility.

Side Effects:
No side effects. The function is pure — it reads only its parameters and returns a boolean result without modifying any state or calling any external functions.
