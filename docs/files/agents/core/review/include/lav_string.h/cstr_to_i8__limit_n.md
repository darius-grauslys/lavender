cstr_to_i8__limit_n — core/include/lav_string.h, lines 32-46

Converts a null-terminated C string to an i8 value, parsing at most limit_n characters.

Pre-conditions:
1. p_cstr must be a non-null pointer to a valid null-terminated C string.
2. limit_n must be a non-negative integer specifying the maximum number of characters to parse.
3. p_OUT_i8 must be a non-null pointer to a writable i8.

Post-conditions:
1. On success, *p_OUT_i8 is set to the parsed i8 value (truncated from the i32 result).
2. Returns true if parsing succeeded, false otherwise.

Correctness Verdict: Incorrect

Semantic Alignment:
The implementation does NOT fulfill the semantic intent of converting a string to an i8. The underlying function cstr_to_i32__limit_n has the signature `bool cstr_to_i32__limit_n(const char *p_cstr, i32 limit_n, i32 *p_OUT_i32)` — it returns a bool indicating success/failure, and writes the parsed value to the output parameter. However, cstr_to_i8__limit_n incorrectly assigns the boolean return value back to the local `value` variable: `value = (i8)cstr_to_i32__limit_n(p_cstr, limit_n, &value);`. This overwrites the correctly parsed integer value with the boolean return value (0 or 1), discarding the actual parsed result. The subsequent `*p_OUT_i8 = (i8)value;` then writes the boolean (0 or 1) instead of the parsed numeric value.

Implementation Correctness:
- Type compatibility: The return type of cstr_to_i32__limit_n is `bool`, but it is cast to `i8` and assigned to an `i32` variable. This is a fundamental type mismatch — the boolean return value (success/failure indicator) is being used as the numeric result.
- Undefined behavior: No undefined behavior in terms of pointer arithmetic or out-of-bounds access, but the logic is semantically broken.
- Validation: The function delegates parsing to cstr_to_i32__limit_n, which handles validation internally. However, the result of that validation (the bool return) is mishandled.

Side Effects:
Mutates *p_OUT_i8 only on success (when result is true). On failure, *p_OUT_i8 is left unmodified.
