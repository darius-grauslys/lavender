# Planning: process__save_chunk.h — Incorrect Modules

**Review source:** `agents/core/review/include/world/process/process__save_chunk.h/incorrect_modules.md`

**Source files reviewed (read-only):**
- `core/include/world/process/process__save_chunk.h`
- `core/include/world/process/process__load_chunk.h`
- `core/include/world/process/process__save_local_space_node.h`
- `core/include/world/process/process__save_collision_node.h`
- `core/source/world/chunk.c` (sibling `m_process__serialize_chunk`)
- `core/source/world/global_space.c` (sibling `m_process__serialize_global_space`, process dispatch)

---

## 1. Problem Identification

Flagged unit: `m_process__save_chunk(Process *p_this_process, Game *p_game)`
(`core/include/world/process/process__save_chunk.h`, lines 6-8).

- **Translation Gap / Stub-real divergence.** The function is declared in the
  header but has **no implementation** anywhere under `./core/source/`. The
  declared interface (a filesystem serialization process for a Chunk's tile
  data) has no realization; the header advertises a capability the binary does
  not provide. Any attempt to take its address or dispatch it would be an
  undefined reference at link time.

- **Orphan / dead declaration.** `m_process__save_chunk` is referenced by **no
  caller, no dispatcher, and no test** outside its own declaration. It is not
  registered as a process handler anywhere.

- **Redundant with the real save path (DRY / SSOT violation).** The actual
  chunk-save behavior already exists and is wired up: `m_process__serialize_chunk`
  (`core/source/world/chunk.c:30`) serializes `p_chunk->tiles` via
  `PLATFORM_write_file` and is registered as a handler and dispatched from
  `m_process__serialize_global_space` (`core/source/world/global_space.c:383`).
  `m_process__save_chunk` would duplicate that responsibility, introducing two
  sources of truth for one operation.

- **Pattern context.** The sibling "save" declarations
  (`process__save_local_space_node.h`, `process__save_collision_node.h`) are also
  header-only with no `.c` implementation, and `process__load_chunk.h` declares no
  function at all. This is a family of unimplemented/orphaned `m_process__save_*`
  declarations, not an isolated typo — reinforcing that they are dead scaffolding
  rather than pending work.

**Core defect in one sentence:** `m_process__save_chunk` is a declared-but-never-implemented
and never-called process handler whose intended behavior is already faithfully
performed by `m_process__serialize_chunk`, making it a redundant, dead declaration.

## 2. Impact Assessment

- **No production dependency on the broken behavior.** Because there is no
  implementation and no caller, no code in `./include` or `./source` relies on
  `m_process__save_chunk`. Nothing is coupled to a broken *behavior*; the only
  coupling is to a *nonexistent* symbol.

- **Coupling that correcting would invalidate.**
  - Any hypothetical future code that casts
    `p_this_process->p_process_data` to `Serialization_Request*` and expects a
    `save_chunk` handler would be building on an unfulfilled **Precondition**
    (a valid, dispatchable filesystem process). That assumption is currently
    unsatisfiable.
  - The real chunk save is a **Single Source of Truth (SSOT)** owned by
    `m_process__serialize_chunk`. Introducing a second `save_chunk` implementation
    would fragment that SSOT (DRY violation) and risk **State Desync** between the
    two paths.

- **De-facto contract.** The de-facto contract for "save a chunk" is
  `m_process__serialize_chunk`, dispatched by `m_process__serialize_global_space`
  (`global_space.c:383`). That contract is intact and must be preserved; the
  orphan declaration must not shadow or compete with it.

- **Blast radius of correction is minimal.** No callers, no tests, and no other
  header includes depend on `m_process__save_chunk`. Correcting it cannot break an
  existing caller because none exist.

## 3. Resolution Assessment

The defect is a missing/redundant implementation, so the resolution is a choice
between two mutually exclusive paths. **Recommended: Option A (remove).**

