poll_input — core/source/input/input.c

Polls platform-specific input state into the Input struct, and dispatches input game actions to multiplayer clients when input is active.

Pre-conditions:
1. p_game must be a non-null pointer to a valid Game struct.
2. p_input must be a non-null pointer to a writable Input struct.
3. p_game->pM_clients may be NULL (single-player/offline mode) or non-NULL (multiplayer mode).
4. p_game->m_game_action_handler__dispatch must be initialized if pM_clients is non-NULL (caller responsibility).

Post-conditions:
1. p_input is mutated by PLATFORM_poll_input — input_flags__held, input_flags__pressed, and input_flags__released are updated to reflect the current platform input state.
2. If any of the three flag fields is non-zero AND p_game->pM_clients is non-NULL, dispatch_game_action__input is called to create a Game_Action from the input and dispatch it to the server.
3. The return value of dispatch_game_action__input (a bool) is discarded.

Correctness Verdict: Correct

Semantic Alignment:
The function correctly coordinates input polling with action dispatch. It first delegates to the platform layer to update the Input struct, then checks whether any input is currently active (held, pressed, or released), and only forwards input to the game action dispatcher when multiplayer clients are present. This matches the semantic intent described in the comment at line 2574-2576 of defines.h: when clients exist, input is relayed to the server; the input flags are the trigger condition. The short-circuit || evaluation is efficient — it stops as soon as any non-zero flag is found. The dispatch is conditionally gated on pM_clients being non-NULL, preventing unnecessary action creation in offline mode.

Implementation Correctness:
Type compatibility — p_game is Game *; PLATFORM_poll_input(Game *, Input *) and dispatch_game_action__input(Game *, Input *) both accept Game * and Input *. p_input is Input *, matching both. No implicit conversions or truncation. The three flag checks use uint32_t truthiness (non-zero → true) which is correct for bitmask-based flag fields. p_game->pM_clients is Client *; testing it for non-null is correct. Undefined behavior — no pointer arithmetic, no null dereference (assuming p_game and p_input are valid), no type punning, no out-of-bounds access. One observation: the return value of dispatch_game_action__input (bool) is discarded — this is not undefined behavior, but if that return value encodes a dispatch failure that the caller should handle, the failure is silently ignored. Validation — no validation is performed on input pointers; this is consistent with the Lavender pattern for mid-level functions where the caller is responsible for providing valid pointers.

Side Effects:
p_input is mutated (its flag fields and potentially cursor positions are updated by PLATFORM_poll_input). If input is active and clients exist, dispatch_game_action__input is invoked — this has its own side effects (network dispatch, game state mutation) but tracking callee internals is out of scope per the review guide. The function itself does not directly modify any state beyond calling its delegates.
