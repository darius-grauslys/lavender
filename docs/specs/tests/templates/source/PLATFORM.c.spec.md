# Specification: tests/templates/source/PLATFORM.c

## Overview

Stub implementations of all `PLATFORM_*` functions for building tests
without a real platform backend. Guarded by `#if !defined(PLATFORM)`.

## Dependencies

- `defines.h`, `timer.h`
- `<stdlib.h>` (for `abort`)
- `<unistd.h>` (POSIX: `fork`)
- `<time.h>` (POSIX: `clock_gettime`, `localtime`)
- `<windows.h>`, `<mmsystem.h>` (Windows: `timeGetTime`)

## Compile Guard

    #if !defined(PLATFORM)
    ...
    #endif

## Functions

### Time (functional implementations)

| Function | Return | Behavior |
|----------|--------|----------|
| `PLATFORM_initialize_time` | `void` | Records monotonic clock baseline (POSIX) or no-op (Windows) |
| `PLATFORM_get_time_elapsed` | `u32F20` | Computes elapsed time using `clock_gettime` (POSIX) or `timeGetTime` (Windows) |
| `PLATFORM_get_date_time` | `void` | Fills `Date_Time` from `localtime` (POSIX only) |

### Process Control

| Function | Behavior |
|----------|----------|
| `PLATFORM_coredump` | `fork()` + `abort()` child (POSIX) or no-op |
| `PLATFORM_pre_abort` | No-op |
| `PLATFORM_abort` | Calls `abort()` |

### No-op Stubs (return void)

`PLATFORM_pre_render`, `PLATFORM_post_render`, `PLATFORM_compose_world`,
`PLATFORM_compose_gfx_window`, `PLATFORM_render_gfx_window`,
`PLATFORM_render_sprite`, `PLATFORM_put_char_in__typer`,
`PLATFORM_initialize_audio`, `PLATFORM_play_audio_effect`,
`PLATFORM_poll_audio_effects`, `PLATFORM_play_audio__stream`,
`PLATFORM_release_texture`, `PLATFORM_release_gfx_window`,
`PLATFORM_release_sprite`, `PLATFORM_release_all__sprites`,
`PLATFORM_initialize_file_system_context`,
`PLATFORM_append_base_directory_to__path`,
`PLATFORM_release_serialization_request`, `PLATFORM_close_file`,
`PLATFORM_closedir`, `PLATFORM_poll_input`, `PLATFORM_tcp_end`

### Null-returning Stubs

| Function | Return |
|----------|--------|
| `PLATFORM_allocate_gfx_window` | `NULL` |
| `PLATFORM_allocate_audio_effect` | `NULL` |
| `PLATFORM_allocate_sprite` | `NULL` |
| `PLATFORM_opendir` | `NULL` |
| `PLATFORM_allocate_serialization_request` | `NULL` |
| `PLATFORM_tcp_begin` | `NULL` |
| `PLATFORM_tcp_connect` | `NULL` |
| `PLATFORM_tcp_server` | `NULL` |
| `PLATFORM_tcp_poll_accept` | `NULL` |

### False/Zero-returning Stubs

| Function | Return |
|----------|--------|
| `PLATFORM_allocate_texture` | `false` |
| `PLATFORM_allocate_texture_with__path` | `false` |
| `PLATFORM_is_audio__streaming` | `false` |
| `PLATFORM_mkdir` | `false` |
| `PLATFORM_tcp_close_socket` | `false` |
| `PLATFORM_set_position_in__file` | `false` |
| `PLATFORM_get_base_directory` | `0` |
| `PLATFORM_get_directories` | `0` |
| `PLATFORM_access` | `0` |
| `PLATFORM_get_quantity_of__active_serialization_requests` | `0` |
| `PLATFORM_tcp_recieve` | `0` |

### Error-returning Stubs

| Function | Return |
|----------|--------|
| `PLATFORM_open_file` | `PLATFORM_Open_File_Error__Unknown` |
| `PLATFORM_write_file` | `PLATFORM_Write_File_Error__Unknown` |
| `PLATFORM_read_file` | `PLATFORM_Read_File_Error__Unknown` |
| `PLATFORM_get_position_in__file` | `-1` (cast to `Index__u32`) |
| `PLATFORM_tcp_send` | `-1` |
| `PLATFORM_tcp_poll_connect` | `TCP_Socket_State__Unknown` |
