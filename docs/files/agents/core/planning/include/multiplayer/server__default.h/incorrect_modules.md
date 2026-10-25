# Planning: server__default.h — Incorrect Modules

**Review source:** `agents/core/review/include/multiplayer/server__default.h/incorrect_modules.md`

**Source files reviewed (read-only):**
- `core/include/multiplayer/server__default.h`
- `core/source/multiplayer/server__default.c`
- `core/include/multiplayer/tcp_socket.h` (TCP_DELIVERY macro, socket I/O API)
- `core/source/multiplayer/tcp_socket.c` (`receive_bytes_over__tcp_socket`, `get_latest__delivery_from__tcp_socket`)
- `core/include/types/core/game_action/tcp/ga_type__tcp__connect_begin.h` (`get_session_token_from__ga_tcp_connect__begin`)
- `core/include/game_action/core/tcp/game_action__tcp_connect.h` (`receive_game_action__connect`)
- `core/include/defines.h` (`Session_Token`, `TCP_Socket_Manager`, `Game_Action`, types)
- `core/include/platform_defaults.h` (`MAX_QUANTITY_OF__TCP_SOCKETS`)
- `tests/core/source/multiplayer/test_suite_multiplayer_server__default.c` (if applicable)

**Flagged as Incorrect in review:**
- `handle_pending_connection` — `**Incorrect**`
- `m_poll_tcp_socket_manager_as__server__default` — `**Incorrect**` (Bug 1, Bug 2, Bug 3)

---

## 1. Problem Identification

### `handle_pending_connection` (server__default.c)

- **P1 — Session-token narrowing (`Non-Injective Translation` / `Mode Confusion`).**
  `get_session_token_from__ga_tcp_connect__begin(...)` returns a `Session_Token`,
  whose `.session_token` field is `Identifier__u64` (`uint64_t`, verified in
  `defines.h`). It is passed positionally to
  `receive_game_action__connect(Game*, Identifier__u32)`. This performs an
  implicit u64→u32 narrowing: any token whose high 32 bits are non-zero maps to
  a different lower-32-bit value, so two distinct 64-bit tokens can collide.
  The mapping is **not injective**. The callee carries `#warning u32 sess token`
  and a `// TODO Why is a u32 session token being used here`, confirming an
  unresolved type-width contract mismatch.

- **P2 — `TCP_DELIVERY` usage (verification note).**
  The review's "Critical Bug: Undeclared variable `delivery`" is based on the
  macro expanding to an anonymous union *type* with no declarator. **Verified
  against current source:** `handle_pending_connection` already writes
  `TCP_DELIVERY(Game_Action, ga_connect) delivery;`, i.e. the declarator is
  present and the code compiles as written. This specific defect appears to have
  been since corrected. The plan retains P2 only as a **regression guard** (see
  Resolution R2) so the macro's no-declarator expansion cannot silently revert
  to an empty declaration.

- **P3 — Uninitialized delivery buffer (minor, `Representation Invariant`).**
  `delivery` is not zero-initialized before `PLATFORM_tcp_recieve`. If fewer than
  `sizeof(delivery)` bytes are received, the unread union region is
  indeterminate and a subsequent kind-dispatch reads garbage. Tolerable only if
  the transport contract guarantees full-buffer fill or an error return.

### `m_poll_tcp_socket_manager_as__server__default` (server__default.c)

- **P4 — Null `p_client` dereference (`Precondition` violation / UB).**
  `get_p_client_by__uuid_from__game(...)` may return NULL when no client is
  registered for the socket's UUID. The result is used unguarded:
  `GET_UUID_P(p_client)` dereferences NULL → undefined behavior. A packet from a
  socket whose client was never created (or was evicted) crashes the poll loop.

- **P5 — Error-code conflation in `receive_bytes_over__tcp_socket` handling
  (`Mode Confusion`).**
  The call site uses `if (!receive_bytes_over__tcp_socket(...)) continue;`.
  That predicate collapses three distinct return modes into one branch:
  - `0` = no data (legitimate "skip"),
  - positive = `MAX_SIZE_OF__TCP_PACKET * quantity` (proceed to drain),
  - `TCP_ERROR__QUEUE_FULL` (negative) = backpressure / overflow.
  Treating a negative error identically to "no data" silently discards the
  overflow diagnostic; a persistently full queue is never surfaced.

