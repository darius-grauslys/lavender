is_ui_manager__dirty — core/include/ui/ui_manager.h

Checks whether the UI_Manager's dirty flag is set, indicating that a composition is pending.

Pre-conditions:
1. p_ui_manager must be a non-null pointer to a valid UI_Manager object.
2. The ui_manager_flags__u8 field must be a valid UI_Manager_Flags__u8 (a u8); only the BIT(0) bit is read by this function.

Post-conditions:
1. Returns true if the UI_MANAGER_FLAG__IS_DIRTY bit is set in ui_manager_flags__u8; returns false otherwise.
2. No state is modified — the function is a pure read.

Correctness Verdict: Correct

Semantic Alignment:
The implementation correctly tests the dirty flag by performing a bitwise AND between ui_manager_flags__u8 and UI_MANAGER_FLAG__IS_DIRTY (BIT(0)). The result is non-zero when the bit is set and zero when it is not, which maps correctly to bool true/false on return. This aligns with the semantic intent of determining whether the UI manager needs composition.

Implementation Correctness:
Type compatibility — ui_manager_flags__u8 is a UI_Manager_Flags__u8 (typedef'd to u8), and UI_MANAGER_FLAG__IS_DIRTY is BIT(0) (an int). Both are promoted to int by the & operator, and the result is implicitly converted to bool on return. No truncation or data loss occurs.
No undefined behavior — no pointer arithmetic, no null dereference (caller must ensure non-null), no type punning, no out-of-bounds access.
No validation is needed — this is a low-level inline query function consistent with the codebase style (other inline accessors in ui_manager.h also do not null-check). The caller is responsible for passing a valid pointer.

Side Effects:
No side effects — the function only reads from the pointed-to UI_Manager struct and returns a bool.
