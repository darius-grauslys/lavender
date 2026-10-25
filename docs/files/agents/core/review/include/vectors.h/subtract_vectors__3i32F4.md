subtract_vectors__3i32F4 — core/include/vectors.h, lines 522-530

Component-wise subtraction of two fixed-point 3D vectors (i32F4 format), returning a new Vector__3i32F4.

Pre-conditions:
1. vector_one is a valid Vector__3i32F4 passed by value (no null constraint; passed by value).
2. vector_two is a valid Vector__3i32F4 passed by value (no null constraint; passed by value).
3. Both vectors use the same i32F4 fixed-point format (int32_t with 4 fractional bits, FRACTIONAL_PERCISION_4__BIT_SIZE = 4).

Post-conditions:
1. Returns a new Vector__3i32F4 whose x, y, and z components are the result of vector_one.x__i32F4 - vector_two.x__i32F4, vector_one.y__i32F4 - vector_two.y__i32F4, and vector_one.z__i32F4 - vector_two.z__i32F4 respectively.
2. Both input vectors remain unmodified (passed by value).

Correctness Verdict: Correct

Semantic Alignment:
The function performs component-wise subtraction of the x, y, and z components of two i32F4 fixed-point vectors. Since both operands share the same fixed-point format (4 fractional bits), direct subtraction of the raw integer values is mathematically correct — the result is automatically in the same i32F4 format. The implementation matches the semantic intent exactly. All three struct fields are assigned in the compound literal return — no member is omitted, no reordering occurs.

Implementation Correctness:
Type compatibility — both parameters are Vector__3i32F4 (struct with i32F4 fields), and the return type is Vector__3i32F4. Each component subtraction operates on i32F4 (int32_t) values, which are the same type as the struct fields. No implicit conversions or truncation.
Undefined behavior — none. No pointer arithmetic, no null dereference, no type punning, no out-of-bounds access. Both parameters are passed by value, eliminating any null pointer risk.
Validation — none needed. This is a pure computational function with value-type parameters. No range checking is required for the subtraction operation itself; overflow behavior is the same as integer arithmetic and is the caller's responsibility if relevant.

Side Effects:
No side effects. The function is pure — it reads its two value parameters and returns a new Vector__3i32F4 without modifying any external state or the input parameters.
