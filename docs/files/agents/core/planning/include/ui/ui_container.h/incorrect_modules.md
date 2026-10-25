# Planning: ui_container.h — Incorrect Modules

**Review source:** `agents/core/review/include/ui/ui_container.h/incorrect_modules.md`

**Source files reviewed (read-only):**
- `core/include/ui/ui_container.h` (declarations under review)
- `core/include/defines.h` (`UI_Element`, `UI_Container_Entries`, `UI_CONTAINER_PTR_ENTRIES_MAXIMUM_QUANTITY_OF`)
- `core/include/types/implemented/ui/ui_element_kind.h` (`enum UI_Element_Kind`)
- `core/include/ui/ui_element.h` (inline accessors / handlers)
- `core/source/ui/ui_element.c` (`initialize_ui_element`, default compose/dispose/transform handlers)

**Flagged Incorrect:**
- `initialize_ui_element_as__container(UI_Element *p_ui_container, UI_Container_Entries *p_entries)`
- `add_ui_element_to__ui_container(UI_Element *p_ui_container)`

---

## 1. Problem Identification

Both flagged functions are declared in `ui_container.h` but have **no implementation anywhere** (no `ui_container.c`, and no definition in `ui_element.c`, `ui_manager.c`, `ui_context.c`, or any other source file). This is a **Stub-real divergence**: the header advertises behavior that does not exist.

### 1.1 `initialize_ui_element_as__container`
- **No implementation (Stub-real divergence / Under Specified Dispatch).** The declared contract (reset to initial conditions, associate the entries pool, link `p_child` to the first entry) is unenforceable because no body exists.
- **Representation Invariant gap.** `UI_Element` (defines.h:1669–1730) has `p_parent / p_child / p_next` but **no field that references its owning `UI_Container_Entries` pool**. The only possible association is the implicit pointer `p_child -> &p_entries[0]`. A by-value array owned by the caller cannot be "associated" with the container struct — the association is not representable, so it is silently lost (State Desync).
- **Kind mismatch.** There is no `UI_Element_Kind__Container` in `enum UI_Element_Kind`; a container must be initialized as `UI_Element_Kind__Logical`. This is an **Under Specified Dispatch** point the implementation must resolve explicitly.

### 1.2 `add_ui_element_to__ui_container`
- **Missing operand (Non-Injective / Under Specified Dispatch).** The signature takes only the container; it does not receive the element to add. A single-argument function cannot determine which element to insert, so its stated intent is unfulfillable regardless of any body.
- **Free-slot ambiguity (Boundary Condition / Representation Invariant).** `UI_Container_Entries` is a **by-value** array `typedef UI_Element UI_Container_Entries[8]` (defines.h:1735). A value array has no NULL slot, so "first available slot" (the intended insertion point) is undefined. The macro name `UI_CONTAINER_PTR_ENTRIES_MAXIMUM_QUANTITY_OF` implies a *pointer* array — a **Surface-form leakage** between the name and the actual typedef.
- **No implementation (Stub-real divergence).**

## 2. Impact Assessment

**Current blast radius is minimal.** Neither function is called anywhere in `./include` or `./source`, and no header other than `ui_container.h` references `UI_Container_Entries`. There is **no de facto contract in use** — the two functions are dead stubs, so correcting them invalidates no existing caller assumptions.

**Coupled representations (the real risk).** The *correct* sibling `remove_all_ui_elements_from__ui_container` iterates the container's children via the `p_child`/`p_next` linked list. If a container is implemented by (a) storing children in a contiguous `UI_Container_Entries` value array **and** (b) linking them through `p_next`, then "the container's children" is expressed by **two** structures — an array position and a linked list. That violates **Single Source of Truth (SSOT)** and invites **State Desync**: the default handlers in `ui_element.c` (`m_ui_element__compose_handler__default`, `m_ui_element__dispose_handler__default`, `m_ui_element__transformed_handler__default`) traverse `p_child`/`p_next` and would treat the entries pool as a generic linked list, with no notion of the 8-slot capacity boundary.

**Struct-layout risk (if resolved by adding a field).** If the fix for §1.1 is to add an owning field (e.g. `UI_Container_Entries *p_container_entries` or a child-count) to `UI_Element`, that changes `sizeof(UI_Element)` and its serialization layout (the body after `Serialization_Header` is memset-cleared in `initialize_ui_element`). That ripples across **all** UI consumers and the serialization path — a broad blast radius. This is why the pointer-array typedef resolution below (which leaves `UI_Element` untouched) is preferred.

## 3. Resolution Assessment

