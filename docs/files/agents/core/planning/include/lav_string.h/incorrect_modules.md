# Planning: lav_string.h — Incorrect Modules

**Review source:** `agents/core/review/include/lav_string.h/incorrect_modules.md`

**Source files reviewed (read-only):**
- `core/include/lav_string.h` (declarations + 4 inline wrappers)
- `core/source/lav_string.c` (`cstr_to_i32__limit_n`, `cstr_to_u32__limit_n`)
- `core/source/multiplayer/ipv4_address.c` (production caller)
- `tests/core/source/test_suite_lav_string.c` (stub — no tests)
- `tests/core/source/multiplayer/test_suite_multiplayer_ipv4_address.c` (indirect coverage)

---

## 1. Problem Identification

Six functions were flagged **Incorrect**. They split into two distinct defect
classes.

### Class A — Return-value overwrite (`Mode Confusion`) — 4 inline wrappers in `lav_string.h`

`cstr_to_u16__limit_n`, `cstr_to_i8__limit_n`, `cstr_to_u8__limit_n`, and
`cstr_to_i16__limit_n` all share one root cause. Each delegates to a 32-bit
callee and then **assigns the callee's `bool` return value back into the same
`value` variable** that the callee populated through its `&value` out-parameter:

```c
value = (u16)cstr_to_u32__limit_n(p_cstr, limit_n, &value);
```

The callee writes the parsed integer via `&value`, then returns a `bool`. The
assignment immediately **overwrites** that integer with `0`/`1`. The subsequent
`bool result = (value != 0)` only re-tests the boolean, and
`*p_OUT_* = (u16)value` always writes `1` on success — never the parsed number.
This is a `Mode Confusion`: the boolean success/failure channel and the numeric
result channel are aliased onto one variable, so the numeric channel is destroyed.
The four wrappers are a `DRY` violation of a broken pattern — one fix shape applies
to all four.

- **`cstr_to_u16__limit_n`** — always outputs `1` on success; non-functional.
- **`cstr_to_i8__limit_n`** — same overwrite; always outputs `1`.
- **`cstr_to_u8__limit_n`** — same overwrite, plus a `value != 0` success guard
  that additionally forbids a legitimately parsed `0` (see Impact).
- **`cstr_to_i16__limit_n`** — same overwrite; always outputs `1`.

### Class B — Callee defects (`lav_string.c`)

**`cstr_to_i32__limit_n`:**
1. **Missing null-terminator check in the digit loop.** The `get_numeric` loop
   tests only `index_towards__limit_n < limit_n`, omitting
   `&& p_cstr[index_towards__limit_n]`. When `limit_n` exceeds the string
   length, it reads past the terminator (`Boundary Condition` violation /
   out-of-bounds read). The null byte fails the digit check and forces a spurious
   `return false` — e.g. `"5"` with `limit_n = 5` returns `false`. This is a
   `Translation Gap`: the loop does not honor the string's actual end.
2. **No digit-count tracking.** If no digit is consumed (e.g. `""` or `"-"`),
   `value` stays `0` and the function returns `true` with `*p_OUT_i32 = 0`,
   violating the intended `Postcondition` that a digit-less string must fail.

**`cstr_to_u32__limit_n`:**
1. **Signed/unsigned comparison.** Loop index is `Index__u32` (`uint32_t`) but
   compared to `limit_n` (`i32`). A negative `limit_n` promotes to a huge
   `uint32_t`, driving the loop past the string bounds (out-of-bounds read).
2. **Signed accumulator.** The accumulator is `i32 value`, so values in
   `[INT32_MAX+1, UINT32_MAX]` cause signed overflow — undefined behavior and a
   broken `Representation Invariant` for the unsigned result type.

## 2. Impact Assessment

### Direct caller — `populate_ipv4_address` (de facto contract already in use)

`core/source/multiplayer/ipv4_address.c` is the **only** production caller of the
four inline wrappers:
- `cstr_to_u8__limit_n` — parses each of the four IPv4 octets.
- `cstr_to_u16__limit_n` — parses the port.

Because both are broken (Class A), `populate_ipv4_address` receives `1` for every
octet and for the port on every "successful" parse. It is **non-functional** today:
`"192.168.1.1"` / port `"7777"` yields `ip_bytes = [1,1,1,1]`, `port = 1`.

The `value != 0` guard in the unsigned wrappers additionally means a parsed `0`
is reported as failure. The caller's inner loop falls through to `return false`
when all length attempts (3/2/1) fail — which happens for any octet of `0` even
after the overwrite bug is fixed. So correcting the overwrite **invalidates an
assumption coupled to the broken behavior**: code paths that treat "parse of 0" as
failure must be re-evaluated.

