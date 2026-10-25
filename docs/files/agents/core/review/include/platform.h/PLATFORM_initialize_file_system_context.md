PLATFORM_initialize_file_system_context — core/include/platform.h, lines 276-279

Prepares a `PLATFORM_File_System_Context` for use: resets the serialization-request pool to its initial (inactive/free) state and sets up the platform-dependent file-system resources (base directory path + a background serialization process; on NDS also FAT and an audio-stream timer). The declaration is marked `// TODO: remove`, suggesting it is being folded into `PLATFORM_initialize_game`.

There is **no implementation in core** (`core/source/...`); per `platform.h` (lines 13-19) these `PLATFORM_*` functions are implemented by backends. Implementations found:
- SDL: `sdl/source/serialization/sdl_filesystem.c:19`
- no_gui: `no_gui/source/serialization/no_gui_filesystem.c:196`
- NDS: `nds/source/serialization/nds_filesystem.c:94`
- test/mock stubs (intentional no-ops): `tests/core/source/PLATFORM.c:324`, `tests/templates/source/PLATFORM.c:324`

Struct definitions (per-backend):
- SDL (`sdl/include/sdl_defines.h:291-296`) and no_gui (`no_gui/include/no_gui_defines.h:91-96`): `SDL_serialization_requests[]` / `NO_GUI_serialization_requests[]`, `path_to__base_directory`, `size_of__path_to__base_directory`.
- NDS (`nds/include/nds_defines.h:283-291`): `serialization_requests[]`, `ptr_array_of__serialization_requests[]`, `f_audio_stream__callback`, `p_serialization_process`, `timer__audio_stream_u8`.

Pre-conditions:
1. `p_PLATOFRM_file_system_context` is a non-null pointer to a writable `PLATFORM_File_System_Context` owned by the caller (the static backend context, e.g. `&__SDL_file_system_context`). NDS validates this under `#ifndef NDEBUG`; SDL/no_gui do not and deref on line 1.
2. `p_game` is a non-null pointer to an initialized `Game` whose process manager is available (via `get_p_process_manager_from__game`), required to spawn the serialization process. Not explicitly validated by SDL/no_gui.
3. The context's serialization-request pool is in an unspecified state on entry (the function is responsible for bringing it to the initial cleared state).
4. The caller has not already spawned a serialization process for this context (call-once init expectation; re-calling leaks/overwrites the prior process handle on NDS).

Post-conditions:
1. Every entry of the context's serialization-request pool is reset to its initial cleared state: zeroed memory with `serialization_request_flags == SERIALIZATION_REQUEST_FLAGS__NONE` (i.e. `IS_ALLOCATED == 0` and `IS_ACTIVE == 0`), so each slot is a free, unallocated, inactive request. (Implemented via the core `initialize_serialization_request`.)
2. `path_to__base_directory` is populated with the platform base directory path, null-terminated within `IO_path` (`MAX_LENGTH_OF__IO_PATH`).
3. `size_of__path_to__base_directory` holds `strnlen(path_to__base_directory, MAX_LENGTH_OF__IO_PATH)`. (SDL/no_gui only.)
4. On NDS, `ptr_array_of__serialization_requests[i]` is zeroed for all slots; `p_serialization_process` points to a registered, critical serialization process whose run-handler is `m_NDS_process__serialization` and whose `p_process_data` is this context; `f_audio_stream__callback` is zeroed; `timer__audio_stream_u8` is initialized via `initialize_timer_u8`. (SDL/no_gui have no such fields.)
5. A critical serialization process has been registered with the game's process manager (SDL/no_gui via `run_process`; NDS via `allocate_process_forcefully_in__process_manager` + `register_process_as__critical_in__process_manager`).
6. Return type is `void`; there is no return value to inspect on failure. (Note: on process-spawn failure the function `debug_abort`s and returns, leaving the context partially initialized — base dir/pools set, but no process.)

Correctness Verdict: Correct

Semantic Alignment:
The implementation fulfills the function's semantic intent as a platform-abstraction initializer: it both (a) resets the serialization-request pool to a reusable initial state — the Lavender "initialization ≠ RAII" pool-cleanup pattern — and (b) performs platform resource setup (base dir, serialization process; NDS: FAT + timer). Per the established precedent in `PLATFORM_initialize_audio.md`, resource setup at the platform-abstraction layer is necessary and legitimate; the "initialization ≠ RAII" principle governs core-engine struct lifecycle, not platform resource setup.

