# Specification: core/include/platform.h

## Overview

Declares all platform-dependent function signatures that must be
implemented by a backend (e.g. SDL, Nintendo DS, no_gui). This is the
engine's **platform abstraction layer** — core code calls these
`PLATFORM_*` functions, and each backend provides the implementations.

Also declares standard C library function signatures (`malloc`, `free`,
`memcpy`, `memset`, `abs`, `srand`, `rand`, `strncmp`, `strnlen`,
`strncpy`) to ensure they are available on all platforms, including
freestanding environments.

Also defines the `IO_path` type used for file system paths.

## Dependencies

- `platform_defaults.h` (for `MAX_LENGTH_OF__IO_PATH` and other defaults)
- `platform_defines.h` (backend-specific, must define `PLATFORM_DEFINES_H`)
- `defines_weak.h` (forward declarations)

## Types

### IO_path

    typedef char IO_path[MAX_LENGTH_OF__IO_PATH];

Fixed-size character array for file system paths. Default max length is
128 characters (configurable via `platform_defaults.h`).

### PLATFORM Type Forward Declarations

    typedef struct PLATFORM_Gfx_Context_t PLATFORM_Gfx_Context;
    typedef struct PLATFORM_Texture_t PLATFORM_Texture_t;
    typedef struct PLATFORM_Sprite_t PLATFORM_Sprite;

## Function Sections

### SECTION_audio

| Function | Signature | Description |
|----------|-----------|-------------|
| `PLATFORM_initialize_audio` | `(PLATFORM_Audio_Context*) -> void` | Initializes the audio subsystem. (TODO: remove) |
| `PLATFORM_allocate_audio_effect` | `(PLATFORM_Audio_Context*) -> Audio_Effect*` | Allocates an audio effect. Returns null on failure. |
| `PLATFORM_play_audio_effect` | `(PLATFORM_Audio_Context*, Audio_Effect*) -> void` | Plays an audio effect. |
| `PLATFORM_poll_audio_effects` | `(PLATFORM_Audio_Context*) -> void` | Polls/updates active audio effects. |
| `PLATFORM_play_audio__stream` | `(PLATFORM_Audio_Context*, Audio_Stream_Kind) -> void` | Starts streaming audio. |
| `PLATFORM_is_audio__streaming` | `(PLATFORM_Audio_Context*) -> bool` | Returns true if audio is currently streaming. |

### SECTION_debug

| Function | Signature | Description |
|----------|-----------|-------------|
| `PLATFORM_coredump` | `(void) -> void` | Creates a core dump. |
| `PLATFORM_pre_abort` | `(void) -> void` | Called before abort for cleanup. |
| `PLATFORM_abort` | `(void) -> void` | Halts execution. |

### SECTION_entity

| Function | Signature | Description |
|----------|-----------|-------------|
| `PLATFORM_render_entity` | `(Entity*, Game*) -> void` | Renders an entity. (TODO: remove) |

### SECTION_game_actions

| Function | Signature | Description |
|----------|-----------|-------------|
| `m_PLATFORM_game_action_handler_for__multiplayer` | `(Game*, Game_Action*) -> void` | Platform multiplayer game action handler. (TODO: remove) |

### SECTION_rendering

| Function | Signature | Description |
|----------|-----------|-------------|
| `PLATFORM_put_char_in__typer` | `(Gfx_Context*, Typer*, unsigned char) -> void` | Renders a character in a typer. |
| `PLATFORM_allocate_sprite` | `(Gfx_Context*, Graphics_Window*, Sprite*, Texture_Flags) -> PLATFORM_Sprite*` | Allocates a platform sprite. |
| `PLATFORM_release_sprite` | `(Gfx_Context*, PLATFORM_Sprite*) -> void` | Releases a platform sprite. |
| `PLATFORM_release_all__sprites` | `(PLATFORM_Gfx_Context*) -> void` | Releases all sprites. |
| `PLATFORM_render_sprite` | `(Gfx_Context*, Graphics_Window*, Sprite*, Vector__3i32F4) -> void` | Renders a sprite at a position. |
| `PLATFORM_initialize_rendering__game` | `(PLATFORM_Gfx_Context*) -> void` | Initializes game rendering. (TODO: remove) |
| `PLATFORM_allocate_texture` | `(PLATFORM_Gfx_Context*, PLATFORM_Graphics_Window*, Texture_Flags, Texture*) -> bool` | Allocates a texture. Returns true on failure. |
| `PLATFORM_allocate_texture_with__path` | `(PLATFORM_Gfx_Context*, PLATFORM_Graphics_Window*, Texture_Flags, const char*, Texture*) -> bool` | Allocates a texture from a file path. Returns true on failure. |
| `PLATFORM_update_texture` | `(Texture) -> void` | Updates a texture. |
| `PLATFORM_use_texture` | `(PLATFORM_Gfx_Context*, Texture) -> void` | Binds a texture. (TODO: remove) |
| `PLATFORM_release_texture` | `(PLATFORM_Gfx_Context*, Texture) -> void` | Releases a texture. |

