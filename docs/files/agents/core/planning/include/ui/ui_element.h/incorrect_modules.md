# Planning: ui_element.h — Incorrect Modules

**Review source:** `agents/core/review/include/ui/ui_element.h/incorrect_modules.md`

**Source files reviewed (read-only):**
- `core/include/ui/ui_element.h`
- `core/source/ui/ui_element.c`
- `core/source/ui/ui_manager.c` (caller)
- `core/source/ui/ui_text_box.c` (caller)
- `core/source/ui/ui_slider.c` (caller)
- `tests/core/source/ui/test_suite_ui_ui_element.c`

Nine functions/modules were flagged **Incorrect**. They fall into three defect
classes: **Stub-real divergence** (declaration/implementation mismatch or missing
definition), **State Desync / Mode Confusion** (value computed from the wrong
source of truth), and **Boundary/Precondition violations** (missing null/boundary
guards). Several of the flagged functions are dead code; a few are live and couple
to the broken behavior.

---

## 1. Problem Identification

| # | Function | Defect class | Core defect (one line) |
|---|----------|--------------|------------------------|
| 1 | `release_ui_element__PLATFORM_sprite` | Stub-real divergence / Translation Gap | Header declares `release_ui_element__PLATFORM_sprite(Gfx_Context*, UI_Element*)`; source defines a *different* symbol `release_ui_element__sprite(Game*, Graphics_Window*, UI_Element*)`. No declaration↔definition pair exists for either name → guaranteed linker error if the header symbol is referenced. |
| 2 | `m_ui_element__compose_handler__default_only_recursive` | State Desync (uninitialized read → UB) | Line 556 passes the *uninitialized* local `p_ui_element__child` to `get_child_of__ui_element()` instead of the parent `p_ui_element`; every sibling handler passes the parent. Reads an indeterminate pointer. |
| 3 | `set_ui_element__sprite` | Stub-real divergence (missing definition) | Declared in header, never defined in `.c`. `UI_Element` has no `p_sprite` field and the signature lacks the `Sprite_Manager` context needed to register a sprite by UUID → cannot link or cannot fulfill intent. |
| 4 | `set_position_3i32_of__ui_element` | Mode Confusion / State Desync + Coupled double-write | Child target is computed as `(parent_new − parent_old) + parent_new = 2·new − old` instead of `child_old + (parent_new − parent_old)`; the child's old position is never read. A transformed handler and the trailing recursive call both write the child's position (two conflicting sources of truth). |
| 5 | `m_ui_element__dispose_handler__default_collection` | Conservation Law violation / dead code | Calls the default dispose handler first, which nulls `p_next`; the following `get_next__ui_element()` returns NULL and the `do`-while is unreachable. If it *were* reachable it would double-dispose (use-after-free) because the default handler already recurses the `next` chain. Marked `// TODO: remove`. |
| 6 | `link_ui_element_to__this_ui_element` | Representation Invariant violation (dead guard) | The self-link guard sets `p_next = 0`, but the unconditional `p_predecessor->p_next = p_successor;` on the next line overwrites it (missing `else`). Self-reference is silently allowed. |
| 7 | `does_ui_element_have__compose_handler` | Precondition / Invariant violation (missing null guard) | Omits the `p_ui_element &&` guard that every sibling `does_ui_element_have__*` query has; a NULL element dereferences through `is_ui_element__using_ui_tile_span`/`get_ui_element__compose_handler` → UB. |
| 8 | `allocate_hitbox_for__ui_element` | Boundary Condition / Precondition violations (3 missing null guards) | No guard on `p_hitbox_aabb_manager`, on the possibly-NULL `p_hitbox_aabb` returned by allocation, or on `p_ui_element` before `GET_UUID_P`. In release builds the debug-only guards in the callees are compiled out → null dereference. |
| 9 | `set_positions_of__ui_elements_in__succession` | Boundary Condition violation (empty collection) | A `do`-while runs the body once *before* the null check, so a NULL head is passed to `set_position_3i32_of__ui_element` → null dereference via `GET_UUID_P`. |

---

## 2. Impact Assessment

### Live callers (broken behavior is coupled to real code paths)

