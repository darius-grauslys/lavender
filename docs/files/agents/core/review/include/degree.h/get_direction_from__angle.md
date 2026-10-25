get_direction_from__angle — core/source/degree.c

Maps a 9-bit angle (0–360° encoded as a uint16_t in the range 0–511, where 512 == 360°) to a bitmask of cardinal directions (NORTH/EAST/SOUTH/WEST), using a ±22.5° tolerance band so that angles lying on a 45° diagonal yield both adjacent cardinal bits (e.g. NORTH | EAST == DIRECTION__NORTH_EAST).

Pre-conditions:
1. `angle` is a `Degree__u9` (uint16_t); the caller is not expected to pre-check bounds—the function performs its own bounds check.
2. If `angle >= ANGLE__OUT_OF_BOUNDS` (1023) the function treats the angle as out of bounds and short-circuits.
3. For a meaningful result, `angle` should be a canonical angle in [0, 512) (0°–360°); non-canonical values in [512, 1022) are accepted but degenerate, collapsing to NORTH only.
4. There are no pointer parameters, so there are no null or dereference concerns.

Post-conditions:
1. Returns a `Direction__u8` (uint8_t) bitmask containing zero or more of DIRECTION__NORTH, DIRECTION__EAST, DIRECTION__SOUTH, DIRECTION__WEST.
2. Returns DIRECTION__NONE (0) when `angle` is out of bounds (>= 1023).
3. Otherwise, each cardinal bit is set iff the angle falls within ±32 units (±22.5°) of that cardinal's reference angle (NORTH=0°/360°, EAST=90°, SOUTH=180°, WEST=270°).
4. The four tolerance bands collectively cover every value in [0, 512) with no gaps; each angle yields exactly one cardinal (near a pure cardinal) or two cardinals (on a 45° diagonal).
5. The four 45° diagonals (45°, 135°, 225°, 315°) each set exactly two adjacent cardinal bits, producing DIRECTION__NORTH_EAST, DIRECTION__SOUTH_EAST, DIRECTION__SOUTH_WEST, and DIRECTION__NORTH_WEST respectively.

Correctness Verdict: Correct

Semantic Alignment:
The implementation fulfills its semantic intent. Each cardinal direction is selected by a range test centered on its reference angle with a symmetric ±22.5° half-width, and the ranges are constructed so adjacent cardinals overlap exactly over the 45° diagonal between them. Traced across the full canonical range [0, 512), every angle sets either one or two direction bits and no angle is left uncovered. The four exact diagonals (64, 192, 320, 448) each produce the expected compound direction, and the pure cardinals (0, 128, 256, 384) each produce a single bit.

Observation (naming, not a logic defect): the constant `ANGLE__27_5` is defined as 32, which in the 9-bit encoding (360° == 512) actually represents 22.5° (half of 45°), not 27.5°. The misnomer is purely cosmetic—the function uses the value consistently for all four bands and the arithmetic is correct—so this does not affect correctness.

Implementation Correctness:
- Type compatibility — `angle` (uint16_t) is compared against the ANGLE__* macros (small int constants), which is well-defined; `direction` (uint8_t) is OR-assigned with DIRECTION__* values (1, 2, 4, 8; max attainable 15), all of which fit in a uint8_t with no truncation. The return type `Direction__u8` (uint8_t) matches the value range exactly. No implicit narrowing conversions occur.
- Undefined behavior — none. The function takes its argument by value and performs no pointer arithmetic, no dereferencing, no type punning, and no array access; all four branches are simple integer comparisons and bitwise assignments.
- Validation — appropriate for a low-level math helper: the single `is_degree_u9__out_of_bounds` guard rejects out-of-range input and yields a safe default (DIRECTION__NONE) rather than producing garbage. No allocation or resource management is involved, so no further validation is warranted.

Side Effects: No side effects. The function is pure—reads its argument by value, performs arithmetic, and returns a computed bitmask. It performs no I/O, mutates no storage, and touches no global state.
