# 1 Specification: core/include/world/chunk_pool.h

## 1.1 Overview

Manages a fixed-size pool of `Chunk` instances. Provides allocation and
deallocation of chunks by 64-bit UUID.

## 1.2 Dependencies

- `defines.h` (for `Chunk_Pool`, `Chunk`, `Identifier__u64`)
- `defines_weak.h` (forward declarations)

## 1.3 Types

### 1.3.1 Chunk_Pool (struct)

    typedef struct Chunk_Pool_t {
        Chunk chunks[QUANTITY_OF__GLOBAL_SPACE];
    } Chunk_Pool;

| Field | Type | Description |
|-------|------|-------------|
| `chunks` | `Chunk[QUANTITY_OF__GLOBAL_SPACE]` | Fixed pool of chunk instances. |

### 1.3.2 Limits

| Macro | Default | Description |
|-------|---------|-------------|
| `QUANTITY_OF__GLOBAL_SPACE` | `VOLUME_OF__LOCAL_SPACE_MANAGER * MAX_QUANTITY_OF__CLIENTS` | Total chunks in pool. |

## 1.4 Functions

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `initialize_chunk_pool` | `(Chunk_Pool*) -> void` | `void` | Initializes all chunks as deallocated. |
| `allocate_chunk_from__chunk_pool` | `(Chunk_Pool*, Identifier__u64) -> Chunk*` | `Chunk*` | Allocates a chunk with the given UUID. Returns null if pool exhausted. |
| `release_chunk_from__chunk_pool` | `(Chunk_Pool*, Chunk*) -> void` | `void` | Returns a chunk to the pool. |

## 1.5 Agentic Workflow

### 1.5.1 Ownership

Owned by `World` (at `world.chunk_pool`). Accessed via
`get_p_chunk_pool_from__world`.

### 1.5.2 Preconditions

- `allocate_chunk_from__chunk_pool`: `uuid__u64` must not be `IDENTIFIER__UNKNOWN__u64`.
- `release_chunk_from__chunk_pool`: `p_chunk` must belong to this pool.

## 1.6 Header Guard

`CHUNK_POOL_H`
