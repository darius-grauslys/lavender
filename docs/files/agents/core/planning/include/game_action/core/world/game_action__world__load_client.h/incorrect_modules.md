# Planning: game_action__world__load_client — Incorrect Modules

**Review source:** `agents/core/review/include/game_action/core/world/game_action__world__load_client.h/incorrect_modules.md`

**Source files reviewed (read-only):**
- `core/include/game_action/core/world/game_action__world__load_client.h`
- `core/source/game_action/core/world/game_action__world__load_client.c`
- `tests/core/source/game_action/core/world/test_suite_game_action_core_world_game_action__world__load_client.c`

**Flagged function:** `m_process__game_action__world__load_client__outbound`
(registered at line 214 as the outbound process handler for `Game_Action_Kind__World__Load_Client`)

---

## 1. Problem Identification

The outbound process handler for the "world load client" action is flagged **Incorrect**. It has two correctness defects that break its stated Postconditions, plus one minor cleanup item.

### Defect A — NULL pointer dereference on the teleport path (line 124)
The function computes the comparison position `gsv__3i32` (lines 112–118) with a correct ternary fallback: use the hitbox position if `p_hitbox_aabb` is non-null, otherwise the world spawn point. However, when a position mismatch triggers a teleport, line 124 calls `get_position_3i32F4_of__hitbox_aabb(p_hitbox_aabb)` **unconditionally**, ignoring the same fallback. When `p_hitbox_aabb` is NULL this violates the Precondition of `get_position_3i32F4_of__hitbox_aabb` (non-null input). In debug builds the internal null check logs and returns a `VECTOR__3i32F4__OUT_OF_BOUNDS` sentinel; in release builds (`NDEBUG`) that check compiles out, yielding a direct NULL dereference — undefined behavior. This breaks Postcondition #2 (teleport must enqueue a well-formed process).

### Defect B — Early return skips enqueue on the create-client path (line 176)
When the client file does not exist (`index_of__path_to__base_directory == 0`), the function dispatches a create-client handler process into `p_process` but then executes `return;` at line 176. This early return skips the null check (line 185) and the `enqueue_process` call (line 195). Consequence: the dispatched create-client process is never enqueued as a child and never executes, and the current process neither completes nor fails — it silently abandons the action. This is a **State Desync** between "process was dispatched" and "process was registered to run," violating Postcondition #5/#6 and the Conservation Law that every dispatched process must be either enqueued or failed. The `else` branch (load existing client) correctly falls through to enqueue, so the two branches are asymmetric.

### Defect C — Dead store (line 160)
`index_of__path` is assigned the return value of `stat_client_file` but never read; only `index_of__path_to__base_directory` is used. Harmless but wasteful; cleanup only.

---

## 2. Impact Assessment

**Dispatch routing.** `m_process__game_action__world__load_client__outbound` is the single registered outbound handler for `Game_Action_Kind__World__Load_Client` (see `register_game_action__world__load_client`, lines 200–218). Every inbound/outbound dispatch of this game action funnels through it, so both defects affect all callers of the "load client" action.

**Defect A blast radius.** Affects any client that is already loaded, has **no** hitbox AABB, and is not yet at its target position. Today the teleport target is undefined (release) or an out-of-bounds sentinel (debug). Correcting it to use the world-spawn fallback turns UB into defined behavior and makes the teleport target consistent with the position that was actually compared (`gsv__3i32`). For clients **with** a hitbox AABB the value passed is unchanged, so this path is behavior-preserving. No other function relies on the broken (dereferencing) behavior.

**Defect B blast radius.** Affects the "create new client" branch (file absent). Today the action stalls: because the create process never runs and the current process neither completes nor fails, control re-enters on retry until the attempt counter exceeds 16, at which point a `bad_request` (error code 3) is dispatched and the process fails. Any caller relying on this action to bring a fresh client online is therefore effectively broken. Correcting it makes the create path enqueue and run, matching the load path — this removes a de facto "silently times out for new clients" behavior that downstream logic may have come to depend on as a failure signal. Callers that treat error code 3 as "client could not be loaded" should be re-checked, since successful creation will now short-circuit before that timeout.

