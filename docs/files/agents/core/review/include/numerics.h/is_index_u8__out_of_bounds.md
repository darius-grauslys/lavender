is_index_u8__out_of_bounds — core/include/numerics.h

Checks whether an `Index__u8` value is the sentinel "unknown" value (`INDEX__UNKNOWN__u8`), which represents an invalid or out-of-bounds index.

Pre-conditions:
1. `index__u8` is any `Index__u8` (i.e., `uint8_t`) value. No constraints required — the function accepts all possible values.

Post-conditions:
1. Returns `true` if `index__u8` equals `INDEX__UNKNOWN__u8` (i.e., `(uint8_t)(-1)`, or 255).
2. Returns `false` otherwise.
3. No state is mutated; the function is pure.

Correctness Verdict: Correct

Semantic Alignment:
The implementation correctly fulfills its semantic intent. The function checks whether the given index equals the sentinel value `INDEX__UNKNOWN__u8`, which is defined as `(uint8_t)(-1)` (255). This is the established convention for representing an unknown or invalid index throughout the codebase. The comparison is a direct equality check against this sentinel, which is the correct and intended behavior.

Implementation Correctness:
- Type compatibility: The parameter `index__u8` is of type `Index__u8` (which is `typedef`'d to `uint8_t`), and `INDEX__UNKNOWN__u8` is defined as `(uint8_t)(-1)`. Both are `uint8_t`, so the comparison is type-safe with no implicit conversions or truncation.
- Undefined behavior: None. The function performs a simple equality comparison on a primitive value type. There is no pointer dereference, no arithmetic, no buffer access, and no type punning.
- Validation: No validation is needed — the function's sole purpose is to perform this comparison. It is a low-level utility function; the caller is responsible for the semantic meaning of the index value passed in.

Side Effects:
No side effects — the function is pure. It reads only its parameter and returns a boolean result without modifying any state or memory.
