debug_abort — core/source/debug/debug.c

Terminates the program via the platform abort hook, optionally logging a formatted, "abort:"-prefixed message to stdout first.

Pre-conditions:
1. msg_fmt must be a valid, non-NULL, null-terminated format string readable by vprintf (a NULL msg_fmt is undefined behavior, matching printf-family contract).
2. If msg_fmt contains conversion specifiers, the caller must supply matching variadic arguments of the correct type and count (standard C varargs contract).
3. The function must be invoked from a context where process termination is acceptable — debug_abort never returns.
4. Standard output must be in a usable state for the optional printf/vprintf calls.

Post-conditions:
1. The function does not return. Its final action, PLATFORM_abort(), terminates the process (POSIX/SDL/no_gui raise SIGABRT via abort(); NDS triggers platform reset via memory-mapped I/O at address 8192).
2. If NDEBUG and NLOG are both undefined, a formatted message prefixed with "abort:" is printed to stdout before termination.
3. No Lavender-owned resources (structs, pools, memory) are cleaned up by this function; process-level resource reclamation is left to the OS/platform upon abort.

Correctness Verdict: Correct

Semantic Alignment:
The implementation faithfully fulfills its semantic intent as a fatal abort facility. It mirrors the structure of sibling debug routines (debug_error, debug_warning, debug_info) while making two distinctions. First, unlike debug_error (which creates a core dump but keeps running), debug_abort always terminates — it calls PLATFORM_pre_abort() then PLATFORM_abort(), never falling through to a return. Second, the logging block is gated behind "!NDEBUG && !NLOG", so the formatted message is emitted only in debug builds with logging enabled, while the abort itself is unconditional. This is the correct split: the fatal termination must always occur, and the human-readable message is a debug-build convenience. The ordering (pre-abort hook → optional logging → abort) is the intended sequence, allowing platforms (e.g., NDS) to set up debug output before the message is printed and before the fatal signal/reset. No semantic drift or omission is present.

Implementation Correctness:
- Type compatibility: msg_fmt is const char *, passed directly to vprintf which expects const char * for the format — exact match. Variadic arguments are forwarded via va_list; va_start(args_list, msg_fmt) correctly names msg_fmt as the last named parameter. No implicit conversions or truncation.
- Undefined behavior: va_start/va_end are correctly paired inside the conditional block and are not invoked when NDEBUG or NLOG is defined. printf/vprintf are not called with a NULL format within the enabled path (documented as a caller pre-condition). No pointer arithmetic, no null dereference, no type punning, no out-of-bounds access within this function. PLATFORM_abort() does not return, so any implicit fall-through after it is unreachable — this is well-defined.
- Validation: No null/format validation is performed, which is appropriate. debug_abort is a low-level facility following the printf contract; validation of whether an abort condition holds is the caller's responsibility (confirmed by the 100+ call sites, each of which evaluates a condition and passes a pre-computed message). Adding defensive checks here would deviate from standard C library conventions and the project's own patterns.

Side Effects:
- Calls PLATFORM_pre_abort() (platform side effect: a no-op on SDL/no_gui; on NDS it initializes the debug sub-screen console so the abort message is visible).
- If logging is enabled (!NDEBUG && !NLOG), prints a message prefixed "abort:" to stdout via printf/vprintf.
- Calls PLATFORM_abort(), which terminates the process (aborts via SIGABRT on POSIX/SDL/no_gui; triggers a platform reset on NDS).
- The function never returns; no Lavender-owned data structures, pools, or allocated memory are mutated or freed by it.
