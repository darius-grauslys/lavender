# Planning: ui_slider.h — Incorrect Modules

**Review source:** `agents/core/review/include/ui/ui_slider.h/incorrect_modules.md`

**Source files reviewed (read-only):**
- `core/include/ui/ui_slider.h`
- `core/source/ui/ui_slider.c`
- `tests/core/source/ui/test_suite_ui_ui_slider.c`

---

## 1. Problem Identification

Four functions were flagged **Incorrect**. Three of them share a single root cause: the
slider's two snap axes disagree about what `slider__distance__u32` *means*, violating a
single **Representation Invariant** and producing a **Mode Confusion** between X and Y
branches. The fourth is an isolated missing-validation defect.

### 1.1 `m_ui_slider__dragged_handler__default` (`core/source/ui/ui_slider.c`)
- **Sign error (Y axis).** The Y branch computes
  `clamp(-cursor.y + hitbox.y + height/2, 0, height)`, i.e. the *negation* of the X pattern
  `clamp(cursor.x - hitbox.x + width/2, 0, width)`. As the cursor moves **down**, the stored
  distance **decreases**. For a vertical slider the value is therefore **inverted** relative to
  the horizontal convention. This is the source of the downstream corruption.
- **Dead code.** `spanning_length__3i32` (lines 95–97) is computed via
  `get_ui_slider__spanning_length` and never used.
- **Implicit conversions.** `Quantity__u32` → `i32` in the `clamp__i32` call, and `i32` → `u32`
  on assignment to `slider__distance__u32`. Safe for realistic sizes but a type mismatch.

### 1.2 `m_ui_slider__transformed_handler__default` (`core/source/ui/ui_slider.c`)
- **Sign error (X axis).** The X branch offsets the thumb by
  `distance + (width >> 1)`; the Y branch offsets by `(height >> 1) - distance`. The two axes use
  **opposite offset formulas**. The X formula is wrong: at `distance = 0` it places the thumb at
  the *right* edge, and at `distance = width` it pushes it *beyond* the track.
- **Coupling note.** The Y branch's `(height/2 - distance)` was written to *compensate* for the
  dragged handler's inverted Y distance. The two sign errors form a matched pair that yields
  approximately-correct **visual** thumb placement while leaving `slider__distance__u32`
  semantically wrong — a classic **State Desync**: the internal state and its consumers disagree
  on the value's meaning.
- **Implicit unsigned arithmetic.** Both branches perform unsigned `+`/`-` on `u32` then pass to
  an `i32` parameter; the Y underflow case is implementation-defined per C11 §6.3.1.3.

### 1.3 `get_percentage_i32F20_from__ui_slider` (`core/include/ui/ui_slider.h`, inline)
- **Division-by-zero UB.** The divisor is `get_width_from__p_ui_element` /
  `get_height_from__p_ui_element`; a missing or zero-sized hitbox yields divisor `0` (in debug,
  a null hitbox returns `0`). No guard exists. This is an unenforced **Precondition** / missing
  **Boundary Condition**.
- **Mixed signed/unsigned division.** The `i32F20` (`int32_t`) dividend is implicitly promoted to
  `uint32_t` before dividing by a `Quantity__u32`. If the dividend is negative (large distance
  overflowing the 20-bit shift), the quotient is silently wrong. Fragile and error-prone.
- **Implicit u32→i32 conversion** feeding `i32_to__i32F20(distance)`.
- **Inherited inversion.** Because it reads `slider__distance__u32`, vertical sliders report an
  **inverted** percentage (consequence of 1.1).

### 1.4 `get_ui_slider__spanning_length` (`core/include/ui/ui_slider.h`, inline)
- **Missing kind validation.** It reads the union member `slider__spanning_length__3i32` with no
  check that the element is `UI_Element_Kind__Slider`; on a non-slider this is **undefined
  behavior**. Every sibling inline function in this header performs an
  `is_ui_element_of__this_kind` debug check — this one does not (the source carries a
  `//TODO: validate ui_element enum`). An inconsistent, unenforced **Precondition**.

