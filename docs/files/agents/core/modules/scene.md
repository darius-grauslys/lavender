# Scene — Engine services scene state machine

**Sources:** `core/source/scene/scene.c` + `core/source/scene/scene_manager.c` + `core/source/scene/implemented/scene__main.c` + `core/source/scene/implemented/scene_registrar.c` + `core/include/scene/scene.h` + `core/include/scene/scene_manager.h` + `core/include/scene/scene__game.h` + `core/include/scene/implemented/scene__main.h` + `core/include/scene/implemented/scene_registrar.h`

## Surface Concerns

The Scene module provides a lightweight scene state machine — the engine's mechanism for switching between high-level gameplay modes (main menu, game, test scene). **L2 ENGINE SERVICES.** Called from `Game` (via `run_game`, `initialize_game`, `register_scenes`).

- **Scene state machine** — switches the active scene via `set_active_scene_for__scene_manager()`. Manages `p_active_scene` and `is_active` flags only; does not itself invoke load/enter/unload handlers — those are called by `run_game` in the game layer during scene transitions.
- **Scene registration** — scenes are registered by kind with load/enter/unload handler triplets. The registrar (`implemented/scene_registrar.c`) carries a GEN block that code generation fills with one `register_scene__<kind>()` call per scene kind (currently `register_scene__main()` for `Scene_Kind__None`); game-layer kinds are added to the GEN block of `types/implemented/scene/scene_kind.h`.
- **Main scene loop** — the default scene (`Scene_Kind__None`) has a built-in enter handler containing the core game loop: tick wait, GEN-FRAME, `manage_game__pre_render()`, GEN-PRE-RENDER, `manage_game__post_render()`, GEN-POST-RENDER, repeat until inactive. Other scenes implement their own loops in enter handlers.
- **Game-scene data accessors** — `scene__game.h` provides inline accessors (`get_hud_timer_from__scene__game`, `get_typer_timer_from__scene__game`) that cast `p_scene_data` to `Scene_Data__Game*` and return pointers to its two `Timer__u8` fields. `Scene_Data__Game` is defined in `defines.h`.

## Public API Surface

### Key Types

**`Scene`** — defined in `defines.h`. Key members:
- `Serialization_Header _serialization_header` — scenes form a contiguous UUID array.
- `m_load_scene_handler`, `m_enter_scene_handler`, `m_unload_scene_handler` — `m_Load_Scene`/`m_Enter_Scene`/`m_Unload_Scene` function pointers installed by the game.
- `p_parent_scene`
- `p_scene_data` — opaque game data pointer.
- `is_active` — boolean.

**`Scene_Manager`** — defined in `defines.h`. Key members:
- `scenes[Scene_Kind__Unknown]` — array indexed by scene kind.
- `p_active_scene` — pointer to currently active scene.

**`Scene_Kind`** — defined in `types/implemented/scene/scene_kind.h`; `defines_weak.h` includes it and only falls back to its own weak enum when the implemented header is absent. Values: `Scene_Kind__None = 0`, a GEN block for game-layer kinds, `Scene_Kind__Unknown` (end marker). **DISCREPANCY:** CHECKPOINT.md says "scene mgr (256)" but the actual capacity is `Scene_Kind__Unknown` — 1 slot until the game layer registers kinds in the GEN block.

### Key Functions

- `void initialize_scene(Scene *scene);`
- `void initialize_scene_manager(Scene_Manager *p_scene_manager);`
- `void register_scene_into__scene_manager(Scene_Manager *p_scene_manager, Scene_Kind kind, m_Load_Scene load, m_Enter_Scene enter, m_Unload_Scene unload);`
- `Scene *get_p_scene_from__scene_manager(Scene_Manager *p_scene_manager, Scene_Kind kind);` — returns scene pointer or 0 on invalid kind.
- `void set_active_scene_for__scene_manager(Scene_Manager *p_scene_manager, Scene_Kind kind);`
- `void quit_scene_state_machine(Scene_Manager *p_scene_manager);` — contains a known bug: checks `!p_active_scene` then dereferences `p_active_scene->is_active` in `scene_manager.c`.
- `void m_load_scene_as__main_handler(Scene *p_this_scene, Game *p_game);`
- `void m_enter_scene_as__main_handler(Scene *p_this_scene, Game *p_game);`
- `void m_unload_scene_as__main_handler(Scene *p_this_scene, Game *p_game);`
- `void register_scene__main(Scene_Manager *p_scene_manager);`
- `void register_scenes(Scene_Manager *p_scene_manager);`
- `static inline bool is_scene__valid(Scene *p_scene);`
- `static inline Scene *get_p_active_scene_from__scene_manager(Scene_Manager *p_scene_manager);` / `bool is_p_scene_the__active_scene_in__scene_manager(Scene_Manager *p_scene_manager, Scene *p_scene);`
- `static inline bool poll_is__scene_active(Game *p_game, Scene *p_scene);`
- `static inline Timer__u8 *get_hud_timer_from__scene__game(Scene *p_scene);` / `Timer__u8 *get_typer_timer_from__scene__game(Scene *p_scene);` — cast `p_scene_data` to `Scene_Data__Game*`.

## Key Files Table

| File | Role |
|------|------|
| `core/source/scene/scene.c` | Scene init (clear all fields) |
| `core/source/scene/scene_manager.c` | Manager init, registration, active scene switching |
| `core/source/scene/implemented/scene__main.c` | Default main scene handlers (core game loop) |
| `core/source/scene/implemented/scene_registrar.c` | Scene registration orchestration (GEN block) |
| `core/include/scene/scene.h` | Scene init API, validation, active check |
| `core/include/scene/scene_manager.h` | Manager API, active scene getters |
| `core/include/scene/scene__game.h` | Game-scene data accessors |
| `core/include/scene/implemented/scene__main.h` | Main scene registrar header |
| `core/include/scene/implemented/scene_registrar.h` | Registrar orchestration header |
