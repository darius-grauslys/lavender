get_elapsed_time__u32F20_of__game — core/include/game.h

Returns the game's accumulated elapsed time (fixed-point F20).

Pre-conditions:
1. p_game must be a non-null pointer to an initialized Game object.

Post-conditions:
1. Returns p_game->time_elapsed__u32F20 (a u32F20, i.e., uint32_t with F20 scaling).
2. The Game struct is not modified by this call.

Correctness Verdict: Correct

Semantic Alignment:
The function performs a direct read of the time_elapsed__u32F20 field, which is the field that tracks accumulated elapsed time within the Game struct. This field is mutated elsewhere by poll_elapsed_time__u32F20_of__game (core/source/game.c) via PLATFORM_get_time_elapsed. The accessor matches the semantic intent — it returns the elapsed time stored on the game, not a recomputed value.

Implementation Correctness:
Type compatibility — return type u32F20 matches the field type u32F20 exactly (both uint32_t).
No undefined behavior — no pointer arithmetic, no null dereference of p_game (caller must provide valid pointer), no type punning, no out-of-bounds access. The dereference is a single field offset access.
No validation needed — this is a low-level inline accessor; the caller owns the Game lifetime and is responsible for ensuring it is valid and initialized.

Side Effects:
No side effects.
