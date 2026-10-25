cstr_to_i32__limit_n — core/source/lav_string.c

Parses a null-terminated C string into a signed 32-bit integer, limited to at most `limit_n` characters, with optional leading sign characters ('+' or '-').

Pre-conditions:
1. p_cstr must be a non-null pointer to a valid null-terminated C string.
2. limit_n must be >= 0. Negative values cause both loops to be skipped, returning true with value 0 (a bug; see Implementation Correctness).
3. p_OUT_i32 must be a non-null pointer to a writable i32.
4. The string may be empty, contain only sign characters, or contain non-digit characters after sign characters — the function is expected to handle these gracefully by returning false.

Post-conditions:
1. On success (return true): *p_OUT_i32 is set to the parsed signed integer value.
2. On failure (return false): *p_OUT_i32 is not written (remains at its prior value); the function returns early without mutating the output.
3. The function does not modify p_cstr (it is const).

Correctness Verdict: Incorrect

Semantic Alignment:
The function's intent is to parse a C string into an i32, respecting a character limit and handling optional leading signs. However, the implementation has two critical bugs that cause it to deviate from this semantic intent:

1. **Missing null-terminator check in the digit-parsing loop**: The second loop (the "get_numeric" loop) only checks `index_towards__limit_n < limit_n` but does NOT check for the null terminator `p_cstr[index_towards__limit_n]`. Compare with the sibling function `cstr_to_u32__limit_n` (lines 48-70), which correctly includes `&& p_cstr[index_towards__limit_n]` in its single loop condition. This omission means:
   - If `limit_n` exceeds the string length, the loop reads past the null terminator (undefined behavior). In practice, the null character `'\0'` produces `char_value = '\0' - '0' = -48`, which fails the `char_value < 0` check and causes the function to return false — even though the preceding characters formed a valid number.
   - Example: parsing "5" with `limit_n = 5` returns false, despite "5" being a valid integer.

2. **No digit-count tracking — sign-only and empty strings return true with value 0**: The variable `value` is initialized to 0 and is only modified inside the second loop. If no digits are parsed (e.g., the string is "-" with `limit_n = 1`, or "" with `limit_n = 0`), `value` remains 0, `is_negative` may be true (but `-0 == 0`), and the function returns true with `*p_OUT_i32 = 0`. This is semantically incorrect — a string with no digits should not parse successfully.

Implementation Correctness:
- **Type compatibility**: All parameter types match exactly (const char*, i32, i32*). The local variable `index_towards__limit_n` is `i32`, matching `limit_n` (also `i32`). No implicit conversions or truncation.
- **Undefined behavior — out-of-bounds read (Critical)**: The second loop lacks a null-terminator check. When `limit_n` is greater than the actual string length, `p_cstr[index_towards__limit_n]` reads memory beyond the null terminator. While the null character itself typically causes the digit check to fail (returning false), this is still undefined behavior per the C standard, as reading past the null terminator of a string is not guaranteed to be safe. In adversarial conditions (e.g., `limit_n` set to a very large value), this could read far into unallocated memory.
- **Undefined behavior — sign-only string returns success (Moderate)**: When the input is a sign-only string (e.g., "-") and `limit_n` equals the string length, the second loop body never executes, `value` stays 0, and the function returns true. This is not UB per se, but it is a logic error that violates the function's semantic contract.
- **Validation**: No null-pointer validation is performed on `p_cstr` or `p_OUT_i32`. This is acceptable as a pre-condition for a low-level utility function, consistent with the engine's pattern (see `cstr_to_u32__limit_n` which also does not validate).
- **Sign toggling behavior (Minor)**: Each '-' character toggles `is_negative`, so "--5" is treated as +5. While unusual, this is a design choice rather than a bug. The '+' character resets `is_negative` to false.

Side Effects:
- Writes the parsed integer to *p_OUT_i32 on success.
- Reads from p_cstr (does not modify it).
- No other side effects (no I/O, no global state mutation, no memory allocation).

Notes on Callers:
- The inline wrappers `cstr_to_i16__limit_n` and `cstr_to_i8__limit_n` in lav_string.h (lines 16-34) have a separate bug: they assign the bool return value of `cstr_to_i32__limit_n` to `value` via `value = (i16)cstr_to_i32__limit_n(...)`, overwriting the parsed value that was written through the `&value` output parameter. This is a caller bug, not a bug in `cstr_to_i32__limit_n` itself, but it renders the wrappers non-functional.
