# stat_game_data_file

**File of origin:** `core/source/serialization/game_directory.c`

## Semantic

Constructs a filesystem path by appending the base directory, a path separator, and the literal "game_data" subdirectory name into the provided buffer. Then checks whether the resulting path exists on disk via `access(buffer, F_OK)`. Returns the total length of the constructed path if the file/directory exists, or `false` (0) if it does not exist.

## Pre-conditions

1. `p_game` must be non-null. It is dereferenced via `get_p_PLATFORM_file_system_context_from__game(p_game)`, which directly accesses `p_game->p_PLATFORM_file_system_context` with no null guard.
2. `buffer` must be non-null and point to a writable region of at least `MAX_LENGTH_OF__IO_PATH` (128) bytes.
3. The base directory path written by `PLATFORM_append_base_directory_to__path` must not fill the buffer to or beyond `MAX_LENGTH_OF__IO_PATH - 1` bytes, otherwise the subsequent `buffer[index_of__path_append++] = '/'` write will overflow the buffer. This is an implicit pre-condition that is not validated by the function.

## Post-conditions

1. `buffer` contains the constructed path: `<base_directory>/game_data` (null-terminated by `strncpy_returns__strlen`).
2. If the path exists on disk: returns `index_of__path_append`, the total length of the path string (excluding the null terminator).
3. If the path does not exist: returns `false` (which evaluates to `0` as `Index__u32`).

## Correctness Verdict

**Incorrect**

## Semantic Alignment

The implementation does not fully fulfill the semantic intent. The function is intended to "stat" (check the existence of) a game data file/directory, but it suffers from a critical buffer overflow vulnerability. After `PLATFORM_append_base_directory_to__path` populates the buffer and updates `index_of__path_append`, the code unconditionally writes `buffer[index_of__path_append++] = '/'` without verifying that `index_of__path_append` is still within the bounds of `MAX_LENGTH_OF__IO_PATH`. If the base directory path already occupies the full buffer (or all but the last byte), this write goes out of bounds.

Additionally, the subsequent `strncpy_returns__strlen` call uses `MAX_LENGTH_OF__IO_PATH - index_of__path_append` as the max copy length. If `index_of__path_append` has already reached or exceeded `MAX_LENGTH_OF__IO_PATH` (due to the unchecked `/` write), this subtraction underflows because both operands are unsigned, resulting in a very large value being passed as `max_length`, which would cause `strncpy` to write far beyond the buffer boundary.

The return value semantics are also questionable: the function returns `Index__u32` (uint32_t) but uses `false` (which is `0` in C) as a sentinel for "file not found." While technically valid since `false` implicitly converts to `0`, this conflates boolean and integer semantics. A return value of `0` is indistinguishable from a valid path of length 0, though in practice a path of length 0 is not meaningful here.

## Implementation Correctness

1. **Type compatibility**: Parameters are compatible with their usage. `strncpy_returns__strlen` returns `Index__u32` which is added to `index_of__path_append` (also `Index__u32`), which is fine. The `false` return value implicitly converts to `0` as `Index__u32`, which is valid but semantically imprecise.

2. **Undefined behavior / buffer overflow**: The primary issue is the unchecked write at `buffer[index_of__path_append++] = '/'`. There is no bounds check before this write. If `PLATFORM_append_base_directory_to__path` fills the buffer to capacity, this write is out of bounds. Furthermore, the `MAX_LENGTH_OF__IO_PATH - index_of__path_append` expression in the `strncpy_returns__strlen` call is vulnerable to unsigned integer underflow if `index_of__path_append >= MAX_LENGTH_OF__IO_PATH`.

3. **Validation**: The function performs no validation of its parameters (`p_game`, `buffer`) or intermediate state (buffer capacity). It relies entirely on the caller to ensure correct usage. For a function that writes to a caller-provided buffer, some form of bounds checking or assertion would be appropriate, especially given the buffer-based path construction pattern.

4. **Resource management**: No dynamic resource allocation or deallocation occurs. The `access()` call is a read-only filesystem check with no side effects on the filesystem.

## Side Effects

1. **Buffer mutation**: The function writes the constructed path string into `buffer`, overwriting any prior contents.
2. **No filesystem side effects**: The `access()` call is a non-mutating check; it does not create, modify, or delete files.
3. **No global state changes**: The function does not modify any global or static state.
