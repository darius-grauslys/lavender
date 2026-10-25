is_vectors_3i32F4__out_of_bounds — core/include/vectors.h

Checks whether any component (x, y, or z) of a Vector__3i32F4 equals the sentinel out-of-bounds value BIT(31).

Pre-conditions:
1. The function takes a const Vector__3i32F4 by value — no pointer parameters, so no null check is needed.
2. The vector components are i32F4 (int32_t) values. No range constraint is required for the function to execute.
3. The sentinel VECTOR__3i32F4__OUT_OF_BOUNDS is defined as (const Vector__3i32F4) VECTOR__OUT_OF_BOUNDS, where VECTOR__OUT_OF_BOUNDS is { BIT(31), BIT(31), BIT(31) }. BIT(31) is ((1U) << 31) = 0x80000000.

Post-conditions:
1) Returns true if any of x__i32F4, y__i32F4, or z__i32F4 equals BIT(31) (the sentinel value).
2) Returns false if none of the components match the sentinel.
3) The input vector is not modified (passed by value as const).

Correctness Verdict: Correct

Semantic Alignment:
The function correctly checks all three components (x, y, z) against the out-of-bounds sentinel value. The Vector__3i32F4 struct (defined in defines_weak.h) has exactly three fields: x__i32F4, y__i32F4, z__i32F4, all of type i32F4 (int32_t). All three are checked. The logic is structurally identical to the sibling functions is_vectors_3i32__out_of_bounds (line 112) and is_vectors_3i32F20__out_of_bounds (line 138), maintaining consistency across the codebase. The computation matches the semantic intent: detect whether any component has been set to the out-of-bounds sentinel.

Implementation Correctness:
Type compatibility — VECTOR__3i32F4__OUT_OF_BOUNDS is a const Vector__3i32F4, and vector__3i32F4 is also a Vector__3i32F4. Both .x__i32F4 accesses yield i32F4 (int32_t) values. The == comparison between two int32_t values is well-defined. No implicit conversions or truncation occur.
Undefined behavior — no pointer arithmetic, no null dereference (no pointers used), no type punning, no out-of-bounds access (struct field access is always safe).
Validation — no validation is needed. This is a pure comparison predicate with no external dependencies. The caller is responsible for interpreting the result.

Side Effects:
No side effects — the function is pure. It takes its argument by value and returns a boolean without modifying any state.
