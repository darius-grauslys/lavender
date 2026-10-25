initialize_3i32F4_vector — core/include/vectors.h

Resets a Vector__3i32F4 struct to its default (zeroed) state.

Pre-conditions:
1. vector must be a non-null pointer to a writable Vector__3i32F4 object.

Post-conditions:
1. vector->x__i32F4 is set to 0.
2. vector->y__i32F4 is set to 0.
3. vector->z__i32F4 is set to 0.

Correctness Verdict: Correct

Semantic Alignment:
This is a Lavender-style initialization — it cleans up a struct to its initial conditions (zeroing all fields) so it can be returned to a free pool or reused. It does NOT perform resource acquisition (not RAII). All three struct fields are assigned — no member is omitted, no reordering occurs. The struct Vector__3i32F4 has exactly three fields (x__i32F4, y__i32F4, z__i32F4) and the function writes to all three.

Implementation Correctness:
Type compatibility — assigning the integer literal 0 to fields of type i32F4 (typedef int32_t) is an exact match with no implicit conversions or truncation.
Undefined behavior — no pointer arithmetic, no null dereference (the null check is the caller's responsibility), no type punning, no out-of-bounds access.
Validation — no validation is needed within this function. It is a low-level struct reset; the caller is responsible for ensuring vector is a valid pointer.

Side Effects:
No side effects — the only observable effect is writing the three fields of the pointed-to struct to zero.
