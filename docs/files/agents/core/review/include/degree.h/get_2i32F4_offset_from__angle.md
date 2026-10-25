get_2i32F4_offset_from__angle — core/source/degree.c

Returns a unit direction-vector offset (Vector__3i32F4) for a given angle by indexing a precomputed lookup table of Vector__3i32F20 unit vectors and down-converting each component from 20-bit to 4-bit fixed-point precision.

Pre-conditions:
1. angle must be a valid index into __DEGREE_TO_2i32F10__LOOKUP_TABLE, i.e. 0 <= angle < 512 (ANGLE__360). Degree__u9 is a uint16_t but semantically a 9-bit value (max 511); the caller must guarantee it does not exceed the table bounds.
2. No bounds checking is performed inside the function; the caller is responsible for ensuring angle < 512 (see is_degree_u9__out_of_bounds in degree.h:20).

Post-conditions:
1. Returns a Vector__3i32F4 whose x__i32F4 and y__i32F4 are the angle's precomputed sine/cosine direction components converted from i32F20 to i32F4 via an arithmetic right shift of 16 bits; z__i32F4 is always 0 (the table's z column is uniformly 0), representing a horizontal (XY-plane) direction.
2. The returned vector is a normalized unit-length direction (magnitude ~1.0 in i32F4) derived from the lookup table.

Correctness Verdict: Correct

Semantic Alignment:
The implementation directly fulfills the declared intent (degree.h:50, "get_2i32F4 offset from an angle"). It indexes the precomputed unit-direction table for the given angle and converts precision to i32F4 via vector_3i32F20_to__vector_3i32F4, which maps all three components (x, y, z). The computation matches the semantic intent exactly — a table lookup followed by precision down-conversion — so there is no semantic drift.

Implementation Correctness:
Type compatibility — the lookup table __DEGREE_TO_2i32F10__LOOKUP_TABLE is of type Vector__3i32F20[512]; its indexed element is passed to vector_3i32F20_to__vector_3i32F4(Vector__3i32F20) and the returned Vector__3i32F4 matches the declared return type. Types match exactly; no implicit conversions or truncation. The inner conversion i32F20_to__i32F4 performs ARITHMETRIC_R_SHIFT(x, 16) (numerics.h:112), correctly reducing 20-bit fractional precision to 4-bit (20 - 16 = 4).
Undefined behavior — if the pre-condition (angle < 512) is violated, __DEGREE_TO_2i32F10__LOOKUP_TABLE[angle] is an out-of-bounds array read (the table has exactly 512 entries, indices 0-511), which is undefined behavior. The function performs no validation of this. This is a low-level lookup/helper: the sibling get_2i32F20_offset_from__angle (degree.c:578) has the identical unchecked pattern, and the codebase provides the is_degree_u9__out_of_bounds helper (degree.h:20) for callers to check before invoking such functions.
Validation — no validation is performed; this is appropriate for the function's role as a low-level table-lookup helper, consistent with the sibling function and the codebase's caller-responsibility validation pattern.

Side Effects:
No side effects. The function is a pure read from the static (never-written) lookup table __DEGREE_TO_2i32F10__LOOKUP_TABLE and returns a value; no memory, state, or I/O is mutated.