### Option A — Remove the orphan declaration (recommended)
Rationale: the intended behavior already exists and is exercised by
`m_process__serialize_chunk`; `save_chunk` is dead scaffolding. Removing it
eliminates the Translation Gap without adding a redundant second source of truth.

Steps:
1. Delete the `m_process__save_chunk` declaration from
   `core/include/world/process/process__save_chunk.h`.
2. If the header becomes empty (as `process__load_chunk.h` already is), either keep
   an empty include-guard-only header for symmetry or delete the header file and its
   `#include` references. Prefer keeping the empty guarded header to match the
   existing `process__load_chunk.h` convention (conservative, low churn).
3. Verify no `#include "process__save_chunk.h"` remains in `./include`/`./source`;
   remove any that do. (None were found during review.)
4. **Callers:** none to update. **Documentation:** none reference it.

### Option B — Implement it following the sibling pattern (only if a distinct
semantic intent is confirmed)
Adopt only if the team confirms `save_chunk` must differ from `serialize_chunk`
(e.g., a different tile format or persistence scope). Do not do this by default,
as it would create a DRY/SSOT violation.

Steps (if chosen):
1. Add `void m_process__save_chunk(Process*, Game*)` to a `.c` in
   `core/source/world/`, mirroring `m_process__serialize_chunk`
   (`chunk.c:30-75`): cast `p_process_data` to `Serialization_Request*`, extract
   the `Global_Space*`, resolve the `Chunk*`, write `p_chunk->tiles` via
   `PLATFORM_write_file`, then call `complete_process()` on success and
   `fail_process()` (+ `set_chunk_as__inactive` / `set_chunk_as__visually_updated`)
   on failure.
2. Enforce the stated **Preconditions** defensively (null `p_global_space`, null
   chunk, valid file handle) with `debug_error` + `fail_process`, matching the
   sibling's **Boundary Condition** handling.
3. Register it in the dispatch table where `m_process__serialize_chunk` is
   registered (`global_space.c:383`) if it is to be reachable.
4. **Callers:** must be added (currently none). **Documentation:** update the
   Postcondition section to reflect actual behavior.

### Phased approach
Not required. The change is small and isolated; no phased rollout is needed.

## 4. Test Verification Checklist

- **Existing tests:** No test references `m_process__save_chunk` (search of the
  test tree returned none). There is no assertion to invalidate.
  - Option A (remove): zero test impact — behavior-preserving for all current
    callers (of which there are none).
  - Option B (implement): new tests required.
- **Recommended tests if Option B is taken:**
  - **Round Trip Check:** serialize a chunk's `tiles` via the save process, then
    deserialize and compare bytes — verifies the write/read path is Round Trip Safe.
  - **Property Based Testing:** for arbitrary `tiles` contents, assert the written
    file is exactly `sizeof(p_chunk->tiles)` and matches the source array.
  - **Equivalence Check:** assert `save_chunk` output is byte-identical to
    `serialize_chunk` output for the same input (would expose the redundancy that
    motivates Option A).
  - **Fuzzing:** boundary cases — empty chunk, null `p_data`, invalid/deallocated
    `Global_Space`, closed file handle — confirm each takes the `fail_process` path
    with no undefined behavior.
- **Test blast radius:** Low (Option A) / Medium (Option B). No phased test update
  needed.

## 5. Blast Radius Summary

- **Files changed:** 1 header (`process__save_chunk.h`) for Option A; plus one new/edited
  `.c` and the `global_space.c` dispatch table for Option B.
- **Behavior-preserving for current callers:** Yes — there are no current callers, so
  removal is fully behavior-preserving.
- **Phased approach needed:** No.
- **De-facto contracts invalidated:** None removed. The real contract
  (`m_process__serialize_chunk`, dispatched from `m_process__serialize_global_space`)
  is preserved and untouched.

**Recommendation:** Proceed with **Option A** — remove the orphan, unimplemented,
never-called `m_process__save_chunk` declaration (keep an empty guarded header for
symmetry with `process__load_chunk.h`). This closes the Translation Gap / Stub-real
divergence without introducing a redundant second source of truth for chunk saving.
