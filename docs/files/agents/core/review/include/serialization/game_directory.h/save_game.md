save_game — core/include/serialization/game_directory.h

Serializes game state (settings, server data, world save names) to persistent storage. This is a backend-declared function — not implemented in core; the backend is expected to provide the implementation.

Pre-conditions:
1. p_game must be a non-null pointer to a valid, initialized Game struct.
2. Must be called from the main menu only (as documented in the header comment).
3. p_game->p_PLATFORM_file_system_context must be valid and initialized.
4. The game data directory (established via stat_game_data_file) should exist or be creatable by the backend.

Post-conditions:
1. No return value (void).
2. Game state data (settings, server data, world save names) is persisted to disk via the platform file system context.
3. The Game struct itself is not mutated by this function.

Correctness Verdict: Correct

Semantic Alignment:
The function declaration aligns with the module's documented purpose ("holds things such as settings, server data and world save names"). The single parameter (Game *p_game) is consistent with the pattern used by other functions in this module (e.g., stat_game_data_file also takes Game *p_game). The void return type is appropriate for a fire-and-forget save operation. The comment "Only call this from the main menu" is a valid usage constraint, as saving during active gameplay could lead to race conditions with world/entity state.

Implementation Correctness:
Type compatibility — the sole parameter is Game *p_game, which matches the Game struct type defined in core/include/defines.h. No implicit conversions or truncation issues.
Undefined behavior — no pointer arithmetic, no null dereference, no type punning, no out-of-bounds access are present in the declaration itself. As a backend function, the implementation is responsible for safe file I/O.
Validation — no validation is performed in the declaration. This is appropriate for a backend function; the caller is responsible for providing a valid Game pointer and ensuring the main-menu context. The backend implementation should validate the file system context.

Side Effects:
Writes game state data (settings, server data, world save names) to persistent storage (file system). The Game struct is not mutated.
