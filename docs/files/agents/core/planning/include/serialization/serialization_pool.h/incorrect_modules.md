# Planning: serialization_pool.h — Incorrect Modules

**Review source:** `agents/core/review/include/serialization/serialization_pool.h/incorrect_modules.md`

**Source files reviewed (read-only):**
- `core/include/serialization/serialization_pool.h`
- `core/include/serialization/hashing.h`
- `core/include/serialization/serialization_header.h`
- `core/source/serialization/hashing.c`
- `core/source/serialization/serialization_header.c`
- `core/include/defines.h` (`Serialization_Pool`, `Serialization_Header`)
- `tests/core/source/serialization/test_suite_serialization_hashing.c`

**Note on missing implementation:** there is **no** `core/source/serialization/serialization_pool.c`; three of the five flagged functions are declaration-only.

---

## 1. Problem Identification

Five functions in `serialization_pool.h` are flagged **Incorrect**. They fall into two defect classes: (A) a shared **Boundary Condition** error in the two `static inline` wrappers, and (B) a **Stub-real divergence** where three declared functions have no definition.

### 1.1 `dehash_from__serialization_pool` — Boundary Condition (byte-count passed as element-count)

The `static inline` function delegates to `dehash_identitier_u32_in__contigious_array`, passing `quantity_of__pool_elements * size_of__element` as the `length_of__p_serialization_headers` argument. That parameter is the **number of elements**, not a byte length, as every callee confirms:

- `poll_for__uuid_collision` computes `identifier__u32 % length_of__p_serialization_headers` for a starting bucket index — only valid as an element count.
- `get_p_serialization_header_from__contigious_array` performs `index >= length_of__p_serialization_headers` as the **Boundary Condition** and uses `size_of__struct * index` for pointer arithmetic — both treat it as element count.
- `initialize_serialization_header__contiguous_array` uses it as the loop iteration count.

Multiplying by `size_of__element` inflates the length by that factor (e.g., 1600 instead of 100 for 100 elements of 16 bytes). The modulo, bounds check, and pointer arithmetic then compute indices/offsets far past the allocated array → **out-of-bounds reads / undefined behavior**. Correct argument is `quantity_of__pool_elements` alone.

### 1.2 `allocate_by_hash_in__serialization_pool` — Translation Gap + Boundary Condition + State Desync

Three defects in one `static inline` function:

1. **Translation Gap / Mode Confusion:** Named "allocate_by_hash" but delegates to `dehash_identitier_u32_in__contigious_array`, a **lookup** that finds an *existing* header with the given UUID — it does not find a *free* slot. The correct allocation pattern (sibling `allocate_serialization_header_with__this_uuid` in `hashing.h`) is `get_next_available__allocation_in__contiguous_array` (finds a deallocated slot via `poll_for__uuid_collision`) followed by the `ALLOCATE_P` macro.
2. **Boundary Condition (shared with 1.1):** the same incorrect `quantity_of__pool_elements * size_of__element` length is passed, producing the same out-of-bounds access.
3. **State Desync:** it directly assigns `p_serialization_header->uuid = uuid__u32` (a redundant no-op, since `dehash` already matched that UUID) instead of using `ALLOCATE_P`, which calls `initialize_serialization_header` and sets **both** `size_of__struct` and `uuid`. The direct assignment leaves `size_of__struct` stale — a **State Desync** between the header metadata and the pool's `size_of__element`.

### 1.3 `initialize_serialization_pool` — Stub-real divergence (no implementation)

Declared (`serialization_pool.h`, lines 8–11) but never defined; no `serialization_pool.c` exists. Any call site is an undefined reference at link time. Expected implementation: set `quantity_of__pool_elements` and `size_of__element` on the pool, then delegate to `initialize_serialization_header__contiguous_array(p_headers, quantity_of__pool_elements, size_of_of__element)` to clear every header to `IDENTIFIER__UNKNOWN__u32`.

### 1.4 `allocate_from__serialization_pool` — Stub-real divergence (no implementation) + signature gap

Declared (lines 13–14) but never defined. Any call site is an undefined reference. The expected pattern is to find a free slot (`get_next_available_p_serialization_header`) then apply `ALLOCATE_P`. **Design gap:** the declared signature takes only `p_serialization_pool` — it has **no UUID and no randomizer parameter**, yet allocation must assign a non-`IDENTIFIER__UNKNOWN__u32` UUID. The signature must be reconciled with this requirement (see 3.4).

### 1.5 `release_from__serialization_pool` — Stub-real divergence (no implementation)

Declared (lines 16–18) but never defined. Expected pattern (per the `DEALLOCATE_P` macro): call `initialize_serialization_header_for__deallocated_struct` on the target header, setting `uuid = IDENTIFIER__UNKNOWN__u32` and preserving `size_of__struct`.

