# PLATFORM_append_base_directory_to__path

- **Function name:** `PLATFORM_append_base_directory_to__path`
- **File of origin:** `core/include/platform.h` (line 291). Reference implementations: `sdl/source/serialization/sdl_filesystem.c:55` and `no_gui/source/serialization/no_gui_filesystem.c:232` (byte-identical). Platform stubs: `nds/source/serialization/nds_filesystem.c:150` (empty body), `tests/core/source/PLATFORM.c:355` (empty body).

## Semantic

Appends the file-system context's base directory string into a caller-provided path buffer at the offset `*p_index_of__path_end`, then advances `*p_index_of__path_end` by the base directory's length. When the buffer is built from offset 0, the base directory becomes the leading component of the assembled path.

## Pre-conditions

1. `p_PLATFORM_file_system_context` is non-null and initialized: `path_to__base_directory` is a null-terminated `IO_path` and `size_of__path_to__base_directory` holds its `strnlen` length (set during `PLATFORM_initialize_file_system_context`).
2. `p_c_str_path` points to a writable buffer of at least `MAX_LENGTH_OF__IO_PATH` bytes (an `IO_path`).
3. `p_index_of__path_end` is non-null.
4. `*p_index_of__path_end` is a valid offset into `p_c_str_path` (i.e. `< MAX_LENGTH_OF__IO_PATH`) representing the current end of meaningful content in the buffer.

## Post-conditions

1. The base directory string is copied into `p_c_str_path` starting at the original `*p_index_of__path_end`.
2. `*p_index_of__path_end` is advanced by `size_of__path_to__base_directory`.
3. The copied base directory is null-terminated within the buffer (provided by `strncpy`'s zero-padding).

## Correctness Verdict

Incorrect

## Semantic Alignment

The implementation fulfills the intended operation: it writes the base directory into the path buffer at the given offset and advances the offset, so the base directory becomes the leading path component when callers start at offset 0 (as they all do today). **Note:** `agents/platform_api.md` describes the behavior as "Prepends" while the function name says "append"; these are consistent given callers start at offset 0 (the base directory ends up as the path prefix), but the wording is imprecise.

## Implementation Correctness

**Defect — `strncpy` count does not account for the write offset (latent out-of-bounds write).**

The copy is performed as:

```c
strncpy(&p_c_str_path[*p_index_of__path_end],
        p_PLATFORM_file_system_context->path_to__base_directory,
        MAX_LENGTH_OF__IO_PATH);
```

The destination buffer `p_c_str_path` is assumed to be `MAX_LENGTH_OF__IO_PATH` bytes, but the write begins at offset `*p_index_of__path_end`. The bytes available from the write position to the end of the buffer are `MAX_LENGTH_OF__IO_PATH - *p_index_of__path_end`, yet the call passes the full `MAX_LENGTH_OF__IO_PATH` as the limit — overstating the available space by `*p_index_of__path_end`.

When `*p_index_of__path_end > 0`, `strncpy` can write up to `MAX_LENGTH_OF__IO_PATH` bytes starting at that offset, writing past the end of the buffer by up to `*p_index_of__path_end` bytes. This is an out-of-bounds write. All current call sites (`core/source/serialization/game_directory.c:12`, `core/source/world/serialization/world_directory.c:82,137,336`) pass offset 0, so the overflow is not currently triggered, but the implementation is incorrect for the general case its parameter contract implies.

This contradicts the codebase's own `append_path` helper (`core/source/serialization/game_directory.c:42`), which bounds the copy correctly: `strncpy(&p_path[length_of__path+1], p_appended_path, MAX_LENGTH_OF__IO_PATH - length_of__path - 1)`.

- **Type compatibility:** No issues. `MAX_LENGTH_OF__IO_PATH` (integer constant) widens to `size_t` for `strncpy`; `Index__u32` and `Quantity__u32` are both `typedef uint32_t`. Index arithmetic is sound.
- **Undefined behavior:** Out-of-bounds write when `*p_index_of__path_end > 0` (see above). No null dereference; no type punning; no pointer arithmetic beyond the buffer.
- **Validation:** None performed — consistent with the function's low-level role; validation is the caller's responsibility.
- The NDS stub (`nds_filesystem.c:150`) and test stub (`tests/core/source/PLATFORM.c:355`) are empty bodies: they leave `p_c_str_path` and `*p_index_of__path_end` untouched. On those platforms the base directory is therefore never written and the offset is never advanced, which will break callers that rely on the base directory being present. This is a separate platform-correctness gap outside the SDL/no_gui reference implementation.

## Side Effects

- Writes the base directory plus `strncpy` null-padding into `p_c_str_path` beginning at the original `*p_index_of__path_end`. The zero-padding effectively zeroes the buffer from the end of the copied base directory up to `*p_index_of__path_end + MAX_LENGTH_OF__IO_PATH` (when the offset is 0, the entire buffer beyond the base directory is zeroed). Bytes before the write offset are left untouched.
- Mutates `*p_index_of__path_end`, adding `size_of__path_to__base_directory`.
- Does not allocate resources, perform I/O, or modify `p_PLATFORM_file_system_context`.
