# Planning: game_action__tcp_delivery.h — Incorrect Modules

**Review source:** `agents/core/review/include/game_action/core/tcp/game_action__tcp_delivery.h/incorrect_modules.md`

**Source files reviewed (read-only):**
- `core/include/game_action/core/tcp/game_action__tcp_delivery.h`
- `core/source/game_action/core/tcp/game_action__tcp_delivery.c`
- `core/source/process/tcp_game_action_process.c`
- `core/include/serialization/serialization_request.h`
- `core/source/serialization/serialization_request.c`
- `tests/core/source/game_action/core/tcp/test_suite_game_action_core_tcp_game_action__tcp_delivery.c`

---

## 1. Problem Identification

**Function:** `m_process__game_action__tcp_delivery__inbound`
**File:** `core/source/game_action/core/tcp/game_action__tcp_delivery.c` (line ~59–68)

**Defect:** Off-by-one error in the `quantity_of__bytes_to__copy` computation (second branch of ternary). The expression subtracts `PAYLOAD_SIZE * (packet_index__u16 + 1)` from `quantity_of__bytes_in__destination`, computing the remaining bytes *after* this packet's slot rather than the remaining bytes *for* this packet.

**Consequence — two failure modes when `total_bytes % PAYLOAD_SIZE != 0`:**

| Packet position | Computed (buggy) | Correct | Effect |
|---|---|---|---|
| Second-to-last (index N-1) | `min(PAYLOAD, total - PAYLOAD*N)` = small remainder | `min(PAYLOAD, total - PAYLOAD*(N-1))` = full PAYLOAD | **Data truncation** — fewer bytes copied than the slot holds; destination buffer left with stale/zero data in the tail. |
| Last (index N) | `min(PAYLOAD, total - PAYLOAD*(N+1))` → unsigned underflow → huge value → returns PAYLOAD | `min(PAYLOAD, total - PAYLOAD*N)` = small remainder | **Buffer overflow** — `memcpy` writes PAYLOAD bytes into a region that only has the small remainder of space. |

The correct formula is confirmed by the outbound counterpart `poll_game_action_process__tcp_delivery` in `core/source/process/tcp_game_action_process.c`, which uses `PAYLOAD_SIZE * index_of__bitmap_bit` (no `+1`).

**Secondary issue — missing null guard:** The function does not validate that `p_serialization_request->p_tcp_packet_destination` or `p_serialization_request->pM_packet_bitmap` are non-null before dereferencing. While the `Process_Kind__Serialized` check provides implicit assurance (only `activate_serialization_request` with `is_serialization_request__tcp_or__io == true` sets up these fields), an explicit null check would harden the function against misuse.

---

## 2. Impact Assessment

### Directly affected code path

The broken function is the **receive-side handler** for TCP-delivered payload chunks. It is registered via `register_game_action__tcp_delivery` into the `Game_Action_Logic_Table` as the inbound process for `Game_Action_Kind__TCP_Delivery`.

### Callers / dependents

| Component | Relationship | Impact of fix |
|---|---|---|
| `poll_game_action_process__tcp_delivery` (`core/source/process/tcp_game_action_process.c`) | **Outbound** counterpart — already correct. No change needed. | None. The fix makes inbound **Faithful** to the outbound's byte-splitting logic, restoring **Round Trip Safe** symmetry. |
| `activate_serialization_request` (`core/source/serialization/serialization_request.c`) | Sets `quantity_of__bytes_in__destination`, `quantity_of__tcp_packets__anticipated`, allocates `pM_packet_bitmap`. | No change needed. The fix aligns the consumer with the producer's allocation intent. |
| Platform TCP receive path (backend `PLATFORM_tcp_recieve`) | Delivers raw bytes that are parsed into `Game_Action` and dispatched to this handler. | No change needed. The wire format is unchanged; only the local copy-into-buffer logic is corrected. |
| Any caller that assumes the destination buffer is fully populated after all packets arrive | Relies on the **Postcondition** that all payload bytes land at the correct offset. | Currently, payloads whose total size is not a multiple of `PAYLOAD_SIZE` arrive **corrupted** (truncated second-to-last + overflowed last). Fixing the bug **restores** the intended postcondition; no existing caller is *correctly* coupled to the broken behavior. The broken behavior has no valid use-case. |

### Assumptions invalidated by the fix

- **None.** The broken formula is a pure defect — no caller can be *correctly* dependent on it. The outbound function already implements the correct arithmetic, confirming the intended **Invariant**: `bytes_to_copy = min(PAYLOAD_SIZE, total - PAYLOAD_SIZE * index)`.
- The bitmap logic (`TCP_PAYLOAD_BYTE` / `TCP_PAYLOAD_BIT`) is unaffected and already correct.
- The first branch of the ternary (single-packet case where `total < PAYLOAD_SIZE`) is already correct and unaffected.

### De facto contract

The broken behavior is **not** a de facto contract. It is a memory-safety defect (buffer overflow) that would corrupt heap memory for any payload whose total size is not an exact multiple of `PAYLOAD_SIZE`. Any system currently "working" with such payloads is operating in undefined behavior territory.

---

## 3. Resolution Assessment

### Change 1: Fix the off-by-one in `quantity_of__bytes_to__copy`

