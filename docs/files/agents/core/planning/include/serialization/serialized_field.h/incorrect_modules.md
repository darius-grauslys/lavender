# Planning: serialized_field.h — Incorrect Modules

**Review source:** `agents/core/review/include/serialization/serialized_field.h/incorrect_modules.md`

**Source files reviewed (read-only):**
- `core/include/serialization/serialized_field.h` (inline: `is_serialized_field_matching__serialization_header`, `is_p_serialized_field__linked`, `point_serialized_field_to__this_serialized_struct`, initializers)
- `core/source/serialization/serialized_field.c` (`initialize_serialized_field`, `link_serialized_field_against__contiguous_array`)
- `core/include/defines.h` (`Serialized_Field` union, lines 245-275; `Serialization_Header`, lines 229-232)
- `core/include/serialization/serialization_header.h` (`initialize_serialization_header`, `is_identifier_u32_matching__serialization_header`)
- `core/source/serialization/hashing.c` (`poll_for__uuid_collision`)
- `tests/core/source/serialization/test_suite_serialized_field.c`

---

## 1. Problem Identification

All three flagged functions share a single root cause: an **Aliasing Bug** in the
`Serialized_Field` union that breaks the **Representation Invariant** that
`identifier_for__serialized_field` is a view of the field's `uuid`.

The struct (`core/include/defines.h`, lines 245-275) overlays two 8-byte views:

```c
union {
    struct { Serialization_Header _serialization_header; };          // size_of__struct @0, uuid @4
    struct { Identifier__u32 identifier_for__serialized_field;       // @0  -> aliases size_of__struct (WRONG)
                         Quantity__u32 :32; };                       // @4  -> aliases uuid
};
```

`Serialization_Header` is `{ Quantity__u32 size_of__struct /*@0*/; Identifier__u32 uuid /*@4*/; }`.
Because `identifier_for__serialized_field` is the *first* member of the convenience struct, it lands at
offset 0 and aliases `size_of__struct`, **not** `uuid` (offset 4). The anonymous `:32` bitfield occupies
offset 4 and aliases `uuid`. This makes the identifier view a **Non-Injective Translation** of the header:
two different uuids collapse to the same read-back value (`sizeof(Serialized_Field)`).

### `initialize_serialized_field` (source) — Incorrect
Intends to set the field's identifier to the `identifier_for__serialized_field` argument. It does so via
`initialize_serialization_header(&field->_serialization_header, identifier, sizeof(Serialized_Field))`, which
writes `size_of__struct = sizeof(Serialized_Field)` (offset 0) and `uuid = identifier` (offset 4). Through the
union overlay, `field.identifier_for__serialized_field` therefore reads back as `sizeof(Serialized_Field)`,
**not** the identifier. The **Postcondition** "identifier is set to the provided value" is violated.
(Secondary: this path writes the header view, whereas `point_serialized_field_to__this_serialized_struct`
writes `identifier_for__serialized_field` directly — a **State Desync** / **Stub-real divergence** between two
initialization paths that touch the same bytes with different meanings.)

### `link_serialized_field_against__contiguous_array` (source) — Incorrect
Search logic and bounds checks are sound, but it feeds `p_serialized_field->identifier_for__serialized_field`
(= `sizeof(Serialized_Field)` after init, not the uuid) into `poll_for__uuid_collision`. It therefore probes the
array for a header whose `uuid == sizeof(Serialized_Field)` instead of the real identifier — the lookup almost
always **fails to find** the correct entry (or false-matches by coincidence).

### `is_serialized_field_matching__serialization_header` (inline) — Incorrect
Delegates to `is_identifier_u32_matching__serialization_header(p_serialization_field->identifier_for__serialized_field, ...)`.
Because that field holds the struct size, the comparison is `size_of__struct == target.uuid` — a semantically wrong
comparison. The **Postcondition** "true iff the field's identifier matches the header's uuid" is not met.

---

## 2. Impact Assessment

The broken behavior is centralized in one layout (`Serialized_Field` union in `defines.h`) and consumed only
through the module's own surface; no external caller can be *relying on the size value* because the tests encode
the opposite intent.

**Directly coupled (read/write the broken field):**
- `core/source/serialization/serialized_field.c`
  - `initialize_serialized_field` — writes the header view; identifier view ends up = size.
  - `link_serialized_field_against__contiguous_array` — reads identifier view for the uuid lookup.
  - `point_serialized_field_to__this_serialized_struct` — writes `identifier_for__serialized_field` directly
    (offset 0). After a layout fix this write must land on `uuid`, or it will corrupt `size_of__struct`.
- `core/include/serialization/serialized_field.h`
  - `is_serialized_field_matching__serialization_header` — reads identifier view.
  - `is_p_serialized_field__linked` — compares `identifier_for__serialized_field` against
    `p_serialized_field__serialization_header->uuid`; today this compares size vs uuid, so the "uuid's match"
    clause is broken.

**Indirect coupling (downstream of the field value):**
- `poll_for__uuid_collision` / `is_identifier_u32_matching__serialization_header` (hashing.c, serialization_header.h)
  are *correct* general utilities; they are only wrong when fed the broken identifier. They need **no** change.
- Any external consumer of the public inline accessors (`is_p_serialized_field__linked`,
  `get_p_*_from__serialized_field`) inherits the corrected behavior automatically once the layout is fixed.

