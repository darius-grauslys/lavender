# Planning: world_directory (stat_chunk_directory) — Incorrect Modules

**Review source:** `agents/core/review/include/world/serialization/world_directory/incorrect_modules.md`

**Source files reviewed (read-only):**
- `core/source/world/serialization/world_directory.c` (`stat_chunk_directory`, and siblings `stat_world_directory`, `stat_world_header_file`, `stat_chunk_file*`, `append_u32_as__hex_to__path`)
- `core/include/world/serialization/world_directory.h`
- `tools/editors/editor_map/core/world_directory.py` (independent port of the same layout)
- `tests/core/source/world/serialization/test_suite_world_serialization_world_directory.c`

---

## 1. Problem Identification

The review flags **`stat_chunk_directory`** (file of origin
`core/source/world/serialization/world_directory.c`) as **Incorrect**. Its
semantic intent is to build `<base>/save/<world>/r_<x>_<y>_<z>/c_.../.../c_<leaf>`
and ensure every parent directory exists, returning the end-of-path index. Four
defects break that contract:

1. **Missing bounds check (buffer overflow).** The `// TODO: bounds check` at
   the world-name `strncpy` is never implemented. The sibling
   `stat_world_directory` guards with
   `if (index_of__path_append + WORLD_NAME_MAX_SIZE_OF >= MAX_LENGTH_OF__IO_PATH) return 0;`,
   but `stat_chunk_directory` omits it. This is a violated **Precondition** /
   **Boundary Condition**: a long base directory lets the `strncpy` (and every
   subsequent append) write past the 128-byte `MAX_LENGTH_OF__IO_PATH` buffer.
   The identical latent defect exists in `stat_world_header_file`.