- **`set_position_3i32_of__ui_element`** — highest blast radius. Called by:
  - `ui_manager.c` → `allocate_ui_element_from__ui_manager_as__child()` (positions a freshly allocated child at its parent's position).
  - `ui_slider.c` → `m_ui_slider__transformed_handler__default()` (positions the slider handle as an absolute offset from the track).
  - Self-recursion inside the function, and `m_ui_element__transformed_handler__default()`.
  - Correcting the child-delta **invalidates a de-facto contract**: callers such as the slider already compute an *absolute* child position and rely on `set_position` to place it. The current code then overwrites that value with the broken `2·new − old` figure, so the slider handle is silently mis-positioned today. Fixing the delta changes what position the recursive write produces; the double-write (transformed handler *and* trailing recursion) must be reconciled or sliders/texts with nested children will move to a different place than they do now.

- **`does_ui_element_have__compose_handler`** — called by:
  - `ui_manager.c` → `f_compose_ui_element_callback__ui_manager()` in the compose sweep. This caller pre-guards `!p_ui_element`, so it is currently safe; the fix is behavior-preserving here but removes a latent UB for any unguarded caller.
  - `ui_element.c` → `m_ui_element__compose_handler__default`, `..._default_only_recursive`, and `set_ui_tile_span_of__ui_element`. These pass live (non-null) elements, so the added null guard is a no-op on the happy path.

- **`m_ui_element__compose_handler__default_only_recursive`** — called by:
  - `ui_text_box.c` → `m_ui_element__compose_handler__text_box()`. Any text box that *has a child* and composes will invoke the uninitialized-read path. This is the most dangerous live bug: it is reachable in normal operation and produces UB (garbage pointer dereference) on every such compose.

### Dead / unlinked code (no production callers found)

- **`release_ui_element__PLATFORM_sprite`** — no callers; the equivalent release logic is inlined in `m_ui_element__dispose_handler__default`. The header declaration is a dangling symbol.
- **`set_ui_element__sprite`** — declared, never defined; no callers (a call would be a linker error). No `p_sprite` field exists to store into.
- **`m_ui_element__dispose_handler__default_collection`** — no callers; flagged `// TODO: remove`. Its only real effect is delegating to the default handler.
- **`set_positions_of__ui_elements_in__succession`** — no callers found in `./include` or `./source`; grid-layout helper is currently unused.

### Tests coupled to the broken behavior

- `tests/.../test_suite_ui_ui_element.c`:
  - `link_ui_element__self_link_sets_null` **asserts the intended (correct) behavior** — that a self-link yields `p_next == NULL`. Against the current missing-`else` implementation this test **fails today**; the fix (adding `else`) makes it pass. This is a post-flag test that already encodes the contract.
  - `does_ui_element_have__compose_handler__requires_tile_span_mode` exercises only non-null elements, so it passes pre- and post-fix; it does **not** cover the missing null guard (new test needed).
  - No tests exist for `set_position_3i32_of__ui_element`, `..._default_only_recursive`, `allocate_hitbox_for__ui_element`, or `set_positions_of__ui_elements_in__succession`.

---

## 3. Resolution Assessment

Grouped by defect class. **Phase 1** removes/fixes the unlinked dead symbols
(low risk, no caller impact). **Phase 2** fixes the live functions (behavior-affecting,
needs test coverage before/after).

### Phase 1 — Stub-real divergence & dead code (behavior-preserving / removal)

1. **`release_ui_element__PLATFORM_sprite`** — Reconcile declaration and definition to a single symbol and signature. The implemented body already operates on `(Game*, Graphics_Window*, UI_Element*)`, so either (a) rename the implementation to match the header, or (b) correct the header declaration to `release_ui_element__sprite(Game*, Graphics_Window*, UI_Element*)`. Because nothing calls it, prefer **deleting the dangling header declaration** (and, if the function is genuinely unused, deleting the orphaned definition too) to eliminate the Stub-real divergence. If retained, also add a release-mode `if (!p_sprite_manager) return;` guard (matching `m_ui_element__dispose_handler__default`) and fix the `bool`/`Sprite*` return mismatch in `does_ui_element_have__sprite`.
   - Callers to update: none. Tests/docs: none.

2. **`set_ui_element__sprite`** — Either implement it or delete the declaration. There is no `p_sprite` field and the signature cannot register a sprite with the `Sprite_Manager`, so the intent as declared is not satisfiable. Recommended: **remove the declaration** (it is unlinked and unimplementable as-is). If a real "associate sprite" operation is needed, re-specify it with `Game*`/`Graphics_Window*` context (SSOT = the `Sprite_Manager` keyed by UUID) before implementing.
   - Callers to update: none. Tests/docs: none.

3. **`m_ui_element__dispose_handler__default_collection`** — **Delete** the function and its declaration (honoring `// TODO: remove`). The default handler already disposes the full `next` chain; the collection wrapper adds a dead loop and a double-dispose/use-after-free hazard.
   - Callers to update: none. Tests/docs: none.

4. **`set_positions_of__ui_elements_in__succession`** — No callers found. Either delete (if confirmed unused across the whole tree) or, if it is intended as a public layout API, add the empty-collection guard before keeping it: `if (!p_ui_element__succession_collection) return;` and convert the `do`-while to a `while`. Confirm no external references before deletion.
   - Callers to update: none. Tests: add an empty-collection case if retained.

### Phase 2 — Live correctness fixes (behavior-affecting)

5. **`m_ui_element__compose_handler__default_only_recursive`** — Change line 556 argument from `p_ui_element__child` to `p_ui_element`:
   ```c
   UI_Element *p_ui_element__child = get_child_of__ui_element(p_ui_element);
   ```
   This matches every sibling handler. Callers (text box) need no change — the fix restores the intended child lookup. **Add a regression test**: a parent with a child that has a compose handler composes exactly once on the child; verify no UB via `Property Based Testing` over random parent/child trees.

6. **`does_ui_element_have__compose_handler`** — Add the null guard as the leading operand, restoring consistency with all sibling queries:
   ```c
   return p_ui_element
       && is_ui_element__using_ui_tile_span(p_ui_element)
       && get_ui_element__compose_handler(p_ui_element);
   ```
   Behavior-preserving for all current (non-null) callers. **Add a test** asserting `does_ui_element_have__compose_handler(0) == false` (null-safety invariant).

7. **`allocate_hitbox_for__ui_element`** — Add three guards mirroring the existing codebase pattern (`set_ui_element__hitbox`, `m_ui_element__dispose_handler__default`, `update_ui_element_origin__relative_to`):
   - `if (!p_ui_element) { debug_error(...); return; }` before `GET_UUID_P`.
   - `if (!p_hitbox_aabb_manager) { debug_error(...); return; }` before allocation.
   - `if (!p_hitbox_aabb) { debug_error(...); return; }` after allocation, before the size/position writes.
   Behavior-preserving on the success path; converts release-mode null dereferences into logged no-ops. **Add tests** for full-pool / NULL-manager / NULL-element rejection (Fuzzing/boundary coverage).

8. **`set_position_3i32_of__ui_element`** — Two coordinated changes:
   - **Fix the delta (Mode Confusion):** read the child's *old* position before mutating the parent, then set `child_new = child_old + (parent_new − parent_old)`. Concretely, capture `get_position_3i32_of__hitbox_aabb(child_hitbox)` ahead of time and use it as the base in the recursive call instead of the parent's already-updated position.
   - **Resolve the double-write (Coupled / SSOT):** today both the transformed handler and the trailing recursive call write the child's position. Pick a single source of truth: either (a) skip the trailing recursive propagation when a transformed handler has already positioned the child, or (b) drop the redundant recursion and let the transformed handler own child placement. Reconcile against `ui_slider.c` and `m_ui_element__transformed_handler__default` so slider handles land where callers expect.
   - **Add null guard** on `p_hitbox_aabb` (matching `set_ui_element__hitbox`) since it is dereferenced without a check.
   - Callers to update: none required if the SSOT is fixed internally, but the slider/text positioning **output may change** — verify with an **Equivalence Check** against expected handle positions and a **Round Trip Check** (position → transform → position) for parent/child pairs.

---

## 4. Test Verification Checklist

- **Existing tests affected:**
  - `link_ui_element__self_link_sets_null` — currently **fails** against the missing-`else` implementation; the fix (item 9) makes it pass. No test edit needed; it already encodes the contract.
  - `link_ui_element__sets_next_pointer`, `iterate_to_next__ui_element__advances_and_returns_current` — use the normal (non-self) link path; unaffected by the fix.
  - `does_ui_element_have__compose_handler__requires_tile_span_mode` — passes pre/post; does not cover the null case.
- **New tests needed:**
  - `does_ui_element_have__compose_handler(0) == false` (null guard).
  - `set_position_3i32_of__ui_element`: parent+child with a known old layout → assert child moves by the parent delta (`Property Based Testing` over offset vectors; **Round Trip Check** for reposition stability).
  - Slider handle positioning after the SSOT fix (**Equivalence Check** vs. expected absolute handle position).
  - `..._default_only_recursive`: parent-with-child compose invokes child handler exactly once, no UB (**Property Based Testing** over tree shapes).
  - `allocate_hitbox_for__ui_element`: rejection on NULL element / NULL manager / full pool (boundary + **Fuzzing**).
  - `set_positions_of__ui_elements_in__succession` (if retained): empty-collection no-op.
- **Suite quality:** run **Mutation Testing** on `ui_element.c` to confirm the new/retained tests actually detect regressions in the delta computation and null guards.

---

## 5. Blast Radius Summary

- **Files changed:** `core/include/ui/ui_element.h` (declarations + inline `link`/`does_*_compose`) and `core/source/ui/ui_element.c` (bodies). No changes required in `ui_manager.c`, `ui_text_box.c`, or `ui_slider.c` *provided* the SSOT/delta fix is contained inside `set_position_3i32_of__ui_element`.
- **Dead-code removals (Phase 1):** 4 symbols; behavior-preserving, zero caller impact, shrinks the header surface.
- **Live fixes (Phase 2):** 4 functions. `does_*_compose` and `allocate_hitbox` are behavior-preserving on happy paths. `..._default_only_recursive` is a pure bug fix (restores intent). **`set_position_3i32_of__ui_element` is the only change that can alter observable output** (slider/text nested-child placement) — it is the highest-risk item and should land with the Equivalence/Round-Trip tests in place.
- **De-facto contracts invalidated:** the slider's reliance on `set_position` to place its handle, and any caller assuming the (broken) `2·new − old` child placement. Both are corrected, not preserved.
- **Phased approach required:** Yes. Land Phase 1 (dead-code removal + trivial guards) first, then Phase 2 live fixes with their test coverage, so the behavior-changing `set_position` fix is isolated and verifiable.
- **Overall blast radius: Medium** — wide in file count (two core files) but narrow in caller impact; concentrated risk is the single `set_position` semantics change.
