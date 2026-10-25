# Planning: game_action__global_space__store.h — Incorrect Modules

**Review source:** `agents/core/review/include/game_action/core/global_space/game_action__global_space__store.h/incorrect_modules.md`

**Source files reviewed (read-only):**
- `core/include/game_action/core/global_space/game_action__global_space__store.h`
- `core/source/game_action/core/global_space/game_action__global_space__store.c`
- `core/include/types/core/game_action/global_space/ga_type__global_space__store.h`
- `core/source/world/global_space.c` (callee: `dispatch_process__serialize_global_space`)
- `tests/core/source/game_action/core/global_space/test_suite_game_action_core_global_space_game_action__global_space__store.c`

---

## 1. Problem Identification

Single flagged module: **`m_process__game_action__global_space__store`** (defined in
`core/source/game_action/core/global_space/game_action__global_space__store.c`, declared as the
process callback registered by `register_game_action__global_space__store`).

Two defects, both inside this one function:

1. **Redundant `stat_chunk_file__tiles` call — dead code (Surface-form leakage / DRY violation).**
   Lines 46–50 allocate a stack `IO_path path` and call `stat_chunk_file__tiles(...)`, but the
   resulting `path` is never read afterwards. The callee `dispatch_process__serialize_global_space`
   (`core/source/world/global_space.c:721`) computes its own path via an identical
   `stat_chunk_file__tiles` call. The outer call therefore performs a redundant file-system stat
   and writes into a buffer that is discarded. The leading `// TODO: handle local file IO.` comment
   marks this as scaffolding for unimplemented local-IO work — the block is dead code that leaks an
   internal path-resolution surface into a layer (game action) where it belongs only in the
   serialization dispatcher.

2. **Misleading failure message — copy-paste / Translation Gap.**
   Line 59 emits `debug_error("... failed to dispatch deserialization process.")` while the function
   actually being dispatched is `dispatch_process__serialize_global_space` (serialization, not
   deserialization). The message misrepresents the operation on the failure path, so an operator or
   log reader is pointed at the wrong subsystem.

Neither defect changes observable control flow: in both branches the process is still failed or
completed identically. The defects are a wasted stat and a mislabeled error string.

## 2. Impact Assessment

- **No behavioral contract is broken.** The redundant `stat_chunk_file__tiles` result is discarded;
  removing it is behavior-preserving for every caller of the store action. The error message change
  alters only a log string, not any return value, process state, or serialized data.

- **Callers / de facto contracts:** `dispatch_game_action__global_space__store` (header inline) and
  `register_game_action__global_space__store` wire `m_process__game_action__global_space__store` into
  the `Game_Action_Logic_Table`. These callers depend only on the callback's *process-outcome*
  contract (complete/fail), which the fix preserves. No caller relies on the discarded `path` or on
  the exact wording of the error string — so no coupled assumption is invalidated.

- **Coupling note (SSOT / DRY):** Path resolution for a global-space chunk file already has a single
  source of truth inside `dispatch_process__serialize_global_space`. Repeating it in the game action
  duplicates that logic across layers; the fix removes the duplication rather than relocating it.

- **Adjacent pre-existing defect (out of scope, noted):** `dispatch_process__serialize_global_space`
  itself carries a matching copy-paste error at its file-open failure branch
  (`debug_error("dispatch_process__deserialize_global_space, error in opening file.")` in
  `core/source/world/global_space.c`). This is the same Translation Gap class but lives in a
  different module and was not flagged by this review; it should be tracked separately.

- **Blast radius:** Low. One function, one file. No signature, header, or data-structure change.

## 3. Resolution Assessment

Resolve entirely within `m_process__game_action__global_space__store`
(`core/source/game_action/core/global_space/game_action__global_space__store.c`):

1. **Remove the dead stat block.** Delete the `IO_path path;` declaration and the
   `stat_chunk_file__tiles(get_p_PLATFORM_file_system_context_from__game(p_game),
   get_p_world_from__game(p_game), p_global_space, path);` call (and its now-orphaned
   `// TODO: handle local file IO.` note, or reword the TODO to name the unimplemented local-IO
   feature explicitly). Keep `dispatch_process__serialize_global_space(p_game, p_global_space)` as the
   sole path-resolution + dispatch point (restores SSOT).

2. **Fix the failure message.** Change line 59's string from
   `"m_process__game_action__global_space__store, failed to dispatch deserialization process."` to a
   serialization-accurate string, e.g.
   `"m_process__game_action__global_space__store, failed to dispatch serialization process."`.

3. **Include hygiene.** After removing the `stat_chunk_file__tiles` call, re-check the `#include`
   set in this `.c` file for now-unneeded headers (e.g. `world/serialization/world_directory.h` if
   only pulled in for the stat call) — but retain any header still required by
   `dispatch_process__serialize_global_space`'s declaration or other used symbols. Confirm no unused
   include is left dangling; do not remove a header that is still transitively required.

**Caller updates:** None required (behavior-preserving).
**Header / type changes:** None.
**Documentation:** If `docs/specs/core/game_action/global_space/game_action__global_space__store.h.spec.md`
references the local-IO path or the message wording, update it to match; otherwise no doc change.

**Phasing:** Not needed — a single-file, behavior-preserving edit. Ship as one atomic change.

### Test Verification Checklist

- **Existing tests** (`test_suite_game_action_core_global_space_game_action__global_space__store.c`)
  cover only `initialize_...` (kind + coordinates) and `register_...` (table population). They do not
  exercise `m_process__game_action__global_space__store`, so the fix invalidates **no** existing
  assertion. Existing tests remain green unchanged.

- **New tests to add (low priority, optional):**
  - A test driving `m_process__game_action__global_space__store` against an unallocated global space
    asserts `complete_process` (Equivalence Check of the post-condition branches).
  - A test with a null/unmapped chunk vector asserts `fail_process`.
  - An **Equivalence Check** regression: with the redundant stat removed, confirm the dispatched
    serialization process is identical to before (same sub-state, same deconstruction flags) — proving
    the removal is behavior-preserving.
  - Optionally a **Round Trip Check** (store then load a global space) to guard the serialize path end
    to end if coverage is desired beyond unit scope.

- **Test blast radius:** Low. No existing assertions change; new tests are additive and optional.

## 4. Blast Radius Summary

- **Files changed:** 1 (`core/source/game_action/core/global_space/game_action__global_space__store.c`);
  optionally the spec doc and one test file if new coverage is added.
- **Behavior-preserving for current callers:** Yes — only a discarded stat and a log string change.
- **Phased approach needed:** No.
- **De facto contracts invalidated:** None. The process-outcome contract of the store action is intact.
