is_vectors_3i32__out_of_bounds — core/include/vectors.h

Checks whether any component of a Vector__3i32 matches the sentinel value VECTOR__3i32__OUT_OF_BOUNDS (all components set to BIT(31), i.e. INT32_MIN on two's-complement systems).

Pre-conditions:
1. vector__3i32 is a valid Vector__3i32 value (passed by value, so always valid). No pointer or memory constraints.
2. No nullability concerns — the parameter is a struct passed by value.

Post-conditions:
1. Returns true if at least one of x__i32, y__i32, or z__i32 equals the corresponding component of VECTOR__3i32__OUT_OF_BOUNDS (BIT(31) / INT32_MIN).
2. Returns false if none of the three components match the sentinel.
3. The input vector is not modified (passed by const value).

Correctness Verdict: Correct

Semantic Alignment:
The function correctly implements its intent: it returns true when any component of the input vector equals the out-of-bounds sentinel. The logic uses OR across the three component-wise equality checks, which is the correct semantic for "is the vector out of bounds" (any single component being the sentinel marks the whole vector as out of bounds). The sentinel VECTOR__OUT_OF_BOUNDS is defined as {BIT(31), BIT(31), BIT(31)} where BIT(31) = (1U << 31) = 0x80000000U. This unsigned value, when stored in the int32_t fields of Vector__3i32 (via the (const Vector__3i32) cast), becomes INT32_MIN (-2147483648) on two's-complement systems. The comparison then compares int32_t to int32_t, which is well-defined.

Implementation Correctness:
Type compatibility — vector__3i32 is Vector__3i32 (struct of int32_t fields via Signed_Index__i32). VECTOR__3i32__OUT_OF_BOUNDS is (const Vector__3i32) VECTOR__OUT_OF_BOUNDS, so VECTOR__3i32__OUT_OF_BOUNDS.x__i32 is also int32_t. Both sides of each == comparison are int32_t. No implicit conversions or truncation issues.
Undefined behavior — none. No pointer arithmetic, no null dereference (struct passed by value, not pointer), no type punning, no out-of-bounds array access. The only subtle point is that BIT(31) produces an unsigned value (0x80000000U) that overflows int32_t when stored in the struct; this conversion is implementation-defined per the C standard, but on all two's-complement systems (the de facto and C2's dominant representation) it results in INT32_MIN. This is a widely-accepted pattern for sentinel values and is not considered a defect.
Validation — appropriate for the function's role. This is a low-level inline predicate; no input validation is needed since the parameter is a struct passed by value.

Side Effects:
No side effects. The function is a pure predicate: it reads the out-of-bounds sentinel constant and the input vector (by value) and returns a bool. No memory is mutated, no I/O occurs, and no global state is touched.
