# is_serialization_request__keep_alive

**File of origin:** `core/include/serialization/serialization_request.h`

## Semantic

Queries whether the `KEEP_ALIVE` flag is set on a `Serialization_Request`, indicating the request should persist (i.e., not be treated as fire-and-forget).

## Pre-conditions

1. `p_serialization_request` must be a valid, non-null pointer to an initialized `Serialization_Request` struct. No NULL check is performed; this is consistent with the codebase convention where callers are responsible for providing valid pointers (see all sibling `is_serialization_request__*` functions).

## Post-conditions

1. Returns `true` if the `SERIALIZATION_REQUEST_FLAG__KEEP_ALIVE` bit (BIT(4) = 0x10) is set in `serialization_request_flags`.
2. Returns `false` if the `SERIALIZATION_REQUEST_FLAG__KEEP_ALIVE` bit is not set.
3. The `Serialization_Request` struct is unmodified — this is a pure query function.

## Correctness Verdict

Correct

## Semantic Alignment

The implementation correctly checks the KEEP_ALIVE flag using a bitwise AND operation against `SERIALIZATION_REQUEST_FLAG__KEEP_ALIVE`. The result of the AND is either 0 (bit not set) or 0x10 (bit set), which implicitly converts to `bool` as `false` or `true` respectively. This correctly aligns with the semantic intent of the function.

## Implementation Correctness

- **Type compatibility:** The `serialization_request_flags` field is of type `Serialization_Request_Flags` (typedef'd to `uint8_t`). The bitwise AND with the flag macro (which expands to `(1U << 4)`) produces an `int` after integer promotion. This is implicitly converted to `bool` on return, which is well-defined in C (any non-zero value becomes `true`, zero becomes `false`). No truncation or implicit conversion issues.
- **Undefined behavior:** No pointer arithmetic, no null dereference (consistent with codebase convention), no type punning, no out-of-bounds access. The function reads a single field and returns a value.
- **Validation:** No NULL check is performed, but this matches the established pattern across all sibling query functions (`is_serialization_request__allocated`, `is_serialization_request__active`, `is_serialization_request__reading`, `is_serialization_request__tcp_or_io`). Validation is the caller's responsibility.

## Side Effects

No side effects. The function is a pure read-only query that accesses the `serialization_request_flags` field of the `Serialization_Request` struct without modifying any state.
