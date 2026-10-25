# Planning: hashing.h — Incorrect Modules

**Review source:** `agents/core/review/include/serialization/hashing.h/incorrect_modules.md`

**Source files reviewed (read-only):**
- `core/include/serialization/hashing.h`
- `core/include/serialization/serialization_header.h`
- `core/include/serialization/identifiers.h`
- `core/source/serialization/hashing.c`
- `tests/core/source/serialization/test_suite_serialization_hashing.c`
- `tests/core/include/serialization/test_suite_serialization_hashing.h`

---

## 1. Problem Identification

Seven functions across `hashing.h` and `hashing.c` are flagged **Incorrect**. They fall into three defect categories:

### 1.1 Missing NULL guard before `ALLOCATE_P` / `ALLOCATE_P__u64` — NULL pointer dereference

Four functions invoke the `ALLOCATE_P` (u32) or `ALLOCATE_P__u64` (u64) macro **unconditionally** after calling a slot-finder that may return NULL when the array is full. The macro dereferences the pointer to read `size_of__struct` before calling `initialize_serialization_header` / `initialize_serialization_header__uuid_64`, so a NULL pointer causes undefined behavior.

The correct pattern already exists in two sibling functions — `allocate_serialization_header_with__this_uuid` (u32, line 117) and `allocate_serialization_header_with__this_uuid__u64` (u64, line 213) — both of which guard the macro call with `if (p_serialization_header)`.

Affected functions:

| # | Function | File | Line | Macro invoked |
|---|----------|------|------|---------------|
| 1 | `allocate_serialization_header` | `core/include/serialization/hashing.h` | 134 | `ALLOCATE_P` |
| 2 | `allocate_serialization_header_with__uuid_branding` | `core/include/serialization/hashing.h` | 150 | `ALLOCATE_P` |
| 3 | `allocate_serialization_header__u64` | `core/include/serialization/hashing.h` | 230 | `ALLOCATE_P__u64` |
| 4 | `allocate_serialization_header_with__uuid_branding__u64` | `core/include/serialization/hashing.h` | 247 | `ALLOCATE_P__u64` |

Each function delegates to `get_next_available__random_allocation_in__contiguous_array` (or its `__uuid_64` variant), which can legitimately return NULL when the contiguous array is completely full (the underlying `poll_for__uuid_collision` returns the `INDEX__UNKNOWN__u32` **Sentinel**). The missing `if (...)` guard violates the **Precondition** that the pointer be non-null before the macro dereferences it.

### 1.2 Missing full-array check + hash-bucket corruption in UUID resolution

Two functions compute a page-aligned base UUID, delegate to `poll_for__uuid_collision`, then add the returned index back to the base. They have two defects:

1. **Hash-bucket corruption (Aliasing Bug):** The UUID is rounded down to a multiple of `length_of__p_serialization_headers` *before* being passed to `poll_for__uuid_collision`. Inside that callee, the starting probe index is computed as `identifier % length`. Because the rounded-down UUID is always a multiple of the length, the starting index is always 0 — the original UUID's hash bucket is never used. Additionally, the collision-match check inside `poll_for__uuid_collision` compares against the rounded-down base rather than the original UUID, so an already-present UUID will never be detected as a collision.

2. **Missing full-array check (Boundary Condition):** When the array is completely full, `poll_for__uuid_collision` returns `INDEX__UNKNOWN__u32`. The function does not test for this **Sentinel** value and instead computes `uuid += INDEX__UNKNOWN__u32`, which wraps to `base - 1` (unsigned wrap-around), producing a garbage UUID rather than `IDENTIFIER__UNKNOWN__u32`.

Affected functions:

| # | Function | File | Lines |
|---|----------|------|-------|
| 5 | `get_next_available__uuid_in__contiguous_array` | `core/source/serialization/hashing.c` | 86–99 |
| 6 | `get_next_available__uuid_in__contiguous_array__uuid_64` | `core/source/serialization/hashing.c` | 101–114 |

### 1.3 Missing invalid-identifier guard in u64 dehash lookup

`dehash_identitier_u64_in__contigious_array` (u64, `hashing.c` lines 159–196) is missing the `is_identifier_u64__invalid` guard that its u32 counterpart (`dehash_identitier_u32_in__contigious_array`, lines 116–157) has at its entry. When `IDENTIFIER__UNKNOWN__u64` (`0xFFFFFFFFFFFFFFFF`) is passed, the function skips validation and proceeds to probe the array. Since `poll_for__uuid_collision__uuid_64` returns the first deallocated slot it finds, the function may return a non-null pointer to a deallocated header instead of NULL.

