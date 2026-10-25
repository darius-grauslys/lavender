delta_u8__no_overflow — core/include/numerics.h

Computes the absolute difference (delta) between two unsigned 8-bit integers without risk of underflow, by always subtracting the smaller value from the larger.

Pre-conditions:
1. first__u8 is any valid u8 value (0 to 255).
2. second__u8 is any valid u8 value (0 to 255).
3. No pointer parameters; both arguments are passed by value, so no null checks are required.

Post-conditions:
1. Returns the absolute difference |first__u8 - second__u8| as a u8.
2. The returned value is always in the range [0, 255] and fits within a u8.

Correctness Verdict: Correct

Semantic Alignment:
The implementation correctly computes the absolute difference between two u8 values. When first__u8 < second__u8, it returns second__u8 - first__u8 (the positive difference). Otherwise, it returns first__u8 - second__u8 (also the positive difference). In both branches, the smaller value is subtracted from the larger, guaranteeing a non-negative result with no underflow. The computation matches the semantic intent of computing a "delta" without overflow.

Implementation Correctness:
Type compatibility — both parameters are u8 and the return type is u8. The subtraction operations are performed on u8 operands, which are promoted to int during arithmetic and then implicitly converted back to u8 for the return. Since the result is always non-negative and within the u8 range, no truncation occurs.
Undefined behavior — no pointer arithmetic, no null dereference, no type punning, no out-of-bounds access. The subtraction is always performed on the larger value minus the smaller value, so no unsigned underflow occurs.
Validation — no validation is needed. The function accepts all u8 values and handles them correctly. This is a low-level arithmetic utility; validation of inputs is the caller's responsibility.

Side Effects:
No side effects. The function is a pure function that takes two values by copy and returns a computed result without modifying any external state or memory.
