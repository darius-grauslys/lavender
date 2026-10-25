subtract_angles — core/include/degree.h, lines 34-42

Computes the modular difference (angle_1 - angle_2) in the engine's fixed-point angle representation, where one full turn (360°) equals 512 units (ANGLE__360). The result is always a valid angle in the range [0, 511].

Pre-conditions:
1. angle_1 must be a valid angle in [0, 511], i.e. angle_1 < ANGLE__360. The caller is responsible for validity; the function does not validate (consistent with the codebase convention seen in add_angles / is_degree_u9__out_of_bounds).
2. angle_2 must be a valid angle in [0, 511], i.e. angle_2 < ANGLE__360.
3. Neither parameter is a pointer, so no nullability constraint applies.

Post-conditions:
1. Returns a value in [0, 511] (always < ANGLE__360, never out of bounds) that equals (angle_1 - angle_2) mod 512.
2. When angle_1 >= angle_2, returns angle_1 - angle_2 (the straightforward, in-range difference).
3. When angle_1 < angle_2, returns ANGLE__360 - (angle_2 - angle_1), i.e. the wrapped-around (modular) difference.
4. The arguments are passed by value and are not modified; no external state is changed.

Correctness Verdict: Correct

Semantic Alignment:
The implementation fulfills the semantic intent of subtracting angle_2 from angle_1 with modular wraparound at 360°. The doc comment contains a typo — it reads "Subtract angle_2 from angle_2" but the code computes angle_1 - angle_2, which is the documented intent. The wraparound branch correctly evaluates to 512 - (angle_2 - angle_1) = (angle_1 - angle_2) mod 512. The non-wraparound branch (angle_1 >= angle_2) simply yields angle_1 - angle_2, also correct. Note that, unlike add_angles, this function correctly does NOT mask the result with ANGLE__MASK (= 31), which would be a bug; the result is naturally confined to [0, 511] without masking.

Implementation Correctness:
Type compatibility — angle_1 and angle_2 are Degree__u9 (uint16_t). All arithmetic (angle_2 - angle_1, angle_1 - angle_2, ANGLE__360 - ...) promotes to int (uint16_t fits within int), so there is no unsigned underflow and no overflow: the largest intermediate is 512 and the smallest is 0. The int result is implicitly converted back to Degree__u9 (uint16_t); since the value is always in [0, 511], no truncation occurs.
Undefined behavior — none. There is no pointer dereference, no array indexing, no type punning, and no out-of-bounds access. The unsigned subtractions only execute in the branch guaranteed to make them positive.
Validation — no validation is performed, which is appropriate for this low-level inline helper; ensuring inputs are valid angles is the caller's responsibility, consistent with the rest of degree.h.

Side Effects:
No side effects. The function is pure: it reads no global state, writes nothing, and only returns a computed value derived from its by-value arguments.
