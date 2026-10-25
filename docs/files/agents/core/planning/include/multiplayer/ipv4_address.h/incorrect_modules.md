# Planning: ipv4_address.h — Incorrect Modules

**Review source:** `agents/core/review/include/multiplayer/ipv4_address.h/incorrect_modules.md`

**Source files reviewed (read-only):**
- `core/include/multiplayer/ipv4_address.h`
- `core/source/multiplayer/ipv4_address.c`
- `core/include/lav_string.h`
- `core/source/lav_string.c`
- `tests/core/source/multiplayer/test_suite_multiplayer_ipv4_address.c`
- `tests/core/source/test_suite_lav_string.c`

---

## 1. Problem Identification

### `populate_ipv4_address` (flagged: **Incorrect**)

The function itself is structurally sound — it correctly iterates over 4 octets and a port, advancing indices past dot separators. However, it delegates all numeric conversion to `cstr_to_u8__limit_n` and `cstr_to_u16__limit_n` (both `static inline` in `core/include/lav_string.h`), and **both helpers contain two compounding defects**:

1. **Mode Confusion** — Each wrapper assigns the `bool` return value of the underlying function (`cstr_to_u32__limit_n`) back into the same variable that holds the parsed numeric result:
   ```c
   u32 value = 0;
   value = (u8)cstr_to_u32__limit_n(p_cstr, limit_n, &value); // bool overwrites parsed value
   ```
   The callee writes the true parsed number through `&value`, but the caller immediately clobbers it with the `bool` return (1 on success, 0 on failure). Result: `*p_OUT_u8` / `*p_OUT_i16` is always **1** for any successfully parsed input.

2. **Boundary Condition** — The success discriminator is `(value != 0)`, which conflates "parse failed" with "parsed value is zero." Any legitimately parsed octet or port of 0 (e.g., `"127.0.0.1"`, `"0.0.0.0"`) is treated as a parse failure, causing `populate_ipv4_address` to return `false` for valid addresses containing zero octets.

**Net effect:** For any valid non-zero input, `populate_ipv4_address` produces `ip_bytes = {1,1,1,1}`, `port = 1`. For any input containing a zero octet or port, it returns `false`.

The identical Mode Confusion + Boundary Condition pattern exists in `cstr_to_i8__limit_n` and `cstr_to_i16__limit_n` (currently uncalled but equally broken).

---

## 2. Impact Assessment

### Direct callers of `populate_ipv4_address`

| Caller | File | Coupling |
|--------|------|----------|
| Test suite | `tests/core/source/multiplayer/test_suite_multiplayer_ipv4_address.c` | Asserts on correct octet/port values; currently **all positive tests fail** against the broken implementation. |

### Downstream consumers of `IPv4_Address` (populated via this path)

| Consumer | File | Assumption invalidated by fix |
|----------|------|-------------------------------|
| `initialize_tcp_socket` | `core/source/multiplayer/tcp_socket.c` | Stores `IPv4_Address` into `TCP_Socket.tcp_socket__address`; downstream network I/O (connect/bind) relies on the correct byte values. Currently receives `{1,1,1,1}` / port `1`. |
| `server__default` poll loop | `core/source/multiplayer/server__default.c` | Calls `poll_tcp_socket_manager_for__pending_connections` which returns an `IPv4_Address`; server-side connection tracking assumes valid address bytes. |
| TCP connect game action | `core/source/game_action/core/tcp/game_action__tcp_begin_connect.c` | Reads `IPv4_Address` from game action payload to drive client-side socket connect. Currently would attempt to connect to `1.1.1.1:1`. |

### Coupling to the broken helper layer

- `core/include/lav_string.h` defines four `static inline` wrappers (`cstr_to_i8__limit_n`, `cstr_to_i16__limit_n`, `cstr_to_u8__limit_n`, `cstr_to_u16__limit_n`) all sharing the same defect pattern. The fix must address all four to prevent latent bugs if any are called in the future.
- The underlying functions (`cstr_to_i32__limit_n`, `cstr_to_u32__limit_n` in `core/source/lav_string.c`) are **correct** — they write the parsed value through the output pointer and return a `bool` indicating parse success. The defect is entirely in the wrapper layer.
- No de facto contract is being relied upon: the broken behavior (always returning 1) has no legitimate consumer. The existing test suite already encodes the *correct* expected behavior, confirming that no caller has adapted to the broken output.

### What correcting this invalidates

Nothing in `./include` or `./source` has adapted to the broken behavior. The fix is purely restorative: it brings the implementation into alignment with its documented contract and existing test assertions. No cascading changes to callers are needed — they already expect correct values.

---

## 3. Resolution Assessment

### Step 1: Fix the four `static inline` wrappers in `core/include/lav_string.h`

For each wrapper, separate the boolean return from the numeric output:

```c
// Before (broken):
u32 value = 0;
value = (u8)cstr_to_u32__limit_n(p_cstr, limit_n, &value);
bool result = (value != 0);
if (result) *p_OUT_u8 = (u8)value;
return result;

// After (correct):
u32 value = 0;
bool success = cstr_to_u32__limit_n(p_cstr, limit_n, &value);
if (success) *p_OUT_u8 = (u8)value;
return success;
```

