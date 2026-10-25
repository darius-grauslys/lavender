tile_vector_3i32_to__local_tile_vector_3u8 — core/include/world/tile_vectors.h

Converts a world-space Tile_Vector__3i32 (signed 32-bit tile indices) into a chunk-local Local_Tile_Vector__3u8 (unsigned 8-bit indices suitable for indexing tiles within a chunk).

Pre-conditions:
1. tile_vector__3i32 is a valid Tile_Vector__3i32 with x__i32, y__i32, z__i32 each of type Signed_Index__i32 (int32_t). No null pointer is involved; the parameter is passed by value.
2. Each component may be any signed 32-bit value (positive, zero, or negative).

Post-conditions:
1. Returns a Local_Tile_Vector__3u8 (alias for Vector__3u8) whose x__u8, y__u8, z__u8 components each hold the result of ARITHMETRIC_MASK(component, MASK(TILE__WIDTH_AND__HEIGHT__BIT_SHIFT)).
2. Each returned component is in the range [0, 7] (i.e., 0 to CHUNK__WIDTH-1, since CHUNK__WIDTH = BIT(CHUNK__WIDTH_AND__HEIGHT__BIT_SHIFT) = 8).
3. No input parameters are mutated; the function is pure.

Correctness Verdict: Correct

Semantic Alignment:
The function's stated purpose (per the comment "Returns a Vector__3u8 with x,y,z fit for indexing tiles") is to produce local tile coordinates within a chunk. The implementation achieves this by applying ARITHMETRIC_MASK to each component of the input tile vector. ARITHMETRIC_MASK(x, 7) computes x mod 8 for both positive and negative x, which correctly yields the local tile index within a chunk of 8×8×8 tiles.

However, the function uses MASK(TILE__WIDTH_AND__HEIGHT__BIT_SHIFT) (= MASK(3) = 7) rather than MASK(CHUNK__WIDTH_AND__HEIGHT__BIT_SHIFT) (= MASK(3) = 7). Both constants currently evaluate to 3, so the mask value is identical (7) and the result is correct. Semantically, CHUNK__WIDTH_AND__HEIGHT__BIT_SHIFT is the more appropriate constant since the operation extracts the local position within a chunk (which has BIT(CHUNK__WIDTH_AND__HEIGHT__BIT_SHIFT) = 8 tiles per axis), not a tile-pixel relationship. This is a latent fragility: if TILE__WIDTH_AND__HEIGHT__BIT_SHIFT were ever changed independently of CHUNK__WIDTH_AND__HEIGHT__BIT_SHIFT, the function would produce incorrect results. The computation itself, however, matches the semantic intent given the current configuration.

Implementation Correctness:
Type compatibility — tile_vector__3i32.x__i32 is Signed_Index__i32 (int32_t). ARITHMETRIC_MASK's first argument is int32_t and second is u32 (from MASK). For the non-negative branch, (x) & (n) promotes int32_t to u32 via usual arithmetic conversions; for the negative branch, all operations are u32. The result is u32. get_vector__3u8 expects u8 parameters; the u32 result is implicitly narrowed to u8. Since ARITHMETRIC_MASK(x, 7) always yields a value in [0, 7], the narrowing to u8 is safe and lossless.
Undefined behavior — none. No pointer arithmetic, no null dereference, no type punning, no out-of-bounds access. The ARITHMETRIC_MASK macro is specifically designed to avoid undefined right-shift of negative values.
Validation — none needed. This is a low-level conversion function; the caller is responsible for providing a valid Tile_Vector__3i32.

Side Effects:
No side effects — the function is pure. It reads the input by value and returns a new Local_Tile_Vector__3u8 without modifying any global state or the input parameter.
