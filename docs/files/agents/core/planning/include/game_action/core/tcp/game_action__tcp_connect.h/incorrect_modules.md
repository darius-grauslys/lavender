# Planning: Incorrect Modules in `game_action__tcp_connect`

## Scope

- **Review file:** `agents/core/review/include/game_action/core/tcp/game_action__tcp_connect.h/incorrect_modules.md`
- **Source files (read-only):**
  - `core/include/game_action/core/tcp/game_action__tcp_connect.h`
  - `core/source/game_action/core/tcp/game_action__tcp_connect.c`
- **Coupled dependencies (read-only):**
  - `core/include/types/core/game_action/tcp/ga_type__tcp__connect.h`
  - `core/include/multiplayer/session_token.h`
  - `core/include/game.h`
  - `core/source/game_action/core/tcp/game_action__tcp_begin_connect.c`
  - `core/source/game_action/core/tcp/test_suite_game_action_core_tcp_game_action__tcp_connect.c`

## 1. Problem Identification

### 1.1 `m_process__game_action__tcp_connect__inbound` (server-side inbound handler)

**File of origin:** `core/source/game_action/core/tcp/game_action__tcp_connect.c`

The function retrieves the session token as an `Identifier__u64` via
`get_session_token_uuid_64_from__ga_tcp_connect` and then performs an implicit
**narrowing conversion** (a **Non-Injective Translation** per the terminology
index) by assigning it directly to `uuid__u32` (`Identifier__u32`):

```c
p_this_process->process_valueB__i32 = 
    uuid__u32 = session_token;
```

This violates the **Type Invariant** that session tokens are 64-bit values
(`session_token__uuid_u64` is `Identifier__u64` in `GA_TCP_Connect`). The
truncation discards the upper 32 bits, producing a **Translation Gap** between
the 64-bit session token space and the 32-bit UUID space. The resulting
`uuid__u32` is then used as the client UUID for all downstream operations in
both states of the process state machine.

