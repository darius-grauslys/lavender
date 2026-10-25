# Planning: game_action_process.h — Incorrect Modules

**Review source:** `agents/core/review/include/process/game_action_process.h/incorrect_modules.md`

**Source files reviewed (read-only):**
- `core/include/process/game_action_process.h`
- `core/include/process/tcp_game_action_process.h`
- `core/source/process/tcp_game_action_process.c`
- `core/source/process/game_action_process.c`
- `core/source/serialization/serialization_request.c`
- `tests/core/source/process/test_suite_process_tcp_game_action_process.c`

---

## 1. Problem Identification

### 1.1 Unchecked return value of `activate_serialization_request` (primary defect)

`set_game_action_process_as__tcp_payload_receiver` calls `activate_serialization_request` and discards its `bool` return value. On TCP-mode activation, this function allocates a packet-tracking bitmap via `malloc`. If allocation fails, the function returns `false`, but the caller proceeds unconditionally to:

- Attach the partially-initialized `Serialization_Request` to `p_process->p_process_data`
- Set the dispose handler and process kind

This violates the **Postcondition** stated in the function's contract: *"On failure (returns false): p_process is left unmodified."* The process is mutated into a state where its `Serialization_Request` has a NULL `pM_packet_bitmap`, breaking the **Representation Invariant** that an active TCP serialization request always owns a valid bitmap.

### 1.2 Translation Gap: header declaration name mismatch (compounding defect)

`core/include/process/tcp_game_action_process.h` declares:
```c
bool initialize_process_as__tcp_game_action_payload_receiver(...);
```

The implementation in `core/source/process/tcp_game_action_process.c` defines:
```c
bool set_game_action_process_as__tcp_payload_receiver(...);
```

`core/include/process/game_action_process.h` also declares `set_game_action_process_as__tcp_payload_receiver`, creating a **Non-Injective Translation**: two distinct header declarations map to one implementation, while the name in `tcp_game_action_process.h` has no corresponding symbol. This is a **Surface-form leakage** — the header's declared name was authored independently of the implementation's actual name. The test file references `initialize_process_as__tcp_game_action_payload_receiver` and notes *"does not have a implementation"*, confirming the **Stub-real divergence**: the declared interface is a placeholder with no backing symbol.

### 1.3 Prerequisite bug in `activate_serialization_request`

`activate_serialization_request` (in `core/source/serialization/serialization_request.c`) calls `memset` on `pM_packet_bitmap` **before** checking whether `malloc` returned NULL. If allocation fails, the function crashes (NULL dereference in `memset`) rather than returning `false`. Until this is fixed, a return-value check in the caller is insufficient — the callee will fault before it can signal failure.

---

## 2. Impact Assessment

### 2.1 Downstream callers relying on the broken behavior

| Caller | File | Coupling |
|--------|------|----------|
| `poll_game_action_process__tcp_receive` | `core/source/process/tcp_game_action_process.c` | Dereferences `p_serialization_request->pM_packet_bitmap` unconditionally (non-`NDEBUG` path). If the bitmap is NULL due to failed activation, this is an immediate NULL dereference. |
| `m_process__dispose_handler__tcp__default` | `core/source/process/tcp_game_action_process.c` | Calls `PLATFORM_release_serialization_request`. The internal `deactivate_serialization_request` checks for NULL bitmap before freeing, so the dispose path is **safe** in the failure case. However, it releases a request that was never properly activated. |
| External process handlers (unidentified) | TBD | Any process that calls `set_game_action_process_as__tcp_payload_receiver` and then polls via `poll_game_action_process__tcp_receive` inherits the NULL-dereference risk. |

### 2.2 Assumptions invalidated by correction

- **Assumption A**: "After a successful call, the process is fully configured for TCP reception." Correcting the function to return `false` on activation failure means callers that previously received `true` (because the return was never checked internally) will now receive `false`. Any caller that does not handle the `false` return will enter an unhandled error path.
- **Assumption B**: "The function name in `tcp_game_action_process.h` is the canonical entry point." Renaming to unify the declaration and implementation will break any code that links against the header-declared name (currently none, since no such symbol exists).
- **De facto contract**: No existing production code appears to call this function yet (tests are stubbed with `MUNIT_FAIL`). The blast radius is therefore contained.

### 2.3 Test impact

`tests/core/source/process/test_suite_process_tcp_game_action_process.c` has both test functions fully commented out with `return MUNIT_FAIL`. No existing assertions are invalidated by the fix. New tests must be authored.

---

## 3. Resolution Assessment

### Phase 1 — Fix prerequisite: `activate_serialization_request` ordering

