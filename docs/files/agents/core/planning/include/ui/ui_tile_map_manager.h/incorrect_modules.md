# Planning: ui_tile_map_manager.h — Incorrect Modules

**Review source:** `agents/core/review/include/ui/ui_tile_map_manager.h/incorrect_modules.md`

**Source files reviewed (read-only):**
- `core/include/ui/ui_tile_map_manager.h`
- `core/source/ui/ui_tile_map_manager.c`
- `core/include/ui/ui_tile_map.h`
- `core/platform_defines.h`
- `tests/core/source/ui/test_suite_ui_ui_tile_map_manager.c`

---

## 1. Problem Identification

### `allocate_ui_tile_map_with__ui_tile_map_manager`

**Defect:** Copy-paste error in loop bounds. The Medium case (line ~109) and Small case (line ~132) both use `UI_TILE_MAP__LARGE__MAX_QUANTITY_OF` (8) as the loop bound instead of their respective pool sizes (`UI_TILE_MAP__MEDIUM__MAX_QUANTITY_OF` = 16, `UI_TILE_MAP__SMALL__MAX_QUANTITY_OF` = 32). This is a **Surface-form leakage**: the constant was copied verbatim from the Large case rather than re-derived per pool.

**Consequence:** Only the first 8 slots of each Medium and Small pool are ever searched. The function returns `UI_TILE_MAP__WRAPPER__INVALID` prematurely when all first-8 slots are in use, even though free slots exist at higher indices. The **Postcondition** ("search the full pool for the requested size category") is violated.

### `release_ui_tile_map_with__ui_tile_map_manager`

**Defect:** Identical copy-paste error. The Medium case (line ~197) and Small case (line ~222) both use `UI_TILE_MAP__LARGE__MAX_QUANTITY_OF` (8) as the loop bound.

**Consequence:** A tile map allocated at index ≥ 8 in the Medium or Small pool can never be located by the release function. The release logs an error and leaves the tile map perpetually allocated — a **State Desync** between the wrapper (invalidated by caller) and the pool slot (still flagged allocated).

**Note:** `initialize_ui_tile_map_manager` correctly uses the proper per-pool constants, confirming the intended pattern. The bug is isolated to the two search functions.

---

## 2. Impact Assessment

### Affected pools and capacity

| Pool | Intended capacity | Effective capacity (buggy) | Slots stranded |
|------|-------------------|----------------------------|----------------|
| Small | 32 | 8 | indices 8–31 (24 slots) |
| Medium | 16 | 8 | indices 8–15 (8 slots) |
| Large | 8 | 8 | none (correct) |

### Callers and data structures relying on the broken behavior

- **`UI_Tile_Map_Manager`** is embedded in `Gfx_Context` (accessed via `get_p_ui_tile_map_manager_from__gfx_context`). Any UI subsystem that allocates > 8 concurrent Small or Medium tile maps through the Gfx_Context path will receive spurious `UI_TILE_MAP__WRAPPER__INVALID` returns.
- **`initialize_ui_tile_map_manager`** correctly zeroes all 32+16+8 slots. The **Representation Invariant** (all pool slots exist in memory and are initialized) holds, but the allocate/release functions fail to honor it. No caller has adapted to the reduced capacity because the bug is silent — it manifests only as a failed allocation, not a crash.
- No code in `./include` or `./source` was found to depend on the *reduced* capacity as a de facto contract. The broken behavior is purely a capacity limitation, not an intentional design constraint.

### How correcting the bug invalidates assumptions

- **None.** The fix strictly expands the searchable range. Any caller that previously succeeded (≤ 8 concurrent allocations per pool) continues to succeed identically. Callers that previously failed at the 9th allocation will now succeed. No existing valid state is invalidated.
- The `Frame Condition` of both functions is unchanged: they still mutate only the target slot's flags and return/modify the wrapper.

---

## 3. Resolution Assessment

### Change (single file: `core/source/ui/ui_tile_map_manager.c`)

