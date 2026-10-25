# Planning: ui_draggable.h — Incorrect Modules

**Review source:** `agents/core/review/include/ui/ui_draggable.h/incorrect_modules.md`

**Source files reviewed (read-only):**
- `core/include/ui/ui_draggable.h`
- `core/source/ui/ui_draggable.c`
- `core/include/ui/ui_element.h` (inline flag setters/clearers)
- `core/include/ui/ui_drop_zone.h`
- `core/source/ui/ui_drop_zone.c`
- `core/source/ui/ui_manager.c` (`handle_drop_in__ui_manager`, `poll_ui_manager__update_for__clicked_and_dropped`, `poll_ui_manager__update_for__held`, `poll_ui_manager__update_for__drag`)
- `core/include/ui/ui_manager.h`
- `core/include/defines.h` (flag bit definitions: `UI_FLAGS__BIT_IS_FOCUSED` = BIT(1), `UI_FLAGS__BIT_IS_BEING_HELD` = BIT(3), `UI_FLAGS__BIT_IS_BEING_DRAGGED` = BIT(4))
- `tests/core/source/ui/test_suite_ui_ui_draggable.c`
- `tests/core/include/ui/test_suite_ui_ui_draggable.h`

---

## 1. Problem Identification

**Flagged module:** `m_ui_draggable__dropped_handler__default` — `core/source/ui/ui_draggable.c:63-85`
**Correctness Verdict:** Incorrect

The dropped handler clears `UI_FLAGS__BIT_IS_FOCUSED` (BIT 1) but fails to clear `UI_FLAGS__BIT_IS_BEING_HELD` (BIT 3) and `UI_FLAGS__BIT_IS_BEING_DRAGGED` (BIT 4). The codebase provides `set_ui_element_as__dropped()` — a `static inline` in `core/include/ui/ui_element.h:410` that atomically clears both drag-related flags — yet this function is never invoked within the handler.

This is a **State Desync**: the handler's semantic intent (transition the element out of its dragged/held state and into a resting state) is only partially fulfilled. The sibling `m_ui_draggable__dragged_handler__default` (`ui_draggable.c:29-61`) sets both `UI_FLAGS__BIT_IS_FOCUSED` and `UI_FLAGS__BIT_IS_BEING_DRAGGED` when dragging begins; the dropped handler should symmetrically call `set_ui_element_as__dropped()` to clear the drag-related state. The **Representation Invariant** of a dropped element — "no `IS_BEING_HELD` or `IS_BEING_DRAGGED` flags set" — is violated.

## 2. Impact Assessment

**Caller 1 — `handle_drop_in__ui_manager` (`core/source/ui/ui_manager.c:440-480`):**
This function calls `set_ui_element_as__dropped(p_ui_element__focused)` at line 449, *before* invoking `m_ui_dropped_handler` at line 475. In this path, the flags are cleared by the caller, compensating for the handler's omission. This creates a **Coupled** dependency: the handler's correctness relies on the caller performing the flag-clearing. This is a **Single Source of Truth (SSOT)** violation — the responsibility for clearing drag state is split between the caller and the handler rather than centralized within the handler itself.

**Caller 2 — `m_ui_drop_zone__receive_drop_handler__default` (`core/source/ui/ui_drop_zone.c:44-92`):**
This function invokes `m_ui_dropped_handler` on the child element at line 77 *without* first calling `set_ui_element_as__dropped`. In this path, the flags are never cleared, and the element retains `IS_BEING_HELD` and `IS_BEING_DRAGGED` after the drop. This is the actively-broken path.

**Downstream reliance on the broken flags:**
After a drop through the drop-zone path, the retained drag flags cause incorrect routing in the UI manager's input polling loop:

- `poll_ui_manager__update_for__clicked_and_dropped` (`ui_manager.c:482-499`) checks `is_ui_element__being_dragged` (line 491). On the next click-release, it routes to `handle_drop_in__ui_manager`, treating the element as still being dragged.
- `poll_ui_manager__update_for__held` (`ui_manager.c:~432-455`) checks `is_ui_element__being_dragged` (line ~440). On the next click-held, it routes to `poll_ui_manager__update_for__drag`, continuing to drag the element as if no drop occurred.
- `poll_ui_manager__update_for__drag` (`ui_manager.c:~415-430`) checks `is_ui_element__being_held` (line ~425) to set `IS_BEING_DRAGGED`, perpetuating the stale state.

**Reliance on the broken behavior as a de facto contract:**
No production code relies on the flags remaining set after a drop through the drop-zone path. The `handle_drop_in__ui_manager` path clears them externally. The drop-zone path's failure to clear is an oversight, not an intentional contract.

**Test coverage:**
The existing test suite (`tests/core/source/ui/test_suite_ui_ui_draggable.c`) contains 4 tests, all targeting `initialize_ui_element_as__draggable`. None test `m_ui_draggable__dropped_handler__default`. No tests assert on the broken or correct flag-clearing behavior. The drop-zone test suite (`tests/core/source/ui/test_suite_ui_ui_drop_zone.c`) similarly only tests initialization.

## 3. Resolution Assessment

