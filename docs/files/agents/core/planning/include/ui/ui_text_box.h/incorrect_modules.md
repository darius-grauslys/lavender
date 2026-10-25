# Planning: ui_text_box.h — Incorrect Modules

**Review source:** `agents/core/review/include/ui/ui_text_box.h/incorrect_modules.md`

**Source files reviewed (read-only):**
- `core/include/ui/ui_text_box.h` (inline wrapper layer)
- `core/source/ui/ui_text_box.c` (`m_ui_element__typed_handler__text_box__alphanumeric`)
- `core/source/ui/ui_text.c` (underlying callees: `insert_c_str_into__ui_text`, `set_c_str_of__ui_text_with__const_c_str`, `clear_c_str_of__ui_text`)
- `core/include/ui/ui_text.h` (`get_p_const_c_str_text_of__ui_text`)
- `tests/core/source/ui/test_suite_ui_ui_text_box.c`
- `tests/core/source/ui/test_suite_ui_ui_text.c`

**Flagged as Incorrect (4):**
1. `insert_c_str_into__ui_text_box` (wrapper) → `insert_c_str_into__ui_text`
2. `set_c_str_of__ui_text_box_with__const_c_str` (wrapper) → `set_c_str_of__ui_text_with__const_c_str`
3. `m_ui_element__typed_handler__text_box__alphanumeric` (handler, in `.c`)
4. `clear_c_str_of__ui_text_box` (wrapper) → `clear_c_str_of__ui_text`

---

## 1. Problem Identification

All four defects live one layer below the flagged header wrappers (or in the `.c`
handler). The public wrappers in `ui_text_box.h` are thin, correct pass-throughs;
the semantic mismatch is in their callees.

### 1.1 `insert_c_str_into__ui_text` (via `insert_c_str_into__ui_text_box`)
**Defect class: `Mode Confusion` / `Translation Gap`.**
The intent is a fixed **byte-count** copy (`size_of__text` bytes) at an index, but the
callee uses `strncpy` (a null-terminated *string* primitive) instead of `memcpy`.
When the source contains an embedded null before `clamp` bytes, fewer bytes are copied
than intended, yet `index_of__cursor_in__char_buffer` is still advanced by the full
`clamp`. This produces a **State Desync** between bytes actually written and the cursor
position. Sibling `append_c_str_into__ui_text` (ui_text.c:253) correctly uses `memcpy`.
Secondary gap: no null guard on `p_text__const_c_str` (a null source to `strncpy` is
undefined behavior) — an unenforced **Precondition**.

### 1.2 `set_c_str_of__ui_text_with__const_c_str` (via `set_c_str_of__ui_text_box_with__const_c_str`)
**Defect class: `Translation Gap` (missing implementation) / Postcondition violation.**
The callee frees the old buffer, allocates a new one, zeroes it with `memset`, and
returns — but **never copies** the content of `p_text__const_c_str`. The buffer is left
all-zero, so the "set" operation silently *clears* the text. This contradicts the
function name and its Postcondition. Sibling initializer
`initialize_ui_element_as__text_with__const_c_str` (ui_text.c:67) correctly performs the
`memcpy`; the `set` variant is missing that call.

### 1.3 `m_ui_element__typed_handler__text_box__alphanumeric`
**Defect class: `Boundary Condition` (off-by-one).**
The filter uses strict inequalities (`symbol > '0' && symbol < '9'`, etc.), which
reject the boundary characters of every range: `0`, `9`, `a`, `z`, `A`, `Z`. Only the
interior characters are accepted. Sibling
`m_ui_element__typed_handler__text_box__numeric` correctly uses inclusive bounds
(`symbol < '0' || symbol > '9'`). Correct form:
`symbol >= '0' && symbol <= '9'` (and the two letter ranges).

### 1.4 `clear_c_str_of__ui_text` (via `clear_c_str_of__ui_text_box`)
**Defect class: `Representation Invariant` violation / `State Desync`.**
The callee zeroes the buffer but does **not** reset
`index_of__cursor_in__char_buffer` to 0. The buffer content and cursor position become
inconsistent: a subsequent `append_symbol_into__ui_text` writes at the stale cursor,
leaving leading null bytes, and the "buffer full" guard reads a stale index. Secondary
gap: no null guard on `pM_char_buffer` before `memset` — `memset(NULL, 0, 0)` is
undefined behavior per C11 §7.24.6.1 (unenforced **Precondition**).

---

## 2. Impact Assessment

**Where the broken behavior is consumed:**
- **Test contract (already asserts correct behavior):**
  `tests/core/source/ui/test_suite_ui_ui_text_box.c` →
  `set_c_str_of__ui_text_box_with__const_c_str__updates_string` asserts the result equals
  `"world"` after a set. Because of defect 1.2 the buffer is all-zero, so this test
  currently **fails**; it encodes the intended contract and will pass once the `memcpy`
  is restored. (Note: this test passes `0` as `p_ui_manager` with a TODO comment.)
- **Downstream readers of the buffer/cursor:**
  - `get_p_const_c_str_text_of__ui_text` (ui_text.h:95) returns the raw
    `pM_char_buffer` + `size_of__char_buffer`. For set/insert/clear it will now reflect
    correct content instead of a zeroed/truncated buffer.
  - `append_symbol_into__ui_text` (ui_text.c:238) and the backspace special-symbol handler
    key off `index_of__cursor_in__char_buffer`. The clear cursor-reset fix (1.4) restores
    the invariant these already *assume*; it changes where the next append lands (from a
    stale index to 0). This is a correction of a desync, not a new contract.

