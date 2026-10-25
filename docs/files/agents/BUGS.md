# Core Code Bugs

Bugs found in `core/` during the 2026-08-25 module-doc review (audio, collisions, sort, entity; client, world, multiplayer, game_action). Line numbers as of that date — re-verify before fixing.

All entries **open**, none verified against a running build.

## 1. Collision resolver polls EAST twice, never SOUTH

- **Where:** `core/source/collisions/collision_resolver_aabb.c` — in `poll_collision_resolver_aabb`, the SOUTH branch (~line 231).
- **What:** the guard checks `is_local_space__active(p_local_space->p_local_space__south)` but the node polled is `get_p_collision_node_from__local_space(p_local_space->p_local_space__east)`.
- **Impact:** the east neighbor's collision node is polled twice and the south neighbor's never is; entities moving south past a chunk edge can miss collisions with the south neighbor's hitboxes.
- **Fix:** poll `p_local_space->p_local_space__south` in that branch.

## 2. `heap_sort__opaque`: header and implementation disagree on parameter order

- **Where:** `core/include/sort/heap_sort__opaque.h` vs `core/source/sort/heap_sort__opaque.c`.
- **What:** the header declares `(p_context, p_ptr_array, size_of__type, size_of__array, ...)`; the implementation defines `(p_context, p_array, length_of__array, size_of__type, ...)`. Parameter types are identical (`Quantity__u32`), so this compiles silently.
- **Impact:** any caller following the header passes (type-size, array-length) and the callee reads (length, type-size) — the two values are swapped at runtime, producing out-of-bounds reads/writes or a no-op sort.
- **Fix:** rename/reorder the `.c` parameters to match the header (or the header to match the `.c`), and add a static assertion or a unit test.

## 3. `Sort_List_Manager` available-counters are swapped

- **Where:** `core/include/sort/sort_list/sort_list_manager.h` — `get_quantity_of__available_sort_lists_in__sort_list_manager` and `get_quantity_of__available_sort_nodes_in__sort_list_manager`.
- **What:** the "available lists" counter subtracts `quantity_of__allocated_sort_nodes` (should be lists); the "available nodes" counter subtracts `quantity_of__allocated_sort_lists` (should be nodes).
- **Impact:** capacity checks in `allocate_sort_list_in__sort_list_manager` are wrong — allocation can succeed past real capacity or fail early.
- **Fix:** swap the two subtrahends.

## 4. `release_sort_nodes_in__sort_list_manager` releases the wrong nodes

- **Where:** `core/source/sort/sort_list/sort_list_manager.c` (~lines 173-187).
- **What:** three problems in one function:
  1. Iterates from index 0 instead of the start of the block being released (`p_sort_nodes` is ignored).
  2. Bounded by `SORT_LIST__MAXIMUM_QUANTITY_OF` (64) instead of `SORT_NODE__MAXIMUM_QUANTITY_OF` (512) — silently truncates blocks longer than 64 nodes.
  3. Calls `set_sort_node_as__allocated` instead of `set_sort_node_as__deallocated`, so "released" nodes stay marked allocated.
- **Impact:** releasing a sort list leaks/corrupts the node pool; subsequent allocations see a corrupted free state.
- **Fix:** compute the block's start index from `p_sort_nodes - manager->sort_nodes`, iterate `quantity_of__nodes` entries bounded by `SORT_NODE__MAXIMUM_QUANTITY_OF`, and mark them deallocated.

## 5. `release_sort_list_in__sort_list_manager` increments the node counter

- **Where:** `core/source/sort/sort_list/sort_list_manager.c` (~lines 199-201).
- **What:** after releasing a list, `quantity_of__allocated_sort_nodes += p_sort_list->size_of__p_node_list;` where it should be `-=`.
- **Impact:** the manager's allocated-node count drifts upward with every release; combined with bug 3, capacity accounting is unusable.
- **Fix:** change `+=` to `-=`.

## 6. `multiplayer.h` does not compile: `USER_ID` is an undefined type

