# Planning: tcp_game_action_process.h — Incorrect Modules

**Review source:** `agents/core/review/include/process/tcp_game_action_process.h/incorrect_modules.md`

**Source files reviewed (read-only):**
- `core/include/process/tcp_game_action_process.h`
- `core/source/process/tcp_game_action_process.c`
- `core/include/serialization/serialization_request.h` (callees: `activate_serialization_request`, `set_serialization_request_as__tcp`)
- `tests/core/source/process/test_suite_process_tcp_game_action_process.c`
- `tests/core/include/process/test_suite_process_tcp_game_action_process.h`

**Flagged (Incorrect):**
- `set_game_action_process_as__tcp_payload_receiver` (defined in `.c`; header declares a different name)
- `get_tcp_packet__bitmap_data` (`.c`)

---

## 1. Problem Identification

### 1.1 Receiver setup: `set_game_action_process_as__tcp_payload_receiver`
Two distinct defects, both breaking the module's semantic contract:

- **Naming mismatch (Translation Gap / Stub-real divergence).** The header
  `tcp_game_action_process.h` declares
  `initialize_process_as__tcp_game_action_payload_receiver`, but the `.c`
  defines a *different* symbol, `set_game_action_process_as__tcp_payload_receiver`.
  The declared function is never defined (linker error if called by name) and the
  defined function is never declared in any header (invisible to conforming
  callers). Header and implementation are not a faithful pair — there is no single
  source of truth (SSOT) for the receiver-setup entry point. The test suite
  corroborates this: every receiver test is stubbed to `MUNIT_FAIL` with a TODO
  stating the header-named function "does not have a implementation".

- **Ignored allocation failure (Precondition/Postcondition violation + leak).**
  `activate_serialization_request` returns `bool` and, per its own contract,
  returns `false` when the TCP packet bitmap (`pM_packet_bitmap`) fails to
  allocate. The receiver setup ignores this return value: on failure it still
  swaps the half-initialized request into `p_process->p_process_data`, sets the
  process kind to `Process_Kind__Serialized`, and returns `true` — reporting
  success for a request whose bitmap is not allocated. The allocated
  `Serialization_Request` is also leaked (never released via
  `PLATFORM_release_serialization_request`). This is a State Desync between the
  reported result and the actual object state.

### 1.2 Bitmap scan: `get_tcp_packet__bitmap_data`
- **Out-of-bounds read on the all-set boundary (Boundary Condition / Invariant
  violation).** The first loop advances `index_of__bitmap_byte` past every fully
  set (`0xff`) byte. When *all* packets are accounted for, it exits with
  `index_of__bitmap_byte == TCP_PAYLOAD_BYTE(quantity_of__tcp_packets__anticipated)`,
  i.e. one past the last valid byte. The second loop then dereferences
  `p_bitmap[index_of__bitmap_byte]` — an out-of-bounds read (undefined behavior).
  The function's documented Postcondition ("return a value
  `>= quantity_of__tcp_packets__anticipated` so callers can detect completion")
  is not upheld on precisely the common completion case; it returns a garbage
  index derived from OOB memory instead.

---

## 2. Impact Assessment

### 2.1 Receiver setup
- **Callers of the header name** (`initialize_process_as__tcp_game_action_payload_receiver`):
  none can currently link — the symbol is undefined. The TCP *receive* path is
  therefore non-functional / dead in-tree; the only references are the stubbed
  tests, which encode a de facto contract (the header name) that the implementation
  does not satisfy.
- **Callers of the defined name** (`set_game_action_process_as__tcp_payload_receiver`):
  no conforming declaration exists in any header, so any in-tree use would be an
  implicit declaration or dead code. No production caller is coupled to the broken
  name, which keeps the rename blast radius low — but it also means the feature is
  currently unreachable through its public interface.
- **Downstream state coupling (State Desync).** `poll_game_action_process__tcp_receive`
  reads `p_serialization_request->pM_packet_bitmap` and feeds it to
  `get_tcp_packet__bitmap_data`. If setup proceeds despite an allocation failure,
  that pointer is null/unallocated and the receive poll dereferences it. Correcting
  setup to bail out on `activate_serialization_request == false` invalidates any
  assumption that a "successful" setup guarantees a valid bitmap; the receive path's
  Precondition (valid, allocated bitmap) becomes real rather than assumed.
- **Leak coupling.** The dispose handler `m_process__dispose_handler__tcp__default`
  releases the request on process teardown, but only if the process was actually
  wired to it. On the failure path the current code wires it anyway, so a partial
  object can be released with an unallocated bitmap — a secondary hazard removed by
  the same fix.

### 2.2 Bitmap scan
- **Callers** are exactly two, both in this file: `poll_game_action_process__tcp_receive`
  and `poll_game_action_process__tcp_delivery`. Both use the return value under the
  assumption that a value `>= quantity` means "complete" (they return
  `End_Of_File` / `Max_Size_Reached`). That completion contract is *already* the
  documented intent; only the implementation fails to honor it. No caller logic needs
  to change — the fix aligns the implementation to the existing caller assumption.