2. **Signed/unsigned Mode Confusion.** `append_u32_as__hex_to__path` declares a
   `u32 value`, yet is called with signed `i32` region/chunk fields. Negative
   coordinates implicitly convert to two's-complement hex (`-1` → `ff`/`ffff…`).
   The naming says unsigned; the data is signed — an **Aliasing**/**Mode
   Confusion** between the encoder's assumed domain and the caller's domain.

3. **Incomplete Z-axis subdivision (Under Specified Dispatch).** The
   `//TODO: recur by Z-axis` shows the descent is a 2-D quadtree, not a 3-D
   octree: only `chunk_vector_quad__3i32.x/y` are halved per level; `z` stays
   pinned at 127 across all six intermediate `c_` directories and only appears
   in the final leaf. The intended recursive subdivision is **not Complete** for
   the Z axis — a **Translation Gap** between stated intent and implemented layout.

4. **Inconsistent Z masking.** `x__i32`/`y__i32` are masked with `MASK(8)` but
   `z__i32` is not. The `beginning_index=2` encoder already truncates to 8 bits,
   so this is a **Canonical Form** hygiene issue, not a value bug — but it breaks
   the symmetry of the representation and diverges from the reference port.

Minor: the documented **Postcondition** that "the buffer is not null-terminated
after return" leaves callers who treat `buffer` as a C-string unsafe; only the
returned index is a reliable **Representation Invariant**.

## 2. Impact Assessment

**Within `core/source/world/serialization/world_directory.c`:**
- `stat_chunk_file` calls `stat_chunk_directory` and appends `/t|e|i` at the
  returned index; it `debug_abort`s on a zero return. The **bounds-check** fix is
  **behavior-preserving** for all currently valid inputs (it only converts a
  would-be overflow into a safe `return 0`); the abort path already handles that.
- `stat_chunk_file__tiles/__entities/__inventories` are thin wrappers over
  `stat_chunk_file`; they inherit any change to the returned path.

**Cross-language de facto contract (SSOT at risk):**
- `tools/editors/editor_map/core/world_directory.py::chunk_dir` is an explicit
  port of `stat_chunk_directory`. It **already replicates the current broken
  behavior**: it descends only `quad_x`/`quad_y` (no `quad_z`, `descend_z` stays
  127) and applies the leaf mask via `chunk_z & 0xFF`. This is a **Single Source
  of Truth** mirror of the *present* layout, not of the intended octree.
- Consequence: **fixing defect #3 (Z recursion) invalidates this mirror and every
  save already on disk.** The directory tree is a persisted **de facto contract**;
  adding a Z level changes every chunk path, orphaning existing saves and any
  editor that reads them. Correcting it is *not* behavior-preserving and requires
  a lockstep update to the Python port plus a save-migration step.

**Defect #2 (signed/unsigned):** Region coords come from
`get_region_that__this_global_space_is_in`. If coordinates can be negative, the
hex directory names depend on two's-complement encoding. Any change to the
encoder's sign handling would rename region directories → breaks existing saves
and the Python `_hex8` (which formats negatives differently, e.g. `-0000001`).
Leaving the encoding as-is and merely making the cast explicit is **behavior-
preserving**.

**Defects #1 and #4:** No downstream layout change. The guard only adds a safe
failure; the Z mask matches what the encoder already computes. **Low blast
radius**, no de facto contract invalidated.

## 3. Resolution Assessment

Phase the work by blast radius. **Phase A (safe, do first); Phase B (breaking,
needs product sign-off + migration).**

### Phase A — behavior-preserving corrections

- **A1 — Add the missing bounds check (defect #1).** Before the world-name
  `strncpy` in `stat_chunk_directory`, insert the same guard as
  `stat_world_directory`:
  `if (index_of__path_append + WORLD_NAME_MAX_SIZE_OF >= MAX_LENGTH_OF__IO_PATH) { debug_error(...); return 0; }`.
  Because the append is unbounded past the world name, also assert the running
  index stays `< MAX_LENGTH_OF__IO_PATH` before each `append_*`/directory step
  (**Invariant**). **DRY/SSOT:** factor this guard (and the identical one missing
  in `stat_world_header_file`) into a shared helper so the check lives in one place.
  Callers: no signature change; `stat_chunk_file*` already handle a zero return.

- **A2 — Make the signed→unsigned conversion explicit (defect #2).** Keep the
  encoder's `u32` two's-complement output as the **Canonical Form** (it is
  deterministic and **Lossless** within the masked width), but cast at each call
  site (`(u32)region_vector__3i32.x__i32`, etc.) so the **Mode Confusion** is
  authored, not implicit. Document that negative coordinates map to
  two's-complement hex. No directory names change → existing saves and the Python
  port stay valid.

- **A3 — Symmetrize Z masking (defect #4).** Add
  `chunk_vector__3i32.z__i32 &= MASK(8);` beside the existing x/y masks to match
  the reference port and enforce a consistent **Representation Invariant**.
  Behavior-preserving (encoder already truncates to 8 bits).

- **A4 — Document/fix the null-termination Postcondition.** Either guarantee a
  `buffer[index_of__path_append] = '\0'` before return, or explicitly document
  that callers must use the returned index and never treat `buffer` as a
  NUL-terminated string. Prefer documenting (matches `stat_chunk_file`, which
  appends at the index).

### Phase B — Z-axis subdivision (defect #3) — breaking, gated

The current layout is a **de facto contract** (persisted saves + Python port).
Choose one:

- **B1 (recommended, non-breaking):** Accept the 2-D-descent + z-in-leaf layout
  as the actual **Canonical Form**. Delete the misleading `//TODO: recur by Z-axis`
  and document the real layout as the contract. No path changes; no migration.
- **B2 (only if product requires true 3-D partitioning):** Implement a full octree
  descent (`descend_z`/`quad_z` halved per level). This **renames every chunk
  directory**, so it must ship with: (a) a lockstep update to
  `world_directory.py::chunk_dir` (keep the port an **Equivalence** mirror), and
  (b) a save-migration/round-trip tool that rewrites existing worlds to the new
  layout. Use a **phased** rollout behind a versioned layout tag. High blast
  radius — do not bundle with Phase A.

## 4. Test Verification Checklist

Existing suite (`test_suite_world_serialization_world_directory.c`) only covers
`append_chunk_file__tiles_to__path`; it has **no coverage of `stat_chunk_directory`**
and asserts nothing on the broken behavior — so no existing assertion is
invalidated, but the flagged function is untested. New tests required:

- **Bounds check (A1):** a **Property Based Testing** case asserting the
  invariant `index_of__path_append < MAX_LENGTH_OF__IO_PATH` for generated world
  names / base-directory lengths up to and past the limit; plus a concrete
  **Fuzzing** case with an over-long base directory that must `return 0` instead
  of overflowing.
- **Layout (A2/A3/B):** a **Golden-file Test** / **Equivalence Check** between
  `stat_chunk_directory` output and `world_directory.py::chunk_dir` for a corpus
  of (x,y,z) including negative values, to lock the C/Python mirror as one SSOT
  and catch any drift from A2/A3.
- **Round trip:** a **Round Trip Check** — build the directory path, write a stub
  file, then re-derive the path from the same coordinates and confirm it resolves
  to the same file.
- **B (if chosen):** a migration test asserting every pre-migration save is
  reachable post-migration (**Equivalence** of content across the layout change).

**Test blast radius:** Low for Phase A (add new cases; nothing to fix). High for
Phase B (new migration + golden-file suite, lockstep Python test update).

## 5. Blast Radius Summary

- **Files changed (Phase A):** `core/source/world/serialization/world_directory.c`
  (+ a small shared guard helper); optionally its header if a helper is exposed;
  `tests/.../test_suite_world_serialization_world_directory.c` (new cases). The
  Python port needs only a comment/doc alignment, no logic change.
- **Behavior-preserving for current callers?** Yes for Phase A (guard adds a safe
  failure; explicit cast and Z-mask are value-neutral). No de facto contract
  invalidated.
- **Phase B:** changes `world_directory.c`, `world_directory.py`, both test
  suites, and requires save-migration tooling. **Not** behavior-preserving — it
  invalidates the persisted directory layout and the Python SSOT mirror; a **phased,
  versioned** approach with migration is mandatory.
- **De facto contracts at stake:** the on-disk chunk directory tree and the
  C↔Python layout mirror (SSOT). Phase A preserves them; Phase B breaks them by
  design and must be gated behind product sign-off.
