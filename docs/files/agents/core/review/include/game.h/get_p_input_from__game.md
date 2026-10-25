get_p_input_from__game — core/include/game.h, lines 295-300

Returns a pointer to the active Input: the local client's input when the game is configured for multiple clients, otherwise the Game's own embedded input member.

Pre-conditions:
1. p_game must be a non-null pointer to a valid, readable Game object (the pointer is dereferenced immediately via p_game->max_quantity_of__clients).
2. When p_game->max_quantity_of__clients != 0, the caller must guarantee that p_game->pM_ptr_array_of__clients is non-null and contains at least one valid Client at index 0; get_p_local_client_by__from__game returns NULL when the array is null, and get_p_input_of__client dereferences that pointer in release builds (NDEBUG).

Post-conditions:
1. Returns an Input * aliasing one of two embedded members:
   - If p_game->max_quantity_of__clients != 0: &local_client->input_of__client, where the local client is p_game->pM_ptr_array_of__clients[0] (input_of__client is the Client field declared at client.h).
   - If p_game->max_quantity_of__clients == 0: &p_game->input (the Game field declared at defines.h:2547, type Input).
2. The returned pointer is valid for the lifetime of the Game (or its local client) and aliases mutable state.
3. No mutation occurs; this is a read-only accessor over the Game struct.

Correctness Verdict: Correct

Semantic Alignment:
The implementation matches the documented intent exactly. The struct field comment at defines.h:2575-2577 states: "If max_quantity_of__clients == 0 we will use input, otherwise local player input." The function returns &p_game->input when the quantity is zero and delegates to the local client's input when it is non-zero, faithfully realizing this contract. No semantic drift is present.

Implementation Correctness:
- Type compatibility — the declared return type is Input *. In the client branch, get_p_input_of__client returns Input * (client.h:170), which matches exactly. In the Game branch, &p_game->input yields Input * because the field input is of type Input (defines.h:2547). No implicit conversions or truncation occur.
- max_quantity_of__clients is Quantity__u32 (i.e., uint32_t, per defines.h:140); using it in the boolean context of if() is well-defined (zero is falsy, non-zero is truthy).
- Undefined behavior — the only potential for undefined behavior is a NULL p_game, which is the caller's responsibility and consistent with every sibling get_p_*_from__game accessor in this file, none of which validate their argument. A secondary concern: when max_quantity_of__clients != 0 but pM_ptr_array_of__clients is null, get_p_local_client_by__from__game returns 0 and get_p_input_of__client dereferences it in release builds. This is a caller-responsibility issue (the pre-condition above documents the guarantee) and matches the codebase convention of placing validation at the call site.
- No broken pointer arithmetic, no type punning, no out-of-bounds access.
- Validation — no validation is performed, which is appropriate for a low-level inline accessor; validation is the caller's responsibility, matching the convention of all sibling accessors in game.h.

Side Effects:
No side effects — the function is a pure accessor. It reads p_game (the pointer value) and the max_quantity_of__clients member, then produces a pointer to one of two embedded members; it does not mutate the Game struct or any other observable state.