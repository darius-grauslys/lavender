does_process_have__run_handler — core/include/process/process.h, lines 237-247

Checks whether the given Process has a non-null run handler function pointer.

Pre-conditions:
1. p_process must be a non-null pointer to a valid Process struct. (In debug builds, this is enforced via a null check that calls debug_abort and returns false. In release builds, the caller is responsible for ensuring p_process is non-null, consistent with the codebase-wide convention for inline accessors.)

Post-conditions:
1. Returns true if p_process->m_process_run__handler is non-null (i.e., the Process has a run handler assigned).
2. Returns false if p_process->m_process_run__handler is null (i.e., the Process has no run handler).
3. In debug mode, returns false if p_process is null (after aborting).
4. The Process struct is not mutated; the function is a pure query.

Correctness Verdict: Correct

Semantic Alignment:
The function correctly fulfills its semantic intent: it tests whether the Process's run handler function pointer is non-null. The return statement `return p_process->m_process_run__handler;` implicitly converts the function pointer to bool, which is well-defined in C — any non-null pointer converts to true, and a null pointer converts to false. This matches the intent of the function name and the analogous does_process_have__dispose_handler, which follows the identical pattern.

Implementation Correctness:
Type compatibility: m_process_run__handler is of type m_Process (a function pointer typedef: void (*m_Process)(Process*, Game*)). Returning it as bool is a valid implicit conversion in C — a pointer-to-function is implicitly convertible to _Bool. No truncation or data loss occurs.
Undefined behavior: In debug mode, the null check on p_process prevents null dereference. In release mode (NDEBUG defined), there is no null check, so a null p_process would cause undefined behavior — but this is the established convention across all inline accessor functions in this codebase (e.g., is_process__active, get_process_status, does_process_have__dispose_handler, etc.).
No pointer arithmetic, no type punning, no out-of-bounds access.

Side Effects:
No side effects. This is a pure query function — it reads p_process->m_process_run__handler and returns a boolean. The Process struct is not modified.