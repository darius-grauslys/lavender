# Planning: ui_drop_zone.h — Incorrect Modules

**Review source:** `agents/core/review/include/ui/ui_drop_zone.h/incorrect_modules.md`

**Source files reviewed (read-only):**
- `core/include/ui/ui_drop_zone.h`
- `core/source/ui/ui_drop_zone.c`
- `core/include/ui/ui_element.h` (callee: `initialize_ui_element`, handler setters)
- `core/source/ui/ui_element.c` (`initialize_ui_element`)
- `tests/core/source/ui/test_suite_ui_ui_drop_zone.c`

---

## 1. Problem Identification

**Flagged:** `initialize_ui_element_as__drop_zone` — `core/source/ui/ui_drop_zone.c`, lines 10-23.
**Verdict:** Incorrect.

Core defect: the function reads the *pre-existing* values of
`p_ui_drop_zone->p_parent`, `->p_child`, `->p_next`, and `->ui_flags`
and passes them back as parameters to `initialize_ui_element`. Because
those arguments are evaluated **before** the call, they capture stale
state. Inside `initialize_ui_element`, a `memset` zeroes the entire
struct (except the `Serialization_Header`) to reset it to its canonical
initial form, and then the stale values are written back over the
zeroed fields.

This is a **Representation Invariant** / **State Desync** violation:
under the Lavender initialization pattern, "initialize" means *reset to
initial conditions for pool reuse*. After initialization the struct must
be in **Canonical Form** — `p_parent == NULL`, `p_child == NULL`,
`p_next == NULL`, `ui_flags == UI_FLAGS__NONE`. By preserving stale
values, the function defeats the reset and leaves a struct that is
supposedly "fresh" but still carries dangling linkage and stale flags.

The **Postcondition** documented in the review ("reset to initial
conditions") is not met for those four fields. The function is also not
**Idempotent** with respect to prior state: re-initializing a previously
linked element yields a different result than initializing a clean one.

## 2. Impact Assessment

- **Callee `initialize_ui_element`** (`core/source/ui/ui_element.c`): its
  `memset`-then-assign is correct in isolation, but for the drop-zone
  path the reset is nullified by the stale arguments supplied by
  `initialize_ui_element_as__drop_zone`. The callee's **Contract-First**
  intent (reset-to-initial) is silently broken by the caller.

- **Production callers in this repo:** none found in `core/source`
  (searched `ui_manager.c`, `ui_window.c`, and the `implemented/`
  registrar). The function is a library entry point; downstream projects
  (e.g. inventory/equipment slot drop zones) are the likely consumers.

- **De-facto contract being relied upon:** any caller that pre-populates
  `p_parent` / `p_child` / `p_next` / `ui_flags` on a pooled element and
  expects those values to *survive* the "initialize" call is coupled to
  the broken behavior. Correcting the function to reset these fields to
  `NULL` / `UI_FLAGS__NONE` **invalidates that assumption**. Per Lavender
  semantics that assumption is itself wrong — linkage and flags are set
  explicitly after initialization via the dedicated setters
  (`set_parent_of__ui_element`, `set_child_of__ui_element`, flag setters),
  so no legitimate caller should depend on persistence through init.

- **Pool-reuse / Cascade Failure risk:** re-initializing a previously
  linked element currently leaves stale parent/child/next pointers and
  flags, which can dangle into recycled memory and propagate **State
  Desync** through the UI tree traversal helpers in
  `ui_element.h` (`iterate_to_parent_of__ui_element`, etc.).

- **Tests mask the defect:** every test in
  `tests/core/source/ui/test_suite_ui_ui_drop_zone.c` calls
  `memset(&ui_element, 0, ...)` before invoking the function. With a
  pre-zeroed struct the stale values are already zero, so the current
  (broken) and the corrected implementations are **Equivalent** for those
  inputs — the existing suite cannot distinguish them.

## 3. Resolution Assessment

**Primary fix — `core/source/ui/ui_drop_zone.c`:**
Replace the self-referential argument reads with canonical initial
values so the reset is not defeated:

```c
initialize_ui_element(
        p_ui_drop_zone,
        NULL,                       // p_parent  (was p_ui_drop_zone->p_parent)
        NULL,                       // p_child   (was p_ui_drop_zone->p_child)
        NULL,                       // p_next    (was p_ui_drop_zone->p_next)
        UI_Element_Kind__Drop_Zone,
        UI_FLAGS__NONE);            // ui_flags  (was p_ui_drop_zone->ui_flags)
```

- **Alternative (if callers need to attach a parent at init):** extend the
  signature to take explicit `p_parent` / `p_child` / `p_next` /
  `ui_flags` parameters from the caller rather than reading them from the
  struct. This preserves **Information Hiding** and makes the intended
  initial linkage explicit instead of implicitly leaking pre-state. Prefer
  the plain reset (first option) unless a concrete caller requires it; keep
  the function **Orthogonal** to post-init linkage setters to avoid
  duplication (DRY).

- **Header doc comment** (`core/include/ui/ui_drop_zone.h`): note that the
  parameter name `p_ui_button` is a copy-paste surface mismatch — rename to
  `p_ui_drop_zone` for clarity. Document the post-init **Representation
  Invariant** (parent/child/next NULL, flags NONE).

- **Callers:** no in-repo callers require signature or behavior changes.
  Downstream consumers that relied on persistence-through-init must switch
  to the explicit setters (already available); flag this in the change note.

**Test verification checklist:**
- Existing tests assert on `the_kind_of_ui_element__this_is` and the
  receive-drop handler; they pre-zero the struct, so they remain valid and
  **Equivalence-preserving** after the fix (no assertion invalidation).
- **New test needed** to exercise the actual defect: pre-populate
  `p_parent` / `p_child` / `p_next` with non-NULL sentinels and
  `ui_flags` with a non-NONE value, call
  `initialize_ui_element_as__drop_zone`, then assert all four reset to
  `NULL` / `UI_FLAGS__NONE`. Frame as a **Round Trip Check** /
  **Property Based Testing** invariant (init ⇒ canonical form) and a
  **Boundary Condition** case (fully-populated stale struct).
- **Separate observation (out of scope for this flag):** the test
  `initialize_ui_element_as__drop_zone__null_handler_uses_default` asserts a
  non-null handler after passing `0`, but `set_ui_element__receive_drop_handler`
  performs a direct field assignment with no default fallback. This is a
  **Stub-real divergence** between the test's stated intent and the
  implementation; route it to its own review rather than bundling into this
  fix.

**Phasing:** single-file, low-risk change — no phased rollout required.

## 4. Blast Radius Summary

- **Files changed:** `core/source/ui/ui_drop_zone.c` (body),
  `core/include/ui/ui_drop_zone.h` (doc comment / param name), and
  `tests/core/source/ui/test_suite_ui_ui_drop_zone.c` (new invariant test).
- **Behavior-preserving for current callers?** Yes for any caller that
  initializes a clean element; **not** for hypothetical callers that relied
  on stale-value persistence — but that reliance is itself the bug and is
  not a legitimate contract. No in-repo callers are affected.
- **Phased approach needed?** No.
- **De-facto contracts invalidated:** the "stale linkage survives init"
  behavior; it is a misreading of the Lavender reset semantics and should be
  retired, with post-init linkage moved to the explicit setters.
