# Specification: core/include/debug/debug.h

## Overview

Provides platform-independent debug logging, warning, and error reporting
functions. These are the engine's primary diagnostic output mechanisms,
used throughout core and platform backends for development-time
instrumentation.

All functions in this header are **platform-implemented** — core declares
them but does not define them. Each backend provides its own
implementation. The reference implementation in
`core/source/debug/debug.c` targets POSIX terminals with ANSI color codes.

All debug print helpers append a trailing newline automatically.

## Dependencies

- `<stdarg.h>` (for `va_list`, `va_start`, `va_end` in implementations)
- `<stdio.h>` (for `printf`, `vprintf` in the reference implementation)
- `platform.h` (for `PLATFORM_pre_abort`, `PLATFORM_abort`,
  `PLATFORM_coredump` used by `debug_abort` and `debug_error`)

## Compilation Flags

| Flag | Effect |
|------|--------|
| `NDEBUG` | When defined, disables `debug_info`, `debug_warning`, `debug_error`, and `debug_abort` output. The `debug.h` header is conditionally included in `defines.h` only when `NDEBUG` is **not** defined. |
| `NLOG` | When defined, suppresses all log output (`debug_info`, `debug_warning`, `debug_error`, `debug_abort`, `debug_info__verbose`, `debug_warning__verbose`). |
| `VERBOSE` | When defined, enables `debug_info__verbose` and `debug_warning__verbose`. These functions produce no output unless `VERBOSE` is defined. |

### Effective Visibility Matrix

| Function | `NDEBUG` unset, `NLOG` unset, `VERBOSE` unset | `VERBOSE` set | `NLOG` set | `NDEBUG` set |
|----------|-----------------------------------------------|---------------|------------|--------------|
| `debug_info__verbose` | silent | active | silent | silent |
| `debug_warning__verbose` | silent | active | silent | silent |
| `debug_info` | active | active | silent | silent |
| `debug_warning` | active | active | silent | silent |
| `debug_error` | active + coredump | active + coredump | silent | silent |
| `debug_abort` | **always halts** | **always halts** | halts (silent) | halts (silent) |

Note: `debug_abort` always calls `PLATFORM_pre_abort()` and
`PLATFORM_abort()` regardless of flags. Only its **printed output** is
suppressed by `NDEBUG`/`NLOG`.

Note: `debug_error` always calls `PLATFORM_coredump()` when output is
active. It does **not** halt execution.

## Types

This header defines no types.

## Functions

### Verbose Logging

| Function | Signature | Description |
|----------|-----------|-------------|
| `debug_info__verbose` | `(const char *msg_fmt, ...) -> void` | Prints a verbose informational message. Only produces output when both `VERBOSE` is defined and `NLOG` is not defined. Reference implementation prefixes with `"\033[37;1m(V) info:\033[0m "`. |
| `debug_warning__verbose` | `(const char *msg_fmt, ...) -> void` | Prints a verbose warning message. Only produces output when both `VERBOSE` is defined and `NLOG` is not defined. Reference implementation prefixes with `"\033[33;1m(V) warning:\033[0m "`. |

### Standard Logging

| Function | Signature | Description |
|----------|-----------|-------------|
| `debug_info` | `(const char *msg_fmt, ...) -> void` | Prints an informational message. Suppressed by `NDEBUG` or `NLOG`. Reference implementation prefixes with `"\033[30;1minfo:\033[0m "`. |
| `debug_warning` | `(const char *msg_fmt, ...) -> void` | Prints a warning message. Suppressed by `NDEBUG` or `NLOG`. Reference implementation prefixes with `"\033[33;1mwarning:\033[0m "`. |

### Error Reporting

| Function | Signature | Description |
|----------|-----------|-------------|
| `debug_error` | `(const char *msg_fmt, ...) -> void` | Prints an error message and triggers `PLATFORM_coredump()`. Does **not** halt execution. Suppressed by `NDEBUG` or `NLOG`. Reference implementation prefixes with `"\033[31;1merror:\033[0m "`. |
| `debug_abort` | `(const char *msg_fmt, ...) -> void` | Calls `PLATFORM_pre_abort()`, prints an error message, then calls `PLATFORM_abort()` to halt execution. Output is suppressed by `NDEBUG` or `NLOG`, but `PLATFORM_pre_abort()` and `PLATFORM_abort()` are **always** called unconditionally. Reference implementation prefixes with `"\033[31;1mabort:\033[0m "`. |