This is observable through the inline helper `has_uuid_in__contiguous_array__uuid_64` (hashing.h lines 264–272), which casts the return value to `bool` — a non-null result for an invalid identifier would incorrectly report that the UUID exists in the array.

Affected function:

| # | Function | File | Lines |
|---|----------|------|-------|
| 7 | `dehash_identitier_u64_in__contigious_array` | `core/source/serialization/hashing.c` | 159–196 |

---

## 2. Impact Assessment

### 2.1 Call chain for Category A (missing NULL guards)

The four broken allocation functions all follow this call chain:

```
allocate_serialization_header[_with__uuid_branding][__u64]
  → get_next_available__random_allocation_in__contiguous_array[_uuid_64]  (hashing.c)
    → get_next_available__allocation_in__contiguous_array[_u64]  (hashing.c)
      → poll_for__uuid_collision[_uuid_64]  (hashing.c)
```

`get_next_available__allocation_in__contiguous_array` (lines 198–215) and its u64 variant (lines 217–235) are **Correct** — they properly check for the `INDEX__UNKNOWN__u32` **Sentinel** and return NULL. The bug is that the four allocation wrappers do not respect that NULL return before invoking `ALLOCATE_P` / `ALLOCATE_P__u64`.

The correct siblings (`allocate_serialization_header_with__this_uuid` and `allocate_serialization_header_with__this_uuid__u64`) demonstrate the established pattern: `if (p_serialization_header) ALLOCATE_P(...)`.

### 2.2 Call chain for Category B (UUID resolution bugs)

`get_next_available__uuid_in__contiguous_array` (u32) and `get_next_available__uuid_in__contiguous_array__uuid_64` (u64) are called by:

- `get_next_available__random_uuid_in__contiguous_array` (hashing.h line 67, inline)
- `get_next_available__random_branded_uuid_in__contiguous_array` (hashing.h line 80, inline)
- `get_next_available__random_uuid_in__contiguous_array__uuid_64` (hashing.h line 156, inline)
- `get_next_available__random_branded_uuid_in__contiguous_array__uuid_64` (hashing.h line 170, inline)

These inline helpers are in turn called by `get_next_available__random_allocation_in__contiguous_array` (hashing.c line 237) and `get_next_available__random_allocation_in__contiguous_array__uuid_64` (hashing.c line 262), which feed the four broken allocation functions in Category A.

**Hash-bucket corruption impact:** Because the UUID is rounded down before probing, all UUIDs effectively start probing from index 0. This defeats the open-addressing hash table's distribution, concentrating all allocations near the beginning of the array and causing premature "full" detection on arrays that are not actually full. The `Conservation Law` of the hash table (each UUID maps to a distinct bucket) is violated.

**Full-array garbage UUID impact:** When the array is full, the garbage UUID returned by `get_next_available__uuid_in__contiguous_array` flows into `get_next_available__allocation_in__contiguous_array`, which calls `poll_for__uuid_collision` with the garbage UUID. If the array is truly full, `poll_for__uuid_collision` returns `INDEX__UNKNOWN__u32`, and `get_next_available__allocation_in__contiguous_array` returns NULL — which then triggers the Category A NULL dereference. If the array is not truly full but the garbage UUID happens to collide with an existing entry, a non-NULL pointer to an already-allocated slot could be returned, causing silent double-allocation.

### 2.3 Call chain for Category C (missing invalid-identifier guard)

`dehash_identitier_u64_in__contigious_array` is called by:
- `has_uuid_in__contiguous_array__uuid_64` (hashing.h line 264, inline)

The u32 counterpart `dehash_identitier_u32_in__contigious_array` correctly guards with `is_identifier_u32__invalid` (hashing.c line 120). The u64 version omits this guard, creating an asymmetry that violates the **Representation Invariant** that both u32 and u64 dehash functions should reject invalid identifiers.

### 2.4 Assumptions coupled to broken behavior