- **P6 — Out-of-bounds socket-array access (`Boundary Condition`).**
  The function reads `ptr_array_of__tcp_sockets[0]` (server) and `[1]` (auth),
  assuming ≥2 entries. `MAX_QUANTITY_OF__TCP_SOCKETS` defaults to `1`
  (`platform_defaults.h`), so on any platform that does not override it the
  `[1]` read is out of bounds. The `#ifndef NDEBUG` guard only checks
  `p_tcp_socket__server != NULL`; it does **not** assert the array is wide enough.

---

## 2. Impact Assessment

**Coupling surface (what relies on the broken behavior):**

- **`receive_game_action__connect` (callee, `game_action__tcp_connect.c/.h`).**
  Its `Identifier__u32` parameter is the SSOT for the connect path. Any caller
  that feeds a full 64-bit token depends on the current (lossy) truncation.
  Widening the parameter to `Identifier__u64` (or passing a `Session_Token` by
  value) is **not** behavior-preserving for downstream code that assumes a 32-bit
  session identity; the `#warning`/TODO in the implementation shows the width is
  a live, unresolved decision. Callers and the token→client-UUID derivation must
  be reconciled together.

- **`m_poll_tcp_socket_manager_as__server__default` callers.**
  It is installed as `TCP_Socket_Manager.m_poll_tcp_socket_manager` and invoked
  each tick for the server. Correcting P4 (guarding `p_client`) changes control
  flow: packets from unknown-UUID sockets will now be *dropped/logged* instead of
  crashing. Any code that (implicitly) relies on "a socket always has a live
  client" is making an assumption the fix invalidates — that assumption is not
  guaranteed by any `Precondition` and must be made explicit.

- **`receive_bytes_over__tcp_socket` return contract (`tcp_socket.c`).**
  The negative `TCP_ERROR__QUEUE_FULL` value is a real signal today, but no
  caller currently distinguishes it. Introducing distinct handling in the server
  poll (log/backoff on overflow) establishes a new de-facto contract that other
  pollers (e.g. the client-side poller in `client__default.c`) may also need to
  honor for consistency (DRY).

- **`MAX_QUANTITY_OF__TCP_SOCKETS` / `TCP_Socket_Manager` layout.**
  The `[0]`=server, `[1]`=auth indexing is a hard assumption baked into the
  server poll. Platforms that keep the default of `1` are already out of bounds;
  platforms that override to ≥2 are safe. Fixing this invalidates any assumption
  that the pointer array is guaranteed to hold an auth slot — the layout must be
  either enforced (asserted) or made data-driven (an explicit count/role field).

**De-facto contracts invalidated by the fix:**
- "A registered socket always resolves to a non-NULL client" (P4) — no such
  invariant is currently enforced; the fix makes the code correct *without* it.
- "`receive_bytes_over__tcp_socket` returning 0 means 'nothing to do'" (P5) —
  overloads the zero sentinel with an error mode; separating them changes the
  observable behavior of the poller on a full queue.
- "The socket pointer array has ≥2 entries" (P6) — currently assumed, not checked.

---

## 3. Resolution Assessment

### R1 — Fix session-token width (`handle_pending_connection`)
- **Change:** align the token width across the connect path. Preferred: widen
  `receive_game_action__connect` to accept `Identifier__u64` (or pass the whole
  `Session_Token`), removing the implicit narrowing so the translation becomes
  injective/lossless. If 32-bit is a hard platform constraint, add an explicit,
  checked truncation (assert/token-space guarantee) instead of a silent cast.
- **Callers:** update every producer of the connect token and the token→client-UUID
  derivation to agree on one width (SSOT). Resolve the existing `#warning`/TODO.
- **Docs/tests:** update the connect spec and add a `Round Trip Check` that a
  64-bit token survives the receive→dispatch path unchanged (or is rejected, if
  truncation is mandated).

### R2 — Guard the `TCP_DELIVERY` declarator (`handle_pending_connection`)
- **Change:** keep the explicit `... delivery;` declarator (already present in
  current source). Add a `Static Analysis` / lint gate so the macro's no-declarator
  expansion cannot regress to an empty declaration.
- **Optional hardening (P3):** zero-initialize `delivery` before receive, or
  assert `quantity_received == sizeof(delivery)`, to uphold the buffer's
  `Representation Invariant`.

