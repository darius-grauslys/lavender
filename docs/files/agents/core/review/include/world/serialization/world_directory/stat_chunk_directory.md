# stat_chunk_directory

**File of origin:** `core/source/world/serialization/world_directory.c`

## Semantic

Constructs a filesystem path for a chunk directory based on the world name, region vector, and chunk vector. The function creates any missing directories along the path (save directory, world directory, region directory, recursive quadtree subdirectories, and leaf chunk directory). It returns the index of the end of the constructed path in the buffer, or 0 on failure.

## Pre-conditions

1. `p_PLATFORM_file_system_context` must be a valid, initialized `PLATFORM_File_System_Context` pointer (non-null).
2. `p_world` must be a valid `World` pointer (non-null), with `p_world->name` being a valid `World_Name_String` (char[32]) and `p_world->length_of__world_name` accurately reflecting the length of the world name.
3. `p_global_space` must be a valid `Global_Space` pointer (non-null), with `p_global_space->chunk_vector__3i32` containing valid chunk coordinates.
4. `buffer` must point to a writable buffer of at least `MAX_LENGTH_OF__IO_PATH` (128) bytes. The buffer contents before the call are overwritten starting from index 0.
5. The buffer is not assumed to be pre-initialized; `PLATFORM_append_base_directory_to__path` and `append_path` use `strnlen` to find the current string length, so the buffer must be zero-initialized or contain a valid null-terminated string at the start.

## Post-conditions

1. On success (non-zero return): The `buffer` contains a null-terminated path string of the form `<base_directory>/save/<world_name>/r_<region_x>_<region_y>_<region_z>/c_<qx>_<qy>_<qz>/.../c_<chunk_x>_<chunk_y>_<chunk_z>`, where intermediate directories are created as needed. The return value is the index of the end of the path (not including any null terminator).
2. On failure (return 0): An error has been logged via `debug_error`, and the buffer contents are indeterminate. No guarantee is made about which directories were created.
3. All directories in the path are created if they do not exist (via `PLATFORM_mkdir` with mode 0777). Existing directories are opened and closed (via `PLATFORM_opendir`/`PLATFORM_closedir`) without modification.
4. The buffer is **not** null-terminated after the function returns. The caller is responsible for null-terminating if needed. (The buffer is null-terminated at intermediate points due to `strncpy` padding, but the final return leaves the path without a null terminator at `index_of__path_append`.)

## Correctness Verdict

**Incorrect**

## Semantic Alignment

The function's intent is to construct a chunk directory path and ensure all parent directories exist. The implementation partially fulfills this intent but has several issues:

1. **Missing bounds check (line 149-150):** The function has a TODO comment where a bounds check should be performed before the `strncpy` of the world name into the buffer. The sibling function `stat_world_directory` (in the same file) implements this check:
   ```c
   if (index_of__path_append + WORLD_NAME_MAX_SIZE_OF
           >= MAX_LENGTH_OF__IO_PATH) {
       debug_error("stat_world_directory, path too long.");
       return 0;
   }
   ```
   `stat_chunk_directory` omits this check, creating a buffer overflow vulnerability if the base directory path plus the world name exceeds `MAX_LENGTH_OF__IO_PATH` (128 bytes).

2. **Type mismatch in `append_u32_as__hex_to__path` calls:** The function `append_u32_as__hex_to__path` declares its `value` parameter as `u32` (unsigned), but is called with `i32` (signed) values from `Region_Vector__3i32` and `Chunk_Vector__3i32` fields. While the bit pattern is preserved through implicit signed-to-unsigned conversion, negative coordinates will produce two's complement hex representations (e.g., -1 becomes "ffffffff" for 8-digit or "ff" for 2-digit), which may not be the intended semantic for directory naming. This is inconsistent with the function's name suggesting it handles unsigned values.

3. **Incomplete z-axis recursion (line 297):** The TODO comment `//TODO: recur by Z-axis` indicates the z-axis is not included in the recursive quadtree-like directory subdivision. The `chunk_vector_descend__3i32.z__i32` remains at 127 throughout all 6 recursion levels, and `chunk_vector_quad__3i32.z__i32` is never halved (only x and y are shifted right by 1 each iteration). This means the z-coordinate is only encoded in the final leaf directory name, not in the intermediate recursive directory structure.

4. **Inconsistent z-axis masking:** `chunk_vector__3i32.x__i32` and `y__i32` are masked with `MASK(8)` (0xFF) at lines 205-206, but `z__i32` is not. While `append_u32_as__hex_to__path` with `beginning_index = 2` effectively truncates to 8 bits for the leaf directory, the lack of masking is inconsistent and could cause confusion.

## Implementation Correctness

1. **Type compatibility:** The `append_u32_as__hex_to__path` function expects `u32` (unsigned) values, but is called with `i32` (signed) values throughout. This is an implicit signed-to-unsigned conversion. While not undefined behavior, it can produce semantically incorrect results for negative coordinates (two's complement hex instead of signed representation). This is a type compatibility issue.

2. **Buffer overflow risk:** The missing bounds check before `strncpy` of the world name (line 149-150) is a real buffer overflow vulnerability. If `PLATFORM_append_base_directory_to__path` writes a long base directory path, the subsequent `strncpy` of `WORLD_NAME_MAX_SIZE_OF` (32) bytes could exceed `MAX_LENGTH_OF__IO_PATH` (128) bytes. The `stat_world_directory` function in the same file correctly guards against this.

3. **No null terminator guarantee:** The function does not explicitly null-terminate the buffer at `index_of__path_append` before calling `PLATFORM_opendir` or `PLATFORM_mkdir`. However, `strncpy` with `WORLD_NAME_MAX_SIZE_OF` padding ensures null termination after the world name copy (as long as `length_of__world_name < WORLD_NAME_MAX_SIZE_OF`). For the region and chunk directory names, the buffer is null-terminated by the previous `strncpy` padding or by the `append_u32_as__hex_to__path` function's output (which doesn't add a null terminator). This is a potential issue but is mitigated by the `strncpy` padding.

4. **Loop bounds:** The recursive descent loop runs exactly 6 times (`level_of__recursion < 6`), which is correct for the intended quadtree subdivision depth. The `chunk_vector_quad__3i32` values start at 128 and are halved each iteration (128, 64, 32, 16, 8, 4), providing 6 levels of binary subdivision.

5. **Validation responsibility:** The function does not validate that `p_world->length_of__world_name` is within bounds (<= `WORLD_NAME_MAX_SIZE_OF`). This is the caller's responsibility, consistent with the engine's pattern of trusting internal data structures.

## Side Effects

1. **Filesystem mutation:** Creates directories via `PLATFORM_mkdir` if they do not exist. Opens and closes existing directories via `PLATFORM_opendir`/`PLATFORM_closedir`.
2. **Buffer mutation:** Writes the constructed path into `buffer`, overwriting any existing content. The buffer is used as both input (for `strnlen` in `append_path`) and output.
3. **No global state mutation:** The function does not modify `p_world`, `p_global_space`, or `p_PLATFORM_file_system_context`.
4. **No logging side effects:** On failure, `debug_error` is called to log an error message.