**No test contract invalidated.** The existing test suite (see §4) covers only the `initialize_*` and `register_*` functions; no test exercises the outbound process, so neither defect is codified as a de facto contract in tests.

---

## 3. Resolution Assessment

All fixes are localized to `m_process__game_action__world__load_client__outbound` in
`core/source/game_action/core/world/game_action__world__load_client.c`. No header signature changes; no caller updates required.

**Fix A (line 124) — align teleport target with the comparison source.**
Replace the unconditional `get_position_3i32F4_of__hitbox_aabb(p_hitbox_aabb)` with the same ternary fallback used for `gsv__3i32`:
```c
Process *p_process__teleport_client =
    teleport_client(
        p_game,
        p_client,
        (p_hitbox_aabb)
            ? get_position_3i32F4_of__hitbox_aabb(p_hitbox_aabb)
            : get_spawn_point_of__world(get_p_world_from__game(p_game)));
```
This enforces a single source of truth (SSOT / DRY): the position used to detect the mismatch and the position passed to the teleport must be identical. Callers: none. Tests/docs: add a regression test (see §4).

**Fix B (line 176) — remove the premature `return;`.**
Delete the `return;` at line 176 so the create-client branch falls through to the shared null check (line 185) and `enqueue_process` (line 195), making it symmetric with the load-existing branch. This restores the Conservation Law for dispatched processes. Callers: none (behavioral correction, not signature change). Tests/docs: add a regression test asserting enqueue + pending state.

**Fix C (line 160) — remove the dead store.**
Drop the unused `index_of__path` assignment (keep only `index_of__path_to__base_directory`). Optional, low priority; do not couple to Fix A/B.

**Phasing.** The two functional fixes are independent and localized; a phased approach is not required. If desired, land Fix B first (restores the functional create path) and Fix A second (removes the UB). Fix C can ride along as a cleanup.

---

## 4. Test Verification Checklist

**Existing tests.** `test_suite_game_action_core_world_game_action__world__load_client.c` contains three stateless tests: `...initialize__sets_kind`, `...initialize__sets_client_uuid`, and `...register__populates_table`. None reference the outbound process, `teleport_client`, create-client dispatch, hitbox AABB, or spawn point. **No existing assertion is invalidated** by Fix A or Fix B.

**New tests required** (the outbound process is currently untested):
- **Equivalence Check / Round Trip Check** — loaded client *with* hitbox AABB at the correct position: assert the process completes and both the hitbox AABB and client are set active (guards the unchanged happy path of Fix A).
- **Boundary Condition / null input** — loaded client with `p_hitbox_aabb == NULL` and a mismatched position: assert a teleport process is enqueued using the world spawn point and that no out-of-bounds/UB occurs (regression for Defect A).
- **Round Trip Check** — client file does not exist: assert the create-client handler process is enqueued as a child of `p_this_process` and the current process remains pending (regression for Defect B).
- **Equivalence Check** — create path and load-existing path produce symmetric enqueue behavior (asserts the two branches converge on the shared null-check + enqueue).
- **Property Based Testing** — sweep the attempt counter around the timeout boundary to confirm bounded retry and that a failed dispatch still routes through `bad_request` (error code 1) / `fail_process`.

**Test blast radius: Medium.** Only new tests are added; no existing assertions change. A phased rollout of tests is not necessary but may follow the fix ordering in §3.

---

## 5. Blast Radius Summary

- **Files changed:** 1 source file (`core/source/game_action/core/world/game_action__world__load_client.c`). Optional: new tests in the existing test suite file. No `.h` changes.
- **Behavior-preserving for current callers?** Fix A is behavior-preserving for all clients with a hitbox AABB and converts UB → defined behavior for those without. Fix B intentionally changes a silently-stalling action into a functioning one; callers that relied on the timeout-driven `bad_request` (error code 3) as the "new client" outcome should be re-verified.
- **De facto contracts invalidated:** None in the test suite. At runtime, the "new-client action stalls until timeout then fails" behavior is deliberately removed — this is the intended correction, not a contract break.
- **Phased approach needed:** No — both functional fixes are contained within one function and are independent.