---

## 2. Impact Assessment

### 2.1 Caller analysis

A search of `./core/include`, `./core/source`, and `./tests` finds **no existing callers** of any of the five flagged functions:
- The three non-inline functions cannot be called at all (link-time undefined reference).
- The two `static inline` functions are defined in the header but referenced by no translation unit.

### 2.2 Shared-callee impact (no collateral)

`dehash_identitier_u32_in__contigious_array` (`hashing.c`) is **correctly used** elsewhere — e.g., `has_uuid_in__contiguous_array` (`hashing.h`) and `test_suite_serialization_hashing.c`, which pass a correct element count directly. Those callers are unaffected: the bug is confined to the two pool wrappers that compute the length incorrectly. The hashing layer itself needs no change.

### 2.3 Assumptions coupled to broken behavior

No code relies on the broken behavior (zero callers), so:
- Fixing the **Boundary Condition** in both inline wrappers invalidates no caller assumption — nothing depends on the inflated length.
- Implementing the three missing functions only adds callable surface; it breaks no existing caller.
- Rewriting `allocate_by_hash_in__serialization_pool` from "lookup + redundant uuid write" to "find free slot + `ALLOCATE_P`" changes observable behavior, but since it is never called, no existing behavior is invalidated.

### 2.4 Representation Invariant / SSOT

The **Representation Invariant** of `Serialization_Pool` is: `quantity_of__pool_elements` = element count, `size_of__element` = per-element byte size. The two inline wrappers violate it by conflating the two when forming the length argument, breaking the **Single Source of Truth (SSOT)** between the pool struct and the hashing layer's element-count contract. Correcting them restores that alignment.

---

## 3. Resolution Assessment

### 3.1 Fix `dehash_from__serialization_pool` — Boundary Condition

**Change:** in `serialization_pool.h`, replace the second argument to `dehash_identitier_u32_in__contigious_array`
from `p_serialization_pool->quantity_of__pool_elements * p_serialization_pool->size_of__element`
with `p_serialization_pool->quantity_of__pool_elements`.

**Callers:** none. **Docs/tests:** add coverage (see 4.2).

### 3.2 Fix `allocate_by_hash_in__serialization_pool` — Translation Gap + Boundary Condition + State Desync

**Change:** rewrite the `static inline` body to mirror `allocate_serialization_header_with__this_uuid`:
1. Call `get_next_available__allocation_in__contiguous_array(p_serialization_pool->p_headers, p_serialization_pool->quantity_of__pool_elements, uuid__u32)` — correct element count, and it finds a *free* slot (or returns the already-matching header on collision).
2. If non-null, apply `ALLOCATE_P(p_serialization_header, uuid__u32)` so both `uuid` and `size_of__struct` are set consistently.

This resolves all three defects at once: correct callee semantics (allocation, not lookup), correct element-count length, and full header initialization (no stale `size_of__struct`).

**Callers:** none. **Docs/tests:** add coverage (see 4.2).

### 3.3 Implement `initialize_serialization_pool` — Stub-real divergence

**Change:** in a new `core/source/serialization/serialization_pool.c`:
1. `p_serialization_pool->quantity_of__pool_elements = quantity_of__pool_elements;`
2. `p_serialization_pool->size_of__element = size_of__element;`
3. Delegate: `initialize_serialization_header__contiguous_array(p_serialization_pool->p_headers, quantity_of__pool_elements, size_of__element);`

**Precondition note:** per the non-RAII convention, the caller must have already pointed `p_headers` at pre-allocated memory large enough for `quantity_of__pool_elements * size_of__element` bytes. This is a **Precondition**, not a defect.

**Callers:** none. **Docs/tests:** add coverage (see 4.2).

### 3.4 Implement `allocate_from__serialization_pool` — Stub-real divergence + signature gap

**Change:** in the new `serialization_pool.c`:
1. Find a free slot: `get_next_available_p_serialization_header(p_serialization_pool->p_headers, p_serialization_pool->quantity_of__pool_elements)`.
2. If non-null, apply `ALLOCATE_P(p_serialization_header, <uuid>)` to set both `uuid` and `size_of__struct`.

**Signature gap — must be resolved before implementation:** the current declaration `Serialization_Header *allocate_from__serialization_pool(Serialization_Pool *)` has no source for the UUID. Options (pick one; this is a design decision, not a mechanical fix):
- **(a) Add a randomizer parameter** — `Repeatable_Psuedo_Random *p_randomizer`, mirroring `allocate_serialization_header`; use `get_next_available__random_allocation_in__contiguous_array` for a random UUID. This is the pattern already proven in `hashing.h`.
- **(b) Add a caller-supplied UUID parameter** — like `allocate_by_hash_in__serialization_pool`, letting the caller choose the UUID.
- **(c) Keep the signature and derive a UUID from pool-local state** (e.g., a monotonic counter or per-pool randomizer field). This would require adding a field to `Serialization_Pool` — a **Representation Invariant** change to the struct, so it is the heaviest option.

