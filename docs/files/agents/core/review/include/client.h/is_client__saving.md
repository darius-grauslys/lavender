is_client__saving — core/include/client.h, lines 139-143

# is_client__saving

## Header

- **Function name:** `is_client__saving`
- **File of origin:** `core/include/client.h`

## Semantic

Returns `true` if the client has the `CLIENT_FLAG__IS_SAVING` flag set in its `client_flags__u16` field; otherwise returns `false`.

## Pre-conditions

1. `p_client` must be non-null.

## Post-conditions

1. Returns `true` if `CLIENT_FLAG__IS_SAVING` is set in `p_client->client_flags__u16`, otherwise returns `false`.

## Correctness Verdict

Correct.

## Semantic Alignment

The function name `is_client__saving` implies a non-mutating predicate that checks whether a client is in a saving state. The implementation fulfills this intent exactly: it performs a flag check on `client_flags__u16` for `CLIENT_FLAG__IS_SAVING` and returns a `bool`. No semantic drift — the function is a clean read-only query.

## Implementation Correctness

- **Type compatibility:** `p_client->client_flags__u16` is `uint16_t` and `CLIENT_FLAG__IS_SAVING` is a bitmask constant of matching type. The `&` operator is correctly applied. No implicit conversions or truncation.
- **Undefined behavior:** The null check (`p_client &&`) prevents null dereference. Bitwise operations on `uint16_t` are well-defined. No type punning or out-of-bounds access.
- **Validation:** The function validates that `p_client` is non-null before accessing its members. This is appropriate for a public query function.

## Side Effects

No side effects. This is a pure read-only query function.
