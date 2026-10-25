# Planning: tile_logic_record.h — Incorrect Modules

**Review source:** `agents/core/review/include/world/tile_logic_record.h/incorrect_modules.md`

**Source files reviewed (read-only):**
- `core/include/world/tile_logic_record.h` (flagged function at lines 52-58)
- `core/include/types/implemented/world/tile_logic_record.h` (`Tile_Logic_Record` layout)
- `core/include/defines.h` (`Tile_Logic_Flags__u16`, `TILE_LOGIC_FLAG__*` constants)
- `core/include/world/tile_logic_context.h` (sole in-repo includer of the helper header)
- `tests/core/source/world/test_suite_world_tile_logic_context.c`, `tests/core/source/world/test_suite_world_tile_logic_table.c` (no references found)

---

## 1. Problem Identification

**`set_tile_logic_record_as__NOT_sight_blocking`** (`core/include/world/tile_logic_record.h`, lines 52-58) — **Incorrect**

- **Type mismatch on return (core defect).** The function declares a `bool` return
  type, but the returned expression
  `p_tile_logic_record->tile_logic_flags__u8 &= ~TILE_LOGIC_FLAG__IS_SIGHT_BLOCKING`
  evaluates to `uint16_t` (the field is typed `Tile_Logic_Flags__u16`). The implicit
  conversion to `_Bool` is a **Non-Injective Translation**: any flag word with a
  non-zero value outside the cleared bit collapses to `true`, destroying the
  modified flag word. The documented Postcondition ("returns the modified
  tile_logic_flags__u8 value") is therefore not satisfiable by the declared
  signature — a **Translation Gap** between contract and implementation.
- **Surface-form leakage (secondary, noted for awareness).** The field is named
  `tile_logic_flags__u8` but is typed `Tile_Logic_Flags__u16` (`uint16_t`). The name
  suffix contradicts the actual width, which is what makes the `bool`/`uint16_t`
  mismatch look plausible at a glance.
- **Pattern replication (DRY concern).** The identical `bool`-returns-`uint16_t`
  pattern appears in all other setters in this file (`set_tile_logic_record_as__unpassable`,
  `set_tile_logic_record_as__passable`, `set_tile_logic_record_as__sight_blocking`,
  `set_tile_logic_record_as__without_ground`, `set_tile_logic_record_as__with_ground`).
  Only the sight-blocking setter was flagged in the review; siblings are a follow-up.

The bit-clearing logic itself is correct: `&= ~FLAG` clears the
`TILE_LOGIC_FLAG__IS_SIGHT_BLOCKING` bit and preserves all other bits (Frame
Condition holds); the defect is purely in the declared return type.

## 2. Impact Assessment

Call-site survey of `core/include`, `core/source`, `examples/`, and `tests/`:

- **No in-repo callers** of `set_tile_logic_record_as__NOT_sight_blocking` were
  found (checked all of `core/source/world/*.c`, `core/source/world/implemented/*.c`,
  `core/source/raycast/ray.c`, example template files, and the world test suites).
- The helper header is included only by `core/include/world/tile_logic_context.h`;
  other world headers (`tile_logic_table.h`, `tile.h`) do not include it. As a
  `static inline` function with no users, it compiles to nothing today.
- **No de facto contract is relied upon in-repo.** No caller consumes the return
  value, so the current truncating `bool` behavior is not coupled into any
  existing logic — correcting it invalidates no in-repo assumption.

How a fix interacts with surrounding code:

- Changing the declared return type from `bool` to `Tile_Logic_Flags__u16` is
  **behavior-preserving** for any caller that ignores the return value (the
  mutation side effect is unchanged). Any *hypothetical external* caller assigning
  the result to a `bool` would observe a semantic change: previously truncated
  (0/1), it would receive the full flag word. This is the intended correction
  (Faithful, non-lossy return), but it must be announced if this header is consumed
  outside this repository.
- The sibling setters share the same signature defect; leaving them `bool` while
  fixing one setter makes the file internally inconsistent (violates DRY and the
  file's implicit **Type Invariant** that all setters have one return convention).
- The `__u8`-named / `u16`-typed field is part of the `Tile_Logic_Record` layout,
  which is a **Single Source of Truth** for tile logic state (potentially
  serialized as raw bytes). Renaming the member is cosmetic and layout-neutral,
  but touches every accessor in this header and any consumer spelling out the
  field name — broader than this review's scope.

## 3. Resolution Assessment

### Step 1 — Fix the flagged function (required)

In `core/include/world/tile_logic_record.h`, change the signature of
`set_tile_logic_record_as__NOT_sight_blocking` from `bool` to
`Tile_Logic_Flags__u16`:

```c
static inline
Tile_Logic_Flags__u16 set_tile_logic_record_as__NOT_sight_blocking(
        Tile_Logic_Record *p_tile_logic_record) {
    return p_tile_logic_record
        ->tile_logic_flags__u8 &=
        ~TILE_LOGIC_FLAG__IS_SIGHT_BLOCKING
        ;
}
```

- The body is unchanged; the declared type now matches the expression type,
  satisfying Postcondition 3 without implicit conversion.
- **Callers:** none in-repo need updating.
- **Documentation:** update the review's contract language if it is carried into
  any doc comments; no `defines.h` or struct changes required.

### Step 2 — Align sibling setters (recommended follow-up, same file)

Apply the identical return-type correction to the other five setters in this file
so the header has a single, consistent return convention (DRY; removes the
replicated Non-Injective Translation). Since no caller consumes any setter's
return value, this is behavior-preserving and can be done in the same change as
Step 1. The `is_*` getters already return `bool` from a `&` expression — that
truncation is the *intended* boolean answer and should be left as-is.

### Step 3 — Field-name correction (optional, deferred)

Rename `tile_logic_flags__u8` → `tile_logic_flags__u16` in
`core/include/types/implemented/world/tile_logic_record.h`, `core/include/defines.h`
(embedded default struct), and every accessor in `tile_logic_record.h`. This is a
layout-neutral refactor that removes the Surface-form leakage which masked the
original defect. Defer unless a rename pass is already planned: it widens the
change surface to any consumer naming the field.

### Phasing

Not required for Step 1 (single header, zero callers). Step 2 may ship with Step 1.
Step 3 should be a separate change if done at all.

## 4. Test Verification Checklist

- **Existing tests:** None reference the record helpers —
  `tests/core/source/world/test_suite_world_tile_logic_context.c` and
  `test_suite_world_tile_logic_table.c` contain no occurrences of
  `tile_logic_record` / `set_tile_logic_record_as__`. No existing assertions are
  invalidated by the fix.
- **New tests needed (none exist for this header today):**
  - **Round Trip Check:** set flag → clear flag (`NOT_sight_blocking`) → verify the
    flag word returns to its pre-set value; then verify the return value equals
    `p_tile_logic_record->tile_logic_flags__u8` after each call.
  - **Property Based Testing:** for arbitrary `Tile_Logic_Flags__u16` inputs,
    assert the **Invariant**: after the call, `IS_SIGHT_BLOCKING` is clear and all
    other bits (including `RESERVED_*`/`CUSTOM_*`) are unchanged; assert the
    returned value is bit-identical to the field (catches truncation regressions).
  - **Boundary Condition cases:** flag word `0`, all-16-bits-set, and
    `IS_SIGHT_BLOCKING`-only.
  - **Lint Gate:** compile this header under `-Wconversion -Werror` in the test
    build so any future implicit narrowing on these setters is rejected at build
    time (Static Analysis guard).
  - **Mutation Testing** (optional, low priority): flip `&= ~FLAG` to `|= FLAG` or
    drop the `~`; confirm the new property test fails.

## 5. Blast Radius Summary

- **Files changed:** 1 (`core/include/world/tile_logic_record.h`) for Step 1;
  still 1 file if Step 2 ships together. Step 3 (if adopted) additionally touches
  `core/include/types/implemented/world/tile_logic_record.h` and
  `core/include/defines.h`.
- **Behavior-preserving for current callers:** Yes — zero in-repo callers; the
  mutation side effect is unchanged, only the declared (and now actually returned)
  type of an unused return value changes.
- **Phased approach needed:** No.
- **De facto contracts invalidated:** None in-repo. The only externally visible
  change is that the return value becomes the full `uint16_t` flag word rather
  than a truncated `bool`; flag this in any change note for out-of-repo consumers.
