# Planning: ui_tile_map.h — Incorrect Modules

**Review source:** `agents/core/review/include/ui/ui_tile_map.h/incorrect_modules.md`

**Source files reviewed (read-only):**
- `core/include/ui/ui_tile_map.h`
- `core/source/ui/ui_tile_map.c`
- `tests/core/source/ui/test_suite_ui_ui_tile_map.c` (no coverage of this function)

---

## 1. Problem Identification

**Flagged:** `fill_ui_tile_map_in__this_region` (`core/source/ui/ui_tile_map.c:125`)
Correctness Verdict: **Incorrect**

- **Defect — off-by-one `Boundary Condition`.** The clip guards at lines 138 and 146 use a strict greater-than (`y > height_of__ui_tile_map`, `x > width_of__ui_tile_map`) instead of greater-or-equal. Valid indices are `x ∈ [0, W-1]` and `y ∈ [0, H-1]`; the `>` comparison lets `y == H` and `x == W` pass, so the write index `x + y * W` lands one past the last allocated element.
- **Postcondition violation.** This breaks postcondition #2 ("No tiles outside the valid map bounds are modified") and corrupts memory beyond the `p_ui_tile_data` array (a `UI_Tile_Raw` array of exactly `W * H` elements). This is undefined behavior whenever the region's right or bottom edge coincides with the map boundary.
- **`Mode Confusion` / non-consistent idiom.** The sibling `generate_ui_span_in__ui_tile_map` (lines 177, 190) correctly uses `>=`, and `fill_ui_tile_map` (lines 108, 112) correctly bounds its loops with `<`. The flagged function alone deviates from the established clip idiom.
- Note: the absence of null-pointer validation is consistent with the codebase pattern (validation is the caller's responsibility via `is_ui_tile_map__wrapper__valid`) and is **not** part of the flagged defect.

## 2. Impact Assessment

- **Data structure affected:** `p_ui_tile_map__wrapper->p_ui_tile_data`, allocated for exactly `W * H` elements. The out-of-bounds write corrupts adjacent heap memory past the tile array — a `Cascade Failure` risk for whatever allocation follows it (heap metadata or a neighboring object), not merely a wrong tile value.
- **Callers:** No callers were found in `core/source/ui/` (all UI modules) or `core/source/rendering/`, nor in `tests/core/source/ui/test_suite_ui_ui_tile_map.c`. The function is a public API declared in `core/include/ui/ui_tile_map.h`, so platform code (sdl/nds) or future callers could invoke it. Its blast radius is therefore **latent**, not active: the `Representation Invariant` (array size `W * H`) is silently violated only when a caller fills a region whose bottom/right edge aligns with the map boundary.
- **Assumptions invalidated by the fix:** The buggy behavior is **not** a de facto contract — it produces undefined behavior, so no correct caller can rely on it. Correcting the guard to `>=` changes observable behavior only in the previously-buggy boundary case: the extra out-of-bounds row/column write is removed and clipped. For regions strictly inside the map, behavior is unchanged (behavior-preserving / `Equivalence Check` safe).
- **Coupling:** The function is otherwise `Orthogonal` — it shares no hidden state with siblings beyond reading `width_of__ui_tile_map`/`height_of__ui_tile_map`. No other function reads the corrupted tail of `p_ui_tile_data`, so the fix has no cascading consumers to update.

## 3. Resolution Assessment

**Goal:** align the clip guards with their declared `Postcondition` and with the sibling idiom, enforcing the `Representation Invariant` that only indices `< W` / `< H` are written.

1. **Implementation change (minimal, `Conservative`):** in `core/source/ui/ui_tile_map.c`,
   - Line 138: `if (y > p_ui_tile_map__wrapper->height_of__ui_tile_map)` → `if (y >= p_ui_tile_map__wrapper->height_of__ui_tile_map)`
   - Line 146: `if (x > p_ui_tile_map__wrapper->width_of__ui_tile_map)` → `if (x >= p_ui_tile_map__wrapper->width_of__ui_tile_map)`

   This matches the exact idiom already used by `generate_ui_span_in__ui_tile_map` (`>=` + skip), keeping the loop structure and row-major indexing unchanged.
2. **Callers:** No caller updates required (no callers exist). The public signature in `core/include/ui/ui_tile_map.h` is unchanged, so no header edit is needed.
3. **Documentation / contract:** No doc change strictly required; the existing pre/post-conditions already describe the intended (correct) behavior, which the fix now satisfies. Optionally add an inline comment noting the boundary is clipped at `>=`.
4. **Test Verification Checklist:**
   - Existing tests: none reference this function, so no existing assertions are invalidated.
   - New tests needed (see `agents/terminologies/testing.md`):
     - **Boundary Condition** cases: region whose right edge is at `x == W` and bottom edge at `y == H`; assert the boundary tile is *not* written and, critically, that no write escapes the array. Run under an AddressSanitizer / heap-check build to convert the latent OOB into a hard test failure.
     - **Equivalence Check:** for a full-map region (`index_*__start = 0`, `width == W`, `height == H`), assert the result equals `fill_ui_tile_map`'s output.
     - **Property Based Testing:** for random regions, assert every written index satisfies `x < W && y < H` and no out-of-range index is touched (invariant verification).
     - **Round Trip Check:** fill a sub-region, then re-read the region and confirm values round-trip without disturbing tiles outside it.
   - Test blast radius: **Low** — additive only; no existing test changes.

## 4. Blast Radius Summary

- **Files changed:** 1 (`core/source/ui/ui_tile_map.c`), 2 lines. No header, caller, or platform changes required.
- **Behavior-preserving for current callers:** Yes — there are no current callers, and the fix only alters the previously-undefined boundary case.
- **Phased approach needed:** No. Single-function, two-character-per-line fix; safe to land in one step.
- **De facto contracts invalidated:** None. The removed behavior was undefined behavior, not a relied-upon contract.
