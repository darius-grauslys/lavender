# Planning: region_file.h — Incorrect Modules

**Review source:** `agents/core/review/include/world/serialization/region_file.h/incorrect_modules.md`

**Source files reviewed (read-only):**
- `core/include/world/serialization/region_file.h`
- `core/include/world/serialization/world_directory.h`
- `core/source/world/serialization/world_directory.c`
- `core/include/world/world.h`
- `core/include/game.h`
- `core/include/defines.h`

---

## 1. Problem Identification

Flagged entry: `-e ./is_region_in__directory.md — Correctness Verdict: Incorrect`

**`is_region_in__directory(World *p_world, Region_Vector__3i32 region_vector__3i32)`**
(`core/include/world/serialization/region_file.h`, lines 6–11)

- **Stub-real divergence (primary defect).** The function is declared with a doc
  comment ("Warning this function does blocking filesystem IO.") but has **no
  implementation anywhere in the codebase**. `core/source/world/serialization/`
  contains only `world_directory.c`; a search of the source and test trees finds no
  definition. The declared contract (exists → `true`; absent or IO failure → `false`;
  read-only) is an unfulfilled Stub — any call would fail to link.
- **Under Specified Dispatch (secondary defect).** The documented Precondition
  requires a `PLATFORM_File_System_Context`, which lives on `Game`
  (`p_game->p_PLATFORM_file_system_context`, accessor
  `get_p_PLATFORM_file_system_context_from__game` in `core/include/game.h`), not on
  `World`. The signature accepts only `World *`, so as declared the function cannot
  reach the filesystem context it needs. Every sibling API in
  `world_directory.h` (`stat_chunk_directory`, `stat_world_header_file`,
  `stat_world_directory`, …) takes `PLATFORM_File_System_Context *` as its first
  parameter; this declaration breaks that established dispatch pattern.

## 2. Impact Assessment

- **No current callers.** Verified by search: no `.c`/`.h` file in `core/include`,
  `core/source`, or `tests` references `is_region_in__directory`, and no file
  includes `region_file.h`. The symbol is dead surface.
- **No de facto contract; nothing coupled to the broken behavior.** Because the
  function is unimplemented and uncalled, no caller, callee, or data structure relies
  on its behavior. Correcting (or removing) it invalidates zero existing assumptions —
  the only "contract" today is the unfulfilled declaration itself.
- **Forward coupling to enforce (not a break):** a correct implementation must derive
  the region directory name `r_XXXXXXXX_YYYYYYYY_ZZZZZZZZ` (8 hex digits per axis,
  built with `append_u32_as__hex_to__path` in `world_directory.c`, lines ~168–192) and
  stat it via the platform context (`PLATFORM_opendir` pattern already used there).
  Re-encoding the name inline would create a **State Desync** between two naming sites
  — the plan below keeps `world_directory.c` the Single Source of Truth (SSOT) for
  region directory naming (DRY).

## 3. Resolution Assessment

**Phase 1 — Fix the signature (close the Translation Gap).**
- Change the declaration to match the sibling API pattern:
  `bool is_region_in__directory(PLATFORM_File_System_Context *p_PLATFORM_file_system_context, World *p_world, Region_Vector__3i32 region_vector__3i32);`
  This makes the context dependency explicit and testable (Stable Dependency),
  instead of reaching for a global or a `Game*`.
- Update the doc comment: Precondition becomes "non-null `p_PLATFORM_file_system_context`;
  non-null `p_world` with populated world name". Postcondition unchanged: `true` iff the
  region directory exists under the world save directory; `false` on absence or IO
  failure (Conservative: IO error is treated as "not present", matching how
  `stat_chunk_directory` reports failures).

**Phase 2 — Implement the function.**
- Create `core/source/world/serialization/region_file.c`.
- Body: build the world save directory path from `p_world`'s name, append the region
  segment using the shared naming logic from `world_directory.c` (expose the
  region-name-append helper in a header if it is currently file-local, so it remains
  the SSOT), then stat the directory through the platform context. Read-only with
  respect to both parameters (Frame Condition holds; no mutation).
- If the name-append helper cannot be shared cleanly, an alternative is to implement
  `is_region_in__directory` inside `world_directory.c` next to `stat_chunk_directory`,
  keeping the naming code in one translation unit.

**Phase 3 — Tests (all additive; none invalidated).**
- No existing test references the function or its header (verified), so the fix
  invalidates no assertions.
- New coverage:
  - **Round Trip Check:** create the region directory via the existing serialization
    path, assert `is_region_in__directory == true`; remove it, assert `false`.
  - **Equivalence Check:** result must agree with directly statting the path built by
    the shared naming helper (guards against naming drift between call sites).
  - **Property Based Testing:** for generated region coordinate triples, assert the
    result equals actual filesystem state after create/remove.
  - **Fuzzing / boundary inputs:** negative coordinates, zero vector, INT32 min/max
    (Boundary Condition coverage of the hex encoding).
  - **Precondition handling:** null context / null world — decide fail-safe behavior
    (debug assert vs. `false`) and document it in the header comment.

**Phase 4 — Decision gate.** If no caller materializes after Phases 1–3, consider
deleting the declaration instead of shipping an implemented-but-uncalled function;
either outcome removes the Stub-real divergence. Recommended default: implement
(Phase 2), since the declaration is intent-bearing and the review judged it correct.

## 4. Blast Radius Summary

- **Files changed:** `core/include/world/serialization/region_file.h` (signature +
  doc comment); new `core/source/world/serialization/region_file.c` (or additions to
  `world_directory.c`); possibly `world_directory.h` if the naming helper is exposed;
  new test file(s) under `tests/core/source/world/serialization/`.
- **Behavior-preserving for current callers:** trivially yes — there are no callers.
- **Phased approach needed:** No; one small, self-contained change set.
- **De facto contracts invalidated:** None.
