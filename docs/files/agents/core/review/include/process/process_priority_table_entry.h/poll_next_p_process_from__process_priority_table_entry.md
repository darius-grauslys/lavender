# poll_next_p_process_from__process_priority_table_entry

**File of origin:** `core/source/process/process_priority_table_entry.c`

## Semantic

Polls (returns) the next process from the priority table entry in a round-robin
fashion, advancing the internal current-swap pointer from the youngest process
toward the oldest. When the oldest process is polled, the pointer wraps around
to the youngest and the function signals that the table entry is done polling
(true), indicating the caller should move to the next priority table entry.

## Pre-conditions

1. `p_process_priority_table_entry` must be non-null and point to a valid,
   initialized `Process_Priority_Table_Entry` struct.
2. `p_ptr_OUT_process` must be non-null (the caller's responsibility; the
   function does not validate this pointer).
3. The internal pointers (`p_ptr_process__youngest_of__priority`,
   `p_ptr_process__oldest_of__priority`, `p_ptr_process__current_priority_to__swap`)
   must all point into the same `Process*` array (i.e., `ptr_array_of__processes`
   within the owning `Process_Table`), or be null (0) if the entry is empty.
4. If the entry is non-empty, `p_ptr_process__current_priority_to__swap` must
   lie within the range [`youngest_of__priority`, `oldest_of__priority`].

## Post-conditions

1. If the table entry is empty (either `oldest` or `youngest` pointer is null),
   the function returns `false` (0) and does not modify `*p_ptr_OUT_process`.
2. If the table entry is non-empty:
   - `*p_ptr_OUT_process` is set to the `Process*` at the current swap position.
   - `p_ptr_process__current_priority_to__swap` is incremented by one.
   - If the incremented pointer exceeds `p_ptr_process__oldest_of__priority`,
     it wraps around to `p_ptr_process__youngest_of__priority`.
   - The return value is `true` if the polled process was the oldest process
     (i.e., the last process in the polling cycle), `false` otherwise.
3. The table entry is not otherwise modified (no processes are added, removed,
   or reordered).

## Correctness Verdict

**Correct**

## Semantic Alignment

The implementation fully aligns with the documented semantic intent. The header
documentation states: "Returns true if the table is wrapping around. In other
words, returns true if the last process in the table entry was polled, and its
time to move to the next table entry."

The function:
- Correctly checks for emptiness via `is_process_priority_table_entry__empty`.
- Retrieves the process at the current swap position.
- Detects when the oldest process has been polled (signaling wrap-around).
- Advances the current pointer and wraps it to the youngest when it exceeds
  the oldest, maintaining the round-robin invariant.
- Outputs the polled process and returns the wrap-around flag.

The polling order (youngest to oldest, then wrap) is consistent with how
processes are stored in the array: `youngest_of__priority` is at the lowest
array index and `oldest_of__priority` at the highest, as established by the
`add_process_to__process_priorty_table_entry_in__ptr_array_of__processes` and
`move_process_priorty_table_entry_up__one_in__ptr_array_of__processes` functions.

## Implementation Correctness

- **Type compatibility:** All pointer types are consistent. The struct fields
  are `Process**`; dereferencing yields `Process*`, which matches the `Process*`
  local variable `p_process` and the `Process*` pointed to by `p_ptr_OUT_process`.
  Pointer comparisons (`p_process == *oldest`, `++current > oldest`) are between
  operands of matching types (`Process*` vs `Process*`, `Process**` vs `Process**`).
  No implicit conversions or truncation occur.

- **Undefined behavior:** No null dereference occurs in the non-empty path
  (emptiness is checked first). Pointer arithmetic (`++current`) is confined to
  the valid range of the `ptr_array_of__processes` array. The wrap-around
  assignment restores `current` to `youngest`, which is always within bounds.
  No type punning or out-of-bounds access is present.

- **Validation:** The function appropriately delegates validation to the
  caller for `p_ptr_OUT_process` (not null-checked), which is consistent with
  the low-level utility nature of this function. The emptiness check is
  appropriate and sufficient for this function's role.

- **Pre-increment correctness:** The use of pre-increment (`++current`) before
  the comparison is correct — the comparison checks whether the *new* position
  has exceeded `oldest`, which is the intended behavior.

## Side Effects

The function mutates `p_process_priority_table_entry->p_ptr_process__current_priority_to__swap`
as its primary side effect: the pointer is advanced by one slot (with wrap-around
to `youngest_of__priority` when it passes `oldest_of__priority`). The output
parameter `*p_ptr_OUT_process` is written with the polled `Process*` when the
table entry is non-empty. No other state is modified.
