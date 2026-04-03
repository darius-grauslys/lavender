# Specification: core/include/world/chunk_pool.h

## Overview

Manages a fixed-size pool of `Chunk` instances. Provides allocation and
deallocation of chunks by 64-bit UUID.

## Dependencies

- `defines.h` (for `Chunk_Pool`, `Chunk`, `Identifier__u64`)
- `defines_weak.h` (forward declarations)

## Types

### Chunk_Pool (struct)

    typedef struct Chunk_Pool_t {
        Chunk chunks[QUANTITY_OF__GLOBAL_SPACE];
    } Chunk_Pool;

| Field | Type | Description |
|-------|------|-------------|
| `chunks` | `Chunk[QUANTITY_OF__GLOBAL_SPACE]` | Fixed pool of chunk instances. |

### Limits

| Macro | Default | Description |
|-------|---------|-------------|
| `QUANTITY_OF__GLOBAL_SPACE` | `VOLUME_OF__LOCAL_SPACE_MANAGER * MAX_QUANTITY_OF__CLIENTS` | Total chunks in pool. |

## Functions

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `initialize_chunk_pool` | `(Chunk_Pool*) -> void` | `void` | Initializes all chunks as deallocated. |
| `allocate_chunk_from__chunk_pool` | `(Chunk_Pool*, Identifier__u64) -> Chunk*` | `Chunk*` | Allocates a chunk with the given UUID. Returns null if pool exhausted. |
| `release_chunk_from__chunk_pool` | `(Chunk_Pool*, Chunk*) -> void` | `void` | Returns a chunk to the pool. |

## Agentic Workflow

### Ownership

Owned by `World` (at `world.chunk_pool`). Accessed via
`get_p_chunk_pool_from__world`.

### Preconditions

- `allocate_chunk_from__chunk_pool`: `uuid__u64` must not be `IDENTIFIER__UNKNOWN__u64`.
- `release_chunk_from__chunk_pool`: `p_chunk` must belong to this pool.

## Header Guard

`CHUNK_POOL_H`
