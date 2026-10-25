# Planning: ui_text.h — Incorrect Modules

**Review source:** `agents/core/review/include/ui/ui_text.h/incorrect_modules.md`

**Source files reviewed (read-only):**
- `core/include/ui/ui_text.h`
- `core/source/ui/ui_text.c`
- `tests/core/source/ui/test_suite_ui_ui_text.c`

**Incorrect functions flagged (7):**
`append_c_str_into__ui_text`, `buffer_c_str_of__ui_text`,
`m_ui_element__transformed_handler__text__centered`,
`set_c_str_of__ui_text_with__const_c_str`, `clear_c_str_of__ui_text`,
`set_cursor_of__ui_text`, `insert_c_str_into__ui_text`

---

## 1. Problem Identification

All seven operate on the same `UI_Text` union members — the
Representation Invariant is that `pM_char_buffer` (non-null iff allocated),
`size_of__char_buffer` (allocated capacity), and
`index_of__cursor_in__char_buffer` (write/read head) stay mutually consistent.
Each defect breaks a distinct facet of that invariant or of the function's
semantic contract.

- **append_c_str_into__ui_text** — Postcondition violation / State Desync.
  It `memcpy`s `clamp__u32` bytes at the cursor but never advances
  `index_of__cursor_in__char_buffer`. Siblings `append_symbol_into__ui_text`
  (post-increments) and `insert_c_str_into__ui_text` (sets cursor to end of
  copy) both advance the head. Repeated appends overwrite the same region. It
  also lacks the full-buffer guard present in `append_symbol_into__ui_text`, so
  a cursor > size causes unsigned underflow in `size_of__char_buffer - cursor`.

- **buffer_c_str_of__ui_text** — Precondition gap / State Desync.
  Unlike its siblings (`initialize_..._with__const_c_str`,
  `initialize_..._with__buffer_size`, `set_c_str_of__ui_text_with__const_c_str`),
  it does not check the `malloc` result. On allocation failure it sets
  `size_of__char_buffer = size_of__text` while `pM_char_buffer == NULL` and then
  `memset`s a null pointer (undefined behavior). The size field and pointer
  desync.

- **set_c_str_of__ui_text_with__const_c_str** — Translation Gap / Stub-real
  divergence. It allocates and zeroes the buffer but never copies
  `p_text__const_c_str`; the parameter is unused. The sibling initializer
  correctly `memcpy`s the source, so this function's output is an empty buffer
  rather than the requested text.

- **clear_c_str_of__ui_text** — Precondition gap / Boundary Condition.
  It `memset`s `pM_char_buffer` with `size_of__char_buffer` bytes without a
  null check. An element initialized with a null buffer
  (`initialize_..._with__pM_c_str`, null source) triggers undefined behavior.

- **set_cursor_of__ui_text** — Boundary Condition / Representation Invariant.
  When `size_of__char_buffer == 0`, the clamp expression
  `size_of__char_buffer - 1` underflows to `UINT32_MAX`, placing the cursor far
  out of range. Downstream, `append_c_str_into__ui_text`'s
  `size_of__char_buffer - cursor` then also underflows, risking an out-of-bounds
  copy.

- **insert_c_str_into__ui_text** — Surface-form leakage / State Desync.
  (a) It uses `strncpy`, which stops at the first source null and pads the
  remainder with nulls, so a `size_of__text` larger than the real string
  overwrites trailing content with nulls. (b) The name "insert" implies a shift
  of existing content, but it overwrites in place. (c) It advances the cursor by
  the full `clamp`, not the actual bytes copied — cursor and content desync.

- **m_ui_element__transformed_handler__text__centered** — Mode Confusion /
  precision loss. (a) The y offset is negated
  (`-(height/2 - font_height/2)`), the opposite sign of the correctly-signed x
  offset, so text is placed outside the hitbox rather than centered. (b) The x
  offset computes `char_buffer_size * (font_max_width >> 1)` (divide-before-
  multiply), truncating odd font widths. It also dereferences `typer.p_font`
  with no null check.

## 2. Impact Assessment

