# Planning: game_action__bad_request.h — Incorrect Modules

**Review source:** `agents/core/review/include/game_action/core/game_action__bad_request.h/incorrect_modules.md`

**Source files reviewed (read-only):**
- `core/include/game_action/core/game_action__bad_request.h`
- `core/source/game_action/core/game_action__bad_request.c`
- `core/source/game.c` (`get_p_client_by__uuid_from__game`)
- `core/include/client.h` (`get_p_game_action_manager__outbound_from__client`)
- `core/source/game_action/game_action_manager.c` (`get_p_game_action_by__uuid_from__game_action_manager`)
- `core/source/game_action/core/tcp/game_action__tcp_connect.c` (established NULL-guard pattern)
- `tests/core/source/game_action/core/test_suite_game_action_core_game_action__bad_request.c`

---

## 1. Problem Identification

**`m_process__game_action__bad_request__inbound`** (`core/source/game_action/core/game_action__bad_request.c`) — **Incorrect.**

The handler performs a chained lookup: `get_p_client_by__uuid_from__game` → `get_p_game_action_manager__outbound_from__client` → `get_p_game_action_by__uuid_from__game_action_manager`. The first lookup is **Total** in the sense that it legally returns `0` (client pool unallocated, UUID not present, or client deallocated — verified in `core/source/game.c`). The intermediate manager getter is null-safe (`if (!p_client) return 0;`), but the terminal getter dereferences `p_game_action_manager->game_actions` **unconditionally** with no null check. The handler guards only the *result* (`p_game_action__responding_to`) and never the intermediate `p_client`, so a missing client yields a NULL-pointer dereference (undefined behavior / crash).

Two contract violations result:
- **Precondition/Boundary Condition violation**: the handler assumes a non-null client for any inbound bad-request; the unallocated-pool and unknown-UUID boundary conditions are unhandled.
- **Postcondition / State Desync**: the documented postcondition "the process is completed in all code paths" is false on the broken path — the process never reaches `Complete`, leaving process status desynced if execution somehow survives (it does not; it crashes).

The rest of the module (`register_game_action__bad_request`, `initialize_game_action_for__bad_request`, `dispatch_game_action__bad_request`) is correct and out of scope.

## 2. Impact Assessment

**Who relies on the current behavior:**

- The inbound handler has **no direct code callers**. It is invoked data-driven: `register_game_action__bad_request` stores the function pointer in a `Game_Action_Logic_Entry`, and the generic dispatch path (`resolve_game_action` / dispatch handlers in `core/include/game.h`) invokes it when a `Game_Action_Kind__Bad_Request` action arrives inbound. So the blast radius of *correcting* the handler is contained to the dispatch mechanism's expectation that handlers terminate their process.
- The crash path is **not a de facto contract** — no caller can rely on a crash. The only "reliance" is the implicit assumption in the generic process runner that an `m_process` handler always transitions the process to a terminal status (`Complete`/`Fail`). The broken behavior violates that assumption; correcting it *restores* it rather than invalidating it.
- Downstream consumers of `GAME_ACTION_FLAGS__BIT_IS_BAD_REQUEST` (via `is_game_action__bad_request`) are unaffected: the flag is set only on the already-working happy path, which the fix does not change.

**Assumptions invalidated by the correction:**

- None in `./include` or `./source`. The fix adds an early-return branch on a path that currently crashes; every currently-succeeding execution path (client found → action found → flag set → complete; client found → action not found → complete) is bit-for-bit unchanged. No caller signature, data layout, or registered table entry changes.
- The documented postconditions become *true* instead of false: process completion now holds on all code paths.

## 3. Resolution Assessment

**Step 1 — Add the missing null guard in the handler (primary fix).**
In `core/source/game_action/core/game_action__bad_request.c`, after the `get_p_client_by__uuid_from__game` call, insert:

```c
if (!p_client) {
    debug_error("m_process__game_action__bad_request__inbound, p_client == 0.");
    complete_process(p_this_process);
    return;
}
```

Rationale:
- Matches the established pattern in `core/source/game.c` (`dispatch_handler_process_to__create_client`, `dispatch_handler_process_to__load_client`) and `core/source/game_action/core/tcp/game_action__tcp_connect.c`, which both check the client lookup result before proceeding. Keeps validation at the call site — **Single Source of Truth (SSOT)** of the "client may be absent" handling stays with the lookup's callers, as elsewhere in the codebase.
- Uses `complete_process` (not `fail_process`) to stay **Conservative** and consistent with the sibling branch in the same function ("responding action not found → complete without modification"). Both are defensible; choosing `complete` preserves the existing semantics of "lookup miss is a no-op, not an error condition" and keeps both miss branches uniform. If the project later standardizes miss-handling on `fail_process`, both branches change together.

**Step 2 — Optional hardening (defer, separate concern).**
`get_p_game_action_by__uuid_from__game_action_manager` (`core/source/game_action/game_action_manager.c`) dereferences its manager parameter unconditionally. Adding a `if (!p_game_action_manager) return 0;` guard would make the getter itself null-safe and protect any future caller. This touches a shared function used by other modules; it is **Orthogonal** to this fix and should be scoped as its own review/plan if pursued, so this plan's change remains minimal and independently verifiable.

**Step 3 — Header / documentation.**
No header change: `m_process__game_action__bad_request__inbound` is file-local (not declared in the `.h`). The module's public surface (`register_`, `initialize_`, `dispatch_`) is unchanged.

**Step 4 — Tests.**
The existing suite (`test_suite_game_action_core_game_action__bad_request.c`) covers only `initialize_game_action_for__bad_request` (kind, error code, response UUID, bad-request flag) and `register_game_action__bad_request` (table population). **No test exercises the inbound handler** — the crash path was untested. Add to the suite:

1. **Happy path**: game with allocated client pool, client whose outbound manager holds the responding action; run the process; assert flag set on responding action and process status `Complete` (**Equivalence Check** against current happy-path behavior).
2. **Boundary Condition — missing client**: bad-request action carrying an absent/deallocated client UUID; assert no crash, no flag mutation anywhere, process status `Complete`.
3. **Boundary Condition — unallocated pool**: game with `pM_clients == 0`; same assertions as (2).
4. **Known gap (regression pin)**: client present but responding action absent → complete without mutation (already implemented; pin it so the new guard cannot regress it).
5. Optional: **Fuzzing** over `uuid_of__client__u32` / `uuid_of__game_action__responding_to` pairs to confirm the handler is Total across the UUID domain (never crashes, always completes).

Test blast radius: **Low** — one test file extended; all existing assertions remain valid because the fix changes no currently-passing behavior. No phased approach needed.

## 4. Blast Radius Summary

- **Files changed:** 1 source (`core/source/game_action/core/game_action__bad_request.c`), 1 test file. Optional Step 2 would add `core/source/game_action/game_action_manager.c` (deferred).
- **Behavior-preserving for current callers:** Yes — all non-crashing paths unchanged; only the UB path becomes a graceful no-op completion.
- **Phased approach needed:** No.
- **De facto contracts invalidated:** None. The fix restores (not breaks) the process-completion invariant expected by the generic dispatcher.
