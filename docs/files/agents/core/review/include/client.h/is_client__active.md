is_client__active — core/include/client.h, lines 132-136

## 1. Header

- **Function name:** `is_client__active`
- **File of origin:** `include/client.h`

## 2. Semantic

Determines whether a `Client` is currently in the active state by checking if the `CLIENT_FLAG__IS_ACTIVE` bit is set in its `client_flags__u16` field.

## 3. Pre-conditions

1. `p_client` must be a valid pointer to a `Client` (the function handles `NULL` internally).
2. `p_client->client_flags__u16` must be a valid `Client_Flags__u16` bitfield value.

## 4. Post-conditions

1. Returns `true` if `CLIENT_FLAG__IS_ACTIVE` (BIT(0)) is set in `client_flags__u16`.
2. Returns `false` if `CLIENT_FLAG__IS_ACTIVE` is not set, or if `p_client` is `NULL`.

## 5. Correctness Verdict

Correct

## 6. Semantic Alignment

The function's intent is to check whether a Client is active. The implementation tests the `CLIENT_FLAG__IS_ACTIVE` bit (defined as `BIT(0)` at line 2415 of `defines.h`), which correctly matches the semantic intent. The function also properly guards against a null `p_client` by returning `false` in that case.

## 7. Implementation Correctness

- **Type compatibility:** `p_client` is `Client*`, dereferencing to `client_flags__u16` of type `Client_Flags__u16` (which is `u16`). `CLIENT_FLAG__IS_ACTIVE` is `BIT(0)`, also a `u16`. The `&` operation between a `u16` and another `u16` is well-defined. The `&&` compound assignment correctly promotes to `bool`. No implicit conversions or truncation issues.
- **No undefined behavior:** No pointer arithmetic, no null dereference (null is guarded), no type punning, no out-of-bounds access.
- **Validation:** The null check is appropriate for the function's role — it takes ownership of null-pointer safety.

## 8. Side Effects

No side effects. This is a pure read function that does not modify `p_client` or any other observable state.