Apply the same pattern to:
- `cstr_to_u8__limit_n` (uses `cstr_to_u32__limit_n`, casts to `u8`)
- `cstr_to_u16__limit_n` (uses `cstr_to_u32__limit_n`, casts to `u16`)
- `cstr_to_i8__limit_n` (uses `cstr_to_i32__limit_n`, casts to `i8`)
- `cstr_to_i16__limit_n` (uses `cstr_to_i32__limit_n`, casts to `i16`)

**No changes required** to:
- `core/source/multiplayer/ipv4_address.c` — its parsing loop logic is correct; it will work once the helpers are fixed.
- `core/source/lav_string.c` — the underlying `cstr_to_u32__limit_n` and `cstr_to_i32__limit_n` are already correct.

### Step 2: Verify existing test suite passes

The test file `tests/core/source/multiplayer/test_suite_multiplayer_ipv4_address.c` already asserts on correct behavior:
- Octet parsing (192, 168, 1, 1) — **currently failing, will pass after fix**
- Port parsing (7777) — **currently failing, will pass after fix**
- Zero boundary (`"0.0.0.0"`, port `"0"`) — **currently failing, will pass after fix**
- Max octets (`255.255.255.255`) — **currently failing, will pass after fix**
- Localhost (`127.0.0.1`, port `8080`) — **currently failing, will pass after fix**
- Null/empty error cases — already passing (no behavior change)

No test modifications are required for the existing suite.

### Step 3: Add direct unit tests for `lav_string.h` wrappers

The test file `tests/core/source/test_suite_lav_string.c` is an empty placeholder. Add tests covering:
- **Round Trip Check**: For a range of values, format to string → parse via wrapper → verify value matches original.
- **Property Based Testing**: Generate random `u8`/`u16`/`i8`/`i16` values, serialize to string, parse back, assert equality (invariant: parse(serialize(x)) == x).
- **Boundary Condition**: Explicit tests for value 0, min, max for each wrapper type.
- **Fuzzing**: Feed malformed strings (non-numeric chars, overly long strings) to confirm the function returns `false` without UB.

### Step 4: No caller changes needed

All downstream consumers (`tcp_socket.c`, `server__default.c`, `game_action__tcp_begin_connect.c`) already expect correct `IPv4_Address` values. The fix is behavior-restoring, not behavior-changing. No refactoring of callers is required.

---

## 4. Test Verification Checklist

| Existing test | Currently asserts | Post-fix expectation |
|---|---|---|
| `populate_ipv4_address__valid_input__returns_true` | `result == true` for `"192.168.1.1"`, `"7777"` | PASSES (was failing) |
| `populate_ipv4_address__valid_input__parses_first_octet` | `ip_bytes[0] == 192` | PASSES (was failing) |
| `populate_ipv4_address__valid_input__parses_second_octet` | `ip_bytes[1] == 168` | PASSES (was failing) |
| `populate_ipv4_address__valid_input__parses_third_octet` | `ip_bytes[2] == 1` | PASSES (was failing) |
| `populate_ipv4_address__valid_input__parses_fourth_octet` | `ip_bytes[3] == 1` | PASSES (was failing) |
| `populate_ipv4_address__valid_input__parses_port` | `port == 7777` | PASSES (was failing) |
| `populate_ipv4_address__zeroes__parses_correctly` | `"0.0.0.0"`, `"0"` → all zeros, returns true | PASSES (was failing — boundary condition) |
| `populate_ipv4_address__max_octets__parses_correctly` | `"255.255.255.255"` → all 255 | PASSES (was failing) |
| `populate_ipv4_address__localhost__parses_correctly` | `"127.0.0.1"`, `"8080"` → 127,0,0,1 / 8080 | PASSES (was failing — zero octets) |
| `populate_ipv4_address__null_ip_string__returns_false` | null → false | PASSES (no change) |
| `populate_ipv4_address__null_port_string__returns_false` | null → false | PASSES (no change) |
| `populate_ipv4_address__empty_ip_string__returns_false` | `""` → false | PASSES (no change) |
| `populate_ipv4_address__empty_port_string__returns_false` | `""` → false | PASSES (no change) |

**New tests needed:** Direct unit tests for the four `lav_string.h` wrappers (see Step 3 above). The `test_suite_lav_string.c` file is currently empty.

**Blast radius of test changes:** **Low** — existing tests require no modification; only new tests are added to the empty `lav_string` suite.

---

## 5. Blast Radius Summary

| Dimension | Assessment |
|-----------|------------|
| Files requiring code changes | **1** (`core/include/lav_string.h`) |
| Files requiring test changes | **1** (`tests/core/source/test_suite_lav_string.c` — currently empty) |
| Behavior-preserving for current callers? | **Yes** — the fix restores intended behavior; no caller has adapted to the broken output. |
| Phased approach needed? | **No** — single-file fix with immediate test verification. |
| De facto contracts invalidated? | **None** — the broken behavior (always-1 output) was never a relied-upon contract. |
| Risk level | **Low** — the underlying `cstr_to_u32__limit_n` / `cstr_to_i32__limit_n` are correct and unchanged; only the thin wrapper layer is corrected. |