Goal: bring the two functions into alignment with their semantic intent, restore a single source of truth for "container children", and make capacity/free-slot well-defined — without churning `UI_Element`'s layout.

### 3.1 Fix the pool type (prerequisite, low blast radius)
- Change `UI_Container_Entries` from a by-value array to a **pointer array** so it matches its `..._PTR_ENTRIES_...` name (resolves the Surface-form leakage) and makes "free slot" = `NULL`:
  - `typedef UI_Element *UI_Container_Entries[UI_CONTAINER_PTR_ENTRIES_MAXIMUM_QUANTITY_OF];`
- This is confined to `defines.h`; the only consumer is `ui_container.h`. No other file references the type.

### 3.2 Implement `initialize_ui_element_as__container`
- Create `core/source/ui/ui_container.c`.
- Body: call `initialize_ui_element(p_ui_container, /*parent*/0, /*child*/p_entries[0], /*next*/0, UI_Element_Kind__Logical, flags)` — i.e. reset to initial conditions with default handlers (Lavender non-RAII init), link `p_child -> p_entries[0]`, and zero any unused pool slots to `NULL`.
- **Precondition:** `p_ui_container` and `p_entries` non-null. **Postcondition:** container is a `Logical` element whose `p_child` addresses the first pool slot; unused slots are `NULL`.
- Callers: none exist — no caller updates required.

### 3.3 Implement `add_ui_element_to__ui_container`
- **Fix the signature first** (the actual defect): add the missing operand →
  `void add_ui_element_to__ui_container(UI_Element *p_ui_container, UI_Element *p_ui_element_to_add);`
- Body: locate the first `NULL` slot in the container's pool (well-defined once §3.1 lands), store `p_ui_element_to_add` there, set the added element's `p_parent -> p_ui_container`, and maintain the `p_next`/`p_child` links so the SSOT invariant holds (the linked list is a *view* of the pool, not an independent source).
- **Precondition:** container initialized via §3.2; at least one free slot (Boundary Condition — reject/log when the pool is full). **Postcondition:** element linked into pool and parent back-pointer set.
- Callers: none exist — no caller updates required.

### 3.4 Consistency with the correct sibling
- Ensure `remove_all_ui_elements_from__ui_container` (already judged Correct) clears both the pool slots (to `NULL`) and the `p_child`/`p_next` links, keeping the SSOT invariant symmetric with add/init. No signature change needed; verify its body matches §3.1's pointer-array model.

### 3.5 Documentation
- Update the header comments on all three declarations to state that a container is a `Logical` `UI_Element`, that its pool is a fixed-capacity pointer array, and that the linked list is a derived view of the pool (single source of truth).

## 4. Test Verification Checklist

- **No existing tests.** `tests/` contains no file referencing the container functions or `UI_Container_Entries`, and no tests assert on current (broken) behavior. Therefore no existing assertions are invalidated; **all coverage is new**.
- **New tests to add** (terminology-based):
  - **Round Trip Check:** `init` → `add` ×N → `remove_all` returns the container to its post-init state (pool slots `NULL`, `p_child == NULL`).
  - **Property Based Testing:** invariant — the number of non-`NULL` pool slots equals the length of the `p_child`/`p_next` chain (SSOT / Representation Invariant), across arbitrary add/remove sequences.
  - **Boundary Condition:** adding beyond capacity (8) is rejected and leaves state unchanged; adding to a full pool is a no-op.
  - **Equivalence Check:** a container's children, iterated via the `p_next` list, are element-for-element identical to the non-`NULL` pool entries in order.
  - **Null-input cases:** null container / null element / null pool are handled per precondition (no UB).
- **Test blast radius: Low** (no existing tests to migrate). No phased test rollout needed; add a single `ui_container` test module alongside the new `ui_container.c`.

## 5. Blast Radius Summary

| Aspect | Assessment |
|---|---|
| Files changed | 3: `defines.h` (typedef), `ui_container.h` (add signature + comments), new `ui_container.c` |
| Behavior-preserving for current callers? | Yes — **no callers exist**; the functions are dead stubs, so no in-use contract is invalidated |
| De facto contracts invalidated? | None |
| `UI_Element` struct layout | **Unchanged** (pointer-array approach avoids a serialization-affecting layout change) |
| Phased approach needed? | No — the fix is localized to the UI container surface; §3.1 → §3.2 → §3.3 is a small linear sequence |

**Overall blast radius: Low.** The defects are contained to an unimplemented, uncalled header; the only cross-cutting care is keeping the pool array and the `p_child`/`p_next` list as a single source of truth so the existing default handlers in `ui_element.c` continue to traverse children correctly.
