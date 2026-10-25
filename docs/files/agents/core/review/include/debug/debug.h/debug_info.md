debug_info — core/source/debug/debug.c

Prints a debug info message (prefixed with "info:" and ANSI color formatting) to stdout using printf/vprintf, only when both NLOG and NDEBUG are undefined (logging and debug builds enabled); otherwise compiles to a no-op.

Pre-conditions:
1. `msg_fmt` must be a non-null pointer to a valid null-terminated format string (same contract as `printf`).
2. The variadic arguments following `msg_fmt` must match the format specifiers in `msg_fmt` (same contract as `printf`/`vprintf`).

Post-conditions:
1. When neither NLOG nor NDEBUG is defined: prints to stdout the prefix "info:" (black bold ANSI color), then the formatted message, then a trailing newline. This matches the header note that "All debug print helpers will print a newline."
2. When NLOG or NDEBUG is defined: the function body is excluded by the preprocessor, so it has no observable effect on stdout or any state.

Correctness Verdict: Correct

Semantic Alignment:
The implementation fulfills its documented intent in debug.h:30-32 ("Displays a message, and nothing else."). It prints the info prefix, the formatted message, and a trailing newline — consistent with all sibling debug print helpers. The output exactly matches the expected pattern.

Implementation Correctness:
Type compatibility — `msg_fmt` is `const char *`, matching `vprintf`'s expected first argument type. The `va_list`/`va_start(args_list, msg_fmt)`/`va_end(args_list)` triad is the standard and correct usage for a variadic function. No implicit conversions or truncation.
No undefined behavior — `vprintf` is called with a `va_list` initialized by `va_start`, which is well-defined. No pointer arithmetic, no null dereference (assuming the caller honors the printf contract), no type punning, no out-of-bounds access.
No validation is performed and none is needed — this mirrors the standard C `printf` contract where the caller is responsible for a valid format string and matching arguments. The header documents this as a simple display function.

Side Effects:
Writes to stdout (via `printf`/`vprintf`) when both NLOG and NDEBUG are undefined. When NLOG or NDEBUG is defined at compile time, the function compiles to nothing — no side effects. Does not modify any program state, global variables, or heap allocations.
