m_process__serialize_client__default — core/source/client.c, lines 469-516

## Function

```c
void m_process__serialize_client__default(
        Process *p_this_process,
        Game *p_game);
```

## Summary

Serializes the Client's Hitbox_AABB struct to a file via the filesystem process pipeline. Retrieves the client's Hitbox_AABB from the game's Hitbox_AABB_Manager using the client's serialization header UUID, writes the struct bytes to the file handler, and handles errors by releasing the client and failing the process.

## Pre-conditions

1. `p_this_process` is a valid, running Process whose `p_process_data` points to a `Serialization_Request*` properly initialized by `initialize_process_as__filesystem_process__open_file`.
2. `p_game` is a valid Game pointer.
3. `p_this_process->p_process_data` is a non-null `Serialization_Request*`.
4. `p_serialization_request->p_data` is a valid `Client*` currently active in the game.
5. `get_p_hitbox_context_from__game(p_game)` returns a non-null `Hitbox_Context*`.
6. The Hitbox_Context contains a valid Hitbox_AABB_Manager retrievable by the game's world UUID via `get_pV_hitbox_manager_from__hitbox_context`.
7. The game's world UUID matches the UUID used to register the Hitbox_AABB_Manager in the Hitbox_Context.
8. The client's Hitbox_AABB exists in the Hitbox_AABB_Manager (identifiable by `GET_UUID_P(p_client)`).
9. `p_serialization_request->p_file_handler` is a valid, open file handle for writing (opened by the calling filesystem process).
10. The platform file system context (`p_game->p_PLATFORM_file_system_context`) is valid.

## Post-conditions

- **On success:** The client's Hitbox_AABB struct (`sizeof(Hitbox_AABB)` bytes) has been written to the file. The client remains in the game (not released). The process completes normally via `complete_process`.
- **On failure (no hitbox):** The client is released from the game via `release_client_from__game`. The process fails via `fail_process`.
- **On failure (write error):** The client is released from the game via `release_client_from__game`. The process fails via `fail_process`.

## Correctness Verdict

Correct

## Semantic Alignment

The function fulfills its semantic intent. The module documentation states: "Clients are serialized as their AABB hitbox data only." The implementation correctly retrieves the client's Hitbox_AABB (which includes `_serialization_header`, position, velocity, acceleration, dimensions, and flags) and writes it to the file. Only the Hitbox_AABB data is serialized — no other Client fields (game_action_managers, local_space_manager, input state, flags) are written. This matches the documented semantic intent.

The UUID used to look up the Hitbox_AABB (`GET_UUID_P(p_client)`) is the client's serialization header UUID, which is the same UUID used when the Hitbox_AABB was allocated into the Hitbox_AABB_Manager (via `allocate_hitbox_aabb_from__hitbox_aabb_manager` with the same UUID). This ensures the correct hitbox is found.

## Implementation Correctness

1. **Type compatibility:** The function correctly casts `Hitbox_AABB*` to `u8*` for the `PLATFORM_write_file` call and uses `sizeof(Hitbox_AABB)` for the write length. This is a standard, safe cast in C with no truncation or implicit conversion issues. The `Quantity__u32` type is compatible with `sizeof` return values.
2. **Undefined behavior:** No issues found. The function does not perform broken pointer arithmetic, null dereference (null checks are performed before use), type punning beyond the standard `Hitbox_AABB*` → `u8*` cast, or out-of-bounds access. The UUID-based lookup is consistent with how clients and their hitboxes are related.
3. **Validation:** The function validates that the Hitbox_AABB exists in the manager. If it does not (client lacks a hitbox component), the process fails and the client is released. This is appropriate for a save handler — a client without a hitbox should not remain in the game. The function does not validate the client pointer itself, but this is the caller's responsibility (the caller ensures a valid Client* is passed via `p_serialization_request->p_data`).

## Side Effects

- **On success:** Writes `sizeof(Hitbox_AABB)` bytes (the client's Hitbox_AABB data) to the file via `PLATFORM_write_file`. The client remains in the game. The process is completed via `complete_process`.
- **On failure (no hitbox):** Releases the client from the game via `release_client_from__game`. The process fails via `fail_process`.
- **On failure (write error):** Releases the client from the game via `release_client_from__game`. The process fails via `fail_process`.

No side effects on the client struct itself (no fields are modified). No side effects on the Hitbox_AABB_Manager (no elements are added or removed beyond the client release path). No side effects on the Hitbox_AABB (it is only read, not modified).
