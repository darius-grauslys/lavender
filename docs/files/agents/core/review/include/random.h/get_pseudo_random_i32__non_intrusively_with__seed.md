get_pseudo_random_i32__non_intrusively_with__seed — core/source/random.c

Generates a pseudo-random i32 value using a caller-supplied seed, without mutating the Repeatable_Psuedo_Random struct, and restores the global RNG state before returning.

Pre-conditions:
1. p_repeatable_psuedo_random must be a non-null pointer to an initialized Repeatable_Psuedo_Random struct (its seed__current_random field must hold a valid seed value).
2. seed is any i32 value; it is implicitly converted to unsigned int when passed to srand (well-defined modulo 2^N conversion).

Post-conditions:
1. Returns a Psuedo_Random__i32 (int32_t) value derived from the provided seed via rand().
2. The Repeatable_Psuedo_Random struct is NOT modified — no field is read for writing, no field is updated.
3. The global C RNG state is restored to p_repeatable_psuedo_random->seed__current_random before the function returns.

Correctness Verdict: Correct

Semantic Alignment:
The function fulfills its semantic intent. It generates a random number from the provided seed and restores the global RNG state, without touching the Repeatable_Psuedo_Random struct. This is consistent with the sibling non-intrusive functions (get_pseudo_random_i32__non_intrusively and get_psuedo_random__direction_u8__non_intrusively_with__seed), which all follow the same srand(seed) / rand() / srand(restore) pattern. The "non-intrusively" qualifier correctly means the struct is not mutated, and the "with__seed" qualifier means the provided seed overrides the struct's seed for this single generation.

Implementation Correctness:
Type compatibility — i32 seed is passed to srand(unsigned int). The implicit signed-to-unsigned conversion is well-defined in C (value converted modulo 2^N). rand() returns int, which is assigned to Psuedo_Random__i32 (int32_t); on standard platforms int is 32 bits, so no truncation occurs.
No undefined behavior — no null dereference (p_repeatable_psuedo_random is assumed valid per pre-conditions, consistent with the codebase convention that validation is the caller's responsibility), no pointer arithmetic, no type punning, no out-of-bounds access.
No validation is performed inside the function — it is a low-level RNG helper. Null-checking p_repeatable_psuedo_random would be the caller's responsibility, consistent with the rest of the module.

Side Effects:
The function temporarily modifies the global C library RNG state (via srand(seed) and srand(seed__current_random)) but restores it to its prior value before returning. The Repeatable_Psuedo_Random struct itself is not modified.