**Assumptions invalidated by correcting the behavior:**
- **1.2 (set):** Any consumer that had adapted to "set yields an empty buffer" would be
  relying on the bug. No such production caller was found in the surveyed `core`/`nds`
  UI files — the broken behavior is not yet a de facto contract.
- **1.1 (insert):** Switching `strncpy`→`memcpy` changes behavior only when the source
  has embedded nulls (currently truncates early). No caller was found relying on that
  truncation.
- **1.4 (clear):** Any code that appends *after* a clear currently tolerates leading nulls
  and a stale cursor; after the fix the cursor is reset to 0, changing write position.
  No caller was found depending on the stale-cursor behavior.

**External blast radius:** A targeted survey of the game UI (`nds/source/ui/**`) and core
UI (`core/source/ui/**`) found **no production callers** of these four functions — they are
currently under-utilized. The only in-tree consumer asserting on them is the test suite
above. This keeps the fix cheap and low-risk.

---

## 3. Resolution Assessment

The fix is localized to two source files (`core/source/ui/ui_text.c` and
`core/source/ui/ui_text_box.c`). The public wrappers in `ui_text_box.h` are unchanged
(they are correct pass-throughs); no signature changes propagate to callers.

### 3.1 `insert_c_str_into__ui_text` (ui_text.c:271)
- Replace the `strncpy(...)` with `memcpy(p_ui_text->pM_char_buffer + index_to__insert_at,
  p_text__const_c_str, clamp)` to match the `append` sibling and honor the byte-count
  semantic. Keep the existing `clamp = min(size_of__text, size - index)` and the
  cursor advance `index + clamp`.
- Add a **Precondition** guard on `p_text__const_c_str` (assert non-null / early return)
  to remove the undefined-behavior path.
- Callers: no change. Tests: see §4 (equivalence + embedded-null cases).

### 3.2 `set_c_str_of__ui_text_with__const_c_str` (ui_text.c:166)
- After the allocation/`memset`, add the missing
  `memcpy(p_ui_text->pM_char_buffer, p_text__const_c_str, size_of__text)` (mirroring
  `initialize_ui_element_as__text_with__const_c_str`, ui_text.c:67). Add a null guard on
  `p_text__const_c_str`.
- Callers: no change. The existing test
  `set_c_str_of__ui_text_box_with__const_c_str__updates_string` will now pass; also resolve
  its `0`-manager TODO by passing a valid `UI_Manager`.

### 3.3 `m_ui_element__typed_handler__text_box__alphanumeric` (ui_text_box.c:208)
- Change the three ranges to inclusive bounds:
  `(symbol >= '0' && symbol <= '9') || (symbol >= 'a' && symbol <= 'z') ||
  (symbol >= 'A' && symbol <= 'Z')`. No caller/handler-registration change.

### 3.4 `clear_c_str_of__ui_text` (ui_text.c:217)
- After the `memset`, reset `p_ui_text->index_of__cursor_in__char_buffer = 0` so the
  buffer and cursor are a consistent **Representation Invariant**.
- Guard the `memset` against a null/zero buffer (`if (pM_char_buffer && size > 0)`) to
  remove the undefined-behavior path.
- Callers: no change.

**Phasing:** Not required. Each fix is independent, small, and confined to the UI text
module; they can land as one change or as four independent commits.

---

## 4. Test Verification Checklist

**Existing tests:**
- `test_suite_ui_ui_text_box.c :: set_c_str_of__ui_text_box_with__const_c_str__updates_string`
  asserts **correct** (post-fix) behavior and currently **fails**; the fix makes it pass.
  Update its `0`-manager placeholder to a valid `UI_Manager`. No assertion needs weakening.
- `test_suite_ui_ui_text.c` has **no** coverage for `insert`, `set`, or `clear`; these are
  untested callees — new tests are required.

**New tests (terminology-based):**
- **1.1 insert** — `Equivalence Check`: for a source with no embedded nulls, `insert` at a
  given index must produce the same buffer as an equivalent `append`/`memcpy`; add an
  embedded-null source case asserting exactly `clamp` bytes are copied and the cursor
  advances by `clamp`. **Fuzzing** of `index_to__insert_at` / `size_of__text` around buffer
  boundaries (in-bounds, == size, > size) to confirm the out-of-bounds early-return and no
  underflow.
- **1.2 set** — `Round Trip Check`: set a string, read it back via
  `get_p_const_c_str_text_of__ui_text`, assert equality; repeat with a second value to
  confirm reallocation + copy. Edge: allocation-failure path leaves `size = 0` / null buffer.
- **1.3 alphanumeric** — `Property Based Testing`: for every `unsigned char`, the handler
  appends iff the value is in `[0-9] ∪ [a-z] ∪ [A-Z]`; explicitly assert the six boundary
  characters (`0,9,a,z,A,Z`) are accepted and specials/symbols are rejected.
- **1.4 clear** — `Round Trip Check`: populate → clear → assert buffer all-zero **and**
  cursor == 0; then append and assert the symbol lands at index 0 (no leading nulls). Edge:
  clear on a null/zero buffer is a safe no-op.

**Test blast radius: Low.** One existing test is corrected (not invalidated), and new cases
are additive. No phased test migration is needed.

---

## 5. Blast Radius Summary

- **Files changed:** 2 source files (`core/source/ui/ui_text.c`,
  `core/source/ui/ui_text_box.c`) + the UI text test files. The `ui_text_box.h` wrappers and
  all public signatures are unchanged.
- **Behavior-preserving for current callers?** Yes — no production caller was found relying
  on the broken behavior, so the corrections introduce no regression for existing code.
- **De facto contracts invalidated:** None. The only in-tree assertion is the test that
  already encodes the *intended* contract (currently failing).
- **Phased approach needed:** No — fixes are independent and localized to one module.
- **Overall blast radius: Low.**
