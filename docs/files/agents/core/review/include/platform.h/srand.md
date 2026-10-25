# Function Review: `srand`

**File of origin:** `core/include/platform.h` (line 173)

## Semantic

Seeds the C standard library pseudo-random number generator so that subsequent calls to `rand()` produce a reproducible sequence of pseudo-random integers.

## Pre-conditions

1. `seed` is any valid `unsigned int` value — all values are valid; no constraints or validation requirements.
2. No pre-existing state requirements; `srand` may be called at any time, including before any prior call to `rand`.

## Post-conditions

1. The internal pseudo-random number generator state is set such that the next call to `rand()` returns the first value in the deterministic sequence determined by `seed`.
2. The same `seed` value produces the same sequence of `rand()` outputs, enabling reproducible pseudo-random behavior.

## Correctness Verdict

**Correct**

## Semantic Alignment

The declaration `void srand(unsigned int seed);` matches the standard C library signature exactly (`void srand(unsigned int seed)`). The parameter type (`unsigned int`) is consistent with the C standard. No semantic drift — the function does exactly what its declaration implies: seeds the PRNG.

## Implementation Correctness

- **Type compatibility:** The `unsigned int` parameter type matches the standard C `srand`. `random.c` passes `p_repeatable_psuedo_random->seed__current_random` and `seed` (an `i32`) — the `i32` argument at line 48 (`srand(seed)`) is implicitly converted to `unsigned int`, which is valid and well-defined conversion behavior.
- **Undefined behavior:** None. The declaration is well-formed; the implementation is provided by the C standard library.
- **Validation:** No validation needed for a seed parameter — any `unsigned int` is a legal seed.

No custom implementation exists in the Lavender codebase. The `sdl/source/TMP.c` file (line 140) contains a commented-out stub `// void srand(unsigned int seed) {}`, but the active code links against the standard C library's `srand`.

## Side Effects

- **Mutates global PRNG state:** Seeds the process-wide pseudo-random number generator used by `rand()`. This is the only observable side effect. All threads share this global state (standard C behavior).
