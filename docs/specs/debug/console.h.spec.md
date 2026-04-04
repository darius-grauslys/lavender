# Specification: core/include/debug/console.h

## Overview

Provides a minimal console abstraction for text output and clearing.
The `Console` struct and its associated functions offer a simple
interface for displaying text to a platform-specific console or
output surface.

This is a lightweight utility intended for basic text display,
separate from the more feature-rich debug logging system in `debug.h`
and the UI-based `Typer`/`Log` systems.

## Dependencies

- None (self-contained header).

## Types

### Console (struct)

    typedef struct Console_t {

    } Console;

An empty struct serving as a placeholder for platform-specific console
state. Backends may extend this with platform-specific fields via the
implemented types pattern (similar to `Entity_Data`, `UI_Element_Data`,
etc.) if needed.

| Field | Type | Description |
|-------|------|-------------|
| *(none)* | — | The struct is currently empty. It exists as a forward-looking type for potential platform-specific extensions. |

## Functions

| Function | Signature | Description |
|----------|-----------|-------------|
| `print_console` | `(const char *str) -> void` | Outputs the given null-terminated string to the console. |
| `clear_console` | `(void) -> void` | Clears all content from the console. |

## Agentic Workflow

### Usage Patterns

The console functions provide direct text output without the formatting,
severity levels, or conditional compilation of the `debug.h` functions.
Use `print_console` for user-facing or always-on output that should not
be suppressed by `NDEBUG` or `NLOG`.

    print_console("Loading world...");
    // ... perform work ...
    clear_console();

### Relationship to debug.h

| Aspect | `console.h` | `debug.h` |
|--------|-------------|-----------|
| Conditional compilation | None — always active | Controlled by `NDEBUG`, `NLOG`, `VERBOSE` |
| Format strings | No — plain strings only | Yes — `printf`-style variadic |
| Severity levels | None | verbose info, info, warning, error, abort |
| Side effects | Output only | Output, core dump (`debug_error`), halt (`debug_abort`) |
| Intended audience | Runtime/user output | Developer diagnostics |
| Newline behavior | Not implicitly appended | Always appended |

### Platform Implementation Requirements

When implementing a new backend, the following must be provided:

1. **`print_console`** — Output a string to whatever display surface
   the platform uses as its console (terminal, on-screen text layer,
   etc.).
2. **`clear_console`** — Reset/clear that display surface.

These are separate from the `PLATFORM_pre_abort` / `PLATFORM_abort` /
`PLATFORM_coredump` functions required by `debug.h`.

### Preconditions

- `print_console`: `str` must be a valid, non-null, null-terminated
  C string.

### Postconditions

- `print_console`: the string content is displayed on the console.
  No newline is implicitly appended (unlike `debug.h` functions).
- `clear_console`: the console display surface is empty.

### Error Handling

These functions do not report errors. If the console is unavailable
on a given platform, implementations should silently no-op.
