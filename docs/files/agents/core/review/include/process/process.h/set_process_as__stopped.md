set_process_as__stopped — core/include/process/process.h

Sets the process's status to Process_Status_Kind__Stopped.

Pre-conditions:
1. p_process must be a non-null pointer to a writable Process object. In debug builds (NDEBUG not defined), a null p_process triggers debug_abort and returns early. In release builds, the caller is responsible for ensuring p_process is non-null.

Post-conditions:
1. p_process->the_kind_of_status__this_process_has is set to Process_Status_Kind__Stopped.
2. All other fields of the Process struct remain unchanged.

Correctness Verdict: Correct

Semantic Alignment:
The implementation fulfills the semantic intent: it transitions the process to the "Stopped" terminal state. This is distinct from stop_process(), which sets the transitional Process_Status_Kind__Stopping state. The Stopped state is correctly recognized as a finished state by is_process__finished(), which returns true for Process_Status_Kind__Stopped (alongside Complete and Fail).

Implementation Correctness:
Type compatibility — the_kind_of_status__this_process_has is of type Process_Status_Kind (an enum), and Process_Status_Kind__Stopped is a valid constant of the same enum type. No implicit conversions or truncation occur.
Undefined behavior — no broken pointer arithmetic, no null dereference (null is checked in debug builds), no type punning, no out-of-bounds access.
Validation — the debug-mode null check is appropriate and consistent with all other status-setting functions in this header (complete_process, fail_process, stop_process, etc.). In release builds, the absence of validation matches the codebase convention for these low-level inline setters.

Side Effects:
The function mutates p_process->the_kind_of_status__this_process_has, setting it to Process_Status_Kind__Stopped. No other state is modified.
