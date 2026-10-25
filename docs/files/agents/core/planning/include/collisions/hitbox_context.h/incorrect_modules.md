# Planning: hitbox_context.h — Incorrect Modules

**Review source:** `agents/core/review/include/collisions/hitbox_context.h/incorrect_modules.md`

**Source files reviewed (read-only):**
- `core/include/collisions/hitbox_context.h`
- `core/source/collisions/hitbox_context.c`
- `core/include/collisions/hitbox_manager_instance.h`
- `core/source/entity/entity.c` (callers)
- `core/source/world/world.c` (callers)
- `tests/core/source/collisions/test_suite_collisions_hitbox_context.c`

---

## 1. Problem Identification

**Flagged:** `get_pV_hitbox_manager_from__hitbox_context` (static inline, `core/include/collisions/hitbox_context.h:88-97`) — **Incorrect**.

- **Missing validation / undefined behavior on failure path.** The function immediately dereferences the result of `get_p_hitbox_manager_instance_using__uuid_from__hitbox_context` (`->pVM_hitbox_manager`) without any null/validity check. The callee dehashes a contiguous array and returns `NULL` when the UUID is not found (e.g., `IDENTIFIER__UNKNOWN__u32`), so the miss path is a NULL pointer dereference — **undefined behavior** instead of the documented "return nothing on failure" **Postcondition**.
- **Broken Precontract.** The function's stated Precondition ("uuid must refer to an existing instance") is unenforced; a caller violating it triggers UB rather than a defined, observable failure.
- **Divergence from sibling idiom.** Every sibling accessor in the same module (`get_pV_hitbox_from__hitbox_context`, `release_hitbox_manager_from__hitbox_context`, `allocate_pV_hitbox_from__hitbox_context`, `get_max_quantity_of__hitboxes_in__hitbox_manager`) guards the lookup result before touching instance fields. This function alone skips the guard — a DRY / Single Source of Truth (SSOT) violation in error handling.
- **State Desync (documentation vs. behavior).** The header doc for `get_p_hitbox_manager_instance_using__uuid_from__hitbox_context` claims "Returns an invalid Hitbox_Manager_Instance when failing to find," but the implementation returns `NULL`. Two representations of the same failure contract have diverged, which is what made the missing guard plausible.

## 2. Impact Assessment

**Callers relying on the (broken) behavior:**

- `core/source/entity/entity.c` — 5 call sites (`m_entity_dispose_handler__default`, `m_entity_enable_handler__default`, `m_entity_disable_handler__default`, `m_entity_serialization_handler__default`, deserialization handler). Each casts the result to `Hitbox_AABB_Manager*`. Three sites carry a NULL guard wrapped in `#ifndef NDEBUG`; all sites assume a de facto contract of "valid pointer or NULL".
- `core/source/world/world.c` — 3 call sites in `manage_world` and the tile-touch path. Results are passed **directly, unguarded**, into `poll_collision_resolver_aabb` and `poll_hitbox_manager_for__movement`.

**How the fix invalidates coupled assumptions:**

- Today the miss path is UB *inside* the inline function, so caller-side NULL guards are dead code in practice — callers couple to a contract the function does not actually honor. Fixing the function to return `NULL` on miss **activates** those de facto contracts:
  - The `#ifndef NDEBUG` guards in `entity.c` become load-bearing only in debug; release builds still pass NULL downstream unguarded.
  - `world.c::manage_world` passes the pointer straight to `poll_collision_resolver_aabb`, which iterates the manager pool with **no NULL tolerance** (verified: no guard on `p_hitbox_aabb_manager`). A post-fix NULL would move the crash from the accessor into that callee — a relocated, not eliminated, defect unless callees or callers are hardened.
