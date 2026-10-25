add_p_vectors__3i32F4 — core/include/vectors.h

Adds the components of p_vector_two to p_vector_one in-place, mutating p_vector_one to hold the component-wise sum of both vectors.

Pre-conditions:
1. p_vector_one must be a non-null pointer to a writable Vector__3i32F4 object.
2. p_vector_two must be a non-null pointer to a valid Vector__3i32F4 object.
3. Both pointers must point to properly allocated Vector__3i32F4 structs.

Post-conditions:
1. p_vector_one is mutated: x__i32F4, y__i32F4, and z__i32F4 each hold the sum of the corresponding component from p_vector_one and p_vector_two.
2. p_vector_two is unchanged (read-only access).

Correctness Verdict: Correct

Semantic Alignment:
The function correctly implements component-wise vector addition using the += operator on all three fields of Vector__3i32F4. All three struct members (x__i32F4, y__i32F4, z__i32F4) are handled — no member is omitted or reordered. The implementation matches the semantic intent of "adding p_vectors" (pointer-based variant), consistent with the sibling function add_vectors__3i32F4 which performs the same addition by value.

Implementation Correctness:
Type compatibility — both parameters are Vector__3i32F4 *, and the fields accessed (x__i32F4, y__i32F4, z__i32F4) are of type i32F4 (typedef int32_t). The += operator operates between i32F4 values, matching field types exactly. No implicit conversions or truncation occur.
Undefined behavior — no pointer arithmetic, no null dereference (pre-condition requires non-null), no type punning, no out-of-bounds access. All three struct fields are accessed correctly.
Validation — no validation is needed. This is a low-level static inline helper; the caller is responsible for ensuring pointers are valid.

Side Effects:
p_vector_one is mutated in-place — all three components (x__i32F4, y__i32F4, z__i32F4) are modified. p_vector_two is read but not modified.
