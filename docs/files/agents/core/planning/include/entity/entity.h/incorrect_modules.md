# Planning: entity.h — Incorrect Modules

**Review source:** `agents/core/review/include/entity/entity.h/incorrect_modules.md`

**Source files reviewed (read-only):**
- `core/include/entity/entity.h`
- `core/source/entity/entity.c`
- `core/source/entity/entity_manager.c`
- `core/include/types/implemented/entity/entity_data.h`
- `core/include/types/implemented/entity/entity_kind.h`
- `core/include/types/implemented/entity/entity_functions.h`
- `tests/core/source/entity/test_suite_entity_entity.c`

**Flagged as Incorrect:**
- `m_entity_enable_handler__default` — `core/source/entity/entity.c:66-94`
- `initialize_entity` — `core/source/entity/entity.c:116-130`

---

## 1. Problem Identification

### 1.1 `m_entity_enable_handler__default` (entity.c:66-94)

- **Stub-real divergence / State Desync.** The name and the unit test
  (`test_suite_entity_entity.c:150`) establish the contract: enabling an
  entity sets `ENTITY_FLAG__IS_ENABLED` (via the existing
  `set_entity_as__enabled` inline, `entity.h:66-69`). The implementation never
  writes that flag; it only calls `set_hitbox_aabb_as__active` on the entity's
  `Hitbox_AABB`. Consequently `is_entity__enabled()` (which reads the flag) and
  the enable action are **desynchronized** — an entity can be "enabled" by the
  handler while `is_entity__enabled()` still reports false. This is a
  **Translation Gap** between the documented semantic and the code.
- **Precondition violation / Undefined behavior.** `p_game` is dereferenced
  unconditionally (`&p_game->hitbox_context`) and `p_world` unconditionally
  (`GET_UUID_P(p_world)`), with no null guard. The unit test invokes the
  handler with `(&entity, NULL, NULL)` — guaranteed UB/crash. The handler is
  not **Total** over its declared domain.
- **Debug/release divergence.** The manager null check (lines 75-79) sits in a
  `#ifndef NDEBUG` block, so in release builds a failed lookup yields an
  invalid `Hitbox_Manager_Instance` that is used anyway. The unchecked
  `void*` → `Hitbox_AABB_Manager*` cast is a **Mode Confusion** risk (no
  runtime verification the stored manager is actually an AABB manager).
- **Copy-paste defect.** The debug log reads `"m_entity_dispose_handler__default"`
  (line 77); correct name is `m_entity_enable_handler__default`.
- **Ignored return value.** `set_hitbox_aabb_as__active` returns `bool`; the
  result is discarded.

### 1.2 `initialize_entity` (entity.c:116-130)

- **Dead parameter / Translation Gap.** `kind_of_entity` is accepted but never
  written to `entity_data.the_kind_of__entity`; the preceding `memset` leaves it
  at `0` (`Entity_Kind__None`) regardless of the argument. The parallel alloc
  functions (`allocate_entity_in__entity_manager`,
  `allocate_entity_with__this_uuid_in__entity_manager`, entity_manager.c:143-144,
  187-188) both assign the field. Correctness today holds only **by
  coincidence** (every caller passes `Entity_Kind__None`); a future non-None
  caller would be silently ignored — the **Representation Invariant** that
  "the kind parameter is reflected in the struct" is not enforced.
- **Read-after-zero / latent State Desync.** `_serialization_header.uuid` is read
  for `initialize_serialization_header` *after* the `memset` zeroed the struct,
  so it is always `0`; the apparent intent to preserve/re-seed the uuid is
  defeated.

---

## 2. Impact Assessment

### Callers / dependents

- **`initialize_entity`:** sole production caller is
  `release_entity_from__entity_manager` (entity_manager.c:218), which passes
  `Entity_Kind__None`; all test callers also pass `None`. The kind field is read
  by `sanitize_entity_functions` (entity_manager.c:74) as the index into
  `entity_functions[]`. On the release/reset path the intent *is* to reset kind
  to `None`, so assigning the (None) argument is consistent and non-breaking.
  The uuid set here is immediately clobbered by the subsequent
  `initialize_serialization_header_for__deallocated_struct` (entity_manager.c:221),
  so the read-after-zero has no observable effect on the current release path —
  it is a latent defect for any direct caller.

