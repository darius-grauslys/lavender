# Function Review: `is_local_space__allocated`

**File of origin:** `core/include/world/local_space.h`

## Semantic

Returns `true` if the given `Local_Space` is allocated — i.e., it is non-null, has a non-null `p_global_space` pointer, and that `Global_Space` is itself allocated (not deallocated and has at least one active reference).

## Pre-conditions

1. `p_local_space` may be null (the function handles this gracefully).
2. If `p_local_space` is non-null, it must point to a valid `Local_Space` struct (i.e., not an invalid/dangling pointer).
3. If `p_local_space->p_global_space` is non-null, it must point to a valid `Global_Space` struct.

## Post-conditions

1. Returns `true` if and only if all of the following hold:
   - `p_local_space` is non-null.
   - `p_local_space->p_global_space` is non-null.
   - `is_global_space__allocated(p_local_space->p_global_space)` returns `true`.
2. Returns `false` otherwise (including when `p_local_space` is null, or when `p_global_space` is null, or when the global space is deallocated or has zero references).
3. The function has no side effects; the state of `Local_Space` and `Global_Space` is unchanged.

## Correctness Verdict

**Correct**

## Semantic Alignment

The implementation correctly fulfills the semantic intent of checking whether a `Local_Space` is allocated. The function delegates to `get_p_global_space_from__local_space` (which safely handles a null `p_local_space` by returning 0) and then to `is_global_space__allocated` (which checks that the global space is non-null, not deallocated via the serialization header UUID check, and has a non-zero reference count). The short-circuit evaluation of `&&` ensures no null pointer dereferences occur. The logic is sound and matches the function's name and purpose.

## Implementation Correctness

- **Type compatibility:** All types match exactly. `p_local_space` is `Local_Space *`, the return of `get_p_global_space_from__local_space` is `Global_Space *`, and `is_global_space__allocated` accepts `Global_Space *`. The return type is `bool`.
- **Undefined behavior:** No undefined behavior. Null pointers are checked before dereferencing. The `&&` short-circuit prevents `get_p_global_space_from__local_space` from being called on a null `p_local_space`, and `is_global_space__allocated` is only called when the global space pointer is non-null.
- **Validation:** Appropriate for the function's role. This is a query/predicate function; it validates its own inputs (null checks) and delegates deeper validation to `is_global_space__allocated`.

## Side Effects

No side effects. This is a pure query function that reads from `Local_Space` and `Global_Space` but does not modify any state.