---

## 2. Impact Assessment

All four defects live inside the slider module (`ui_slider.h` / `ui_slider.c`). The coupling is a
short internal chain, but it threads through every consumer of `slider__distance__u32`.

**Data-flow / coupling graph (all within the slider module):**
```
m_ui_slider__dragged_handler__default  ──writes──▶  slider__distance__u32
        │                                                        │
        └─ calls ─▶ m_ui_slider__transformed_handler__default ◀──┤ (reader: thumb placement)
                                                                 ├─▶ get_percentage_i32F20_from__ui_slider (reader)
                                                                 │        │
                                                                 │        └─▶ get_offset_from__ui_slider_percentage
                                                                 │                 │
                                                                 └──────────────────┴─▶ m_ui_slider__dragged_handler__gfx_window__default (positions owned window)

get_ui_slider__spanning_length ──read by──▶ dragged_handler__default, dragged_handler__gfx_window__default
```

**Who relies on the broken behavior:**
- `get_offset_from__ui_slider_percentage` (inline, same header) consumes the percentage and is
  called by `m_ui_slider__dragged_handler__gfx_window__default` to position the slider's owned
  graphics window. For **vertical** sliders this currently uses the inverted distance, so the
  owned window is mis-positioned. Fixing 1.1 corrects it; any code that "worked around" the
  inversion would break.
- `m_ui_slider__transformed_handler__default` is the **de facto contract** for thumb rendering.
  Its Y branch was tuned to cancel the dragged handler's inversion. Correcting the convention in
  1.1 *and* 1.2 together keeps the Y-axis thumb visually identical (the two sign changes cancel)
  while fixing the X-axis thumb from wrong → correct. **The two must change as a unit** or the
  visual regression will be introduced on one axis.
- `get_ui_slider__spanning_length` is read by both dragged handlers; the dead read in
  `dragged_handler__default` (1.1) is safe to remove without affecting behavior.

**Assumptions invalidated by the correction:**
- The implicit contract that "for a Y slider, `slider__distance__u32` increases upward" is
  currently true and will be **reversed** once the X/Y convention is unified (distance increases
  from the start edge: left for X, top for Y). Any external application/scene code that reads
  `get_percentage_i32F20_from__ui_slider` on a vertical slider and compensated for the inversion
  will need updating. No such consumer was found inside `core/source` or `core/include`; the risk
  is confined to out-of-tree/application code, but it should be called out before the fix lands.
- The X-axis thumb position is a visible behavior change (bug → correct), not a silent refactor.

---

## 3. Resolution Assessment

**Goal: establish one Representation Invariant for `slider__distance__u32`** — distance measured
from the *start* edge (left for X, top for Y), increasing toward the *end* edge, clamped to
`[0, dim]`. Both the writer (dragged) and every reader (transformed, percentage, offset) must
agree. This removes the **Mode Confusion** and makes the X/Y branches a single shared formula
(**DRY**).

### 3.1 Fix the sign convention (dragged + transformed — change as a unit)
- `m_ui_slider__dragged_handler__default`: change the Y branch to
  `clamp(cursor.y - hitbox.y + (height >> 1), 0, height)` to match the X pattern
  `cursor.x - hitbox.x + (width >> 1)`. Remove the dead `spanning_length__3i32` computation.
- `m_ui_slider__transformed_handler__default`: unify **both** branches to
  `distance - (dim >> 1)` (X: `distance - width/2`, Y: `distance - height/2`).
- **Callers:** No signature changes. Y-axis thumb visuals are preserved (net offset unchanged);
  X-axis thumb visuals change from incorrect to correct.
- **Docs:** Update the spec (`docs/specs/core/ui/ui_slider.h.spec.md`) to state the unified
  distance invariant explicitly.

### 3.2 Harden `get_percentage_i32F20_from__ui_slider`
- Add a **Boundary Condition** guard: if the selected span dimension is `0`, return `0` (no
  division). This closes the division-by-zero UB for missing/zero-size hitboxes.
