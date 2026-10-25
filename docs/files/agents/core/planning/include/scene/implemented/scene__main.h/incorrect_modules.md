# Planning: scene__main.h — Incorrect Modules

**Review source:** `agents/core/review/include/scene/implemented/scene__main.h/incorrect_modules.md`

**Source files reviewed (read-only):**
- `core/include/scene/implemented/scene__main.h`
- `core/source/scene/implemented/scene__main.c`
- `core/include/scene/scene_manager.h`
- `core/source/scene/scene_manager.c`
- `core/include/game.h`
- `core/source/game.c`
- `core/include/defines.h`
- `core/include/defines_weak.h`
- `core/include/types/implemented/scene/scene_kind.h`
- `core/include/scene/scene.h`
- `core/source/scene/scene.c`
- `tests/core/source/scene/implemented/test_suite_scene_implemented_scene__main.c`
- `tests/core/include/scene/implemented/test_suite_scene_implemented_scene__main.h`

---

## 1. Problem Identification

### `m_unload_scene_as__main_handler`

**Verdict:** Incorrect

The function `m_unload_scene_as__main_handler` is registered as the `m_Unload_Scene` handler for `Scene_Kind__None` (the default/initial scene) via `register_scene__main()`, which is invoked through `register_scenes()` during `initialize_game()`. However, the function body is completely empty — it contains only `// GEN-UNLOAD-BEGIN` and `// GEN-UNLOAD-END` markers with no implementation.

The `m_Unload_Scene` typedef is documented as "Cleans up p_game following scene exit" (see `defines.h`, line 1361). An unload handler is expected to perform cleanup operations such as releasing allocated resources, resetting scene state, and freeing memory. The absence of any implementation constitutes a **Stub-real divergence**: the function is registered as a real handler but behaves as a stub, producing no observable cleanup. This also represents a **Translation Gap** — the semantic intent of scene cleanup is not translated into executable code.

The companion load handler (`m_load_scene_as__main_handler`) is similarly a stub (empty `GEN-LOAD-BEGIN`/`GEN-LOAD-END`), and the enter handler's frame/pre-render/post-render sections are also empty. While no resources are currently allocated during load, the unload handler's emptiness violates the **Representation Invariant** that a `Scene` should be returned to a clean, initialized state after unload (i.e., `is_active == false`, `p_scene_data == 0`).

## 2. Impact Assessment

### Invocation site

The unload handler is invoked in `run_game()` in `core/source/game.c` (lines 717–721):

```c
debug_info("unloading scene.");
if (p_active_scene->m_unload_scene_handler)
    p_active_scene->m_unload_scene_handler(
            p_active_scene,
            p_game);
```

This call occurs after `m_enter_scene_as__main_handler` returns (i.e., when the main game loop exits). The `Scene_Kind__None` scene is the initial scene activated in `run_game()` when no active scene exists.

### Callers relying on the broken behavior

- **`run_game()` in `game.c`**: Calls the unload handler after the enter handler returns. Currently, the empty handler means no cleanup is performed, and the loop simply proceeds to check `p_active_scene` again. If the unload handler were to set `p_active_scene` to null (via `quit_scene_state_machine` or similar), it would terminate the game loop — but currently it does nothing.
- **`initialize_game()` in `game.c`**: Calls `register_scenes()` → `register_scene__main()`, which registers the empty unload handler. No assumption is coupled to the handler being empty; the registration simply stores the function pointer.
- **`is_scene__valid()` in `scene.h`**: Checks `m_enter_scene_handler` (not `m_unload_scene_handler`), so implementing cleanup in the unload handler will not affect validity checks.
- **`set_active_scene_for__scene_manager()` in `scene_manager.c`**: Sets `is_active = false` on the old scene when switching. If the unload handler also resets `is_active`, this would be redundant but not conflicting.
- **`quit_scene_state_machine()` in `scene_manager.c`**: Sets `p_active_scene = 0` without calling the unload handler. This is a separate code path that bypasses the unload handler entirely. (Note: `quit_scene_state_machine` also contains a separate **Boundary Condition** bug — the null check is inverted: `if (!p_scene_manager->p_active_scene)` should be `if (p_scene_manager->p_active_scene)` — but this is outside the scope of this review.)

### Data structures affected

- **`Scene` struct** (`defines.h`, lines 1365–1373): Contains `p_scene_data`, `is_active`, and handler function pointers. After unload, the **Representation Invariant** expects `is_active == false` and `p_scene_data == 0` (matching the state set by `initialize_scene()`). The empty handler fails to enforce this.
- **`Scene_Data__Game`** (`defines.h`, lines 1347–1350): A struct containing `timer_for__hud_notification__u8` and `timer_for__typer_sliding__u8`. If the load handler were extended to allocate and attach a `Scene_Data__Game` to `p_scene_data`, the empty unload handler would leak it. This represents a latent **Conservation Law** violation.

### De facto contracts

No existing code relies on the unload handler being empty as a de facto contract. The `run_game()` loop simply proceeds regardless of what the unload handler does. However, if the unload handler is implemented to reset `p_scene_data` or `is_active`, any future code that assumes scene state persists after the enter handler returns would be invalidated.

