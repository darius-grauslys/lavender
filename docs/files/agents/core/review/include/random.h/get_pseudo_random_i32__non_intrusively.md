get_pseudo_random_i32__non_intrusively — core/source/random.c

Generates a pseudo-random i32 from the Repeatable_Psuedo_Random struct's current seed without mutating the struct.

Pre-conditions:
1. p_repeatable_psuedo_random must be a non-null pointer to a valid, initialized Repeatable_Psuedo_Random struct.
2. The global RNG state is unspecified prior to this call; the function is expected to seed from the struct's seed__current_random field.
3. seed__current_random is a Psuedo_Random_Seed__u32 (uint32_t) and is a valid seed value for srand().

Post-conditions:
1. The Repeatable_Psuedo_Random struct is NOT mutated — seed__initial and seed__current_random remain unchanged (non-intrusive).
2. The global RNG is re-seeded with p_repeatable_psuedo_random->seed__current_random as a side effect.
3. Returns a Psuedo_Random__i32 (int32_t) value.

Correctness Verdict: Incorrect

Semantic Alignment:
The semantic intent of this function, by comparison with get_pseudo_random_i32__non_intrusively_with__seed and get_pseudo_random_i32__intrusively, is to produce a deterministic random value derived from the struct's seed__current_random field. The "non-intrusive" qualifier means the struct itself is not mutated (unlike the intrusive variant which updates seed__current_random), but the result should still be deterministic based on the struct's seed.

The current implementation is semantically incorrect. It calls rand() BEFORE calling srand() with the struct's seed:

    Psuedo_Random__i32 random = rand();           // uses whatever global RNG state exists
    srand(p_repeatable_psuedo_random->seed__current_random);  // seeds AFTER the value is already generated
    return random;

This means the returned value is NOT deterministic with respect to the struct's seed — it depends on whatever global RNG state existed prior to this call. Compare with the correct pattern used in get_pseudo_random_i32__non_intrusively_with__seed, which seeds first, then generates:

    srand(seed);
    Psuedo_Random__i32 random = rand();
    srand(p_repeatable_psuedo_random->seed__current_random);
    return random;

The correct implementation should seed the global RNG from the struct's seed before calling rand():

    srand(p_repeatable_psuedo_random->seed__current_random);
    Psuedo_Random__i32 random = rand();
    return random;

This matches the semantic intent: generate a deterministic value from the struct's seed without modifying the struct.

Implementation Correctness:
Type compatibility — rand() returns int, which is implicitly converted to Psuedo_Random__i32 (int32_t). On platforms where int is 32-bit, this is a safe conversion. srand() expects unsigned int, and seed__current_random is uint32_t, which is compatible.
Undefined behavior — no pointer arithmetic, no null dereference (assuming pre-condition holds), no type punning, no out-of-bounds access.
Validation — the function does not validate p_repeatable_psuedo_random for null. This is consistent with the other functions in random.c, which also assume a valid pointer. The validation burden is on the caller, which is appropriate for this low-level utility module.
The ordering bug (rand() before srand()) is a logical/semantic error, not a type or UB issue.

Side Effects:
The global RNG state is modified as a side effect: srand() is called with p_repeatable_psuedo_random->seed__current_random, which re-seeds the global random number generator. This is an observable side effect on global state. The struct pointed to by p_repeatable_psuedo_random is not modified.
