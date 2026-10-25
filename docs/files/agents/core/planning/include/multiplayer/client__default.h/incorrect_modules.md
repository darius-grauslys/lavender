# Planning: client__default.h — Incorrect Modules

**Review source:** `agents/core/review/include/multiplayer/client__default.h/incorrect_modules.md`

**Review entry:** `agents/core/review/include/multiplayer/client__default.h/m_poll_tcp_socket_manager_as__client__default.md`

**Source files reviewed (read-only):**
- `core/source/multiplayer/client__default.c` (the flagged function)
- `core/include/multiplayer/client__default.h`
- `core/source/multiplayer/tcp_socket.c` (`receive_bytes_over__tcp_socket`, `get_latest__delivery_from__tcp_socket`)
- `core/include/multiplayer/tcp_socket.h` (return-value contracts)
- `core/source/multiplayer/server__default.c` (reference implementation)
- `core/include/game.h` (inline `receive_game_action`, `get_p_client_by__index_from__game`)
- `core/source/game.c` (`begin_multiplayer_for__game`, `poll_multiplayer`, `m_game_action_handler__receive__multiplayer`)
- `tests/core/source/multiplayer/test_suite_multiplayer_client__default.c`

---

## 1. Problem Identification

The review flags `m_poll_tcp_socket_manager_as__client__default`
(`core/source/multiplayer/client__default.c`) as **Incorrect**. Its high-level
intent — poll the client's server-bound socket (`tcp_sockets[0]`) and dispatch
received game actions to the local client — is implemented, but it diverges from
the server-side reference (`m_poll_tcp_socket_manager_as__server__default`) in
ways that produce a functional defect and a latent undefined-behavior (UB) risk.

### Issue 1 — Return value of `get_latest__delivery_from__tcp_socket` ignored (State Desync / Representation Invariant)

The server reference wraps the call in a `while` loop that **drains all** queued
packets per poll cycle:

```c
// server__default.c
while (get_latest__delivery_from__tcp_socket(
        p_tcp_socket__client, &deliver.tcp_packet)) {
    deliver.game_action.uuid_of__client__u32 = GET_UUID_P(p_tcp_socket__client);
    receive_game_action(p_game, GET_UUID_P(p_client), &deliver.game_action);
}
```

The client calls it **once, unconditionally**, and ignores the `bool` return.
`get_latest__delivery_from__tcp_socket` (`tcp_socket.c`) returns `false` when
`quantity_of__received_packets == 0`. Consequences:

- **Uninitialized read / UB:** when the call returns `false`, the `delivery`
  union is never written, yet the code then reads `delivery.game_action` (the
  assignment `...uuid_of__client__u32 = 0` and the full-struct pass to
  `receive_game_action`). Reading an uninitialized union member violates the
  **Representation Invariant** that a `TCP_Packet` is only meaningful after a
  successful dequeue — undefined behavior.
- **Packet-loss / starvation (Conservation Law):** even when data is present,
  only **one** packet is dequeued per poll instead of draining the queue. The
  client falls behind the server and effectively drops/starves inbound game
  actions — a **State Desync** between the socket's receive queue and the local
  client state.

### Issue 2 — `uuid_of__client__u32` hardcoded to a bare `0` (Translation Gap / Sentinel)

