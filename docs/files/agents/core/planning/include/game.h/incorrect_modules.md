# Planning: game.h — Incorrect Modules

**Review source:** `agents/core/review/include/game.h/incorrect_modules.md`

**Source files reviewed (read-only):**
- `core/include/game.h`
- `core/source/game.c`
- `core/include/defines.h` (`Game` struct)
- `core/source/client.c` (callee: `receive_game_action_for__client`)
- `tests/core/source/test_suite_game.c` (stub — no assertions)

**Flagged incorrect (11):**
`save_client`, `save_all__clients`, `release_client_from__game`,
`m_game_action_handler__receive__multiplayer`, `broadcast_game_action`,
`stop_multiplayer_for__game`, `release_client_pool_from__game`, `manage_game`,
`allocate_client_pool_for__game`,
`get_p_local_space_manager_thats__closest_to__this_position`,
`reset__game_tick_timer`.

---

## 1. Problem Identification

- **`save_client`** (`game.c:529`): Broken error gate. `stat_client_file`'s return
  value is stored in `index_of__path` but never checked; the guard tests the
  out-param `index_of__path_to__base_directory`, which is set *before* the file-
  existence check. A missing client file therefore passes the guard and a save
  process is dispatched for a non-existent path. Violates the intended
  `Postcondition` (null return on failure).

- **`save_all__clients`** (`game.c:512`): No null/deallocated guard. Each pointer
  from `get_p_client_by__index_from__game` is forwarded unguarded to
  `save_client`, which dereferences it via `GET_UUID_P`. A vacant slot → null
  dereference (UB). Omits the codebase's own validation convention.

- **`release_client_from__game`** (`game.c:348`): No input validation. `DEALLOCATE_P(p_client)`
  reads `p_client->size_of__struct` with no `IS_DEALLOCATED_P` guard → null
  dereference and double-deallocation. Pool array accessed without a
  non-null allocation check. Missing `break` after swap-remove wastes iterations.

- **`m_game_action_handler__receive__multiplayer`** (`game.c:810`): Contract drift on the
  non-local path. `receive_game_action_for__client(...)` is called as an
  expression statement; its `bool` is discarded and the function hard-codes
  `return true`. Genuine failures (unsupported action, alloc/dispatch failure)
  are mis-reported as success — a **Non-Injective Translation** of the callee's
  outcome. The local path and both sibling handlers propagate the return; only
  this branch does not.

- **`broadcast_game_action`** (`game.c:572`): Broken `Loop Invariant`. The `for`
  condition is the bare expression `get_max_quantity_of__clients_for__game(p_game)`
  with the `index_of__client <` comparison missing (`game.c:587-589`). The bound is a
  constant non-zero value → infinite loop; in debug the helper aborts, in release
  it returns null and the null manager is dereferenced (UB).

- **`stop_multiplayer_for__game`** (`game.c:292`): Incomplete teardown. Frees
  `pM_tcp_socket_manager` but leaves it dangling (not nulled), does not reset the
  three `m_game_action_handler__*` pointers to their `__singleplayer` variants, and
  does not clear `GAME_FLAG__IS_SERVER_OR__CLIENT`. Not the inverse of
  `begin_multiplayer_for__game` → **State Desync** and use-after-free on any later
  `is_game__multiplayer`/TCP-context access.

- **`release_client_pool_from__game`** (`game.c:191`): Conservation-law and state defects.
  Frees `pM_clients` but never frees `pM_ptr_array_of__clients` (leak) and resets
  neither pointer, `max_quantity_of__clients`, nor `index_to__next_client_in__pool`
  (dangling). The active-client scan iterates to pool *capacity* instead of
  `index_to__next_client_in__pool`, emitting spurious debug errors.

- **`manage_game`** (`game.h:39`): Dead declaration / **Stub-real divergence**. No core
  or backend implementation exists; the per-frame work lives entirely in
  `manage_game__pre_render`/`__post_render`. No call site anywhere, but as a
  non-inline free function any future reference is an undefined-symbol link error.

