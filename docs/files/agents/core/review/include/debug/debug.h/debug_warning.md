debug_warning — core/source/debug/debug.c

Prints a warning message to stdout using printf, with a colored "warning:" prefix and a trailing newline.

Pre-conditions:
1. msg_fmt must be a non-null pointer to a valid C string (printf-format compatible).
2. The variadic arguments must match the format specifiers in msg_fmt per the printf contract.

Post-conditions:
1. If NDEBUG is not defined and NLOG is not defined at compile time, a formatted warning line is written to stdout prefixed with an ANSI yellow bold "warning:" and terminated with a newline.
2. If NDEBUG or NLOG is defined, the function is a no-op (no output, no side effects).
3. Returns void.

Correctness Verdict: Correct

Semantic Alignment:
The implementation matches the documented intent from debug.h ("Displays a warning, and nothing else.") and the header note ("All debug print helpers will print a newline."). The function prints exactly the warning message with a "warning:" prefix and a trailing newline, and does no additional work (unlike debug_error, it does not call PLATFORM_coredump).

Implementation Correctness:
- Type compatibility — msg_fmt is const char *, passed directly to vprintf which expects const char *. The va_list is consumed by vprintf with no type mismatch.
- Undefined behavior — va_start is correctly paired with va_end within the same function scope. The only risk is a malformed printf format string, but that is a caller responsibility, not a defect in this function. No pointer arithmetic, no null dereference (msg_fmt would only be UB if NULL, which is a caller contract violation), no type punning, no out-of-bounds access.
- Validation — no validation is needed; printf-style formatting delegates format correctness to the caller. This is appropriate for a low-level debug helper.

Side Effects:
Writes to stdout via printf/vprintf (only when NDEBUG and NLOG are both undefined). No other observable state is modified. When either guard macro is defined, the function has no side effects.
