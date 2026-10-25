# Planning: log.h — Incorrect Modules

**Review source:** `agents/core/review/include/log/log.h/incorrect_modules.md`

**Source files reviewed (read-only):**
- `core/include/log/log.h`
- `core/source/log/log.c`
- `core/include/defines.h` (Log struct, MESSAGE_MAX_QUANTITY_OF)
- `core/include/log/message.h`
- `core/source/log/message.c`
- `tests/core/source/log/test_suite_log_log.c`
- `tests/core/include/log/test_suite_log_log.h`

---

## 1. Problem Identification

Two functions in `core/source/log/log.c` were flagged as **Incorrect**:

### 1.1 `get_p_message_from__log` — Undefined behavior on empty log with index > 0

When the `Log` is empty (`p_oldest_message` is NULL, as set by `initialize_log`) and `index_of__message > 0`, the function initializes `p_message_current` to NULL and enters the loop. The boundary check `p_message_current == p_log->p_next_message` does not catch this case because `NULL != &p_log->messages[0]`. The function then calls `poll_message_pointer_for__wrapping` with `&p_message_current` where `*p_message_ptr` is NULL. Inside the callee, `(*p_message_ptr)++` performs pointer arithmetic on a NULL pointer, which is **undefined behavior** in C. Additionally, this triggers the misplaced initialization side effect in the callee, mutating `p_log->p_oldest_message` from a read-only getter — a **State Desync** between the function's `read-only query` semantics and its actual `mutating` behavior.

### 1.2 `poll_message_pointer_for__wrapping` — Side effect mismatch and skipped wrapping check

The function's name and documented intent is to advance a `Message *` by one position and handle circular-buffer wrapping. However, it contains two defects:

1. **Side effect mismatch**: When `p_log->p_oldest_message` is NULL, the function sets it to `&p_log->messages[0]` and returns early. This is an **initialization** concern (transitioning the log from "empty" to "non-empty"), not a wrapping concern. This represents a **Translation Gap** between the function's name/surface-form and its actual behavior.

2. **Skipped wrapping check**: The early `return` when `p_oldest_message` is NULL causes the wrapping check (`if (p_message - p_log->messages >= MESSAGE_MAX_QUANTITY_OF)`) to be skipped entirely. If the pointer has already advanced past the end of the `messages` array, it will not be wrapped — a latent **Boundary Condition** defect.

---

## 2. Impact Assessment

### 2.1 `get_p_message_from__log`

- **Declared in**: `core/include/log/log.h` (public API).
- **External callers found**: None identified in the codebase. The `Game` struct (`core/include/defines.h`, line 2557) holds `Log log__global`, `Log log__local`, `Log log__system`, but no call sites for `get_p_message_from__log` were found outside `log.c`.
- **De facto contract**: The current broken behavior treats `get_p_message_from__log` as an implicit initializer — calling it on an empty log with `index > 0` mutates `p_oldest_message` via the callee's side effect. Correcting this invalidates that de facto contract, but it is a **broken contract** that conflates read-only query semantics with state mutation. No legitimate caller should depend on a getter to initialize state.

### 2.2 `poll_message_pointer_for__wrapping`

- **Declared in**: Not present in `core/include/log/log.h` — it is an internal helper with no public declaration.
- **Call sites** (all within `core/source/log/log.c`):
  1. `flush_message_into__log` — first call: `poll_message_pointer_for__wrapping(p_log, &p_log->p_next_message)`. This is the call site that relies on the side effect to initialize `p_oldest_message` from NULL to `&messages[0]` on the first flush after `initialize_log`.
  2. `flush_message_into__log` — second call: `poll_message_pointer_for__wrapping(p_log, &p_log->p_oldest_message)` when the buffer is full (`p_oldest == p_next`). This call does not rely on the side effect.
  3. `get_p_message_from__log` — calls `poll_message_pointer_for__wrapping(p_log, &p_message_current)` during iteration. This is the call site that triggers the UB when `p_message_current` is NULL.
- **Impact of removing the side effect**: `flush_message_into__log` must be updated to perform the `p_oldest_message` NULL-check and initialization itself, before calling `poll_message_pointer_for__wrapping`. The observable behavior of `flush_message_into__log` is preserved (verified by tracing the circular-buffer logic through a full wrap-around cycle).

### 2.3 `flush_message_into__log`

- **Declared in**: `core/include/log/log.h` (public API).
- **External callers found**: None identified in the codebase.
- **Impact of changes**: Must add the `p_oldest_message` initialization guard before the first `poll_message_pointer_for__wrapping` call. The observable behavior (message insertion, circular wrapping, oldest-pointer advancement) is unchanged.

### 2.4 `initialize_log`

- No changes needed. Sets `p_oldest_message = 0` (NULL sentinel for empty log) and `p_next_message = &messages[0]`.

---

## 3. Resolution Assessment

### 3.1 Fix `poll_message_pointer_for__wrapping`

**What changes**: Remove the `p_oldest_message` NULL-check and early return. The function should purely advance the pointer and perform the wrapping check unconditionally.

```c
void poll_message_pointer_for__wrapping(
        Log *p_log,
        Message **p_message_ptr) {
    (*p_message_ptr)++;
    Message *p_message = *p_message_ptr;
    if (p_message
            - p_log->messages
            >= MESSAGE_MAX_QUANTITY_OF) {
        *p_message_ptr =
            &p_log->messages[0];
    }
}
```

