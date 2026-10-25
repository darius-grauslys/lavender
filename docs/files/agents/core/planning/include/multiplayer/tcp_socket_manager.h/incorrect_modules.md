# Planning: tcp_socket_manager.h — Incorrect Modules

**Review source:** `agents/core/review/include/multiplayer/tcp_socket_manager.h/incorrect_modules.md`

**Source files reviewed (read-only):**
- `core/include/multiplayer/tcp_socket_manager.h`
- `core/source/multiplayer/tcp_socket_manager.c`
- `core/source/multiplayer/tcp_socket.c` (shared callee `initialize_tcp_socket`)
- `core/source/multiplayer/server__default.c` (primary coupled caller)
- `tests/core/source/multiplayer/test_suite_multiplayer_tcp_socket_manager.c`

---

## 1. Problem Identification

Seven functions in the `TCP_Socket_Manager` were flagged **Incorrect**. Each violates a
stated Precondition/Postcondition or its semantic intent. One shared root cause in a
sibling module (`tcp_socket.c`) amplifies three of them.

| Function | Core defect | Terminology |
|----------|-------------|-------------|
| `initialize_tcp_socket_manager` | Leaves `p_PLATFORM_tcp_context` and `ipv4__pending_connection` indeterminate; struct is not fully reset to initial conditions. | **Representation Invariant** / **State Desync** |
| `accept_socket_on__tcp_socket_manager__ipv4` | No null check after `allocate_tcp_socket_from__tcp_socket_manager`; null deref when the pool is exhausted. | **Boundary Condition** / undefined behavior |
| `open_socket_on__tcp_socket_manager__ipv4` | (a) Same missing null check → null deref; (b) platform socket leaked on allocation failure; (c) triggers the shared `initialize_tcp_socket` overflow below. | **Boundary Condition** / resource leak |
| `open_server_socket_on__tcp_socket_manager__ipv4` | Missing null check after allocation; skips `initialize_tcp_socket` (TODO), leaving `packet_size__entries`, `tcp_socket__state_of`, `tcp_socket_flags__u8` as garbage. | **Stub-real divergence** / **Representation Invariant** |
| `close_socket_on__tcp_socket_manager__ipv4` | Uninitialized `p_ptr_tcp_socket__being_release` / `p_ptr_tcp_socket__last` → undefined behavior when the socket is not found or the pool is empty; unconditional `quantity_of__connections--` underflows on a no-op; relies on a fragile "compact array" loop break. | **Representation Invariant** / **State Desync** / **Conservation Law** |
| `poll_tcp_socket_manager_for__pending_connections` | Max-connections guard runs *before* the cached-pending check, so a cached pending connection becomes unreachable at capacity (stuck state); also writes stale `*p_ipv4` when no new connection is found. | **State Desync** / **Boundary Condition** |
| `reject_pending_connection` | No null guard on `p_PLATFORM_tcp_socket__pending_connection` before crossing the platform boundary → null deref; discards the error return of `PLATFORM_tcp_close_socket`. | **Precondition** / undefined behavior |

**Shared root cause (cross-module):** `initialize_tcp_socket` in
`core/source/multiplayer/tcp_socket.c` (lines 46–48) performs
`memset(&p_tcp_socket->queue_of__tcp_packet, 0, sizeof(TCP_Socket))`. Because
`queue_of__tcp_packet` is not at offset 0 (it follows `_serialization_header`), this
writes `sizeof(Serialization_Header)` bytes past the end of the struct — a **buffer
overflow** that corrupts adjacent slots in the `tcp_sockets` array. It fires on every
call, i.e. from both `accept_socket…` and `open_socket…`. This is a
**Representation Invariant** violation with a large blast radius and must be fixed as
part of this plan even though it lives outside the reviewed file.

---

## 2. Impact Assessment

**Coupled callers and de facto contracts:**

