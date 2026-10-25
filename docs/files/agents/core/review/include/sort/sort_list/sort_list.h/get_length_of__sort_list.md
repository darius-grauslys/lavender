get_length_of__sort_list — core/include/sort/sort_list/sort_list.h

Returns the number of nodes in a Sort_List by reading its size_of__p_node_list field.

Pre-conditions:
1. p_sort_list must be a non-null pointer to a valid, initialized Sort_List struct.
2. In debug builds (NDEBUG not defined), null is checked via debug_abort before dereference. In release builds, passing null results in undefined behavior — this is the caller's responsibility.

Post-conditions:
1. Returns the value of p_sort_list->size_of__p_node_list, a 31-bit bitfield representing the number of nodes allocated in the sort list.
2. No state is mutated — the function is purely read-only.

Correctness Verdict: Correct

Semantic Alignment:
The function correctly retrieves and returns the size_of__p_node_list field, which semantically represents the length (number of nodes) of the sort list. The implementation directly matches the intended purpose of returning the sort list's length. No semantic drift is present.

Implementation Correctness:
Type compatibility — The return type is Quantity__u32 (uint32_t) and size_of__p_node_list is declared as `Quantity__u32 size_of__p_node_list :31`, so the types match exactly with no implicit conversion or truncation.
Undefined behavior — In debug builds, the null pointer is checked before dereference, preventing UB. In release builds, the check is compiled out; this is a deliberate codebase-wide pattern and the caller is expected to ensure validity.
Validation — The debug-only null check is appropriate for catching programming errors during development. No additional validation is needed for a simple accessor function — it does not validate ranges or state beyond the pointer check.

Side Effects:
No side effects. This is a pure read accessor that reads p_sort_list->size_of__p_node_list and returns its value without modifying any state.