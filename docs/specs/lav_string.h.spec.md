# Specification: core/include/lav_string.h

## Overview

Provides C-string to integer parsing functions with length limits. These
are the engine's safe string-to-number conversion utilities, used for
parsing configuration values, user input, and serialized text data.

All functions return a boolean indicating success or failure, and write
the parsed value through an output pointer.

## Dependencies

- `defines_weak.h` (for `i32`, `u32`, `i16`, `i8`, `u16`, `u8`, `bool`)

## Types

None.

## Functions

### Core Parsing Functions

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `cstr_to_i32__limit_n` | `(const char*, i32 limit_n, i32*) -> bool` | `bool` | Parses a signed 32-bit integer from a C-string, reading at most `limit_n` characters. Returns true on success. |
| `cstr_to_u32__limit_n` | `(const char*, i32 limit_n, u32*) -> bool` | `bool` | Parses an unsigned 32-bit integer from a C-string, reading at most `limit_n` characters. Returns true on success. |

### Narrowing Wrappers (static inline)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `cstr_to_i16__limit_n` | `(const char*, i32 limit_n, i16*) -> bool` | `bool` | Parses via `cstr_to_i32__limit_n` and narrows to `i16`. |
| `cstr_to_i8__limit_n` | `(const char*, i32 limit_n, i8*) -> bool` | `bool` | Parses via `cstr_to_i32__limit_n` and narrows to `i8`. |
| `cstr_to_u16__limit_n` | `(const char*, i32 limit_n, u16*) -> bool` | `bool` | Parses via `cstr_to_u32__limit_n` and narrows to `u16`. |
| `cstr_to_u8__limit_n` | `(const char*, i32 limit_n, u8*) -> bool` | `bool` | Parses via `cstr_to_u32__limit_n` and narrows to `u8`. |

## Agentic Workflow

### When to Use

Use these functions when:

- Parsing numeric values from configuration files or user input.
- Converting serialized text fields to numeric types.
- Any situation where `atoi` / `strtol` would be used but you need
  bounded parsing and success/failure indication.

### Usage Pattern

    i32 value;
    if (cstr_to_i32__limit_n(p_cstr, 10, &value)) {
        // parsing succeeded, use value
    } else {
        // parsing failed
    }

### Known Issues

The narrowing wrappers cast the **return value** of the inner parsing
function rather than the parsed value:

    bool result = (i16)cstr_to_i32__limit_n(...);

This casts the boolean result (0 or 1) to the narrow type and then
assigns to `bool`, which works correctly but is misleading. The actual
narrowing of the parsed value is done correctly via the separate
assignment. However, no overflow check is performed when narrowing from
32-bit to the smaller type — the value is silently truncated.

### Preconditions

- `p_cstr` must be a valid null-terminated string.
- `limit_n` must be greater than 0.
- Output pointer must be non-null.

### Postconditions

- On success (returns true): the output pointer contains the parsed value.
- On failure (returns false): the output pointer is not modified (for
  narrowing wrappers, the intermediate `value` variable is 0 but the
  output is only written on success).

### Error Handling

- Returns `false` on parse failure (invalid characters, empty string,
  overflow for the 32-bit parse functions).
- No `debug_error` or `debug_abort` calls.
