# Specification: core/include/serialization/game_directory.h

## Overview

Provides file system utilities for game data persistence. Handles checking
for game data files, saving game state, and path manipulation for the
engine's directory structure.

## Dependencies

- `defines.h` (for `Game`, `IO_path`, `Index__u32`)

## Types

### IO_path

    typedef char IO_path[MAX_LENGTH_OF__IO_PATH];

A fixed-size character buffer for file system paths. `MAX_LENGTH_OF__IO_PATH`
defaults to 128 and is defined in `platform_defaults.h`.

## Functions

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `stat_game_data_file` | `(Game*, char* buffer) -> Index__u32` | `Index__u32` | Checks for the existence of the game data file. Populates `buffer` with the path. Returns an index or status code. |
| `save_game` | `(Game*) -> void` | `void` | Saves the current game state. **Only call from the main menu.** |
| `append_path` | `(IO_path path, IO_path appended) -> void` | `void` | Appends `appended` to `path` in-place. |

## Agentic Workflow

### When to use this module

- Use `stat_game_data_file` to check if a save file exists before attempting
  to load.
- Use `save_game` from the main menu scene to persist game state.
- Use `append_path` when constructing file paths for world data, region
  files, or other serialized assets.

### Preconditions

- `save_game` must only be called from the main menu context. Calling it
  during gameplay may result in incomplete or corrupted saves.
- `p_game` must be fully initialized.
- Path buffers must be of size `MAX_LENGTH_OF__IO_PATH`.

### Postconditions

- After `save_game`: game state is written to disk via the platform file
  system.
- After `append_path`: `path` contains the concatenated result.

### Error Handling

- `stat_game_data_file` returns a status code; check the return value
  before proceeding with file operations.

### Platform Integration

This module relies on platform functions for actual file I/O:

- `PLATFORM_get_base_directory`
- `PLATFORM_append_base_directory_to__path`
- `PLATFORM_open_file`
- `PLATFORM_write_file`
- `PLATFORM_read_file`
- `PLATFORM_close_file`
- `PLATFORM_access`
- `PLATFORM_mkdir`

### Path Separator

The path separator character is defined in `platform_defaults.h` as
`PATH_SEPERATOR` (defaults to `'/'`).
