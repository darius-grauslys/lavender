get_p_global_space_from__local_space — core/include/world/local_space.h, lines 29-35

Returns the Global_Space pointer stored in the Local_Space's p_global_space field, or null if the input is null.

Pre-conditions:
1. p_local_space is a pointer (may be NULL).

Post-conditions:
1) If p_local_space is non-null, returns p_local_space->p_global_space (the Global_Space* stored in the struct).
2) If p_local_space is null, returns 0 (NULL).

Correctness Verdict: Correct

Semantic Alignment:
The function retrieves the Global_Space pointer associated with a Local_Space. The ternary correctly distinguishes between null and non-null inputs. The member access p_local_space->p_global_space directly yields the intended Global_Space pointer. No semantic drift.

Implementation Correctness:
Type compatibility — parameter type Local_Space * matches the struct's p_global_space field type (Global_Space *). Return type Global_Space * is exact; no implicit conversion or truncation.
No undefined behavior — the null check guards against null dereference. No pointer arithmetic, no type punning, no out-of-bounds access.
No validation is needed — this is a simple accessor/getter function. The caller is responsible for ensuring p_local_space is a valid pointer if a non-null result is expected.

Side Effects:
No side effects — this function only reads from the input pointer and returns a value. It does not mutate any state.