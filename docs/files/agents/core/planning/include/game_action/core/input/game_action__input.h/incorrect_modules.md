# Planning: game_action__input.h — Incorrect Modules

**Review source:** `agents/core/review/include/game_action/core/input/game_action__input.h/incorrect_modules.md`

**Source files reviewed (read-only):**
- `core/include/game_action/core/input/game_action__input.h`
- `core/source/game_action/core/input/game_action__input.c`
- `core/include/types/core/game_action/input/ga_type__input.h`
- `core/include/types/core/game_action/input/ga_types__input.h`
- `core/include/game_action/game_action.h`
- `core/include/input/input.h`
- `core/include/client.h`
- `tests/core/source/game_action/core/input/test_suite_game_action_core_input_game_action__input.c`

**Flagged entry:**
- `./initialize_game_action_for__input.md` — **Correctness Verdict: Incorrect**

---

## 1. Problem Identification

The single flagged unit is `initialize_game_action_for__input(Game_Action*, Input*)`
(`core/source/game_action/core/input/game_action__input.c`, lines 78–102). Its intent is to
zero a `Game_Action`, stamp its kind to `Game_Action_Kind__Input`, and copy client input into
the payload. The `#else` branch does this correctly via a whole-struct copy through the
`get_p_input_from__game_action` accessor. The `#ifdef SECURITY_0` branch (lines 85–97) is
defective in two independent ways:

- **Defect A — Surface-form leakage / Translation Gap.** Lines 90–96 reference the member
  `p_game_action->ga_kind__input__input`. No such member exists. The macro-generated
  `Game_Action` payload is reached only through the generated accessor
  `get_p_input_from__game_action(p_game_action)` (which resolves to
  `GA_Input__Payload.input` past `_Game_Action_Header`) or the union path
  `_ga_payload_union.GA_Input.GA_Input__Payload.input`. The hand-written path
  `ga_kind__input__input` is a surface form the generator never emits, so the
  `SECURITY_0` configuration does not compile.

- **Defect B — Aliasing Bug / Non-Injective Translation.** All four assignments (lines
  90–97) write to the *same* destination field `input_flags__held`. The second, third, and
  fourth should target `input_flags__pressed`, `input_flags__pressed_old`, and
  `input_flags__released` respectively. As written the mapping from four distinct source
  fields to one destination is non-injective: only the last write (`released`) survives in
  `held`, and `pressed` / `pressed_old` / `released` remain zeroed from the
  `initialize_game_action` memset. This violates Postcondition 3 (flag fields populated from
  `p_input`) and defeats the purpose of the SECURITY_0 flag-relay path.

Both defects are confined to the `SECURITY_0` branch; the `#else` branch and the header
declarations are correct.

---

## 2. Impact Assessment

**Build coupling (hard blocker).** Defect A is a compile-time error, so any build configured
with `SECURITY_0` fails outright. Correcting Defect A is a precondition for that configuration
to exist at all; there are no downstream callers in the broken state because the code does not
build.

**Server-side consumer relies on whole-struct payload semantics.** The registered server
handler `m_process__game_action__input__inbound_server` reads the payload through the same
`get_p_input_from__game_action` accessor and forwards it to
`copy_input_into__client`, which performs a *whole-struct* copy
(`p_client->input_of__client = *p_input`). This is the de facto contract: the server assumes
the inbound payload carries a complete `Input`, including cursor fields.

- Under `SECURITY_0`, the intent (per the in-code comment) is to relay only flags and omit
  cursor positions so the client window size is not leaked. Because `GA_Input__Payload` embeds
  a full `Input`, the payload structurally still contains cursor fields; after a correct
  per-field flag copy they remain zeroed. The whole-struct `copy_input_into__client` would then
  overwrite the server-side client's cursor with zeros every input frame — a **State Desync**
  between the real client cursor and the server's mirror of it. Correcting Defects A/B does not
  by itself resolve this; it merely makes the flag relay correct while leaving the cursor
  clobbering intact.

**Sanitization SSOT / Coupling.** The server logic entry registers
`GAME_ACTION_FLAGS__OUTBOUND_SANITIZE` and `GAME_ACTION_FLAGS__INBOUND_SANITIZE`. That
registered sanitization is the intended **Single Source of Truth** for what crosses the wire.
The manual per-field copy inside `SECURITY_0` is a second, competing sanitization point — a
**DRY** / **Coupled** violation and the likely origin of the hand-written (broken) path. If the
serialization layer already strips cursor fields at the boundary, the manual copy is redundant
and should be removed rather than repaired in place.

**Non-security callers unaffected.** The `#else` wholesale-copy path and all callers of
`initialize_game_action_for__input` / `dispatch_game_action__input` in the default build depend
on the current (correct) behavior; any fix must remain **behavior-preserving** (Equivalence
Check) for that configuration.

---

## 3. Resolution Assessment

### Phase 1 — Restore a compilable, correct `SECURITY_0` flag relay (fixes Defects A & B)

In the `#ifdef SECURITY_0` branch of `initialize_game_action_for__input`:

1. **Fix the accessor (Defect A).** Replace every
   `p_game_action->ga_kind__input__input` with the generated accessor
   `get_p_input_from__game_action(p_game_action)` (returns `Input *`). This reuses the exact
   accessor already used by the `#else` branch and by the server handler, keeping payload
   access at a single point (**SSOT**) and eliminating the leaked surface form. A local pointer
   (`Input *p_payload = get_p_input_from__game_action(p_game_action);`) keeps the block readable.
2. **Fix the field mapping (Defect B).** Assign each source field to its distinct destination:
   - `p_payload->input_flags__held        = p_input->input_flags__held;`
   - `p_payload->input_flags__pressed     = p_input->input_flags__pressed;`
   - `p_payload->input_flags__pressed_old = p_input->input_flags__pressed_old;`
   - `p_payload->input_flags__released    = p_input->input_flags__released;`
3. Leave the `#else` branch untouched so the default build is **behavior-preserving**.

Callers: no caller changes required for Phase 1 (the function signature and kind stamping are
unchanged). This phase makes `SECURITY_0` compile and satisfies Postcondition 3.

### Phase 2 — Reconcile cursor sanitization with the whole-struct consumer (removes State Desync)

Determine where cursor stripping is supposed to happen, then enforce it at exactly one point:

- **Preferred (Option B):** Route cursor omission through the registered
  `OUTBOUND_SANITIZE`/`INBOUND_SANITIZE` mechanism in the serialization layer so the wire
  format never carries cursor positions, and let the server-side consumer tolerate an
  intentionally-omitted cursor (e.g., `copy_input_into__client` copies flags but preserves the
  server's existing cursor, or a SECURITY_0-aware variant). Then **delete** the manual per-field
  copy in `SECURITY_0` and fall back to the shared wholesale path — restoring a single
  sanitization **SSOT** and removing the **Coupled**/DRY duplication that produced the bug.
- **Fallback (Option A):** If sanitization must stay in this function, keep the Phase-1
  per-field flag copy, explicitly zero (or leave zeroed) the cursor fields, and confirm with the
  server owner that clobbering the server-side client cursor to zero each frame is acceptable.

This phase may touch `core/include/client.h` (`copy_input_into__client`) or the serialization
layer; scope it after confirming where sanitization currently lives.

### Phase 3 — Tests and documentation

- Implement the currently-stubbed tests (see §4).
- Update/author the spec at
  `docs/specs/core/game_action/input/game_action__input.h.spec.md` (referenced by the test file
  but not present) so Section 1.4.2 documents both build configurations and the cursor policy.

---

## 4. Test Verification Checklist

**Existing tests.** The suite
`tests/core/source/game_action/core/input/test_suite_game_action_core_input_game_action__input.c`
contains five `TEST`s, all stubbed with `FAIL("Not implemented")`, including
`initialize_game_action_for__input`. No test asserts on the broken behavior, so the fix
**invalidates no existing assertion** (nothing to preserve). Coverage is currently zero.

**New tests required:**

- **Compile / Lint Gate.** A `SECURITY_0` build of this translation unit must compile. This is
  the minimal gate proving Defect A is resolved (today it cannot build).
- **Round Trip Check (per configuration).** Populate an `Input` with distinct values in
  `held` / `pressed` / `pressed_old` / `released`; call
  `initialize_game_action_for__input`; read back via
  `get_p_input_from__game_action`; assert each flag field round-trips to its own value (no
  cross-field aliasing). Run for both the default and `SECURITY_0` builds.
- **Property Based Testing.** For randomized flag bit-fields, assert Postcondition 3 holds
  field-by-field under `SECURITY_0` (each source field maps injectively to its destination),
  guarding against regression of the Aliasing Bug.
- **Equivalence Check.** Assert the default-build wholesale copy and the `SECURITY_0` flag copy
  produce identical flag fields, and that cursor handling matches the chosen Phase-2 policy
  (omitted/zeroed vs preserved).
- **Boundary Condition / Fuzzing.** Edge flag values (`INPUT_NONE`, all-bits set) to confirm no
  field is dropped and no out-of-range write occurs.

**Test blast radius: Medium.** All five stubs need real bodies, and a `SECURITY_0` build target
must be added to exercise the secure path. A phased rollout (Phase 1 tests first, then Phase 2
cursor-policy tests) is advisable.

---

## 5. Blast Radius Summary

- **Files changed:** 1 for the core fix (`core/source/game_action/core/input/game_action__input.c`).
  Possibly `core/include/client.h` and/or the serialization layer in Phase 2 if cursor sanitization
  is relocated to its SSOT. One test file gains real coverage.
- **Behavior-preserving for current callers:** Yes for the default (non-`SECURITY_0`) build — the
  `#else` path is untouched. For `SECURITY_0`, there is no prior working behavior to preserve; the
  fix *restores* intended behavior (flags relayed, cursor policy defined).
- **De facto contract invalidated:** The server handler's reliance on a complete `Input` in the
  payload (via whole-struct `copy_input_into__client`) is intentionally narrowed under
  `SECURITY_0`. This must be reconciled in Phase 2, not silently accepted, to avoid a State Desync
  on the server-side client cursor.
- **Phased approach needed:** Yes — Phase 1 (compile + correct flag mapping, low risk), Phase 2
  (cursor sanitization SSOT, moderate risk), Phase 3 (tests + spec). Each phase is independently
  verifiable via the gates in §4.
