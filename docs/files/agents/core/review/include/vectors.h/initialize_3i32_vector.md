initialize_3i32_vector — core/include/vectors.h

Resets a Vector__3i32 struct to its initial conditions by zeroing all three components (x, y, z).

Pre-conditions:
1. `vector` must be a non-null pointer to a writable Vector__3i32 object.

Post-conditions:
1. `vector->x__i32` is set to 0.
2. `vector->y__i32` is set to 0.
3. `vector->z__i32` is set to 0.

Correctness Verdict: Correct

Semantic Alignment:
This is a Lavender-style initialization (not RAII). It performs a pool cleanup / reset, setting all struct fields to their default (zero) values so the struct can be returned to a free pool or reused. The struct Vector__3i32 is defined as:
```c
typedef struct Vector__3i32_t {
    Signed_Index__i32 x__i32,
                      y__i32,
                      z__i32;
} Vector__3i32;
```
The struct has exactly three fields, and all three are assigned. No member is omitted and no reordering occurs.

Implementation Correctness:
- Type compatibility: The literal `0` is assigned to `Signed_Index__i32` fields (which are `int32_t`). The value 0 is implicitly and safely convertible to `int32_t` with no truncation or loss.
- Undefined behavior: No pointer arithmetic, no null dereference (pre-condition requires non-null), no type punning, no out-of-bounds access.
- Validation: No validation is needed — this is a low-level struct assignment. The caller is responsible for ensuring `vector` is a valid, non-null pointer.

Side Effects:
The only observable effect is writing 0 to all three fields (x__i32, y__i32, z__i32) of the pointed-to Vector__3i32 struct.