The TODO comments on lines 56–57 ("this is to be changed" and "use
authentication result to get user uuid") acknowledge this is a placeholder
that should be replaced with proper authentication-based UUID derivation.

### 1.2 `receive_game_action__connect` (client-side entry point)

**File of origin:** `core/source/game_action/core/tcp/game_action__tcp_connect.c`

The function parameter is declared as `Identifier__u32 session_token`, but the
target field `session_token__uuid_u64` in `GA_TCP_Connect` is `Identifier__u64`.
The code itself acknowledges this defect with a `#warning u32 sess token`
directive and a `// TODO Why is a u32 session token being used here` comment.

The companion function `initialize_game_action_for__tcp_connect` correctly
accepts `Identifier__u64 session_token`, and the `Session_Token` struct (in
`defines.h`) stores both `player_uuid` and `session_token` as `Identifier__u64`.
This parameter type signals an incorrect **API contract**: callers cannot pass
a full 64-bit session token.

While the implicit `u32`-to-`u64` widening does not truncate the value itself,
the type mismatch is a **Surface-form leakage** of the intended 64-bit
contract — the parameter type constrains the representable session token space
to 32 bits.

## 2. Impact Assessment

### 2.1 Downstream reliance on truncated UUID in `m_process__game_action__tcp_connect__inbound`

The truncated `uuid__u32` is consumed by the following calls, all of which
expect `Identifier__u32`:

| Call | Expected type | Coupling concern |
|------|--------------|------------------|
| `get_p_client_by__uuid_from__game(p_game, uuid__u32)` | `Identifier__u32` | Duplicate-client check; a truncated UUID may match the wrong or no client |
| `accept_pending_connection(..., uuid__u32)` | `Identifier__u32` | TCP socket is branded with a truncated UUID |
| `load_client(p_game, uuid__u32)` | `Identifier__u32` | Client load process is enqueued with a truncated UUID |
| `get_p_tcp_socket_for__this_uuid(..., uuid__u32)` (State 1) | `Identifier__u32` | Socket lookup in the second state relies on the same truncated UUID stored in `process_valueB__i32` |
| `get_p_client_by__uuid_from__game(p_game, uuid__u32)` (State 1) | `Identifier__u32` | Client lookup in the second state relies on the stored truncated UUID |

The truncated UUID is persisted across state transitions in
`process_valueB__i32`, coupling the two states to the broken value. Correcting
the narrowing invalidates the assumption that `process_valueB__i32` holds a
valid 32-bit client UUID derived from the session token.

### 2.2 `receive_game_action__connect` parameter type

`receive_game_action__connect` is a public API declared in
`game_action__tcp_connect.h`. Changing its signature from `Identifier__u32` to
`Identifier__u64` **invalidates the calling convention** for all callers.
Currently no internal caller passes a value wider than 32 bits, but the
`Session_Token` struct and `get_uuid_u32_of__session_token_player_uuid_u64`
helper (in `session_token.h`) confirm that the canonical session token is
64-bit, so the `u32` parameter is **de facto** a lossy projection.

### 2.3 `dispatch_game_action__connect` (inline, header) — coupled dependency

The `static inline` function `dispatch_game_action__connect` in
`game_action__tcp_connect.h` shares the same defect:

```c
static inline
void dispatch_game_action__connect(
        Game *p_game,
        Identifier__u32 session_token) {
    Game_Action ga_connect;
    initialize_game_action_for__tcp_connect(
            &ga_connect, 
            session_token);   // u32 → u64 widening (type mismatch)
    dispatch_game_action(
            p_game,
            session_token,     // u32, matches dispatch_game_action's 2nd param
            &ga_connect);
}
```

It passes the `u32` parameter to `initialize_game_action_for__tcp_connect`
(which expects `u64`), creating the same **Type Invariant** violation. The
caller in `game_action__tcp_begin_connect.c` (State `Connected`) passes
`get_uuid_u32_of__session_token_player_uuid_u64(session_token)` — a branded
32-bit projection — rather than the full 64-bit session token.

### 2.4 Test coupling

The test suite at
`core/source/game_action/core/tcp/test_suite_game_action_core_tcp_game_action__tcp_connect.c`
exercises `initialize_game_action_for__tcp_connect` with a full 64-bit value
(`0x12345678ABCDEF00ULL`) and asserts the field retains the full value. This
confirms the **intended type contract**. No test currently exercises
`receive_game_action__connect` or `m_process__game_action__tcp_connect__inbound`
with values exceeding 32 bits, so the truncation defect is **unverified** by
existing tests.

### 2.5 De facto contract

The current `u32`-based API is **de facto** relied upon by
`game_action__tcp_begin_connect.c`, which extracts a branded `u32` from the
session token before calling `dispatch_game_action__connect`. Correcting the
type to `u64` invalidates this extraction step and requires the caller to pass
the full session token (or a separately-resolved `u32` client UUID).

## 3. Resolution Assessment

### 3.1 `receive_game_action__connect`

**What changes:** Change the parameter type from `Identifier__u32` to
`Identifier__u64 session_token` in both the declaration (header) and the
definition (source). Remove the `#warning u32 sess token` directive and the
associated TODO comment.

**Caller impact:** Any caller passing a `u32` literal or variable will require
an explicit widening or a type adjustment. The widening itself is lossless, but
the API signature change is a breaking change.

**Tests/docs:** Update any caller sites; add a test that passes a full 64-bit
session token to `receive_game_action__connect` to verify the value is not
truncated.

### 3.2 `dispatch_game_action__connect` (inline, header)

**What changes:** Change the parameter type from `Identifier__u32` to
`Identifier__u64 session_token`. The call to `initialize_game_action_for__tcp_connect`
becomes type-correct (u64 → u64). The call to `dispatch_game_action` expects a
`Identifier__u32 uuid_of__client__u32` as its second parameter — the session
token (u64) cannot be directly substituted. The resolution must **decouple**
the session token (u64, for the payload) from the client UUID (u32, for
dispatch). Either:

- Accept two parameters (`Identifier__u64 session_token` and
  `Identifier__u32 uuid_of__client__u32`), or
- Derive the client UUID from the session token via
  `get_uuid_u32_of__session_token_player_uuid_u64` inside the inline function.

**Caller impact:** The caller in `game_action__tcp_begin_connect.c` (State
`Connected`) currently passes `get_uuid_u32_of__session_token_player_uuid_u64(session_token)`.
If the inline is changed to accept `Identifier__u64`, the caller must pass the
full session token instead.

**Tests/docs:** Update the caller; verify the game action payload contains the
full 64-bit session token and the dispatch uses the correct 32-bit client UUID.

### 3.3 `m_process__game_action__tcp_connect__inbound`

**What changes:** Replace the implicit narrowing
`p_this_process->process_valueB__i32 = uuid__u32 = session_token` with proper
authentication-based UUID derivation. The TODO comments indicate the intended
flow: authenticate the session token, resolve the player's UUID, and determine
the local server UUID. Until authentication is implemented, the assignment
should at minimum use an explicit, auditable conversion (e.g.,
`get_uuid_u32_of__session_token_player_uuid_u64` applied to the session token)
rather than a raw truncation.

**Caller impact:** None — this is an internal process handler. However,
correcting the UUID derivation invalidates the assumption that
`process_valueB__i32` holds a raw truncation of the session token; downstream
state-1 logic that reads `process_valueB__i32` as the client UUID remains
compatible as long as the derived `u32` is consistent with what
`accept_pending_connection` and `load_client` expect.

**Tests/docs:** Add a test or assertion that verifies the UUID stored in
`process_valueB__i32` is derived consistently from the session token and does
not silently truncate high bits.

### 3.4 Phasing

The `receive_game_action__connect` and `dispatch_game_action__connect` fixes
are a **single type-contract change** (u32 → u64) with a localized blast
radius (one caller in `game_action__tcp_begin_connect.c`). These should be
addressed first as a **Sound (translator)** correction — the type change is
mechanically verifiable.

The `m_process__game_action__tcp_connect__inbound` fix requires implementing
the authentication flow (a larger feature). As an **interim** measure, the
implicit truncation should be replaced with an explicit, documented conversion
using `get_uuid_u32_of__session_token_player_uuid_u64` to make the
**Non-Injective Translation** intentional and auditable, deferring full
authentication-based UUID resolution to a follow-up.
