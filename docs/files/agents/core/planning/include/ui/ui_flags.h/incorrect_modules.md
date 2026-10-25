# Planning: ui_flags.h — Incorrect Modules

**Review source:** `agents/core/review/include/ui/ui_flags.h/incorrect_modules.md`

**Source files reviewed (read-only):**
- `core/include/ui/ui_flags.h`
- `core/include/defines.h` (SSOT for `UI_Flags__u16` typedef and `UI_FLAGS__BIT_*` constants)
- `core/source/ui/ui_element.c` (independent, duplicated flag accessors)
- `core/source/ui/ui_manager.c` (uses distinct `IS_DEALLOCATED_P` pointer-poison mechanism; not coupled to the flag bit)

---

## 1. Problem Identification

All four flagged functions share a single root cause: they reference
`UI_FLAGS__BIT_*` macros that are **never defined** in the constant SSOT
(`core/include/defines.h`). Because `ui_flags.h` declares these as
`static ... inline`, their bodies are still parsed on inclusion, so the
undefined identifier is a **compile-time error**, not a runtime one. This is a
**Translation Gap**: the declared semantic intent (query/set a specific flag bit)
is not backed by any defined constant, so the functions cannot fulfill their
contract and the header is un-includable as written.

The bit layout in `defines.h` (lines 1632–1650) confirms the gap:

| Bit | Constant | Status |
|-----|----------|--------|
| 0–6 | `IS_ENABLED` … `IS_USING__SPRITE_OR_UI_TILE_SPAN` | defined |
| **7** | *(none)* | **gap — intended for `IS_ALLOCATED`** |
| 8–11 | `RESERVED_0..3` | defined (reserved) |
| 12–15 | `CUSTOM_0..3` | defined (custom) |

Per-function:

- **`is_ui_flags__allocated`** — references undefined `UI_FLAGS__BIT_IS_ALLOCATED`;
  compile error. The `& mask → (bool)` idiom itself is correct.
- **`set_p_ui_flags__u8_as__allocated`** — references the same undefined
  `UI_FLAGS__BIT_IS_ALLOCATED`; compile error. The `|= mask` idiom is correct.
- **`set_p_ui_flags__u8_as__deallocated`** — references the same undefined
  `UI_FLAGS__BIT_IS_ALLOCATED`; compile error. The `&= ~mask` idiom is correct.
  Carries a `//TODO: move to private header` note (Information Hiding debt).
- **`is_ui_flags__needing_update`** — references undefined
  `UI_FLAGS__BIT_IS_NEEDING_UPDATE`; compile error. Unlike the allocated trio,
  this flag has **no corresponding setter anywhere** and **no free bit** in the
  `u16` (bits 8–15 are reserved/custom) — it was never fully integrated.

Secondary (non-blocking) issue across all functions: parameters are named
`ui_flags__u8` / `p_ui_flags__u8` but the declared type is `UI_Flags__u16`
(`uint16_t`). This is **Surface-form leakage** — a misleading name for a 16-bit
value. It does not affect correctness.

## 2. Impact Assessment

- **No live callers (orphaned header).** A project-wide survey found **no**
  translation unit that `#include`s `ui_flags.h`, and **no** test file references
  any of the four functions. The undefined macros therefore do not currently
  break the build — the header is isolated. Blast radius of the correctness fix
  is **low**.
- **No de facto contract on the missing bits.** `UI_FLAGS__BIT_IS_ALLOCATED` and
  `UI_FLAGS__BIT_IS_NEEDING_UPDATE` are referenced nowhere else in `./include` or
  `./source`. The "allocated" naming in `ui_manager.c` refers to a pool counter
  (`quantity_of__ui_elements__allocated`) and to the distinct
  `IS_DEALLOCATED_P` pointer-poison macro — **not** to this flag bit. There is no
  hidden coupling to invalidate.
- **Duplicated accessors (DRY / SSOT debt).** `core/source/ui/ui_element.c`
  re-implements the flag getters/setters inline against the `UI_Element.ui_flags`
  member using only the *defined* macros (`IS_ENABLED`, `IS_FOCUSED`,
  `IS_BEING_HELD`, etc.). It does **not** use `ui_flags.h`. Once `ui_flags.h` is
  made compilable, this duplication becomes a candidate for consolidation to a
  single source of truth — but that is an optional refactor, not required for the
  correctness fix.
- **Correcting behavior invalidates nothing.** Because the broken functions are
  unused, defining the missing macros (or removing the orphaned function) changes
  no observable behavior in any existing caller. The only "invalidation" is at the
  compile boundary of `ui_flags.h` itself, which no consumer currently crosses.

