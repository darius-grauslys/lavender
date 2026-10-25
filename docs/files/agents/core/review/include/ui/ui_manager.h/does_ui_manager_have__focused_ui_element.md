does_ui_manager_have__focused_ui_element — core/source/ui/ui_manager.c

Checks whether the UI_Manager currently holds a valid, focused UI_Element, lazily clearing the focus pointer if the referenced element is no longer focused.

Pre-conditions:
1. p_ui_manager must be a non-null pointer to an initialized UI_Manager (no null-check is performed; this is consistent with the codebase convention where callers are responsible for passing valid pointers, as seen in initialize_ui_manager which only guards null in debug builds).
2. p_ui_manager->p_ui_element__focused may be NULL or a valid pointer to a UI_Element that resides within the manager's ui_element pool.

Post-conditions:
1. If p_ui_manager->p_ui_element__focused is non-null AND is_ui_element__focused(p_ui_manager->p_ui_element__focused) returns true, the function returns true and leaves p_ui_element__focused unchanged.
2. If p_ui_manager->p_ui_element__focused is NULL, OR the pointed-to UI_Element is no longer marked as focused (UI_FLAGS__BIT_IS_FOCUSED is unset), the function sets p_ui_manager->p_ui_element__focused to 0 and returns false.

Correctness Verdict: Correct

Semantic Alignment:
The implementation fulfills its semantic intent. It checks whether the manager's tracked focused element is genuinely still focused, and if not, performs a lazy cleanup by nulling the stale pointer. This matches the pattern used by the sibling function get_p_ui_element__focused_of__ui_manager, which performs the same stale-pointer cleanup. The short-circuit evaluation of the && operator ensures is_ui_element__focused is only called when p_ui_element__focused is non-null, preventing a null dereference.

Implementation Correctness:
Type compatibility — p_ui_manager->p_ui_element__focused is of type UI_Element *, and is_ui_element__focused accepts UI_Element *. Types match exactly. No implicit conversions or truncation.
Undefined behavior — no broken pointer arithmetic, no null dereference (guarded by short-circuit &&), no type punning, no out-of-bounds access. The assignment of 0 to a pointer is well-defined.
Validation — no validation of p_ui_manager is performed, which is appropriate for this function's role as a low-level query/cleanup utility. The caller is responsible for passing a valid UI_Manager pointer, consistent with the engine's conventions.

Side Effects:
Mutates p_ui_manager->p_ui_element__focused by setting it to 0 when the currently referenced focused element is either null or no longer marked as focused.