- **De facto contract to codify:** "lookup miss ⇒ return NULL; success ⇒ non-null opaque manager pointer." Callers currently assume this; the fix makes it true, but only if downstream callees (`poll_collision_resolver_aabb`, `poll_hitbox_manager_for__movement`, `get_p_hitbox_aabb_by__uuid_u32_from__hitbox_aabb_manager`) either tolerate NULL or all call sites are guarded.
- **Docs:** the stale "invalid instance" doc comment on the UUID getter must be corrected to "NULL on miss," otherwise the State Desync persists for the next reader.

## 3. Resolution Assessment

**Phase 1 — Fix the accessor (core change):**
- In `core/include/collisions/hitbox_context.h`, rewrite `get_pV_hitbox_manager_from__hitbox_context` to bind the lookup result, validate it with `is_p_hitbox_manager_instance__valid` (the module's existing validity predicate from `hitbox_manager_instance.h`; strictly stronger than a NULL check and keeps one SSOT for "valid instance"), log via `debug_error` on miss, and return `NULL`.
- No signature change; success-path behavior is preserved (returns `instance->pVM_hitbox_manager`), so this is an Equivalence Check-friendly change: only the failure path changes from UB to NULL.

**Phase 2 — Align contracts and error idiom:**
- Update the doc comment on `get_p_hitbox_manager_instance_using__uuid_from__hitbox_context` to state the real Postcondition (`NULL` on miss). Contract-First: write the Pre/Postconditions, then confirm the implementation.
- Audit sibling accessors for the mixed NULL-check / `is_p_hitbox_manager_instance__valid` idiom; standardize on the validity predicate (DRY). Optional but recommended; behavior-preserving since `is_p_hitbox_manager_instance__valid` subsumes the NULL check.

**Phase 3 — Harden coupled callers (required for a complete fix):**
- `core/source/world/world.c`: guard the `manage_world` call sites (or make `poll_collision_resolver_aabb` / `poll_hitbox_manager_for__movement` NULL-tolerant with a debug log + early return). Prefer hardening the two callees once rather than guarding at every future call site.
- `core/source/entity/entity.c`: promote the `#ifndef NDEBUG` guards to unconditional guards (a miss is a recoverable error, not a debug-only assertion), or rely on Phase-3 callee hardening.

**Test verification checklist:**
- Existing test `get_pV_hitbox_manager_from__hitbox_context__returns_correct_opaque_manager_pointer` in `tests/core/source/collisions/test_suite_collisions_hitbox_context.c` is a **stub** (`END_TEST`) — it asserts neither correct nor broken behavior. No existing assertion is invalidated by the fix.
- Implement the stub as an **Equivalence Check**: returned pointer equals `instance->pVM_hitbox_manager` from `get_p_hitbox_manager_instance_using__uuid_from__hitbox_context` for an allocated manager.
- Add a miss-path test: unknown / `IDENTIFIER__UNKNOWN__u32` UUID ⇒ returns NULL, does not crash (Boundary Condition coverage; **Fuzzing** over the identifier space is a cheap extension).
- Add **Property Based Testing**: for any UUID, the accessor either returns the instance's `pVM_hitbox_manager` or NULL — never UB (invariant: "result is defined for all inputs").
- Test blast radius: **Low** — one suite file, stub already registered; no rewrites needed.

## 4. Blast Radius Summary

- **Files changed:** 3 source/header files (`hitbox_context.h`, `world.c`, `entity.c`) + 1 test file; optional doc-only touch on the UUID getter's comment (same header).
- **Behavior-preserving for current callers?** Success path: yes, byte-identical. Failure path: changes from UB to NULL — this is the de facto contract callers already code against, so no caller *assumption* is invalidated; instead, previously-dormant guards become live and unguarded callees must be hardened (Phase 3).
- **Phased approach needed?** No hard phase gating; Phase 1 + Phase 3 should land together so the activated NULL path never reaches an unguarded callee. Phase 2 (idiom standardization) can follow independently.
- **De facto contracts affected:** "miss ⇒ NULL" becomes a real, documented Postcondition; the stale "invalid instance" doc comment is retired.
