# Planning: ga_types__collisions.h — Incorrect Modules

**Review source:** `agents/core/review/include/types/core/game_action/collisions/ga_types__collisions.h/incorrect_modules.md`

**Source files reviewed (read-only):**
- `core/include/types/core/game_action/collisions/ga_types__collisions.h`
- `core/include/types/implemented/collisions/hitbox_kind.h`
- `core/include/defines.h` (`Game_Action` struct, `_ga_payload_union`, `GET_P_GAME_ACTION_PAYLOAD_AS_P`)
- `core/source/game_action/core/hitbox/game_action__hitbox.c`
- `core/include/game_action/core/hitbox/game_action__hitbox.h`
- `tests/core/source/game_action/core/hitbox/test_suite_game_action_core_hitbox_game_action__hitbox.c`

---

## 1. Problem Identification

### `get_p_the_kind_of_hitbox_from__ga_collisions` — **Incorrect**

- **Defect (Aliasing Bug / type confusion):** The accessor is declared to return
  `Identifier__u32 *`, but it returns the address of the
  `the_kind_of__hitbox` field, which is typed `Hitbox_Kind` (a plain C enum,
  underlying type `int`, per `hitbox_kind.h`). Taking the address yields a
  `Hitbox_Kind *`; returning it as `Identifier__u32 *` is a type-incompatible
  pointer conversion.
