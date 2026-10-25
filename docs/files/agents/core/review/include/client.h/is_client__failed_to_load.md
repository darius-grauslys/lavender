is_client__failed_to_load — core/include/client.h, lines 84-90

## 1. Header

- **Function name**: `is_client__failed_to_load`
- **File of origin**: `core/include/client.h`

## 2. Semantic

A static inline check that reports whether a given `Client` has the `CLIENT_FLAG__IS_FAILED_TO_LOAD` flag set, and as a side effect marks the client as inactive.

## 3. Pre-conditions

1. `p_client` may be null. The function does not validate this upfront; it relies on short-circuit evaluation in the return expression.
2. No other pre-conditions. The function does not require the client to be valid, loaded, or in any specific state prior to entry.

## 4. Post-conditions

1. **Side effect**: `p_client` is marked inactive — `CLIENT_FLAG__IS_ACTIVE` is cleared from `p_client->client_flags__u16` (regardless of whether `p_client` is null or not).
2. **Return value**: Returns `true` if `p_client` is non-null and `p_client->client_flags__u16` has `CLIENT_FLAG__IS_FAILED_TO_LOAD` set; otherwise returns `false`.

## 5. Correctness Verdict

Incorrect.

## 6. Semantic Alignment

The function name and declaration (`bool is_client__failed_to_load(Client *p_client)`) strongly imply a pure read-only query. However, the function mutates state by calling `set_client_as__inactive(p_client)`. This is a semantic drift: a function whose name begins with "is_" is expected to be a non-mutating predicate, yet it produces an observable side effect.

## 7. Implementation Correctness

There is a null-pointer dereference bug.

The function calls `set_client_as__inactive(p_client)` unconditionally at line 87. That callee (lines 78–82) has **no null check** on its `p_client` parameter and directly dereferences it:

```c
p_client->client_flags__u16 &= ~CLIENT_FLAG__IS_ACTIVE;
```

Meanwhile, `is_client__failed_to_load` itself does not null-check `p_client` at entry. If `p_client` is null:
- `set_client_as__inactive(NULL)` is invoked → null pointer dereference → undefined behavior.
- The return statement short-circuits (`p_client && ...`) so the function returns `false` without actually reaching the problematic access — but this is a coincidence of expression evaluation order, not a safety guarantee. The UB occurs at the call site of `set_client_as__inactive`, which is reached unconditionally.

Additionally, the function mutates `client_flags__u16` via `set_client_as__inactive` even when the intent is to *read* the `IS_FAILED_TO_LOAD` flag. If the caller only wanted a read, the mutation is unnecessary and surprising.

## 8. Side Effects

- **Mutates `p_client`**: `CLIENT_FLAG__IS_ACTIVE` is cleared from `p_client->client_flags__u16` via `set_client_as__inactive`.
- The mutation occurs unconditionally and is independent of the return value.