- `server__default.c::m_poll_tcp_socket_manager_as__server__default` is the primary
  consumer. It **hard-codes** `ptr_array_of__tcp_sockets[0]` as the server socket and
  `[1]` as the auth socket, and iterates the pointer array with a loop that **breaks on
  the first null entry**. This is a de facto contract coupled to the *compact-array*
  **Representation Invariant** (all non-null slots precede all null slots). Any change
  to how `allocate…`/`close…` maintain that array must preserve slot-index stability and
  compactness, or these hard-coded indices and the iteration loop silently break.
- `client__default.c` consumes the manager through `m_poll_tcp_socket_manager`; it is
  subject to the same coupling via `poll_tcp_socket_manager_for__pending_connections`.
- `game.c` (`begin_multiplayer_for__game`) assigns `p_PLATFORM_tcp_context` *after*
  calling `initialize_tcp_socket_manager`. The init bug is therefore currently **masked
  by caller ordering** — a de facto contract that "the caller fills the context." Zeroing
  the field in init is defensive and behavior-preserving for this caller.
- `accept_pending_connection` (same file) calls `accept_socket…` and checks its return
  for null. Today that check is too late (crash happens inside `accept_socket…`). Fixing
  the null check turns a crash into a clean `0` return; the existing caller check then
  becomes meaningful rather than dead.

**Assumptions invalidated by the fixes:**

- Correcting `close_socket…` to guard against an unfound/empty pool changes its
  **Postcondition**: `quantity_of__connections` will only decrement when a removal
  actually occurs (**Conservation Law**). Any caller that today relies on the counter
  decrementing unconditionally (e.g., to compensate for the underflow) is coupled to the
  broken behavior and must be re-examined.
- Fixing `poll…` to return a cached pending connection even at capacity changes its
  observable behavior: callers that inferred "no pending connection" from a `NULL` return
  at capacity will now start receiving one. This is the intended correction, not a
  regression, but it must be validated against `server__default.c`'s accept/reject flow.
- Fixing the shared `initialize_tcp_socket` overflow changes memory writes for every
  socket init; it is behavior-preserving for correct in-bounds use but repairs silent
  corruption of neighboring slots today.

**Files likely touched:** `tcp_socket_manager.c` (all seven functions),
`tcp_socket.c` (`initialize_tcp_socket` memset), and possibly the coupled callers if the
compaction scheme changes (preferred: keep the scheme, only make it robust).

---

## 3. Resolution Assessment

Order matters: fix the shared overflow first so that re-enabling
`initialize_tcp_socket` in `open_server_socket…` is safe.

1. **`initialize_tcp_socket` (tcp_socket.c) — shared root cause.** Replace
   `memset(&p_tcp_socket->queue_of__tcp_packet, 0, sizeof(TCP_Socket))` with a zero-fill
   of the queue's actual size (`sizeof(p_tcp_socket->queue_of__tcp_packet)`). This removes
   the out-of-bounds write. Callers (`accept_socket…`, `open_socket…`) need no change for
   this step.

2. **`initialize_tcp_socket_manager`.** Also zero `p_PLATFORM_tcp_context = 0` and
   `ipv4__pending_connection`. Restores the "reset to initial conditions" semantic and
   clears the latent stale-data risk on re-init. Behavior-preserving for `game.c`
   (which re-assigns the context afterward).

3. **`accept_socket_on__tcp_socket_manager__ipv4`.** After allocation, `if (!p_tcp_socket)
   return 0;` before `initialize_tcp_socket`. No caller change; `accept_pending_connection`
   already handles the null return.

4. **`open_socket_on__tcp_socket_manager__ipv4`.** Add the same null check after
   allocation; on allocation failure, release the already-created platform socket via
   `PLATFORM_tcp_close_socket` before returning `0` (closes the resource leak).

5. **`open_server_socket_on__tcp_socket_manager__ipv4`.** Add the null check after
   allocation; delete the TODO manual-init block and call `initialize_tcp_socket(...)`
   (safe after step 1), so `packet_size__entries`, `tcp_socket__state_of`, and
   `tcp_socket_flags__u8` are all set. This removes the **Stub-real divergence** with its
   two sibling functions (**DRY**).