## 3. Resolution Assessment

Goal: bring `ui_flags.h` into alignment with its semantic intent by closing the
Translation Gap, restoring a valid **Representation Invariant** for the bit layout,
and keeping `defines.h` as the single source of truth for all bit constants.

### Step A — Define `UI_FLAGS__BIT_IS_ALLOCATED` (fixes 3 of 4 functions)
- Add to `core/include/defines.h`, filling the existing gap:
  ```c
  #define UI_FLAGS__BIT_IS_ALLOCATED BIT(7)
  ```
- Placing it at bit 7 preserves every existing bit assignment (0–6, 8–15), so the
  change is **non-breaking** for all current consumers. This resolves
  `is_ui_flags__allocated`, `set_p_ui_flags__u8_as__allocated`, and
  `set_p_ui_flags__u8_as__deallocated` in one edit. No caller updates required.

### Step B — Resolve `is_ui_flags__needing_update` (the orphaned flag)
Two mutually exclusive options; recommend **(B1)**:
- **(B1) Remove the function (conservative, recommended).** It has no setter, no
  usage anywhere, and no free bit in the `u16`. Deleting it removes a dangling,
  non-integrable interface. If the "needing update" concept is genuinely wanted in
  the future, reintroduce it together with its setter and an explicit bit allocation
  (which would require either repurposing a `RESERVED_*` bit or widening the type —
  both out of scope now).
- **(B2) Assign a bit and add the missing setter.** Only if the feature is in scope:
  repurpose one `UI_FLAGS__BIT_RESERVED_*` slot (documenting the promotion from
  reserved to active) **or** widen `UI_Flags__u16`, then add a matching
  `set_p_ui_flags__u8_as__needing_update`. Higher blast radius; not recommended now.

### Step C — Naming consistency (optional, cosmetic)
- Rename the misleading `__u8`-suffixed parameters/names to `__u16` to match the
  `UI_Flags__u16` type, eliminating the Surface-form leakage. Purely a readability
  fix; do **not** bundle with Step A/B if you want the correctness change isolated.

### Step D — Hygiene / Information Hiding (optional follow-up)
- Honor the `//TODO: move to private header` on `set_p_ui_flags__u8_as__deallocated`
  by relocating it to a private header once the public interface is settled.
- DRY/SSOT: optionally route `ui_element.c`'s inline accessors through `ui_flags.h`
  now that the header compiles, and wire `ui_flags.h` into the UI umbrella header.
  This must be gated behind an **Equivalence Check** (see below) to confirm
  behavior preservation before it is considered a correctness fix.

**Phasing:** Step A + Step B are the correctness fix and are independent of any
caller — they can land in one small change set. Steps C and D are separable,
lower-priority follow-ups.

## 4. Test Verification Checklist

- **Existing tests:** None found. No `tests/**` file references `ui_flags.h` or any
  of the four functions, so no existing assertions are invalidated by the fix.
- **New tests required** (the header is currently untestable because it does not
  compile). Add a focused unit test for the flag helpers:
  - **Round Trip Check** on allocation: `set_p_ui_flags__u8_as__allocated(&f)` →
    `is_ui_flags__allocated(f) == true`; then
    `set_p_ui_flags__u8_as__deallocated(&f)` → `is_ui_flags__allocated(f) == false`.
  - **Property Based Testing** for the **Representation Invariant**: after any set/
    clear sequence, exactly the intended bit is toggled and all other bits are
    preserved (frame condition). Verify `BIT(7)` does not collide with any defined
    bit (0–6, 8–15).
  - **Equivalence Check** (only if Step D consolidates `ui_element.c`): assert the
    inline accessors and the `ui_flags.h` helpers produce identical results on
    identical inputs, confirming the refactor is behavior-preserving.
- **Blast radius of test changes:** Low (greenfield — new test file only; no
  existing tests to migrate).

## 5. Blast Radius Summary

- **Files changed for the correctness fix:** 1–2. `core/include/defines.h` (add one
  macro) and, for option B1, `core/include/ui/ui_flags.h` (remove one function).
- **Behavior-preserving for current callers:** Yes — no caller exists; the missing
  bits have no de facto contract.
- **Phased approach:** Not required for correctness; recommended only to isolate the
  optional naming/hygiene follow-ups (Steps C/D).
- **De facto contracts invalidated:** None. The only boundary affected is the
  compile of `ui_flags.h` itself, which is currently unconsumed.