### Data structures coupled to the broken behavior

`IPv4_Address { u8 ip_bytes[4]; u16 port; }` is embedded in:
- `TCP_Socket.tcp_socket__address` (`core/include/multiplayer/tcp_socket.h`,
  `core/source/multiplayer/tcp_socket.c`) — every socket's address.
- `TCP_Socket_Manager` (`tcp_socket_manager.c`) — pending-connection address.

Both are populated through the same parsing path. Fixing the wrappers changes the
values these structs observe, so any downstream assumption that a parsed octet/port
is `1` (the current broken output) is invalidated.

### Test coupling

- `tests/core/source/multiplayer/test_suite_multiplayer_ipv4_address.c` asserts
  concrete octet/port values and includes zero-valued and localhost cases that
  exercise the `value == 0` edge the guard currently blocks. These assert **correct**
  behavior (pre-flag) and cannot pass until the fix lands; they will validate it.
- `tests/core/source/test_suite_lav_string.c` is a **stub** (`#warning`, no tests).
  No existing test pins the broken behavior as a contract, so there is no de facto
  test to preserve.

### Other callers

A scan of `./core/source` and `./core/include` found **no** other references to
`cstr_to_i32__limit_n`, `cstr_to_u32__limit_n`, or the four wrappers outside
`ipv4_address.c` and the `lav_string.h/.c` definition pair.

## 3. Resolution Assessment

### Phase 1 — Fix the four inline wrappers (Class A)

For each wrapper in `core/include/lav_string.h`, capture the callee's `bool` in a
separate variable and write only the parsed `value` to the output:

```c
u32 value = 0;
bool result = cstr_to_u32__limit_n(p_cstr, limit_n, &value);
if (result)
    *p_OUT_u16 = (u16)value;
return result;
```

- **Decision point:** the `value != 0` guard rejects a legitimate `0`. The
  `populate_ipv4_address__zeroes` test implies `0` should be a valid parse. Resolve
  before implementing: either drop the guard and return the callee's `bool` directly
  (recommended, matches the caller contract), or keep it if `0` is intentionally
  invalid. This decision is a `Single Source of Truth` question about what "success"
  means for these wrappers.

### Phase 2 — Fix `cstr_to_u32__limit_n` (Class B)

1. Change the accumulator `i32 value` → `u32 value` to match the output type and
   remove signed-overflow UB for values `> INT32_MAX`.
2. Resolve the signed/unsigned comparison so a negative `limit_n` cannot produce an
   enormous unsigned bound — either validate `limit_n >= 0` (return `false`) or
   compare against a controlled unsigned bound.

### Phase 3 — Fix `cstr_to_i32__limit_n` (Class B)

1. Add `&& p_cstr[index_towards__limit_n]` to the `get_numeric` loop condition so it
   stops at the null terminator (mirroring the pattern already in
   `cstr_to_u32__limit_n`).
2. Track whether any digit was consumed; if none, return `false` without writing
   `*p_OUT_i32`, so sign-only and empty strings are rejected per contract.

### Phase 4 — Test verification

- **Populate the stub** `test_suite_lav_string.c` with direct unit tests for all six
  functions (currently empty). Use:
  - `Property Based Testing` to assert the parse invariant (round-trip of generated
    digit strings against a reference parser).
  - `Round Trip Check` / `Equivalence Check` — formatted integer re-parses to the
    same value.
  - `Fuzzing` for boundary cases: negative `limit_n`, empty string, sign-only,
    non-digit chars, values near `INT32_MAX`/`UINT32_MAX`, and zero-valued input.
- **Re-run** `test_suite_multiplayer_ipv4_address.c`; the zero/localhost/valid/max
  cases confirm the caller path is repaired end-to-end.
- If the Phase 1 guard is removed, add an explicit case asserting a parsed `0`
  succeeds (octet `0`, port `0`).

## 4. Blast Radius Summary

- **Files changed:** 2 (`lav_string.h`, `lav_string.c`) + test files
  (`test_suite_lav_string.c`, and re-run of the ipv4_address suite). No other source
  file requires modification.
- **Behavior-preserving for current callers?** No — the current output is broken
  (always `1`); the fix changes observable values, which is the intended correction.
  The one de facto contract invalidated is "parse of `0` ⇒ failure", resolved by the
  Phase 1 guard decision.
- **Phased approach:** Recommended (wrappers → u32 callee → i32 callee → tests),
  though all fixes are independent and could land in one coordinated change.
- **Overall blast radius: Low–Moderate**, contained to `lav_string` and its single
  production caller `populate_ipv4_address` (and the structs that consume it).
