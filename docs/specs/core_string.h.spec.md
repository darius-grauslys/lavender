# Specification: core/include/core_string.h

## Overview

Provides a utility string copy function that returns the length of the
copied string. This is a convenience wrapper around `strncpy` behavior
with an added return value for tracking string lengths during path
construction and serialization.

## Dependencies

- `defines_weak.h` (for `Index__u32`, `Quantity__u32`)

## Types

None.

## Functions

### strncpy_returns__strlen

    Index__u32 strncpy_returns__strlen(
            void *p_destination,
            const void *p_source,
            Quantity__u32 max_length_of__copy);

Copies up to `max_length_of__copy` bytes from `p_source` to
`p_destination`, behaving like `strncpy`. Returns the length of the
string that was copied (not including the null terminator, if present).

| Parameter | Type | Description |
|-----------|------|-------------|
| `p_destination` | `void*` | Destination buffer. Must be at least `max_length_of__copy` bytes. |
| `p_source` | `const void*` | Source null-terminated string. |
| `max_length_of__copy` | `Quantity__u32` | Maximum number of bytes to copy. |

**Return value**: The number of characters copied (the length of the
resulting string), not including any null terminator.

## Agentic Workflow

### When to Use

Use `strncpy_returns__strlen` when:

- Building file paths incrementally (e.g. appending directory names)
  and you need to track the current write position.
- Copying a string and immediately needing its length for subsequent
  operations.

Do **not** use when:

- You only need to copy a string without knowing its length. Use
  `strncpy` directly.
- The source is not null-terminated. This function assumes C string
  semantics.

### Usage Pattern

    IO_path path;
    Index__u32 index = 0;
    index += strncpy_returns__strlen(
            path + index,
            "/saves/",
            MAX_LENGTH_OF__IO_PATH - index);
    index += strncpy_returns__strlen(
            path + index,
            world_name,
            MAX_LENGTH_OF__IO_PATH - index);

### Preconditions

- `p_destination` must point to a buffer of at least
  `max_length_of__copy` bytes.
- `p_source` must be a valid null-terminated string.
- `max_length_of__copy` must be greater than 0.

### Postconditions

- Up to `max_length_of__copy` bytes are written to `p_destination`.
- The return value is the number of characters copied.

### Error Handling

- No explicit error handling. Null pointers result in undefined behavior.
