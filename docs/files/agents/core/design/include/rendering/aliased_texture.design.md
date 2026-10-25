# `aliased_texture` — Design Review

> **Module:** `core/include/rendering/aliased_texture.h` + `core/source/rendering/aliased_texture.c`
> **Record type:** `Aliased_Texture` (`core/include/defines.h:847-851`)
> **Sole production consumer:** `core/source/rendering/aliased_texture_manager.c`
> **Embedded in:** `Gfx_Context.aliased_texture_manager` (`defines.h:2526`) → `Game`
> **Related documents:**
> - `docs/core/memory/Life_Cycle_Patterns.md` (life cycle / ownership SSOT)
> - `agents/core/design/design_guide.md` (checklist §1–§10)
> - `agents/terminiologies/index.md` (terminology)
>
> **Status:** Under review. **Concerns documented only — no code changes made at
> this time.** Not yet tracked via `track_core_modules.py`.

---

## 1. Module Summary

`aliased_texture` is a **record-level** module: it provides name and
texture-handle access for a *single* `Aliased_Texture` entry. It has no globals,
no pools, and no platform includes. The pool, UUID assignment, capacity limits,
and platform release all live one level up in `aliased_texture_manager`.

- **Layer:** **Core** (rendering-subsystem record module). *Note:* the
  design-guide layer table does not name a rendering layer — see **F9**.
- **Role:** **Abstraction.** It surfaces a stable semantic — *a named texture
  record: alias ↔ texture handle* — to the **policy** layer (the manager).

The record:

```c
typedef struct Aliased_Texture_t {          // defines.h:847
    Serialization_Header _serialization_header;
    Texture_Name__c_str  name_of__texture__c_str;   // char[32]  (defines.h:845)
    Texture              texture;                   // { PLATFORM_Texture *; Texture_Flags }
} Aliased_Texture;
```

---

## 2. Ownership & Life Cycle Model (resolves findings 6.2 / 6.3)

Ownership is stated **at the layer where the resource crosses the boundary**,
per `Life_Cycle_Patterns.md`:

| Resource | Owner | Where the ownership is clarified |
|----------|-------|----------------------------------|
| `PLATFORM_Texture` handle | `Aliased_Texture` | **This module** — the `give_texture_to` / `get_texture_from` accessors are the ownership boundary (finding **6.2**). |
| `Aliased_Texture` slot | `Aliased_Texture_Manager` | **Manager** — allocation, `uuid` assignment, and release (finding **6.2**). |

### `a > b > c` placement

- `Aliased_Texture_Manager` lives inside `Gfx_Context` inside `Game` →
  **level (a), full game life cycle, implied shared.**
- An individual `Aliased_Texture` slot, while allocated, is **level (c)** —
  single-owner, owned by the manager, bounded by the manager's context.

### `p_OUT_` convention (resolves finding 6.3)

The manager's `allocate_texture_with__alias` / `load_texture_from__path_with__alias`
take `Texture *p_OUT_texture`. Per the `p_OUT_` convention
(`Life_Cycle_Patterns.md` §2), **the caller owns** `*p_OUT_texture`; the manager
populates it but does not own it. The manager's *stored* copy (in the slot) is a
separate, manager-owned relationship. Note the stored copy is a **shallow** copy
of the `PLATFORM_Texture *` handle — see the abstraction-risk note in §1.

---

## 3. Findings Register

Each finding carries the review decision and a timeline. **"Documented (not
acted)"** means: recorded here now, no code change at this time.

| # | Concern | Class | Timeline | Status now |
|:-:|---------|-------|----------|------------|
| **F1** | Fused init; reset is not total (by-value bug) | Architectural | **post v1.0.0** | Documented |
| **F2** | `c_str` semantic overload (Mode Confusion) | Type / semantic | **post v1.0.0** (tracked with F1) | Documented |
| **F3** | Prefix-match → non-injective alias lookup | Correctness | **pre v1.0.0** | Documented (not acted) |
| **F4** | "Double call leaks" doc — leak by side effect | Contract / doc | **pre v1.0.0** (doc) | Documented |
| **F5** | "Used" sentinel not local to the module | Invariant locality | **pre v1.0.0** | Documented (not acted) |
| **F6** | Copy-paste diagnostic strings | Hygiene | **pre v1.0.0** | Documented (not acted) |
| **F7** | Inconsistent null handling across the module | Error boundary | **pre v1.0.0** | Documented (not acted) |
| **F8** | `design_guide.md` should understand spec reconstruction | Guide gap | pending | To update guide |
| **F9** | `design_guide.md` lacks a rendering layer | Guide gap | pending | To update guide |

---

## 4. Findings Detail

### F1 — Fused init; the reset is not total  ·  *post v1.0.0*

`initialize_aliased_texture` calls `initialize_texture(p_aliased_texture->texture)`,
but `initialize_texture` takes `Texture` **by value** (`texture.h:7-12`). A copy
is zeroed and discarded; the record's `texture` member is **never reset**.

- The **reset operation is not total**: it fails to clear the full state of the
  record (name ✓, header ✓, texture ✗).
- Consequence: after a release, the freed slot still holds the *released*
  `PLATFORM_Texture *` → **State Desync** between the header's "deallocated"
  state and a stale, live-looking handle. `release_all_aliased_textures`
  (`aliased_texture_manager.c:299-315`) then releases **all 128 slots
  unconditionally** → **double-release** of every previously released texture.
- Root cause is the **fused init** pattern: one `initialize_X` serving as both
  create-time init and release-time reset.

**Decision:** This is a serious, systemic issue. Lavender should move to a
**separate reset/dealloc pattern** instead of fused init (see
`agents/docs/design/memory/Life_Cycle_Patterns.design.md` §2). That is a
**large-scale refactor, prohibitively
expensive now → deferred to post v1.0.0**.