### ANSI Color Reference (Reference Implementation)

| Prefix | ANSI Code | Color |
|--------|-----------|-------|
| `(V) info:` | `\033[37;1m` | Bold white |
| `(V) warning:` | `\033[33;1m` | Bold yellow |
| `info:` | `\033[30;1m` | Bold dark gray |
| `warning:` | `\033[33;1m` | Bold yellow |
| `error:` | `\033[31;1m` | Bold red |
| `abort:` | `\033[31;1m` | Bold red |

### Reference Implementation Control Flow

#### debug_info__verbose

    #ifndef NLOG
    #ifdef VERBOSE
        va_start(...)
        printf prefix
        vprintf msg_fmt
        va_end(...)
        printf newline
    #endif
    #endif

#### debug_warning__verbose

    #ifndef NLOG
    #ifdef VERBOSE
        va_start(...)
        printf prefix
        vprintf msg_fmt
        va_end(...)
        printf newline
    #endif
    #endif

#### debug_info

    #ifndef NLOG
    #ifndef NDEBUG
        va_start(...)
        printf prefix
        vprintf msg_fmt
        va_end(...)
        printf newline
    #endif
    #endif

#### debug_warning

    #ifndef NDEBUG
    #ifndef NLOG
        va_start(...)
        printf prefix
        vprintf msg_fmt
        va_end(...)
        printf newline
    #endif
    #endif

#### debug_error

    #ifndef NDEBUG
    #ifndef NLOG
        va_start(...)
        printf prefix
        vprintf msg_fmt
        va_end(...)
        printf newline
        PLATFORM_coredump()
    #endif
    #endif

#### debug_abort

    PLATFORM_pre_abort()          // UNCONDITIONAL
    #ifndef NDEBUG
    #ifndef NLOG
        va_start(...)
        printf prefix
        vprintf msg_fmt
        va_end(...)
        printf newline
    #endif
    #endif
    PLATFORM_abort()              // UNCONDITIONAL

## Agentic Workflow

### Usage Patterns

Debug functions are used throughout the engine for runtime diagnostics.
They follow a severity escalation pattern:

    debug_info__verbose(...)    // Noisy development tracing
    debug_info(...)             // General status messages
    debug_warning(...)          // Recoverable issues
    debug_error(...)            // Serious problems, core dump, continues
    debug_abort(...)            // Unrecoverable, halts execution

### Null Pointer Guard Pattern

Many `static inline` functions throughout the engine use `debug_abort`
as a null-pointer guard in debug builds:

    static inline
    void some_function(SomeType *p_thing) {
    #ifndef NDEBUG
        if (!p_thing) {
            debug_abort("some_function, p_thing is null.");
            return;
        }
    #endif
        // ... normal logic ...
    }

This pattern provides fail-fast behavior during development while
compiling to zero overhead in release builds. See `process.h` for
extensive examples of this pattern.

### Format String Convention

All functions accept `printf`-style format strings with variadic
arguments. Implementations use `va_list` / `va_start` / `va_end`
with `vprintf` (or platform equivalent) internally.

### Error Message Convention

Error and abort messages throughout the engine follow the pattern:

    "function_name, description of problem."

For example:

    debug_abort("complete_process, p_process is null.");
    debug_error("enqueue_process, cannot enqueue itself.");

### Preconditions

- `msg_fmt` must be a valid, non-null `printf`-style format string.
- Variadic arguments must match the format specifiers in `msg_fmt`.

### Postconditions

- `debug_info__verbose`, `debug_warning__verbose`, `debug_info`,
  `debug_warning`: no side effects beyond output.
- `debug_error`: may trigger a core dump via `PLATFORM_coredump()`
  (platform-dependent). Execution continues.
- `debug_abort`: `PLATFORM_pre_abort()` is called, output is emitted
  (if not suppressed), then `PLATFORM_abort()` is called. Control does
  **not** return to the caller.

### Thread Safety

These functions are **not** thread-safe. The engine's cooperative
scheduling model (see `process.h` specification) means all debug
output occurs on a single thread, so this is acceptable for the
target platforms.
