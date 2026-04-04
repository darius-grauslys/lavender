# Specification: core/include/align.h

## Overview

Provides a single macro for stack-allocating a buffer with a guaranteed
memory alignment. This is used on platforms where certain hardware
operations (DMA, SIMD, peripheral registers) require data to be aligned
to specific byte boundaries.

## Dependencies

- `<stdint.h>` (for `intptr_t`, used in pointer arithmetic)

## Types

None.

## Macros

### ALIGN

    #define ALIGN(alignment, type, name)

Stack-allocates a `char` buffer large enough to hold one instance of
`type` plus `alignment` bytes of padding, then computes an aligned
pointer `p_<name>` of type `type*` within that buffer.

| Parameter | Type | Description |
|-----------|------|-------------|
| `alignment` | integer constant | Required byte alignment. Must be a power of 2. |
| `type` | type name | The type of the object to be aligned. |
| `name` | identifier | Base name. Produces `__align_<name>` (raw buffer) and `p_<name>` (aligned pointer). |

**Expansion**:

    char __align_<name>[sizeof(type) + alignment];
    type *p_<name> = (type*)(((intptr_t)__align_<name>)
            + (alignment - ((intptr_t)__align_<name> % alignment)));

**Example**:

    ALIGN(32, Chunk_Data, chunk_data);
    // p_chunk_data is now a Chunk_Data* aligned to a 32-byte boundary.

## Functions

None.

## Agentic Workflow

### When to Use

Use `ALIGN` when:

- A platform peripheral (e.g. NDS DMA) requires data at a specific
  alignment boundary.
- You need a temporary, stack-allocated aligned buffer for a single
  scope.

Do **not** use `ALIGN` when:

- The data is heap-allocated. Use platform-specific aligned allocation
  instead.
- The alignment requirement is already satisfied by the type's natural
  alignment.
- The buffer must persist beyond the current scope (stack allocation
  is scope-limited).

### Usage Pattern

    void my_dma_function(void) {
        ALIGN(32, My_Struct, my_data);
        // p_my_data is a My_Struct* aligned to 32 bytes
        memset(p_my_data, 0, sizeof(My_Struct));
        // ... use p_my_data ...
        // p_my_data is invalid after this scope exits
    }

### Preconditions

- `alignment` must be a power of 2 and greater than 0.
- `sizeof(type) + alignment` must fit on the stack. On constrained
  platforms (e.g. Nintendo DS), large types or large alignments may
  cause stack overflow.
- `type` must be a complete type (i.e. `sizeof(type)` must be valid).

### Postconditions

- `p_<name>` points to a region of at least `sizeof(type)` bytes within
  `__align_<name>`, aligned to `alignment` bytes.
- `((intptr_t)p_<name>) % alignment == 0`.
- The memory is uninitialized.

### Limitations

- Stack-only. The aligned pointer is invalid after the enclosing scope
  exits.
- Only one `ALIGN` per `name` per scope (due to variable naming).
- The raw buffer `__align_<name>` wastes up to `alignment - 1` bytes.

### Error Handling

None. Misuse (non-power-of-2 alignment, insufficient stack space) results
in undefined behavior.
