# cstr_to_i16__limit_n

**File of origin:** `core/include/lav_string.h`

## Semantic

Parses a null-terminated string into a signed 16-bit integer (`i16`), using a length limit `limit_n` to constrain how many characters are consumed from the input string. Returns `true` if a non-zero value was successfully parsed, `false` otherwise.

## Pre-conditions

1. `p_cstr` must be a non-null pointer to a character array of at least `limit_n` characters (or null-terminated within `limit_n` characters).
2. `limit_n` must be a non-negative `i32`. A negative value would cause the loop in `cstr_to_i32__limit_n` to not execute, yielding a parsed value of 0.
3. `p_OUT_i16` must be a non-null pointer to a writable `i16`.

## Post-conditions

1. If parsing succeeds and the resulting parsed value is non-zero, `*p_OUT_i16` is set to the parsed value truncated to `i16`.
2. The function returns `true` if parsing succeeded and the parsed value was non-zero; returns `false` otherwise.

## Correctness Verdict

**Incorrect**

## Semantic Alignment

The function does **not** fulfill its semantic intent. The intent is to parse a string into an `i16` and write the result to `*p_OUT_i16`. However, due to a critical type confusion bug, the function never writes the actual parsed value to the output.

The underlying function `cstr_to_i32__limit_n` has the signature:
```c
bool cstr_to_i32__limit_n(const char *p_cstr, i32 limit_n, i32 *p_OUT_i32);
```
It returns a `bool` (success/failure) and writes the parsed `i32` value through the output pointer `&value`.

The bug occurs on this line:
```c
value = (i16)cstr_to_i32__limit_n(p_cstr, limit_n, &value);
```

Here, `cstr_to_i32__limit_n` is called with `&value` as the output parameter, so it writes the parsed integer to `value`. However, the function **also** returns a `bool`. The code then casts this `bool` return value to `(i16)` (converting `true`→1, `false`→0) and assigns it back to `value`, **overwriting** the parsed integer that was written through the pointer.

As a result:
- `value` becomes 0 (if parsing failed) or 1 (if parsing succeeded), instead of the actual parsed integer.
- `bool result = (value != 0);` then checks whether `value` is non-zero, which is effectively just checking whether parsing succeeded (since value is 0 or 1).
- `if (result) *p_OUT_i16 = (i16)value;` writes `1` to the output (if parsing succeeded), not the parsed integer value.

The function should instead capture the `bool` return value in a separate variable and use the parsed value from `&value`:
```c
bool success = cstr_to_i32__limit_n(p_cstr, limit_n, &value);
if (success)
    *p_OUT_i16 = (i16)value;
return success;
```

## Implementation Correctness

- **Type compatibility:** **Critical type mismatch.** The return type of `cstr_to_i32__limit_n` is `bool`, but the code treats it as if it were the parsed `i32` value. The cast `(i16)` applied to the `bool` return value produces 0 or 1, not the parsed integer. This is the root cause of the bug.
- **Undefined behavior:** No undefined behavior is present in terms of pointer arithmetic, null dereference, type punning, or out-of-bounds access. The pointers are used correctly (assuming pre-conditions are met).
- **Validation:** No validation is performed within this function (e.g., null checks on `p_cstr` or `p_OUT_i16`). This is consistent with the low-level nature of the function; validation is the caller's responsibility.
- **Truncation:** The cast from `i32` to `i16` in `*p_OUT_i16 = (i16)value;` is intentional and semantically appropriate for narrowing from a 32-bit to a 16-bit integer, though it silently discards the upper 16 bits.

## Side Effects

- Mutates `*p_OUT_i16` (sets it to the truncated parsed value) if parsing succeeds and the value is non-zero.
- Calls `cstr_to_i32__limit_n`, which reads from the `p_cstr` buffer but does not modify it.
- No other side effects.
