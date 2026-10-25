# Planning: world.h — Incorrect Modules

**Review source:** `agents/core/review/include/world/world.h/incorrect_modules.md`

**Source files reviewed (read-only):**
- `core/include/world/world.h`
- `core/source/world/world.c`
- `core/include/defines.h` (`typedef struct World_t`)
- `core/source/collisions/core/aabb/hitbox_aabb_manager.c` (caller chain)
- `core/source/game_action/core/hitbox/game_action__hitbox.c` (caller chain)
- `tests/core/source/world/test_suite_world_world.c` (test survey)

**Flagged incorrect functions (7):**
`initialize_world`, `poll_world_for__scrolling`, `manage_world__entities`,
`allocate_entity_into__world`, `save_world`,
`get_p_entity_from__world_using__3i32F4`, `poll_for_collision_node_update`.

---

## 1. Problem Identification

The `World` module contains **two distinct defect classes**: (a) **Stub-real divergence** —
functions whose declared semantic intent is unfulfilled because the body is a `debug_abort`
stub or is entirely missing; and (b) **logic/contract defects** in implemented functions —
a broken **Loop Invariant**, missing null guards (undefined behavior), and an ordering bug that
violates a membership **Invariant**.

| Function | Defect class | Core defect (one sentence) |
|----------|--------------|----------------------------|
| `initialize_world` | Incomplete init / State Desync | Resets only 15 of the 20 `World` fields, leaving `region_manager`, `structure_manager`, `camera`, `f_tile_render_kernel`, and `p_graphics_window_for__world` in an indeterminate state; also registers core items into the *game's* item manager instead of `p_world`'s. |
| `poll_world_for__scrolling` | Stub-real divergence | Body is `debug_abort(...)`; the trailing `return false` is unreachable dead code. No scrolling logic exists. |
| `manage_world__entities` | Broken Loop Invariant / State Desync | Uses `break` (not `continue`) on an unallocated entity slot, terminating iteration early and skipping all higher-index entities' update handlers. |
| `allocate_entity_into__world` | Missing implementation / Translation Gap | Declared in `world.h` but has **no definition anywhere** in the tree; any call site is a linker error. |
| `save_world` | Stub-real divergence | Body is `debug_abort(...)`; performs no serialization. Debug builds crash on call; release builds silently save nothing (inverse of `load_world` unimplemented). |
| `get_p_entity_from__world_using__3i32F4` | Missing Boundary Condition guards / UB | Dereferences `p_global_space->_serialization_header.uuid` and passes `p_collision_node` onward with **no null check**, though both lookups can legitimately return `NULL`. |
| `poll_for_collision_node_update` | Ordering bug / Invariant violation (State Desync) | Removes the entry from the old collision node **before** checking the new global space exists; on failure the entry is released to the pool and orphaned from all collision nodes. |

---

## 2. Impact Assessment

### Per-function blast radius

**`initialize_world` (Representation Invariant).**
- The `World` struct is a **Single Source of Truth** for world state; leaving five fields
  uninitialized breaks the **Representation Invariant** that a Lavender-style initializer resets
  *all* fields to safe defaults.
- Coupled readers already exist in `world.h` inline accessors: `get_p_camera_from__world`
  (returns `&p_world->camera`), `get_p_graphics_window_from__world` (returns the raw,
  uninitialized pointer), and `get_f_tile_render_kernel_of__world` (returns an uninitialized
  function pointer). Any of these called before a separate setter produces undefined behavior.
- The `register_core_items_into__item_manager(get_p_item_manager_from__game(p_game))` call is a
  **State Desync**: the game-level accessor resolves the item manager from the game's stored
  world, which may differ from `p_world`. Core items may be registered into the wrong manager.
- Correcting this invalidates any code that currently papers over the gap by setting those five
  fields ad hoc after init; such call sites become redundant but remain valid.

**`poll_world_for__scrolling` (Stub-real divergence).**
- No active caller was found in `core/source`; the function is not yet wired into a live loop.
  Blast radius is **Low** today, but any future wiring would abort the process in debug builds.
- The unreachable `return false` must be removed/replaced so the `bool` postcondition is real.

**`manage_world__entities` (broken Loop Invariant — HIGHEST live impact).**
- Called directly from `manage_world` (`world.c:111`), which is the per-frame world tick.
- The entity pool allocates/deallocates at arbitrary indices; `ptr_array_of__entities` may
  contain `NULL` at any index. A single deallocated slot at a low index causes every
  higher-index entity's `m_entity_update_handler` to be skipped — silent, cumulative gameplay
  breakage (frozen entities). This is a **de facto contract** violation: callers assume the
  function updates *all* active entities.
