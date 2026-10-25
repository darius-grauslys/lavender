manage_game — core/include/game.h, line 39

A high-level, per-frame game-management entry point. By naming convention it would coordinate the game's per-frame lifecycle (the implemented `manage_game__pre_render` and `manage_game__post_render` are the actual per-frame phases; the analogous top-level `manage_world` lives in `world.h`/`world.c`). No implementation exists, so the intent is inferred from naming rather than code.

Pre-conditions:
1. `p_game` must be a non-null pointer to a writable `Game` struct (defined at `core/include/defines.h:2595`). This follows the convention of every other `manage_game_*` and `manage_world` function.
2. The `Game` struct should have been initialized via `initialize_game()` (which zero-inits the struct and sets up embedded managers) — the same precondition assumed by `manage_game__pre_render` and `manage_game__post_render`. (Cannot be verified against an implementation; inferred from sibling functions.)
3. No other parameter constraints can be stated — the function has a single pointer parameter and no body.

Post-conditions:
1. None can be determined. No implementation exists, so no state changes, return values, or guarantees are produced.

Correctness Verdict: Incorrect

Semantic Alignment:
Cannot be evaluated. There is no implementation to compare against semantic intent, and the semantic intent itself is ambiguous. The actual per-frame work is performed entirely by the implemented `manage_game__pre_render` (game.c:737-739, which calls `PLATFORM_pre_render`) and `manage_game__post_render` (game.c:741-755, which runs poll_input, reset_tick_timer, poll_process_manager, `PLATFORM_poll_audio_effects`, `PLATFORM_post_render`, and the loop tick timer). Neither calls `manage_game`. The scene enter handlers (`scene__main.c:28`, `scene__main.c:31`, `nds/.../scene__game.c:89`, `scene__main.c:126`) likewise call only the `__pre_render` and `__post_render` variants. The bare `manage_game` declaration appears to be a stale/redundant declaration that was superseded by the pre/post-render split — a dead symbol.

Implementation Correctness:
- No implementation exists to evaluate type compatibility, undefined behavior, or validation against.
- The declaration itself is syntactically valid: `void manage_game(Game *p_game);` — a free (non-inline, non-static) function taking a single `Game *` parameter and returning `void`. The parameter type matches the `Game` struct definition at `core/include/defines.h`.
- No undefined behavior is present in the declaration (no pointer arithmetic, no dereference, no type punning, no array access — there is simply nothing).
- The declaration carries no validation logic (there is none to assess).
- Significant concern: The header file begins with the comment "This entire file is not implemented in core. You will need to compile with a backend." This comment is misleading — most functions declared in `game.h` (including `manage_game__pre_render`, `manage_game__post_render`, `initialize_game`, `run_game`, `poll_multiplayer`, etc.) ARE implemented in `core/source/game.c`. Only a subset of declarations (including `manage_game`) lack a core implementation. Furthermore, no backend (sdl, nds, no_gui) implements `manage_game` either. The declaration is a non-inline free function, which means it must be provided by exactly one translation unit; since none provides it, any reference to `manage_game` would produce an undefined-symbol linker error. There is no call site anywhere in the codebase, so the dead declaration does not currently break the build, but it is an incomplete, unusable API entry.

Side Effects:
No side effects. No implementation exists, so there are no observable mutations, I/O, or state changes. If implemented following the pattern of its siblings, it would likely mutate `Game` state (tick timers, process manager, logs) and invoke `PLATFORM_*` callbacks — but that is speculative and not present in any actual code.
