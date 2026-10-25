# Outstanding Item 3 — Validate World Generation → Save → Load → Save → Load

**Scope:** static analysis + concerns only (per request; no code changes).
**Verdict: the round-trip is structurally sound for the data that matters (tiles, world seed,
client position), and the W→S→L→S→L cycle is closed. The gaps are in *derived* state (flags,
slopes for edge chunks, collision entries) and in failure paths (corrupt chunk file ⇒ permanent
hole). Nothing in the round-trip is a memory-safety bug; the save/load process lifetimes are
sound because the process manager is single-threaded and sequential.**

Date: 2026-09-17. Citations: `core/…` = Lavender_Dev, `AG/…` = Projects__Lavender/AncientsGame.

---

## 1. The actual save flow (what gets written)

The save scene (`AG/source/scene/implemented/scene__world_save.c`) does **not** write chunks
itself. Each tick it only calls `save_client()` (lines 98-106), gated on
`is_local_space_manager__loaded` and `!is_client__saving`.

1. **Client**: `save_client()` (`core/source/game.c:529-566`) → `stat_client_file` → dispatch
   `m_process__serialize_client__ag` (`AG/source/ag__client.c:166-205`) → writes the entity
   (hitbox AABB etc.) via `serialize_entity`. Note: `set_client_as__saving` is set only
   *after* both failure checks pass (`game.c:563-564`); on process-level failure the client is
   `release_client_from__game` + `fail_process` (`ag__client.c:191-198`) and the flag is later
   cleared by `set_client_as__active` (`core/include/client.h:186-191`) on the next load. The
   save scene re-checks `is_client__saving` every tick and has a 255-tick (~8 s) failed-text
   timer bounding the visible state.
2. **Chunks**: written as a *side effect of leaving the world*. Transiting to the save scene
   unloads the world scene, which re-centers the local-space manager at a distant point:
   `set_center_of__local_space_manager` (`core/source/world/local_space_manager.c:300-356`)
   takes the far path when the move exceeds the rendering window (lines 325-341):
   `drop_all__local_spaces_in__local_space_manager` (line 258, called at 343) → for each of the
   648 local spaces, `drop_global_space_within__global_space_manager`
   (`core/source/world/global_space_manager.c:196-237`):
   - **active** global space → `set_global_space_as__awaiting_deconstruction` + dispatch
     `game_action__global_space__store` (priority 0, **critical**,
     `game_action__global_space__store.c:75-90`) →
     `dispatch_process__serialize_global_space` (`core/source/world/global_space.c:716-758`)
     opens `chunks/region_<x>/chunk_<x>_<y>_<z>.dat` with `"wb"` →
     `m_process__serialize_chunk` (`core/source/world/chunk.c:52-76`) writes exactly
     `sizeof(p_chunk->tiles)` bytes (512 × `sizeof(Tile)` raw tile array) — **no chunk header,
     no `chunk_flags`, no collision data** — then the store process deconstructs (frees) the
     global space.
   - **inactive** global space → `release_global_space` immediately, **no file written**.
3. **World metadata**: `world.dat` (world name + repeatable-pseudo-random seed —
   `core/source/world/serialization/world_directory.c`).

