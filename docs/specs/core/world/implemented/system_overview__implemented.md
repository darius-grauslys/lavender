# 1 System Overview: Implemented (Game Templates)

## 1.1 Purpose

The `implemented/` subfolder contains **template** headers that declare
game-specific registration functions. These files are copied to the game
project's corresponding `implemented/` directory by the `lav_new_project`
script. The game developer modifies the copies; the originals in core serve
as defaults. The `implemented/` directory is NOT in the core include path —
it is only in the game project's include path.

## 1.2 Architecture

### 1.2.1 Template Files

| File | Function Declared | Registers Into | Called During |
|------|-------------------|---------------|--------------|
| `chunk_generator_registrar.h` | `register_chunk_generators` | `Chunk_Generator_Table` | World initialization |
| `tile_logic_table_registrar.h` | `register_tile_logic_tables` | `Tile_Logic_Table` | World initialization |

### 1.2.2 Registration Flow

    Game initialization / World initialization
        |
        +-> register_chunk_generators(&chunk_generator_table)
        |   |
        |   +-> For each game-defined Chunk_Generator_Kind:
        |       register_chunk_generator_into__chunk_generator_table(
        |           &table, kind, m_process_handler)
        |
        +-> register_tile_logic_tables(p_game, &tile_logic_table)
            |
            +-> For each game-defined Tile_Kind:
                Populate Tile_Logic_Record with:
                    - Tile_Logic_Flags (unpassable, sight blocking, no ground)
                    - tile_height__i32F4

## 1.3 Template Behavior

### 1.3.1 How Templates Work

1. The core engine ships default versions of these headers in
   `core/include/world/implemented/`.
2. The `lav_new_project` script copies them to the game project's
   `implemented/` directory.
3. The game developer modifies the copies to register game-specific
   chunk generators and tile logic records.
4. The game project's include path includes its own `implemented/`
   directory, which shadows the core defaults.

### 1.3.2 Associated Enum Extensions

Each registrar depends on a corresponding enum that the game must also
extend in its `types/implemented/` directory:

| Registrar | Depends On Enum | Default Values |
|-----------|----------------|----------------|
| `register_chunk_generators` | `Chunk_Generator_Kind` | `Chunk_Generator_Kind__None`, `Chunk_Generator_Kind__Unknown` |
| `register_tile_logic_tables` | `Tile_Kind` | `Tile_Kind__None`, `Tile_Kind__Unknown` |

The game adds new enum values between `__None` and `__Unknown` to define
its custom tile kinds and chunk generator kinds.

## 1.4 Integration Points

| System | Integration |
|--------|-------------|
| `Chunk_Generator_Table` | Populated by `register_chunk_generators`. Used during chunk construction to select the appropriate generation process. |
| `Tile_Logic_Table` | Populated by `register_tile_logic_tables`. Used at runtime for tile passability, sight blocking, height, and custom flag queries. |
| `World` | Owns both tables. Initialization calls both registration functions. |

## 1.5 Preconditions

- Both registration functions must be implemented by the game project.
- The corresponding enums must be extended before registration is called.
- Registration functions are called exactly once during world initialization.