> **Clarification (review Q&A):** "not total" refers to the **reset
> operation**, not the documentation. The documentation problem is a *separate*
> finding (**F4**). The two are tracked independently.

### F2 — `c_str` semantic overload (Mode Confusion)  ·  *post v1.0.0, with F1*

`defines.h:845` — `typedef char Texture_Name__c_str[MAX_LENGTH_OF__TEXTURE_NAME];`
— shows the concrete type is a **fixed 32-byte array, not a C string**. The
**Representation Invariant** implied by the `c_str` naming ("this is a
null-terminated C string") does **not** reflect the preferred concrete
implementation (a bounded byte array that is *not* guaranteed terminated).

The surface form `c_str` is **dangerously overloaded**: it bears two
contradicting semantics at once —

1. *"a null-terminated C string"* (what the name and most call sites assume), and
2. *"a fixed 32-byte field"* (what the type actually is).

This is **Mode Confusion** — the same surface form expressing two semantic modes.

**Decision:** Introduce a **`Lav_String_c32`** type to **decouple** the
overloaded `c_str` semantic. Tracked **alongside F1**; the decoupling is a
**post v1.0.0 dev goal**.

### F3 — Prefix-match → non-injective alias lookup  ·  *pre v1.0.0*

`is_c_str_matching__aliased_texture` (`aliased_texture.c:30-46`) breaks the loop
when the *input* hits null and returns true — so any input that is a **prefix**
of the stored name matches (`stored="texture_a"`, query `"texture"` → `true`).

In `get_p_aliased_texture_by__alias` (first match wins, index order), the
name→texture mapping becomes **Non-Injective**: a lookup can return the **wrong
texture**. This is an **Aliasing Bug** in the alias table the module exists to
protect. The function is **Pure** and **Deterministic** — trivially fixable
(require the stored byte at the input's terminator to also be null) and
testable.

**Decision:** Fix **prior to v1.0.0**. *Documented only at this time — not acted on.*

### F4 — "Double call leaks" documentation  ·  *pre v1.0.0 (doc), pairs with F1*

`aliased_texture.h:6-8` states *"Double calling this will leak memory."* Per
review, the **precondition is technically correct** — a `PLATFORM_Texture`
**is** leaked on double-init — but the *kind* of leak is misattributed. It is a
**leak by side effect** (the double-init orphans the `uuid` mapping, so the
platform handle can no longer be reached/released), **not** a malloc leak inside
the function. See `docs/core/memory/Life_Cycle_Patterns.md` §4 for the classification.

**Decision:** Pairs with **F1**. The **documentation** can be corrected
**pre v1.0.0** (state the real side-effect hazard, or remove the claim).

### F5 — "Used" sentinel not local to the module  ·  *pre v1.0.0*

`is_aliased_texture__used` (`aliased_texture.h:46-50`) uses
`name_of__texture__c_str[0]` as the **Sentinel** for occupancy. The invariant
*"used ⟹ non-empty name"* is enforced only by the **manager** (which rejects
empty aliases at allocation). This module's own `set_c_str_of__aliased_texture`
will happily store `""` in a live slot, silently marking it free — a future
re-name path in the manager would then **leak** the platform handle.

**Decision:** Agreed — the invariant should be **local** to the module (reject
empty in `set_c_str`, or a dedicated used flag). **pre v1.0.0.** *Not acted on now.*

### F6 — Copy-paste diagnostic strings  ·  *pre v1.0.0*

`aliased_texture.h:39` — `get_texture_from__aliased_texture` logs
`"give_PLATFORM_texture_to__aliased_texture, …"`, a function name that exists
**nowhere** in the tree. **Surface-form leakage** — the diagnostic is wrong
exactly when it is needed.

**Decision:** Fixable **pre v1.0.0.** *Not acted on now.*

### F7 — Inconsistent null handling  ·  *pre v1.0.0*

Two of four null-checked entry points check `p_aliased_texture` (and only under
`#ifndef NDEBUG`); `set_c_str_of__aliased_texture` and
`is_c_str_matching__aliased_texture` check **nothing** in any build
(`strnlen(NULL, …)` is UB). The functions are **Partial** where they present as
**Total**; the error boundary is inconsistent within the module.

**Decision:** Fixable **pre v1.0.0.** *Not acted on now.*

---

## 5. Design-Guide Gaps (pending — not acted on)

These require edits to `agents/core/design/design_guide.md`. **Not made at this
time** (documentation-only mode). Listed here so the intent is captured.

- **F8 — Spec reconstruction.** `design_guide.md` §10.4 should be written to be
  *understanding of spec reconstruction*: specs are being rebuilt and the
  previously auto-generated ones (and the dangling
  `docs/specs/…/aliased_texture.h.spec.md` reference) were produced in a flawed
  automated manner. A dangling spec reference should be treated as a known,
  in-progress condition, not a defect of the module.
- **F9 — Rendering layer.** The §1 layer table should **incorporate rendering as
  a layer** so modules under `rendering/` do not require inference to place.

---

## 6. Timeline Summary

- **pre v1.0.0 (planned, not started):** F3, F5, F6, F7 (code) · F4 (doc)
- **post v1.0.0:** F1 (reset/dealloc refactor) · F2 (`Lav_String_c32`, with F1)
- **Guide updates (pending):** F8, F9 → `design_guide.md`
- **New SSOT produced:** `docs/core/memory/Life_Cycle_Patterns.md`
  (`a > b > c`, `p_OUT_` ownership, `IDENTIFIER_UNKNOWN` sentinel, leak
  classification)

> **No code has been changed.** This document records concerns and decisions for
> review. Tracking (`track_core_modules.py --track aliased_texture`) is
> intentionally **not** run yet.
