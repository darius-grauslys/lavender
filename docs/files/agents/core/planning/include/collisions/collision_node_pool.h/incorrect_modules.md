# Planning: collision_node_pool.h — Incorrect Modules

**Review source:** `agents/core/review/include/collisions/collision_node_pool.h/incorrect_modules.md`

**Source files reviewed (read-only):**
- `core/include/collisions/collision_node_pool.h`
- `core/source/collisions/collision_node_pool.c`
- `core/include/collisions/collision_node.h`
- `core/source/collisions/collision_node.c`
- `core/include/defines.h` (Collision_Node, Collision_Node_Pool struct definitions)
- `core/include/serialization/serialization_header.h`
- `tests/core/source/collisions/test_suite_collisions_collision_node_pool.c`

---

## 1. Problem Identification

### `release_collision_node_from__collision_node_pool` — `core/source/collisions/collision_node_pool.c`

**Defect 1 — Incomplete cleanup (State Desync):**
The release function resets `_serialization_header` to the deallocated sentinel (`IDENTIFIER__UNKNOWN__u64`) but omits resetting `p_linked_list__collision_node_entries__tail` to `0`. The allocation path (`allocate_collision_node_from__collision_node_pool` → `initialize_collision_node`) sets both fields. The sibling `release_collision_node_entry_from__collision_node_pool` calls `initialize_collision_node_entry` which fully resets all entry fields. This violates the pool's **Representation Invariant**: a deallocated node must be indistinguishable from an initialized (never-allocated) node. The stale tail pointer constitutes a **State Desync** between the serialization header (says deallocated) and the linked-list field (still points to a live or freed entry).

**Defect 2 — Missing null-precondition checks (Boundary Condition):**
In debug mode, neither `p_collision_node_pool` nor `p_collision_node` is null-checked before dereference. If either is null, the pointer subtraction `p_collision_node - p_collision_node_pool->collision_nodes` is undefined behavior. The sibling entry-release function null-checks both parameters before its bounds check. This is a missing **Precondition** guard.

---

## 2. Impact Assessment

### Callers and coupled assumptions

| Caller / Consumer | Coupling to broken behavior |
|---|---|
| `allocate_collision_node_from__collision_node_pool` | Calls `initialize_collision_node` which resets the tail on allocation, masking the stale-pointer defect. No direct break on reallocation, but the node is in an inconsistent state between release and next allocation. |
| `poll_for__collisions_within_this__collision_node` (collision_node.c) | Iterates `p_linked_list__collision_node_entries__tail`. If invoked on a released-but-not-reallocated node (e.g., during world teardown), it would follow a dangling pointer into freed/reused entry slots. |
| `get_p_hitbox_aabb_at__vector_3i32F4_from__collision_node` (collision_node.c) | Same iteration pattern; same dangling-pointer risk. |
| `get_quantity_of__entries_in__collision_node` (collision_node.c) | Iterates the linked list; would return a non-zero count for a "deallocated" node, violating the **Invariant** that deallocated state implies no active entries. |
| `remove_entry_from__collision_node` (collision_node.c) | Reads and writes `p_linked_list__collision_node_entries__tail`. If called on a stale released node, it would corrupt entry state. |
| `Global_Space.p_collision_node` (defines.h) | Holds a raw pointer to a pool node. During global-space disposal the node is released; any subsequent access via this pointer before reallocation sees the inconsistent state. |

### How correcting invalidates assumptions

- The **de facto contract** currently in place: callers may assume that a deallocated node's tail is still valid because no code path today exercises the released-but-not-reallocated window. Adding the tail reset makes the release function a true cleanup-to-initial-conditions operation, which is safe but changes observable state in that window.
- No caller today relies on the stale tail being non-null after release (the allocation path overwrites it). The fix is therefore **behavior-preserving** for all current callers in normal operation; it only corrects the error/teardown path.

---

## 3. Resolution Assessment

### Change 1: Add tail-pointer reset to release function

In `release_collision_node_from__collision_node_pool`, after the serialization header reset, add:

```c
p_collision_node->p_linked_list__collision_node_entries__tail = 0;
```

Alternatively (preferred for **DRY** and **Single Source of Truth**): extract the full node reset into a helper (e.g., `reset_collision_node_to_initial(Collision_Node*)`) that both the release path and `initialize_collision_node` can share, ensuring the **Representation Invariant** is enforced from one code path.

### Change 2: Add null-precondition guards in debug mode

Prepend to the function body (inside `#ifndef NDEBUG`):

```c
if (!p_collision_node_pool) {
    debug_error("release_collision_node_from__collision_node_pool, p_collision_node_pool == 0.");
    return;
}
if (!p_collision_node) {
    debug_error("release_collision_node_from__collision_node_pool, p_collision_node == 0.");
    return;
}
```

This mirrors the sibling `release_collision_node_entry_from__collision_node_pool` and closes the **Boundary Condition** gap.

### Caller updates

- **None required.** The fix is internal to the release function. All existing callers pass valid pool/node pointers and do not depend on the stale tail surviving release.

### Documentation / spec updates

- Update the postcondition in `collision_node_pool.h.spec.md` (section 1.5.5) to explicitly state: "On return, `p_collision_node->p_linked_list__collision_node_entries__tail == 0`."
- Update the precondition list to include null-pointer guards.

---

## 4. Test Verification Checklist

### Existing tests

| Test | Asserts on broken behavior? | Invalidated by fix? |
|---|---|---|
| `collision_node_pool__release_node__marks_deallocated` | Checks only `is_collision_node__allocated == false`. Does NOT assert on tail. | No — still passes. |
| `collision_node_pool__release_and_reallocate_node__works` | Release → reallocate cycle. Relies on allocation resetting tail (already correct). | No — still passes. |

No existing test asserts the stale tail is non-null after release, so no assertion is invalidated.

### New tests needed

1. **Post-release tail reset (Property Based Testing):**
   Allocate a node, add one or more entries via `add_entry_to__collision_node`, release the node, assert `p_node->p_linked_list__collision_node_entries__tail == 0`. This verifies the **Representation Invariant** directly.

2. **Round Trip Check (allocate → add entries → release → allocate):**
   After the full cycle, assert that `get_quantity_of__entries_in__collision_node` returns 0 on the reallocated node, confirming no stale entries leak across cycles.

3. **Null-pointer guards (Boundary Condition / Fuzzing):**
   Call `release_collision_node_from__collision_node_pool(0, valid_node)` and `(valid_pool, 0)` in a debug build; assert no crash (debug_error path taken).

### Blast radius for tests: **Low**
- Two new test functions added to the existing suite. No existing assertions change. No phased approach needed.

---

## 5. Blast Radius Summary

| Metric | Assessment |
|---|---|
| Files requiring changes | 1 source file (`core/source/collisions/collision_node_pool.c`), 1 test file, optionally 1 spec file |
| Behavior-preserving for current callers? | Yes — no caller depends on stale tail surviving release |
| Phased approach needed? | No — single-function fix, atomic |
| De facto contracts invalidated? | None — the stale-tail state was never a relied-upon contract; it was an oversight |
