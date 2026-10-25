append_path — core/source/serialization/game_directory.c

Appends a path component (p_appended_path) to an existing path buffer (p_path),
inserting a platform path separator between them.

Pre-conditions:
1. p_path must be a non-null pointer to a writable IO_path buffer (char[MAX_LENGTH_OF__IO_PATH], i.e. 1024 bytes).
2. p_path must be a null-terminated C string (or have no null terminator within the first MAX_LENGTH_OF__IO_PATH bytes, in which case the function is a no-op).
3. p_appended_path must be a non-null pointer to a null-terminated C string.
4. p_appended_path may be empty (zero-length string), in which case the path should remain unchanged.
5. p_path may be empty (zero-length string), in which case the result should be just p_appended_path.

Post-conditions:
1. p_path is mutated in-place to contain the concatenation of the original p_path, a PATH_SEPERATOR, and p_appended_path.
2. p_path remains null-terminated after the call.
3. p_path does not exceed MAX_LENGTH_OF__IO_PATH bytes (including null terminator).
4. If p_path was already at MAX_LENGTH_OF__IO_PATH (no null terminator found), the function returns without modifying p_path.

Correctness Verdict: Incorrect

Semantic Alignment:
The implementation does not fulfill the semantic intent as specified by the test suite
(tests/core/source/serialization/test_suite_serialization_game_directory.c). The tests
expect the following behaviors, all of which the current implementation violates:

- Test game_directory__append_path_concatenates: base="/home/user", suffix="/saves"
  expects "/home/user/saves" but the implementation produces "/home/user//saves"
  (double separator). The function unconditionally writes PATH_SEPERATOR at
  p_path[length_of__path] and then copies p_appended_path verbatim via strncpy,
  which includes the leading '/' of "/saves", resulting in a double separator.

- Test game_directory__append_path_empty_suffix: base="/home/user", suffix=""
  expects "/home/user" (unchanged) but the implementation writes a trailing
  PATH_SEPERATOR, producing "/home/user/". The function does not check for an
  empty suffix before inserting the separator.

- Test game_directory__append_path_empty_base: base="", suffix="/saves"
  expects "/saves" but the implementation writes a leading PATH_SEPERATOR at
  p_path[0], producing "//saves". The function does not special-case an empty
  base path.

Additionally, the implementation has a latent null-termination bug: strncpy does
not guarantee null-termination when the source string length is greater than or
equal to the count parameter (MAX_LENGTH_OF__IO_PATH - length_of__path - 1). If
p_appended_path is sufficiently long to fill the remaining buffer space, the
resulting p_path will not be null-terminated, leading to undefined behavior when
p_path is later used as a C string.

Implementation Correctness:
Type compatibility — parameter types match the IO_path typedef (char array)
correctly. Index__u32 (uint32_t) is used for the length, which is compatible.
No implicit conversions or truncation issues.

Undefined behavior:
- No null-termination guarantee after strncpy when p_appended_path is long
  enough to fill the remaining buffer. This is the most severe issue: a
  non-null-terminated p_path will cause undefined behavior in any subsequent
  strnlen, strlen, or string comparison on p_path.
- No buffer overflow occurs — the bounds check (length_of__path >=
  MAX_LENGTH_OF__IO_PATH) and the strncpy count (MAX_LENGTH_OF__IO_PATH -
  length_of__path - 1) correctly prevent writes beyond the buffer. However,
  the missing null terminator means the buffer content is not a valid C string.

Validation:
The function performs a basic bounds check (early return if path is already
at max length), which is appropriate. However, it lacks validation for the
empty-suffix and empty-base edge cases that the tests require. The function
also lacks an explicit null-termination step after strncpy.

Side Effects:
- Mutates p_path in-place: inserts a PATH_SEPERATOR and copies p_appended_path
  into the buffer starting after the separator.
- Does not modify p_appended_path.
- No other side effects (no I/O, no global state changes, no memory allocation).