## 3. Resolution Assessment

### Plan

Implement `m_unload_scene_as__main_handler` to fulfill the semantic contract of the `m_Unload_Scene` typedef: "Cleans up p_game following scene exit."

#### Step 1: Reset scene state

The unload handler should reset the `Scene` struct to its initialized state, matching the postconditions of `initialize_scene()`:

- Set `p_this_scene->is_active = false`
- Set `p_this_scene->p_scene_data = 0` (if it was allocated, free it first)

This enforces the **Representation Invariant** that a scene is in a clean state after unload.

#### Step 2: Free `p_scene_data` if allocated

If `p_this_scene->p_scene_data` is non-null, it should be freed before being set to null. Although the current load handler does not allocate `p_scene_data`, implementing this defensively ensures that if the load handler is later extended (e.g., to allocate a `Scene_Data__Game`), the unload handler will properly conserve the resource (**Conservation Law**).

```c
if (p_this_scene->p_scene_data) {
    free(p_this_scene->p_scene_data);
    p_this_scene->p_scene_data = 0;
}
```

#### Step 3: Reset game-level state

The unload handler receives `Game *p_game`, which may have had state set up during the enter handler's game loop. Any game-level state that was initialized for this scene should be reset. However, since the enter handler's frame/pre-render/post-render sections are currently empty (stubs), there is no game-level state to reset at this time. This step should be revisited if the enter handler is extended.

#### Step 4: Update `quit_scene_state_machine` (optional, out of scope)

The `quit_scene_state_machine()` function in `scene_manager.c` does not call the unload handler. If scene unloading is expected to be uniform across all exit paths, `quit_scene_state_machine` should invoke `p_scene_manager->p_active_scene->m_unload_scene_handler` before nulling the active scene pointer. However, this is a separate concern from the empty handler body and may be tracked separately.

### Caller impact

- **`run_game()` in `game.c`**: The call site already guards with `if (p_active_scene->m_unload_scene_handler)`, so no caller changes are needed. The implementation will be invoked transparently.
- **`register_scene__main()`**: No changes needed — the function pointer is already correctly registered.
- **`set_active_scene_for__scene_manager()`**: No changes needed. The redundant `is_active = false` in the unload handler is harmless.

### Test verification

The existing test suite (`test_suite_scene_implemented_scene__main.c`) contains only one test:

```c
TEST_FUNCTION(register_scene__main__does_not_crash_on_initialized_manager) {
    Scene_Manager scene_manager;
    initialize_scene_manager(&scene_manager);
    register_scene__main(&scene_manager);
    return MUNIT_OK;
}
```

This test verifies registration but does not test the unload handler's behavior. New tests are needed:

- **`Property Based Testing`**: Verify that after calling the unload handler, the `Scene` struct's `is_active` is `false` and `p_scene_data` is null, matching the state set by `initialize_scene()`.
- **`Round Trip Check`**: Verify that a load → enter → unload sequence leaves the scene in a clean state (i.e., `is_scene__valid` still returns true because `m_enter_scene_handler` is preserved, while `is_active` is false and `p_scene_data` is null).
- **`Equivalence Check`**: Verify that the unload handler's effect is equivalent to calling `initialize_scene()` on the scene's mutable state (excluding handler function pointers).

### Blast radius for tests

- **Existing tests**: The single existing test (`register_scene__main__does_not_crash_on_initialized_manager`) will not be invalidated by the fix, as it only tests registration.
- **New tests**: 2–3 new test cases are recommended for the unload handler.
- **Blast radius**: Low — the change is localized to one function body in `scene__main.c`.

## 4. Test Verification Checklist

- [ ] **Existing test survey**: The existing test only checks registration, not unload behavior. No existing assertions will be invalidated.
- [ ] **New test: state reset after unload**: Verify `is_active == false` and `p_scene_data == 0` after calling the unload handler. (**Property Based Testing**)
- [ ] **New test: round-trip load/enter/unload**: Verify the scene returns to a clean state after a full lifecycle. (**Round Trip Check**)
- [ ] **New test: p_scene_data cleanup**: If `p_scene_data` is set to a non-null value before unload, verify it is freed and set to null. (**Equivalence Check**)
- [ ] **Edge cases**: Verify the handler does not crash when `p_this_scene` or `p_game` is null (though preconditions state they must be valid). (**Fuzzing** for boundary/edge case coverage)
- [ ] **Blast radius**: Low — only the unload handler function body changes; no caller updates required.

## 5. Blast Radius Summary

- **Files needing changes**: 1 — `core/source/scene/implemented/scene__main.c` (unload handler body only).
- **Behavior-preserving for callers**: Yes — the call site in `game.c` already guards with a null check on the handler pointer, and no code relies on the handler being empty.
- **Phased approach needed**: No — the change is localized and low-risk.
- **De facto contracts invalidated**: None — no code depends on the unload handler being a no-op.
- **Test impact**: Low — existing test is unaffected; 2–3 new tests recommended.