- **Where:** `core/include/multiplayer/multiplayer.h` (line 8).
- **What:** `USER_ID get_user_id(Game* game);` declares a return type that is defined nowhere in the codebase. The three functions declared in this header (`is_in_multiplayer_game`, `is_host`, `get_user_id`) also have no implementations in core or any backend.
- **Impact:** any translation unit that includes `multiplayer.h` fails to compile (`unknown type name 'USER_ID'`). The header is currently dead — nothing includes it.
- **Fix:** either implement the three functions (defining `USER_ID` first) or remove the header.

## 7. `broadcast_game_action` loop condition is a constant — infinite loop / OOB read

- **Where:** `core/source/game.c` — `broadcast_game_action`, for-loop at ~line 587.
- **What:** the loop condition is `get_max_quantity_of__clients_for__game(p_game)` with the `index_of__client <` comparison missing, so it is always true whenever a client pool is allocated.
- **Impact:** any `BROADCASTED` game action in a multiplayer context never terminates the loop:
  - debug builds: at the first index past `index_to__next_client_in__pool`, `get_p_client_by__index_from__game` returns 0, and `get_p_local_space_from__local_space_manager(0, ...)` (no null check, local_space_manager.c ~line 837) dereferences NULL → crash.
  - release builds: that bounds check is compiled out, so the loop indexes `pM_ptr_array_of__clients` without bound (heap OOB read) → crash or wild dispatch to garbage `Client` pointers.
- **Fix:** make the condition `index_of__client < get_max_quantity_of__clients_for__game(p_game)` (or iterate to `index_to__next_client_in__pool`).

## 8. `initialize_tcp_socket` memset overflows the struct by `sizeof(Serialization_Header)`

- **Where:** `core/source/multiplayer/tcp_socket.c` — `initialize_tcp_socket`, memset at ~line 46.
- **What:** `memset(&p_tcp_socket->queue_of__tcp_packet, 0, sizeof(TCP_Socket))` starts at the queue field but writes a full `sizeof(TCP_Socket)` — since `_serialization_header` precedes the queue, this writes 8 bytes past the end of the struct. It is called by `accept_socket_on__tcp_socket_manager__ipv4` and `open_socket_on__tcp_socket_manager__ipv4` immediately after `allocate_tcp_socket_from__tcp_socket_manager` set the pool's ptr-array entry.
- **Impact:**
  - default config (`MAX_QUANTITY_OF__TCP_SOCKETS=1`): the overflow lands exactly on `ptr_array_of__tcp_sockets[0]`, zeroing the pointer the allocator just stored (little-endian) → the server default poll then sees a missing server socket (debug abort / NULL deref in release).
  - multi-socket configs: the overflow zeroes the next slot's `Serialization_Header` (uuid → 0, which is neither a valid UUID nor the `0xFFFFFFFF` deallocated marker), silently removing that slot from the allocatable pool.
- **Fix:** `memset(p_tcp_socket, 0, sizeof(TCP_Socket))` (as `initialize_tcp_socket_as__deallocated` already does), then re-initialize the header.

## 9. `close_socket_on__tcp_socket_manager__ipv4` — uninitialized pointer + corrupts ptr-array invariant

- **Where:** `core/source/multiplayer/tcp_socket_manager.c` (~lines 178-221).
- **What:**
  1. `p_ptr_tcp_socket__last` is never initialized; when the closed socket is the only entry it is read uninitialized (`being_release != last` comparison, then `*being_release = *last`) — UB.
  2. When the closed socket is the **last** entry in the compact ptr-array (e.g. closing the client in `[server, client]`), the swap writes the tail into the release slot and nulls the tail, leaving a hole (`[0, server]`) instead of `[server, 0]`.
- **Impact:** (1) can read/copy through a garbage pointer when closing the sole socket. (2) breaks the compact-prefix invariant: `allocate_tcp_socket_from__tcp_socket_manager` (first empty slot) and the server default poll's `while (... && *p_ptr)` iteration (stops at first hole) both misbehave afterwards — the server default poll reads `ptr_array[0]` as the server socket and gets 0.
- **Fix:** initialize `p_ptr_tcp_socket__last = 0`, and swap so the released slot becomes 0 and the tail's position receives the last element (hole = release index, tail = last non-null index, matching the `release_client_from__game` pattern).

## 10. Server default poll reads `ptr_array_of__tcp_sockets[1]` out of bounds

