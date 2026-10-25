debug_warning__verbose — core/source/debug/debug.c

Prints a verbose warning to stdout with a yellow "(V) warning:" prefix, the printf-formatted variadic arguments, and a trailing newline — only when NLOG is undefined and VERBOSE is defined at compile time.

Pre-conditions:
1. msg_fmt must be a non-null pointer to a NUL-terminated format string compatible with vprintf. Passing NULL is undefined behavior (vprintf requires a valid format string).
2. The variadic arguments supplied by the caller must match the conversion specifiers in msg_fmt (caller responsibility; C variadic calls are not type-checked at runtime).
3. Compile-time: NLOG must be undefined (logging enabled) and VERBOSE must be defined (verbose mode on) for the body to be compiled; otherwise the function is an empty no-op.

Post-conditions:
1. Returns void.
2. If either NLOG is defined or VERBOSE is not defined, no output occurs and no state changes.
3. If both compile guards pass, stdout receives: the prefix "\033[33;1m(V) warning:\033[0m ", the result of vprintf(msg_fmt, args_list), and a final "\n". No other state (globals, files, etc.) is modified.

Correctness Verdict: Correct

Semantic Alignment:
The implementation matches the header's documented intent: "Displays a verbose warning, and nothing else. Only if VERBOSE compilation const is defined." and the header note "All debug print helpers will print a newline." The "(V) warning:" prefix and trailing printf("\n") are present. Color (yellow bold, \033[33;1m) is consistent with the sibling debug_warning and the Lavender convention that warnings are yellow. The "(V)" qualifier distinguishes this verbose variant from debug_warning, whose prefix is plain "warning:". The structure mirrors debug_info__verbose (white "(V) info:") — same guard nesting, same va_start/vprintf/va_end pattern — so the verbose family is internally consistent.

Implementation Correctness:
Type compatibility — msg_fmt (const char *) is passed to va_start as the required last named parameter and to vprintf (which expects const char *restrict); args_list (va_list) is passed to vprintf (which expects va_list). All types match exactly; no implicit conversions or truncation.
Undefined behavior — va_start is correctly paired with va_end on every path where it is reached (there is no early return or branch between them), so the va_list is always properly closed. No pointer arithmetic, no type punning, no out-of-bounds access. The only UB risk is a NULL msg_fmt, which is a documented caller precondition across all sibling debug functions (debug_info__verbose, debug_info, debug_warning, debug_error) and is intentionally left unguarded as a low-level debug helper.
Validation — no runtime NULL-check on msg_fmt is performed. This is appropriate and consistent with the established convention for these debug print helpers; validation is the caller's responsibility, and vprintf itself would surface the caller's error as UB in the same way for all siblings.

Side Effects:
When both compile-time guards are satisfied, the function writes colored text to stdout (the "(V) warning:" prefix, the formatted variadic message, and a trailing newline). When either guard is not satisfied, the entire body is compiled out and the function has no side effects. A local va_list is initialized with va_start and cleaned up with va_end; no global, file, or external state is mutated.