### R3 — Guard null client (`m_poll_...__server__default`, P4)
- **Change:** after `get_p_client_by__uuid_from__game(...)`, check `p_client != NULL`
  before any dereference. On NULL, skip dispatch for that packet and emit a
  diagnostic (log / `debug_error`) rather than UB. This restores the missing
  `Precondition`/`Postcondition`.
- **Callers:** none required; behavior becomes defined for unknown-UUID sockets.

### R4 — Disambiguate socket-receive error codes (P5)
- **Change:** capture the return value and branch explicitly:
  - `< 0` (e.g. `TCP_ERROR__QUEUE_FULL`) → log backpressure / defer, do not treat as "no data";
  - `== 0` → skip drain;
  - `> 0` → proceed to `get_latest__delivery_from__tcp_socket` drain loop.
- **Consistency:** mirror the same handling in the client-side poller (DRY) so the
  error contract is uniform across server/client.

### R5 — Enforce socket-array bound (P6)
- **Change:** replace the implicit `[0]`/`[1]` assumption with an explicit bound
  check. Either (a) assert `MAX_QUANTITY_OF__TCP_SOCKETS >= 2` at the top of the
  server poll, or (b) drive the loop from an explicit connection count / role
  field rather than fixed indices. Extend the `#ifndef NDEBUG` guard to cover the
  array-width `Boundary Condition`, not just null.

**Phasing:** R3 and R4 are local, low-risk, and can land first (purely defensive).
R1 has the widest blast radius (cross-module type contract) and should be isolated
in its own change with dedicated tests. R5 is a configuration/assertion fix that
should ship before any platform with the default socket count is enabled as a server.

---

## 4. Test Verification Checklist

**Existing suite (`test_suite_multiplayer_server__default.c`):** contains only
`..._symbol_exists` — a symbol-existence check. It asserts **nothing** about the
broken behavior (no coverage of P1–P6). The fix therefore invalidates no existing
assertion, but also means **none of these defects are currently caught**.

**New tests required (all currently missing):**
- **R3 / P4:** inject a socket whose UUID has no registered client; assert the
  poller does not crash and skips dispatch (`Property Based Testing` over
  socket→client mappings; `Fuzzing` of UUID values incl. `IDENTIFIER__UNKNOWN`).
- **R4 / P5:** force a full packet queue and assert the poller surfaces the
  overflow (logged/deferred) rather than silently dropping it; assert the
  `== 0` and `> 0` paths drain correctly (`Equivalence Check` against a reference
  poller).
- **R1 / P1:** `Round Trip Check` — build a `GA_TCP_Connect__Begin` with a
  high-bit-set 64-bit token, run it through `handle_pending_connection`, and assert
  the token reaching `receive_game_action__connect` is lossless (or explicitly
  rejected) (`Property Based Testing` over the full u64 range).
- **R5 / P6:** a `Golden-file Test` / compile-time assertion that a build with the
  default `MAX_QUANTITY_OF__TCP_SOCKETS == 1` cannot reach the `[1]` read (or that
  the assert fires in debug).

**Blast radius of test changes: Low.** The suite is tiny; additions are net-new
and do not modify existing assertions. No phased test migration is needed, but the
R1 round-trip test should land with the R1 type change (not before).

---

## 5. Blast Radius Summary

- **Files changed (implementation):** `server__default.c` (R2, R3, R4, R5);
  `game_action__tcp_connect.h/.c` and its token producers/consumers (R1);
  optionally the client-side poller for R4 consistency; `platform_defaults.h` /
  platform defines only if enforcing a minimum socket count (R5).
- **Behavior-preserving for current callers?** R3, R4, R5 are defensive and
  preserve correct-path behavior. **R1 is not** behavior-preserving — it changes
  the session-token width contract and must be coordinated with all token
  producers/consumers.
- **Phased approach needed?** Yes. Land R3/R4/R5 first (low risk); land R1 as a
  separate, test-gated change due to its cross-module type impact.
- **De-facto contracts invalidated:** the three implicit assumptions listed in the
  Impact Assessment (always-live client; `0`-means-nothing; ≥2 socket slots) are
  all currently *unverified* and become *explicit* after the fix. No externally
  observable contract is broken; the risk is concentrated in R1's type-width change.
