# Planning: game_action__entity__get.h — Incorrect Modules

**Review source:** `agents/core/review/include/game_action/core/entity/game_action__entity__get.h/incorrect_modules.md`

**Source files reviewed (read-only):**
- `core/include/game_action/core/entity/game_action__entity__get.h`
- `core/source/game_action/core/entity/game_action__entity__get.c`
- `core/include/game_action/game_action_logic_entry.h` (helper flag patterns)
- `core/include/game_action/game_action.h` (`is_game_action__with_process`)
- `core/source/game_action/implemented/game_action_registrar.c` (call-site wiring)
- `tests/core/source/game_action/core/entity/test_suite_game_action_core_entity_game_action__entity__get.c`

---

## 1. Problem Identification

Flagged entry: `register_game_action__entity__get_for__client`
(`core/source/game_action/core/entity/game_action__entity__get.c:183-200`).

**Defect — Mode Confusion / State Desync between flag fields and process-pointer fields.**
The client registration hand-writes a raw `initialize_game_action_logic_entry(...)` call whose
flag arguments are decoupled from its process arguments:

- **Outbound** carries a real process (`m_process__game_action__entity__get__outbound_client__init`)
  but its flags are the plain `GAME_ACTION_FLAGS__OUTBOUND_SANITIZE` — **missing**
  `BIT_IS_WITH_PROCESS | BIT_IS_PROCESSED_ON_INVOCATION_OR_RESPONSE`.
- **Inbound** carries a NULL process (`0`) but its flags *do* carry
  `BIT_IS_WITH_PROCESS | BIT_IS_PROCESSED_ON_INVOCATION_OR_RESPONSE`.

The flag bits and the process pointers therefore point to opposite directions — a
Representation Invariant violation (a `BIT_IS_WITH_PROCESS` bit must co-occur with a non-NULL
process in the same direction). The server registration
(`register_game_action__entity__get_for__server`, lines 164-181) is the mirror image and is correct:
it places the process bits on **inbound** (where its process lives) and leaves outbound plain.

Consequences once the entry is exercised:
- An inbound `Entity__Get` response gets `BIT_IS_WITH_PROCESS` stamped during sanitize, so
  `is_game_action__with_process` (`game_action.h:91`) returns true; dispatch retrieves the NULL
  inbound process and fails (`m_process__game_action == 0`).
- The outbound process is never dispatched, because outbound lacks the process bit.

## 2. Impact Assessment

**Callers / wiring:**
- `register_game_action__entity__get_for__client` is **not** currently invoked from
  `register_game_actions__client` (`game_action_registrar.c`) — that function registers only
  `bad_request`, the `tcp_*` family, `global_space_*`, `hitbox_for__client`, and
  `input_for__client`. The broken entry is therefore **latent** in the live client logic table;
  no de facto contract depends on it yet.
- The only active caller is the test suite
  (`test_suite_..._game_action__entity__get.c:73`), which asserts only that the entry pointer is
  non-null. It does **not** assert flag/process placement, so it passes despite the defect.

**Assumptions coupled to the broken behavior:**
- The dispatch path in `game_action.c`/`game_action.h` keys off the runtime action flags stamped
  from the entry flags during sanitize (`is_game_action__with_process`,
  `is_game_action__processed_on__invocation_or__respose`). Any consumer that assumes
  "process bit ⇔ non-NULL process, same direction" is coupled to the correct (currently violated)
  invariant. Fixing the registration restores that invariant; no consumer currently relies on the
  swapped state, so correction **invalidates no live assumption** — it only removes a latent fault.

**Cascading changes:** none in `./include`/`./source` beyond the registration function itself.
The helper `initialize_game_action_logic_entry_as__process__out`
(`game_action_logic_entry.h:52`) already encodes the exact correct layout, so the fix is local.

## 3. Resolution Assessment

**Goal:** make the client entry's flags a faithful reflection of its process placement — outbound
process present + process bits on outbound; inbound plain, no process.

Preferred change (SSOT / DRY):
- Replace the raw `initialize_game_action_logic_entry(...)` call in
  `register_game_action__entity__get_for__client` with the existing helper
  `initialize_game_action_logic_entry_as__process__out(
        entry, PROCESS_PRIORITY__0_MAXIMUM,
        m_process__game_action__entity__get__outbound_client__init, PROCESS_FLAGS__NONE)`.
- This single call yields exactly the intended layout:
  - Outbound flags = `OUTBOUND_SANITIZE | BIT_IS_WITH_PROCESS | BIT_IS_PROCESSED_ON_INVOCATION_OR_RESPONSE`
  - Inbound flags = `INBOUND_SANITIZE` (plain)
  - Outbound process = `m_process__game_action__entity__get__outbound_client__init`, inbound process = `0`.
- Rationale: the helper is the Single Source of Truth for the "process-out" pattern, so the
  flag/process pairing can no longer drift (removes the Mode Confusion root cause).

Minimal alternative (if helper reuse is undesired): swap the two flag literals in the raw call —
move `BIT_IS_WITH_PROCESS | BIT_IS_PROCESSED_ON_INVOCATION_OR_RESPONSE` from the inbound argument
to the outbound argument, and set inbound to plain `GAME_ACTION_FLAGS__INBOUND_SANITIZE`.

**Callers:** none need updating (no live client wiring; signature unchanged).
**Docs:** update the spec section `1.4.1. Registration` for the client case to state the
process-out flag contract explicitly.

### Test Verification Checklist
- **Existing tests:** `register_for_client__populates_table` asserts only non-null entry → does not
  catch this defect; it will still pass after the fix (no assertion invalidated).
- **New assertions (Equivalence Check + Representation Invariant):** in the client registration
  test, assert outbound flags contain both process bits, `get_m_process__outbound...` ==
  `m_process__game_action__entity__get__outbound_client__init`, inbound process == `0`, and inbound
  flags == plain `INBOUND_SANITIZE`. Optionally assert equivalence with the output of
  `initialize_game_action_logic_entry_as__process__out` (Equivalence Check against the SSOT helper).
- **New dispatch test (Round Trip Check, if infra permits):** register the client entry, feed an
  outbound invocation and an inbound response through the dispatch path, and assert the outbound
  process runs while no spurious inbound dispatch occurs.
- **Strategy:** `Property Based Testing` for the "bit ⇔ non-NULL process" invariant across both
  directions; `Equivalence Check` against the helper.

## 4. Blast Radius Summary
- **Files changed:** 1 source (`game_action__entity__get.c`) + 1 test file (add assertions). Optional
  spec note.
- **Behavior-preserving for current callers:** yes — no live client registration consumes the entry,
  and the test suite asserts only non-null (still satisfied).
- **Phased approach:** not required (single-function, low blast radius).
- **De-facto contracts invalidated:** none; the fix only removes a latent fault.
