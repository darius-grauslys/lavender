set_ui_manager_as__NOT_dirty — core/include/ui/ui_manager.h

Clears the IS_DIRTY flag on a UI_Manager's flags byte.

Pre-conditions:
1. p_ui_manager must be a non-null pointer to a writable UI_Manager object.
2. The ui_manager_flags__u8 field must be a valid UI_Manager_Flags__u8 (u8) value.

Post-conditions:
1. The UI_MANAGER_FLAG__IS_DIRTY bit in p_ui_manager->ui_manager_flags__u8 is cleared (set to 0).
2. All other bits in ui_manager_flags__u8 remain unchanged.

Correctness Verdict: Correct

Semantic Alignment:
The function's intent is to mark the UI_Manager as not dirty by clearing the IS_DIRTY flag. The implementation performs a bitwise AND with the complement of UI_MANAGER_FLAG__IS_DIRTY, which correctly clears only that specific bit while preserving all other flag bits. This matches the semantic intent exactly.

Implementation Correctness:
Type compatibility — p_ui_manager is UI_Manager_Flags__u8 (u8) and UI_MANAGER_FLAG__IS_DIRTY is BIT(0) (u8). The bitwise AND assignment is type-safe with no implicit conversions or truncation.
Undefined behavior — no pointer arithmetic, no null dereference (pre-condition requires non-null), no type punning, no out-of-bounds access. The operation is a simple bitwise clear on a valid u8 field.
Validation — no validation is performed, which is appropriate for this low-level inline flag manipulation function. It is the caller's responsibility to ensure p_ui_manager is valid.

Side Effects:
Mutates p_ui_manager->ui_manager_flags__u8 by clearing the UI_MANAGER_FLAG__IS_DIRTY bit. No other side effects.
