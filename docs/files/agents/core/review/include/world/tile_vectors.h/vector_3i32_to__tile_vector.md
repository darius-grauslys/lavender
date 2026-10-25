vector_3i32_to__tile_vector — core/include/world/tile_vectors.h

Converts a 3D fixed-point vector (i32F4) into a Tile_Vector__3i32 by normalizing each component to a tile index.

Pre-conditions:
1. `vector` is a `Vector__3i32F4` — a 3-tuple of 32-bit fixed-point integers with 4 fractional bits. No null-pointer concern since it is passed by value.
2. Each component (`x__i32F4`, `y__i32F4`, `z__i32F4`) is a raw `int32_t` (`i32F4`) whose lower 4 bits represent the fractional portion.

Post-conditions:
1. Returns a `Tile_Vector__3i32` (a `Vector__3i32` typedef) where each component is the tile index derived from the corresponding fixed-point input component.
2. The function does not mutate its input or any external state.

Correctness Verdict: Incorrect

Semantic Alignment:
The function name `vector_3i32_to__tile_vector` implies it accepts a `Vector__3i32` (plain 32-bit integer vector), but the parameter is actually `Vector__3i32F4` (fixed-point with 4 fractional bits). This is a parameter-type mismatch relative to the function name. More critically, the implementation calls `normalize_xyz_i32_to__tile_xyz_i32` — which expects a plain `i32` — on `i32F4` values. Since `i32F4` is a fixed-point type with 4 fractional bits in the lower 4 bits, passing the raw `i32F4` value to `normalize_xyz_i32_to__tile_xyz_i32` (which simply right-shifts by `TILE__WIDTH_AND__HEIGHT__BIT_SHIFT` = 3) does not strip the fractional bits first. The fractional bits are included in the shift, producing incorrect tile coordinates.

The correct sibling function `vector_3i32F4_to__tile_vector` demonstrates the proper approach: it calls `normalize_xyz_i32F4_to__tile_xyz_i32`, which first converts `i32F4` to `i32` via `i32F4_to__i32` (right-shift by `FRACTIONAL_PERCISION_4__BIT_SIZE` = 4) before performing the tile normalization shift. The reviewed function should use the same `normalize_xyz_i32F4_to__tile_xyz_i32` function instead of `normalize_xyz_i32_to__tile_xyz_i32`.

Implementation Correctness:
Type compatibility — `i32F4` is `typedef int32_t i32F4` and `i32` is `typedef int32_t i32`, so they are the same underlying type. The compiler will not flag a type error, but the semantic mismatch is significant: the 4 fractional bits in the `i32F4` values are not stripped before the tile normalization right-shift, causing the resulting tile indices to be incorrect.
No undefined behavior — no pointer arithmetic, no null dereference, no type punning, no out-of-bounds access.
No validation is needed — this is a pure computation function. The caller is responsible for providing valid input.

Side Effects:
No side effects — this is a pure function that returns a newly constructed `Tile_Vector__3i32` without modifying its input or any external state.