- Related latent pattern: `poll_hitbox_manager_for__movement` (`hitbox_aabb_manager.c`) uses the
  same `break`-on-null idiom; if hitboxes are deallocated non-contiguously it has the same defect.
  Out of scope for this plan but flagged for follow-up.

**`allocate_entity_into__world` (missing implementation).**
- No definition exists in the tree, so there is currently **no live caller** that compiles —
  the risk is latent (linker failure the moment a spawn path is added). Blast radius **Low** now;
  **High** once wired, since it is intended as the canonical entity-spawn convenience API.

**`save_world` (Stub-real divergence).**
- Intended as the inverse of `load_world` / `m_process__serialize_world`. Called only when leaving
  a world to the main menu. Debug builds crash; release builds silently drop the save (world name
  + PRNG seeds lost). Blast radius **Low** in frequency but with data-loss consequences.

**`get_p_entity_from__world_using__3i32F4` (missing Boundary Condition guards).**
- A read-only spatial query that may be called with an arbitrary position. Two unguarded null
  dereferences turn a "no entity here" query into undefined behavior instead of the documented
  `NULL` postcondition. Callers are coupled to the *documented* safe contract, so fixing it is
  behavior-preserving for valid inputs and eliminates UB for out-of-range positions.

**`poll_for_collision_node_update` (ordering bug — HIGHEST live impact).**
- **Actively in the per-frame loop**: `manage_world` → `poll_hitbox_manager_for__movement`
  (`hitbox_aabb_manager.c:323`) → `dispatch_game_action__hitbox` →
  `m_process__game_action__hitbox` (`game_action__hitbox.c:103`) → this function.
- The remove-before-check sequence violates the membership **Invariant** (an entity's entry is
  present in exactly one collision node). When the destination chunk's global space is not yet
  allocated, `remove_entry_from__collision_node` has already released the entry to the pool; the
  function then returns `false`, leaving the entity **orphaned** — invisible to collision
  detection until it re-crosses into an allocated chunk. This is a **Cascade Failure** source for
  any entity moving into ungenerated terrain.

### Cross-cutting note
Correcting `initialize_world` (adding the five field initializations) and correcting
`poll_for_collision_node_update` (reordering) both tighten **Invariants** that current code does
not depend on being broken — no de-facto contract relies on the buggy behavior, so fixes are
behavior-preserving for correct inputs.

---

## 3. Resolution Assessment

### `initialize_world`
- Add the five missing initialization calls, each delegating to the existing routine:
  - `initialize_region_manager(&p_world->region_manager);`
  - `initialize_structure_manager(&p_world->structure_manager);`
  - `initialize_camera_as__inactive(&p_world->camera);`
  - `set_f_tile_render_kernel_of__world(p_world, <default or 0>);` (establish a defined default)
  - `p_world->p_graphics_window_for__world = 0;` (NULL until assigned)
- Change `register_core_items_into__item_manager(get_p_item_manager_from__game(p_game))` →
  `register_core_items_into__item_manager(get_p_item_manager_from__world(p_world))` so the target
  manager matches the world being initialized.
- Callers: none need signature changes. Verify any ad-hoc post-init setters for these five fields
  are now redundant (safe to keep or remove).

### `poll_world_for__scrolling`
- Replace the `debug_abort` stub with real scrolling logic: compare player/camera position against
  viewport/chunk boundaries and update the graphics window viewport; return whether scrolling
  occurred. Remove the unreachable `return false`.
- If no live caller exists, gate the work: either implement minimally or mark the function
  explicitly unimplemented with a reachable `return false` (no abort) so debug builds do not crash.

### `manage_world__entities`
- Change line 162 `break;` → `continue;` so unallocated slots are skipped and iteration covers all
  `MAX_QUANTITY_OF__ENTITIES` slots. This is the one-line fix that restores the "update all active
  entities" contract.
- Callers: unchanged. Recommend a follow-up audit of the identical `break`-on-null idiom in
  `poll_hitbox_manager_for__movement`.

### `allocate_entity_into__world`
- Add the missing definition to `world.c`: delegate to
  `allocate_entity_in__entity_manager(get_p_entity_manager_from__world(get_p_world_from__game(p_game)), the_kind_of_entity)`,
  then allocate + position the entity's hitbox at `position__3i32F4`; return `NULL` on pool
  exhaustion. Keep the existing header declaration as-is (signature already correct).