- **Consequence:** Any read or write through the returned pointer uses
  `uint32_t` semantics on an object declared as `Hitbox_Kind`, violating strict
  aliasing — Undefined Behavior at optimization time. The function's stated
  Postcondition ("caller can read or modify the hitbox kind through the
  returned pointer") is not safely realizable with the declared type.
- **Contrast:** The sibling by-value accessor
  `get_the_kind_of_hitbox_from__ga_collisions` (returns `Identifier__u32`) is
  correct — enum-to-integer conversion by value is well-defined. Only the
  pointer-level variant carries the defect.
- **Not a defect (for scope clarity):** The absence of null/validity validation
  on `p_game_action` matches the codebase-wide accessor pattern; validation is
  the caller's responsibility per the established contract and is out of scope.

## 2. Impact Assessment

**Reachability:** `defines.h` includes `ga_types__core.h`, which includes
`ga_types__collisions.h`; since `defines.h` is broadly included, the
`static inline` accessor is visible to nearly every TU. However, a survey of
`./include` and `./source` found exactly **one** consumer:

- `core/source/game_action/core/hitbox/game_action__hitbox.c`:
  - `m_process__game_action__hitbox` — reads the kind via the **by-value**
    accessor (line ~46). Unaffected by the fix.
  - `initialize_game_action_for__hitbox` — **writes** through the broken
    pointer (line ~168):
    `*get_p_the_kind_of_hitbox_from__ga_collisions(p_game_action) = the_kind_of__hitbox;`
    The RHS is already a `Hitbox_Kind`, so this is precisely the strict-aliasing
    write site the review flags as UB.

**Callers of `initialize_game_action_for__hitbox`:**
- `dispatch`-style helper in `game_action__hitbox.h` (static inline, builds and
  forwards a hitbox game action to the server).
- The test suite `test_suite_game_action_core_hitbox_game_action__hitbox.c`.

**Assumptions invalidated by the fix:**
- The de facto contract of the broken signature is narrow: the single write
  site passes a `Hitbox_Kind` value, so retyping the return to `Hitbox_Kind *`
  is **behavior-preserving** for every existing caller — no caller relies on
  `uint32_t`-typed access to this field.
- No serialization, networking, or layout assumption is coupled to the pointer
  type: the wire/struct layout is determined by the `GA_Collisions` field type
  (`Hitbox_Kind`), which this plan does **not** change.
- The sibling accessor `get_p_uuid_of__target_from__ga_collisions` already
  returns a pointer whose type matches its field (`Identifier__u32`); it stays
  as the reference pattern and needs no change (Single Source of Truth for the
  field's type remains the struct definition).
- **Out of scope (noted, not planned):** retyping `Hitbox_Kind` to a fixed-width
  typedef would change struct layout and serialization (Canonical Form
  Enforcement with broad blast radius). Not required to resolve this defect.

## 3. Resolution Assessment

**Goal:** Make the pointer accessor's declared type faithful to the field's
actual type, eliminating the type-incompatible pointer conversion and the
resulting UB.

### Steps

1. **`core/include/types/core/game_action/collisions/ga_types__collisions.h`**
   - Change the return type of `get_p_the_kind_of_hitbox_from__ga_collisions`
     from `Identifier__u32 *` to `Hitbox_Kind *`.
   - Ensure `Hitbox_Kind` is in scope at the point of use (verify the include
     chain through `defines.h`; add a direct include of
     `types/implemented/collisions/hitbox_kind.h` if the type is only visible
     transitively, to preserve Information Hiding / self-contained headers).
   - Do not touch `get_the_kind_of_hitbox_from__ga_collisions` (correct as-is).
2. **`core/source/game_action/core/hitbox/game_action__hitbox.c`**
   - The write in `initialize_game_action_for__hitbox` assigns a `Hitbox_Kind`
     to the dereferenced pointer; after step 1 this becomes a well-typed,
     aliasing-safe assignment with **no code change required** (verify by
     compilation). No caller signature changes anywhere.
3. **Tests / documentation:**
   - Existing suite
     `tests/core/source/game_action/core/hitbox/test_suite_game_action_core_hitbox_game_action__hitbox.c`
     exercises `initialize_game_action_for__hitbox` but asserts only on the
     action kind and target UUID — it does **not** pin the broken pointer type,
     so no existing assertion is invalidated.
   - **Add a Round Trip Check:** for each `Hitbox_Kind` value
     (`Opaque`, `AABB`, `Unknown`), call `initialize_game_action_for__hitbox`
     then read back via `get_the_kind_of_hitbox_from__ga_collisions` and assert
     equality; also read back through the pointer accessor to cover the
     aliasing path.
   - **Add an Equivalence Check:** a payload built via the pointer write must
     compare byte-for-byte with one built by direct struct assignment of
     `the_kind_of__hitbox`.
   - **Lint Gate:** enable/keep `-Wincompatible-pointer-types` and strict
     aliasing warnings (`-Wstrict-aliasing`) so this class of Type Invariant
     violation is caught at build time (Static Analysis).

### Phasing

Single-phase; the change is one signature edit plus test additions. No
migration or phased rollout is needed.

## 4. Test Verification Checklist

| Item | Finding |
|------|---------|
| Existing tests referencing the function | Test suite calls `initialize_game_action_for__hitbox` (indirect consumer); no test references the pointer accessor directly |
| Assertions pinned to broken behavior | None — existing assertions (action kind, target UUID) are behavior-preserving under the fix |
| New tests required | Round Trip Check per `Hitbox_Kind` value; Equivalence Check (pointer write vs. direct field write); boundary: `Hitbox_Kind__Unknown` sentinel value round trip |
| Terminology-based recommendations | `Round Trip Check`, `Equivalence Check`, `Lint Gate`; `Property Based Testing` optional if a hitbox-kind property suite is later added |
| Test blast radius | **Low** — one test file extended; no existing assertion changes |

## 5. Blast Radius Summary

- **Files changed:** 1 header (`ga_types__collisions.h`, signature edit) + 1
  test file (new cases). The one consumer `.c` file compiles unchanged.
- **Behavior-preserving for current callers:** Yes — the sole write site
  already supplies a `Hitbox_Kind`; observable behavior is identical, only the
  UB is removed.
- **Phased approach needed:** No.
- **De facto contracts invalidated:** None — no caller relied on the
  `Identifier__u32 *` typing of this field; struct layout and serialization are
  untouched.
