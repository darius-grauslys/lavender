# System Overview: Debug & Console Output

## Purpose

The debug output system provides two independent text output mechanisms
for the engine: a conditional, severity-leveled debug logging system
(`debug.h`) and an unconditional, minimal console abstraction
(`console.h`). Together they cover the full range of text output needs
from developer diagnostics to runtime user-facing messages.

## Architecture

### Subsystem Relationship

    +-------------------------------------------------------+
    |                   Text Output Layer                    |
    |                                                       |
    |  +-------------------------+  +--------------------+  |
    |  |      debug.h            |  |    console.h       |  |
    |  |                         |  |                    |  |
    |  | debug_info__verbose     |  | print_console      |  |
    |  | debug_warning__verbose  |  | clear_console      |  |
    |  | debug_info              |  |                    |  |
    |  | debug_warning           |  | Console (struct)   |  |
    |  | debug_error             |  +--------------------+  |
    |  | debug_abort             |           |              |
    |  +-------------------------+           |              |
    |       |          |                     |              |
    |       v          v                     v              |
    |  +---------+ +----------+    +------------------+    |
    |  |Compile  | |PLATFORM_ |    | Platform display |    |
    |  |Flags    | |Functions |    | surface          |    |
    |  +---------+ +----------+    +------------------+    |
    +-------------------------------------------------------+

### Key Distinction

The two subsystems are **independent** — neither depends on the other,
and they serve different audiences with different guarantees:

| Aspect | `debug.h` | `console.h` |
|--------|-----------|-------------|
| Conditional compilation | Yes — `NDEBUG`, `NLOG`, `VERBOSE` | None — always active |
| Format strings | Yes — `printf`-style variadic | No — plain strings only |
| Severity levels | 6 levels (verbose info/warning, info, warning, error, abort) | None |
| Side effects | `debug_error`: core dump; `debug_abort`: halt | Output only |
| Intended audience | Developer diagnostics | Runtime/user output |
| Newline behavior | Always appended automatically | Not implicitly appended |

## Debug Logging Subsystem (debug.h)

### Severity Escalation

The debug functions follow a strict severity escalation pattern:

    debug_info__verbose(...)    // Noisy development tracing
    debug_info(...)             // General status messages
    debug_warning(...)          // Recoverable issues
    debug_error(...)            // Serious problems, core dump, continues
    debug_abort(...)            // Unrecoverable, halts execution

### Compilation Flag Control

Three preprocessor flags control which debug functions produce output:

| Flag | Effect |
|------|--------|
| `NDEBUG` | Disables `debug_info`, `debug_warning`, `debug_error`, and `debug_abort` output. The `debug.h` header is conditionally included only when `NDEBUG` is **not** defined. |
| `NLOG` | Suppresses all log output across all debug functions. |
| `VERBOSE` | Enables `debug_info__verbose` and `debug_warning__verbose`. These produce no output unless `VERBOSE` is defined. |

#### Effective Visibility Matrix

| Function | Default (no flags) | `VERBOSE` set | `NLOG` set | `NDEBUG` set |
|----------|-------------------|---------------|------------|--------------|
| `debug_info__verbose` | silent | active | silent | silent |
| `debug_warning__verbose` | silent | active | silent | silent |
| `debug_info` | active | active | silent | silent |
| `debug_warning` | active | active | silent | silent |
| `debug_error` | active + coredump | active + coredump | silent | silent |
| `debug_abort` | **always halts** | **always halts** | halts (silent) | halts (silent) |

Note: `debug_abort` always calls `PLATFORM_pre_abort()` and
`PLATFORM_abort()` regardless of flags. Only its **printed output** is
suppressed.

Note: `debug_error` always calls `PLATFORM_coredump()` when output is
active. It does **not** halt execution.

### Platform Hooks

The debug subsystem depends on three platform-implemented functions:

| Function | Called By | Purpose |
|----------|-----------|---------|
| `PLATFORM_pre_abort()` | `debug_abort` (unconditional) | Platform-specific cleanup before halt |
| `PLATFORM_abort()` | `debug_abort` (unconditional) | Halt execution |
| `PLATFORM_coredump()` | `debug_error` (when output active) | Create a core dump if possible |

### Common Usage Pattern: Null Pointer Guard

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

This provides fail-fast behavior during development while compiling to
zero overhead in release builds.

### Error Message Convention

Error and abort messages follow the pattern:

    "function_name, description of problem."

For example:

    debug_abort("complete_process, p_process is null.");
    debug_error("enqueue_process, cannot enqueue itself.");

## Console Subsystem (console.h)

### Functions

| Function | Signature | Description |
|----------|-----------|-------------|
| `print_console` | `(const char *str) -> void` | Outputs a null-terminated string to the console display surface. |
| `clear_console` | `(void) -> void` | Clears all content from the console display surface. |

### Console Struct

    typedef struct Console_t {
    } Console;

An empty struct serving as a placeholder for platform-specific console
state. Backends may extend this with platform-specific fields via the
implemented types pattern if needed.

### Usage

The console functions provide direct text output without formatting,
severity levels, or conditional compilation:

    print_console("Loading world...");
    // ... perform work ...
    clear_console();

## Platform Implementation Requirements

When implementing a new backend, the following must be provided for the
debug and console output system:

### From debug.h

1. **All six debug functions** — `debug_info__verbose`,
   `debug_warning__verbose`, `debug_info`, `debug_warning`,
   `debug_error`, `debug_abort`.
2. **`PLATFORM_pre_abort()`** — called by `debug_abort` before output.
   Used for platform-specific cleanup.
3. **`PLATFORM_abort()`** — called after `debug_abort` output to halt
   execution.
4. **`PLATFORM_coredump()`** — called by `debug_error` to create a
   core dump if possible on the platform.

Implementations must respect the `NDEBUG`, `NLOG`, and `VERBOSE`
preprocessor flags as described above.

### From console.h

1. **`print_console`** — output a string to whatever display surface
   the platform uses as its console.
2. **`clear_console`** — reset/clear that display surface.

These are separate from the `PLATFORM_pre_abort` / `PLATFORM_abort` /
`PLATFORM_coredump` functions required by `debug.h`.

### Error Handling

Console functions do not report errors. If the console is unavailable
on a given platform, implementations should silently no-op.

Debug functions do not validate their own output success. The critical
guarantee is that `debug_abort` always invokes `PLATFORM_pre_abort()`
and `PLATFORM_abort()` regardless of output success or flag state.

## Thread Safety

Neither subsystem is thread-safe. The engine's cooperative scheduling
model means all debug and console output occurs on a single thread,
so this is acceptable for the target platforms.
