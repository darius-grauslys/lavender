# Planning: multiplayer.h — Incorrect Modules

**Review source:** `agents/core/review/include/multiplayer/multiplayer.h/incorrect_modules.md`

**Source files reviewed (read-only):**
- `core/include/multiplayer/multiplayer.h`
- `core/include/game.h`
- `core/include/defines.h`
- `core/include/defines_weak.h`
- `core/include/multiplayer/session_token.h`
- `core/source/game.c`

---

## 1. Problem Identification

Three functions are declared in `core/include/multiplayer/multiplayer.h` (lines 6–8) but
are all flagged **Incorrect**. Each is analyzed below.

### `is_in_multiplayer_game` (line 6)

```c
bool is_in_multiplayer_game(Game* game);
```

**Defect:** **Translation Gap** — the function is *declared* in `multiplayer.h` but has
**no definition** anywhere in `core/source`, `no_gui`, or `sdl`. Any caller that includes
this header and invokes the function will encounter a **linker error**.

The intended semantic — testing whether the game is in a multiplayer session — is already
served by the `static inline` function `is_game__multiplayer(Game *p_game)` in
`core/include/game.h` (line 353), which returns `p_game->pM_tcp_socket_manager`
(non-null pointer ⇒ allocated TCP socket manager ⇒ in multiplayer). That canonical
implementation is set during `begin_multiplayer_for__game` (game.c:251) and cleared during
`stop_multiplayer_for__game` (game.c:292).

### `is_host` (line 7)

```c
bool is_host(Game* game);
```

**Defect:** **Translation Gap** + **Mode Confusion** — the function is *declared* but has
**no definition** anywhere in the codebase. Furthermore, no `GAME_FLAG__IS_HOST` macro
exists; the only multiplayer-related flag is `GAME_FLAG__IS_SERVER_OR__CLIENT`
(`BIT(0)`, defines.h:2542), which is **Non-Injective** with respect to host/client: it
collapses both the server (host) and client roles into a single bit.

In `begin_multiplayer_for__game` (game.c:251), the host is distinguished by
`p_game->max_quantity_of__clients != 1` (server/host branch) versus `== 1` (client branch),
and the flag is set via `flag_game_as__server` / `flag_game_as__client` (game.c:9–18). There
is no dedicated flag or field to query "is host" after initialization, so the declared
`is_host` predicate has no backing data to read.

### `get_user_id` (line 8)

```c
USER_ID get_user_id(Game* game);
```

**Defect:** **Translation Gap** + **State Desync** — the return type `USER_ID` is **not
defined as a type anywhere** in the codebase (confirmed absent from `defines.h`,
`defines_weak.h`, `platform.h`, `platform_defines.h`, and all multiplayer headers). This
makes the declaration **non-compilable** as written. No implementation exists in any `.c`
file.

The intended semantic — returning the player's identifier from the session token — is already
served by `get_raw_uuid_u32_of__player_from__game_session_token(Game *p_game)` in
`core/include/game.h` (line 314), which delegates to
`get_uuid_u32_of__session_token_player_uuid_u64` (session_token.h) to extract an
`Identifier__u32` from `Game.session_token.player_uuid` (`Identifier__u64`, defines.h:1196).

---

## 2. Impact Assessment

### Current dependency surface

`multiplayer/multiplayer.h` is **not included** by any file in `core`, `no_gui`, `sdl`, or
`tests`. It is not pulled in transitively by `game.h` (which includes only
`multiplayer/session_token.h` and `multiplayer/tcp_socket_manager.h`). Consequently:

- **No in-tree code calls** `is_in_multiplayer_game`, `is_host`, or `get_user_id`.
- **No in-tree code references** the `USER_ID` type.
- **No test file** asserts on any of these three functions or the `USER_ID` type.

### Coupling to the broken behavior

Although nothing currently depends on these declarations, the header is part of the
public API surface for the multiplayer module. If any external consumer were to include
`multiplayer/multiplayer.h`:

| Function | Failure mode |
|---|---|
| `is_in_multiplayer_game` | Linker error (undefined reference) |
| `is_host` | Linker error (undefined reference) |
| `get_user_id` | **Compile error** (`USER_ID` is an undefined type) |

### De facto contracts

The canonical equivalents in `game.h` are the **de facto contracts** that any consumer
should use instead:

- `is_game__multiplayer` (game.h:353) — pure query on `pM_tcp_socket_manager`.
- `is_game__server_or__client` (game.h:425) — reads `game_flags__u32 &
  GAME_FLAG__IS_SERVER_OR__CLIENT`.
- `get_raw_uuid_u32_of__player_from__game_session_token` (game.h:314) — extracts the
  player UUID as `Identifier__u32`.

`game.c` itself uses `p_game->pM_tcp_socket_manager` directly in `poll_multiplayer`
(game.c:614) and in `begin_multiplayer_for__game` / `stop_multiplayer_for__game`. The
`is_game__multiplayer` inline in `game.h` is the existing abstraction over this same check.

### Assumption invalidation

Correcting these declarations (implementing or removing them) does **not** invalidate any
existing caller assumption, because no callers exist. However, if `is_host` were
implemented by reusing `GAME_FLAG__IS_SERVER_OR__CLIENT`, it would introduce a **Mode
Confusion** bug: that flag is set for *both* server and client, so `is_host` would return
`true` for a client instance — violating the `Postcondition` that it "Returns true if the
game instance is the host."

---

## 3. Resolution Assessment

### Option A (preferred): Remove the three declarations and consolidate on `game.h`

