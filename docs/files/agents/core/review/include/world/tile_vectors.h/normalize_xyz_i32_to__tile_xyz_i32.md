normalize_xyz_i32_to__tile_xyz_i32 — core/include/world/tile_vectors.h

Right-shifts a 32-bit signed integer by TILE__WIDTH_AND__HEIGHT__BIT_SHIFT (3) bits to convert a world-space coordinate into a tile index.

Pre-conditions:
1. xyz__i32 is any i32 value (no range constraint). It may be positive, negative, or zero.

Post-conditions:
1. Returns an i32 representing the tile index. For non-negative input, the result is equivalent to integer division by 8 (BIT(3)). For negative input, the behavior is implementation-defined (see Implementation Correctness).

Correctness Verdict: Incorrect

Semantic Alignment:
The function's intent is to convert a world-space coordinate to a tile index by dividing by the tile size (8 pixels, i.e., shifting right by 3). The implementation does perform a right shift by the correct amount. However, for negative inputs, the C standard does not guarantee arithmetic (sign-extending) right shift behavior — it is implementation-defined. The codebase already provides the ARITHMETRIC_R_SHIFT macro in numerics.h specifically to handle this case portably, but this function does not use it. This means the function's behavior on negative coordinates is not portable and may produce incorrect tile indices on compilers that implement logical (zero-filling) right shift for signed integers.

Implementation Correctness:
Type compatibility — the parameter type (i32) and return type (i32) are identical. No implicit conversions or truncation occur.
Undefined behavior — right-shifting a negative signed integer is implementation-defined behavior per the C standard (pre-C23). While most mainstream compilers (GCC, Clang) implement arithmetic right shift, this is not guaranteed. The codebase has an established pattern (ARITHMETRIC_R_SHIFT) to avoid this, but it is not used here.
Validation — no validation is needed for this low-level utility function; the caller is responsible for providing valid input.

Side Effects:
No side effects — the function is a pure computation that does not modify any state or access memory beyond the parameter.