**Direct caller surface (low within shipped code).** A survey of `./include` and
`./source` shows none of the seven plain `_ui_text` functions is called by a
shipped module: `ui_text_box.c` uses its own `_ui_text_box` variants (not these),
and `scene`, `ui_window`, `ui_manager`, `ui_element`, and `input` modules do not
reference them. They are exported API in `ui_text.h` (spec-defined surface) and
are exercised only by the test suite. Blast radius among current callers is
therefore small, but each is a **de facto contract** for any present or future
consumer of the text-element API.

**Coupled consumers inside `ui_text.c` (medium).** The defects are not isolated;
they share the `UI_Text` buffer/cursor representation:
- `get_p_const_c_str_text_of__ui_text` returns `pM_char_buffer` and
  `size_of__char_buffer`. `buffer_c_str_of__ui_text`'s malloc-failure path
  (null pointer + non-zero size) makes this accessor return a null pointer with
  a bogus size — a State Desync that poisons every reader.
- `m_ui_element__compose_handler__text` renders via
  `put_c_string_in__typer(pM_char_buffer, size_of__char_buffer)`. Buffer
  corruption from the `append`/`set_c_str`/`insert` bugs and the null-pointer
  paths flow directly into composition/rendering.
- The cursor head is shared by `set_cursor_of__ui_text`,
  `append_c_str_into__ui_text`, and `insert_c_str_into__ui_text`. Fixing the
  zero-size underflow in `set_cursor` is a precondition for the
  `size - cursor` subtraction in `append` to be safe; these fixes are coupled.

**Assumptions invalidated by the fixes.**
- Correcting `append_c_str_into__ui_text` to advance the cursor changes its
  observable state: callers who (implicitly) relied on the cursor staying put —
  e.g. re-appending at a fixed offset — would see sequential behavior instead.
  This is the intended contract, but it is a behavior change for any such caller.
- Correcting `set_c_str_of__ui_text_with__const_c_str` to actually copy the
  source changes output from empty-buffer to populated-buffer; any consumer that
  (workaround-style) re-wrote the buffer after calling it would now double-write.
- Correcting `insert_c_str_into__ui_text` to `memcpy` (no null padding) and to
  advance by actual bytes copied changes both buffer contents and cursor
  postconditions.

## 3. Resolution Assessment

Fix each function to satisfy its stated Pre/Postconditions; keep the shared
representation invariant intact. No signature changes are required — all fixes
are body-local, so callers do not need updating unless a postcondition change is
relied upon (see §2).

1. **append_c_str_into__ui_text** — Add the full-buffer guard (mirror
   `append_symbol_into__ui_text`: early-return if `cursor >= size`). After the
   `memcpy`, advance `index_of__cursor_in__char_buffer += clamp__u32`. This
   makes the cursor a true write head and removes the underflow path.

2. **buffer_c_str_of__ui_text** — Add a `malloc` null check identical to the
   siblings: on failure set `size_of__char_buffer = 0`, log via `debug_error`,
   and return before the `memset`. Restores the pointer/size invariant.

3. **set_c_str_of__ui_text_with__const_c_str** — After allocation and zeroing,
   `memcpy(pM_char_buffer, p_text__const_c_str, size_of__text)` (as the
   initializer already does). Remove the ignored-parameter gap.

4. **clear_c_str_of__ui_text** — Guard `memset` with a null check on
   `pM_char_buffer` (and/or `size_of__char_buffer != 0`). No behavior change for
   valid buffers; removes the undefined-behavior path.

5. **set_cursor_of__ui_text** — Handle the zero-size boundary: if
   `size_of__char_buffer == 0`, set the cursor to `0`; otherwise keep the
   existing clamp (`min(requested, size - 1)`). Eliminates the underflow and
   protects downstream `append`.

6. **insert_c_str_into__ui_text** — Replace `strncpy` with `memcpy` over
   `clamp` (no null padding, consistent with `append`). Advance the cursor by
   the actual bytes written. Reconcile naming: either rename to reflect
   overwrite semantics or implement a true shift-insert; recommend aligning the
   name/contract to overwrite-with-clamp to match `append`, and documenting it.

