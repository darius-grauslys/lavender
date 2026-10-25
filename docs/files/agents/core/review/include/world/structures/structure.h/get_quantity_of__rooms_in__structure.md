get_quantity_of__rooms_in__structure — core/include/world/structures/structure.h

Returns the quantity of rooms stored in the structure by reading the `quantity_of__rooms_in__structure` field of the `Structure` struct.

Pre-conditions:
1. p_structure must be a non-null pointer to a valid, initialized Structure object.

Post-conditions:
1. Returns the value of `p_structure->quantity_of__rooms_in__structure` as a `Quantity__u32`.
2. The Structure object is not modified.

Correctness Verdict: Correct

Semantic Alignment:
The function's implementation directly returns the `quantity_of__rooms_in__structure` field, which matches the documented semantic intent ("Returns quantity of rooms in the structure"). The return type is `Quantity__u32` while the underlying field is `Quantity__u8`; this is a widening (promotion) conversion from uint8_t to uint32_t, which is safe and lossless — no data is lost.

Implementation Correctness:
Type compatibility — the field `quantity_of__rooms_in__structure` is of type `Quantity__u8` (uint8_t) and the return type is `Quantity__u32` (uint32_t). This is a standard integer promotion (implicit widening), which is well-defined in C and does not cause truncation. No implicit conversions that lose data.
Undefined behavior — the function dereferences `p_structure` without a null check. However, this is consistent with the codebase pattern for static inline accessors (e.g., `get_the_kind_of__structure`, `is_structure__allocated`). Validation is the caller's responsibility, which is appropriate for a low-level getter.
No pointer arithmetic, no type punning, no out-of-bounds access.

Side Effects:
No side effects — this is a pure read accessor. The only observable effect is reading a field from the pointed-to Structure.
