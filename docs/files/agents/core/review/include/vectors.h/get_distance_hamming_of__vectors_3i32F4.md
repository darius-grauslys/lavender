get_distance_hamming_of__vectors_3i32F4 — core/include/vectors.h

Computes the Hamming (Manhattan/L1) distance between two Vector__3i32F4 vectors by summing the absolute differences of their x, y, and z components.

Pre-conditions:
1. Both vector parameters are passed by value; no null pointer constraints apply.
2. Each component (x__i32F4, y__i32F4, z__i32F4) is of type i32F4 (int32_t); any valid int32_t value is acceptable as input.
3. No validation is needed for this low-level inline helper; the caller is responsible for providing valid vectors.

Post-conditions:
1. Returns the sum of |vector_one.x - vector_two.x| + |vector_one.y - vector_two.y| + |vector_one.z - vector_two.z| as an i32F4 (int32_t).
2. Neither input vector is mutated (both passed by value).

Correctness Verdict: Correct

Semantic Alignment:
The implementation correctly computes the Hamming/Manhattan distance between two 3D vectors. The fixed-point representation (i32F4 with 4 bits of fractional precision) is a raw int32_t, so subtraction and abs() operate correctly on the underlying integer values — the fixed-point encoding preserves sign and ordering, meaning component-wise absolute differences are computed correctly. The computation matches the semantic intent: sum of absolute component-wise differences. This is consistent with the sibling function get_distance_hamming_of__vectors_3i32 which performs the same computation on Vector__3i32.

Implementation Correctness:
Type compatibility — abs() from <stdlib.h> takes int and returns int. i32F4 is typedef'd as int32_t. On target platforms where int is 32 bits (the common case assumed by this codebase, evidenced by widespread use of abs() on i32/Signed_Index__i32 values throughout vectors.h and numerics.h), the types are compatible with no truncation or implicit conversion issues. The return type i32F4 (int32_t) matches the result type of the addition.
Undefined behavior — abs(INT32_MIN) is technically undefined behavior on platforms where int is 32 bits, as the result cannot be represented in int. This could occur if the difference between two components equals INT32_MIN (e.g., one component is INT32_MIN and the other is 0). Additionally, the sum of three abs() results could overflow int32_t. However, these are pre-existing patterns consistent with the rest of the codebase (e.g., get_distance_hamming_of__vectors_3i32, get_manhattan_distance__of_vector_3i32_as__u32), and no overflow protection is applied in either sibling function. This is an accepted tradeoff in this codebase.
Validation — no validation is appropriate for this function; it is a low-level static inline helper. The caller is responsible for ensuring inputs are valid.

Side Effects:
No side effects. The function is pure — it takes both vectors by value and returns a computed i32F4 result without modifying any state, memory, or I/O.
