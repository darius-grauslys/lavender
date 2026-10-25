# Planning: game_action__global_space__resolve — Incorrect Modules

**Review source:** `agents/core/review/include/game_action/core/global_space/game_action__global_space__resolve.h/incorrect_modules.md`

**Source files reviewed (read-only):**
- `core/include/game_action/core/global_space/game_action__global_space__resolve.h`
- `core/include/types/core/game_action/global_space/ga_type__global_space__resolve.h`
- `core/source/game_action/core/global_space/game_action__global_space__resolve.c`
- `core/include/world/global_space.h`
- `core/include/world/global_space_manager.h`
- `core/include/world/chunk_pool.h`
- `core/include/collisions/collision_node_pool.h`
- `core/source/world/global_space_manager.c`
- `core/source/world/global_space.c`
- `core/source/game_action/core/global_space/game_action__global_space__request__offline.c`
- `core/source/game_action/core/global_space/game_action__global_space__request__multiplayer.c`
- `tests/core/source/game_action/core/global_space/test_suite_game_action_core_global_space_game_action__global_space__resolve.c`

---

## 1. Problem Identification

One function/module was flagged as **Incorrect**:

### 1.1 `m_process__game_action__global_space__resolve`
**File:** `core/source/game_action/core/global_space/game_action__global_space__resolve.c` (lines 29–161)

**Defect — `Conservation Law` violation / resource leak (`invariants-and-correctness`):** After allocating a `Chunk` (line 76) and a `Collision_Node` (line 90) and assigning both to the `Global_Space` via `p_global_space->p_chunk = p_chunk` and `p_global_space->p_collision_node = p_collision_node` (lines 107–108), the function dispatches a deserialization sub-process via `dispatch_process__deserialize_global_space` (line 118). When that dispatch returns `NULL` (lines 123–126), the function calls only `fail_process` and returns — **without releasing the already-allocated chunk and collision node back to their pools, and without dropping the global space.**

This is inconsistent with the two sibling failure paths in the same function, both of which release resources before returning:

| Failure path | Chunk assigned to `p_global_space`? | Collision node assigned? | Cleanup performed |
|---|---|---|---|
| Chunk allocation failure (lines 81–88) | No | No | `drop_global_space_within__global_space_manager` + `fail_process` |
| Collision node allocation failure (lines 95–105) | No | No | `release_chunk_from__chunk_pool` + `drop_global_space_within__global_space_manager` + `fail_process` |
| **Deserialization dispatch failure (lines 123–126)** | **Yes** | **Yes** | **`fail_process` only — leak** |

The deserialization-failure path is `Coupled` (`design-principles`) to `p_global_space->p_chunk` / `p_collision_node` being set, but unlike the collision-node-failure path it performs no `release_*_from__pool` call, so the `Chunk_Pool` and `Collision_Node_Pool` never recover the slots. Over repeated failures this exhausts the fixed-size pools (`QUANTITY_OF__GLOBAL_SPACE` entries each), causing cascading allocation failures.

Additionally, the leaked global space retains stale `p_chunk` / `p_collision_node` pointers. On a subsequent re-entry the re-entry guard `if (get_p_chunk_from__global_space(p_global_space))` (line 64) finds the stale chunk, treats the space as already resolved, and calls `complete_process` — a `State Desync` (`translation-and-semantics`) where the global space appears deserialized/constructed despite never having been loaded from disk.

> **Note on verdict discrepancy:** The detailed review file for this module records "Correctness Verdict: Correct" and characterizes the leak as "minor" and "not a correctness issue." The master `incorrect_modules.md` review file overrides this to **Incorrect**, treating the `Conservation Law` violation and the `State Desync` as correctness defects. This plan follows the master review's verdict.

---

## 2. Impact Assessment

### 2.1 Direct impact of the leak
- **`Chunk_Pool` / `Collision_Node_Pool` exhaustion:** Both pools are fixed-size contiguous arrays indexed by `QUANTITY_OF__GLOBAL_SPACE`. Each un-released chunk/collision node permanently consumes one slot. Repeated deserialization-dispatch failures (e.g., under process-pool exhaustion during `run_process` inside `dispatch_process__deserialize_global_space`) eventually starve the pools, causing unrelated `allocate_chunk_from__chunk_pool` / `allocate_collision_node_from__collision_node_pool` calls to fail.
- **`Global_Space` state corruption:** The leaked global space keeps stale `p_chunk` / `p_collision_node` pointers. The re-entry guard at line 64 will short-circuit to `complete_process` on the next invocation, producing a global space that is "complete" but never deserialized — a `State Desync` that can propagate into tile lookups (`get_p_tile_from__global_space_manager` dereferences `p_global_space->p_chunk->chunk_data`).

### 2.2 Callers / consumers of the resolve process
- **`m_process__game_action__global_space__request__outbound_offline`** (`game_action__global_space__request__offline.c`, line 44): dispatches the resolve process via `dispatch_game_action__global_space__resolve` after calling `hold_global_space`. Expects the resolve process to either complete, fail-and-clean-up, or enqueue a sub-process. The broken failure path leaves the global space in the inconsistent state described above.
- **`m_process__game_action__global_space__request__outbound_server`** (`game_action__global_space__request__multiplayer.c`, line 75): same dispatch pattern; same exposure.
- **`drop_global_space_within__global_space_manager`** → **`release_global_space`** (`global_space_manager.c`, lines 74–105): the cleanup function that *would* release the chunk and collision node (via `release_chunk_from__chunk_pool` / `release_collision_node_from__collision_node_pool`) is gated behind `drop_global_space` returning `true` (reference-count exhaustion). The deserialization-failure path never calls `drop_global_space_within__global_space_manager` at all, so `release_global_space` is never reached for this path.

