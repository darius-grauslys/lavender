get_p_client_by__uuid_from__game

## 1. Header

- **Function name:** `get_p_client_by__uuid_from__game`
- **File of origin:** `core/source/game.c`

## 2. Semantic

Looks up and returns a pointer to a non-deallocated `Client` in the game's contiguous client pool whose serialization-header `uuid` matches the requested `Identifier__u32`, or null if no such live client exists.

## 3. Pre-conditions

1. `p_game` must be non-null. The function does not null-check `p_game`; it dereferences it immediately, so this is the caller's responsibility per the codebase convention (sibling functions such as `allocate_client_from__game` and `release_client_from__game` follow the same convention).
2. `p_game->pM_clients` should have been allocated and its `Serialization_Header` slots initialized (e.g. via `initialize_serialization_header__contiguous_array`) so that `max_quantity_of__clients` accurately describes the pool length and each element has a well-formed header.
3. `p_game->max_quantity_of__clients` must equal the number of elements in the `pM_clients` contiguous array (it is consumed as the bound by `dehash_identitier_u32_in__contigious_array`).
4. `uuid__u32` may be any value; invalid identifiers (e.g. `IDENTIFIER__UNKNOWN__u32`) are handled by the callee (`dehash_identitier_u32_in__contigious_array` validates and returns 0), so no prior constraint is placed on the caller.
5. The client pool must have been allocated; otherwise the function logs a diagnostic and returns null.

## 4. Post-conditions

1. Returns a `Client *` whose `Serialization_Header.uuid` equals `uuid__u32`, or returns `0` (null) when:
   - the client pool is unallocated (`p_game->pM_clients == 0`),
   - `uuid__u32` is an invalid identifier,
   - no slot in the pool holds the requested uuid (identifier not present), or
   - the resolved slot is deallocated (`IS_DEALLOCATED_P` is true).
2. On a non-null return, the returned `Client` is guaranteed live (its uuid matches and is not `IDENTIFIER__UNKNOWN__u32`).
3. No state is mutated; the function is a read-only lookup.

## 5. Correctness Verdict

Correct

## 6. Semantic Alignment

The implementation fulfills the semantic intent. It (a) guards against an unallocated client pool, (b) delegates to `dehash_identitier_u32_in__contigious_array` to locate the matching live header (which both validates the identifier and walks the open-addressing collision chain), and (c) defensively rejects any deallocated entry via `IS_DEALLOCATED_P` before returning. Because `dehash_identitier_u32_in__contigious_array` only returns a header whose `uuid` matches the requested identifier, the returned pointer is guaranteed to correspond to the requested client. The redundant-looking `IS_DEALLOCATED_P` check is harmless defensive code: since the matching-header path can never yield a deallocated (`IDENTIFIER__UNKNOWN__u32`) entry, the guard is effectively a no-op on the success path but provides a safe null-return if that invariant is ever violated.

## 7. Implementation Correctness

- **Type compatibility:** `p_game->pM_clients` is `Client *`; `Client` declares `Serialization_Header _serialization_header` as its first member, so the cast to `Serialization_Header *` is a valid first-member struct alias (not type punning) and `dehash_identitier_u32_in__contigious_array` only reads within the `Serialization_Header` region. `p_game->max_quantity_of__clients` (`Quantity__u32`) is passed to a `Quantity__u32` parameter, and `uuid__u32` (`Identifier__u32`) to an `Identifier__u32` parameter — exact matches, no implicit conversions or truncation. The `(Client*)` return cast is the inverse of the valid first-member alias.
- **Undefined behavior:** None present on the intended usage path. There is no out-of-bounds access (the dehash callee bounds all indexing by `max_quantity_of__clients` and validates indices via `is_index_u32__out_of_bounds`); no broken pointer arithmetic; no null dereference in `IS_DEALLOCATED_P` (it short-circuits on a null pointer). `Client *` and `Serialization_Header *` share the first-member aliasing guarantee.
- **Validation:** Appropriate for the function's role. Pool allocation is validated here; identifier validity and lookup correctness are delegated to `dehash_identitier_u32_in__contigious_array` (single-responsibility delegation, consistent with sibling lookups such as `get_p_sprite_by__uuid_from__game`). Null-checking `p_game` is intentionally omitted to match the codebase-wide convention that `p_game` is non-null; this is the caller's responsibility.

## 8. Side Effects

No state mutation. The function is a pure read-only lookup. The only observable side effect is on the failure path where the client pool is unallocated: it emits diagnostic output via `debug_warning` ("Did you forget to allocate the client pool?") and `debug_error` ("get_p_client_by__uuid_from__game, pM_clients == 0.").
