santize_game_action__inbound — core/source/game_action/game_action_logic_entry.c

Clears and sets specific flag bits on a Game_Action's inbound flags using a mask-and-OR pattern from the Game_Action_Logic_Entry configuration.

Pre-conditions:
1. p_game_action_logic_entry must be a non-null pointer to a valid Game_Action_Logic_Entry.
2. p_game_action must be a non-null pointer to a valid Game_Action.
3. game_action_flags__inbound_mask in the logic entry specifies which bits to clear (1 = clear).
4. game_action_flags__inbound in the logic entry specifies which bits to set (1 = set).

Post-conditions:
1. p_game_action is mutated: bits in game_action_flags corresponding to mask bits set to 1 in game_action_flags__inbound_mask are cleared, then bits set to 1 in game_action_flags__inbound are OR'd in.

Correctness Verdict: Correct

Semantic Alignment:
The function correctly implements a sanitize operation for inbound game action flags. The mask clears the bits that the logic entry wants to control (via &= ~mask), and then the inbound flags are applied (via |= flags__inbound). This matches the intent of sanitizing inbound game actions according to the logic entry's configuration.

Implementation Correctness:
Type compatibility — all operations are on Game_Action_Flags (uint8_t), so types match exactly. No implicit conversions or truncation.
No undefined behavior — both pointers are dereferenced directly without null checks, but this is consistent with the low-level pattern used throughout the codebase where callers are expected to pass valid pointers. No pointer arithmetic, no type punning, no out-of-bounds access.
Validation — no validation is performed within the function; this is appropriate for a low-level flag manipulation function, consistent with the codebase pattern where callers ensure pointer validity.

Side Effects:
Mutates p_game_action->game_action_flags in place. No other side effects.