### SECTION_core

| Function | Signature | Description |
|----------|-----------|-------------|
| `PLATFORM_initialize_time` | `(void) -> void` | Initializes the time subsystem. |
| `PLATFORM_get_date_time` | `(Date_Time*) -> void` | Gets the current date and time. |
| `PLATFORM_get_time_elapsed` | `(Timer__u32*, Timer__u32*) -> u32F20` | Returns elapsed time in fixed-point. |
| `PLATFORM_initialize_game` | `(Game*) -> void` | Platform-specific game initialization. |
| `PLATFORM_close_game` | `(Game*) -> void` | Platform-specific game cleanup. |
| `PLATFORM_pre_render` | `(Game*) -> void` | Called before rendering. |
| `PLATFORM_post_render` | `(Game*) -> void` | Called after rendering. |

### SECTION_ui

| Function | Signature | Description |
|----------|-----------|-------------|
| `PLATFORM_allocate_gfx_window` | `(Gfx_Context*, Texture_Flags) -> PLATFORM_Graphics_Window*` | Allocates a graphics window. |
| `PLATFORM_release_gfx_window` | `(Gfx_Context*, Graphics_Window*) -> void` | Releases a graphics window. |
| `PLATFORM_get_provided_windows` | `(Gfx_Context*, PLATFORM_Graphics_Window**, Texture_Flags*, Quantity__u32, Index__u32) -> Quantity__u32` | Gets platform-provided windows. Returns overflow count. |
| `PLATFORM_compose_gfx_window` | `(Game*, Graphics_Window*) -> void` | Composes a graphics window via tiles. |
| `PLATFORM_compose_ui_span_in__gfx_window` | `(Game*, Graphics_Window*, Quantity__u32, Quantity__u32, Index__u32, Index__u32) -> void` | Composes a UI tile span in a window. |
| `PLATFORM_compose_world` | `(Game*, Graphics_Window*) -> void` | Composes world tiles into a window. |
| `PLATFORM_project_gfx_window` | `(Game*, Graphics_Window*) -> void` | Projects a window via 3D projection. |
| `PLATFORM_project_world` | `(Game*, Graphics_Window*) -> void` | Projects the world via 3D projection. |
| `PLATFORM_render_gfx_window` | `(Game*, Graphics_Window*) -> void` | Renders a graphics window. |

### SECTION_serialization

| Function | Signature | Description |
|----------|-----------|-------------|
| `PLATFORM_initialize_file_system_context` | `(Game*, PLATFORM_File_System_Context*) -> void` | Initializes the file system. (TODO: remove) |
| `PLATFORM_get_base_directory` | `(IO_path) -> Quantity__u32` | Gets the base directory path. Returns length. |
| `PLATFORM_access` | `(const char*, IO_Access_Kind) -> int` | Checks file access. |
| `PLATFORM_opendir` | `(const char*) -> PLATFORM_Directory*` | Opens a directory. |
| `PLATFORM_closedir` | `(PLATFORM_Directory*) -> void` | Closes a directory. |
| `PLATFORM_mkdir` | `(const char*, uint32_t) -> bool` | Creates a directory. |
| `PLATFORM_append_base_directory_to__path` | `(PLATFORM_File_System_Context*, char*, Index__u32*) -> void` | Appends base directory to a path. |
| `PLATFORM_get_quantity_of__active_serialization_requests` | `(PLATFORM_File_System_Context*) -> Quantity__u32` | Returns active serialization request count. |
| `PLATFORM_allocate_serialization_request` | `(PLATFORM_File_System_Context*) -> Serialization_Request*` | Allocates a serialization request. |
| `PLATFORM_release_serialization_request` | `(PLATFORM_File_System_Context*, Serialization_Request*) -> void` | Releases a serialization request. |
| `PLATFORM_open_file` | `(PLATFORM_File_System_Context*, const char*, const char*, Serialization_Request*) -> PLATFORM_Open_File_Error` | Opens a file. |
| `PLATFORM_close_file` | `(PLATFORM_File_System_Context*, Serialization_Request*) -> void` | Closes a file. |
| `PLATFORM_write_file` | `(PLATFORM_File_System_Context*, u8*, Quantity__u32, Quantity__u32, void*) -> PLATFORM_Write_File_Error` | Writes to a file. |
| `PLATFORM_read_file` | `(PLATFORM_File_System_Context*, u8*, Quantity__u32*, Quantity__u32, void*) -> PLATFORM_Read_File_Error` | Reads from a file. |
| `PLATFORM_get_position_in__file` | `(PLATFORM_File_System_Context*, void*) -> Index__u32` | Gets file position. Returns -1 on error. |
| `PLATFORM_set_position_in__file` | `(PLATFORM_File_System_Context*, Index__u32, void*) -> bool` | Sets file position. |
| `PLATFORM_get_directories` | `(PLATFORM_File_System_Context*, IO_path, char*, Quantity__u32, Quantity__u32) -> Quantity__u32` | Lists directories. |

