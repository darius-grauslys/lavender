get_quantity_of__clients_connect_to__game — core/include/game.h

Returns the quantity (count) of clients currently connected to the game.

Pre-conditions:
1. `p_game` must be a non-null pointer to a valid, initialized `Game` object whose client pool has been allocated (i.e., `allocate_client_pool_for__game` or `initialize_game` has run successfully).
2. The caller must have permission to read the `Game` struct's `index_to__next_client_in__pool` field.

Post-conditions:
1. Returns the value of `p_game->index_to__next_client_in__pool`, which is the count of clients currently connected to the game (also used as the index of the next available slot in the client pool).
2. The returned value is `0` when no clients have been connected, and increases by 1 each time a client is added (`allocate_client_from__game` / `dispatch_handler_process_to__create_client` path).
3. No state is modified on `p_game` or any other object.
4. No global state is changed.

Correctness Verdict: Correct

Semantic Alignment:
The function is a simple accessor (getter) that returns the `index_to__next_client_in__pool` field from the `Game` struct. The field name reflects that it tracks the index of the next client to be placed in the pool; equivalently, since clients are added contiguously starting from index 0, this field also serves as the count of currently-connected clients. This dual role is confirmed by usage throughout `core/source/game.c`: it is incremented after each client allocation (game.c:325), decremented when a client is released (game.c:364), used as the loop upper bound when iterating over connected clients (game.c:223, game.c:353), and used for bounds checking in `get_p_client_by__index_from__game` (game.h:342). The function name (`get_quantity_of__clients_connect_to__game`) reflects the intent to report the number of connected clients, which the field accurately provides. No computation is performed and no field is omitted or reordered — there is only one field returned.

Implementation Correctness:
- **Type compatibility:** The return type `Quantity__u32` is a typedef for `uint32_t` (defined in `defines_weak.h:49` and `defines.h:140`). The field `index_to__next_client_in__pool` is declared as `Quantity__u32` in the `Game` struct (`defines.h:2579`), so the parameter type `Game *` and the field access type match exactly. No implicit conversions or truncation occur.
- **Undefined behavior:** No broken pointer arithmetic, no null dereference (caller's responsibility), no type punning, no out-of-bounds access. The function performs only a single field read on a struct pointer, which is well-defined as long as the pointer is valid — no UB.
- **Validation:** No validation is performed. This is a `static inline` low-level accessor; ensuring `p_game` validity is the caller's responsibility, consistent with the pattern used by neighboring accessors (e.g., `get_session_token_from__game` at game.h:303 and `get_max_quantity_of__clients_for__game` at game.h:320).

Side Effects:
No side effects. This is a pure read-only query function — it does not modify the `Game` struct or any other state.
