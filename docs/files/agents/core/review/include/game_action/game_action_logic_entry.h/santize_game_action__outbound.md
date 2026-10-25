santize_game_action__outbound — core/source/game_action/game_action_logic_entry.c

Sanitizes the game_action_flags of a Game_Action by clearing bits specified by the outbound mask and then setting bits specified by the outbound flags from the logic entry.

Pre-conditions:
1. p_game_action_logic_entry must be a non-null pointer to a valid Game_Action_Logic_Entry struct.
2. p_game_action must be a non-null pointer to a writable Game_Action struct.
3. p_game_action_logic_entry->game_action_flags__outbound_mask and game_action_flags__outbound are any valid Game_Action_Flags values (uint8_t); no range constraint.

Post-conditions:
1. p_game_action->game_action_flags is mutated such that all bits set in game_action_flags__outbound_mask are cleared, and all bits set in game_action_flags__outbound are set.
2. Bits not in the mask are preserved (unchanged) unless also targeted by the set operation.

Correctness Verdict: Correct

Semantic Alignment:
The implementation fulfills the semantic intent of "sanitizing" outbound game action flags. The two-step operation (clear masked bits, then set new bits) is the standard mask-and-set pattern. The inbound counterpart (santize_game_action__inbound) uses the same pattern with inbound fields, confirming this is the intended design. The function correctly uses the outbound-specific fields (game_action_flags__outbound_mask and game_action_flags__outbound) rather than the inbound ones.

Implementation Correctness:
Type compatibility — both p_game_action->game_action_flags and the logic entry's game_action_flags__outbound_mask and game_action_flags__outbound fields are of type Game_Action_Flags (uint8_t). The bitwise operations (&=, |=, ~) are performed on identical types. No implicit conversions or truncation.
No undefined behavior — no pointer arithmetic, no null dereference (caller responsibility), no type punning, no out-of-bounds access. The function dereferences two pointers to access struct fields, which is safe given valid pre-conditions.
No validation is needed — this is a low-level bit-manipulation utility. Null pointer validation is the caller's responsibility, consistent with the codebase pattern (e.g., the inbound counterpart and initialize_game_action_logic_entry also do not validate).

Side Effects:
Mutates p_game_action->game_action_flags. No other side effects.