**File:** `core/source/serialization/serialization_request.c`

Reorder the TCP-path allocation block:
1. Call `malloc`.
2. **Immediately** check for NULL; if NULL, `debug_error` and `return false`.
3. Call `memset` on the confirmed non-NULL pointer.

Also correct the copy-paste error in the `debug_error` string (`"initialize_serialization_request"` → `"activate_serialization_request"`).

This is a prerequisite: without it, the return-value check in Phase 2 is dead code (the callee crashes before returning).

### Phase 2 — Check return value in `set_game_action_process_as__tcp_payload_receiver`

**File:** `core/source/process/tcp_game_action_process.c`

After the `activate_serialization_request` call, add:
```c
if (!activate_serialization_request(...)) {
    PLATFORM_release_serialization_request(
        get_p_PLATFORM_file_system_context_from__game(p_game),
        p_serialization_request);
    return false;
}
```

This restores the **Postcondition**: on failure, `p_process` is left unmodified (the dispose handler and `p_process_data` are not yet set at the point of the check, since the activation call precedes them in the current code layout). If the current ordering sets the dispose handler *before* activation, reorder so that all `p_process` mutations occur only after successful activation.

### Phase 3 — Resolve Translation Gap: unify function name

**Files:** `core/include/process/tcp_game_action_process.h`, `core/include/process/game_action_process.h`, `core/source/process/tcp_game_action_process.c`

Choose one canonical name (recommendation: `set_game_action_process_as__tcp_payload_receiver`, since it is already declared in `game_action_process.h` and matches the implementation). Then:

- Update `tcp_game_action_process.h` to declare the same name (or remove the redundant declaration if `tcp_game_action_process.h` always includes `game_action_process.h`).
- Ensure **SSOT**: exactly one header declares the function.
- Update the test file to reference the correct name.

### Phase 4 — Test coverage

**File:** `tests/core/source/process/test_suite_process_tcp_game_action_process.c`

Uncomment and adapt existing stubs, or author new tests:

| Test | Strategy | Purpose |
|------|----------|---------|
| `set_tcp_receiver__success_path` | **Equivalence Check**: verify post-call state (dispose handler, process kind, `p_data` preservation, bitmap non-NULL) matches the **Postcondition**. | Confirms happy path. |
| `set_tcp_receiver__activation_failure` | **Fuzzing** / fault injection: mock or inject a `malloc` failure so `activate_serialization_request` returns `false`. Assert function returns `false` and `p_process` is unmodified. | Verifies the corrected error path. |
| `set_tcp_receiver__allocation_failure` | Fault injection on `PLATFORM_allocate_serialization_request`. Assert early return with no mutation. | Verifies the pre-existing allocation guard. |
| `poll_tcp_receive__after_failed_setup` | **Property Based Testing**: for any process where setup returned `false`, polling must not dereference NULL. (Guarded by the fix; test documents the invariant.) | Prevents regression of the NULL-deref. |
| `round_trip__process_data_preservation` | **Round Trip Check**: after setup + complete, `p_process_data` should be restorable to its original value. | Verifies the pointer-save/restore contract. |

**Blast radius (test): Low.** No existing active assertions are invalidated. All tests are new or re-enabled from stubs.

---

## 4. Test Verification Checklist

- [ ] No existing test assertions reference the broken behavior (confirmed: all tests are `MUNIT_FAIL` stubs).
- [ ] New tests must cover: success path, activation-failure path, allocation-failure path.
- [ ] **Property Based Testing**: generate random payload sizes (0, 1, exact-multiple-of-packet-size, max `u16`) and verify the bitmap size formula and activation outcome.
- [ ] **Round Trip Check**: verify that `p_process_data` is preserved through the Serialization_Request wrapper and recoverable.
- [ ] **Mutation Testing** (post-implementation): confirm the test suite catches removal of the return-value check.

---

## 5. Blast Radius Summary

| Dimension | Assessment |
|-----------|------------|
| Files requiring changes | 4 (1 prerequisite fix, 1 primary fix, 1 header rename, 1 test file) |
| Behavior-preserving for current callers? | Yes — no production caller exists yet; tests are stubs. |
| Phased approach needed? | Yes — Phase 1 (prerequisite) must land before Phase 2 (primary fix) is observable. Phase 3 (rename) is independent and can follow. |
| De facto contracts invalidated? | None in production. The only "contract" is the test stubs, which are already non-functional. |
| Risk of `poll_game_action_process__tcp_receive` NULL deref post-fix? | Eliminated — the function can no longer leave a process in a partially-activated TCP state. |
