swap_ui_element__children — core/source/ui/ui_manager.c

Swaps the child UI_Element of two parent UI_Element objects. Both children are captured before any mutation occurs, ensuring the second parent receives the correct (original) child. If a parent is null, the non-null parent's child is removed (detached and set to null).

Pre-conditions:
1. p_ui_manager is required for priority updates performed by the callee set_ui_element_as__the_parent_of__this_ui_element; it may be null only if no priority adjustment is needed, but this is the caller's responsibility to ensure validity.
2. p_parent__one may be null; if non-null, it must point to a valid, initialized UI_Element.
3. p_parent__two may be null; if non-null, it must point to a valid, initialized UI_Element.
4. The p_child fields of both parents may be null (handled gracefully by the callee).

Post-conditions:
1. If both parents are non-null: p_parent__one's child becomes p_parent__two's original child, and p_parent__two's child becomes p_parent__one's original child. Both children's p_parent pointers are updated to their new parent. The old parent-child links are severed (old child's p_parent set to null, new child's old parent's p_child set to null if applicable).
2. If only p_parent__one is non-null: p_parent__one's child is removed (p_parent__one->p_child set to null, child's p_parent set to null).
3. If only p_parent__two is non-null: p_parent__two's child is removed (p_parent__two->p_child set to null, child's p_parent set to null).
4. If both parents are null: no-op, no state changes.
5. Priority ordering is updated for each child that is re-parented (via set_ui_element_priority_higher_than__this_ui_element_in__ui_manager).

Correctness Verdict: Correct

Semantic Alignment:
The implementation correctly fulfills the semantic intent of swapping children between two parents. The critical design choice is capturing both children (p_child__one and p_child__two) BEFORE any mutation occurs. This prevents the first call to set_ui_element_as__the_parent_of__this_ui_element from invalidating the child pointer needed for the second call. The use of ternary operators for null-safe child extraction, combined with if-guards on the parent pointers before calling the callee, ensures all null cases are handled. The function is not a Lavender-style initialization function (it does not reset structs to initial conditions); it is a structural mutation function.

Implementation Correctness:
Type compatibility — all parameters are UI_Manager * and UI_Element *, matching the function signature exactly. The ternary expressions yield either 0 (a valid null pointer constant in C) or p_parent->p_child (UI_Element *), both of which are type-compatible with the UI_Element * local variables and the callee's parameters. No implicit conversions or truncation occur.
Undefined behavior — no null dereference occurs: null parents are guarded by if-checks before the callee is invoked, and null children are handled internally by set_ui_element_as__the_parent_of__this_ui_element. No out-of-bounds access, no type punning, no broken pointer arithmetic.
Validation — null-parent handling is appropriate for this function's role as a mid-level structural operation. The callee (set_ui_element_as__the_parent_of__this_ui_element) performs its own validation (null parent abort, self-referential parent/child warning). This division of responsibility is consistent with the codebase's patterns.

Side Effects:
Mutates the p_child and p_parent pointers of up to four UI_Element objects (two parents and their two children). For each child that is re-parented (non-null child), the callee also adjusts priority ordering within the UI_Manager via set_ui_element_priority_higher_than__this_ui_element_in__ui_manager, which may swap render priority entries in the UI_Manager's priority table.