- **`allocate_client_pool_for__game`** (`game.c:152`): Two defects. (1) `memset` on the
  pointer array uses `max_quantity_of__clients` bytes instead of
  `sizeof(Client*) * quantity_of__clients` (`game.c:176`) → only ~1/8 of the array
  is zeroed for a large pool (**Representation Invariant** violation). (2) Neither
  `malloc` return is checked → null dereference on allocation failure, deviating
  from the `allocate_ui_manager__members` convention.

- **`get_p_local_space_manager_thats__closest_to__this_position`** (`game.c:210`):
  Uninitialized return (UB). `p_local_space_manager__closest` is declared without an
  initializer (`game.c:220`) and returned unmodified when the pool is empty or the
  first slot is vacant. Secondary semantic concern: `break` on first null client
  assumes a dense pool and can skip the true closest client.

- **`reset__game_tick_timer`** (`game.c:641`): Wrong arithmetic. It subtracts the whole-
  tick portion from the accumulator instead of masking the combined value to
  `MASK(15)`. When no whole ticks elapsed the fractional remainder is lost; when
  whole ticks elapsed and the accumulator is smaller, unsigned underflow corrupts
  the accumulator. Violates the intended **Conservation Law** for tick time.

## 2. Impact Assessment

- **Client pool lifecycle (`allocate`/`release_client_pool_for__game`, `release_client_from__game`)**
  is a shared subsystem: `allocate_client_pool_for__game`, `release_client_pool_from__game`,
  `allocate_client_from__game`, `release_client_from__game`, `get_p_client_by__index/uuid/
  local_client_from__game`, `save_all__clients`, and
  `get_p_local_space_manager_thats__closest_to__this_position` all read the same pool state
  (`pM_clients`, `pM_ptr_array_of__clients`, `max_quantity_of__clients`,
  `index_to__next_client_in__pool`). Fixing `release` to free *both* allocations and reset
  *all four* fields restores a well-defined single source of truth; until then the dangling
  `pM_clients` also makes the `allocate` guard (`pM_clients != 0 → "Release first"`) permanently
  block re-allocation for the process lifetime. The `allocate` memset fix and the `release`
  reset must land together or the pool's **Representation Invariant** stays broken on one side.

- **Game-action routing (`m_game_action_handler__receive__multiplayer`, `broadcast_game_action`)**
  is consumed by `receive_game_action`/`dispatch_game_action` and their callers, which treat
  the handler `bool` as a success signal. Correcting the receive handler to propagate the
  callee's return changes observable behavior for any caller that currently relies on the
  de-facto "always true" contract (it will now see real failures). Correcting the broadcast
  loop is behavior-preserving only in the sense that it stops the infinite loop; the intended
  per-client dispatches become reachable for the first time, so downstream
  `dispatch_game_action_for__client` effects (TCP sends) start firing.

- **Multiplayer teardown (`stop_multiplayer_for__game`)**: currently only invoked from the
  `begin_multiplayer_for__game` failure-rollback path (`game.c:270`). Extending it to null the
  socket manager, reset the three handler pointers, and clear the flag makes that rollback a
  correct inverse of `begin` (improving it), but any future caller that expects `stop` to be a
  no-op partial teardown would see stronger state reset. `is_game__multiplayer`,
  `get_p_PLATFORM_tcp_context_from__game`, and the multiplayer action handlers all key off the
  freed/handler/flag state, so the fix removes a use-after-free hazard across that cluster.

- **Tick timer (`reset__game_tick_timer`)**: called every frame from
  `manage_game__post_render` (`game.c:745`) and from the shutdown drain loop in `run_game`
  (`game.c:728`). Correcting the arithmetic changes accumulated tick counts on every frame —
  high behavioral blast radius for anything driven by ticks (process polling cadence, world
  updates). Callers need no signature change; only the computed value becomes correct.

- **`save_client` / `save_all__clients`**: `save_client` is invoked by `save_all__clients` and
  reachable via the save-client process dispatch. Fixing `save_client`'s guard to test the real
  return value makes it correctly reject missing files; adding the null/deallocated guard in
  `save_all__clients` protects against vacant pool slots. No signature changes; callers are
  unaffected, but a save that previously "succeeded" for a missing file will now correctly fail.