7. **m_ui_element__transformed_handler__text__centered** — Drop the leading
   negation on the y offset so x and y use the same sign convention
   (`hitbox/2 - font/2`). Reorder x to multiply-before-shift
   (`(size_of__char_buffer * max_width) >> 1`). Add a null guard on
   `typer.p_font` (skip positioning if null).

**Phasing.** Items 1, 2, 4, 5 are safe, behavior-preserving-for-valid-input
hardening and can land first. Item 3 changes output content and item 6 changes
both content and cursor postconditions; item 7 changes on-screen placement.
Land the hardening batch first, then the semantic/behavior-change batch so each
is independently verifiable.

## 4. Test Verification Checklist

Existing suite (`tests/core/source/ui/test_suite_ui_ui_text.c`) covers only
initializers, the two accessors, and one `set_cursor` case
(`set_cursor_of__ui_text__sets_cursor_index`, in-range size-5/cursor-3). It
asserts correct behavior and is **not** invalidated by the fixes — the existing
`set_cursor` case stays green after the zero-size fix. Notably, the suite has
**no coverage** for `append_c_str_into`, `buffer_c_str_of`,
`clear_c_str_of`, `insert_c_str_into`, `set_c_str_of__..._const_c_str`, or the
centered handler. New tests are required.

Proposed additions (terminology-based):
- **append_c_str_into__ui_text** — *Round Trip Check*: append twice, assert the
  buffer holds concatenated content and the cursor advanced to the end.
  *Boundary Condition*: append past capacity is clamped; full-buffer early-return.
- **buffer_c_str_of__ui_text** — *Property Based Testing* on the invariant
  `pM_char_buffer == NULL ⇔ size_of__char_buffer == 0` across sizes; simulate
  allocation failure to assert no null-`memset` and size reset to 0.
- **set_c_str_of__ui_text_with__const_c_str** — *Equivalence Check*: buffer
  contents equal the source for `size_of__text` bytes (currently fails).
- **clear_c_str_of__ui_text** — *Boundary Condition*: null-buffer element does
  not crash; valid buffer is fully zeroed with size/pointer unchanged.
- **set_cursor_of__ui_text** — *Boundary Condition*: zero-size buffer yields
  cursor 0 (not `UINT32_MAX`); over-large request clamps to `size - 1`.
- **insert_c_str_into__ui_text** — *Round Trip Check*: no null padding past the
  real string; cursor equals actual bytes written, not the raw clamp.
- **m_ui_element__transformed_handler__text__centered** — *Golden-file Test* /
  *Equivalence Check* on computed position for a fixed font+hitbox; assert y
  offset sign matches x and odd-width fonts center without truncation bias; null
  `p_font` is a no-op.

**Test blast radius: Medium.** No existing assertions break, but ~7 new test
functions must be added. Recommend the same two-phase rollout as the fixes:
hardening tests first, then semantic tests.

## 5. Blast Radius Summary

- **Files changed:** 1 implementation file (`core/source/ui/ui_text.c`, all 7
  fixes are body-local); `core/include/ui/ui_text.h` only if the `insert`
  rename/contract is adopted (documentation/signature). No other `.c`/`.h` in
  `./include` or `./source` needs changes — no shipped module calls these
  functions.
- **Behavior-preserving for current callers?** Mostly yes. Hardening fixes
  (items 1-guard, 2, 4, 5) preserve valid-input behavior. Items 3 and 6 change
  observable output/cursor postconditions and item 7 changes placement; these are
  the intended contract but would invalidate any caller relying on the broken
  de facto behavior (none found in-tree).
- **Phased approach:** Yes — land the safe hardening batch, then the semantic
  batch, each independently testable.
- **De facto contracts invalidated:** The "cursor does not advance on append"
  and "set_c_str yields an empty buffer" behaviors are the only de facto
  contracts at risk; no in-tree consumer depends on them, so invalidation is
  contained to the API contract itself (and to future/text-box-style consumers).