So: **every active (generated) chunk in the volume is saved; never-generated chunks are not**
(they have no file; on load they regenerate deterministically from the seed —
`get_random_sample` in `AG/…/ag__chunk_generator_overworld.c:196-303` is a pure function of
(x, y) + the world's repeatable PRNG, and the seed is persisted in `world.dat`).

## 2. The load flow (what gets reconstructed)

`AG/source/scene/implemented/scene__world_load.c:125-137` dispatches `load_world` and
`load_client`, with `enqueue_process(load_client, load_world)` so the client resolves **after**
the world.

1. **World**: `game_action__world__load_world` → `load_local_space_manager_at__global_space_vector__3i32`
   → `set_center_of__local_space_manager` (far path on a fresh world: initialize +
   `hold_all__unheld_local_spaces_in__local_space_manager`, `local_space_manager.c:206-280`) →
   for each local space: `hold_global_space_within__global_space_manager`
   (`global_space_manager.c:150-201`: allocate global space + dispatch request GA +
   `awaiting_construction`) → `game_action__global_space__resolve`
   (`core/source/game_action/core/global_space/game_action__global_space__resolve.c`):
   - chunk already exists → complete (the post-deserialize re-run).
   - else allocate chunk + collision node (same uuid as the global space);
     `stat_chunk_file__tiles` hit → `dispatch_process__deserialize_global_space`
     (`global_space.c:535-575`) → `m_process__deserialize_chunk`
     (`core/source/world/chunk.c:78-133`): reads exactly `sizeof(p_chunk->tiles)` bytes,
     verifies the length, `set_chunk_as__active`, complete. **No generator process is spawned
     for a deserialized chunk.**
   - no file → the resolve process mutates itself into the chunk generator (line 141-161) —
     normal generation path.
2. **Client**: `game_action__world__load_client.c:150-176` → file exists →
   `m_process__deserialize_client__ag` (`AG/source/ag__client.c:92-164`); missing → create new
   entity.
3. The scene transitions when `is_client__active` — **it does not wait for all 648 chunks**.

## 3. Round-trip analysis (S₁ vs S₂)

What survives, what doesn't, per artifact:

| Artifact | In S₁ file? | After load | In S₂ file? | Round-trip status |
|---|---|---|---|---|
| Tile array (kinds + covers, incl. baked slopes) | yes (raw dump) | byte-identical | identical | **OK** |
| World seed / name (`world.dat`) | yes | restored | identical | **OK** — fileless chunks regenerate bit-identically |
| Client position/entity | yes | restored | identical | **OK** |
| `CHUNK_FLAG__IS_DONE_TERRAIN` (MODDABLE_0) | **no** (file = tiles only) | cleared (`initialize_chunk`), `IS_ACTIVE` set instead | cleared again | see §4.1 |
| Slopes for chunks that left the volume **unresolved** | no (never baked into tiles) | no generator spawned → **never resolved** | no (persisted slope-less) | **permanent loss** — see §4.2 |
| Collision node entries | **no** (runtime registrations; `add_entry_to__collision_node` called only from `world.c:369`, `client.c:130`, `hitbox.c:149`, `collision_utils.c:145`) | node allocated by resolve, empty | empty | see §4.3 |
| `IS_DIRTY` / other runtime flags | no | cleared | — | no correctness impact; see §4.4 |
| Process state (generators, enqueues) | no | not restored (by design) | — | **OK** — nothing downstream depends on it (verified: no saved artifact references process uuids) |

### 4.1 `IS_DONE_TERRAIN` non-persistence — LOW (mitigated by `IS_ACTIVE`)
Loaded chunks come back with `IS_ACTIVE` set but `IS_DONE_TERRAIN` clear. The neighbor check
that consumes the flag is `is_global_space__finished_terrain`
(`AG/…/ag__chunk_generator_overworld.c:700-708`) = `is_global_space__active(gs) || flag` —
**active is the first disjunct**, and deserialize sets it (`chunk.c:131`), so a freshly
generated chunk adjacent to loaded chunks still sees its neighbors as finished. The only
fragile corner: a chunk whose generator *failed on timeout* (Item 1, Mechanism D) has the
flag set but its global-space `constructing` flag state depends on whether the dispose ran —
any consumer keying on the flag *alone* would misread loaded vs failed chunks. Keep the
`active || flag` form in all consumers.

### 4.2 Slope loss for edge chunks — MEDIUM (a design decision, not a bug)
Slopes are baked into tile data by the resolver (`render_slope_map_into__chunk`,
lines 665-694), so **if** they were resolved before the chunk left the volume, they ride in the
tile array and survive the round-trip. But the *normal* lifecycle (Item 1, Mechanism A) is:
edge chunk waits for out-of-volume neighbors that never exist → deconstruction escape hatches
it **unresolved** → saved slope-less → loaded with no generator spawned → slope-less in S₂
forever. Deterministic and stable (S₂ == S₁ bytes), but the world permanently loses stair
slopes on every chunk that ever left the volume at the edge. Decision needed: accept it, or
spawn a *slope-only* process for loaded chunks whose 8 neighbors are also loaded/active
(the resolver's own gate at lines 964-970 is the existing guard — reusing it is cheap).

### 4.3 Collision entries not re-derived on load — MEDIUM
Collision node entries are pure runtime registrations (four call sites above; none in the
chunk generator). After load, each chunk's node is empty and repopulates as entities register
their hitboxes — fine for entity-vs-entity and entity-vs-chunk collisions that re-register on
spawn. There is **no code path that re-derives static terrain collision (sight-blocking /
passability) from the deserialized tiles** (`m_process__deserialize_chunk` only sets
`IS_ACTIVE`). If any AI/nav/sight system expects chunk-level entries to exist immediately
post-load, loaded chunks are invisible to it until entities touch them. Worth a conscious
"this is expected" note or a small re-derivation pass at activation.

### 4.4 Full rewrite every save — LOW (I/O, not correctness)
`IS_DIRTY` is runtime-only and `m_process__serialize_chunk` ignores it: every in-volume active
chunk is rewritten with `"wb"` on every save, even if untouched. At 512 tiles × `sizeof(Tile)`
per chunk × 648 chunks this is the dominant save cost. A dirty-gated write (skip file write
when `!IS_DIRTY` and a file already exists) is a straightforward optimization.

### 4.5 Corrupt/short chunk file ⇒ permanent hole — MEDIUM
`m_process__deserialize_chunk` on a read error or short read: `set_chunk_as__inactive` +
`fail_process` (`chunk.c:107-130`). The chunk allocation **remains** (inactive). The resolve
process re-runs, sees `get_p_chunk_from__global_space != 0`, and completes **without** falling
back to the generator (resolve's first check, lines 66-71). Result: the chunk stays an
inactive hole for the session; on the next save it's dropped as *inactive* (no file written —
the old corrupt file stays on disk) → next load hits the same corrupt file → **hole is
permanent** until the file is manually deleted. Suggested later fix: on deserialize failure,
release the chunk allocation and re-dispatch through the generator branch.

## 5. Lifetime hazards checked (no memory-safety findings in the round-trip itself)

- **Serialize/deserialize process vs global-space release**: the store process runs to
  completion *before* the deconstruction release; the process manager is single-threaded and
  sequential, so a serialize process cannot observe a re-allocated slot mid-write. The one
  real hazard found is **not** in save/load — it's the drop-path deferred `fail_process` of a
  *generator* process (dangling `p_process_data`, dispose writing into a re-allocated slot),
  detailed in Item 1 §6. It intersects save/load only in that a save triggered while
  generators are pending (Item 1's cutoff state) would freeze the store's *waiter* semantics —
  the store GA itself is **critical**, so it still runs.
- **Load ordering**: client enqueued after world (`scene__world_load.c:125-137`) — the player
  cannot spawn before its chunk exists.
- **`__Tile_Data` (the WIP header)**: `AG/include/types/implemented/world/tile.h:14-17`
  declares bare type names as struct members (`Tile_Kind;`) — GCC warns "declaration does not
  declare anything" and creates **no** members; verified empirically
  (`sizeof(__Tile_Data) == 0`, the `array_of__tile_data__u8[sizeof(__Tile_Data)]` union member
  is a zero-length array; `sizeof(Tile)` is dominated by the bitfield layer struct = 4 bytes).
  Serialization uses `sizeof(p_chunk->tiles)` directly, so **save/load is unaffected** — it's
  dead code that costs ~3 warnings per translation unit (×281 TUs per build; see Item 4).

## 6. Concerns, severity-ordered

1. **MEDIUM** — Corrupt/short chunk file ⇒ permanent inactive hole + unhealable file
   (§4.5). Needs the deserialize-failure → re-generate fallback.
2. **MEDIUM** — Slope loss for edge chunks is permanent across S→L→S (§4.2). Needs a decision:
   accept, or spawn slope-only processes for loaded chunks with loaded neighbors.
3. **MEDIUM** — No static-collision re-derivation on load (§4.3). Document or implement.
4. **LOW** — `IS_DONE_TERRAIN` not persisted; safe today only because consumers use
   `active || flag` (§4.1). Keep that invariant; consider persisting the flag in the file
   header if more flag-keyed consumers appear.
5. **LOW** — Full-rewrite saves ignore `IS_DIRTY` (§4.4).
6. **LOW** — Save scene transitions on client-active only; chunks load asynchronously
   (pop-in) — cosmetic.
7. **LOW** — `__Tile_Data` dead struct: fix the header to kill the per-TU warnings.
8. **INFO** — The save scene's failed-text state machine has no visible trigger in
   `m_enter_scene_as__world_save_handler` (lines 67-158) wiring a failed process to
   `Saving_Text_State__Failed`; verify the unshown tail (or the process-completion hook)
   actually sets it, or "Saving…" dots spin until the 8 s timer regardless of outcome.

## 7. What would a full validation harness look like (for later)

- Golden test: generate a fixed-seed world at a fixed position → save → quit → load → assert
  per-chunk tile hashes equal the pre-save hashes for all 648 in-volume chunks; save again →
  byte-compare S₁ vs S₂ chunk files (expected: identical except slope-chunk set changes if §4.2
  is fixed).
- Corrupt-file test: flip bytes in one chunk file, load, assert the fallback (§4.5 fix) and
  that the chunk is playable.
- Both are runnable headless via the `no_gui` platform + the existing `tests/` harness.
