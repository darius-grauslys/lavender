get_pseudo_random_i32_with__xy__intrusively — core/source/random.c

Generates a pseudo-random i32 value derived from coordinates (x, y) and the repeatable random's seed__initial, using the global C RNG (srand/rand).

Pre-conditions:
1. p_repeatable_psuedo_random must be a non-null pointer to a valid Repeatable_Psuedo_Random struct.
2. seed__initial must have been set (via initialize_repeatable_psuedo_random) to a meaningful seed value.
3. x and y are Signed_Index__i32 (int32_t); they may be negative. No range constraint is enforced.

Post-conditions:
1. Returns a Psuedo_Random__i32 (int32_t) computed as the sum of two rand() calls.
2. The global C RNG state is modified (srand is called twice with intermediate values).
3. seed__current_random in the Repeatable_Psuedo_Random struct is NOT modified — despite the "intrusively" in the function name.

Correctness Verdict: Incorrect

Semantic Alignment:
The function name suggests "intrusive" behavior — i.e., it should modify the internal state of the Repeatable_Psuedo_Random struct (specifically seed__current_random), as the other intrusive function get_pseudo_random_i32__intrusively does. However, this function does NOT modify seed__current_random at all. It only reads seed__initial. This is a semantic mismatch: the function is named as intrusive but behaves non-intrusively with respect to the struct's mutable state. The core intent — generating a deterministic pseudo-random value from (x, y) and the initial seed — is fulfilled, but the naming does not match the implementation.

Implementation Correctness:
Type compatibility — srand() expects unsigned int, but the argument `x + p_repeatable_psuedo_random->seed__initial` mixes int32_t (signed, from x) and uint32_t (unsigned, from seed__initial). When a signed int32_t is added to a uint32_t, the signed value is implicitly converted to unsigned. If x is negative, this conversion produces a large unsigned value, which may not be the intended behavior. Similarly, `random__result + y + p_repeatable_psuedo_random->seed__initial` mixes int (from rand()) with int32_t (y) and uint32_t (seed__initial), again causing implicit signed-to-unsigned conversion.
The return type is Psuedo_Random__i32 (int32_t), but random__result is the sum of two rand() results (each an int) plus the intermediate unsigned arithmetic. The final return involves an implicit conversion from unsigned back to signed, which is implementation-defined if the value exceeds INT32_MAX.
Undefined behavior — no null dereference (p_repeatable_psuedo_random is dereferenced without null check, but this is the caller's responsibility per the codebase pattern). No pointer arithmetic or out-of-bounds access. No type punning.
No validation is performed — consistent with the codebase pattern where low-level functions do not validate their pointer arguments; validation is the caller's responsibility.

Side Effects:
The function modifies global state by calling srand() twice, which changes the global C library random number generator state. This can affect any other code that subsequently calls rand() or srand(). The Repeatable_Psuedo_Random struct itself is not mutated (seed__current_random remains unchanged).
