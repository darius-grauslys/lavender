abs — core/include/platform.h

Computes the absolute (non-negative magnitude) of an int argument.

Pre-conditions:
1. x is an int (the declared parameter type).
2. x must not be INT_MIN — the C standard defines abs(INT_MIN) as undefined behavior, since |INT_MIN| is not representable in int (two's-complement). All callers must guarantee this.

Post-conditions:
1. Returns |x| as a non-negative int.
2. For x == INT_MIN the behavior is undefined; no value is guaranteed.

Correctness Verdict: Correct

Semantic Alignment:
The declaration int abs(int x) faithfully matches the intent of computing the absolute value of an integer, and matches the C standard library abs signature exactly (parameter int, return int). The standard-library implementation that backs this declaration computes |x| as intended. No semantic drift.

Implementation Correctness:
Type compatibility — parameter is int and return is int, matching the C standard library abs exactly. The single caller site in core/source/degree.c passes i32 (int32_t, which is int on the target), an exact match with no implicit conversion or truncation.
Undefined behavior — the only UB is abs(INT_MIN) (documented above). There is no pointer arithmetic, null dereference, type punning, or out-of-bounds access.
Validation — appropriate for a low-level math primitive: no validation is needed; the INT_MIN constraint is the caller's responsibility.
Note — the SDL backend file sdl/source/TMP.c:139 contains a commented-out custom stub "// int abs(int x) {}". Were it ever uncommented, it would be undefined behavior (falling off the end of a non-void function with no return). It is currently inactive, so the active implementation is the standard-library abs.

Side Effects:
No side effects — (standard-library) abs is a pure function: it reads only x and yields |x|, touching no shared/global state.