### SECTION_input

| Function | Signature | Description |
|----------|-----------|-------------|
| `PLATFORM_poll_input` | `(Game*, Input*) -> void` | Polls platform input. |

### SECTION_log

| Function | Signature | Description |
|----------|-----------|-------------|
| `PLATFORM_update_log__global` | `(Game*) -> bool` | Updates global log display. (TODO: remove) |
| `PLATFORM_update_log__local` | `(Game*) -> bool` | Updates local log display. (TODO: remove) |
| `PLATFORM_update_log__system` | `(Game*) -> bool` | Updates system log display. (TODO: remove) |
| `PLATFORM_clear_log__global` | `(Game*) -> bool` | Clears global log display. (TODO: remove) |
| `PLATFORM_clear_log__local` | `(Game*) -> bool` | Clears local log display. (TODO: remove) |
| `PLATFORM_clear_log__system` | `(Game*) -> bool` | Clears system log display. (TODO: remove) |

### SECTION_multiplayer

| Function | Signature | Description |
|----------|-----------|-------------|
| `PLATFORM_tcp_begin` | `(Game*) -> PLATFORM_TCP_Context*` | Initializes TCP subsystem. |
| `PLATFORM_tcp_end` | `(Game*) -> void` | Shuts down TCP subsystem. |
| `PLATFORM_tcp_connect` | `(PLATFORM_TCP_Context*, IPv4_Address*) -> PLATFORM_TCP_Socket*` | Connects to a remote host. Returns null on failure. |
| `PLATFORM_tcp_poll_connect` | `(PLATFORM_TCP_Socket*) -> TCP_Socket_State` | Polls connection status. |
| `PLATFORM_tcp_server` | `(PLATFORM_TCP_Context*, Index__u16 port) -> PLATFORM_TCP_Socket*` | Creates a server socket. Returns null on failure. |
| `PLATFORM_tcp_close_socket` | `(PLATFORM_TCP_Context*, PLATFORM_TCP_Socket*) -> bool` | Closes a socket. Returns true on error. |
| `PLATFORM_tcp_poll_accept` | `(PLATFORM_TCP_Context*, PLATFORM_TCP_Socket*, IPv4_Address*) -> PLATFORM_TCP_Socket*` | Accepts a new connection. |
| `PLATFORM_tcp_send` | `(PLATFORM_TCP_Socket*, u8*, Quantity__u32) -> i32` | Sends bytes. Returns count or -1 on error. |
| `PLATFORM_tcp_recieve` | `(PLATFORM_TCP_Socket*, u8*, Quantity__u32) -> i32` | Receives bytes. Returns count or TCP_ERROR. |

### Standard C Library

| Function | Signature |
|----------|-----------|
| `free` | `(void*) -> void` |
| `malloc` | `(unsigned long) -> void*` |
| `memcpy` | `(void*, const void*, unsigned long) -> void*` |
| `memset` | `(void*, int, unsigned long) -> void*` |
| `abs` | `(int) -> int` |
| `srand` | `(unsigned int) -> void` |
| `rand` | `(void) -> int` |
| `strncmp` | `(const char*, const char*, size_t) -> int` |
| `strnlen` | `(const char*, size_t) -> size_t` |
| `strncpy` | `(char*, const char*, size_t) -> char*` |

## Agentic Workflow

### Role in the Engine

`platform.h` is the **contract** between core and backends. Core code
calls `PLATFORM_*` functions without knowing the implementation. Each
backend (SDL, NDS, no_gui) provides implementations in its own source
files.

### Implementing a New Backend

To create a new backend:

1. Create `platform_defines.h` in your backend's include directory.
   Define `PLATFORM_DEFINES_H` and all `PLATFORM_*` structs.
2. Implement all `PLATFORM_*` functions declared in this file.
3. Optionally override defaults from `platform_defaults.h` in your
   `platform_defines.h`.

### Compile-Time Guard

    #ifndef PLATFORM_DEFINES_H
    #error Cannot build AncientsGame without a backend implementation.
    #endif

This ensures compilation fails immediately if no backend is configured.

### Preconditions

- `platform_defines.h` must be provided by the backend and must define
  `PLATFORM_DEFINES_H`.
- All `PLATFORM_*` structs must be defined before `platform.h` is
  included.

### Error Handling

- Functions that can fail return error enums (`PLATFORM_Open_File_Error`,
  `PLATFORM_Write_File_Error`, `PLATFORM_Read_File_Error`) or null
  pointers.
- `PLATFORM_tcp_send` / `PLATFORM_tcp_recieve` return negative values
  on error.
- `PLATFORM_allocate_texture` / `PLATFORM_allocate_texture_with__path`
  return `true` on failure (inverted convention).
