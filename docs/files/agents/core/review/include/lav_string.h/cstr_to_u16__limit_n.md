cstr_to_u16__limit_n — core/include/lav_string.h

Parses a C-string to a u16 value, bounded by a character limit, delegating to cstr_to_u32__limit_n.

Pre-conditions:
1. p_cstr must be a non-null pointer to a NUL-terminated C-string containing only digit characters (0-9) within the first limit_n characters.
2. limit_n must be a non-negative i32 specifying the maximum number of characters to parse.
3. p_OUT_u16 must be a non-null pointer to a writable u16.

Post-conditions:
1. On success (return true): *p_OUT_u16 is set to the parsed u16 value.
2. On failure (return false): *p_OUT_u16 is not modified.
3. The function returns a bool indicating whether parsing succeeded.

Correctness Verdict: Incorrect

Semantic Alignment:
The function's intent is to parse a string of digits into a u16 value and report success or failure. The implementation does NOT fulfill this semantic intent. The critical bug is on the line:

    value = (u16)cstr_to_u32__limit_n(p_cstr, limit_n, &value);

The return value of cstr_to_u32__limit_n is a bool (0 or 1). Casting it to u16 yields 0 or 1, and assigning it back to the u32 variable value OVERWRITES the parsed numeric value that cstr_to_u32__limit_n stored via the &value out-parameter. After this assignment, value holds 0 or 1 (the boolean result), not the parsed number.

Subsequently, bool result = (value != 0) merely checks whether the callee returned true, and *p_OUT_u16 = (u16)value sets the output to 1, never the actual parsed value. As a result, the function always outputs 1 on success regardless of the actual numeric content of the string, making it completely non-functional for its intended purpose.

The correct implementation should capture the bool return value separately and only assign the output from value (which holds the parsed result):

    u32 value = 0;
    bool result = cstr_to_u32__limit_n(p_cstr, limit_n, &value);
    if (result)
        *p_OUT_u16 = (u16)value;
    return result;

Implementation Correctness:
Type compatibility — The return value of cstr_to_u32__limit_n is bool, but it is cast to u16 and assigned to a u32 variable. This is an implicit narrowing conversion (bool to u16) that loses the semantic meaning of the return value and corrupts the parsed data. The parameter types (const char *, i32, u16 *) are otherwise correct.
Undefined behavior — No null dereference, no pointer arithmetic, no out-of-bounds access. However, the logic is fundamentally broken: the parsed value is destroyed by overwriting value with the boolean return.
Validation — No validation of p_cstr or p_OUT_u16 for null is performed. This is consistent with the pattern used by the sibling functions and the codebase's convention that callers are responsible for passing valid pointers. The callee cstr_to_u32__limit_n does validate that characters are digits (returning false on non-digit characters).

Note: The same bug pattern exists in all four sibling wrapper functions (cstr_to_i16__limit_n, cstr_to_i8__limit_n, cstr_to_u8__limit_n), but this review covers only cstr_to_u16__limit_n.

Side Effects:
No side effects — the function does not modify any global or shared state. Its only observable effects are writing to *p_OUT_u16 (on success) and returning a bool. However, due to the bug, the value written to *p_OUT_u16 is always 1 on success, not the correctly parsed value.