- **`m_entity_enable_handler__default`:** dispatched through the
  `Entity_Functions` table with real (non-null) `p_game`/`p_world` in
  production, where the hitbox-activation path is the de facto behavior.
  `is_entity__enabled()` is a de facto contract elsewhere: the flag is today
  written only by `set_entity_as__enabled` (alloc path, entity_manager.c; and
  `m_entity_deserialization_handler__default`, entity.c) and cleared by
  `set_entity_as__disabled`. Adding a second writer in the enable handler
  introduces a **Single Source of Truth (SSOT)** concern that must be reconciled.

### Assumptions invalidated by the fix

- **Additive, not breaking, if both effects are kept.** If the enable handler
  sets the flag *and* retains hitbox activation, production callers keep their
  current hitbox behavior and gain flag consistency — low risk. If instead the
  hitbox path is *replaced* by flag-setting (per the `#warning` "replace with
  opaque hitbox pointer"), any production code that relies on enable→hitbox-active
  silently loses that coupling — a behavioral regression. The plan therefore
  keeps the hitbox effect as a guarded secondary side-effect (see §3).
- **Coupled sibling handlers.** The same unconditional-deref + `#ifndef NDEBUG`
  pattern exists in `m_entity_disable_handler__default` (entity.c:95-113) and
  `m_entity_dispose_handler__default` (entity.c:27-59). Their unit tests
  (`..._disables_entity`, `..._does_not_crash`) also pass `NULL, NULL`. Fixing
  the enable handler's null-safety in isolation leaves the disable/dispose
  handlers still UB-prone; the fix is **Coupled** across all three and should be
  applied uniformly to keep the test suite green and the handlers **Total**.

---

## 3. Resolution Assessment

### 3.1 `m_entity_enable_handler__default`

1. **Add a Conservative null guard (Precondition).** At entry, if `!p_game ||
   !p_world`, return early (no dereference). This makes the handler safe/Total
   for the `(NULL, NULL)` test case and eliminates the UB. Apply the identical
   guard to `m_entity_disable_handler__default` and `m_entity_dispose_handler__default`.
2. **Set the flag (primary contract).** Call `set_entity_as__enabled(p_this_entity)`
   so the Postcondition "IS_ENABLED is set" holds and the State Desync /
   Stub-real divergence is resolved. This is the core fix.
3. **Retain hitbox activation as a guarded secondary effect.** Keep
   `set_hitbox_aabb_as__active`, but only when `p_game`/`p_world` are valid, the
   manager lookup succeeds, and a `Hitbox_AABB` is found — preserving the current
   production de facto contract (additive blast radius). Reconcile SSOT by
   documenting that allocation seeds the flag and the enable/disable handlers are
   the authoritative runtime toggle.
4. **Harden the manager cast.** Keep the `void*` → `Hitbox_AABB_Manager*` cast but
   make the null/invalid-manager check active in *both* debug and release
   (remove its `#ifndef NDEBUG` confinement, or add a release-safe guard) to close
   the Mode Confusion / debug-release divergence.
5. **Fix copy-paste log string** to `m_entity_enable_handler__default` (and the
   matching wrong string in the disable handler).
6. **Handle the ignored `bool`** return of `set_hitbox_aabb_as__active` (log on
   failure) — minor, non-blocking.

**Callers:** no signature change; production dispatch sites are unaffected by the
guard and gain flag consistency. **Docs:** update the handler's contract comment /
resolve the `#warning` note to state the dual flag+hitbox responsibility.

### 3.2 `initialize_entity`

1. **Assign the kind.** Add `p_entity->entity_data.the_kind_of__entity =
   kind_of_entity;` (matching the parallel alloc functions). Fixes the dead
   parameter / Translation Gap and enforces the Representation Invariant.
2. **Fix read-after-zero.** Capture `p_entity->_serialization_header.uuid` into a
   local *before* the `memset` and pass that value to `initialize_serialization_header`
   (or, if the reset path is intended to zero the uuid, pass `0` explicitly and
   document it). Note the release path clobbers the header immediately after, so
   this is a latent-correctness fix with no observable change to current callers.
3. **No change** to leaving update/serialize/deserialize handlers NULL (by design;
   division of labor with `f_entity_initializer__default`, entity_manager.c:15-40).

**Callers:** none require changes (all pass `Entity_Kind__None`). **Docs:** update
the header comment to state that the kind argument is now written through.

### 3.3 Sequencing (phased)

- **Phase 1 — null-guards.** Add entry guards to all three handlers. Fixes the
  UB/crash on the NULL test cases; low risk, keeps build green.
- **Phase 2 — flag semantics.** Add `set_entity_as__enabled` /
  `set_entity_as__disabled` to the enable/disable handlers; flips the two handler
  tests from failing to passing.
- **Phase 3 — `initialize_entity`.** Assign kind + fix uuid ordering.

---

## 4. Test Verification Checklist

Existing tests in `tests/core/source/entity/test_suite_entity_entity.c`:

| Test | Current state | After fix | Action |
|------|---------------|-----------|--------|
| `initialize_entity__sets_kind` | Passes **by coincidence** (passes `None`) | Still passes | **Extend** — add non-None case (`Entity_Kind__Unknown`) to actually verify assignment |
| `initialize_entity__entity_is_not_enabled_by_default` | Passes (memset 0) | Unchanged | None |
| `m_entity_enable_handler__default__enables_entity` | **Cannot pass** (NULL deref + flag never set) | Passes (guard + flag set) | Already asserts correct behavior; fix validates it |
| `m_entity_disable_handler__default__disables_entity` | Crashes/UB + flag never cleared → fails | Passes (guard + `set_entity_as__disabled`) | Add guard + clear to disable handler |
| `m_entity_dispose_handler__default__does_not_crash` | UB on NULL → fails/crashes | Passes (guard) | Add guard to dispose handler |

**New / strengthened tests (terminology-based):**
- **Property Based Testing** over all `Entity_Kind` values: after
  `initialize_entity(&e, k)`, `get_kind_of__entity(&e) == k` (invariant that the
  parameter is reflected in the struct).
- **Boundary Condition / Fuzzing:** each handler invoked with `(valid entity,
  NULL, NULL)` and `(NULL entity, ...)` must be a safe no-op (no crash), asserting
  Totality.
- **Round Trip Check:** handler-level enable→disable→enable round trip on the
  `IS_ENABLED` flag (extend the existing
  `set_entity_as__enabled_then_disabled__roundtrip` to exercise the handlers).
- **Equivalence Check:** for callers passing valid `p_game`/`p_world`, hitbox
  activation behavior is preserved (guards are no-ops on valid input).

**Test blast radius: Medium.** Three currently failing/crashing tests flip to
passing; ~2 new cases added. No existing passing assertion is invalidated. A
phased approach (matching §3.3) keeps the suite green incrementally.

---

## 5. Blast Radius Summary

- **Files changed:** `core/source/entity/entity.c` (three handlers +
  `initialize_entity`). `core/include/entity/entity.h` requires comment-only
  updates; **no signature change** is needed (the `kind_of_entity` parameter is
  retained and simply used). Low API blast radius.
- **Behavior-preserving for current callers?** Largely yes. The enable handler's
  fix is *additive* (flag set + null guard) as long as hitbox activation is
  retained; `initialize_entity`'s kind assignment is a no-op for the sole
  production caller (passes `None`). The read-after-zero fix has no observable
  effect on the release path.
- **Phased approach:** Recommended (3 phases, §3.3) to isolate UB fixes from
  semantic changes and keep the build/test suite green at each step.
- **De facto contracts affected:** (a) "enable handler = hitbox activation only"
  is *extended* (not broken) by adding the flag; (b) the SSOT for `IS_ENABLED`
  expands from allocation/deserialization to also include the enable/disable
  handlers — document this so the two writers stay consistent. The disable and
  dispose handlers are **Coupled** to the same fix and must be updated together.