- **Where:** `core/source/multiplayer/server__default.c` (~lines 51-62).
- **What:** `p_tcp_socket__auth = p_tcp_socket_manager->ptr_array_of__tcp_sockets[1];` unconditionally, although `MAX_QUANTITY_OF__TCP_SOCKETS` is 1 by default (a size-1 array). The debug guard only checks the server socket — the `!p_tcp_socket__auth` half of the condition is commented out.
- **Impact:** OOB read (UB) in every configuration; with the default config the "auth" socket is a one-past-the-end pointer that is never validated before use.
- **Fix:** guard the read on `MAX_QUANTITY_OF__TCP_SOCKETS > 1` (or rework the fixed-index server/auth layout) and re-enable the auth check.

## 11. `release_client_pool_from__game` leaks the ptr array and makes the pool un-allocatable

- **Where:** `core/source/game.c` (~lines 191-208).
- **What:** frees `pM_clients` but never frees `pM_ptr_array_of__clients`, never nulls either field, and never resets `max_quantity_of__clients` / `index_to__next_client_in__pool`.
- **Impact:** the ptr array leaks on every release; `pM_clients` remains a dangling non-NULL pointer, so the `if (p_game->pM_clients)` guard in `allocate_client_pool_for__game` makes re-allocation impossible for the rest of the process.
- **Fix:** free both allocations, null both pointers, and reset the two counters (and the ptr array contents).

## 12. `teleport_client` dereferences `run_process` result without a null check

- **Where:** `core/source/client.c` — `teleport_client`, ~lines 155-163.
- **What:** `p_process->process_valueA__i32 = GET_UUID_P(p_client);` runs unconditionally after `run_process`, which returns 0 when the process pool is exhausted.
- **Impact:** NULL dereference crash if the 512-process pool is full at teleport time (the sibling handler `m_process__teleport_client` fails gracefully in the same situation).
- **Fix:** check `p_process` and return 0 on failure.

## 13. client.c dispatch/receive pass a NULL action when a WITH_PROCESS action is already allocated

- **Where:** `core/source/client.c` — `receive_game_action_for__client` (~lines 243-271) and `dispatch_game_action_for__client` (~lines 325-353).
- **What:** both functions declare `p_game_action__allocated = 0` and only assign it inside `if (!is_game_action__allocated(p_game_action))`. In the already-allocated case the local stays 0 and is then passed to `dispatch_game_action_process__inbound/__outbound` (which dereferences it for the kind) and, on process failure, to `release_game_action_from__game_action_manager` (which in release builds writes a deallocated header through NULL).
- **Impact:** crash (NULL deref / NULL write) whenever an already-allocated `WITH_PROCESS` action enters the dispatch or receive path; the `if (!is_game_action__allocated(...))` guard shows the case was anticipated but not handled.
- **Fix:** in the already-allocated branch use `p_game_action` itself (e.g. `p_game_action__allocated = p_game_action;` after the if/else).

## 14. Dangling public declarations (link error if called)

- **Where:**
  - `core/include/client.h`: `set_entity_of__client` (~line 44), `allocate_game_action_from__client` (~line 40).
  - `core/include/world/world.h`: `allocate_entity_into__world` (~line 15).
- **What:** declared in public headers with no definition anywhere in core or the backends. (`Client` has no entity member for `set_entity_of__client` to set.)
- **Impact:** link failure for any caller; the module docs now annotate them as "declared, no core implementation".
- **Fix:** implement or remove the declarations.

## Notes

- Bugs 3-5 all sit in the sort-list manager's accounting/release path; fix them together and add a small pool round-trip test (allocate lists/nodes, release, re-allocate) to lock the counters in.
- Bug 1 is the only gameplay-visible one of the first set (missed south-neighbor collisions); bugs 2-5 are latent in the sort infrastructure.
- Bugs 6-14 come from the client/world/multiplayer/game_action doc review. Bugs 7 and 8 are the most severe: any broadcasted game action (7) and any accepted/opened TCP socket (8) hit them in the default configuration. Bugs 7-11 are all in the multiplayer client/socket path and should be reviewed together — they share the `ptr_array_of__tcp_sockets` compact-prefix invariant.
- Bug 6 is a compile blocker for anything including `multiplayer.h`; the header is currently included by nothing, so it has stayed hidden.
