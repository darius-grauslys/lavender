is_quantity_u16__out_of_bounds — core/include/numerics.h

Checks whether a u16 quantity value equals the sentinel QUANTITY__UNKNOWN__u16 (0xFFFF).

Pre-conditions:
1. quantity__u16 is a valid Index__u16 (uint16_t) value; no range constraint is required.

Post-conditions:
1. Returns true if quantity__u16 equals QUANTITY__UNKNOWN__u16 (0xFFFF), false otherwise.
2. No state is mutated; the function is a pure predicate.

Correctness Verdict: Correct

Semantic Alignment:
The implementation correctly checks whether the provided quantity value matches the unknown-quantity sentinel (0xFFFF). This is consistent with the sibling functions is_quantity_u8__out_of_bounds and is_quantity_u32__out_of_bounds, which follow the same pattern of comparing against QUANTITY__UNKNOWN__uN. The computation matches the semantic intent exactly.

Implementation Correctness:
Type compatibility — the parameter type Index__u16 is a typedef for uint16_t (defined in defines_weak.h), and QUANTITY__UNKNOWN__u16 is (uint16_t)(-1) = 0xFFFF (defined in defines.h). The comparison is between two uint16_t values, so there are no implicit conversions or truncation.
No undefined behavior — no pointer arithmetic, no null dereference, no type punning, no out-of-bounds access.
No validation is needed — this is a low-level pure comparison function. The caller is responsible for ensuring the value being checked is meaningful.

Side Effects:
No side effects — the function is a pure predicate with no observable effects beyond its boolean return value.