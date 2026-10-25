# strings — bounded parse-to-int (lav_string) and length-returning copy (core_string)

**Sources:** `core/include/lav_string.h` + `core/source/lav_string.c` + `core/include/core_string.h` + `core/source/core_string.c`

## Surface Concerns

The engine has **two distinct string modules** with different responsibilities. **lav_string** parses C-strings to integers with bounded scans; **core_string** copies bytes with length reporting. Their name overlap is coincidental — one converts text to numbers, the other copies bytes and returns the length copied. Layer: SUPPORT (unlayered leaf, used across the tree). Called from networking (`ipv4_address.c`) and serialization (`game_directory.c`).

- **lav_string: bounded parse-to-int** — converts `const char *` to `i32`/`u32` (bases, `lav_string.c`) and `i16`/`i8`/`u16`/`u8` (inline wrappers, `lav_string.h`), reading at most `limit_n` characters. Returns `bool` — `true` means the output parameter was written. The only in-tree caller of `lav_string` is `ipv4_address.c`, via the `u8`/`u16` wrappers.
- **The two bases have different NUL contracts** — `cstr_to_u32__limit_n` reads digits until NUL or `limit_n`; `cstr_to_i32__limit_n` scans a leading sign run first (`-` toggles, `+` clears) and then requires digits to fill the rest of the `limit_n` window — a NUL or non-digit inside the window returns `false`. For NUL-terminated input, `limit_n` must exactly cover the sign run and the digits.
- **No overflow detection** — no range checking; both bases accumulate in `i32` and wrap on overflow (the `u32` output is a cast of that `i32`). `limit_n` bounds the read and is the primary safety mechanism for untrusted input.
- **16/8-bit wrappers discard the parsed value** — all four wrappers pass a local to the 32-bit base, then overwrite that local with the base call's boolean return, so on success they always write `1` to the output, never the parsed number (a parsed zero reports success, not failure). `ipv4_address.c` therefore receives `1` for every octet and port; the `i16`/`i8` wrappers have no in-tree callers.
- **core_string: length-returning strncpy** — copies up to `max_length_of__copy` bytes from source to destination, stopping after a NUL (which is copied). Unlike `strncpy`, returns the number of bytes copied rather than the destination pointer. Used in `game_directory.c` for bounded string copies where the caller needs both the copy and the length.

## Public API Surface

### Key Functions

#### lav_string — parse strings to integers

- `bool cstr_to_i32__limit_n(const char *p_cstr, i32 limit_n, i32 *p_OUT_i32);` — base: optional leading sign run, then digits filling the rest of the `limit_n` window; returns `false` on a NUL or non-digit inside the window.
- `bool cstr_to_u32__limit_n(const char *p_cstr, i32 limit_n, u32 *p_OUT_u32);` — base: digits until NUL or `limit_n`; no sign handling; returns `false` on a non-digit.
- `static inline bool cstr_to_i16__limit_n(const char *p_cstr, i32 limit_n, i16 *p_OUT_i16);` / `static inline bool cstr_to_i8__limit_n(const char *p_cstr, i32 limit_n, i8 *p_OUT_i8);` — call the `i32` base, then overwrite the local with the call's boolean return; on success always write `1` to `p_OUT`.
- `static inline bool cstr_to_u16__limit_n(const char *p_cstr, i32 limit_n, u16 *p_OUT_u16);` / `static inline bool cstr_to_u8__limit_n(const char *p_cstr, i32 limit_n, u8 *p_OUT_u8);` — same, via the `u32` base.

#### core_string — length-returning strncpy

- `Index__u32 strncpy_returns__strlen(void *p_destination, const void *p_source, Quantity__u32 max_length_of__copy);` — returns the number of bytes copied (including NUL if encountered), or `max_length_of__copy` if no NUL found.

## Key Files Table

| File | Role |
|------|------|
| `core/include/lav_string.h` | Base parse declarations, `i16/u16/i8/u8` inline wrappers |
| `core/source/lav_string.c` | `cstr_to_i32__limit_n`, `cstr_to_u32__limit_n` implementations |
| `core/include/core_string.h` | `strncpy_returns__strlen` declaration |
| `core/source/core_string.c` | `strncpy_returns__strlen` implementation |