### 2.3 De facto contracts coupled to the broken behavior
- No correct code relies on the leak. No caller inspects the global space's chunk/collision node after a resolve failure expecting them to be present but uninitialized.
- However, the **absence** of cleanup means the global space's `p_chunk` / `p_collision_node` pointers survive the failure. Any future code that assumes "a non-null `p_chunk` implies a valid, deserialized chunk" would be built on this broken assumption. Correcting the leak invalidates this (unintended) de facto contract.

### 2.4 Test coverage gap
- The test suite (`test_suite_game_action_core_global_space_game_action__global_space__resolve.c`) includes the `.c` file directly but only asserts on `initialize_game_action_for__global_space__resolve` (kind + coordinates) and `register_game_action__global_space__resolve` (table population). **No test exercises `m_process__game_action__global_space__resolve` itself** — neither the success path, the deserialization-dispatch-failure path, nor any resource-accounting assertion. Existing tests are therefore unaffected by the fix (Low test blast radius).

---

## 3. Resolution Assessment

### Fix 1 — Release allocated resources on deserialization-dispatch failure
**File:** `core/source/game_action/core/global_space/game_action__global_space__resolve.c`, lines 123–126.

Replace the bare `fail_process` + `return` with the same cleanup pattern used by the collision-node-allocation-failure path (lines 95–105), extended to also release the collision node:

```c
if (!p_process) {
    debug_error("m_process__game_action__global_space__resolve, failed to dispatch deserialization process.");
    release_chunk_from__chunk_pool(
            p_chunk_pool,
            p_chunk);
    release_collision_node_from__collision_node_pool(
            p_collision_node_pool,
            p_collision_node);
    p_global_space->p_chunk = 0;
    p_global_space->p_collision_node = 0;
    drop_global_space_within__global_space_manager(
            p_game,
            gsv__3i32);
    fail_process(p_this_process);
    return;
}
```

**Rationale for each step:**
1. `release_chunk_from__chunk_pool` — returns the allocated `Chunk` to the pool (mirrors the collision-node-failure path at line 97).
2. `release_collision_node_from__collision_node_pool` — returns the allocated `Collision_Node` to the pool (no sibling path releases it because the collision-node-failure path occurs *before* assignment, but here both are assigned).
3. `p_global_space->p_chunk = 0; p_global_space->p_collision_node = 0;` — clears the stale pointers to prevent a `State Desync` (the re-entry guard at line 64 would otherwise see a non-null chunk) and to avoid a double-free inside `release_global_space` (which is called by `drop_global_space_within__global_space_manager` when the reference count allows).
4. `drop_global_space_within__global_space_manager` — decrements the global-space reference count and, if exhausted, calls `release_global_space` (which would now find null pointers and skip — no double-free). This matches the cleanup convention of both sibling failure paths.
5. `fail_process` — terminates the resolve process (moved after cleanup, matching the ordering in the collision-node-failure path at lines 100–103).

**Callers needing updates:** None. The fix only changes the failure-path behavior; all success and other-failure paths are unchanged.

**Header changes:** None. The public API (`dispatch_game_action__global_space__resolve`, `register_game_action__global_space__resolve`, `initialize_game_action_for__global_space__resolve`) is unaffected.

### Phased approach
The fix is a single, self-contained change to one failure path. It can be landed independently. No cross-file structural changes are required.

---

## 4. Test Verification Checklist

**Existing tests:** The test suite (`test_suite_game_action_core_global_space_game_action__global_space__resolve.c`) covers only `initialize_game_action_for__global_space__resolve` and `register_game_action__global_space__resolve`. No test exercises `m_process__game_action__global_space__resolve`. **Test blast radius: Medium** (requires constructing a `Game` / `World` / `Process_Manager` with populated pools and a `Global_Space_Manager` to drive the resolve process).

**New tests needed:**
- **`Conservation Law` check (`Property Based Testing`):** Drive the resolve process against a global space whose chunk file exists on disk but where `dispatch_process__deserialize_global_space` returns `NULL` (inject process-pool exhaustion or mock the dispatch). Assert that after the failure, the `Chunk_Pool` and `Collision_Node_Pool` have the same number of available slots as before the call (i.e., the allocated chunk and collision node were returned). `Mutation Testing` of the failure path guards against regression.
- **`State Desync` regression (`Round Trip Check`):** After the failed resolve, assert `p_global_space->p_chunk == NULL` and `p_global_space->p_collision_node == NULL` so the re-entry guard does not short-circuit to `complete_process` with stale data.
- **`Boundary Condition` / `Fuzzing`:** Trigger the deserialization-failure path under varying pool-exhaustion conditions (chunk pool full, collision-node pool full, both full) to confirm resources are always released regardless of which allocation succeeds.
- **`Equivalence Check`:** Verify that the deserialization-failure path's cleanup matches the collision-node-allocation-failure path's cleanup (same set of release/drop calls).

---

## 5. Blast Radius Summary

- **Files changed:** 1 source file — `core/source/game_action/core/global_space/game_action__global_space__resolve.c`. No header, spec, or caller files require changes.
- **Behavior preservation for current callers:** Strictly corrective. All success paths (chunk-generator transform, `memset`-zero path, successful deserialization dispatch, re-entry completion) and all other failure paths (global-space-not-found, chunk-allocation-failure, collision-node-allocation-failure) are unchanged. Only the deserialization-dispatch-failure path gains resource cleanup.
- **De facto contracts invalidated:** The unintended contract that a failed resolve leaves stale `p_chunk` / `p_collision_node` pointers on the `Global_Space` (which could cause a false-positive re-entry completion). No correct code depends on this.
- **Phased approach:** Yes — the fix is a single failure-path change; it can be landed and verified in isolation.