- **No caller relies on the NULL dereference:** The four allocation functions document a post-condition of returning NULL when the array is full. Currently they crash instead. Fixing the NULL guard aligns behavior with the documented contract.
- **No caller relies on the garbage UUID:** `get_next_available__uuid_in__contiguous_array` is only called through the random-allocation chain. No direct caller exists outside this chain.
- **No caller relies on the missing invalid-identifier guard:** No code currently passes `IDENTIFIER__UNKNOWN__u64` to `dehash_identitier_u64_in__contigious_array` or `has_uuid_in__contiguous_array__uuid_64` in a way that depends on the broken behavior.

### 2.5 Existing correct reference implementations

The codebase already contains correct reference implementations for every broken pattern:

- `allocate_serialization_header_with__this_uuid` (u32, hashing.h:108) — correct NULL guard pattern
- `allocate_serialization_header_with__this_uuid__u64` (u64, hashing.h:201) — correct NULL guard pattern + correct `ALLOCATE_P__u64` usage
- `dehash_identitier_u32_in__contigious_array` (hashing.c:116) — correct `is_identifier_u32__invalid` guard pattern

---

## 3. Resolution Assessment

### 3.1 Fix Categories A.1–A.4: Add NULL guards before `ALLOCATE_P` / `ALLOCATE_P__u64`

For each of the four functions, add an `if (...)` guard around the macro call, matching the pattern in `allocate_serialization_header_with__this_uuid` / `allocate_serialization_header_with__this_uuid__u64`.

**Files to change:** `core/include/serialization/hashing.h`

| Function | Current code | Fix |
|----------|-------------|-----|
| `allocate_serialization_header` (line 134) | `ALLOCATE_P(p_serialization_header, uuid__u32);` | `if (p_serialization_header) ALLOCATE_P(p_serialization_header, uuid__u32);` |
| `allocate_serialization_header_with__uuid_branding` (line 150) | `ALLOCATE_P(p_serialization_header, uuid__branding__u32);` | `if (p_serialization_header) ALLOCATE_P(p_serialization_header, uuid__branding__u32);` |
| `allocate_serialization_header__u64` (line 230) | `ALLOCATE_P__u64(p_serialization_header__u64, uuid__u64);` | `if (p_serialization_header__u64) ALLOCATE_P__u64(p_serialization_header__u64, uuid__u64);` |
| `allocate_serialization_header_with__uuid_branding__u64` (line 247) | `ALLOCATE_P__u64(p_serialization_header__u64, uuid__branding__u64);` | `if (p_serialization_header__u64) ALLOCATE_P__u64(p_serialization_header__u64, uuid__branding__u64);` |

**Caller updates:** None — the fix makes the functions return NULL as already documented in their post-conditions.

### 3.2 Fix Categories B.5–B.6: Correct UUID resolution logic

For `get_next_available__uuid_in__contiguous_array` (u32, hashing.c:86–99) and `get_next_available__uuid_in__contiguous_array__uuid_64` (u64, hashing.c:101–114):

1. **Preserve the original UUID for probing:** Compute the page-aligned base separately, but pass the *original* UUID to `poll_for__uuid_collision` / `poll_for__uuid_collision__uuid_64` so that the correct hash bucket is used and collision detection compares against the correct identifier.

2. **Check for the full-array Sentinel:** After `poll_for__uuid_collision` returns, check if the result is `INDEX__UNKNOWN__u32`. If so, return `IDENTIFIER__UNKNOWN__u32` (u32) / `IDENTIFIER__UNKNOWN__u64` (u64) instead of computing a garbage UUID.

**Proposed fix for u32 version (hashing.c:86–99):**
```c
Identifier__u32 get_next_available__uuid_in__contiguous_array(
        Serialization_Header *p_serialization_headers,
        Quantity__u32 length_of__p_serialization_headers,
        Identifier__u32 uuid) {
    Identifier__u32 base_uuid =
        uuid - (uuid % length_of__p_serialization_headers);
    Index__u32 index__u32 =
        poll_for__uuid_collision(
                p_serialization_headers,
                length_of__p_serialization_headers,
                uuid,
                INDEX__UNKNOWN__u32);
    if (index__u32 == INDEX__UNKNOWN__u32)
        return IDENTIFIER__UNKNOWN__u32;
    return base_uuid + index__u32;
}
```

