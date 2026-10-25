strnlen — core/include/platform.h

Returns the length of the null-terminated string `s`, not including the null terminator, but at most `maxlen`. That is, it returns `min(strlen(s), maxlen)`. Unlike `strlen`, it never reads beyond `maxlen` bytes.

Pre-conditions:
1. `s` must be a non-null pointer to a readable, null-terminated character array; passing NULL is undefined behavior per ISO C (C99 and later).
2. `s` must point to at least `maxlen` readable bytes of memory, because `strnlen` may scan up to `maxlen` bytes searching for a null terminator. It is safe to call on a buffer that contains no null terminator within `maxlen` bytes — in that case it returns `maxlen` without reading further.

Post-conditions:
1. Returns `min(strlen(s), maxlen)`.
2. If a null terminator exists within the first `maxlen` bytes of `s`, the return value is the offset of that null terminator (i.e., `strlen(s)`), and no byte beyond the terminator is read.
3. If no null terminator exists within the first `maxlen` bytes, the return value is `maxlen` and exactly `maxlen` bytes were read.
4. The contents of `s` are not modified; the pointer is not advanced or stored.

Correctness Verdict: Correct

Semantic Alignment:
The declaration `size_t strnlen(const char *, size_t)` precisely matches the ISO C standard signature (C99 through C23). There is no Lavender-specific implementation — the header re-declares the system libc function as part of the platform abstraction layer (see surrounding declarations at lines 168-177: free, malloc, memcpy, memset, abs, srand, rand, strncmp, strncpy). As documented in `agents/platform_api.md` (line 292), this stdlib re-declaration block exists for static-linking scenarios (e.g., NDS) where standard libc functions must be resolved locally. No divergence from standard semantics exists in any Lavender source; `strnlen` is only ever invoked, never defined, by Lavender code.

Implementation Correctness:
- Type compatibility: Parameter and return types match the C standard exactly — `size_t` return value, `const char *` for `s`, `size_t` for `maxlen`. No implicit conversions or truncation.
- Undefined behavior: The declaration introduces no undefined behavior itself. The only UB risk is at call sites that pass a NULL `s` or a buffer with fewer than `maxlen` readable bytes. The function bounds its reads to `maxlen` bytes, so it is safe on non-terminated buffers (unlike `strlen`). All known call sites pass a defined maximum length and a valid buffer: `sdl/source/serialization/sdl_filesystem.c:16` (`strnlen(path, MAX_LENGTH_OF__IO_PATH)`), `no_gui/source/serialization/no_gui_filesystem.c:17` (same), `core/source/serialization/game_directory.c:37` (`strnlen(p_path, MAX_LENGTH_OF__IO_PATH)`), `core/source/world/world.c:57,338` (`strnlen(p_world->name, WORLD_NAME_MAX_SIZE_OF)`), and `core/source/rendering/aliased_texture.c:23` (`strnlen(c_str, MAX_LENGTH_OF__TEXTURE_NAME)`).
- Validation: No validation is needed — this is a standard library function re-declared for platform abstraction (not a `PLATFORM_*` function implemented by a backend). Caller responsibility governs pointer validity and buffer sizing, consistent with how the surrounding stdlib re-declarations are treated.

Side Effects:
No side effects. The function is a pure read: it scans at most `maxlen` bytes of the input string for a null terminator and returns a `size_t` result. It does not modify the input buffer, allocate, free, or alter any global state. (The declaration itself has no side effects.)