Lavender "initialization ≠ RAII" classification: This function does BOTH. The pool-clearing loop is Lavender-style initialization (reset to initial conditions for pooling). The process/timer/FAT setup is RAII-style resource acquisition at the platform layer. This dual nature is consistent with sibling platform init functions and is correct for this layer.

Field coverage:
- SDL: all three struct fields are touched — pool cleared (✓), `path_to__base_directory` (✓), `size_of__path_to__base_directory` (✓). No field omitted or reordered.
- no_gui: identical coverage to SDL (✓ all three).
- NDS: all five struct fields are touched — `serialization_requests` cleared (✓), `ptr_array_of__serialization_requests` zeroed (✓), `f_audio_stream__callback` zeroed (✓), `p_serialization_process` set (✓), `timer__audio_stream_u8` initialized (✓). No field omitted or reordered.
- Test stubs: empty (intentional mocks, out of scope).

Implementation Correctness:
- Type compatibility: All parameter/field type matches are exact in every backend (e.g. `get_p_process_manager_from__game(p_game)` returns the manager; `run_process(..., PROCESS_PRIORITY__0_MAXIMUM, PROCESS_FLAG__IS_CRITICAL)`; `strnlen(path, MAX_LENGTH_OF__IO_PATH)` returns `size_t` assigned to `Quantity__u32` — `MAX_LENGTH_OF__IO_PATH` is bounded and small, so the narrowing to `u32` is safe). The parameter name in the header has the persistent typo `p_PLATOFRM_...` (missing 'F'); this is a cosmetic header issue with no type impact.
- Validation: Appropriate validation is inconsistent across backends. NDS checks `p_PLATOFRM_file_system_context != NULL` under `#ifndef NDEBUG`; SDL/no_gui perform no null check and deref `p_PLATOFRM_file_system_context` on the very first statement (line 1 of the loop), so a null context in a release SDL/no_gui build yields null dereference / UB. Given the function is low-level platform setup invoked once at game init with a known-static context, relying on the caller invariant is defensible, but the inconsistency with NDS is worth flagging.
- Critical issue — NDS is non-compilable: The NDS implementation (and the NDS `allocate`/`release` paths) calls `initialize_serialization_request_as__uninitalized`, a function that is **declared nowhere and defined nowhere** in the repository (verified via grep across `core/` and `nds/`). The intended behavior is clearly "zero + mark as uninitialized," which matches the core `initialize_serialization_request` pattern, but because the symbol is absent the NDS port produces a hard link error. This is a link-time failure, not runtime UB, and it is a systemic issue affecting multiple NDS functions — not a logic defect within this function's body per se. If the NDS port is inactive, this may be latent; as written the NDK build cannot link.
- Off-by-one / bounds: Loop bounds are correct in all backends (`index < MAX_QUANTITY_OF__SERIALIZATION_REQUESTS` for SDL/no_gui, `index < FILE_SYSTEM_CONTEXT__QUANTITY_OF__SERIALIZAITON_REQUESTS` for NDS), and the array accesses stay in range. `strnlen` is used correctly to cap the path length at `MAX_LENGTH_OF__IO_PATH`.
- `run_process` return value is checked for null after the call in all backends (SDL/no_gui abort+return; NDS aborts+returns), so no null process is stored.
- No pointer arithmetic, no type punning, no uninitialized reads in the working backends.

Side Effects:
- Mutates `p_PLATOFRM_file_system_context` in place: resets every serialization-request slot to the cleared/inactive state; writes `path_to__base_directory` and `size_of__path_to__base_directory` (SDL/no_gui); zeroes `ptr_array_of__serialization_requests`, `f_audio_stream__callback` and sets `p_serialization_process` + initializes `timer__audio_stream_u8` (NDS).
- Calls platform resource-setup side effects outside the struct (out of scope to trace per review rules, but observable): spawns and registers a critical background serialization `Process` with the game's process manager (which begins running that process each tick), and on NDS calls `fatInitDefault()` (initializes the FAT filesystem driver).
- On process-spawn failure: `debug_abort`s (which is fatal in this codebase) and early-returns; the context is left with pool + base dir initialized but no serialization process.
- Test/mock stubs: no side effects (empty bodies).

Note: The declaration is annotated `// TODO: remove`, and `agents/platform_api.md` notes file-system init is merged into `PLATFORM_initialize_game`; callers invoke this from each backend's game-init (`sdl_game.c:44`, `no_gui_game.c:14`, `nds_main.c:25`). The NDS backend's undefined `initialize_serialization_request_as__uninitalized` symbol should be resolved (define or alias it to `initialize_serialization_request`) so that port compiles.
