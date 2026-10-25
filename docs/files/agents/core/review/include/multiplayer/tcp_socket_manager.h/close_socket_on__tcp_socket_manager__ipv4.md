close_socket_on__tcp_socket_manager__ipv4 — core/source/multiplayer/tcp_socket_manager.c, lines 178-221

Removes a TCP_Socket from the TCP_Socket_Manager's active pool using a swap-with-tail compaction of the ptr_array_of__tcp_sockets indirection array, then resets the socket's data to a deallocated state and decrements the connection counter.

Pre-conditions:
1. p_tcp_socket_manager must be non-null and previously initialized via initialize_tcp_socket_manager (which zeroes ptr_array_of__tcp_sockets and initializes all tcp_sockets entries as deallocated).
2. p_tcp_socket must point within the p_tcp_socket_manager->tcp_sockets contiguous array (validated only in debug builds via pointer arithmetic).
3. p_tcp_socket must be a valid, currently-allocated socket that is registered in ptr_array_of__tcp_sockets. If it is not found in the indirection array, the function exhibits undefined behavior (see Implementation Correctness).
4. quantity_of__connections must be > 0 to avoid unsigned underflow on the final decrement.

Post-conditions:
1. The pointer to p_tcp_socket is removed from ptr_array_of__tcp_sockets.
2. If the removed socket was not the last active entry in the indirection array, the last active socket's pointer is moved into the freed slot (swap-with-tail compaction).
3. The last active slot in ptr_array_of__tcp_sockets is set to NULL.
4. p_tcp_socket is zeroed and its serialization header is marked as deallocated via initialize_tcp_socket_as__deallocated.
5. quantity_of__connections is decremented by 1.

Correctness Verdict: Incorrect

Semantic Alignment:
The function's semantic intent is to remove a socket from the manager's active pool using swap-with-tail compaction on the pointer indirection array, then reset the socket to a deallocated state. The swap-with-tail logic itself (copying the last active pointer into the freed slot, then nullifying the last slot) is semantically correct and matches the pattern used by release_entity_from__entity_manager in the entity manager. The call to initialize_tcp_socket_as__deallocated correctly resets the socket to its initial/deallocated state, consistent with the Lavender convention that "initialization" means cleaning up to default conditions rather than RAII resource acquisition.

However, the implementation fails to uphold its semantic contract because it does not validate that the target socket was actually found in the indirection array before proceeding with the compaction logic. This means the function can operate on uninitialized pointers, violating the post-conditions when the socket is not present in the ptr array.

Implementation Correctness:
- Type compatibility: Parameter types match correctly. The pointer arithmetic (p_tcp_socket - p_tcp_socket_manager->tcp_sockets) uses unsigned long for the index, which is compatible with the comparison against MAX_QUANTITY_OF__TCP_SOCKETS. No implicit conversions or truncation in the core logic.

- Undefined behavior — CRITICAL BUG: The local variables p_ptr_tcp_socket__being_release and p_ptr_tcp_socket__last are declared without initialization:
  TCP_Socket **p_ptr_tcp_socket__being_release;
  TCP_Socket **p_ptr_tcp_socket__last;

  If p_tcp_socket is NOT found in ptr_array_of__tcp_sockets (the matching branch never executes), p_ptr_tcp_socket__being_release remains uninitialized. It is then used in the comparison (p_ptr_tcp_socket__being_release != p_ptr_tcp_socket__last) and potentially dereferenced (*p_ptr_tcp_socket__being_release = *p_ptr_tcp_socket__last), causing undefined behavior.

  Similarly, if no non-null entries exist in ptr_array_of__tcp_sockets (the manager has zero active connections), the loop breaks immediately on the first null entry and p_ptr_tcp_socket__last is never assigned. It is then read in the comparison and the conditional (if (p_ptr_tcp_socket__last)), and potentially dereferenced, also causing undefined behavior.

- Undefined behavior — loop break on null: The loop breaks on the first null entry in ptr_array_of__tcp_sockets (the else branch). This assumes the indirection array is always compact (all non-null entries precede all null entries). While allocate_tcp_socket_from__tcp_socket_manager fills the first available null slot (maintaining compactness under normal operation), this assumption is fragile. If the array ever becomes fragmented, the loop will terminate before finding p_tcp_socket, leaving p_ptr_tcp_socket__being_release uninitialized and triggering the UB described above.

- Unsigned underflow: quantity_of__connections-- is called unconditionally, even if p_tcp_socket was not found in the ptr array (no removal occurred) or if the manager had zero connections. Since quantity_of__connections is a Quantity__u32 (uint32_t), this can silently underflow to a very large value.

- No validation after loop: The function does not check whether p_ptr_tcp_socket__being_release was ever assigned before using it. A correct implementation would either initialize both pointers to NULL and check after the loop, or verify that the socket was found.

- Comparison with correct pattern: The entity manager's release_entity_from__entity_manager uses a maintained cursor (p_ptr_entity__next_in_ptr_array) to track the end of active entries, and breaks out of the loop immediately upon finding the target entity. This avoids the uninitialized-variable problem entirely. The TCP socket manager lacks such a cursor and instead scans for the last non-null entry, introducing the UB risk.

Side Effects:
1. Mutates ptr_array_of__tcp_sockets: Removes the pointer to p_tcp_socket from its slot; if swap-with-tail is performed, copies the last active pointer into the freed slot and nullifies the last slot.
2. Mutates p_tcp_socket (via initialize_tcp_socket_as__deallocated): Zeroes the entire TCP_Socket struct and marks its serialization header as deallocated (UUID set to IDENTIFIER__UNKNOWN__u32).
3. Mutates quantity_of__connections: Decrements by 1.