**File:** `core/source/game_action/core/tcp/game_action__tcp_delivery.c`
**Location:** Lines 63–68 (second branch of ternary)

**Current (broken):**
```c
: min__u32(
        GA_KIND__TCP_DELIVERY__PAYLOAD_SIZE_IN__BYTES,
        p_serialization_request
            ->quantity_of__bytes_in__destination
        - (GA_KIND__TCP_DELIVERY__PAYLOAD_SIZE_IN__BYTES
            * (packet_index__u16 + 1)));
```

**Corrected:**
```c
: min__u32(
        GA_KIND__TCP_DELIVERY__PAYLOAD_SIZE_IN__BYTES,
        p_serialization_request
            ->quantity_of__bytes_in__destination
        - (GA_KIND__TCP_DELIVERY__PAYLOAD_SIZE_IN__BYTES
            * packet_index__u16));
```

**Rationale:** Remove the `+1`. The formula must compute bytes remaining *for* this packet's slot: `total - PAYLOAD_SIZE * index`. This matches the outbound function's arithmetic exactly, ensuring **Equivalence** between send and receive paths.

### Change 2: Add null guards for TCP-specific fields (defensive, low priority)

**File:** `core/source/game_action/core/tcp/game_action__tcp_delivery.c`
**Location:** After line 40 (after casting `p_process_data` to `Serialization_Request*`)

**Add:**
```c
if (!p_serialization_request->p_tcp_packet_destination
        || !p_serialization_request->pM_packet_bitmap) {
    debug_error("m_process__game_action__tcp_delivery__inbound, null tcp fields.");
    fail_process(p_this_process);
    return;
}
```

**Rationale:** Hardens against **Representation Invariant** violations if the process kind is set without proper activation. Low risk, defensive.

### Callers requiring update

- **None.** The function signature and contract are unchanged. Only the internal arithmetic is corrected.

### Documentation / spec updates

- If a spec file exists at `docs/specs/core/game_action/tcp/game_action__tcp_delivery.h.spec.md`, verify the postcondition description matches the corrected formula. No structural change to the spec is expected — the spec likely already states the correct intent.

### Phased approach

Not needed. The fix is a single-expression change in one function. Blast radius is minimal.

---

## 4. Test Verification Checklist

### Existing test coverage

The test file `tests/core/source/game_action/core/tcp/test_suite_game_action_core_tcp_game_action__tcp_delivery.c` currently covers:
- Registration (`register_game_action__tcp_delivery`)
- Initialization field-setting (kind, client UUID, response UUID, packet index, payload copy)

**Gap:** No test exercises `m_process__game_action__tcp_delivery__inbound`'s byte-copy logic. The existing tests are all **stateless** and do not construct a `Process` + `Game` + `Serialization_Request` scenario to invoke the inbound handler.

### Required new tests

| Test | Strategy | What it verifies |
|---|---|---|
| `inbound__single_packet__copies_all_bytes` | **Equivalence Check** against direct memcpy | When `total < PAYLOAD_SIZE`, all bytes land at offset 0. |
| `inbound__multiple_packets_exact_multiple` | **Round Trip Check**: send via `poll_game_action_process__tcp_delivery`, receive via inbound handler, compare destination buffer to source. | When `total % PAYLOAD_SIZE == 0`, full buffer is reconstructed. |
| `inbound__multiple_packets_non_exact_multiple` | **Round Trip Check** with `total = k*PAYLOAD + r` where `0 < r < PAYLOAD`. | Second-to-last packet copies full PAYLOAD bytes; last packet copies only `r` bytes. No overflow. This is the **Boundary Condition** that exposed the bug. |
| `inbound__packet_index_exceeds_anticipated__fails` | Direct assertion on process status. | Precondition enforcement: out-of-bounds index → `Process_Status_Kind__Fail`. |
| `inbound__null_tcp_fields__fails` | Inject null `p_tcp_packet_destination` or `pM_packet_bitmap`. | Defensive null-guard path (Change 2). |

### Test blast radius

- **Low.** New tests are additive. No existing test asserts on the broken behavior (the broken function is not exercised at all by current tests).
- No existing test will break as a result of the fix.

### Recommended testing methodology

- **Round Trip Check** for the primary correctness property (send/receive symmetry).
- **Property Based Testing** to fuzz `total_bytes` across `[1, 2*PAYLOAD_SIZE + PAYLOAD_SIZE - 1]` and verify the destination buffer always equals the source.
- **Mutation Testing** (optional) to confirm the new tests would catch reintroduction of the `+1`.

---

## 5. Blast Radius Summary

| Dimension | Assessment |
|---|---|
| Files modified | **1** (`core/source/game_action/core/tcp/game_action__tcp_delivery.c`) — single expression fix + optional null guard. |
| Behavior-preserving for current callers? | **Yes.** The fix corrects a memory-safety defect. No caller is correctly coupled to the broken arithmetic. |
| Phased approach needed? | **No.** Single-expression change, no API change, no cascading edits. |
| De facto contracts invalidated? | **None.** The broken behavior is a bug, not a contract. |
| Test impact | **Low.** Additive tests only; no existing assertions invalidated. |
| Risk of regression from fix | **Minimal.** The corrected formula is confirmed correct by the outbound function (SSOT of the byte-splitting logic). |