**Proposed fix for u64 version (hashing.c:101–114):**
```c
Identifier__u64 get_next_available__uuid_in__contiguous_array__uuid_64(
        Serialization_Header__UUID_64 *p_serialization_headers,
        Quantity__u32 length_of__p_serialization_headers,
        Identifier__u64 uuid__u64) {
    Identifier__u64 base_uuid__u64 =
        uuid__u64 - (uuid__u64 % length_of__p_serialization_headers);
    Index__u32 index__u32 =
        poll_for__uuid_collision__uuid_64(
                p_serialization_headers,
                length_of__p_serialization_headers,
                uuid__u64,
                INDEX__UNKNOWN__u32);
    if (index__u32 == INDEX__UNKNOWN__u32)
        return IDENTIFIER__UNKNOWN__u64;
    return base_uuid__u64 + index__u32;
}
```

**Caller updates:** The inline callers (`get_next_available__random_uuid_in__contiguous_array`, `get_next_available__random_branded_uuid_in__contiguous_array`, and their u64 counterparts) will now receive `IDENTIFIER__UNKNOWN__u32` / `IDENTIFIER__UNKNOWN__u64` when the array is full, instead of a garbage UUID. They pass this value to `get_next_available__allocation_in__contiguous_array` / `get_next_available__allocation_in__contiguous_array__u64`, which will call `poll_for__uuid_collision` with `IDENTIFIER__UNKNOWN__u32` / `IDENTIFIER__UNKNOWN__u64` as the identifier. This is consistent with the existing behavior — `poll_for__uuid_collision` will probe for a deallocated slot (since `IDENTIFIER__UNKNOWN__u32` matches the deallocated sentinel), and if the array is full, return `INDEX__UNKNOWN__u32`, causing the allocation function to return NULL. The behavior is now correct and well-defined.

### 3.3 Fix Category C.7: Add invalid-identifier guard

For `dehash_identitier_u64_in__contigious_array` (hashing.c:159–196), add the `is_identifier_u64__invalid` guard at the top of the function, matching the u32 counterpart:

```c
if (is_identifier_u64__invalid(identifier__u64)) {
    debug_warning__verbose("dehash_identitier_u64_in__contigious_array, identifier is invalid.");
    return 0;
}
```

**Caller updates:** `has_uuid_in__contiguous_array__uuid_64` (hashing.h:264) will now correctly return `false` for `IDENTIFIER__UNKNOWN__u64`, matching the u32 behavior of `has_uuid_in__contiguous_array`.

---

## 4. Test Verification Checklist

### 4.1 Existing test coverage

- `tests/core/source/serialization/test_suite_serialization_hashing.c` tests only the u32 path: `dehash_identitier_u32_in__contigious_array`, `allocate_serialization_header_with__this_uuid`, `get_next_available__allocation_in__contiguous_array`, `has_uuid_in__contiguous_array`, collision resolution, and `hashing__allocation_returns_null_when_full` (which tests `allocate_serialization_header_with__this_uuid`, the correct sibling — **not** the broken `allocate_serialization_header`).
- **No u64 tests exist at all** in the test suite.
- **No tests directly exercise any of the 7 broken functions.**

### 4.2 Tests that would break after the fix

- **None.** No existing test asserts on the broken behavior. The existing test `hashing__allocation_returns_null_when_full` already tests the correct sibling function and will remain valid.

### 4.3 New tests needed

