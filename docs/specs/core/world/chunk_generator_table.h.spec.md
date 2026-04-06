# 1 Specification: core/include/world/chunk_generator_table.h

## 1.1 Overview

Manages a table of chunk generator process handlers indexed by
`Chunk_Generator_Kind`. Each generator is an `m_Process` function that
populates a `Global_Space` with tile data during world construction.

## 1.2 Dependencies

- `defines.h` (for `Chunk_Generator_Table`, `m_Process`)
- `types/implemented/chunk_generator_kind.h` (for `Chunk_Generator_Kind` enum)

## 1.3 Types

### 1.3.1 Chunk_Generator_Table (struct)

    typedef struct Chunk_Generator_Table_t {
        m_Process M_process__chunk_generators[
            Chunk_Generator_Kind__Unknown];
    } Chunk_Generator_Table;

| Field | Type | Description |
|-------|------|-------------|
| `M_process__chunk_generators` | `m_Process[Chunk_Generator_Kind__Unknown]` | Array of generator process handlers indexed by kind. |

### 1.3.2 Chunk_Generator_Kind (enum)

    typedef enum Chunk_Generator_Kind {
        Chunk_Generator_Kind__None = 0,
        Chunk_Generator_Kind__Unknown
    } Chunk_Generator_Kind;

Games extend this enum in their `implemented/` copy. The default generator
is `Chunk_Generator_Kind__None`.

## 1.4 Functions

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `initialize_chunk_generator_table` | `(Chunk_Generator_Table*) -> void` | `void` | Initializes all generator slots to null. |
| `register_chunk_generator_into__chunk_generator_table` | `(Chunk_Generator_Table*, Chunk_Generator_Kind, m_Process) -> void` | `void` | Registers a generator process for the given kind. |
| `get_chunk_generator_process_from__chunk_generator_table` | `(Chunk_Generator_Table*, Chunk_Generator_Kind) -> m_Process` | `m_Process` | Returns the generator process for the given kind. |
| `get_default_chunk_generator_process` | `(Chunk_Generator_Table*) -> m_Process` | `m_Process` | Returns the generator for `Chunk_Generator_Kind__None`. (static inline) |

## 1.5 Agentic Workflow

### 1.5.1 Ownership

Owned by `World` (at `world.chunk_generator_table`). Accessed via
`get_p_chunk_generation_table_from__world`.

### 1.5.2 Registration

Populated by `register_chunk_generators` (see
`implemented/chunk_generator_registrar.h`), which is a game-implemented
template function.

### 1.5.3 Generator Process Convention

Generator processes receive a `Global_Space*` via `p_process_data` and
populate its chunk with tiles. They follow the cooperative process model
(see `process.h` spec).

## 1.6 Header Guard

`CHUNK_GENERATOR_TABLE_H`
