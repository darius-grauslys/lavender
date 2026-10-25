# Planning: game_action__hitbox.h — Incorrect Modules

**Review source:** `agents/core/review/include/game_action/core/hitbox/game_action__hitbox.h/incorrect_modules.md`

**Source files reviewed (read-only):**
- `core/include/game_action/core/hitbox/game_action__hitbox.h`
- `core/source/game_action/core/hitbox/game_action__hitbox.c`
- `core/include/types/core/game_action/collisions/ga_types__collisions.h`
- `core/include/types/implemented/collisions/hitbox_kind.h`
- `core/include/game_action/game_action_logic_entry.h`
- `core/source/game_action/game_action_logic_entry.c`
- `core/source/client.c` (`dispatch_game_action_for__client`)
- `core/source/game_action/implemented/game_action_registrar.c`
- `tests/core/source/game_action/core/hitbox/test_suite_game_action_core_hitbox_game_action__hitbox.c`

---

## 1. Problem Identification

### 1.1 `register_game_action__hitbox_for__server` — missing `GAME_ACTION_FLAGS__BIT_IS_WITH_PROCESS` (Mode Confusion)

The entry registration sets an outbound process handler (`m_process__game_action__hitbox`)
with `PROCESS_FLAG__IS_CRITICAL`, but omits `GAME_ACTION_FLAGS__BIT_IS_WITH_PROCESS`
from the outbound flags. Every other registration in the codebase — and all three inline
helpers in `game_action_logic_entry.h` (`initialize_game_action_logic_entry_as__process__out`,
`..._as__process__in`, `..._as__process__out_and_in`) — sets `BIT_IS_WITH_PROCESS`
whenever a process handler is present.

Because `santize_game_action__outbound` (in `game_action_logic_entry.c`) copies the
entry's outbound flags onto `p_game_action->game_action_flags`, and
`dispatch_game_action_for__client` (in `core/source/client.c`) branches on
`is_game_action__with_process`, the missing bit silently switches dispatch into the
**ephemeral inline branch**: a stack-allocated `Process` runs the handler synchronously
during dispatch. Consequences:

- No `Game_Action` copy is allocated in the outbound `Game_Action_Manager`.
- The action is not queued through the `Process_Manager`; it executes immediately.
- `PROCESS_FLAG__IS_CRITICAL` is dead data — no dedicated `Process` is ever registered
  with the process manager, so the critical-priority contract is not honored.

This is a **Mode Confusion**: the registration's declared intent (dedicated, critical,
queued process) diverges from the mode the dispatch layer actually selects. The
registration pattern in `game_action_logic_entry.h` is the **Single Source of Truth (SSOT)**
for the flag/handler pairing invariant; this function violates that **Representation Invariant**
(handler non-null ⇒ `BIT_IS_WITH_PROCESS` set), breaking **Don't Repeat Yourself (DRY)**
with its sibling registrations.

Related (not flagged in this review, same defect class): `register_game_action__hitbox_for__client`
omits `BIT_IS_WITH_PROCESS` from the *inbound* flags despite setting an inbound handler,
so the server-side inbound path has the identical Mode Confusion.

### 1.2 `initialize_game_action_for__hitbox` — type-mismatched hitbox-kind accessors (Aliasing Bug)

The `GA_Collisions` payload declares `the_kind_of__hitbox` as `Hitbox_Kind` (an enum),
but the accessors in `ga_types__collisions.h` are declared:

- `Identifier__u32 get_the_kind_of_hitbox_from__game_action...` → returns `Identifier__u32`
- `Identifier__u32 *get_p_the_kind_of_hitbox_from__ga_collisions(...)` → returns `Identifier__u32 *`

`initialize_game_action_for__hitbox` writes a `Hitbox_Kind` through a `uint32_t *`,
and `m_process__game_action__hitbox` reads a `Hitbox_Kind` from a value typed
`Identifier__u32`. This is an **Aliasing Bug** at the type level: the accessor's declared
type does not match the field's actual type, violating the **Type Invariant** of the
payload and risking undefined behavior under strict-aliasing. It is a **Translation Gap**
between the payload's real representation (`Hitbox_Kind`) and its exposed surface form
(`Identifier__u32`).

## 2. Impact Assessment

### 2.1 Who relies on the broken registration behavior

- **`core/source/client.c` — `dispatch_game_action_for__client`:** currently routes
  hitbox actions into the ephemeral inline branch (lines ~360–381). Any caller that has
  adapted to *synchronous* execution of `m_process__game_action__hitbox` is coupled to
  the broken behavior. After the fix, execution becomes *queued* via
  `dispatch_game_action_process__outbound` through the `Process_Manager`.
- **`core/include/game_action/core/hitbox/game_action__hitbox.h` — `register_game_action__hitbox_for__offline`:**
  delegates to the server registration, so offline mode inherits both the defect and the fix.
- **`core/source/game_action/implemented/game_action_registrar.c`:** calls all three
  registrations; no signature changes, but the resulting table contents change.
- **De facto contract (explicitly noted):** hitbox game actions currently execute
  inline and synchronously inside dispatch, *before* the TCP send, with no manager
  allocation. This is not the intended contract (critical queued process) but is the
  observable behavior today. Correcting the flag invalidates this de facto contract:
  - The `Game_Action` will be copied into the outbound `Game_Action_Manager`
    (new allocation/release lifecycle per dispatch).
    `m_process__game_action__hitbox` reads `p_this_process->p_process_data`; in the
    dedicated-process path that pointer is the *allocated copy*, so the handler must
    remain safe when run later, off the dispatch stack. The current handler body is
    already written against `p_this_process`/`p_process_data` and calls
    `complete_process`/`fail_process`, so it is compatible with both modes — no change needed.
  - Ordering: hitbox updates will apply when the process manager runs the queue, not
    mid-dispatch. Callers that poll collision state immediately after dispatch
    (e.g., same-frame `poll_for_collision_node_update` expectations) may observe a one-tick
    deferral.