**Callers needing updates**: `flush_message_into__log` (see below).

### 3.2 Fix `flush_message_into__log`

**What changes**: Add the `p_oldest_message` initialization guard before the first `poll_message_pointer_for__wrapping` call, replacing the side effect that was previously in the callee.

```c
void flush_message_into__log(
        Log *p_log) {
    if (!p_log->p_oldest_message) {
        p_log->p_oldest_message =
            &p_log->messages[0];
    }
    poll_message_pointer_for__wrapping(
            p_log,
            &p_log->p_next_message);
    initialize_message(p_log->p_next_message);
    if (p_log->p_oldest_message
            == p_log->p_next_message) {
        poll_message_pointer_for__wrapping(
                p_log,
                &p_log->p_oldest_message);
    }
}
```

**Verification**: Traced through the circular-buffer logic:
- After `initialize_log`: `p_oldest = NULL`, `p_next = &messages[0]`.
- First `flush_message_into__log`: guard sets `p_oldest = &messages[0]`; `p_next` advances to `&messages[1]`; `p_oldest != p_next` (no second call). Result: `p_oldest = &messages[0]`, `p_next = &messages[1]` — same as original.
- 31st `flush_message_into__log` (when `p_next` is at `&messages[31]`): guard is a no-op (`p_oldest` is non-NULL); `p_next` advances to `&messages[32]` (one-past-end); wrapping check wraps to `&messages[0]`; `initialize_message(&messages[0])`; `p_oldest == p_next` triggers second call advancing `p_oldest` to `&messages[1]`. Result: `p_oldest = &messages[1]`, `p_next = &messages[0]` — same as original.

### 3.3 Fix `get_p_message_from__log`

**What changes**: Add an early return guard for the empty-log case.

```c
Message *get_p_message_from__log(
        Log *p_log,
        Index__u8 index_of__message) {
    if (!p_log->p_oldest_message)
        return 0;
    Message *p_message_current =
        p_log->p_oldest_message;
    for (Index__u8 index_of__message_lookup = 0;
            index_of__message_lookup < index_of__message;
            index_of__message_lookup++) {
        if (p_message_current
                == p_log->p_next_message)
            return 0;
        poll_message_pointer_for__wrapping(
                p_log,
                &p_message_current);
    }
    return p_message_current;
}
```

**Callers needing updates**: None. The fix is a pure guard addition that prevents the UB path. With the guard in place, `get_p_message_from__log` never calls `poll_message_pointer_for__wrapping` with a NULL pointer, and never triggers the (now removed) side effect.

### 3.4 Documentation

No documentation updates needed beyond the code changes. The function comments in `log.h` already state "Will return nullptr if the index is out of range," which the fix makes true for all cases including the empty-log scenario.

---

## 4. Test Verification Checklist

### Existing Tests

- `tests/core/source/log/test_suite_log_log.c` — **No test cases exist**. The file is a stub containing only `#warning Please make tests for...` and `DEFINE_SUITE(log, END_TESTS)`.
- `tests/core/source/log/test_suite_log_message.c` — **No test cases exist**. Also a stub.

### Tests Asserting on Broken Behavior

- No existing tests assert on the incorrect behavior of either function, since no tests exist for the log module.

### New Tests Needed

- **`get_p_message_from__log` on empty log**: Verify it returns NULL for `index 0` and `index > 0` without side effects (no mutation of `p_oldest_message`). Use **Property Based Testing** to verify the `Representation Invariant` (empty log remains empty after read).
- **`get_p_message_from__log` on non-empty log**: Verify correct message retrieval at valid indices and NULL return for out-of-range indices. Use **Boundary Condition** testing at index 0, index `quantity - 1`, and index `quantity` (out of range).
- **`get_p_message_from__log` after full wrap-around**: Verify correct indexing after the circular buffer has wrapped. Use **Round Trip Check** to verify that flushing N messages and then retrieving them by index returns the expected messages in order.
- **`flush_message_into__log` circular buffer**: Verify that after flushing `MESSAGE_MAX_QUANTITY_OF` (32) messages, the buffer wraps correctly and `p_oldest_message` advances. Use **Property Based Testing** to verify the `Conservation Law` (number of valid messages never exceeds 32).
- **`poll_message_pointer_for__wrapping` wrapping**: Verify pointer advancement and wrap-to-start behavior at the array boundary. Use **Fuzzing** to test edge cases where the pointer is at or near the end of the array.

### Test Impact Assessment

- **Blast radius**: Low. No existing tests to update. New tests are additive.
- **Phased approach**: Not needed. The test suite for the log module is empty, so new tests can be added directly.

---

## 5. Blast Radius Summary

- **Files changed**: 1 source file (`core/source/log/log.c`). No header changes needed.
- **Functions changed**: 3 (`poll_message_pointer_for__wrapping`, `flush_message_into__log`, `get_p_message_from__log`).
- **Behavior preservation**: The changes are behavior-preserving for all correct callers of `flush_message_into__log`. The fix to `get_p_message_from__log` corrects UB without changing behavior for valid inputs.
- **De facto contracts invalidated**: The side effect in `poll_message_pointer_for__wrapping` that initialized `p_oldest_message` is removed. The only caller that relied on this (`flush_message_into__log`) is updated to handle it directly. No external callers depend on this behavior.
- **Phased approach**: Not needed. The blast radius is contained to a single internal module with no external callers.