| Location | Current (incorrect) | Corrected |
|----------|---------------------|-----------|
| `allocate` — Medium case, line ~109 | `< UI_TILE_MAP__LARGE__MAX_QUANTITY_OF` | `< UI_TILE_MAP__MEDIUM__MAX_QUANTITY_OF` |
| `allocate` — Small case, line ~132 | `< UI_TILE_MAP__LARGE__MAX_QUANTITY_OF` | `< UI_TILE_MAP__SMALL__MAX_QUANTITY_OF` |
| `release` — Medium case, line ~197 | `< UI_TILE_MAP__LARGE__MAX_QUANTITY_OF` | `< UI_TILE_MAP__MEDIUM__MAX_QUANTITY_OF` |
| `release` — Small case, line ~222 | `< UI_TILE_MAP__LARGE__MAX_QUANTITY_OF` | `< UI_TILE_MAP__SMALL__MAX_QUANTITY_OF` |

Four constant substitutions. No structural refactoring required. The **SSOT** for each pool's capacity is already established in `core/platform_defines.h`; the fix simply references the correct constant per case, restoring **DRY** alignment with `initialize_ui_tile_map_manager`.

### Caller updates

None. The function signatures, return types, and semantics are unchanged. The fix is internal to the loop bound.

### Documentation updates

None required. The header declarations and spec (`docs/specs/core/ui/ui_tile_map_manager.h.spec.md`) already describe the intended full-pool search behavior.

---

## 4. Test Verification Checklist

### Existing tests (in `tests/core/source/ui/test_suite_ui_ui_tile_map_manager.c`)

| Test | Asserts | Pre-fix status | Post-fix status |
|------|---------|----------------|-----------------|
| `initialize_ui_tile_map_manager__all_deallocated` | All slots deallocated (uses correct constants) | PASS | PASS (unchanged) |
| `allocate_ui_tile_map__small__returns_valid_wrapper` | Single small alloc succeeds | PASS | PASS (unchanged) |
| `allocate_ui_tile_map__medium__returns_valid_wrapper` | Single medium alloc succeeds | PASS | PASS (unchanged) |
| `allocate_ui_tile_map__large__returns_valid_wrapper` | Single large alloc succeeds | PASS | PASS (unchanged) |
| `release_ui_tile_map__nullifies_wrapper_data` | Alloc slot 0, release nullifies wrapper | PASS | PASS (unchanged) |
| `allocate_ui_tile_map__exhaust_small_pool` | All 32 small maps allocatable, 33rd fails | **FAIL** (fails at i=8) | **PASS** |
| `release_and_reallocate__small_tile_map` | Round-trip on slot 0 | PASS | PASS (unchanged) |

### New tests required

1. **`allocate_ui_tile_map__exhaust_medium_pool`** — Symmetric to the small-pool test: allocate all 16 medium maps, assert each valid; assert 17th returns INVALID. **Property Based Testing**: for each pool size N ∈ {32, 16, 8}, allocating N succeeds and N+1 fails.
2. **`release_ui_tile_map__high_index_slot`** — Allocate a small tile map at a known index ≥ 8 (by pre-allocating 8 slots first), then release it. Assert the wrapper is nullified and the slot flag is cleared. This directly exercises the previously-unsearchable region.
3. **`Round Trip Check`** — For each pool size: allocate → release → re-allocate, verifying the same slot is reused and flags transition correctly.

### Blast radius (tests)

**Low.** One existing test transitions from FAIL to PASS. Two new tests to add. No existing passing test is invalidated.

---

## 5. Blast Radius Summary

| Dimension | Assessment |
|-----------|------------|
| Files requiring change | **1** (`core/source/ui/ui_tile_map_manager.c`) |
| Lines changed | **4** (constant substitutions) |
| Behavior-preserving for current callers? | **Yes** — strictly expands capacity; no previously-valid path is altered |
| Phased approach needed? | **No** — single-file, atomic fix |
| De facto contracts invalidated? | **None** — the broken behavior was a silent capacity limit, not a contract any caller adapted to |
