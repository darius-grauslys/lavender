save_world — core/source/world/world.c

Saves the world's serialized state to disk by writing world header data (name, random seeds) to the world's header file. Intended to be called when leaving the world and returning to the main menu.

Pre-conditions:
1. p_PLATFORM_file_system_context must be a non-null pointer to a valid PLATFORM_File_System_Context (used for file I/O operations).
2. p_world must be a non-null pointer to a valid, initialized World object whose name field is populated and whose repeatable_pseudo_random seeds are set.

Post-conditions:
1. On success, the world's name and pseudo-random seeds (seed__initial and seed__current_random) are written to the world's header file on disk.
2. The function returns void; no return value indicates success or failure.

Correctness Verdict: Incorrect

Semantic Alignment:
The function is intended to save the world's state to disk, serving as the inverse of load_world. However, the implementation is a stub that calls debug_abort("save_world, impl") instead of performing any actual serialization. The function does not open a file, write any world data, or call any serialization routines. The semantic intent (persisting world state to disk) is not fulfilled at all.

Looking at the related m_process__serialize_world function in the same source file, the world header data that should be serialized consists of:
- p_world->name (WORLD_NAME_MAX_SIZE_OF bytes)
- p_world->repeatable_pseudo_random.seed__initial
- p_world->repeatable_pseudo_random.seed__current_random

This data should be written to the file path established by stat_world_header_file. The save_world function should use stat_world_header_file to obtain the file path, open the file via PLATFORM_open_file with "wb" mode, write the header data using PLATFORM_write_file, and close the file via PLATFORM_close_file. None of this is implemented.

Implementation Correctness:
The function body consists solely of debug_abort("save_world, impl"). In debug builds (NDEBUG not defined), debug_abort prints the message and calls abort(), terminating the program. In release builds (NDEBUG defined), debug_abort calls PLATFORM_pre_abort() and returns without performing any save operation. This means:
- In debug builds: the function crashes the application whenever called.
- In release builds: the function silently does nothing, giving the caller no indication that the world was not saved.

There are no type mismatches, undefined behavior, or pointer issues in the current implementation because no actual work is performed. However, the function fails to fulfill its contract entirely.

Side Effects:
In debug builds: calls debug_abort which prints an error message and terminates the process (abort). In release builds: no side effects — the world is not saved to disk.
