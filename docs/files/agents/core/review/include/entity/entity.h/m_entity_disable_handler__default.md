# Function Review: m_entity_disable_handler__default

## 1. Header
- **Function name:** `m_entity_disable_handler__default`
- **File of origin:** `core/source/entity/entity.c` (currently lines 91-114 in the reviewed source; declared in `core/include/entity/entity.h:22`)

## 2. Semantic
Default disable handler for an `Entity`: soft-deactivates the entity's AABB hitbox by clearing its active flag so it no longer participates in collision/overlap checks, without releasing or removing the hitbox from its manager's pool. It is the symmetric counterpart of `m_entity_enable_handler__default` (which sets the active flag) and the soft sibling of `m_entity_dispose_handler__default` (which releases the hitbox from the pool). Installed as the entity's `m_entity_disable_handler` function pointer by `initialize_entity` (entity.c:126-127).

## 3. Pre-conditions
1. `p_this_entity` must be non-NULL. It is dereferenced via `GET_UUID_P(p_this_entity)` (entity.c:109) to look up its UUID; passing NULL is undefined behavior.
2. `p_game` must be non-NULL. It is dereferenced unconditionally via `get_p_hitbox_context_from__game(p_game)` -> `&p_game->hitbox_context` (game.h:193) to obtain the `Hitbox_Context`; there is no null guard, even in debug builds.
3. `p_world` must be non-NULL. It is dereferenced via `GET_UUID_P(p_world)` -> `(&p_world->uuid)` (serialization_header.h:19) to select the world's hitbox manager; there is no null guard.
4. `p_game->hitbox_context` must be a valid, initialized `Hitbox_Context` (no per-call validation).
5. `p_game` + `p_world`'s UUID must map to a registered `Hitbox_AABB_Manager` for this handler to have any effect. If no manager is registered for the world's UUID, the handler has no effect in debug (early return) and exhibits latent undefined behavior in release (see Implementation Correctness).
6. The signature must match the `m_Entity_Handler` typedef `void (*)(Entity*, Game*, World*)` (defines_weak.h:202). The definition matches the declaration/assignment exactly (only the first parameter is renamed `p_this_entity` vs `p_entity_self`, which is immaterial).

## 4. Post-conditions
1. If a `Hitbox_AABB` is associated with `p_this_entity`, its `HITBOX_FLAG__IS_ACTIVE` bit is cleared (the hitbox transitions to the "not active / disabled" state) via `set_hitbox_aabb_as__disabled` (entity.c:112 -> hitbox_aabb.h:129 -> hitbox.h:41).
2. The hitbox itself remains allocated in the manager's pool; this handler does NOT release, deallocate, or remove the hitbox (`m_entity_dispose_handler__default` performs that release via `release_hitbox_aabb_from__hitbox_aabb_manager`).
3. `p_game` and `p_world` are read but not mutated by this function.
4. Returns `void` (no return value).
5. If no manager is found for the world (debug builds only), the function returns early with no mutation.
6. If no `Hitbox_AABB` is registered for the entity's UUID, no mutation occurs.

## 5. Correctness Verdict
Correct

The function correctly fulfills its intent: it clears the active flag on the entity's associated AABB hitbox, which is exactly what "disable the entity" means in this codebase. The defects documented below do not cause the disable operation itself to fail; they affect debug diagnostics and release-mode robustness (both of which are pre-condition/contract concerns shared with the sibling enable/dispose handlers).

## 6. Semantic Alignment
- **Intent vs. implementation:** Aligned. The semantic intent is to soft-deactivate the entity's hitbox; the implementation clears `HITBOX_FLAG__IS_ACTIVE` through the dedicated `set_hitbox_aabb_as__disabled` helper (entity.c:112).
- **Symmetry with enable:** `m_entity_enable_handler__default` sets `HITBOX_FLAG__IS_ACTIVE` via `set_hitbox_aabb_as__active` (entity.c:87); this handler clears it via `set_hitbox_aabb_as__disabled` (entity.c:112). The pair is symmetric and mutually exclusive on the same flag. Aligned.
- **"Disabled" vs "not active" naming:** There is no dedicated "disabled" flag; in this codebase "disabled" is implemented as "not active" (clear `HITBOX_FLAG__IS_ACTIVE`, hitbox.h:41-45). `is_hitbox_aabb__active` (hitbox_aabb.h:119) consults the same flag. The naming is a codebase-wide convention and the function is consistent with it, but it is worth noting that "disable" here is not a distinct state from "not active".
- **Distinct from dispose (RAII):** Under Lavender semantics, "initialization" means cleaning/resetting a struct to return it to a free pool, and "dispose" corresponds to the RAII-style release. This "disable" handler performs neither deallocation nor pool return — it only flips the active flag. This is the correct separation of concerns: disable is reversible (re-enabled later), dispose is terminal (release). No RAII coupling defect is present here.
- **Defect in debug diagnostics (does not affect disable behavior):** The debug error string is copy-pasted from the dispose handler: `debug_error("m_entity_dispose_handler__default, p_hitbox_aabb_manager == 0.")` (entity.c:102). It should read `m_entity_disable_handler__default`. This mislabels debug output but does not change the disable logic. (The enable handler at entity.c:77 has the identical copy-paste bug.)

