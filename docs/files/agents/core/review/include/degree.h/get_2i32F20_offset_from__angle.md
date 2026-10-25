get_2i32F20_offset_from__angle — core/source/degree.c

Returns a precomputed direction offset vector (Vector__3i32F20, 20-bit fractional fixed-point) for the given angle by indexing a 512-entry lookup table.

Pre-conditions:
1. `angle` must be a valid `Degree__u9` value in the range `[0, 511]` (i.e., `[0, ANGLE__360 - 1]`). The lookup table has exactly 512 entries; an `angle >= 512` would cause an out-of-bounds array access.
2. The global lookup table `__DEGREE_TO_2i32F10__LOOKUP_TABLE` must be initialized. It is a file-scope array initialized at compile time, so this is always satisfied.
3. The caller is responsible for ensuring bounds; the function performs no validation, consistent with the engine's convention (see `is_degree_u9__out_of_bounds`).

Post-conditions:
1. Returns a `Vector__3i32F20` whose `.x__i32F20` and `.y__i32F20` fields hold the precomputed sine/cosine direction components (20-bit fractional fixed-point) for `angle`. The `.z__i32F20` field is 0 (XY-plane-only offsets).
2. The returned vector is not mutated by the function; the table itself is never written to.

Correctness Verdict: Correct

Semantic Alignment:
The implementation returns `__DEGREE_TO_2i32F10__LOOKUP_TABLE[angle]`, which is exactly the precomputed direction offset for the given angle. The sibling function `get_2i32F4_offset_from__angle` (same file, lines 572-576) performs the identical lookup and then converts the result down to F4 precision via `vector_3i32F20_to__vector_3i32F4`, confirming this function is the higher-precision (F20) source of truth. The lookup table entries are 2D unit vectors (z = 0), consistent with the documented purpose of providing short-range direction offsets. The implementation fulfills its semantic intent.

Implementation Correctness:
- Type compatibility — `angle` is `Degree__u9` (`uint16_t`), used directly as a non-negative array index; no sign-conversion issues. The return type `Vector__3i32F20` matches the array element type exactly. No implicit conversions or truncation occur.
- Undefined behavior — no pointer arithmetic, no null dereference, no type punning. The only potential UB is an out-of-bounds index if the caller passes `angle >= 512`, but this is the caller's responsibility (the engine uses `is_degree_u9__out_of_bounds` for such checks); the function itself does nothing unsafe given a valid angle. No out-of-bounds access occurs when the pre-condition is met.
- Validation — no validation is performed, which is appropriate for this low-level pure-lookup function. The engine's design delegates bounds checking to the caller (see `add_angles`/`subtract_angles` comments and `is_degree_u9__out_of_bounds`).

Side Effects:
No side effects — the function is a pure lookup. It reads from the read-only lookup table and returns a value; it does not mutate any global or local state.