Per **Single Source of Truth (SSOT)** and **Don't Repeat Yourself (DRY)**, the multiplayer
query predicates and accessors already live in `game.h` as `static inline` functions. The
declarations in `multiplayer.h` are redundant duplicates with no implementation.

**Steps:**

1. **`is_in_multiplayer_game`** — Remove the declaration from `multiplayer.h`. Direct all
   callers to `is_game__multiplayer(Game *p_game)` in `game.h`. No caller updates needed
   (no callers exist).

2. **`is_host`** — Remove the declaration from `multiplayer.h`. The host determination
   already occurs in `begin_multiplayer_for__game` (game.c:251) via the
   `max_quantity_of__clients != 1` branch and `flag_game_as__server`. If a queryable
   "is host" predicate is needed in the future, introduce a dedicated `GAME_FLAG__IS_HOST`
   and set it in `begin_multiplayer_for__game`. For now, removal eliminates the
   **Mode Confusion** risk.

3. **`get_user_id`** — Remove the declaration from `multiplayer.h`. The `USER_ID` type
   does not exist; the canonical accessor
   `get_raw_uuid_u32_of__player_from__game_session_token` in `game.h` already returns the
   player identifier as `Identifier__u32`. No caller updates needed.

**Caller impact:** None — no in-tree code includes `multiplayer.h` or calls these functions.

**Test impact:** None — no tests reference these functions.

### Option B (if the functions must be retained as a public multiplayer API)

If the intent is to expose a dedicated multiplayer query API in `multiplayer.h` rather
than relying on `game.h`, the following must happen:

1. **`is_in_multiplayer_game`** — Add a `static inline` definition in `multiplayer.h`
   mirroring `is_game__multiplayer`:
   ```c
   static inline
   bool is_in_multiplayer_game(Game* game) {
       return game->pM_tcp_socket_manager;
   }
   ```
   This satisfies the `Postcondition` (returns `true` when `pM_tcp_socket_manager` is
   non-null) and the `Precondition` (`game` non-null). **Information Hiding** concern:
   this duplicates the logic already in `game.h`; consider delegating instead.

2. **`is_host`** — Introduce `GAME_FLAG__IS_HOST` (e.g., `BIT(1)` in defines.h) and set
   it in `begin_multiplayer_for__game` during the server branch. Then implement:
   ```c
   static inline
   bool is_host(Game* game) {
       return game->game_flags__u32 & GAME_FLAG__IS_HOST;
   }
   ```
   This avoids the **Non-Injective Translation** of reusing
   `GAME_FLAG__IS_SERVER_OR__CLIENT`.

3. **`get_user_id`** — Define `USER_ID` as a typedef (e.g.,
   `typedef Identifier__u32 USER_ID;` in `defines.h` / `defines_weak.h`) and implement:
   ```c
   static inline
   USER_ID get_user_id(Game* game) {
       return get_raw_uuid_u32_of__player_from__game_session_token(game);
   }
   ```
   This reuses the existing extraction logic, satisfying **DRY**.

**Caller impact:** None (no callers exist).

**Test impact:** New tests would be needed — see §4.

---

## 4. Test Verification Checklist

**Existing test survey:** No test file in `./tests/` references `is_in_multiplayer_game`,
`is_host`, `get_user_id`, or the `USER_ID` type (confirmed across
`tests/core/source/multiplayer/`, `tests/core/source/test_suite_game.c`, and
`tests/test_suite_game.c`).

**Blast radius for tests:** **Low** — no existing assertions would be invalidated because
no tests exercise these functions.

**New test recommendations (if Option B is chosen):**

| Function | Recommended technique | Rationale |
|---|---|---|
| `is_in_multiplayer_game` | **Round Trip Check** + **Property Based Testing** | Verify `is_in_multiplayer_game` returns `false` after `initialize_game`, `true` after `begin_multiplayer_for__game`, and `false` after `stop_multiplayer_for__game`. |
| `is_host` | **Property Based Testing** | Verify `is_host` returns `true` only for the server instance (where `max_quantity_of__clients != 1`) and `false` for the client instance. |
| `get_user_id` | **Equivalence Check** | Verify `get_user_id(game)` returns the same value as `get_raw_uuid_u32_of__player_from__game_session_token(game)` — **Differential Testing** against the canonical implementation. |

**Mutation Testing** should be applied to any new implementation to confirm the test
suite catches injected faults (e.g., flipping the return value, removing the flag check).

---

## 5. Blast Radius Summary

| Metric | Assessment |
|---|---|
| Files needing change | 1 (`core/include/multiplayer/multiplayer.h`) — or 2–3 if Option B (also `defines.h`/`defines_weak.h` for `USER_ID` / `GAME_FLAG__IS_HOST`) |
| Behavior-preserving for current callers | Yes — no callers exist |
| De facto contracts invalidated | None — the canonical functions in `game.h` remain the source of truth |
| Phased approach needed | No — the change is isolated to a single header with zero in-tree consumers |

**Recommendation:** Adopt **Option A** (remove the three declarations). The functions are
dead declarations with no implementation, no callers, and no tests. The canonical
equivalents in `game.h` already fulfill the same semantic intent. This eliminates the
**Translation Gap**, the **Mode Confusion** around host vs. server-or-client, and the
**State Desync** of the undefined `USER_ID` type, all while adhering to **SSOT** and
**DRY**. If a dedicated multiplayer query API is desired in the future, it should be
implemented *against* the existing `game.h` primitives rather than as parallel declarations.
