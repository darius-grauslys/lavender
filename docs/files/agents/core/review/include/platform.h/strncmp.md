strncmp — core/include/platform.h, line 175

Compares at most `n` characters of two null-terminated strings (`s1` and `s2`), interpreting each byte as `unsigned char`. The comparison stops at the first differing byte, at a null terminator in either string, or after `n` bytes — whichever comes first. Returns zero if the compared portions are equal, a negative integer if `s1` is less than `s2` at the first differing position, or a positive integer if `s1` is greater.

Pre-conditions:
1. `s1` and `s2` must be non-null pointers to readable, null-terminated character arrays; passing NULL is undefined behavior per ISO C.
2. Each pointed-to array must have at least `n` readable bytes, because `strncmp` may examine up to `n` bytes searching for a differing or null character.
3. `n` is the maximum number of bytes to compare, not a required buffer size; it is safe to pass an `n` larger than the actual string lengths because comparison halts at a null terminator.
4. The memory regions pointed to by `s1` and `s2` must not overlap (standard `strncmp` does not define behavior for overlapping strings in all implementations).

Post-conditions:
1. Returns `0` when the first `n` bytes (or fewer, up to the first null terminator in either string) of `s1` and `s2` are identical.
2. Returns a negative `int` when, at the first differing byte position `i` (0 ≤ i < n), `(unsigned char)s1[i] < (unsigned char)s2[i]`.
3. Returns a positive `int` when, at the first differing byte position `i`, `(unsigned char)s1[i] > (unsigned char)s2[i]`.
4. If one string has a null terminator at position `i` and the other does not, the null terminator (0) is treated as less than any non-null byte, so `s1` (or `s2`) is "less" and a negative (or positive) result is returned.
5. Neither `s1` nor `s2` is modified; no bytes beyond the stopping point are read beyond the null terminator or beyond `n`.

Correctness Verdict: Correct

Semantic Alignment:
The declaration `int strncmp(const char *, const char *, size_t)` precisely matches the ISO C standard signature (C89 through C23). There is no Lavender-specific implementation — the header re-declares the system libc function as part of the platform abstraction layer (see surrounding declarations at lines 168-177: `free`, `malloc`, `memcpy`, `memset`, `abs`, `srand`, `rand`, `strnlen`, `strncpy`). As documented in `agents/platform_api.md` (line 292), this stdlib re-declaration block exists for static-linking scenarios (e.g., NDS) where standard libc functions must be resolved locally. No divergence from standard semantics exists in any Lavender source; `strncmp` is only ever invoked, never defined, by Lavender code.

Observed call-site semantic intent confirms standard `strncmp` usage: a prefix-equality check idiom (`!strncmp(name, ".", 1)` for "." directory entries at `sdl/source/serialization/unix/unix_filesystem.c:73` and `no_gui/source/serialization/unix/unix_filesystem.c:73`), an exact fixed-buffer comparison (`strncmp(shader->GL_shader_string, p_c_str, MAX_LENGTH_OF__SHADER_STRING) != 0` at `sdl/source/rendering/opengl/gl_shader_manager.c:115`), and command-line/test-name prefix matching (`strncmp("--", argv[arg], 2)` and `strncmp(pre, *test_name, pre_l)` in `tests/core/source/munit.c`). None of these usages diverge from standard `strncmp` semantics.

Lavender initialization ≠ RAII note: This function is not an initialization/reset function (name contains no "init", "initialize", or "reset"); the platform-abstraction/rRAII rules in the review guide do not apply. This is purely a standard-library comparison utility re-declared for platform independence.

Implementation Correctness:
- Type compatibility: All parameter and return types match the C standard exactly — `int` return, `const char *` for both strings, `size_t` for the count. No implicit conversions or truncation arise from the declaration.
- Undefined behavior: The declaration introduces no undefined behavior itself. The only UB risk is at call sites that pass a NULL pointer or a buffer with fewer than `n` readable bytes. The function bounds its reads to `n` bytes and stops at a null terminator, so it is safe on non-terminated buffers (it will not read past `n`). All known call sites pass a defined maximum length and a valid buffer.
- Validation: No validation is needed — this is a standard library function re-declared for platform abstraction, not a `PLATFORM_*` function implemented by a backend. Caller responsibility governs pointer validity and buffer sizing, consistent with how the surrounding stdlib re-declarations are treated.

Side Effects:
No side effects. The function is a pure read: it scans at most `n` bytes of each input string, compares them as `unsigned char`, and returns an `int` result. It does not modify either input buffer, advance any pointer, allocate or free memory, or alter any global state. (The declaration itself has no side effects.)