- Make the division **explicitly signed**: cast the divisor to `i32` (or compute in a signed type)
  so the dividend is not promoted to `uint32_t`. Keep the existing debug kind check.
- **Callers:** Behavior of `get_offset_from__ui_slider_percentage` and
  `m_ui_slider__dragged_handler__gfx_window__default` becomes correct for vertical sliders; no
  signature change.

### 3.3 Validate `get_ui_slider__spanning_length`
- Add the same `is_ui_element_of__this_kind(p_ui_element, UI_Element_Kind__Slider)` debug check
  used by its siblings (log + return a zeroed `Vector__3i32` on mismatch), removing the
  `//TODO`. Aligns the accessor with the file's **Precondition** convention and eliminates the
  union-access UB.
- **Callers:** No change for valid sliders; only the invalid-kind path (previously UB) is now
  handled.

### Phasing (recommended)
1. **Phase A — sign convention:** landed atomically across `dragged_handler__default` and
   `transformed_handler__default` (they are a matched pair; partial application regresses an axis).
2. **Phase B — guards/validation:** divisor guard in `get_percentage…`, kind check in
   `get_ui_slider__spanning_length`. Independent of Phase A.
3. **Phase C — tests + spec:** add the tests in §4 and update the spec's stated invariant.

---

## 4. Test Verification Checklist

**Existing suite** (`tests/core/source/ui/test_suite_ui_ui_slider.c`) covers only:
`initialize…` (kind, snap flag, spanning length, handlers), `get_ui_slider__spanning_length`, and
`set_ui_slider_at__this_distance_u32`. It has **no coverage** of the dragged handler, transformed
handler, or percentage/offset path — so no existing assertion encodes the broken behavior. The
`sets_spanning_length` test passes regardless of the missing validation. **No existing assertion is
invalidated by the fix**, but a large verification gap must be closed.

**New tests required:**
- **Property Based Testing** — for both axes, assert the **Invariant**: `0 ≤ slider__distance__u32 ≤ dim`
  and `0 ≤ percentage ≤ 1.0`; distance increases monotonically from the start edge to the end edge.
- **Equivalence Check** — X and Y branches are symmetric: feeding an equivalent normalized cursor
  position into an X slider vs a Y slider yields the same `percentage`/`offset`. This directly
  detects any residual **Mode Confusion**.
- **Round Trip Check** — `set_ui_slider_at__this_distance_u32(d)` → `get_percentage…` →
  `get_offset_from__ui_slider_percentage(range)` → reposition, and confirm the thumb lands at the
  expected edge for `d = 0`, `d = dim/2`, `d = dim`.
- **Fuzzing** / boundary — zero-width/zero-height hitbox (divisor guard), missing hitbox component
  (early-return + disable path), and distances pinned to the clamp edges.
- **Mutation Testing** — run the new suite against sign-flipped variants to confirm the tests would
  catch a regression in either axis's sign.

**Blast radius of test changes:** Low–Medium. Add new test cases to the existing suite (and its
`.h`); no existing assertions need editing.

---

## 5. Blast Radius Summary

- **Files changed:** `core/source/ui/ui_slider.c`, `core/include/ui/ui_slider.h`,
  `tests/core/source/ui/test_suite_ui_ui_slider.c` (+ its `.h`), and the spec md. ~3–4 files, all
  in the slider module. No out-of-tree core source references the broken functions.
- **Behavior-preserving?** Y-axis thumb visuals: preserved. X-axis thumb visuals: changed (bug →
  correct). Y-axis percentage/offset: changed (inverted → correct). These are intentional corrections,
  not silent refactors.
- **De facto contract invalidated:** the implicit "vertical slider distance increases upward"
  convention. Any application code compensating for it must be re-checked; none found in-tree.
- **Phased approach needed:** Yes — the dragged/transformed sign fix must land atomically (Phase A);
  guards/validation (Phase B) and tests/spec (Phase C) can follow independently.