| Test | Technique | Target function(s) | Rationale |
|------|-----------|-------------------|-----------|
| `hashing__allocate_returns_null_when_full` | `Round Trip Check` | `allocate_serialization_header` | Fill the array, call the function, assert NULL is returned (no crash). |
| `hashing__allocate_with_branding_returns_null_when_full` | `Round Trip Check` | `allocate_serialization_header_with__uuid_branding` | Same as above for the branding variant. |
| `hashing__allocate__u64_returns_null_when_full` | `Round Trip Check` | `allocate_serialization_header__u64` | Same for u64 variant. |
| `hashing__allocate_with_branding__u64_returns_null_when_full` | `Round Trip Check` | `allocate_serialization_header_with__uuid_branding__u64` | Same for u64 branding variant. |
| `hashing__allocate__u64_then_dehash__u64` | `Round Trip Check` | `allocate_serialization_header__u64`, `dehash_identitier_u64_in__contigious_array` | Full u64 round-trip: allocate with specific UUID, dehash by same UUID, verify pointer match. |
| `hashing__allocate_with_uuid_branding__u64_sets_uuid` | `Equivalence Check` | `allocate_serialization_header_with__uuid_branding__u64` | Verify the UUID written has the branding bits OR'd in, equivalent to `allocate_serialization_header_with__this_uuid__u64` behavior. |
| `hashing__get_next_available_uuid_returns_unknown_when_full` | `Property Based Testing` | `get_next_available__uuid_in__contiguous_array` | Fill array, call function, assert return is `IDENTIFIER__UNKNOWN__u32`. |
| `hashing__get_next_available_uuid__u64_returns_unknown_when_full` | `Property Based Testing` | `get_next_available__uuid_in__contiguous_array__uuid_64` | Same for u64 variant. |
| `hashing__get_next_available_uuid_preserves_hash_bucket` | `Property Based Testing` | `get_next_available__uuid_in__contiguous_array` | Verify that the returned UUID hashes to the same bucket as the input (i.e., `(returned % length) == (input % length)`), confirming the hash-bucket corruption fix. |
| `hashing__get_next_available_uuid__u64_preserves_hash_bucket` | `Property Based Testing` | `get_next_available__uuid_in__contiguous_array__uuid_64` | Same for u64 variant. |
| `hashing__dehash_u64_returns_null_for_unknown_identifier` | `Boundary Condition` | `dehash_identitier_u64_in__contigious_array` | Pass `IDENTIFIER__UNKNOWN__u64`, assert NULL return. |
| `hashing__has_uuid__u64_returns_false_for_unknown_identifier` | `Boundary Condition` | `has_uuid_in__contiguous_array__u64` | Pass `IDENTIFIER__UNKNOWN__u64`, assert `false`. |
| `hashing__dehash_u64_collision_resolution` | `Round Trip Check` | `dehash_identitier_u64_in__contigious_array` | Allocate two UUIDs that hash to the same bucket, verify both are dehashable to distinct pointers. |

### 4.4 Test impact summary

**Medium.** No existing tests break. However, substantial new test coverage is needed for the u64 code path (which is entirely untested) and for the full-array / invalid-identifier edge cases. A phased approach is recommended: (1) add NULL-guard tests for the allocation functions, (2) add full-array and hash-bucket tests for UUID resolution, (3) add invalid-identifier and round-trip tests for the u64 dehash path.

---

## 5. Blast Radius Summary

- **Files needing changes:** 2
  - `core/include/serialization/hashing.h` — add NULL guards in 4 `static inline` functions (lines 134, 150, 230, 247).
  - `core/source/serialization/hashing.c` — fix 2 UUID-resolution functions (lines 86–99, 101–114) and add invalid-identifier guard to 1 dehash function (line 159).
- **Behavior-preserving for current callers:** No. The fixes change observable behavior:
  - The four allocation functions will now return NULL (instead of crashing) when the array is full.
  - `get_next_available__uuid_in__contiguous_array[_uuid_64]` will return `IDENTIFIER__UNKNOWN__u32/u64` (instead of a garbage UUID) when the array is full, and will use the correct hash bucket for probing.
  - `dehash_identitier_u64_in__contigious_array` will return NULL for `IDENTIFIER__UNKNOWN__u64` (instead of potentially returning a deallocated slot).
- **Phased approach needed:** Recommended. The fixes are interdependent: fixing the NULL guards (Category A) without fixing the full-array check (Category B) means the allocation functions will correctly return NULL, but the garbage UUID from Category B could still cause issues if `get_next_available__uuid_in__contiguous_array` is called directly. The three categories should be fixed together, but tests can be added incrementally.
- **De facto contracts invalidated:** None of practical consequence. No code in the current codebase calls these functions in a way that depends on the broken behavior. The `hashing__allocation_returns_null_when_full` test already validates the correct sibling function's NULL-return contract, which the broken functions should emulate.
- **Coupling concerns:** The four allocation functions are `Coupled` to `get_next_available__random_allocation_in__contiguous_array` / `_uuid_64` via the shared NULL-return contract. The `Single Source of Truth (SSOT)` for the NULL-guard pattern is already established in `allocate_serialization_header_with__this_uuid` and `allocate_serialization_header_with__this_uuid__u64`. The fix restores consistency across all allocation functions. The `get_next_available__uuid_in__contiguous_array` functions are `Coupled` to `poll_for__uuid_collision` / `poll_for__uuid_collision__uuid_64` via the `INDEX__UNKNOWN__u32` **Sentinel** convention — the fix ensures this convention is respected.
