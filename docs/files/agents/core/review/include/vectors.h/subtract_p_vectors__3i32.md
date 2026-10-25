subtract_p_vectors__3i32 — core/include/vectors.h

Subtracts the components of the second vector from the first vector in-place, mutating the target vector.

Pre-conditions:
1. p_vector_one__target must be a non-null pointer to a writable Vector__3i32 object.
2. p_vector_two must be a non-null pointer to a readable Vector__3i32 object.

Post-conditions:
1. p_vector_one__target is mutated: x__i32, y__i32, and z__i32 each have the corresponding component of p_vector_two subtracted (i.e., target = target - other for all three axes).
2. p_vector_two is not modified.

Correctness Verdict: Correct

Semantic Alignment:
The implementation correctly performs component-wise subtraction: p_vector_one__target->x__i32 -= p_vector_two->x__i32, and likewise for y and z. This matches the semantic intent of "subtract_p_vectors" — subtracting one vector from another in-place. All three struct fields (x__i32, y__i32, z__i32) are accessed and modified. No member is omitted, no reordering occurs. The function is consistent with its sibling subtract_p_vectors__3i32F4 and add_p_vectors__3i32.

Implementation Correctness:
Type compatibility — both parameters are Vector__3i32 *, and the fields accessed (x__i32, y__i32, z__i32) are Signed_Index__i32 (i.e., int32_t). The -= operator operates on matching types with no implicit conversions or truncation.
No undefined behavior — no pointer arithmetic, no null dereference (assuming pre-conditions hold), no type punning, no out-of-bounds access. The function dereferences two pointers, which is safe as long as they are valid (caller responsibility).
No validation is needed — this is a low-level static inline helper. The caller is responsible for ensuring the pointers are valid.

Side Effects:
Mutates *p_vector_one__target: its x__i32, y__i32, and z__i32 fields are each decremented by the corresponding field of *p_vector_two. *p_vector_two is read-only; no side effects on it.
