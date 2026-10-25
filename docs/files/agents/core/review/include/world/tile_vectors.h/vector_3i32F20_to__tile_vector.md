vector_3i32F20_to__tile_vector — core/include/world/tile_vectors.h

Converts a Vector__3i32F20 (3-tuple of 32-bit fixed-point integers with 20 fractional bits) into a Tile_Vector__3i32 (3-tuple of signed 32-bit integers representing tile coordinates) by normalizing each component through fixed-point-to-integer conversion followed by a tile-bit-shift.

Pre-conditions:
1. `vector` is a valid `Vector__3i32F20` value passed by value (no pointer, no null concern).
2. Each component `vector.x__i32F20`, `vector.y__i32F20`, `vector.z__i32F20` is of type `i32F20` (typedef `int32_t`), which is the expected input type of `normalize_xyz_i32F20_to__tile_xyz_i32`.

Post-conditions:
1. Returns a `Tile_Vector__3i32` (which is a typedef alias for `Vector__3i32_t`, having fields `x__i32`, `y__i32`, `z__i32`).
2. The returned struct's `x__i32` field is the result of `normalize_xyz_i32F20_to__tile_xyz_i32(vector.x__i32F20)`.
3. The returned struct's `y__i32` field is the result of `normalize_xyz_i32F20_to__tile_xyz_i32(vector.y__i32F20)`.
4. The returned struct's `z__i32` field is the result of `normalize_xyz_i32F20_to__tile_xyz_i32(vector.z__i32F20)`.
5. The function is pure — it does not modify any state.

Correctness Verdict: Correct

Semantic Alignment:
The function correctly converts a 3i32F20 vector to a tile vector. Each component (x, y, z) is independently normalized through `normalize_xyz_i32F20_to__tile_xyz_i32`, which first converts the i32F20 value to a plain i32 via arithmetic right shift by `FRACTIONAL_PERCISION_20__BIT_SIZE` (20 bits), then shifts right by `TILE__WIDTH_AND__HEIGHT__BIT_SHIFT` (3 bits) to obtain the tile coordinate. The compound literal initializer `(Tile_Vector__3i32) { ... }` uses positional initialization matching the struct field order (`x__i32`, `y__i32`, `z__i32`), so `vector.x__i32F20` maps to `x__i32`, `vector.y__i32F20` maps to `y__i32`, and `vector.z__i32F20` maps to `z__i32`. This is consistent with the sibling functions `vector_3i32_to__tile_vector` and `vector_3i32F4_to__tile_vector`, which follow the same pattern.

Implementation Correctness:
Type compatibility — `normalize_xyz_i32F20_to__tile_xyz_i32` accepts `i32F20` and returns `i32` (`int32_t`). The input `vector.x__i32F20` (type `i32F20`) matches exactly. The return type `i32` is assigned to `Signed_Index__i32` (which is `typedef int32_t Signed_Index__i32`), so there is no implicit conversion or truncation.
Undefined behavior — no pointer arithmetic, no null dereference, no type punning, no out-of-bounds access. The function operates entirely on a by-value struct parameter and returns a by-value struct.
Validation — no validation is needed or expected for this low-level conversion function. It is the caller's responsibility to provide a valid `Vector__3i32F20`.

Side Effects:
No side effects. The function is pure: it reads from its by-value parameter and returns a new `Tile_Vector__3i32` without modifying any observable state.
