get_psuedo_random__direction_u8__non_intrusively_with__seed — core/source/random.c

Generates a pseudo-random direction value (Direction__u8) using a caller-supplied seed, without permanently altering the global random state.

Pre-conditions:
1. p_repeatable_psuedo_random must be a non-null pointer to a writable Repeatable_Psuedo_Random object.
2. p_repeatable_psuedo_random must have been initialized via initialize_repeatable_psuedo_random so that seed__current_random holds a valid seed value.
3. seed is any i32 value; negative values are implicitly converted to unsigned int by srand, which is standard and acceptable for seeding.

Post-conditions:
1. Returns a Direction__u8 (uint8_t) value in the range [0, 63], obtained by masking rand() with DIRECTION__ANY (MASK(6) = 0x3F).
2. The global random seed is restored to p_repeatable_psuedo_random->seed__current_random, leaving the global RNG state as it was prior to the call.

Correctness Verdict: Correct

Semantic Alignment:
The implementation fulfills its semantic intent. It seeds the global RNG with the provided seed, generates a random value, masks it to the 6 direction bits (NORTH, EAST, SOUTH, WEST, UPWARDS, DOWNWARDS), and restores the global RNG state. This matches the pattern used by the sibling function get_pseudo_random_i32__non_intrusively_with__seed, which performs the same seed-generate-restore sequence. The masking with DIRECTION__ANY ensures the result only contains valid direction flag bits, and the result always fits within uint8_t.

Implementation Correctness:
Type compatibility — seed is i32 (int32_t) passed to srand(unsigned int); the implicit signed-to-unsigned conversion is well-defined and standard for seed values. rand() returns int; the expression rand() & DIRECTION__ANY yields an int in [0, 63], which is safely narrowed to Direction__u8 (uint8_t) with no truncation.
Undefined behavior — none. No pointer arithmetic, no null dereference (p_repeatable_psuedo_random is dereferenced only for seed__current_random, which is valid under pre-condition 2), no type punning, no out-of-bounds access.
Validation — no validation is needed; this is a low-level utility function. The caller is responsible for ensuring p_repeatable_psuedo_random is valid and initialized.

Side Effects:
Temporarily modifies the global random seed via srand(seed) and then restores it via srand(p_repeatable_psuedo_random->seed__current_random). The net observable effect is that the global RNG state is left as p_repeatable_psuedo_random->seed__current_random. The Repeatable_Psuedo_Random struct itself is not mutated.
