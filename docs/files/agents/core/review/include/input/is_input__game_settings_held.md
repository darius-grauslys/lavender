is_input__game_settings_held — core/include/input/input.h

Returns whether the game settings input flag is currently held.

Pre-conditions:
1. p_input must be a non-null pointer to a writable Input object (the function dereferences it without a null check).

Post-conditions:
1. Returns true if the INPUT_GAME_SETTINGS bit is set in input_flags__held; returns false otherwise.

Correctness Verdict: Correct

Semantic Alignment:
The implementation correctly checks whether the INPUT_GAME_SETTINGS bit (a single bit, value 1<<4 = 16) is set in the input_flags__held bitmask. The bitwise AND yields a non-zero value exactly when the bit is set, which converts to true. This matches the semantic intent of querying the held state of the game settings input.

Implementation Correctness:
Type compatibility — input_flags__held is Input_Flags__u32 (uint32_t), and INPUT_GAME_SETTINGS expands to (INPUT_BACKWARD<<1) which is (1<<3)<<1 = 1<<4 = 16, also of type int/uint32_t in practice. The bitwise AND yields a uint32_t, which is implicitly converted to bool for the return. This is a standard, well-defined conversion in C (any non-zero value becomes true, zero becomes false). No truncation occurs.
No undefined behavior — no pointer arithmetic, no null dereference (given the non-null pre-condition), no type punning, no out-of-bounds access.
No validation is performed, which is consistent with all 17 other is_input__*_held functions in the same file. Validation is the caller's responsibility; this is a low-level query function appropriate for inline expansion.

Side Effects:
No side effects — the function only reads input_flags__held and returns a boolean based on the bitwise test. No state is mutated.
