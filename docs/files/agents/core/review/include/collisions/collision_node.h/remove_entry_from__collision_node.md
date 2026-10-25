# remove_entry_from__collision_node

## 1. Header
- **Function name**: `remove_entry_from__collision_node`
- **File of origin**: `core/source/collisions/collision_node.c`

## 2. Semantic
Removes the `Collision_Node_Entry` matching the given `uuid__u32` from the singly-linked (backward-traversing) entry list of `p_collision_node`, unlinking it from its predecessor and returning the entry to its owning pool.

## 3. Pre-conditions
1. `p_collision_node` must be non-null (validated; the function early-returns on null).
2. `p_collision_node_pool` is expected to be valid and to be the pool that owns entries linked into `p_collision_node`; it is NOT validated by this function (only by the callee `release_collision_node_entry_from__collision_node_pool` in debug builds).
3. `uuid__u32` is the identifier of a previously-added hitbox entry; if no entry with this uuid is present the function early-returns after logging an error.
4. The entries linked via `p_linked_list__collision_node_entries__tail` form a singly-linked list following `p_previous_entry`, terminating in a null pointer.

## 4. Post-conditions
1. If `p_collision_node` was null: no state was modified; an error was logged.
2. If no matching entry was found: no state was modified; an error was logged.
3. If the matching entry was the tail (or the only entry, i.e. `p_collision_node_entry == p_collision_node_entry__parent`): `p_collision_node->p_linked_list__collision_node_entries__tail` is advanced to `entry->p_previous_entry`, bypassing the removed entry.
4. Otherwise: `p_collision_node_entry__parent->p_previous_entry` is set to `entry->p_previous_entry`, unlinking the removed entry from the middle of the list while preserving the rest of the chain.
5. In the success cases (3 & 4) the removed entry is passed to `release_collision_node_entry_from__collision_node_pool`, which re-initializes it to default/known-free state (uuid = `IDENTIFIER__UNKNOWN__u32`, `p_previous_entry = 0`) so it may be returned to the free pool — consistent with Lavender's non-RAII "initialization = pool cleanup" semantics.
6. The function returns no value (`void`).

## 5. Correctness Verdict
- Correct

## 6. Semantic Alignment
The implementation faithfully fulfills the semantic intent: it traverses the backward-linked list starting at the tail, locates the entry by uuid, unlinks it via the appropriate branch (tail vs. middle/interior), and releases the entry back to its pool. All fields of `Collision_Node_Entry` are re-initialized by `initialize_collision_node_entry` (called from the release helper), with no reordering or omission.

One minor semantic gap: `p_collision_node_pool` is neither validated nor documented as being permitted to be null by this caller, even though the pool pointer flows into the release helper (which itself null-checks in debug). Since the pool pointer is required for the release to be meaningful, callers must always supply a valid pool; this is a caller-responsibility validation matter rather than a semantic defect.

## 7. Implementation Correctness
- **Type compatibility**: `p_collision_node_entry__parent` and `p_collision_node_entry` are both `Collision_Node_Entry *`; the comparison `p_collision_node_entry == p_collision_node_entry__parent` is between identical types. Assignments to `p_linked_list__collision_node_entries__tail` and `p_previous_entry` are from `Collision_Node_Entry *` to `Collision_Node_Entry *`. No implicit conversions or truncation. `uuid__u32` (`Identifier__u32`/`uint32_t`) is compared against `p_collision_node_entry->uuid_of__hitbox__u32` (`Identifier__u32`) with `==` — exact type match, no integer promotion concerns for equal-width unsigned types.
- **Undefined behavior**: No null dereference occurs on the happy path. The initial `p_collision_node_entry` is read from `p_linked_list__collision_node_entries__tail`, which may itself be null; however, the `while (p_collision_node_entry)` guard prevents dereferencing a null pointer. Pointer arithmetic is only performed inside the debug-only check in `release_collision_node_entry_from__collision_node_pool` (`p_collision_node_entry - p_collision_node_pool->collision_node_entries`), guarded by `#ifndef NDEBUG`, and only after a null check on both operands.
- **Null handling**: `p_collision_node` is null-checked before use. `p_collision_node_pool` is not checked here but is checked in the callee (debug only). If `p_collision_node_pool` were null in a release build, the release helper's debug checks are compiled out and `initialize_collision_node_entry` would be called without further pool use — no dereference of the pool occurs on that path, so no UB, only a silently-released entry.
- **Validation**: Validation is appropriate to the function's role — null `p_collision_node` and missing-entry cases are handled with error logging and early return. Absent validation of `p_collision_node_pool` is acceptable as a caller responsibility, matching the pattern used by the sibling `add_entry_to__collision_node`.

## 8. Side Effects
- Mutates `p_collision_node`: the `p_linked_list__collision_node_entries__tail` pointer is rewritten when the removed entry is the tail (or the sole entry); otherwise a predecessor entry's `p_previous_entry` is rewritten to skip the removed entry.
- Calls `release_collision_node_entry_from__collision_node_pool`, which (Lavender-style) re-initializes the removed `Collision_Node_Entry` to `IDENTIFIER__UNKNOWN__u32` / null `p_previous_entry`, effectively returning it to the pool's free state.
- Emits debug/log output via `debug_error` on the null-`p_collision_node` and missing-entry early-return paths.
- No allocation, no I/O beyond logging, no modification of global state outside the collision node and entry pool.