## 7. Implementation Correctness
- **Type compatibility:** The definition `void m_entity_disable_handler__default(Entity*, Game*, World*)` matches the `m_Entity_Handler` typedef (defines_weak.h:202) and the declaration (entity.h:22) exactly: `Entity*` -> `Entity*`, `Game*` -> `Game*`, `World*` -> `World*`. No implicit conversion or truncation. `set_hitbox_aabb_as__disabled(Hitbox_AABB*)` receives `p_hitbox_aabb` of type `Hitbox_AABB*`; `get_p_hitbox_aabb_by__entity_from__hitbox_aabb_manager(Hitbox_AABB_Manager*, Entity*)` receives the manager pointer and `p_this_entity`; all types line up.
- **Opaque cast:** The result of `get_pV_hitbox_manager_from__hitbox_context` (type `void*`, hitbox_context.h:89) is cast to `Hitbox_AABB_Manager*` (entity.c:96-99). This is the standard opaque-pointer hand-off for the default/AABB path and is valid when the world's manager is an AABB manager; the `#warning` (entity.c:95) correctly flags this as tech-debt to be replaced with an opaque hitbox pointer.
- **Undefined behavior / null dereference:**
  - `p_game` and `p_world` are dereferenced with no null guard (even in debug) via `get_p_hitbox_context_from__game` and `GET_UUID_P`. Passing NULL for either is undefined behavior; the contract is the caller's responsibility.
  - The null check on `p_hitbox_aabb_manager` (entity.c:101) is guarded by `#ifndef NDEBUG`, so it is debug-only. In release builds, if no manager is registered for the world's UUID, `p_hitbox_aabb_manager` is NULL and is passed to `get_p_hitbox_aabb_by__entity_from__hitbox_aabb_manager` (entity.c:106), which forwards the NULL to `get_p_hitbox_aabb_by__uuid_u32_from__hitbox_aabb_manager` (hitbox_aabb_manager.c:308-321). That function's own null check is also debug-only (hitbox_aabb_manager.c:311-315), so in release it proceeds to access `p_hitbox_aabb_manager->pM_pool_of__hitboxes` (hitbox_aabb_manager.c:318) — a member access on a NULL pointer, i.e., undefined behavior.
  - This release-mode gap is a latent crash path, but it is a codebase-wide convention: the sibling `m_entity_dispose_handler__default` and `m_entity_enable_handler__default` use the identical debug-only null-guard pattern (entity.c:47-51 and entity.c:75-79). It is a pre-condition that the world has a registered hitbox manager before these handlers run.
- **Off-by-one / bounds:** No loops or indexed array access within this function. None.
- **Validation appropriateness:** Consistent with the sibling handlers. The debug null-guard plus the truthy `if (p_hitbox_aabb)` check before mutation are appropriate for this role; release-mode hardening would require extending the convention (out of scope for this single-function review).

## 8. Side Effects
- **Mutates** the `Hitbox_AABB` associated with `p_this_entity` (if one exists) by clearing its `HITBOX_FLAG__IS_ACTIVE` flag, transitioning that hitbox to the "not active / disabled" state. The hitbox remains in the manager's pool (not released).
- **Reads** `p_game` (its `hitbox_context`) and `p_world` (its UUID) only; it does not write to them.
- **Debug builds only:** emits a `debug_error` diagnostic (and returns early) when no hitbox manager is found for the world. In release builds there is no logging and no early return for that case.
- No dynamic allocation, deallocation, I/O, or global state changes are performed by this function itself. (Callee sites such as `get_p_hitbox_context_from__game`, `get_pV_hitbox_manager_from__hitbox_context`, `set_hitbox_aabb_as__disabled`, and the dehashing lookup are out of scope and omitted per review convention.)
