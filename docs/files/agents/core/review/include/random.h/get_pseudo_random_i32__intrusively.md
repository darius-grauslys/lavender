get_pseudo_random_i32__intrusively — core/source/random.c

Generates a pseudo-random i32 value by seeding the global RNG with the struct's current seed, stores the newly generated value back into the struct, and returns it.

Pre-conditions:
1. p_repeatable_psuedo_random must be a non-null pointer to a writable Repeatable_Psuedo_Random object.
2. p_repeatable_psuedo_random must have been previously initialized via initialize_repeatable_psuedo_random so that seed__current_random holds a valid seed value.

Post-conditions:
1. p_repeatable_psuedo_random->seed__current_random is mutated to hold the newly generated pseudo-random value from rand().
2. The global RNG state is modified (srand is called with the previous seed, then rand advances the global state).
3. The function returns the new pseudo-random value as a Psuedo_Random__i32 (int32_t).

Correctness Verdict: Correct

Semantic Alignment:
The function correctly implements the "intrusive" pattern: it seeds the global RNG with the struct's current seed (seed__current_random), generates a new random value via rand(), stores that value back into the struct (mutating seed__current_random), and returns it. This matches the semantic intent of producing a repeatable pseudo-random sequence where each call advances the internal state. The seed chain is maintained correctly — the returned value becomes the seed for the next call.

Implementation Correctness:
Type compatibility — srand() accepts unsigned int; seed__current_random is uint32_t (Psuedo_Random_Seed__u32). On the target platform where unsigned int is 32-bit, these are compatible with no truncation. rand() returns int, which is assigned to seed__current_random (uint32_t); since rand() returns non-negative values, this signed-to-unsigned conversion is safe. The return statement returns seed__current_random (uint32_t) as int32_t (Psuedo_Random__i32); since the stored value always originates from rand() (which returns int, always in [0, RAND_MAX] where RAND_MAX <= INT_MAX), the unsigned-to-signed conversion is always well-defined and safe.
No undefined behavior — no pointer arithmetic, no null dereference (caller's responsibility per codebase convention), no type punning, no out-of-bounds access.
No validation is needed — this is a low-level function following the codebase pattern where the caller is responsible for ensuring p_repeatable_psuedo_random is valid.

Side Effects:
1. Mutates p_repeatable_psuedo_random->seed__current_random with the new pseudo-random value.
2. Modifies global RNG state via srand() and rand() calls (the global seed is set to the struct's seed, then advanced by rand()).
