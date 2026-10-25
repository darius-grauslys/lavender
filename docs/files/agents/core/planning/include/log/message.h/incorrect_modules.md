# Planning: message.h — Incorrect Modules

**Review source:** `agents/core/review/include/log/message.h/incorrect_modules.md`

**Source files reviewed (read-only):**
- `core/include/log/message.h`
- `core/source/log/message.c`
- `core/include/defines.h` (`Message`, `MESSAGE_MAX_LENGTH_OF`, `MESSAGE_NAME_MAX_LENGTH_OF`)
- `core/source/game.c` (callers via `print_log__*`)
- `tests/core/source/log/test_suite_log_message.c` (stub)

---

## 1. Problem Identification

Two functions in `core/source/log/message.c` are flagged **Incorrect**. Both share one root defect: a **Boundary Condition** violation that breaks the documented **Postcondition** (a **Translation Gap** between the header contract and the real implementation, i.e. a `Stub-real divergence`).

### 1.1 `put_cstr_into__message` — `core/source/log/message.c:43`
- **Documented Postcondition:** "Returns true if message body is full."
- **Defect:** the loop only returns `true` when the callee `put_char_into__message` reports the body was *already* full at call time. It never detects the case where the body becomes full exactly on the final character. The trailing `return false;` (line 60) therefore returns `false` for an input string of exactly `MESSAGE_MAX_LENGTH_OF` (96) chars, even though `index_of__body == 96` (full). **The Postcondition is violated at the exact-fit boundary.**
- **Secondary defects (noted in review, lower priority):**
  - No null check for `cstr`, inconsistent with the debug-build `p_message` check (undefined behavior on null `cstr`).
  - Loop counter `size_of__message` is `Quantity__u8`; a **latent overflow** if `MESSAGE_MAX_LENGTH_OF` ever exceeds 255.
  - `cstr` is non-`const` though only read.

### 1.2 `set_title_of__message` — `core/source/log/message.c:67`
- **Documented Postcondition:** "Will return true if the title had to be truncated."
- **Defect:** the truncation test `size_of__message + 1 > MESSAGE_NAME_MAX_LENGTH_OF` (line 78) is equivalent to `size_of__message >= 16`, which fires *after* the 16th (last valid) byte has been written. For an input of exactly 16 chars (no truncation), it unconditionally returns `true`. **The Postcondition is violated at the exact-fit boundary** — it reports truncation when the buffer was merely filled.
- **Secondary defects:** no null checks (`p_message`/`cstr`); empty-string input leaves `length_of__message__title` at its prior value (not reset to 0).

Both are off-by-one / wrong-side-of-boundary checks, contrasting with the correct pattern in `put_char_into__message` (line 33), which checks the boundary *before* writing.

## 2. Impact Assessment

The defects are confined to the **return value** of each function. The buffer mutation behavior (`message__body`, `message__title`, and the length/index fields) is already correct and is **not** changed by the fix — so no `State Desync` or **Representation Invariant** break is introduced by correcting them.

Callers relying on the broken return value:

- **`put_cstr_into__message`:** called only by three wrappers in `core/source/game.c` — `print_log__global` (line 649), `print_log__local` (line 659), `print_log__system` (line 669). Each captures the result and propagates it via its own return. These wrappers are declared in `core/include/game.h:177-179`. **No in-tree code calls the `print_log__*` wrappers** (verified across `core/`, `no_gui/`, `examples/`), so the broken value is currently an unobserved de facto contract. Correcting it flips the return from `false`→`true` only for exact-96-char inputs; all other inputs are unchanged, so existing callers remain behavior-preserving.
- **`set_title_of__message`:** **no in-tree callers found.** Zero blast radius within the repo.
- **Data structures:** `Message` (`core/include/defines.h`) fields are written identically before and after; only the boolean outcome changes.

**Net:** correcting these invalidates no in-tree assumption. The only de facto contract touched is the propagated return of `print_log__*`, which is exposed to external game code — a Low-risk, behavior-preserving change for all but the exact-fit boundary case.

## 3. Resolution Assessment

Fix both functions to make the actual return value `Faithful` to the documented Postcondition. Scope is a single file (`core/source/log/message.c`) plus test authoring; **no caller changes are required in-tree.**

### 3.1 `put_cstr_into__message`
- Replace the trailing `return false;` (line 60) with:
  ```c
  return p_message->index_of__body >= MESSAGE_MAX_LENGTH_OF;
  ```
  This makes the return reflect the true **Postcondition** (body full) in all cases, including exact-fit.
- Optional hardening (aligns with codebase convention): add a debug-build `cstr` null check mirroring the existing `p_message` check; declare `const char *cstr`.
- Latent overflow: keep `MESSAGE_MAX_LENGTH_OF < 256`; if that bound is ever raised, widen the counter type. Note as a **Precondition** rather than changing the type now.

### 3.2 `set_title_of__message`
- Change the truncation return (line 79) to peek one byte past the filled buffer:
  ```c
  if (size_of__message + 1 > MESSAGE_NAME_MAX_LENGTH_OF) {
      return cstr[size_of__message] != 0;
  }
  ```
  Returns `true` only when a real character beyond capacity was dropped; `false` when the string ended exactly at capacity.
- Optional hardening: reset `length_of__message__title = 0` for empty-string input; add null checks for consistency with `put_cstr_into__message`.

### 3.3 Documentation
- The header comments in `core/include/log/message.h` already state the *correct* intent — no doc change needed; the implementation is brought into alignment with them.

**Blast radius: Low.** One source file changes; changes are behavior-preserving for all current callers except the exact-fit boundary (which is the intended correction). No phased approach required.

## 4. Test Verification Checklist

- **Existing tests:** `tests/core/source/log/test_suite_log_message.c` is a **stub** (`DEFINE_SUITE(message, END_TESTS)` with a `#warning` placeholder) — it asserts nothing, so no existing assertions are invalidated. The suite currently provides no coverage for either function.
- **New tests required** (author from scratch in the stub):
  - **Equivalence Check** at the boundaries: input lengths `{95, 96, 97}` for `put_cstr_into__message` and `{15, 16, 17}` for `set_title_of__message`; assert the return value and the length/index fields.
  - **Property Based Testing**: for arbitrary `cstr`, assert `put_cstr_into__message(...) == (index_of__body >= MESSAGE_MAX_LENGTH_OF)` and that written length equals `min(strlen(cstr), capacity)`.
  - **Round Trip Check**: after `set_title_of__message`, the title bytes up to `length_of__message__title` equal `min(input, 16)`; empty input yields length 0.
  - **Fuzzing**: random-length inputs around both capacities to catch any residual off-by-one.
- **Test blast radius: Low** — additive only (stub → populated); no existing green tests to re-baseline.

## 5. Blast Radius Summary

- **Files changed:** `core/source/log/message.c` (2 functions). Optionally `core/include/log/message.h` (no change needed — doc already correct).
- **Caller updates:** none in-tree (`print_log__*` propagate but are unobserved; `set_title_of__message` has no callers).
- **Behavior-preserving for current callers:** yes, for all inputs except the exact-fit boundary (the intended fix).
- **Phased approach:** not needed.
- **De facto contracts invalidated:** only the previously-wrong exact-fit return value of `put_cstr_into__message` as surfaced through `print_log__*`; no in-tree consumer depends on it.
