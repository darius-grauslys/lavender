# Planning: collision_resolver_aabb.h — Incorrect Modules

**Review source:** `agents/core/review/include/collisions/collision_resolver_aabb.h/incorrect_modules.md`

**Source files reviewed (read-only):**
- `core/include/collisions/collision_resolver_aabb.h`
- `core/source/collisions/collision_resolver_aabb.c`
- `core/source/world/world.c` (sole caller: `manage_world`)
- `core/source/collisions/collision_node.c` (callee: `poll_for__collisions_within_this__collision_node`)
- `tests/core/source/collisions/test_suite_collisions_collision_resolver_aabb.c`

---

## 1. Problem Identification

Single flagged unit: `poll_collision_resolver_aabb` (`core/source/collisions/collision_resolver_aabb.c`, line 124). Verdict: **Incorrect**. Two independent defects break the documented contract (a 3×3 local-space scan + independent handler dispatch).

**Defect A — Guard tests the wrong handler (line 151).**
The tile-collision poll is gated by `if (f_hitbox_aabb_collision_handler)` but the call it protects forwards `f_hitbox_aabb_tile_touch_handler`. This is a **Mode Confusion** / **State Desync**: the guard's tested value and the value actually used are two different function pointers. The **Postcondition** "tile-collision polling occurs when the tile-touch handler is non-NULL" is violated. Consequences:
- collision handler NULL + tile-touch handler non-NULL → tile polling silently skipped (defeats the tile-touch handler).
- collision handler non-NULL + tile-touch handler NULL → `poll_hitbox_aabb_for__tile_collision` reaches its internal `f_hitbox_aabb_tile_touch_handler(...)` call (line ~470) with a NULL pointer on any unpassable tile → NULL-call.

**Defect B — South block checks south, polls east (lines 233–242).**
The guard tests `is_local_space__active(p_local_space->p_local_space__south)` but the poll passes `get_p_collision_node_from__local_space(p_local_space->p_local_space__east)`. This is a copy-paste **Aliasing Bug** / **State Desync**: the guard and its argument reference two different local spaces. Consequences (both **active** in the default config):
- The south neighbor's collision node is never polled → AABB collisions with hitboxes resident only in the south local space are missed.
- The east neighbor's collision node is polled twice (once in the east block, once here). Because the callee `poll_for__collisions_within_this__collision_node` invokes the collision handler per colliding hitbox and the default handler **mutates velocity** (non-**Idempotent**), east-resident collisions are displaced twice per tick.

## 2. Impact Assessment

**Sole caller — `manage_world` (`core/source/world/world.c`, line 99).**
It passes `p_world->f_hitbox_aabb_collision_handler` and `p_world->f_hitbox_aabb_tile_touch_handler`, both set to the `__default` handlers in `initialize_world`. In the default config both are non-NULL:
- **Defect A is latent** here: because the collision handler is non-NULL, tile polling does occur, so current gameplay is unaffected. The fix removes a latent hazard (wrong-handler coupling + NULL-call path) rather than changing present behavior.
- **Defect B is active** here: south collisions are missed and east collisions are double-displaced every tick. This broken behavior is the **de facto contract** the running game currently exhibits; correcting it changes runtime collision outcomes (a non-behavior-preserving change for the current binary).

**Callee — `poll_for__collisions_within_this__collision_node` (`collision_node.c`, line 151).**
Shared and correct; not **Idempotent** (handler invoked per colliding entry, mutating velocity). The resolver over-calls it (east twice). Fixing the resolver to poll each of the 9 local spaces exactly once restores single application. No change required to the callee.

**Same-file callee — `poll_hitbox_aabb_for__tile_collision` (line 286).**
Internally invokes `f_hitbox_aabb_tile_touch_handler` with no NULL guard. After Fix A gates on the tile-touch handler, this call is only reached when the handler is non-NULL, so the NULL-call path disappears. No mandatory change; an optional defensive NULL check hardens it independently.

**Data structures / headers.**
None affected. The `Local_Space` neighbor chain representation and the `poll_collision_resolver_aabb` signature are unchanged; only which node the resolver selects to poll is corrected. No `.h` edits.

## 3. Resolution Assessment

Both fixes are localized to `poll_collision_resolver_aabb`; no signature, header, or caller changes.

**Fix A (Defect A):** Change line 151 from
`if (f_hitbox_aabb_collision_handler)` → `if (f_hitbox_aabb_tile_touch_handler)`.
- Callers: `world.c` needs no change (both handlers non-NULL).
- Optional: add a defensive `if (!f_hitbox_aabb_tile_touch_handler) return;` at the top of `poll_hitbox_aabb_for__tile_collision` so the callee is robust independent of its guard.

**Fix B (Defect B):** In the south block (line 239), change
`p_local_space->p_local_space__east` → `p_local_space->p_local_space__south`.
- Callers: no change.
- Effect: south node polled once, east node polled once → the intended 3×3 grid (center + N/NE/E/SE/S/SW/W/NW) is complete and each local space is polled exactly once.

**Ordering / phasing:** Recommended two-phase, single-file. Phase 1 = Fix B (active, gameplay-visible; land with its regression test first). Phase 2 = Fix A (latent contract hardening). Both may ship in one commit; staging the tests bounds regression risk.

## 4. Test Verification Checklist

**Existing suite** (`test_suite_collisions_collision_resolver_aabb.c`): covers only the default handlers (crash-free), direct custom-handler invocation, and `is_hitbox_aabb__colliding`. It **never calls `poll_collision_resolver_aabb`**, so no existing assertion exercises either defect and **none is invalidated** by the fixes.

**New tests required** (add to the existing suite):
- **Fix A — guard independence.** *Equivalence Check*: collision handler NULL + tile-touch handler non-NULL over an unpassable tile ⇒ `tile_touch_handler_call_count > 0`. Collision handler non-NULL + tile-touch handler NULL ⇒ no crash, `tile_touch_handler_call_count == 0`.
- **Fix B — south scan.** *Equivalence Check*: a colliding hitbox resident only in the south local space ⇒ collision handler fires exactly once (proves the south node is polled). An east-resident hitbox ⇒ fires exactly once (proves no double-poll).
- **Full grid.** *Property Based Testing*: seed one colliding hitbox in each of the 8 neighbor local spaces and assert each yields exactly one handler invocation (verifies no missed neighbor and no duplicate).
- *Mutation Testing* optional: confirm the new tests fail when either line is reverted to the buggy form.

**Test blast radius:** Low–Medium. Only additive test functions; nothing existing breaks. Phased (Fix B test, then Fix A test) is recommended but not mandatory.

## 5. Blast Radius Summary

- **Files changed:** 1 — `core/source/collisions/collision_resolver_aabb.c` (two one-line edits; optional one-line NULL guard in the same file). No `.h`, no `world.c` changes.
- **Behavior-preserving for current callers?** Fix A: **yes** for the sole caller (both handlers always non-NULL) — it only removes a latent hazard. Fix B: **no** — it corrects active runtime collision behavior (south now detected, east no longer double-displaced).
- **De facto contracts invalidated:** The running game implicitly relies on east being double-resolved and south being ignored. Any gameplay tuned around the broken displacement (entity placement, collision-magnitude tuning) should be re-validated after Fix B.
- **Phased approach needed:** Recommended (Phase 1 = Fix B + test; Phase 2 = Fix A + test) to isolate the gameplay-visible change from the latent-contract hardening.
