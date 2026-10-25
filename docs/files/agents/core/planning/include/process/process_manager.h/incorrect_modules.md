# Planning: process_manager.h — Incorrect Modules

**Review source:** `agents/core/review/include/process/process_manager.h/incorrect_modules.md`

**Source files reviewed (read-only):**
- `core/include/process/process_manager.h`
- `core/source/process/process_manager.c`
- `core/include/defines.h` (`Process_Manager_t`, lines ~1333–1339)
- `core/source/game.c` (`load_client`, lines ~484–507)
- `tests/core/source/process/test_suite_process_process_manager.c`

---

## 1. Problem Identification

**Flagged function:** `initialize_process_manager` (`core/source/process/process_manager.c:44`)

The function is a Lavender-style reset that returns a `Process_Manager` to its empty/pooled state. It correctly resets `processes[]`, `process_table`, `next__uuid__u32`, and the pseudo-random generator, but it **omits the `p_process__latest` field** (`core/include/defines.h:1337`). After initialization that pointer holds an **indeterminate value**.

- **Core defect:** a violated **Postcondition**. The init contract promises the manager is in a fully empty state, yet `p_process__latest` is left uninitialized. This is a **State Desync** between the intended empty state and the actual representation — a broken **Representation Invariant** on `Process_Manager`.
- **Consequence:** reading an uninitialized pointer is **Undefined Behavior**. The getter `get_p_latest_allocated_process_from__process_manager` (`process_manager.h`, inline) reads `p_process__latest` and returns it. If called before any `run_process`/`poll_process_manager`, it returns a garbage pointer instead of the intended NULL **Sentinel** meaning "no latest process."

The other write sites already establish the correct convention: `poll_process_manager` sets `p_process__latest = 0` at the start of every poll (`.c:157`) and `run_process` sets it to the newly allocated process (`.c:217`). Only the initializer fails to establish the NULL **Sentinel**.

## 2. Impact Assessment

**Who relies on the broken behavior / on the field:**

- `get_p_latest_allocated_process_from__process_manager` (`process_manager.h`, inline) — reads and clears `p_process__latest`. It is the sole reader of the field and inherits the indeterminate-value hazard.
- `core/source/game.c` `load_client` (lines ~490, 501): calls the getter and then guards with `if (!p_process)` (line 504). This guard is a **de-facto contract** that the getter returns NULL when nothing has been allocated. With the broken init, the field can be a non-NULL garbage pointer, so the `!p_process` check does **not** catch it and `load_client` may return an invalid pointer — propagating UB downstream.

**How the fix invalidates coupled assumptions:**

- The hazard window is narrow: between `initialize_process_manager` and the first `run_process`/`poll_process_manager`. In a running game, `poll_process_manager` clears the field each cycle (`.c:157`), so the bug mainly bites on a freshly initialized / pooled manager.
- No caller today *depends on* the indeterminate value as a feature; callers uniformly assume NULL-**Sentinel**-when-empty. Correcting the init therefore **restores** an already-relied-upon contract rather than breaking one. The fix is behavior-correcting, not behavior-altering, for existing callers: it makes the getter deterministically return NULL where it previously could return garbage.
- No data-structure or signature changes are required; the **Single Source of Truth** for "no latest process" remains the NULL value of `p_process__latest`.

## 3. Resolution Assessment

**Change (single, localized):** in `initialize_process_manager` (`core/source/process/process_manager.c`, inside the body after line 61 / before the closing brace at line 66), add:

```c
p_process_manager->p_process__latest = 0;
```

This aligns the initializer with the NULL-**Sentinel** convention already used by `poll_process_manager` (`.c:157`) and satisfies the init **Postcondition** that every field is in its empty state.

- **Callers:** no caller or signature changes required. `load_client` (game.c) and the getter become *safer* — their existing NULL checks now hold deterministically.
- **Documentation/spec:** update `docs/specs/core/process/process_manager.h.spec.md` init section to list `p_process__latest = 0` as an explicit **Postcondition**, so the **Representation Invariant** is documented and enforced contract-first.
- **Tests:** see checklist below.

### Test Verification Checklist

Surveyed `tests/core/source/process/test_suite_process_process_manager.c`:

- Existing tests (`run_process__sets_latest`, `get_p_latest__returns_null_after_consumption`) always call `run_process` **before** the getter, so they assert on correct behavior and do **not** exercise the uninitialized-read path. The fix does not invalidate any existing assertion.
- **New test required (gap):** a case that calls `get_p_latest_allocated_process_from__process_manager` immediately after `initialize_process_manager` with **no** prior `run_process`/poll, asserting it returns NULL. This is the exact broken path and currently has no coverage.
- **Recommended techniques:**
  - **Property Based Testing** on the init **Invariant**: after `initialize_process_manager`, all fields — including `p_process__latest` — are in their canonical empty values (uuid = `IDENTIFIER__UNKNOWN__u32`, handlers NULL, priority 1, status None, flags NONE, table zeroed, next uuid 0, latest NULL).
  - **Fuzzing** of the init→getter sequence (init then getter with zero allocations) to catch any residual indeterminate read under varied stack contents.

### Blast Radius Summary

- **Files changed:** 1 implementation file (`core/source/process/process_manager.c`, one line) + 1 spec/doc update + 1 test file (new case).
- **Behavior for current callers:** correcting, not altering — the getter's NULL-**Sentinel** contract becomes deterministic; no caller relies on the broken value.
- **Phased approach:** not needed; the change is a single additive line with no signature or data-structure impact.
- **De-facto contracts:** the fix *upholds* the existing "NULL when empty" contract relied on by `load_client`; it invalidates no de-facto contract.
- **Test blast radius:** Low (one new test case; no existing assertions invalidated).
