# Planning: entity_registrar.h — Incorrect Modules

**Review source:** `agents/core/review/include/entity/implemented/entity_registrar.h/incorrect_modules.md`

**Source files reviewed (read-only):**
- `core/include/entity/implemented/entity_registrar.h`
- `core/source/entity/implemented/entity_registrar.c`
- `core/include/entity/entity_manager.h`
- `core/source/entity/entity_manager.c`
- `core/include/entity/entity.h`
- `core/include/types/implemented/entity/entity_kind.h`
- `core/include/types/implemented/entity/entity_functions.h`
- `core/include/types/implemented/entity/entity_data.h`
- `core/include/defines.h` (Entity_Manager, Entity, Entity_Functions struct definitions)
- `core/source/scene/implemented/scene_registrar.c` (reference: properly generated registrar pattern)
- `core/source/game_action/implemented/game_action_registrar.c` (reference: mixed static + GEN registrar pattern)
- `tests/core/source/entity/implemented/test_suite_entity_implemented_entity_registrar.c`
- `tests/core/include/entity/implemented/test_suite_entity_implemented_entity_registrar.h`

---

## 1. Problem Identification

**`register_entities`** (`core/source/entity/implemented/entity_registrar.c`, declared in `core/include/entity/implemented/entity_registrar.h`) is flagged **Incorrect**.

The function is a **Stub-real divergence**: its body, delimited by `GEN-BEGIN`/`GEN-END` code-generation markers, contains only a single `debug_warning("register_entities, impl.")` call and performs zero registrations. The intended **Postcondition** — that `p_entity_manager->entity_functions[]` is populated with a function-pointer table for each concrete `Entity_Kind` — is never satisfied. This is a **Translation Gap** between the function's documented semantic intent (register every concrete entity type's function table into the entity manager) and its actual behavior (no-op). The `entity_functions[]` array, sized `[Entity_Kind__Unknown]`, remains entirely zeroed after initialization.

Two concrete defects:

1. **Missing dispatch population (State Desync / Representation Invariant violation):** No `register_entity_into__entity_manager` call is ever made within the stub body. The `entity_functions[]` lookup table — read back by `sanitize_entity_functions` and `set_entity_functions` — is left in its zeroed state. The **Representation Invariant** that "every concrete `Entity_Kind` has a registered `Entity_Functions` table" does not hold.

2. **Missing Precondition guard (Boundary Condition):** Unlike its sibling `register_entity_into__entity_manager` (which guards `p_entity_manager == 0` under `#ifndef NDEBUG`), `register_entities` performs no null check. This is harmless only because the pointer is currently unused; once the stub is filled in, a null dereference would occur. The unconditional `debug_warning("register_entities, impl.")` also constitutes **Surface-form leakage** of a code-generation placeholder into production log output on every `initialize_entity_manager` call.

---

## 2. Impact Assessment

### Direct caller: `initialize_entity_manager`

`initialize_entity_manager` (`core/source/entity/entity_manager.c:49`) invokes `register_entities(p_entity_manager)` as its final step (line 66). Because `register_entities` is a no-op stub, every `Entity_Manager` is left with an all-zeroed `entity_functions[]` table. **Correcting `register_entities` invalidates** any assumption that the table is all-NULL post-initialization.

### Downstream consumers of the empty table

- **`sanitize_entity_functions`** (`entity_manager.c:82`): Iterates over `p_entity_manager->entity_functions[kind]` and copies non-NULL function pointers into the entity. With an all-zeroed table, **no** registered handlers are ever copied — entities rely solely on whatever `f_entity_initializer__default` set (dispose, serialize, deserialize only). Enable/disable and update handlers remain `NULL` for all entity kinds.
- **`set_entity_functions`** (`entity_manager.h`, `static inline`): Copies the full `Entity_Functions` struct from the table into an entity. With the table empty, this overwrites any handlers the entity may have had with all-NULLs.
- **`allocate_entity_in__entity_manager`** / **`allocate_entity_with__this_uuid_in__entity_manager`**: Both call `sanitize_entity_functions` post-allocation, so every newly allocated entity inherits the empty function table.

### Coupling (Coupled / SSOT)

The `Entity_Manager` struct declares `Entity_Functions entity_functions[Entity_Kind__Unknown]` as the **Single Source of Truth (SSOT)** for per-kind dispatch. Both `sanitize_entity_functions` and `set_entity_functions` read from this SSOT. Because the SSOT is never populated, the entire entity lifecycle operates without registered kind-specific behavior. `initialize_entity_manager` is **Coupled** to `register_entities` as the sole registration entry point.

### De facto contract

The all-zeroed `entity_functions[]` table is currently a **de facto contract** relied upon by:
- `f_entity_initializer__default`, which intentionally wires only dispose/serialize/deserialize (enable/disable deferred to `sanitize_entity_functions`).
- The test `sanitize_entity_functions__applies_registered_functions`, which bypasses `register_entities` by manually calling `register_entity_into__entity_manager` — it passes *because* it does not exercise the full-initialization path.
- The test `register_entity__does_not_crash`, which calls `initialize_entity_manager` then manually registers — no assertion on the table being empty.

**Correcting `register_entities` invalidates** the assumption that `entity_functions[]` is all-zeroed after initialization. Once implemented, `sanitize_entity_functions` and `set_entity_functions` will begin copying registered handlers, changing entity allocation behavior.

---

## 3. Resolution Assessment

### Step 1: Implement the registration body (GEN region)

Replace the `debug_warning("register_entities, impl.")` stub within the `GEN-BEGIN`/`GEN-END` markers with calls that populate `entity_functions[]` for each concrete `Entity_Kind`.

