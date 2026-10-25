debug_info__verbose — core/source/debug/debug.c

Prints a verbose informational message to stdout with a colored "(V) info:" prefix, but only when logging is enabled (NLOG undefined) and verbose mode is active (VERBOSE defined); otherwise the function is a no-op.

Pre-conditions:
1. msg_fmt must be a non-null, valid printf-style format string.
2. The variadic arguments must match the conversion specifiers in msg_fmt (standard printf contract).
3. If NLOG is defined, msg_fmt and all variadic arguments are ignored (no-op).
4. If VERBOSE is not defined, msg_fmt and all variadic arguments are ignored (no-op).

Post-conditions:
1) Returns void (no return value).
2) When NLOG is defined or VERBOSE is not defined: no observable effect; the function is a no-op.
3) When NLOG is not defined and VERBOSE is defined: a single line is written to stdout consisting of the escape sequence "\033[37;1m(V) info:\033[0m ", followed by the formatted message text, followed by a newline. No return value.

Correctness Verdict: Correct

Semantic Alignment:
The implementation fulfills the semantic intent declared in debug.h ("Displays a verbose message, and nothing else. Only if VERBOSE compilation const is defined."). The guard condition is NLOG-undefined AND VERBOSE-defined; this dual guard is consistent across all sibling debug functions in the same file (e.g., debug_info, debug_warning, debug_error all use NLOG + a debug-level macro), so the VERBOSE-only mention in the header is a documentation simplification rather than an implementation mismatch. The "(V) info:" prefix correctly distinguishes verbose informational output. The output matches the documented behavior of appending a trailing newline.

Implementation Correctness:
Type compatibility — msg_fmt (const char *) is passed to printf and vprintf as the first argument (which expect const char *); args_list (va_list) is passed to vprintf as the second argument (which expects va_list). No implicit conversions or truncation occur.
Undefined behavior — va_start and va_end are correctly paired within the same conditional branch; va_start is invoked with msg_fmt (the last named parameter) as the second argument, which is correct. No pointer arithmetic, no null dereference, no type punning, no out-of-bounds access. Passing the user-supplied format string directly to vprintf is the standard pattern; a malformed format string or argument mismatch is the caller's responsibility (same contract as printf itself), not a defect of this function. When the function body is compiled out (NLOG defined or VERBOSE undefined), the variadic arguments are simply never consumed — no UB results from the caller passing more arguments than are read.
Validation — no internal validation is performed, which is appropriate for a low-level debug helper; the caller is responsible for supplying a valid format string and matching arguments.

Side Effects:
When active (NLOG undefined and VERBOSE defined): writes to the standard output stream via printf and vprintf, which is an observable external side effect on global I/O. When inactive, there are no side effects.
