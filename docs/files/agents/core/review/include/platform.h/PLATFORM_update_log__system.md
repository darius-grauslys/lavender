PLATFORM_update_log__system — core/include/platform.h (declaration, line 368)

Renders (backend-specific) the system log for display. This is a platform-abstracted function: core declares only the contract; the real logic lives in a per-platform `.c` file. The declaration is marked `// TODO: remove`, and its sole call site in core (`core/source/game.c:674`) is commented out, so the in-core system log is currently a write-only ring buffer with no display.

Implementations found:
- Stubs (no-op, `return false`): `sdl/source/TMP.c:168`, `tests/core/source/PLATFORM.c:440`, `tests/templates/source/PLATFORM.c:440`
- Real implementation: `nds/source/nds_log.c:35`

Semantic
Updates/renders the system log to its backend display (e.g., on-screen HUD) and reports whether rendering occurred. Stubs render nothing.

Pre-conditions:
1. `p_game` must be a non-null pointer to a valid `Game`.
2. (NDS) `p_game->gfx_context.p_PLATFORM_gfx_context` must be valid/usable (queried via `get_p_PLATFORM_gfx_context_from__game`); stubs ignore `p_game` entirely.
3. (NDS) Only renders when the active UI window kind is `UI_Window_Kind__Idle`; otherwise short-circuits and returns false without rendering.
4. The system `Log` is accessed read-only for display; it is populated/cleared by the caller (`print_log__system` -> `put_cstr_into__message`/`flush_message_into__log`, and `clear_log__system` -> `clear_log`/`initialize_log`), so no further initialization precondition applies here. This is not an init/reset/RAII function — it only refreshes the backend's representation of an already-populated log.

Post-conditions:
1. Returns `bool`: intended `false` when no rendering occurred (not idle); `true` when the system log was rendered. (NDS violates this — see Implementation Correctness.)
2. (NDS) On the idle path, calls `NDS_update_log(gfx, system_log)`, which mutates the on-screen log UI for the system log; on non-idle windows, no rendering occurs.
3. (Stubs) No state mutation; always returns `false`; renders nothing.

Correctness Verdict: Incorrect

Semantic Alignment:
The header intent (per `agents/platform_api.md`) is "Backend renders the system log (e.g., on-screen)."
- Stubs: do NOT fulfill the intent — they return `false` and render nothing. Acceptable only as placeholders (contract marked TODO: remove).
- NDS: fulfills the intent — it gates on the active UI window being `Idle` and calls `NDS_update_log` to render the system log. However the implementation is bugged on the success path (see below), so it does not reliably fulfill the intent.

Implementation Correctness:
- Type compatibility: `p_game` (`Game*`) matches the prototype; arguments to `NDS_update_log` (`PLATFORM_Gfx_Context*`, `Log*`) match its declared `void NDS_update_log(PLATFORM_Gfx_Context*, Log*)` signature. `get_p_log__system_from__game` returns `Log*` (`&p_game->log__system`), matching the second parameter exactly. No implicit conversions or truncation.
- Undefined behavior (NDS, `nds/source/nds_log.c:35`): the function is declared `bool`, but on the idle (success) path it reaches the closing brace after the `void` call `NDS_update_log(...)` with NO `return` statement. Since `NDS_update_log` is `void`, the return register is indeterminate. Falling off a non-void function is undefined behavior (C99 §6.8.6.4); the compiler will emit `-Wreturn-type`. This is a real defect. Fix: add `return true;` (or the intended bool) after the `NDS_update_log` call. The sibling functions `PLATFORM_update_log__global`/`__local` and all `PLATFORM_clear_log__*` in `nds_log.c` share the identical missing-return defect.
- Null-safety: NDS dereferences `p_game` via getters without a null check, but `p_game` is a required non-null parameter (Pre-condition 1), so this is caller responsibility — acceptable for a low-level platform function.
- Validation: appropriate — window-kind gating is the intended validation; stubs intentionally omit it.

Side Effects:
- (NDS) Mutates the on-screen log UI via `NDS_update_log` (writes into the `PLATFORM_Gfx_Context`'s UI/log state for the system log) when the active UI window is `Idle`; otherwise no effect.
- (Stubs) No side effects — returns `false` and mutates nothing.
- Does NOT mutate `p_game->log__system`; that `Log` is written/cleared by core (`print_log__system`, `clear_log__system`) prior to/without this call.
