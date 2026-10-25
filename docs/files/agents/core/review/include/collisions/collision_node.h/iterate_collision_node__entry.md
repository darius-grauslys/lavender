iterate_collision_node__entry — core/include/collisions/collision_node.h

Advances a caller-held cursor backward through the linked list of collision node entries by one step, updating the cursor in place and returning the new (previous) entry.

Pre-conditions:
1. p_collision_node__entry must be a non-null pointer to a valid Collision_Node_Entry ** (the cursor handle).
2. *p_collision_node__entry must be non-null at call time; the function dereferences it to read p_previous_entry, so a NULL cursor will cause undefined behavior (null dereference). End-of-iteration checking is the caller's responsibility.
3. The Collision_Node_Entry pointed to by *p_collision_node__entry must be a live, properly initialized entry whose p_previous_entry field is either a valid pointer to the prior entry in the list or NULL (signaling the head of the list).

Post-conditions:
1. *p_collision_node__entry is mutated to point to the previous entry (the entry that was p_previous_entry before the call).
2. The return value is identical to the updated *p_collision_node__entry.
3. If the cursor was on an entry whose p_previous_entry was NULL (i.e., the head of the list), both *p_collision_node__entry and the return value become NULL, signaling end-of-iteration to the caller.

Correctness Verdict: Correct

Semantic Alignment:
The implementation faithfully realizes the semantic intent of a backward iteration step. It dereferences the cursor, reads the p_previous_entry pointer from the current entry, stores it back into the cursor, and returns it. This is exactly what an iterator step — "move to the previous entry" — should do. The Collision_Node_Entry struct (defined in defines.h) has exactly two fields: uuid_of__hitbox__u32 and p_previous_entry. This function only touches p_previous_entry, which is correct — the uuid field is not relevant to iteration.

Implementation Correctness:
Type compatibility — p_collision_node__entry is Collision_Node_Entry **; *p_collision_node__entry is Collision_Node_Entry *; (*p_collision_node__entry)->p_previous_entry is struct Collision_Node_Entry_t *. The typedef Collision_Node_Entry is an alias for struct Collision_Node_Entry_t, so these types are identical. The return type Collision_Node_Entry * matches the stored value. No implicit conversions, no truncation.
No undefined behavior — no pointer arithmetic, no type punning, no out-of-bounds access. The only potential null-dereference concern (calling when *p_collision_node__entry is NULL) is a caller-side contract violation, not a defect in this function's implementation. The function performs a single level of dereference on the cursor and a single member access on the entry, both guarded by the pre-condition that *p_collision_node__entry is non-null.
Validation — no validation is needed within this function. It is a low-level static inline iterator; checking the return value for NULL is how callers detect end-of-iteration. Adding a null check inside would contradict the performance-oriented inline pattern and would not align with how the companion function iterate_entities_in__collision_node_entry is expected to be used.

Side Effects:
Mutates the caller's cursor: *p_collision_node__entry is overwritten with the previous entry pointer. No other memory is touched and no globals are read or written. The return value aliases the same pointer stored into *p_collision_node__entry.

Notes:
This function is part of Lavender's pool-based collision architecture. Collision_Node_Pool maintains a fixed-size array of Collision_Node_Entry objects that are linked via p_previous_entry to form a singly-linked list (tail to head). iterate_collision_node__entry walks this list backward from the tail, which is consistent with the "initialization = pool cleanup" pattern used elsewhere in Lavender — entries are returned to the pool by unlinking, not by freeing.
