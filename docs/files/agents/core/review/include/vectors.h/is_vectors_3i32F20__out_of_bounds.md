is_vectors_3i32F20__out_of_bounds — core/include/vectors.h, lines 138-148

Checks whether any component (x, y, or z) of a Vector__3i32F20 equals the out-of-bounds sentinel value (BIT(31), i.e. INT32_MIN on two's complement systems).

Pre-conditions:
1. The parameter vector__3i32F20 is passed by value; no null-pointer concern exists.
2. Each field (x__i32F20, y__i32F20, z__i32F20) is of type i32F20 (int32_t); no additional range constraint is required.

Post-conditions:
1. Returns true if any component of the input vector matches VECTOR__3i32F20__OUT_OF_BOUNDS (the sentinel where every component is BIT(31)).
2. Returns false if no component matches the sentinel.
3. The input vector is not modified (passed by value, const-qualified).

Correctness Verdict: Correct

Semantic Alignment:
The implementation faithfully fulfills the semantic intent: it returns true when any component of the vector matches the out-of-bounds sentinel. The comparison uses the same VECTOR__3i32F20__OUT_OF_BOUNDS macro that callers use to set the sentinel (e.g., get_ray__out_of_bounds in ray.h), ensuring consistency between sentinel assignment and detection. The logic is identical in structure to the sibling functions is_vectors_3i32__out_of_bounds and is_vectors_3i32F4__out_of_bounds, which use the same BIT(31) sentinel for their respective vector types.

Implementation Correctness:
Type compatibility — VECTOR__3i32F20__OUT_OF_BOUNDS.x__i32F20 is i32F20 (int32_t) and vector__3i32F20.x__i32F20 is also i32F20 (int32_t). The == comparison is between two int32_t values; no implicit conversions or truncation occur. The same applies to the y and z component comparisons.
Undefined behavior — none. The function performs only integer comparisons on values passed by value. There is no pointer arithmetic, no null dereference, no type punning, and no out-of-bounds array access.
Validation — the function's role is to detect a sentinel value, not to validate caller-provided ranges. No additional validation is needed or expected at this level.

Side Effects:
No side effects. The function is pure: it takes its argument by value (const-qualified) and returns a boolean without modifying any state.