### 2.2 Who relies on the broken accessor types

- **`core/source/game_action/core/hitbox/game_action__hitbox.c`:**
  - `initialize_game_action_for__hitbox` (write path through `uint32_t *`).
  - `m_process__game_action__hitbox` (read path via `get_the_kind_of_hitbox_from__ga_collisions`,
    implicitly converting `Identifier__u32` → `Hitbox_Kind`).
- No other consumers of these two accessors were found in `core/include`/`core/source`;
  serialization and other payload readers touch `GA_Collisions` fields directly, not via
  these accessors.
- Correcting the accessor return types to `Hitbox_Kind` / `Hitbox_Kind *` is
  source-compatible with all known callers (they already treat the value as `Hitbox_Kind`).
  It invalidates only the assumption that hitbox kind round-trips as a plain `Identifier__u32`.

## 3. Resolution Assessment

### 3.1 Fix `register_game_action__hitbox_for__server`

- In `core/source/game_action/core/hitbox/game_action__hitbox.c`, add
  `GAME_ACTION_FLAGS__BIT_IS_WITH_PROCESS` to the outbound flags argument of the
  `initialize_game_action_logic_entry` call:
  `GAME_ACTION_FLAGS__OUTBOUND_SANITIZE | GAME_ACTION_FLAGS__BIT_IS_WITH_PROCESS | GAME_ACTION_FLAGS__BIT_IS_PROCESSED_ON_INVOCATION_OR_RESPONSE`.
- Keep the flag masks and priorities unchanged; do **not** switch to the
  `initialize_game_action_logic_entry_as__process__out` helper, because that helper also
  forces `GAME_ACTION_FLAGS__BIT_IS_LOCAL`, which would suppress TCP transmission of hitbox
  actions to remote peers — a semantic change beyond the defect.
- Callers: none (signature unchanged). Tests/docs: update registration tests (below).

### 3.2 Related fix: `register_game_action__hitbox_for__client`

- Same one-bit addition to the *inbound* flags, restoring the SSOT invariant on the
  server-side inbound path. Include in the same change; it is the mirror image of 3.1.

### 3.3 Fix hitbox-kind accessors in `ga_types__collisions.h`

- Change return types:
  - `get_the_kind_of_hitbox_from__ga_collisions` → `Hitbox_Kind`
  - `get_p_the_kind_of_hitbox_from__ga_collisions` → `Hitbox_Kind *`
- No caller changes required (callers already use `Hitbox_Kind` semantics).
- Add a **Static Analysis** guard (strict-aliasing / type-mismatch lint gate on the
  `types/core/game_action` accessors) so accessor signatures must match the payload
  field types — preventing recurrence of this Aliasing Bug.

### 3.4 Test verification checklist

Existing suite: `tests/core/source/game_action/core/hitbox/test_suite_game_action_core_hitbox_game_action__hitbox.c`

- **Registration tests** (`register_for_server__populates_table`, `register_for_offline__populates_table`)
  assert only entry non-null and outbound handler non-null. They do **not** assert on flag
  bits, so the fix does not invalidate them — but they also do not catch this defect.
- **Initialization tests** assert payload fields (kind, uuid, position, velocity, acceleration)
  directly; they assert *correct* behavior and remain valid after the accessor type fix.

New tests required:

1. **Equivalence Check** — after `register_game_action__hitbox_for__server`, assert the entry's
   outbound flags equal the reference pattern used by a known-correct registration (e.g.,
   `world__load_world` minus `BIT_IS_LOCAL`), i.e., include `BIT_IS_WITH_PROCESS`.
2. **Property Based Testing** — table-wide invariant: for every registered kind, if the
   outbound (resp. inbound) process handler is non-null, the corresponding flags include
   `BIT_IS_WITH_PROCESS`. This encodes the Representation Invariant and would have flagged
   both hitbox registrations.
3. **Round Trip Check** — `initialize_game_action_for__hitbox` → `santize_game_action__outbound`
   → `is_game_action__with_process(ga)` is true; and the kind read back via
   `get_the_kind_of_hitbox_from__ga_collisions` equals the value passed in (all three
   `Hitbox_Kind` discriminators).
4. **Dispatch-level test** — with a registered table, dispatch a hitbox action through
   `dispatch_game_action_for__client` and assert a dedicated `Process` is allocated in the
   `Process_Manager` with `PROCESS_FLAG__IS_CRITICAL`, and that the outbound
   `Game_Action_Manager` holds the copied action.
5. **Mutation Testing** — run the suite against mutants that drop either flag bit or revert
   an accessor type, to confirm the new tests kill them (guards against silent regression).

**Test blast radius: Low.** No existing assertions are invalidated; changes are additive
plus one flag-bit assertion tightening in the registration tests.

## 4. Blast Radius Summary

- **Files changed:** 3 — `core/source/game_action/core/hitbox/game_action__hitbox.c`
  (two flag bits), `core/include/types/core/game_action/collisions/ga_types__collisions.h`
  (two accessor return types), and the hitbox game-action test file.
- **Behavior-preserving for current callers?** No — by design. Hitbox actions move from
  ephemeral inline execution to dedicated queued critical processes (allocation + deferral).
  This invalidates the de facto synchronous-inline contract; the intended contract per the
  registration pattern and `PROCESS_FLAG__IS_CRITICAL` is restored.
- **Phased approach:** Not required. Both fixes are one-line class changes with no signature
  changes; ship as a single change with the new tests. Verify ordering-sensitive gameplay
  code (same-frame collision polling after dispatch) in integration testing.