The server sets `deliver.game_action.uuid_of__client__u32 =
GET_UUID_P(p_tcp_socket__client)` (the originating socket's uuid). The client
hardcodes `delivery.game_action.uuid_of__client__u32 = 0`.

Semantically this field is the **originating client** of the action. A
server-originated action has no originating *client* in the local pool, so
zeroing is arguably intentional — but it is a **Translation Gap**: the client
does not derive the field from a documented source and uses an un-named `0`
instead of a `Sentinel`. Correctness then silently depends on every downstream
handler treating `0` as "server-originated / no client". Flagged as a semantic
observation, not a definite defect.

### Issue 3 — Error-code handling for `receive_bytes_over__tcp_socket` (Boundary Condition)

`receive_bytes_over__tcp_socket` returns `i32`: positive on success, `0` on
no-data / `TCP_ERROR__DESTINATION_OVERFLOW`, and a **negative**
`TCP_ERROR__QUEUE_FULL` when the receive queue is full. The guard
`if (!receive_bytes_over__tcp_socket(...))` uses boolean negation: `!(-2)` is
`false`, so a queue-full error is treated as "data received" and processing
proceeds into the (broken) delivery path. This **Boundary Condition** conflates
the error path with the no-data path. It is the same idiom the server uses, so
it is not unique here — but fixing it requires the `receive_bytes_over__tcp_socket`
return contract to be stable.

### Issue 4 — No null-check on `p_client` before `GET_UUID_P(p_client)` (Precondition / Boundary Condition)

`get_p_client_by__index_from__game(p_game, 0)` may return `NULL` (unallocated
client pool or out-of-bounds index — see the debug guards in `game.h`).
`GET_UUID_P(NULL)` then reads `->uuid` through a null pointer (UB). The stated
**Precondition** requires a valid client at index 0; the code enforces none. A
debug-build assertion or guard would make the precondition observable.

### Issue 5 — `#ifndef IS_SERVER` stubbed to `#if 1` (Stub-real divergence / Surface-form leakage)

The source contains:
```c
//#ifndef IS_SERVER
#if 1
```
The real conditional-compilation guard is commented out and replaced with `#if 1`,
so the client poll body compiles unconditionally — including in server builds.
This is a **Stub-real divergence**: the placeholder satisfies structural checks but
violates the semantic contract that client-only code be excluded from server mode.
The server source mirrors this (`// #ifdef IS_SERVER` → `#if 1`), compounding the
**Surface-form leakage** across both translation units.

---

## 2. Impact Assessment

### 2.1 Callers and dependents (verified in `core/source/game.c`)

- **`poll_multiplayer(Game*)`:** invokes
  `p_game->pM_tcp_socket_manager->m_poll_tcp_socket_manager(...)` **every tick**.
  In client mode this callback is `m_poll_tcp_socket_manager_as__client__default`,
  so the broken behavior is exercised on **every tick** of a multiplayer client
  session. The drain-all fix (Issue 1) raises the per-tick dispatch rate — the
  intended correction, but it changes the throughput/timing contract callers rely on.

- **`begin_multiplayer_for__game(Game*, m_Poll_TCP_Socket_Manager)`:** registers
  the poll callback via `initialize_tcp_socket_manager` and, in client mode
  (`max_quantity_of__clients == 1`), sets
  `p_game->m_game_action_handler__receive =
  m_game_action_handler__receive__multiplayer`. This is where the broken function
  is wired in; no signature change is required by the fixes.

- **`m_game_action_handler__receive__multiplayer`** (the receive sink, reached via
  the inline `receive_game_action` in `game.h`): dispatches on
  `is_game_action__local(p_game_action)` (reads `game_action_flags`, **not** the
  `uuid_of__client__u32` field) and then calls
  `receive_game_action_for__client`. It is not itself broken, but its **call
  frequency changes** with the drain-all fix. Any timing-sensitive assumption in
  deeper handlers (process spawning, entity updates) is affected.

- **`receive_game_action` (inline, `game.h`):** resolves the recipient via
  `get_p_client_by__uuid_from__game(p_game, uuid_of__client__u32)` using the
  *argument* (`GET_UUID_P(p_client)`), then forwards the `Game_Action*`. The
  client poll function already looked up `p_client` by index, so this is a
  redundant double-lookup (**Don't Repeat Yourself**). The **field**
  `p_game_action->uuid_of__client__u32` (hardcoded `0`) is what any deeper reader
  of `get_client_uuid_from__game_action` / `GA_UUID_SOURCE` observes.

- **`tcp_sockets[0]` receive queue:** `receive_bytes_over__tcp_socket` appends
  packets; `get_latest__delivery_from__tcp_socket` advances
  `index_of__enqueue_begin` and decrements `quantity_of__received_packets`. The
  current single-call pattern leaves queued packets undrained (the **State
  Desync** of Issue 1); switching to a `while` loop drains them, changing queue
  cadence.

### 2.2 Existing tests

`tests/core/source/multiplayer/test_suite_multiplayer_client__default.c` contains
a single test, `...__symbol_exists`, which only asserts the function pointer is
non-null. It asserts **no** behavioral property, so:
- It will still pass after the fixes (symbol existence unchanged).
- No existing assertion is invalidated pre- or post-flag.
- New behavioral tests are required (see §4).

### 2.3 De facto contracts invalidated by the correction

The current single-call pattern has established a **de facto contract** of
one dispatched action per poll cycle; any downstream rate-limiting / frame
coalescing that assumes this cadence is affected. Additionally:
- `uuid_of__client__u32 == 0` for all client-received actions (Issue 2).
- `receive_bytes_over__tcp_socket` error codes silently ignored (Issue 3).
- Client poll code compiled into server builds (Issue 5).

---

## 3. Resolution Assessment

### 3.1 Issue 1 — Drain the queue; eliminate the uninitialized read

**Change:** replace the single unconditional call with a `while` loop matching
the server reference, and scope/initialize the union so it is only read after a
successful dequeue:

```c
union { Game_Action game_action; TCP_Packet tcp_packet; } delivery = {0};
while (get_latest__delivery_from__tcp_socket(
        p_tcp_socket_to__server, &delivery.tcp_packet)) {
    delivery.game_action.uuid_of__client__u32 = 0;   // see 3.2
    receive_game_action(p_game, GET_UUID_P(p_client), &delivery.game_action);
}
```

Declaring `delivery` inside the loop (or zero-initializing it) is the cleanest
UB fix — the union is only accessed when a packet was actually dequeued.

**Callers:** none — `receive_game_action` signature and the union layout are
unchanged.

**Tests/docs:** a **Property Based Testing** case asserting drain-all (N queued
→ N dispatched in one poll); a **Fuzzing** / sanitizer case on the empty-queue
boundary to prove no uninitialized read.

### 3.2 Issue 2 — Make the origin field explicit (Sentinel / SSOT)

**Change:** do not force the field to the socket uuid (the server is not a client
in the local pool, so that would be semantically wrong). Instead, replace the bare
`0` with a named `Sentinel` (e.g. `IDENTIFIER__UNKNOWN__u32`) and document that
server-originated actions carry "no client origin". This removes the **Translation
Gap** by making the intent explicit and gives downstream readers a single,
documented source of truth (**Single Source of Truth**) for "no client".

**Callers:** audit any handler reading `get_client_uuid_from__game_action` /
`GA_UUID_SOURCE` on inbound actions to confirm they already treat the sentinel as
"server-originated". No signature change.

**Tests/docs:** an **Equivalence Check** confirming the client and server dispatch
paths agree on origin semantics for the same action class.

### 3.3 Issue 3 — Distinguish error returns from no-data (Boundary Condition)

**Change:** replace `if (!receive_bytes_over__tcp_socket(...))` with an explicit
three-way check on the `i32` return, logging and skipping on
`TCP_ERROR__QUEUE_FULL`:

```c
i32 received = receive_bytes_over__tcp_socket(p_tcp_socket_to__server);
if (received <= 0) {
    if (received == TCP_ERROR__QUEUE_FULL)
        debug_error("client poll: receive queue full");
    break;
}
```

**Dependency:** this is only correct once `receive_bytes_over__tcp_socket`'s
return contract is stable (it currently returns a computed max-size and swallows
`TCP_ERROR__DESTINATION_OVERFLOW` as `0`). Coordinate with that function's own
review resolution.

**Callers:** the server poll uses the same idiom; apply consistently to both for
**Don't Repeat Yourself**.

**Tests/docs:** a **Mutation Testing** case with a full queue, verifying the error
is logged and the socket is skipped rather than silently processed.

### 3.4 Issue 4 — Guard the `p_client` precondition (Precondition)

**Change:** after `get_p_client_by__index_from__game(p_game, 0)`, add a guard:

```c
if (!p_client) {
    debug_warning("client poll: local client not allocated");
    return;   // do not deref NULL via GET_UUID_P
}
```

This makes the stated precondition observable and removes the null-deref UB.

**Callers:** none — defensive guard internal to the function.

**Tests/docs:** a **Fuzzing** case with an unallocated pool / out-of-bounds index,
verifying no null deref.

### 3.5 Issue 5 — Restore the `IS_SERVER` guard (Surface-form leakage)

**Change:** restore `#ifndef IS_SERVER ... #endif` (client) and `#ifdef IS_SERVER
... #endif` (server), replacing the `#if 1` stubs in **both** translation units so
client code is excluded from server builds and vice versa.

**Callers:** none at source level; verify the affected build configurations (e.g.
the `IS_SERVER`-defined targets) still compile.

**Tests/docs:** a **Lint Gate** / compile-time check that `IS_SERVER` builds exclude
client-only poll code.

---

## 4. Test Verification Checklist

- **Existing test** (`test_suite_multiplayer_client__default.c`): symbol-existence
  only; no behavioral assertions. No existing assertion is invalidated.
  **Status: passes after fix.**
- **New tests needed:**
  - **Property Based Testing** — drain-all invariant: N queued packets ⇒ N
    dispatches in a single poll call.
  - **Fuzzing** (sanitizer-instrumented) — empty-queue boundary: no uninitialized
    read when `get_latest__delivery_from__tcp_socket` returns `false`.
  - **Fuzzing** — null `p_client`: no null deref on unallocated/out-of-bounds pool.
  - **Mutation Testing** — queue-full: `TCP_ERROR__QUEUE_FULL` is detected and the
    socket skipped, not treated as data.
  - **Equivalence Check** — client vs. server dispatch agree on origin-field
    semantics for equivalent action classes.
  - **Lint Gate** — `IS_SERVER` builds exclude client-only poll code.
- **Harness note:** new tests need a `TCP_Socket_Manager` with a populated packet
  queue plus a mocked `Game` (client pool + `m_game_action_handler__receive`) —
  the same shape as the server-side test infrastructure.
- **Blast radius (test):** Low. Only one symbol-only test exists; no phased
  approach needed for tests.

---

## 5. Blast Radius Summary

- **Files affected:**
  - `core/source/multiplayer/client__default.c` — primary fix site (Issues 1–5).
  - `core/source/multiplayer/server__default.c` — coordinated fix for Issue 3 (same
    error idiom) and Issue 5 (`#if 1` stub); the two poll handlers are **Coupled**
    by the shared drain-all pattern.
  - `core/source/multiplayer/tcp_socket.c` — return-contract stabilization for
    `receive_bytes_over__tcp_socket` (Issue 3 dependency).
  - `core/source/game.c` — no change required, but `poll_multiplayer` dispatch
    cadence and `m_game_action_handler__receive__multiplayer` call frequency change
    as a consequence of Issue 1.
  - `tests/core/source/multiplayer/test_suite_multiplayer_client__default.c` — new
    behavioral tests.
- **Behavior-preserving for current callers?** No. The drain-all fix changes the
  cadence from one action per tick to all-queued-actions per tick — the intended
  correction, but it invalidates the de facto one-action-per-tick contract.
- **Phased approach needed?** Yes:
  - **Phase 1** (Issue 1): drain-all + union initialization — highest-impact
    functional + UB fix.
  - **Phase 2** (Issues 3–4): error-code handling + null guard — removes crashes,
    improves observability; Issue 3 depends on stabilizing the socket return
    contract.
  - **Phase 3** (Issues 2, 5): origin-field `Sentinel` + restore `IS_SERVER`
    guards — lower-risk cleanup and consistency work.
- **De facto contracts invalidated:** one-action-per-poll cadence (Issue 1);
  `uuid_of__client__u32 == 0` for all client-received actions (Issue 2); silently
  ignored socket error codes (Issue 3); client poll code compiled into server
  builds (Issue 5).
