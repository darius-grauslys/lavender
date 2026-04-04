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
| `cstr_to_i16__limit_n` | `(const char*, i32 limit_n, i16*) -> bool` | `bool` | Parses via `cstr_to_i32__limit_n`, narrows return to target width, converts to bool, and narrows parsed value to `i16` on success. |
| `cstr_to_i8__limit_n` | `(const char*, i32 limit_n, i8*) -> bool` | `bool` | Parses via `cstr_to_i32__limit_n`, narrows return to target width, converts to bool, and narrows parsed value to `i8` on success. |
| `cstr_to_u16__limit_n` | `(const char*, i32 limit_n, u16*) -> bool` | `bool` | Parses via `cstr_to_u32__limit_n`, narrows return to target width, converts to bool, and narrows parsed value to `u16` on success. |
| `cstr_to_u8__limit_n` | `(const char*, i32 limit_n, u8*) -> bool` | `bool` | Parses via `cstr_to_u32__limit_n`, narrows return to target width, converts to bool, and narrows parsed value to `u8` on success. |

### Narrowing Wrapper Pattern

Each narrowing wrapper follows this pattern:

1. Declare a stack variable `value` of the wide type (i32 or u32),
   initialized to 0.
2. Call the wide parsing function, cast the boolean return to the
   narrow target type, and assign to `value`.
3. Convert `value` to `bool` via `!= 0` comparison and assign to
   `result`.
4. If `result` is true, cast `value` to the narrow type and write
   through the output pointer.
5. Return `result`.

This ensures the output pointer is only written on successful parse,
and the narrowing cast is applied to the parsed value.

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

No overflow check is performed when narrowing from 32-bit to the
smaller type — the value is silently truncated if it exceeds the
target type's range.

### Preconditions

- `p_cstr` must be a valid null-terminated string.
- `limit_n` must be greater than 0.
- Output pointer must be non-null.

### Postconditions

- On success (returns true): the output pointer contains the parsed
  value (narrowed to the target type for wrapper functions).
- On failure (returns false): the output pointer is not modified.

### Error Handling

- Returns `false` on parse failure (invalid characters, empty string,
  overflow for the 32-bit parse functions).
- No `debug_error` or `debug_abort` calls.
