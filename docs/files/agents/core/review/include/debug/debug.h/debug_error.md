debug_error — core/source/debug/debug.c

Displays a formatted error message to stdout (with a red "error:" prefix and trailing newline) and triggers a platform core dump, without halting program execution.

Pre-conditions:
1. msg_fmt must be a non-null pointer to a valid printf-style format string (standard printf-family contract).
2. The variadic arguments following msg_fmt must be consistent with the format specifiers in msg_fmt.
3. These pre-conditions apply only when logging is enabled (i.e., neither NDEBUG nor NLOG is defined); if either is defined, the function body is compiled out and no arguments are used.

Post-conditions:
1) When NDEBUG and NLOG are both undefined: the formatted error message is printed to stdout with a red "error:" prefix followed by a newline, and PLATFORM_coredump() is invoked to attempt a core dump. The program continues execution (the function does not abort or exit).
2) When either NDEBUG or NLOG is defined: the function performs no work — no output is produced and no core dump is created.
3) The function always returns void; no return value is produced in any configuration.

Correctness Verdict: Correct

Semantic Alignment:
The implementation faithfully fulfills the documented semantic intent in debug.h — "Displays an error, and if possible for the given backend, creates a core dump." The error text is printed with the red "error:" prefix, a newline is appended, and PLATFORM_coredump() is called to create the core dump. The comment on line 75 ("create core dump, but keep going") confirms that not halting is intentional and matches the distinction between debug_error and debug_abort. The conditional compilation guards match the pattern used by debug_warning and debug_info, and the function correctly degrades to a no-op in release/non-logging builds.

Implementation Correctness:
Type compatibility — msg_fmt (const char *) matches the expected type for printf/vprintf; args_list (va_list) is correctly initialized via va_start(args_list, msg_fmt), where msg_fmt is the last named parameter — correct usage of the C variadic API. No implicit conversions or truncation occur.
Undefined behavior — no pointer arithmetic, no null dereference, no type punning, no out-of-bounds access. The only remaining risk is a null msg_fmt or mismatched format arguments, which is standard caller-contract behavior for printf-family functions (not an implementation defect).
Validation — no validation is performed, which is appropriate for a low-level debug logging function that follows the printf contract. Ensuring a non-null msg_fmt and well-formed format string is the caller's responsibility; adding defensive validation here would be inconsistent with the function's role and the convention used by the sibling debug_* helpers.

Side Effects:
Writes formatted text (the red "error:" prefix, the formatted message, and a trailing newline) to stdout via printf/vprintf. Invokes PLATFORM_coredump(), which may produce platform-specific effects such as flushing output and writing a core dump artifact to disk. The function does NOT terminate the program (no abort/exit call). When logging is disabled (NDEBUG or NLOG defined), there are no side effects.
