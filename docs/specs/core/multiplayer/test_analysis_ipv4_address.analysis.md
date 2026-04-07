# Test Analysis: ipv4_address

## 1. Overview

This document analyses the failing tests reported in
`test_suite_multiplayer_ipv4_address.c.report` against the specification
in `ipv4_address.h.spec.md` and the implementation in
`core/source/multiplayer/ipv4_address.c`.

---

## 2. Failing Tests Summary

| Line | Assertion | Expected | Actual |
|------|-----------|----------|--------|
| 15 | `addr.ip_bytes[0] == 192` | `192` | `1` |
| 22 | `addr.ip_bytes[1] == 168` | `168` | `1` |
| 43 | `addr.port == 7777` | `7777` | `1` |
| 51 | `addr.ip_bytes[0] == 0` | `0` | `1` |
| 63 | `addr.ip_bytes[0] == 255` | `255` | `1` |
| 74 | `addr.ip_bytes[0] == 127` | `127` | `1` |
| 106 | `result is not false` | `false` | `true` (not false) |

---

## 3. Root Cause Analysis

### 3.1 ip_bytes are always 1 (lines 15, 22, 51, 63, 74)

All `ip_bytes` fields are being set to `1` instead of the parsed octet
value. The actual values being stored are the **return value of
`cstr_to_u8__limit_n`** (a boolean `true`/`1` on success), rather than
the parsed byte value written into `ip_byte`.

In `populate_ipv4_address`, the inner loop calls:

