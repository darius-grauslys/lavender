is_quantity_u8__out_of_bounds — core/include/numerics.h

Checks whether a u8 quantity value is "out of bounds" by comparing it against the sentinel constant QUANTITY__UNKNOWN__u8 (which equals (uint8_t)(-1), i.e. 255). This follows the same pattern as is_index_u8__out_of_bounds, is_quantity_u16__out_of_bounds, and is_quantity_u32__out_of_bounds.

Pre-conditions:
1. quantity__u8 is an Index__u8 (typedef for uint8_t). No range or validity constraints — any u8 value is acceptable input.

Post-conditions:
1. Returns true if quantity__u8 equals QUANTITY__UNKNOWN__u8 (the sentinel value 255), indicating the quantity is out of bounds / unknown.
2. Returns false for all other values, indicating the quantity is valid.

Correctness Verdict: Correct

Semantic Alignment:
The implementation correctly fulfills the semantic intent. The function checks whether a quantity value has been set to the "unknown" sentinel, which is the established convention in this codebase for representing an out-of-bounds or uninitialized quantity. The comparison is straightforward and matches the intent expressed by the function name.

Implementation Correctness:
- Type compatibility: The parameter type Index__u8 is a typedef for uint8_t (defined in defines_weak.h and defines.h). QUANTITY__UNKNOWN__u8 is defined as (uint8_t)(-1). Both operands of the == comparison are uint8_t values (promoted to int for comparison), so the comparison is well-defined and correct. No implicit conversions or truncation occur.
- The parameter is typed as Index__u8 rather than Quantity__u8, but both are typedefs for uint8_t, so this is semantically equivalent. This is consistent with the sibling functions is_quantity_u16__out_of_bounds (which takes Index__u16) and is_quantity_u32__out_of_bounds (which takes Index__u32), indicating this is an intentional, consistent design choice.
- No undefined behavior — no pointer arithmetic, no null dereference, no type punning, no out-of-bounds access.
- No validation is needed — this is a pure comparison function with no preconditions to enforce.

Side Effects:
No side effects. This is a pure function that reads its argument and returns a boolean.