- **`manage_game`**: no current callers (only `__pre_render`/`__post_render` are used by scenes),
  so removing or implementing it is low-risk to existing behavior; the risk is only a latent
  undefined-symbol if left declared and later referenced.

## 3. Resolution Assessment

Per-function plan (implementation changes / caller updates / test+doc updates):

1. **`save_client`** — change the guard to test the return value:
   `if (!index_of__path) { debug_error(...); return 0; }`. Remove/repurpose the unused
   `index_of__path_to__base_directory` out-param if it is no longer needed. *Callers:* none.
   *Tests:* new case asserting null return when the client file does not exist, and a
   non-null process when it does.

2. **`save_all__clients`** — add `if (!p_client || IS_DEALLOCATED_P(p_client)) continue;`
   before calling `save_client`, matching the sibling convention. *Callers:* none.
   *Tests:* a pool with a mid-range vacant slot must not crash and must skip it.

3. **`release_client_from__game`** — guard the head with
   `if (!p_game->pM_ptr_array_of__clients || IS_DEALLOCATED_P(p_client)) return;`,
   add `break;` after a successful swap-remove, and validate the pool is allocated before
   the scan. *Callers:* none (behavior only tightens). *Tests:* double-release and
   null-client calls must be no-ops, not UB.

4. **`m_game_action_handler__receive__multiplayer`** — replace the discard + `return true;`
   on the non-local path with `return receive_game_action_for__client(p_client, p_game,
   p_game_action);`. *Callers:* `receive_game_action` and its callers now observe real failure
   results (intended). *Tests:* an unsupported/unknown non-local action must propagate `false`.

5. **`broadcast_game_action`** — restore the missing comparison in the loop condition:
   `for (Index__u32 index_of__client = 0; index_of__client <
   get_max_quantity_of__clients_for__game(p_game); index_of__client++)`. *Callers:*
   `m_game_action_handler__dispatch__multiplayer` unchanged. *Tests:* a pool with N clients
   must complete the loop (no hang) and dispatch only to clients with the broadcast point
   loaded.

6. **`stop_multiplayer_for__game`** — make it the inverse of `begin`: after `free`, set
   `p_game->pM_tcp_socket_manager = 0`; reset
   `m_game_action_handler__dispatch/__receive/__resolve` to their `__singleplayer` variants;
   clear `GAME_FLAG__IS_SERVER_OR__CLIENT`. *Callers:* the `begin` rollback path now fully
   unwinds. *Tests:* after stop, `is_game__multiplayer` is false and no freed pointer remains.

7. **`release_client_pool_from__game`** — free **both** `pM_clients` and
   `pM_ptr_array_of__clients`; reset both pointers, `max_quantity_of__clients`, and
   `index_to__next_client_in__pool` to 0; change the active-client scan bound from capacity to
   `index_to__next_client_in__pool`. *Callers:* none (fixes leak + dangling). *Tests:*
   double-release is a safe no-op; no leak (allocator/instrumentation check).

8. **`manage_game`** — remove the dead declaration (preferred) or implement it as a thin
   coordinator over `__pre_render`/`__post_render`. Also correct the misleading "not
   implemented in core" header comment. *Callers:* none currently. *Tests:* N/A for removal;
   if implemented, mirror sibling coverage.

9. **`allocate_client_pool_for__game`** — fix `memset` byte count to
   `sizeof(Client*) * quantity_of__clients`; check both `malloc` results and on the second
   failure free the first allocation and return false (mirror `allocate_ui_manager__members`).
   *Callers:* none. *Tests:* a pool larger than 1 has every pointer slot zeroed; simulated
   malloc failure returns false without leaking/dereferencing null.

