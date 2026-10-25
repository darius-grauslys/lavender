set_ui_manager_as__dirty — core/include/ui/ui_manager.h, lines 168-171

Sets the IS_DIRTY flag bit on a UI_Manager's flags field, marking the manager as needing re-composition.

Pre-conditions:
1. p_ui_manager must be a non-null pointer to a valid, writable UI_Manager object.

Post-conditions:
1. p_ui_manager->ui_manager_flags__u8 has the UI_MANAGER_FLAG__IS_DIRTY bit (bit 0) set.
2. All other bits in ui_manager_flags__u8 are preserved (bitwise OR is used, not assignment).
3. After return, is_ui_manager__dirty(p_ui_manager) will return true.

Correctness Verdict: Correct

Semantic Alignment:
The implementation fulfills its semantic intent — it marks the UI_Manager as dirty by setting the IS_DIRTY flag bit. This flag is used to indicate that the UI manager's composition has changed (e.g., UI elements were added or removed) and a re-composition pass is needed. The bitwise OR operation correctly sets only the target bit without disturbing other flag bits.

Implementation Correctness:
Type compatibility — UI_MANAGER_FLAG__IS_DIRTY is BIT(0) which expands to ((1U) << (0)), a u32 value of 1. The field ui_manager_flags__u8 is of type UI_Manager_Flags__u8 (a u8). The |= operation promotes the u8 to int for the bitwise OR, then truncates back to u8 on assignment. Since the value being ORed (1) fits within u8 range, there is no truncation or data loss. No implicit signed/unsigned conversion issues arise since both operands are effectively unsigned.
No undefined behavior — no pointer arithmetic, no null dereference (assuming pre-condition holds), no type punning, no out-of-bounds access. The function dereferences p_ui_manager once to access the flags field, which is a direct struct member access.
No validation is performed — this is a low-level static inline helper. The caller is responsible for ensuring p_ui_manager is non-null and valid. This is consistent with the pattern used by sibling functions like is_ui_manager__dirty and set_ui_manager_as__NOT_dirty, which also perform no null checks.

Side Effects:
Mutates p_ui_manager->ui_manager_flags__u8 by setting the IS_DIRTY bit via bitwise OR. No other state is modified. No memory allocation, no I/O, no calls to other functions.
