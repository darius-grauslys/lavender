cstr_to_u8__limit_n — core/include/lav_string.h, lines 64-78

## Semantic

Parses a null-terminated C string of decimal digits into a u8 value, respecting a character limit, and writes the result through an output pointer. Returns true on success (non-zero parsed value), false on failure (invalid character or parsed value is zero).

## Pre-conditions

1. p_cstr must be a non-null pointer to a null-terminated C string containing only decimal digit characters ('0'–'9'). Null-pointer dereference will occur if p_cstr is NULL (the underlying cstr_to_u32__limit_n dereferences it in its loop condition).
2. limit_n must be a non-negative i32 specifying the maximum number of characters to parse. A negative value causes the loop comparison (unsigned Index__u32 vs signed i32) to promote limit_n to a very large unsigned value, effectively parsing until the null terminator instead of limiting the parse.
3. p_OUT_u8 must be a non-null pointer to a writable u8. Null-pointer dereference will occur if p_OUT_u8 is NULL when the function attempts to write the output.

## Post-conditions

1. If parsing succeeds and the parsed value is non-zero: *p_OUT_u8 is set to the parsed value (truncated to u8), and the function returns true.
2. If parsing fails (invalid character encountered) or the parsed value is zero: *p_OUT_u8 is left unmodified, and the function returns false.

## Correctness Verdict

Incorrect

## Semantic Alignment

The implementation does NOT fulfill its semantic intent. The function is supposed to parse a string of decimal digits into a u8 value and return that value through p_OUT_u8. However, due to a variable-reuse bug, the function always outputs 1 instead of the actual parsed value.

The root cause is on this line:

```c
value = (u8)cstr_to_u32__limit_n(
        p_cstr,
        limit_n,
        &value);
```

The function `cstr_to_u32__limit_n` returns a `bool` (true on success, false on invalid character) and writes the parsed numeric value through the `*p_OUT_u32` pointer (i.e., through `&value`). However, the return value (a `bool`, which is 0 or 1) is cast to `(u8)` and assigned back to `value`, **overwriting** the parsed numeric value that was just written through the pointer.

After this line, `value` holds 0 (parse failed) or 1 (parse succeeded) — never the actual parsed number. The subsequent check `bool result = (value != 0)` then evaluates to true whenever parsing succeeded (since value is 1), and `*p_OUT_u8 = (u8)value` always writes 1 instead of the parsed value.

For example:
- Parsing "5" produces *p_OUT_u8 = 1 (should be 5)
- Parsing "255" produces *p_OUT_u8 = 1 (should be 255)
- Parsing "0" produces *p_OUT_u8 = 1 (should return false, since parsed value is 0)

The correct implementation should capture the bool return value in a separate variable and use the parsed `value` for the output:

```c
u32 value = 0;
bool parsed = cstr_to_u32__limit_n(p_cstr, limit_n, &value);
bool result = (parsed && value != 0);
if (result)
    *p_OUT_u8 = (u8)value;
return result;
```

## Implementation Correctness

**Type compatibility:** The `(u8)` cast is applied to the `bool` return value of `cstr_to_u32__limit_n`, not to the parsed value. While `bool` is implicitly convertible to `u8`, this is the source of the semantic bug — the cast destroys the parsed value by overwriting `value` with 0 or 1.

**Undefined behavior:** No undefined behavior in the strict sense (no null dereference if pre-conditions are met, no out-of-bounds access). The unsigned/signed comparison between `Index__u32` and `i32 limit_n` in the callee is implementation-defined but not UB.

**Validation:** No input validation is performed. This is consistent with the low-level utility function pattern in this codebase (validation is the caller's responsibility). However, the lack of validation does not excuse the core logic bug.

## Side Effects

No side effects beyond writing to *p_OUT_u8 (when parsing succeeds with a non-zero value). The function does not modify p_cstr or any global state.