6. **`close_socket_on__tcp_socket_manager__ipv4`.** Initialize both local pointers to
   `NULL`; after the scan, perform the swap-with-tail compaction and the counter decrement
   **only if** `p_ptr_tcp_socket__being_release` was found. This eliminates the undefined
   behavior, fixes the unsigned underflow (**Conservation Law**), and keeps the compact-array
   **Representation Invariant** intact for `server__default.c`. Optionally adopt the
   entity-manager's maintained end-cursor pattern to drop the fragile first-null break — but
   only if it provably preserves slot-index stability for the hard-coded `[0]`/`[1]` reads.

7. **`poll_tcp_socket_manager_for__pending_connections`.** Reorder: return a cached pending
   connection **first**, then apply the max-connections guard only before issuing a new
   `PLATFORM_tcp_poll_accept`. Also stop writing `*p_ipv4` when the poll finds no new
   connection (guard on a non-null result). Fixes the stuck-pending **State Desync**.

8. **`reject_pending_connection`.** Guard: only call `PLATFORM_tcp_close_socket` when
   `p_PLATFORM_tcp_socket__pending_connection` is non-null; capture and log its error return
   instead of discarding it.

**Phasing:** All edits are localized to two `.c` files and are individually behavior-safe.
A single pass is acceptable, but the shared overflow (step 1) must land before step 5 is
enabled. No header signature changes are required, so the public surface is stable.

---

## 4. Test Verification Checklist

Existing suite (`tests/core/source/multiplayer/test_suite_multiplayer_tcp_socket_manager.c`)
covers **only** `initialize_tcp_socket_manager` with five stateless tests asserting correct
post-conditions (`quantity_of_connections_is_zero`, `sets_poll_callback`,
`all_sockets_are_deallocated`, `pending_connection_is_null`, `null_callback__sets_null`).
These assert **correct** behavior and are not invalidated by the plan. No existing test
covers the other six flagged functions.

Gaps to close (recommendations use testing terminology):

- **`initialize_tcp_socket_manager`:** add an assertion that `p_PLATFORM_tcp_context == 0`
  and `ipv4__pending_connection` is zeroed after init (currently untested → the bug is
  invisible today). The stack-declared, un-zeroed `manager` in existing tests makes this a
  clean **Equivalence Check** against a fully-defaulted struct.
- **`close_socket…`:** **Property Based Testing** of the invariant
  `quantity_of__connections == (count of non-null ptr_array slots)` across randomized
  allocate/close sequences; explicitly test the previously-UB cases: closing a socket not in
  the pool, and closing when the pool is empty (must be a no-op, counter unchanged).
- **`accept_socket…` / `open_socket…`:** boundary test that exhausting the pool returns `0`
  with no crash (previously null deref); for `open_socket…`, assert the platform socket is
  closed on allocation failure (**Round Trip Check** of resource acquire/release).
- **`open_server_socket…`:** assert all nine `TCP_Socket` fields are set (no indeterminate
  state) — a **Representation Invariant** check.
- **`poll…`:** test that a cached pending connection is returned even when the active count
  is at `MAX_QUANTITY_OF__TCP_SOCKETS`; test that `*p_ipv4` is untouched when no new
  connection is found.
- **`reject_pending_connection`:** test the no-pending (null) path does not call the platform
  close and does not crash; verify the error return is surfaced.
- **`initialize_tcp_socket` overflow:** a **Fuzzing**/heap-checker (ASan) run over init to
  confirm the out-of-bounds write is gone; this is the highest-value verification.

**Blast radius: Medium.** Two source files change; public signatures are unchanged, so
changes are behavior-preserving for correctly-behaving callers. The de facto contracts that
would be *restored* (not broken) are the compact-array invariant and the init-to-defaults
contract. A phased approach is only needed to sequence step 1 before step 5; test updates
can land alongside the code changes without a separate phase.