The mechanism is the existing generic `register_entity_into__entity_manager(p_entity_manager, kind, functions)` (validated in `entity_manager.c:69`), which performs a by-value copy of an `Entity_Functions` struct into the correct array slot.

Currently `Entity_Kind` defines only `Entity_Kind__None = 0` and `Entity_Kind__Unknown = 1` (array size = 1 slot). The minimal correct implementation registers the `Entity_Kind__None` slot with default handlers (`m_entity_dispose_handler__default`, `m_entity_serialization_handler__default`, `m_entity_deserialization_handler__default`).

When concrete entity kinds are added via the `#define DEFINE_ENTITY_KIND` code-generation mechanism, the code generator must emit one `register_entity_into__entity_manager` call per kind within the GEN region. The pattern is demonstrated by `scene_registrar.c` (GEN-INCLUDE-BEGIN for headers, GEN-BEGIN/END for calls) and `game_action_registrar.c` (static core calls outside markers + GEN markers for project-specific extensions).

### Step 2: Add Precondition guard

Add a `#ifndef NDEBUG` null check on `p_entity_manager`:
```c
#ifndef NDEBUG
    if (!p_entity_manager) {
        debug_error("register_entities, p_entity_manager == 0.");
        return;
    }
#endif
```
This matches the convention in `register_entity_into__entity_manager` and `initialize_entity_manager`, enforcing the **Precondition** that the manager pointer is valid before any registration writes.

### Step 3: Remove the placeholder warning

Eliminate `debug_warning("register_entities, impl.")`. This is **Surface-form leakage** of a code-generation placeholder. Once the body is implemented, the warning is obsolete. If a temporary placeholder is needed during development, it should be gated behind a debug-only macro rather than emitted unconditionally on every initialization.

### Step 4: No caller changes required

`initialize_entity_manager` already calls `register_entities(p_entity_manager)` correctly. The fix is entirely within `register_entities` itself. No header changes needed (signature is already correct).

### Step 5: Code-generation alignment

The `GEN-BEGIN`/`GEN-END` markers indicate this file is managed by a code generator. The resolution must ensure:
- If the code generator is active, it emits registration calls (not the debug_warning placeholder).
- If no code generator is active, the calls can be hand-written within the markers.
- The `GEN-INCLUDE-BEGIN`/`GEN-INCLUDE-END` pattern (as seen in `scene_registrar.c`) should be added for auto-including concrete entity headers when kinds are defined.

---

## 4. Test Verification Checklist

### Existing tests surveyed

- **`test_suite_entity_implemented_entity_registrar.c`** (suite `entity_registrar`):
  - `register_entity__does_not_crash`: Calls `initialize_entity_manager` then manually registers via `register_entity_into__entity_manager`. Does **not** assert on `entity_functions[]` being empty. **Not invalidated** by the fix.
  - `sanitize_entity_functions__applies_registered_functions`: Manually registers, then asserts `sanitize_entity_functions` copies handlers. Bypasses `register_entities` entirely. **Not invalidated.**
  - `set_entity_initializer__does_not_crash`: Tests initializer wiring. **Not invalidated.**

- **`test_suite_entity_entity_manager.c`**:
  - `initialize_entity_manager__does_not_crash`: Crash-safety only. **Not invalidated.**
  - `initialize_entity_manager__next_ptr_is_set`: Pointer setup only. **Not invalidated.**
  - Allocation tests: Assert on pointer non-nullness, kind, UUID — none assert on `entity_functions[]` contents. **Not invalidated** (default handlers don't interfere with allocation bookkeeping).

### New tests needed

1. **Postcondition verification (Property Based Testing):** After `initialize_entity_manager`, assert that `entity_functions[Entity_Kind__None]` has at least one non-NULL handler (e.g., `m_entity_dispose_handler`). Verifies the **Representation Invariant** that every concrete kind has a registered table. Extend per-kind as new kinds are added.

2. **Round Trip Check:** Call `initialize_entity_manager` (which invokes `register_entities`), allocate an entity of `Entity_Kind__None`, and verify `sanitize_entity_functions` copies the registered handlers into the entity. Confirms the registration → dispatch pipeline is **Round Trip Safe**.

3. **Precondition / Boundary Condition:** Call `register_entities(NULL)` in a debug build and verify it emits `debug_error` and returns without crashing (matching the convention in `register_entity_into__entity_manager`).

### Test blast radius
**Low.** No existing test asserts on `register_entities` being a no-op or on `entity_functions[]` being all-NULL. The fix is additive (populating previously-empty slots). No phased approach required for the test suite; new tests should be added alongside the implementation.

---

## 5. Blast Radius Summary

| Dimension | Assessment |
|-----------|-----------|
| Files requiring changes | 1 — `core/source/entity/implemented/entity_registrar.c` |
| Behavior-preserving for current callers? | Yes. No caller relies on `entity_functions[]` being all-NULL as a contractual requirement. The all-NULL state is an artifact of the stub, not an intended invariant. |
| De facto contracts invalidated | The assumption that `entity_functions[]` is all-zeroed post-`initialize_entity_manager`. Review documents referencing this assumption should be updated. |
| Phased approach needed? | No. Change is localized to a single function body. |
| Code-generator risk | Medium. Must ensure the code generator (if active) emits registration calls rather than overwriting them with the placeholder. |
| Downstream impact | `sanitize_entity_functions` and `set_entity_functions` will begin copying registered handlers into entities — the intended behavior. Entities allocated post-init will have kind-appropriate function tables. |