### `save_world`
- Replace the `debug_abort` stub with a real serialization pass mirroring
  `m_process__serialize_world`: obtain the header path via `stat_world_header_file`, open it with
  `PLATFORM_open_file(..., "wb")`, write `_serialization_header` + `name` (WORLD_NAME_MAX_SIZE_OF
  bytes) + `repeatable_pseudo_random.seed__initial/seed__current_random` via
  `PLATFORM_write_file`, then `PLATFORM_close_file`. Make it the true inverse of `load_world`.

### `get_p_entity_from__world_using__3i32F4`
- After `get_p_global_space_from__global_space_manager(...)`, add a null guard: if `!p_global_space`
  return `0`. After `get_p_collision_node_by__uuid_64_from__collision_node_pool(...)`, add a null
  guard: if `!p_collision_node` return `0`. This restores the documented "return NULL when not
  found" postcondition and removes both UB paths. No caller changes needed.

### `poll_for_collision_node_update`
- **Reorder** so both global spaces are validated *before* any mutation:
  1. Look up `p_global_space__old`; if null → `debug_error`, return `false`.
  2. Look up `p_global_space__new`; if null → `debug_error`, return `false` **without removing**.
  3. Only then `remove_entry_from__collision_node(old)` and `add_entry_to__collision_node(new)`.
- This preserves the "entry present in exactly one collision node" **Invariant** on all paths.
  Callers unchanged (signature and return semantics preserved).

### Phasing
- **Phase 1 (correctness, low risk, do first):** `manage_world__entities` (`break`→`continue`),
  `get_p_entity_from__world_using__3i32F4` (null guards), `poll_for_collision_node_update`
  (reorder), `initialize_world` (5 fields + item-manager target). These are behavior-preserving
  for valid inputs and eliminate UB / state desync in the live loop.
- **Phase 2 (implementation, additive):** `allocate_entity_into__world` (add definition),
  `save_world` (implement serialization), `poll_world_for__scrolling` (implement or safely no-op).

---

## 4. Test Verification Checklist

**Test survey:** `tests/core/source/world/test_suite_world_world.c` does **not** reference any of
the seven functions, and no world-specific test asserts on their current (broken) behavior.
Therefore **no existing assertions are invalidated**; the gap is coverage, not contradictions.

Recommended new tests (terminology from `agents/terminologies/testing.md`):
- `manage_world__entities` — **Property Based Testing**: with a sparsely allocated entity pool
  (allocated slots non-contiguous, gaps at low indices), assert every *enabled* entity's update
  handler is invoked exactly once per tick. Guards the Loop Invariant.
- `get_p_entity_from__world_using__3i32F4` — **Fuzzing** over positions: positions in empty chunks
  / unallocated global spaces must return `NULL`, never crash (Boundary Condition coverage).
- `poll_for_collision_node_update` — **Property Based Testing** of the membership Invariant: after
  any old/new position pair, each entry appears in exactly one collision node; when the destination
  chunk is unallocated, return `false` and the entry remains in the *old* node (no orphaning).
- `initialize_world` — **Property Based Testing** / invariant check: after init, all 20 fields are
  in their defined default state (no indeterminate reads); core items registered into `p_world`'s
  item manager.
- `save_world` / `load_world` — **Round Trip Check**: save then load yields byte-identical header
  (name + PRNG seeds); an **Equivalence Check** against `m_process__serialize_world` output.
- `allocate_entity_into__world` — **Round Trip Check**: allocate at a position, then
  `get_p_entity_from__world_using__3i32F4` at the same position returns the same entity; pool
  exhaustion returns `NULL`.

**Test blast radius: Low.** No existing tests to update; all additions are new cases in the world
test suite. A phased rollout matching Phase 1 / Phase 2 above is appropriate (Phase 1 tests first,
as those fixes are the highest live impact).

---

## 5. Blast Radius Summary

- **Files changed:** `core/source/world/world.c` (6 of 7 functions live here) and, for
  `allocate_entity_into__world`, only `world.c` gains a definition (header already correct).
  No header signature changes required. Follow-up (out of scope): the analogous `break`-on-null
  idiom in `core/source/collisions/core/aabb/hitbox_aabb_manager.c`.
- **Behavior-preserving for current callers?** Yes for all Phase 1 fixes — they tighten invariants
  that no correct caller depends on being broken; valid-input behavior is unchanged.
- **De-facto contracts invalidated?** None. No code relies on the buggy behavior; the two live-loop
  bugs (`manage_world__entities`, `poll_for_collision_node_update`) are silent-correctness defects,
  not depended-upon semantics.
- **Phased approach needed?** Yes — Phase 1 (correctness fixes in the live per-frame loop) then
  Phase 2 (additive stub implementations). Phase 1 is small and low-risk; Phase 2 is larger and
  additive with no caller impact until wired in.
