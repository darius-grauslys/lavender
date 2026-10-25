get_manhattan_distance__of_vector_3i32_as__u32 — core/include/vectors.h

Computes the Manhattan distance (sum of absolute component-wise differences) between two 3D integer vectors, returning the result as a Quantity__u32 (uint32_t).

Pre-conditions:
1. vector_one__3i32 is a valid Vector__3i32 passed by value; no null concern.
2. vector_two__3i32 is a valid Vector__3i32 passed by value; no null concern.
3. The x__i32, y__i32, z__i32 fields are Signed_Index__i32 (int32_t) and may be any value in the full int32_t range, including INT32_MIN and INT32_MAX.

Post-conditions:
1. Returns the Manhattan distance |x1−x2| + |y1−y2| + |z1−z2| as a Quantity__u32 (uint32_t).
2. Neither input vector is modified (both are passed by value).

Correctness Verdict: Incorrect

Semantic Alignment:
The function's semantic intent is to compute the Manhattan distance between two 3D integer vectors and return it as a u32. The computation uses abs() on the per-component differences and sums them — this is the correct formula for Manhattan distance. However, the implementation does not fulfill the semantic intent because the arithmetic is performed entirely in signed int arithmetic, which can overflow before the result is converted to the unsigned return type. The sibling function get_distance_hamming_of__vectors_3i32 performs the identical computation but returns i32F4 (int32_t), where the signed return type is at least consistent with the signed computation. Here, the return type is u32 (unsigned, max ~4.29 billion) but the intermediate sum is computed in int (signed, max ~2.15 billion), meaning the function cannot correctly handle valid inputs whose Manhattan distance falls between INT_MAX and UINT32_MAX.

Implementation Correctness:

Bug 1 — Signed integer overflow in subtraction (Undefined Behavior):
The expression `vector_one__3i32.x__i32 - vector_two__3i32.x__i32` subtracts two int32_t values. When one component is INT32_MAX (2147483647) and the other is INT32_MIN (-2147483648), the mathematical result is 4294967295, which cannot be represented as int32_t. This is signed integer overflow, which is undefined behavior in C. The same issue applies to the y and z components.

Bug 2 — abs(INT32_MIN) is undefined behavior:
If the per-component difference is exactly INT32_MIN (e.g., 0 - INT32_MIN, or INT32_MIN - 0), then abs(INT32_MIN) is undefined behavior because the result (2147483648) cannot be represented as int. The abs() function is declared in platform.h as `int abs(int x)` and cannot represent the absolute value of INT32_MIN.

Bug 3 — Signed overflow in the sum (Undefined Behavior):
The abs() function returns int. The sum of three int values can exceed INT_MAX (2147483647). For example, if each component difference has an absolute value of 1073741824 (just over INT_MAX/2), the sum is 3 × 1073741824 = 3221225472, which exceeds INT_MAX. This is signed integer overflow, which is undefined behavior. The result is then implicitly converted to uint32_t, but the UB has already occurred in the intermediate computation.

Bug 4 — Type mismatch between computation and return type:
The computation is performed entirely in int (signed) arithmetic, but the function returns Quantity__u32 (uint32_t). While the implicit conversion from int to uint32_t is well-defined, the signed overflow (Bug 3) occurs before this conversion. The function is designed to return a u32, which can hold values up to UINT32_MAX (4294967295), but the intermediate int computation overflows at INT_MAX (2147483647). This means the function cannot correctly compute Manhattan distances that exceed INT_MAX but fit within UINT32_MAX — a range that is valid for the return type.

Suggested Fix:
The computation should be performed in unsigned arithmetic to avoid signed overflow. The codebase already provides delta_u32__no_overflow in numerics.h, which safely computes the absolute difference of two u32 values. The fix would cast each i32 component to u32 and use delta_u32__no_overflow for each axis, then sum the results in u32 arithmetic:

```c
static inline
Quantity__u32 get_manhattan_distance__of_vector_3i32_as__u32(
        Vector__3i32 vector_one__3i32,
        Vector__3i32 vector_two__3i32) {
    return
        delta_u32__no_overflow(
            (u32)vector_one__3i32.x__i32,
            (u32)vector_two__3i32.x__i32)
        + delta_u32__no_overflow(
            (u32)vector_one__3i32.y__i32,
            (u32)vector_two__3i32.y__i32)
        + delta_u32__no_overflow(
            (u32)vector_one__3i32.z__i32,
            (u32)vector_two__3i32.z__i32);
}
```

This avoids all signed overflow (subtraction, abs, and sum are all done in u32 arithmetic) and is consistent with the codebase's existing overflow-safe patterns (e.g., get_distance_squared_of__vector_3i32__no_overflow).

Side Effects:
No side effects. The function is a pure computation: it takes two Vector__3i32 values by copy, performs arithmetic, and returns a result. No memory is read or written, no global state is accessed, and no pointers are dereferenced.