**Primary fix — `m_ui_draggable__dropped_handler__default` (`core/source/ui/ui_draggable.c`):**
Insert a call to `set_ui_element_as__dropped(p_this_draggable)` after the existing `set_ui_element_as__NOT_focused(p_this_draggable)` call and before the null-parent early return. This ensures the drag-related flags are cleared regardless of whether the element has a parent, satisfying the **Postcondition** that a dropped element has no `IS_BEING_HELD` or `IS_BEING_DRAGGED` flags.

The corrected function body becomes:
```c
void m_ui_draggable__dropped_handler__default(
        UI_Element *p_this_draggable,
        Game *p_game,
        Graphics_Window *p_graphics_window) {
    Hitbox_AABB_Manager *p_hitbox_aabb_manager =
        (Hitbox_AABB_Manager*)get_pV_hitbox_manager_from__graphics_window(
                p_game, 
                p_graphics_window);

    set_ui_element_as__NOT_focused(p_this_draggable);
    set_ui_element_as__dropped(p_this_draggable);  // <-- ADDED

    if (!p_this_draggable->p_parent) {
        return;
    }

    set_position_3i32_of__ui_element(
            p_game,
            p_graphics_window,
            p_this_draggable, 
            get_position_3i32_from__p_ui_element(
                p_hitbox_aabb_manager,
                p_this_draggable->p_parent));
}
```

- **Implementation change:** Add one line (`set_ui_element_as__dropped(p_this_draggable)`). `set_ui_element_as__dropped` is already available as a `static inline` in `ui_element.h`, which `ui_draggable.c` includes. No header changes required.
- **Caller updates:** No caller code changes are strictly required. The `set_ui_element_as__dropped` call in `handle_drop_in__ui_manager` (`ui_manager.c:449`) becomes redundant — it is **idempotent** (clearing already-cleared flags is a no-op). It can be retained for defense-in-depth or removed for **Don't Repeat Yourself (DRY)**. Recommended: retain it, since `handle_drop_in__ui_manager` calls it *before* checking whether a dropped handler exists — removing it would leave elements without a dropped handler uncleared on the UI-manager drop path.
- **Drop-zone path:** Automatically fixed by the handler change — no changes needed in `ui_drop_zone.c`.
- **Tests:** New tests needed (see Section 4).

**Recommended follow-up (related, not in this review's scope):**
Audit all other `m_ui_*__dropped_handler__default` implementations (e.g., button, slider) to verify they also call `set_ui_element_as__dropped`. If any omit it, the same **State Desync** pattern may exist elsewhere.

## 4. Test Verification Checklist

Surveyed: `tests/core/source/ui/test_suite_ui_ui_draggable.c` (4 tests, Munit framework).

| Test | Asserts | Affected by fix? |
|------|---------|------------------|
| `initialize_ui_element_as__draggable__sets_kind` | kind == `UI_Element_Kind__Draggable` | No — unaffected. |
| `initialize_ui_element_as__draggable__sets_dragged_handler` | dragged handler present | No — unaffected. |
| `initialize_ui_element_as__draggable__sets_dropped_handler` | dropped handler present | No — unaffected. |
| `initialize_ui_element_as__draggable__custom_drag_handler` | custom handler set | No — unaffected. |

**Findings:**
- No existing tests exercise `m_ui_draggable__dropped_handler__default`. The fix introduces no regression risk to existing assertions.
- The dropped handler requires a `Game`, `Graphics_Window`, and `Hitbox_AABB_Manager` to run, making unit testing more involved than the initialization tests. Tests should use the same Munit framework and mocking/construction patterns as the drop-zone tests.
- **Recommended new tests** (terminology from `testing.md`):
  - `Property Based Testing`: After invoking the dropped handler on a draggable element with `IS_BEING_HELD` and `IS_BEING_DRAGGED` set, assert both flags are cleared and `IS_FOCUSED` is cleared — regardless of whether the element has a parent.
  - `Round Trip Check`: Set drag flags → invoke dropped handler → assert flags cleared. Then invoke dragged handler → assert flags set. Verify the state machine is symmetric.
  - `Equivalence Check`: Assert that calling `set_ui_element_as__dropped` directly produces the same flag state as invoking the dropped handler (for the flag-clearing aspect).
  - `Mutation Testing`: Mutate the handler to remove the `set_ui_element_as__dropped` call and confirm the new tests detect the regression.
- **Blast radius on tests:** Low. No existing test assertions are invalidated. New test cases should be added to cover the dropped handler's flag-clearing behavior.

## 5. Blast Radius Summary

- **Files changed:** 1 (`core/source/ui/ui_draggable.c` — one line added; no signature or header changes).
- **Behavior-preserving for current callers:** Yes. The `handle_drop_in__ui_manager` path already clears the flags externally; the handler now self-clears (idempotent overlap). The drop-zone path is fixed (previously broken, now correct).
- **De facto contracts invalidated:** The implicit assumption that "the caller is solely responsible for clearing drag flags" is invalidated — the handler now takes ownership. This is the desired centralization (**SSOT**). No caller relied on the handler *not* clearing flags.
- **Phased approach needed:** No. The change is a single-line, additive, idempotent fix with no cascading caller changes required.
- **Test blast radius:** Low. Add new test cases for the dropped handler; no existing tests are invalidated.