**Assumptions invalidated by the fix:**
- The de-facto assumption that `identifier_for__serialized_field` sits at offset 0 (== `size_of__struct`) is
  discarded. Any code that *read* it expecting a uuid (the intended contract, per tests) is **corrected**, not
  broken. No caller was found that depends on the size value as a contract — the test suite asserts the uuid
  semantics and currently fails, confirming the broken state is not a relied-upon behavior.
- `point_serialized_field_to__this_serialized_struct` writes the identifier member directly; after relocating that
  member to offset 4 this write becomes correct (lands on `uuid`). It must be verified, not blindly kept.

---

## 3. Resolution Assessment

Resolve at the **Single Source of Truth** (the union layout), then canonicalize the readers so correctness does
not depend on a convenience member's offset (**Canonical Form Enforcement**).

### Step A — Fix the union layout (root cause, `core/include/defines.h`)
Reorder the convenience arm so `identifier_for__serialized_field` aliases `uuid` (offset 4):

```c
union {
    struct { Serialization_Header _serialization_header; };
    struct { Quantity__u32 :32;                       // @0 -> aliases size_of__struct
             Identifier__u32 identifier_for__serialized_field; }; // @4 -> aliases uuid
};
```

Both arms remain 8 bytes and the struct alignment is unchanged. `Serialized_Field` is a runtime handle (its data
is pointed to, not embedded in the serialized payload), so this layout change does **not** alter any on-disk or
on-wire format. This restores the **Representation Invariant** and removes the **State Desync** between the two
initialization paths — `identifier_for__serialized_field` becomes a faithful, injective view of `uuid`.

- *Callers:* none need signature changes; readers now observe the uuid. Behavior-correcting for all consumers.
- *Docs:* update the struct comment to state the invariant "`identifier_for__serialized_field` aliases
  `_serialization_header.uuid`."

### Step B — Canonicalize the readers (defense-in-depth, `core/source/serialization/serialized_field.c`)
Even with Step A, prefer reading the canonical member so correctness is independent of member ordering:
- `link_serialized_field_against__contiguous_array`: pass `p_serialized_field->_serialization_header.uuid` to
  `poll_for__uuid_collision`.
- `is_serialized_field_matching__serialization_header` (in `.h`): pass
  `p_serialization_field->_serialization_header.uuid` to `is_identifier_u32_matching__serialization_header`.
- `is_p_serialized_field__linked`: compare `_serialization_header.uuid` against the linked header's uuid.
- Keep `point_serialized_field_to__this_serialized_struct` writing the uuid (now correctly aliased); verify it.

Optional cleanup: fix the debug_abort message naming mismatch (`p_serialized_field` vs `p_serialization_field`)
noted in the review — cosmetic only.

### Step C — Callers / docs
- No public signature changes; no external caller updates required (behavior is corrected, not changed in contract).
- Run a codebase-wide search for `identifier_for__serialized_field`, `is_p_serialized_field__linked`,
  `is_serialized_field_matching__serialization_header`, and `link_serialized_field_against__contiguous_array` to
  confirm no caller depended on the broken (size) value.

### Phasing
Steps A and B should land **together** to avoid an intermediate state where the layout is fixed but a reader still
assumes the old offset (or vice-versa). No multi-phase rollout required; blast radius is small.

---

## 4. Test Verification Checklist

Existing suite: `tests/core/source/serialization/test_suite_serialized_field.c`.

- **Current state:** the tests assert the *intended* (uuid) semantics — e.g.
  `munit_assert_uint32(field.identifier_for__serialized_field, ==, 42)` after
  `initialize_serialized_field(&field, &target, 42)`, plus link/match/link-status cases. Given the current layout
  these **fail** (the field reads back as `sizeof(Serialized_Field)`). They therefore serve as the pre-flagged
  acceptance gate: **no test edits are required**; they should pass unmodified once Steps A+B land.
- **Equivalence Check (add):** assert `field.identifier_for__serialized_field == field._serialization_header.uuid`
  for every initialization path (`initialize_serialized_field`, `..._as__unassigned`, `..._as__unlinked`,
  `point_serialized_field_to__this_serialized_struct`) — pins the restored **Invariant**.
- **Round Trip Check (add):** `initialize_serialized_field(&f, data, id)` then read the identifier back and confirm
  it equals `id` (not the size).
- **Property Based Testing (add):** for a range of branded uuids, verify the identifier view round-trips and never
  equals `sizeof(Serialized_Field)`.
- **Boundary Condition (add):** `id == IDENTIFIER__UNKNOWN__u32`; empty / full contiguous arrays in
  `link_serialized_field_against__contiguous_array`; confirm no false match when no header's uuid equals the size.
- **Mutation Testing (optional):** confirm the suite fails if the union arm order is reverted, guarding the layout.

**Test blast radius: Low.** Existing tests need no change (they already encode correct intent); only additive
edge-case coverage is proposed.

---

## 5. Blast Radius Summary

- **Files changed:** 2 — `core/include/defines.h` (union arm order) and
  `core/source/serialization/serialized_field.c` (+ the inline reader in `serialized_field.h`).
- **Behavior-preserving for callers?** The fix is *correcting*, not contract-changing: no caller relied on the
  broken size value (tests prove the intended contract is uuid), so all consumers observe improved, spec-aligned
  behavior. No public signatures change.
- **Phased approach needed?** No — land Steps A and B in one change to avoid an inconsistent intermediate state.
- **De-facto contracts invalidated?** None. The only "contract" was the accidental offset-0 aliasing; the tests
  establish that uuid semantics were always the intent, so nothing valid is broken.
