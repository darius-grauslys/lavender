# is_process__failed

**File of origin:** `core/include/process/process.h`

## Semantic

A query function that checks whether a `Process` has a status of `Process_Status_Kind__Fail`, indicating the process has failed.

## Pre-conditions

1. `p_process` must be a valid, non-null pointer to a `Process` struct.
2. In debug builds (`NDEBUG` not defined), a null `p_process` triggers `debug_abort` and the function returns `false`.
3. In release builds (`NDEBUG` defined), the null check is omitted; callers must ensure `p_process` is non-null to avoid undefined behavior.
4. `p_process->the_kind_of_status__this_process_has` must be a valid `Process_Status_Kind` enum value.

## Post-conditions

1. Returns `true` if `p_process->the_kind_of_status__this_process_has` equals `Process_Status_Kind__Fail`.
2. Returns `false` for any other status value (e.g., `Process_Status_Kind__None`, `Process_Status_Kind__Stopped`, `Process_Status_Kind__Idle`, `Process_Status_Kind__Busy`, `Process_Status_Kind__Stopping`, `Process_Status_Kind__Enqueued`, `Process_Status_Kind__Complete`, `Process_Status_Kind__Unknown`).
3. The `Process` struct is not modified; this is a read-only query.

## Correctness Verdict

Correct

## Semantic Alignment

The implementation correctly delegates to `get_process_status(p_process)` and compares the result against `Process_Status_Kind__Fail`. This precisely matches the semantic intent of the function name `is_process__failed`. The function checks only for the `Fail` status and does not conflate it with other terminal statuses such as `Complete` or `Stopped`. The use of `get_process_status` as the accessor is consistent with the pattern used by other `is_process__*` query functions in the same header (e.g., `is_process__complete`, `is_process__active`).

## Implementation Correctness

- **Type compatibility:** `p_process` is `Process *`, matching the parameter signature of `get_process_status`. The return type of `get_process_status` is `enum Process_Status_Kind`, and `Process_Status_Kind__Fail` is a valid enumerator of that enum. The comparison `==` between two values of the same enum type is type-safe with no implicit conversions or truncation.
- **Undefined behavior:** No null dereference occurs in debug builds, as the null check precedes the call to `get_process_status`. In release builds, the null check is removed, but this is consistent with the established pattern across all `is_process__*` functions in this header and is a deliberate design choice for performance.
- **Validation:** The null check in debug builds is appropriate for a query function and matches the validation pattern used by all sibling functions. The function does not perform additional validation beyond what is expected for its role.

## Side Effects

No side effects. This is a pure query function. It reads `p_process->the_kind_of_status__this_process_has` via `get_process_status` and returns a boolean result without modifying the `Process` struct or any other state.
