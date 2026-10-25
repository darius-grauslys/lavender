# Planning: game_action__tcp_begin_connect — Incorrect Modules

**Review source:** `agents/core/review/include/game_action/core/tcp/game_action__tcp_begin_connect.h/incorrect_modules.md`

**Source files reviewed (read-only):**
- `core/include/game_action/core/tcp/game_action__tcp_begin_connect.h`
- `core/source/game_action/core/tcp/game_action__tcp_begin_connect.c`
- `tests/core/source/game_action/core/tcp/test_suite_game_action_core_tcp_game_action__tcp_begin_connect.c`
- `core/include/multiplayer/tcp_socket.h` (state accessor surface)

---

## 1. Problem Identification

Two functions in `game_action__tcp_begin_connect.c` are flagged **Incorrect**.

### 1a. `m_process__game_action__tcp_connect__begin`

- **State Desync / Representation Invariant violation (Accept case).** In the
  `Game_Action_Kind__TCP_Connect__Accept` branch, the socket state is set to
  `TCP_Socket_State__Authenticated`, then immediately overwritten to
  `TCP_Socket_State__Connected`. The surviving final state is `Connected`, which
  is the *pre-authentication* state. This breaks the intended
  `Connected → Authenticating → Authenticated` progression and violates the
  socket state machine's Representation Invariant. On any subsequent run (or any
  external inspection), the `Connected` case re-dispatches `connect` and re-enters
  `Authenticating`, producing a **Cascade Failure** of duplicate connection
  attempts / an infinite loop.
- **Missing Precondition guard (null socket).** `get_p_tcp_socket_for__this_uuid`
  may return null, but the function immediately dereferences the result via
  `get_state_of__tcp_socket(p_tcp_socket)` with no null check → undefined
  behavior. This is an unguarded **Boundary Condition**.
- **Unchecked return value (uninitialized read).** In the `Authenticating` case,
  `get_latest__delivery_from__tcp_socket` returns a `bool` that is not checked.
  On `false`, the `delivery` union is left uninitialized and
  `get_kind_of__game_action(&delivery.ga_response)` reads indeterminate memory.

### 1b. `m_process__game_action__tcp_connect__begin__init`

- **Null dereference on client lookup.** `get_p_client_by__uuid_from__game` can
  return null; the result is passed straight to `GET_UUID_P(p_client)`, which
  dereferences it as a `Serialization_Header*`. Missing **Precondition** guard →
  undefined behavior.
- **Null dereference on socket open.** `open_socket_on__tcp_socket_manager__ipv4`
  can return null (platform connect failure or pool exhaustion); the result is
  passed straight to `set_tcp_socket_as__manually_driven(p_tcp_socket)`, which
  dereferences `p_tcp_socket->tcp_socket_flags__u8`. Missing **Precondition**
  guard → undefined behavior.

Both functions perform resource acquisition / process setup rather than
Lavender-style struct reset; that naming distinction is not itself a defect. The
defects are the state overwrite and the missing null guards.

---

## 2. Impact Assessment

- **State-machine consumers of `TCP_Socket` state.** Anything that reads
  `get_state_of__tcp_socket` to branch on connection progress is **Coupled** to
  the socket's state being a **Single Source of Truth (SSOT)**. The buggy
  overwrite makes a successfully-authenticated socket *appear* unauthenticated
  (`Connected`). Callers or follow-up processes that treat `Connected` as
  "auth not yet started" will re-trigger the connect dispatch. Correcting the
  overwrite to leave the socket in `Authenticated` invalidates any downstream
  code that has come to rely on the de-facto "post-accept == Connected" behavior;
  such reliance would be a latent **State Desync** and must be audited and removed.
- **Process lifecycle.** `complete_process` is called in the Accept path, so in
  the happy path the process is not re-run by its own loop — the infinite-loop
  risk is bounded to external/other processes inspecting the socket state after
  completion. Blast radius of the state fix is therefore localized to other
  readers of socket state, not the process's own control flow.
- **Callers of the init function.** `register_game_action__tcp_connect__begin`
  wires `m_process__game_action__tcp_connect__begin__init` as the process init
  handler and `m_process__game_action__tcp_connect__begin` as the run handler.
  Adding null guards changes only the *failure* path (early return / no-op) and
  is behavior-preserving for all currently-valid inputs; no caller contract
  changes.
