get_distance_hamming_of__vectors_3i32 — core/include/vectors.h

Computes the Manhattan distance (sum of absolute component-wise differences) between two 3D integer vectors, returning the result as an i32F4.

Pre-conditions:
1. vector__one__3i32 is any valid Vector__3i32 (passed by value, no null concern).
2. vector__two__3i32 is any valid Vector__3i32 (passed by value, no null concern).
3. No range constraints on individual components; the caller is responsible for ensuring values do not cause integer overflow in subtraction or abs (e.g., INT32_MIN).

Post-conditions:
1. Returns the sum |x1-x2| + |y1-y2| + |z1-z2| as an i32F4 (int32_t).
2. Neither input vector is modified (both are passed by value).

Correctness Verdict: Correct

Semantic Alignment:
The function correctly computes the Manhattan distance — the sum of absolute differences of the x, y, and z components. In this codebase, "hamming distance" is used as a domain-specific synonym for Manhattan distance, consistent with the Path struct's distance__hamming__i32 field and the sibling function get_manhattan_distance__of_vector_3i32_as__u32 (which performs the identical computation but returns Quantity__u32). The implementation matches the semantic intent.

Implementation Correctness:
Type compatibility — Vector__3i32 fields are Signed_Index__i32 (typedef int32_t). The abs() function is declared in platform.h as int abs(int x). On standard platforms int and int32_t are the same type, so the implicit conversion from int32_t to int is a no-op. The sum of three int values is int, which is then returned as i32F4 (int32_t) — no truncation.
Undefined behavior — No pointer arithmetic, no null dereference, no type punning, no out-of-bounds access. The function operates entirely on stack-passed values. Note: abs(INT32_MIN) is technically undefined per the C standard, and the subtraction of two int32_t values can overflow; however, these are inherent limitations of integer arithmetic and are the caller's responsibility to avoid.
Validation — No validation is needed. This is a pure arithmetic computation. The caller is responsible for ensuring input values are within safe ranges.

Side Effects:
No side effects. The function is a pure computation: it takes two Vector__3i32 values by copy, performs arithmetic, and returns a result. No memory is read or written, no global state is accessed.