Recommended: **(a)** for a "next available" semantic (matches the function name and the `hashing.h` idiom), or **(b)** if callers should dictate UUIDs. The header declaration must be updated to match whichever is chosen.

**Callers:** none. **Docs/tests:** add coverage (see 4.2).

### 3.5 Implement `release_from__serialization_pool` — Stub-real divergence

**Change:** in the new `serialization_pool.c`, apply `DEALLOCATE_P(p_serialization_header)` (→ `initialize_serialization_header_for__deallocated_struct`), which sets `uuid = IDENTIFIER__UNKNOWN__u32` and preserves `size_of__struct`.

**Callers:** none. **Docs/tests:** add coverage (see 4.2).

### 3.6 New source file + build

Create `core/source/serialization/serialization_pool.c` housing the three definitions (3.3–3.5). Add it to the serialization build so the new translation unit is compiled and linked. (The two inline functions in 3.1–3.2 stay in the header.)

---

## 4. Test Verification Checklist

### 4.1 Existing coverage
- `test_suite_serialization_hashing.c` exercises `dehash_identitier_u32_in__contigious_array`, `allocate_serialization_header_with__this_uuid`, and `get_next_available__allocation_in__contiguous_array` — but **only at the hashing layer** with direct element-count arguments.
- No test file exists for the `serialization_pool.h` wrappers, and no existing test asserts on the broken behavior (there are no callers).

### 4.2 New tests needed (additive)

| Test | Technique | Rationale |
|------|-----------|-----------|
| `pool__dehash_no_out_of_bounds` | `Property Based Testing` + `Fuzzing` | Vary element count and `size_of__element`; assert lookups stay in bounds and return the correct header (guards the 3.1 element-count fix). |
| `pool__allocate_dehash_round_trip` | `Round Trip Check` | Allocate then dehash by UUID; returned pointer must match. |
| `pool__allocate_by_hash_finds_free_slot` | `Equivalence Check` | Assert `allocate_by_hash_in__serialization_pool` is equivalent to `allocate_serialization_header_with__this_uuid` (finds a free slot, not an existing match). |
| `pool__allocate_preserves_size_of__struct` | `Property Based Testing` | After allocation, `size_of__struct == size_of__element` (covers the 3.2 **State Desync** fix). |
| `pool__initialize_clears_all_headers` | `Round Trip Check` | After `initialize_serialization_pool`, every header is `IDENTIFIER__UNKNOWN__u32` with correct `size_of__struct`. |
| `pool__release_returns_to_deallocated` | `Round Trip Check` | Allocate then release; header returns to `IDENTIFIER__UNKNOWN__u32`, `size_of__struct` unchanged. |
| `pool__full_lifecycle_reuse` | `Round Trip Property` | initialize → allocate → dehash → release → re-allocate; the released slot must be reusable. |

### 4.3 Test blast radius
**Low.** No existing tests reference the pool functions; all new tests are additive. The hashing-layer suite stays valid because the hashing functions are unchanged. A `Mutation Testing` pass on the two inline wrappers is worthwhile to confirm the element-count fix is actually asserted (a reverted `* size_of__element` should be caught).

---

## 5. Blast Radius Summary

- **Files needing changes:** 2
  - `core/include/serialization/serialization_pool.h` — fix the two inline wrappers (3.1, 3.2); optionally adjust the `allocate_from__serialization_pool` declaration per the 3.4 signature decision.
  - `core/source/serialization/serialization_pool.c` — **new file** implementing 3.3–3.5; add to the build.
- **Behavior-preserving for current callers:** Yes — there are no current callers of any of the five functions.
- **Phased approach needed:** No — changes are isolated to the serialization pool module; the new `.c` and header edits do not touch other modules.
- **De facto contracts invalidated:** None. Nothing depends on the broken behavior; the inflated length produced undefined behavior, not a relied-upon contract.
- **Open design decision:** the 3.4 signature gap (no UUID/randomizer source for `allocate_from__serialization_pool`) must be resolved before implementation; all other fixes are mechanical.
- **Coupling:** the two inline wrappers are `Coupled` to the hashing layer through the shared `length_of__p_serialization_headers` element-count convention; passing the correct element count restores **SSOT** with `Serialization_Pool.quantity_of__pool_elements`.
