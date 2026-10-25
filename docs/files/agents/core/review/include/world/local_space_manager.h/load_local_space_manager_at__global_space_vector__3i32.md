load_local_space_manager_at__global_space_vector__3i32 — core/include/world/local_space_manager.h

Loads (reloads) the local space manager so that it is centered at the specified global space vector, performing a full drop and reinitialize of all local spaces.

Pre-conditions:
1. p_local_space_manager must be a non-null pointer to a valid, properly initialized Local_Space_Manager struct.
2. p_game must be a non-null pointer to a valid Game struct, as it is forwarded to set_center_of__local_space_manager which uses it to access the global space manager.
3. global_space_vector__3i32 may be any Global_Space_Vector__3i32 value (a chunk coordinate). No range constraint is required; it represents the desired center of the local space manager.

Post-conditions:
1. The local space manager is fully reinitialized: all existing local spaces are dropped, the manager is reinitialized with the new center, and all unheld local spaces are reacquired from the global space manager.
2. p_local_space_manager->center_of__local_space_manager__3i32 equals global_space_vector__3i32.

Correctness Verdict: Correct

Semantic Alignment:
The function correctly achieves a full reload rather than a scroll by first setting center_of__local_space_manager__3i32 to VECTOR__3i32__OUT_OF_BOUNDS. This sentinel value causes set_center_of__local_space_manager to skip its early-return optimization (which only fires when the current center is valid and equal to the target) and to skip the incremental scroll path (which only fires when the Manhattan distance is within [-1, 1] on each axis). Instead, it falls through to the full drop + initialize + hold path, which is the intended behavior for loading the local space manager at a new position.

Lavender-Specific Semantics:
This function's name contains "load" rather than "init"/"initialize"/"reset", so the Lavender-specific initialization semantics do not directly apply to this function itself. However, it indirectly triggers initialize_local_space_manager, which in the Lavender convention performs cleanup/reinitialization (resetting the struct to initial conditions for pool reuse), NOT RAII-style resource acquisition. This is the correct Lavender pattern.

Implementation Correctness:
Type compatibility — Global_Space_Vector__3i32 is a typedef for Vector__3i32 (see defines_weak.h:109), and Chunk_Vector__3i32 is also a typedef for Vector__3i32 (see defines_weak.h:107). Therefore the parameter is type-compatible with set_center_of__local_space_manager's expected Chunk_Vector__3i32 parameter. No implicit conversions or truncation occur.
Undefined behavior — No pointer arithmetic, no null dereference (assuming pre-conditions are met), no type punning, no out-of-bounds access.
Validation — No validation is performed in this function itself. This is appropriate for a low-level inline helper; the caller is responsible for ensuring valid pointers. The delegated set_center_of__local_space_manager also performs no null checks, consistent with the codebase's convention of relying on callers.

Side Effects:
Mutates p_local_space_manager — sets center_of__local_space_manager__3i32 to VECTOR__3i32__OUT_OF_BOUNDS, then through set_center_of__local_space_manager: drops all local spaces (releasing their global space references), reinitializes the local space manager struct (reassigning all local space global_space__vector__3i32 fields and neighbor pointers), and holds all previously-unheld local spaces from the global space manager. The p_game pointer is forwarded to callees which may mutate global space manager state (holding/dropping global spaces).
