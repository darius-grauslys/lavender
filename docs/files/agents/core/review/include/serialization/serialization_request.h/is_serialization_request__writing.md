# is_serialization_request__writing

**File of origin:** `core/include/serialization/serialization_request.h` (lines 121–125)

## Semantic

Returns `true` if the given `Serialization_Request` is configured for a **write** operation, and `false` if it is configured for a **read** operation. It does this by negating the result of `is_serialization_request__reading`.

## Pre-conditions

1. `p_serialization_request` must be a valid, non-null pointer to an initialized `Serialization_Request` struct.
2. The `serialization_request_flags` field must have been set by one of the `set_serialization_request_as__read` or `set_serialization_request_as__write` functions (or otherwise had the `SERIALIZATION_REQUEST_FLAG__READ_OR_WRITE` bit configured appropriately).

## Post-conditions

1. Returns `true` when the `SERIALIZATION_REQUEST_FLAG__READ_OR_WRITE` bit (BIT(3)) is **clear** in `serialization_request_flags`.
2. Returns `false` when the `SERIALIZATION_REQUEST_FLAG__READ_OR_WRITE` bit (BIT(3)) is **set** in `serialization_request_flags`.
3. The `Serialization_Request` struct is **not modified** — the function is non-mutating.

## Correctness Verdict

**Correct**

## Semantic Alignment

The implementation correctly fulfills its semantic intent. The companion function `is_serialization_request__reading` checks whether the `SERIALIZATION_REQUEST_FLAG__READ_OR_WRITE` bit is set (returning a non-zero value when reading, zero when writing). The setter functions confirm the encoding:

- `set_serialization_request_as__read` sets the flag (OR with `SERIALIZATION_REQUEST_FLAG__READ_OR_WRITE`).
- `set_serialization_request_as__write` clears the flag (AND with `~SERIALIZATION_REQUEST_FLAG__READ_OR_WRITE`).

Therefore, a request is "writing" when the flag bit is clear, and `is_serialization_request__writing` correctly returns the logical negation of `is_serialization_request__reading`. The use of `!` ensures a normalized boolean result regardless of the raw bitwise-AND magnitude returned by `is_serialization_request__reading`.

## Implementation Correctness

- **Type compatibility:** The return type is `bool`, and `!is_serialization_request__reading(...)` produces a `bool` result. The parameter type `Serialization_Request *` matches the struct definition. No implicit conversions or truncation occur.
- **Undefined behavior:** No null dereference is avoided by contract (the caller must pass a valid pointer, consistent with all sibling functions in this header). No pointer arithmetic, type punning, or out-of-bounds access occurs. The function delegates to `is_serialization_request__reading`, which performs a simple bitwise AND on a `uint8_t` field.
- **Validation:** No validation is performed, which is appropriate — this is a simple inline accessor consistent with the pattern used by all sibling `is_serialization_request__*` functions in the same header. Validation is the caller's responsibility.

## Side Effects

No side effects. The function is a pure, non-mutating query that reads the `serialization_request_flags` field and returns a boolean result. It does not modify the `Serialization_Request` struct or any other state.