- **Data structures.** No struct layout or serialization format changes are
  required. The fix is confined to control flow within the two functions.

---

## 3. Resolution Assessment

### `m_process__game_action__tcp_connect__begin`
1. **Remove the overwrite.** Delete the trailing
   `set_state_of__tcp_socket(p_tcp_socket, TCP_Socket_State__Connected)` in the
   Accept branch so the socket remains in `TCP_Socket_State__Authenticated`.
   This restores the state machine's Representation Invariant. Callers need no
   signature change.
2. **Guard the null socket.** After `get_p_tcp_socket_for__this_uuid`, if the
   returned pointer is null, treat it as a failed/bad-state path (log and
   `fail_process`) instead of dereferencing. Establish the **Precondition** that
   a valid socket exists before entering the state switch.
3. **Check the delivery return.** In the `Authenticating` case, only proceed into
   the response `switch` when `get_latest__delivery_from__tcp_socket` returns
   true; otherwise break (leave state as-is). Optionally initialize the
   `delivery` union defensively.

### `m_process__game_action__tcp_connect__begin__init`
1. **Guard the client lookup.** After `get_p_client_by__uuid_from__game`, if
   null, do not call `GET_UUID_P`; instead fail/skip socket open (and, per the
   existing TODO, surface a bad-action error once UUID resolution lands).
2. **Guard the socket open.** After `open_socket_on__tcp_socket_manager__ipv4`,
   if null, skip `set_tcp_socket_as__manually_driven` and do not install the run
   handler.

### Tests / docs
- The existing test file covers **only** registration
  (`register__populates_table`); it asserts nothing about the process handler or
  init behavior, so no existing assertion is invalidated by these fixes.
- New tests are required (see §4). No public header signature changes, so header
  documentation is unaffected; add a short note to the spec on the socket state
  progression invariant.

### Phasing
- **Phase 1 (behavior-correct, low risk):** remove the Accept overwrite and add
  the three null/return guards. All changes are behavior-preserving for valid
  inputs and only alter failure paths.
- **Phase 2 (audit):** grep all readers of `get_state_of__tcp_socket` to confirm
  no code relies on the old post-accept `Connected` de-facto contract; fix any
  found.

---

## 4. Test Verification Checklist

- **Existing tests:** only registration is tested; no assertion touches the
  buggy process/init paths, so the fix invalidates nothing. **Test impact: Low.**
- **New tests needed:**
  - `m_process__game_action__tcp_connect__begin`:
    - **Round Trip Check** of the state machine: drive a socket through
      `Connected → Authenticating → (Accept) → Authenticated` and assert the
      terminal state is `Authenticated` (not `Connected`).
    - **Property Based Testing** / **Equivalence Check**: after an Accept, a
      second invocation must *not* re-dispatch connect (idempotence of the
      authenticated terminal state).
    - **Boundary Condition** cases: null socket from lookup → process fails, no
      crash; `get_latest__delivery` returning false → no uninitialized read.
  - `m_process__game_action__tcp_connect__begin__init`:
    - **Boundary Condition** cases: `get_p_client_by__uuid_from__game` returns
      null; `open_socket_on__tcp_socket_manager__ipv4` returns null → no
      dereference, handler not installed.
- **Recommendation:** add these as new Munit test functions in
  `test_suite_game_action_core_tcp_game_action__tcp_begin_connect.c`; consider
  **Mutation Testing** to confirm the guards are actually exercised (a mutation
  removing a guard should be caught).

---

## 5. Blast Radius Summary

- **Files changed:** 1 source file
  (`core/source/game_action/core/tcp/game_action__tcp_begin_connect.c`) + 1 test
  file. No header or struct-layout changes.
- **Behavior-preserving for valid callers:** Yes — the fix only alters the
  failure paths and corrects one terminal state value.
- **Phased approach:** Recommended (Phase 1 fix + Phase 2 audit of socket-state
  readers).
- **De-facto contracts invalidated:** Any downstream code assuming
  "post-accept socket state == `Connected`" is a latent **State Desync** and must
  be corrected in Phase 2. Overall blast radius: **Low–Medium**.