- **Data-structure coupling.** The bitmap is a fixed array sized
  `TCP_PAYLOAD_BYTE(quantity)` (ceil(quantity/8)). The OOB read violates that
  Representation Invariant. Any consumer that relies on the scan being total over a
  correctly-sized array (e.g., delivery slicing via `p_bitmap[...] |= BIT(...)`) is
  protected only once the scan stops reading past the last byte.

---

## 3. Resolution Assessment

### 3.1 Receiver setup
1. **Unify the name (SSOT / eliminate Stub-real divergence).** Pick one canonical
   name and apply it to the header declaration, the `.c` definition, and the test
   suite in a single change. Recommend keeping the header's
   `initialize_process_as__tcp_game_action_payload_receiver` (it is already referenced
   by the tests and spec) and renaming the `.c` definition to match; alternatively
   rename header+tests to the `.c` name. Either way, exactly one symbol must exist so
   the module links and is reachable. Update the debug_error string to match.
2. **Check `activate_serialization_request`.** Capture its `bool` return. On `false`:
   release the request via
   `PLATFORM_release_serialization_request(p_platform_ctx, p_serialization_request)`,
   leave `p_process` unmutated (do not swap `p_process_data`, do not set the dispose
   handler or process kind), and return `false`. Only on success perform the
   `p_process_data` swap, dispose-handler install, and kind/flag setup, then return
   `true`. This makes the Postcondition honest and removes the leak and the
   use-after-failure.
3. **Callers:** none need signature changes (bool contract is unchanged); only the
   rename must propagate to any forward declarations. The redundant
   `set_serialization_request_as__tcp` may be dropped or kept (harmless; `activate`
   already sets the flag) — leave as-is to minimize churn.
4. **Tests/docs:** un-stub the two receiver tests
   (`initialize_tcp_receiver__fails_without_game_context`,
   `initialize_tcp_receiver__process_data_was_game_action`) now that a real
   implementation exists under the canonical name.

### 3.2 Bitmap scan
1. **Guard the boundary (enforce the Representation Invariant).** After the first
   loop, if `index_of__bitmap_byte == TCP_PAYLOAD_BYTE(quantity)` (no partially-set
   byte found, i.e. all bytes `0xff`), return a value `>= quantity`
   (e.g. `quantity_of__tcp_packets__anticipated`) *without* entering the second
   loop and without dereferencing `p_bitmap`. Otherwise run the bit scan as today and
   return `(index_of__bitmap_byte << 3) + index_of__bitmap_bit`.
2. **Optional hardening (Conservative):** clamp the returned index so it can never
   exceed `quantity`, and add a debug assertion that the read stays within
   `TCP_PAYLOAD_BYTE(quantity)` bytes.
3. **Callers:** none — both callers already branch on `>= quantity`, so the corrected
   return makes their completion detection correct with no change to them.
4. **Tests/docs:** add coverage for the all-set bitmap case (see below).

---

## 4. Test Verification Checklist

- **Existing tests** (`test_suite_process_tcp_game_action_process.c`): both receiver
  tests are currently stubbed to `MUNIT_FAIL` and assert nothing. They must be
  re-enabled after the rename + failure-path fix; they will then assert on *correct*
  behavior (fail-without-context returns false; process_data is preserved as the
  Game_Action before setup). No existing assertion encodes the broken behavior.
- **New tests needed:**
  - **Receiver — allocation failure path (Equivalence/Property):** force
    `activate_serialization_request` to fail and assert the function returns `false`,
    `p_process->p_process_data` is unchanged, and no request leaks (Equivalence Check
    against the success path's invariants).
  - **Bitmap — all-set boundary (Property Based Testing / Fuzzing):** for a range of
    `quantity` values, fill the bitmap with all `0xff` and assert the return is
    `>= quantity` with no OOB read (ASan/UBSan clean). Include the edge where
    `quantity % 8 != 0` so the trailing partial byte is exercised.
  - **Bitmap — completion contract (Round Trip Check):** set bits incrementally and
    assert the scan advances to each next unset index and finally reports completion,
    matching the `poll_*` completion branches.
- **Blast radius of tests:** Low–Medium. Only this module's suite is touched; no other
  suite references these symbols. No phased rollout needed.

---

## 5. Blast Radius Summary

- **Files changed:** 2 source/header (`tcp_game_action_process.h`,
  `tcp_game_action_process.c`) + the module's test file. No other production file
  references the broken names or the bitmap helper (helper is file-local).
- **Behavior-preserving for current callers?** The success path of receiver setup is
  unchanged; only the failure path becomes correct (return false + release). The
  bitmap fix makes the completion return correct where it was previously undefined —
  callers' existing `>= quantity` check becomes valid rather than broken. Effectively
  behavior-preserving on all reachable paths and correcting previously-UB ones.
- **Phased approach?** Not required; both fixes are local and independent. The rename
  (3.1.1) should land atomically with the test un-stubbing so the module compiles,
  links, and tests green in one step.
- **De facto contracts invalidated:** The header name
  `initialize_process_as__tcp_game_action_payload_receiver` was the de facto contract
  (tests + spec) that the implementation violated; unifying on it *satisfies* rather
  than invalidates it. The bitmap's "return `>= quantity` on completion" contract is
  preserved and finally honored. No external caller depends on the broken behavior.
