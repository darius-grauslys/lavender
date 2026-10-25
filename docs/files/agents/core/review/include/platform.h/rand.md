rand — core/include/platform.h, line 174

Forward declaration of the standard C library pseudo-random number generator.

Pre-conditions:
1. There are no parameters.
2. The pseudo-random number generator must have been seeded via the matching `srand` declaration (line 173) prior to relying on the result. The C standard guarantees a fallback seed of 1 if no seeding occurs, but every engine call site in `core/source/random.c` invokes `srand` before `rand`, so this invariant holds at all actual usage points.

Post-conditions:
1. Returns an `int` pseudo-random value in the inclusive range [0, RAND_MAX] per the C standard.
2. Advances the internal state of the global PRNG so that repeated calls without reseeding yield different values.
3. No engine state is read or written by the declaration itself.

Correctness Verdict: Correct

Semantic Alignment:
`rand` is not a Lavender-implemented function; it is a verbatim forward declaration of the standard C library `rand`. The declaration matches the documented semantics of the C standard exactly, so there is no semantic drift to evaluate within the engine.

Implementation Correctness:
There is no Lavender implementation body under review. The `platform.h` file header (lines 14-19) documents that everything declared in this file is "NOT implemented in core" and is "platform dependent," to be supplied by a backend. This is confirmed by `sdl/source/TMP.c` (line 141), where the engine-side stub `// int rand(void) {}` is commented out and the SDL backend instead relies on the host C standard library. Because there is no engine-defined body, there are no type-compatibility, undefined-behavior, or validation concerns within Lavender's code: `int rand(void)` is the exact standard prototype with no implicit conversions, no pointer parameters to validate, and no engine-defined arithmetic that could be off, reentrant, or type-punned. The correctness of the actual behavior is the backend's (or the host libc's) responsibility, which is consistent with the file's design intent.

Side Effects:
Advances the global pseudo-random number generator's internal state. (From the engine's perspective, the only effect is the returned integer; the state mutation is the standard library's internal behavior, not an engine side effect.)

Reviewer note: The original stub entry `(no implementation found)` is accurate and intentional — `rand` is a stdlib forward declaration, not an engine function. No implementation exists to patch or fix within Lavender.
