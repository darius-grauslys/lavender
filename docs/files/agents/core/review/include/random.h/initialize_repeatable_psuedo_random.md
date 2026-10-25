initialize_repeatable_psuedo_random — core/source/random.c

Sets both seed fields of a Repeatable_Psuedo_Random struct to the provided seed value, resetting the struct to its initial conditions.

Pre-conditions:
1. p_repeatable_psuedo_random must be a non-null pointer to a writable Repeatable_Psuedo_Random object.
2. seed__initial is any Psuedo_Random_Seed__u32 (uint32_t); no range constraint needed.

Post-conditions:
1. p_repeatable_psuedo_random->seed__initial equals seed__initial.
2. p_repeatable_psuedo_random->seed__current_random equals seed__initial.

Correctness Verdict: Correct

Semantic Alignment:
This is Lavender-style initialization (cleaning up a struct to its initial conditions, NOT RAII). The struct Repeatable_Psuedo_Random has exactly two fields — seed__initial and seed__current_random — and the function assigns both. No member is omitted; no reordering occurs. The chained assignment (a = b = c) is valid C and correctly writes the same seed value to both fields.

Implementation Correctness:
Type compatibility — the parameter seed__initial is Psuedo_Random_Seed__u32 (uint32_t) and both struct fields are Psuedo_Random_Seed__u32. Types match exactly; no implicit conversions or truncation.
No undefined behavior — no pointer arithmetic, no type punning, no out-of-bounds access. The only potential UB is dereferencing a null p_repeatable_psuedo_random, but null-checking is the caller's responsibility per Lavender conventions (consistent with initialize_audio_effect and similar low-level struct initializers).
No validation is needed — this is a low-level struct assignment. The caller is responsible for ensuring p_repeatable_psuedo_random is valid.

Side Effects:
Mutates the Repeatable_Psuedo_Random struct pointed to by p_repeatable_psuedo_random, setting both seed__initial and seed__current_random to the provided seed value. No other side effects — does not call srand() or any other external function.
