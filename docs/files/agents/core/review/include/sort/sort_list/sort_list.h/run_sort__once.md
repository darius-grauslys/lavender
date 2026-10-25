run_sort__once — core/include/sort/sort_list/sort_list.h

Invokes the sort list's step-function once and returns whether sorting is complete.

Pre-conditions:
1. p_sort_list must be a non-null pointer to a valid Sort_List object (checked in debug builds via debug_abort).
2. p_sort_list->m_sort must be a non-null function pointer (checked in debug builds via debug_abort).
3. In release builds (NDEBUG defined), both preconditions are caller-responsibility; violating them results in undefined behavior.

Post-conditions:
1. The m_sort function pointer has been invoked exactly once with p_sort_list as its sole argument.
2. The return value of m_sort (true if fully sorted, false otherwise) is intended to be returned to the caller — however, the implementation is buggy and does NOT actually return this value (see Correctness Verdict).

Correctness Verdict: Incorrect

Semantic Alignment:
The semantic intent of run_sort__once is to execute a single step of the sort algorithm and return whether the list is now fully sorted. The m_Sort typedef (defined in defines.h) specifies: "Return true if fully sorted, otherwise false." The function signature declares a bool return type, and the debug-mode error paths correctly return true. However, the normal execution path calls `p_sort_list->m_sort(p_sort_list)` without a `return` keyword. This means the function's return value is undefined (falling off the end of a non-void function in C). The implementation does NOT fulfill its semantic intent of returning the sort-completion status to the caller.

Implementation Correctness:
- Type compatibility: The parameter type (Sort_List *) matches the m_Sort typedef's parameter type exactly. No implicit conversions or truncation occur.
- Undefined behavior: Yes — the function is declared to return bool but falls off the end of the function body without a return statement on the normal execution path. In C, falling off the end of a non-void function results in undefined behavior. The compiler may return an indeterminate value in the appropriate register, meaning callers receive garbage.
- Validation: The debug-mode validation (null checks for p_sort_list and p_sort_list->m_sort) is appropriate and consistent with the codebase's pattern. In release builds, validation is the caller's responsibility, which is also consistent with the engine's design philosophy.
- Fix: The last line should be `return p_sort_list->m_sort(p_sort_list);` instead of `p_sort_list->m_sort(p_sort_list);`.

Side Effects:
The function invokes p_sort_list->m_sort(p_sort_list), which may mutate the Sort_List and its associated Sort_Node array (e.g., swapping nodes, updating sort_data fields like index_of__heapification and index_of__heap_sort). The function itself does not directly mutate any struct fields — all mutation is delegated to the m_sort callee.
