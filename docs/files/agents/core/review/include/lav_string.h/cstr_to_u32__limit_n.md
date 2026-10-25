cstr_to_u32__limit_n — core/source/lav_string.c, lines 48-70

Converts a C-string to a u32 (unsigned 32-bit integer), parsing at most `limit_n` characters and stopping at the null terminator.

Pre-conditions:
1. p_cstr must be a non-null pointer to a null-terminated C-string containing only decimal digit characters ('0'–'9'). If any character in the scanned range is not a digit, the function returns false.
2. limit_n must be a non-negative i32 specifying the maximum number of characters to scan. If limit_n is negative, the signed-to-unsigned conversion in the loop condition causes undefined behavior (the negative value is promoted to a very large uint32_t, potentially causing out-of-bounds memory access).
3. p_OUT_u32 must be a non-null pointer to a writable u32 destination. The function does not validate this pointer before writing to it.
4. The numeric value represented by the digit string must fit within INT32_MAX (2,147,483,647). Values up to UINT32_MAX (4,294,967,295) cannot be correctly parsed because the intermediate `value` variable is declared as i32 (signed), causing signed integer overflow (undefined behavior in C) when the value exceeds INT32_MAX.

Post-conditions:
1. On success (return true): *p_OUT_u32 is set to the parsed unsigned integer value.
2. On failure (return false): *p_OUT_u32 is left unmodified (the function returns false before writing). The caller cannot rely on the value of *p_OUT_u32 in this case.

Correctness Verdict: Incorrect

Semantic Alignment:
The function's intent is to convert a C-string of decimal digits into a u32 value. The parsing logic (subtracting '0', checking range 0–9, accumulating value *= 10 + char_value) is semantically correct for the core conversion. However, the implementation fails to fulfill this intent due to several bugs:
- The loop variable `index_towards__limit_n` is typed as `Index__u32` (uint32_t), while `limit_n` is `i32` (int32_t). This signed/unsigned mismatch means that if a caller passes a negative `limit_n` (which is a valid i32 value), the comparison `index_towards__limit_n < limit_n` promotes `limit_n` to uint32_t, turning a small negative number into a very large positive number. This causes the loop to potentially scan far beyond the string's bounds, leading to out-of-bounds memory access.
- The intermediate `value` is `i32` (signed) rather than `u32` (unsigned), which means the function cannot correctly parse values in the range [INT32_MAX + 1, UINT32_MAX]. For such values, signed integer overflow occurs (undefined behavior in C).

Implementation Correctness:
- Type compatibility: The loop variable `Index__u32` (uint32_t) is compared against `limit_n` (i32/int32_t), creating a signed/unsigned comparison. This is a type mismatch that causes incorrect behavior when limit_n is negative. The intermediate `value` is `i32` but is assigned to `*p_OUT_u32` which is `u32`, creating another type mismatch — the i32 type limits the representable range and causes undefined behavior on overflow.
- Undefined behavior:
  1. Signed/unsigned comparison: Comparing `Index__u32` with `i32` is implementation-defined behavior per the C standard; in practice, the i32 is converted to u32, which produces incorrect results for negative limit_n.
  2. Signed integer overflow: `value *= 10` and `value += char_value` operate on an `i32`. If the parsed value exceeds INT32_MAX, signed overflow occurs, which is undefined behavior in C.
  3. Out-of-bounds access: If limit_n is negative (converted to large unsigned), the loop may access p_cstr beyond the null terminator, reading arbitrary memory.
- Validation: The function performs no null pointer validation on p_cstr or p_OUT_u32, despite dereferencing both. It also does not validate that limit_n is non-negative. For a low-level string parsing utility, some validation (at minimum null checks) would be appropriate, or at minimum the function should be documented as requiring non-null pointers and non-negative limit_n.

Side Effects:
1. Writes the parsed value to *p_OUT_u32 on success. On failure (non-digit character encountered), *p_OUT_u32 is not written.
2. Reads memory through p_cstr up to limit_n characters or until the null terminator, whichever comes first.
