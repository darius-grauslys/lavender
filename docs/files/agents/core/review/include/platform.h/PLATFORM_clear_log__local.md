PLATFORM_clear_log__local — core/include/platform.h (declaration line 373; reference impl: nds/source/nds_log.c:60; stubs: sdl/source/TMP.c:171, tests/core/source/PLATFORM.c:445, tests/templates/source/PLATFORM.c:445)

Clears the platform/backend-level local log display/rendering state for the active platform. Takes the Game context and returns a bool indicating whether the clear was performed (true) or skipped/failed (false). On the reference (NDS) backend it gates on the active UI window being Idle before issuing the platform clear.

Pre-conditions:
1. p_game must be a non-null pointer to a valid, writable Game. The reference (NDS) implementation dereferences p_game via get_p_PLATFORM_gfx_context_from__game (which reads p_game->gfx_context.p_PLATFORM_gfx_context), so a null p_game is undefined behavior.
2. The backend gfx context must be initialized and available (the real implementation reads p_game->gfx_context.p_PLATFORM_gfx_context and operates on it). For NDS, the active UI window state must be accessible so that the Idle-window gate can be evaluated.
3. The platform backend must provide an implementation of PLATFORM_clear_log__local(Game *); per agents/platform_api.md this is supplied per-backend (NDS: nds_log.c:60; SDL/no_gui stubs: sdl/source/TMP.c:171). The function is marked "// TODO: remove" in the header (line 372).

Post-conditions:
1. On a real backend the local log display/rendering state is cleared (NDS: NDS_clear_log is invoked on the gfx context). The stubs unconditionally return false and perform no clearing.
2. Returns false when the clear is skipped (NDS: returns false when the active UI window is not UI_Window_Kind__Idle). NOTE: the stubs return false unconditionally, and the NDS reference implementation does NOT return a value on the success path (see Implementation Correctness) — so the documented "true on success" contract is not actually honored.

Correctness Verdict: Incorrect

Semantic Alignment:
The semantic intent — clear the backend's local log display — is correctly conveyed by the name and by the reference (NDS) implementation, which gates on the UI window being Idle and then calls NDS_clear_log. The SDL/no_gui stubs (`return false;`) and the test stubs do not fulfill this intent; they are acceptable only as TODO:remove placeholders, not as real implementations. The only complete implementation (NDS) is semantically aligned but mechanically broken (missing return). Note: NDS_clear_log itself is currently an unimplemented stub (nds_ui__log.c:43, `//TODO: impl`), so even on the success path no clearing actually occurs today.

Lavender-specific note: The core Log struct itself is cleared by the CALLER (clear_log__local in game.h -> clear_log -> initialize_log), which is Lavender-style initialization (reset to default state, NOT RAII resource acquisition). PLATFORM_clear_log__local itself only clears the backend's representation; it is not an init/reset/RAII function.

Implementation Correctness:
- Undefined behavior (critical): The reference NDS implementation at nds/source/nds_log.c:60 is declared `bool PLATFORM_clear_log__local(Game *p_game)` but, after calling NDS_clear_log(...) — which is `void` (see nds_ui__log.h:18) — it falls off the end of the function without a return statement. Falling off the end of a non-void function is undefined behavior in C (C99 §6.8.6.4). It must `return true;` (or otherwise yield a value) on the success path. The sibling functions PLATFORM_clear_log__global / __system at nds_log.c:48 and :72 share the identical defect, as do PLATFORM_update_log__global / __local / __system at nds_log.c:9, :22, and :35.
- Type compatibility: p_game is Game *, matching the parameter type exactly. get_p_PLATFORM_gfx_context_from__game returns PLATFORM_Gfx_Context *, matching NDS_clear_log's first parameter. The arguments to is_ui_window_kind_of__this_kind / get_the_kind_of__active_ui_window match their declared types. No implicit conversions or truncation anywhere.
- Null dereference / pointer safety: No null-check on p_game; the getter dereferences it. This matches Lavender convention (low-level platform shims do not validate p_game and rely on the caller), but it is a latent UB if p_game is null. No other pointer arithmetic, type punning, or out-of-bounds access occurs within this function.
- Stubs: sdl/source/TMP.c:171 and tests/{core,templates}/source/PLATFORM.c:445 define `bool PLATFORM_clear_log__local(Game *p_game) { return false; }`. These are defined (no UB) but perform no work and never succeed; acceptable only as TODO:remove placeholders.
- Validation: Appropriate for the role — no validation is performed, consistent with the Lavender convention for low-level platform shims; ensuring p_game validity is the caller's responsibility (clear_log__local in game.h passes a valid Game *).

Side Effects:
1. On a real backend (NDS): triggers the platform-specific clearing of the local log display/rendering state via NDS_clear_log(p_PLATFORM_gfx_context). This mutates/clears backend rendering state (on NDS, the log background text buffer). NOTE: NDS_clear_log is currently an unimplemented stub, so in practice no rendering state is mutated.
2. The stubs (SDL/no_gui, tests) have no side effects — they simply return false.
3. The function does NOT mutate p_game->log__local; the core Log struct is cleared by the caller's prior clear_log(...) -> initialize_log(...). This platform function only clears the backend's own representation of the log.
