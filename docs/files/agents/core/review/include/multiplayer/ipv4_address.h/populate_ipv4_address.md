# populate_ipv4_address

**File of origin:** `core/source/multiplayer/ipv4_address.c`

## Semantic

Parses a dotted-decimal IPv4 address string and a port string, populating an `IPv4_Address` struct with the resulting 4-byte IP and 16-bit port. Returns `true` on success, `false` on failure.

## Pre-conditions

1. `p_ipv4_address` must be non-null; it is dereferenced to write the result.
2. `p_ip_address__cstr` must be non-null; it is indexed into during parsing.
3. `p_port__cstr` must be non-null; it is passed to `cstr_to_u16__limit_n`.
4. `p_ip_address__cstr` should be in standard dotted-decimal notation (e.g., "192.168.1.1"), with each octet being 1-3 digits separated by dots.
5. `p_port__cstr` should contain a numeric string representing a valid port number (0-65535).

## Post-conditions

1. On success (`true`): `*p_ipv4_address` is fully populated with the parsed IP bytes and port.
2. On failure (`false`): `*p_ipv4_address` is not modified (the function uses a local `IPv4_Address` and only assigns to the output pointer on the success path).
3. The local `IPv4_Address` is zero-initialized via `memset` before parsing begins.

## Correctness Verdict

**Incorrect**

## Semantic Alignment

The implementation's intent is to parse a dotted-decimal IP address and port string into an `IPv4_Address` struct. The parsing logic in `populate_ipv4_address` itself is structurally sound: it iterates over 4 IP bytes, trying to parse 1-3 character segments (trying longer lengths first to handle multi-digit octets), and advancing past dot separators via `index_of__ip_address__cstr += length_of__byte_chars + 1`.

However, the function relies on `cstr_to_u8__limit_n` and `cstr_to_u16__limit_n` to perform the actual numeric conversion, and **both helper functions contain a critical bug** that causes `populate_ipv4_address` to produce incorrect results.

In `cstr_to_u8__limit_n` (defined in `core/include/lav_string.h`):
```c
u32 value = 0;
value = (u8)cstr_to_u32__limit_n(p_cstr, limit_n, &value);
bool result = (value != 0);
```
The return value of `cstr_to_u32__limit_n` (a `bool`, i.e., `true` = 1 or `false` = 0) is cast to `(u8)` and assigned to `value`, **overwriting the parsed numeric value** that was written through the `&value` pointer. As a result, `value` becomes 1 on success (instead of the actual parsed number), and `*p_OUT_u8` is always set to 1.

The same bug exists in `cstr_to_u16__limit_n`:
```c
u32 value = 0;
value = (u16)cstr_to_u32__limit_n(p_cstr, limit_n, &value);
bool result = (value != 0);
```

Due to these bugs, `populate_ipv4_address` will:
- Set every successfully parsed IP byte to **1** (instead of the actual octet value). For example, "192.168.1.1" would produce `ip_bytes = {1, 1, 1, 1}`.
- Set the port to **1** (instead of the actual port value).

Additionally, both helper functions use `(value != 0)` as the success/failure discriminator, meaning they return `false` when the parsed value is 0. This would cause IP addresses containing zero octets (e.g., "192.168.0.1") to fail parsing entirely, even if the return-value bug were fixed.

## Implementation Correctness

- **Type compatibility:** Parameter types match the target struct fields correctly (`u8` for `ip_bytes`, `u16` for `port`). No implicit conversions or truncation issues in `populate_ipv4_address` itself.
- **Undefined behavior:** No broken pointer arithmetic, null dereference (assuming non-null inputs), type punning, or out-of-bounds access in `populate_ipv4_address` itself. The local `IPv4_Address` is properly zero-initialized.
- **Validation:** `populate_ipv4_address` does not validate that its pointer parameters are non-null. This is a potential safety issue but may be acceptable if the caller is expected to guarantee non-null inputs (consistent with the engine's design philosophy).
- **Helper function bugs:** The function delegates parsing to `cstr_to_u8__limit_n` and `cstr_to_u16__limit_n`, which have a type confusion bug (assigning a `bool` return value to a numeric variable) and a zero-value handling bug (treating a parsed value of 0 as a parse failure). These bugs make `populate_ipv4_address` produce incorrect output.

## Side Effects

- **Mutates `*p_ipv4_address`** on the success path (return `true`): the entire struct is overwritten with the parsed IP bytes and port.
- On the failure path (return `false`): `*p_ipv4_address` is not modified.
- No other external side effects; no I/O, no global state mutation.
