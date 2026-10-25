# Function Review: enqueue_process

## 1. Header
- **Function name:** `enqueue_process`
- **File of origin:** `core/include/process/process.h`

## 2. Semantic
Enqueues a process to run after another process completes by linking the enqueued process to the "host" process via the `p_enqueued_process` pointer and marking the enqueued process's status as `Process_Status_Kind__Enqueued`. The enqueued process will be dequeued (set to `Process_Status_Kind__Idle`) when the host process finishes during `poll_process_manager`.

## 3. Pre-conditions
1. `p_process_to__enqueue` must be non-null and point to a valid, initialized `Process` struct.
2. `p_process_to__enqueue_behind` must be non-null and point to a valid, initialized `Process` struct.
3. `p_process_to__enqueue` must not be the same pointer as `p_process_to__enqueue_behind` (checked only in debug builds via `#ifndef NDEBUG`).
4. `p_process_to__enqueue` should not already be enqueued (no check is performed; this could cause a previously linked enqueued process to be orphaned).

## 4. Post-conditions
1. `p_process_to__enqueue_behind->p_enqueued_process` is set to `p_process_to__enqueue`.
2. `p_process_to__enqueue->the_kind_of_status__this_process_has` is set to `Process_Status_Kind__Enqueued`.
3. `p_process_to__enqueue` will be skipped during `poll_process_manager` until the host process completes.
4. When the host process finishes, `p_process_to__enqueue` will be dequeued (status set to `Process_Status_Kind__Idle`) by the process manager's poll loop.

## 5. Correctness Verdict
**Incorrect**

## 6. Semantic Alignment
The implementation does not fully fulfill the semantic intent. The function is named "enqueue_process," which implies adding a process to a queue. However, the implementation only supports a single enqueued process per host process (via the `p_enqueued_process` union member). If called multiple times on the same `p_process_to__enqueue_behind`, the previous enqueued process pointer is silently overwritten, causing it to be orphaned — it will never be dequeued or run. This is a semantic mismatch between the function name (which implies queue semantics) and the implementation (which supports only a single next-process link).

Additionally, the `#ifndef NDEBUG` guard means the self-enqueue check is completely absent in release builds, providing no validation in production.

## 7. Implementation Correctness
- **Missing null checks:** Neither `p_process_to__enqueue` nor `p_process_to__enqueue_behind` is checked for null, even in debug mode. Every other similar function in this file (e.g., `complete_process`, `fail_process`, `get_process_status`, `is_process__enqueued`, `set_process_as__enqueued`, `set_process_as__dequeued`, etc.) includes a `#ifndef NDEBUG` null check with `debug_abort`. The absence of null checks here is inconsistent and introduces a null dereference risk.
- **No validation in release builds:** The only validation (self-enqueue check) is guarded by `#ifndef NDEBUG`, so release builds have zero validation.
- **Type compatibility:** Parameter types (`Process *`) match the struct field types exactly. No implicit conversions or truncation.
- **Undefined behavior risk:** If either pointer is null, the function will dereference null, causing undefined behavior. If `p_process_to__enqueue_behind` is null, writing to `->p_enqueued_process` is a null dereference.

## 8. Side Effects
- **Mutates** `p_process_to__enqueue_behind->p_enqueued_process`, setting it to `p_process_to__enqueue`.
- **Mutates** `p_process_to__enqueue->the_kind_of_status__this_process_has`, setting it to `Process_Status_Kind__Enqueued`.
- No other side effects. No memory allocation, no I/O, no external state changes.