10. **`get_p_local_space_manager_thats__closest_to__this_position`** — initialize
    `p_local_space_manager__closest = 0;` and define the empty-pool contract (return NULL).
    Change `break` on first null client to `continue` (or document a dense-pool precondition).
    Optionally harden the Manhattan-distance helper against `abs(INT32_MIN)`/int overflow with
    a wider intermediate type. *Callers:* none found in core. *Tests:* empty pool and
    mid-pool gap both return a defined result.

11. **`reset__game_tick_timer`** — replace the subtract-with-`~MASK(15)` with the mask form:
    `p_game->tick_accumilator__u32F20 =
    (p_game->tick_accumilator__u32F20 + p_game->time_elapsed__u32F20) & MASK(15);`
    then `time_elapsed__u32F20 = 0`. *Callers:* none need signature changes. *Tests:* property
    based — for all (A,T), the retained remainder equals `(A+T) & MASK(15)` and never underflows.

**Phasing:** Group the fixes into three low-coupling batches to keep review/verification
manageable: (A) pool lifecycle — `allocate`/`release_client_pool`, `release_client_from__game`,
`save_all__clients`, `get_p_local_space_manager...`; (B) multiplayer/action routing —
`stop_multiplayer`, `receive__multiplayer`, `broadcast_game_action`; (C) misc — `save_client`,
`reset__game_tick_timer`, `manage_game`. Batches A and B have internal cross-dependencies
(pool state; begin/stop inverse) and should each land atomically; batch C is independent.

## 4. Test Verification Checklist

- **Existing coverage:** `tests/core/source/test_suite_game.c` is a stub — it includes
  `game.c` but contains only `DEFINE_SUITE(game, END_TESTS)` and a `#warning` to add tests.
  No existing assertions cover any flagged function, so no current test is invalidated by the
  fixes; all verification must be added new. Backend suites (`tests/sdl`, `tests/no_gui`)
  likewise do not reference these functions.

- **New tests to add (terminology-driven):**
  - `reset__game_tick_timer`: **Property Based Testing** — across the full (A,T) space, assert
    the retained accumulator equals `(A+T) & MASK(15)` and is never a wrapped/underflowed value;
    add explicit boundary cases (A=0,T=0x4000; A=0,T=0x8000).
  - `allocate`/`release_client_pool`: **Round Trip Check** — allocate then release returns the
    Game to a fully zeroed pool state; pair with an allocation-instrumentation (leak) check for
    the previously-leaked pointer array.
  - `save_client`: **Equivalence Check** — present file → non-null process; absent file → null
    return (the exact case the broken guard missed).
  - `broadcast_game_action` / pool scans: **Fuzzing**/bounded iteration to prove termination
    (no infinite loop) and correct per-client dispatch selection.
  - `receive__multiplayer`: **Equivalence Check** — unsupported non-local action propagates
    `false`, matching the local-path and sibling-handler behavior.
  - `get_p_local_space_manager...`: boundary cases for empty pool and mid-pool gap returning a
    defined (NULL or valid) pointer, not an indeterminate one.

- **Blast radius (test impact):** **Medium.** No existing assertions break, but a meaningful new
  test surface is required across three batches. A phased rollout (batches A→B→C) is recommended
  so each subsystem's invariants are verified before moving on.

## 5. Blast Radius Summary

- **Files changed:** primarily `core/source/game.c` (10 of 11 functions) plus
  `core/include/game.h` (`manage_game` removal/comment). No other translation unit needs source
  edits; the fixes are localized to these functions.
- **Behavior-preserving for current callers?** Mostly tightening: pool and save fixes remove UB/
  leaks without changing the happy path. Two are observable changes: `receive__multiplayer` now
  reports real failures (callers of `receive_game_action` see `false` where they saw a spurious
  `true`), and `broadcast_game_action`/tick-timer start producing their intended per-client
  dispatches / correct tick counts.
- **De-facto contracts invalidated:** the "always-true" receive contract and the
  "freed-but-not-reset" multiplayer/pool state are the two implicit contracts that correction
  removes; both are defects, not relied-upon guarantees.
- **Phased approach:** Yes — three atomic batches (pool lifecycle / multiplayer routing / misc)
  as described in the Resolution Assessment.
