# Lavender Comprehension Project — CHECKPOINT

**Date:** 2026-08-23 (session interrupted for compute reallocation)
**Repo state:** `doc-gen` branch, HEAD `f3d92ab` "cleanup slop"
**Constraint:** Only files under `./agents/` may be created/modified.

---

## 1. PLAN (what we set out to do)

Build a high-level comprehension roadmap of Lavender — a monolithic ~150k-LOC
cross-platform retro C game engine (pulled from the author's AncientsGame repo)
that abstracts hardware behind a `core/include/platform.h` API surface with
three backends (SDL / NDS / no_gui).

Deliverables (all under `./agents/`):

| # | File | Purpose | Status |
|---|------|---------|--------|
| 1 | `agents/README.md` | Index of all docs, how to navigate | ⬜ not started |
| 2 | `agents/ARCHITECTURE.md` | High-level roadmap: layers, module dependency graph, frame lifecycle | ⬜ not started (material gathered) |
| 3 | `agents/platform_api.md` | Full platform.h API surface + wiring mechanism | ⬜ not started (material gathered) |
| 4 | `agents/modules/*.md` | One page per core module (entity, world, scene, collisions, raycast, game_action, process, inventory, sort, config, rendering, ui, audio, input, log, debug, serialization, multiplayer, util, strings) | ⬜ not started (material gathered, presentation module partial) |
| 5 | `agents/backends/*.md` | SDL / NDS / no_gui backend pages + comparison matrix | ⬜ not started (raw report saved: `agents/reports/backend_report_raw.md`) |
| 6 | `agents/build_and_tools.md` | Makefiles, lav_build, lavender_tools, tools2 specs, tests, docker | ⬜ not started (material gathered) |
| 7 | `agents/reports/` | Raw explore-agent reports for reference | 🟡 1 of 5 saved (backends) |

Method: parallel `explore` subagents (read-only) per domain, findings
cross-verified against the tree, then synthesized into the docs above.

---

## 2. ACCOMPLISHED (verified facts + agent findings)

### 2.1 Tree & size (verified by direct measurement, 2026-08-23)

| Area | Files | LOC |
|------|-------|-----|
| `core/` (engine) | 350 .c/.h | 43,571 |
| `sdl/` (backend) | 103 | 43,127 |
| `nds/` (backend) | 123 | 12,494 |
| `no_gui/` (backend) | 12 | 1,699 |
| `tests/` | 524 | — (munit-based) |
| `tools/` | 148 | — (mostly Python) |

Key file sizes (verified `wc -l`): `core/include/platform.h` **452** (121
PLATFORM_ lines, ≈50 functions in 7 groups); `core/platform_defines.h` 188;
`core/include/platform_defaults.h` 262; `core/include/defines.h` 2597;
`defines_weak.h` 635; `core/source/main.c` **13**; `game.c` **880**;
`client.c` 516; `sdl/source/sdl_game.c` **67**; `no_gui_game.c` 19.

**Platform-awareness per core module** (files referencing `platform.h`,
verified by grep): rendering 6, world 4, process 4, ui 3, game_action 3,
multiplayer 3, audio/debug/entity/inventory/serialization/util 1 each,
collisions/config/input/log/raycast/scene/sort **0**. 27 core .c files include
platform.h directly. → rendering/world/process are the platform-heavy modules;
collisions/config/log/scene/sort are pure logic.

### 2.2 Platform API surface (`core/include/platform.h`, 452 lines)

Function groups (agent A1 catalog + backend report signatures):
- **Audio (6):** `PLATFORM_initialize_audio`, `allocate_audio_effect`,
  `play_audio_effect`, `poll_audio_effects`, `play_audio__stream`,
  `is_audio__streaming`
- **Filesystem (8):** `initialize_file_system`, `allocate/release_serialization_request`,
  `open/close/read/write_file` (+ error enums), `get/set_position_in__file`, `get_directories`
- **Time (3):** `initialize_time`, `get_date_time`, `get_time_elapsed`
- **Game lifecycle (4):** `initialize_game`, `close_game`, `pre_render`, `post_render`
- **Log (6):** `update/clear_log__global/local/system`
- **TCP (9):** `tcp_begin/end`, `tcp_connect`, `tcp_poll_connect`, `tcp_server`,
  `tcp_poll_accept`, `tcp_close_socket`, `tcp_send`, `tcp_receive`
- **Graphics (10+):** `initialize_rendering__game`, `allocate_texture`
  (`_with__path`, `_with_size`), `update/use/release_texture`, texture-flag
  query fns, `allocate/release/release_all_sprites`, `render_sprite`,
  `render_gfx_window`, `compose_gfx_window`, `initialize/update_input`,
  `update_input__for__sprite`, sprite allocation count fns,
  `coredump/pre_abort/abort` (debug), `get_quantity_of__active_serialization_requests`

### 2.3 Bootstrap & game loop (`main.c` → `game.c`)

- `main()` (13 lines): `initialize_game(&game)` → `run_game(&game)` → `PLATFORM_close_game`.
- `initialize_game` (game.c): memsets Game, then inits ~15 fixed-capacity
  managers: graphics context, scene mgr (256), entity mgr (128), process mgr
  (256 procs, 16 priority levels), sort list mgr (256), hitbox context (256),
  aliased texture mgr (256), logs (global/local/system), timers, game-action
  logic table, inventory (64), camera/region/tile/chunk mgrs; then
  `PLATFORM_initialize_game` + `setup_platform_provided_graphics_windows`.
- `run_game`: iterates scenes via `m_load/enter/unload_scene_handler`; then
  waits out active serialization (save/load) requests.
- Frame: `manage_game__pre_render` = `PLATFORM_pre_render` (SDL: pump events +
  clear) → `poll_input` → reset tick timer → `poll_process_manager`;
  `manage_game__post_render` = `poll_input` → process cleanup pass →
  `PLATFORM_poll_audio_effects` → `PLATFORM_post_render` (SDL: swap window) →
  tick timer.

### 2.4 Process + game action system (core's execution engine)

- Process: run handler (per tick) + dispose handler, priority 0–15,
  `IS_CRITICAL` flag, enqueue/subprocess links. `poll_process_manager` walks a
  priority table; finished process → dispose handler.
- **Game actions are wrapped as processes**: on dispose,
  `m_process__dispose_handler__game_action__default` → `resolve_game_action`
  (dispatch by action kind: input, spawn, get, hitbox, …) → `complete_process`.
  This is how the whole engine mutates state (single- and multiplayer).

### 2.5 World / entity / scene / collision

- `manage_world`: `poll_collision_resolver_aabb` (128 AABB hitboxes;
  collision-node tree with 8-way adjacency; velocity-delta resolution +
  tile-touch/stair special cases) → `poll_hitbox_manager_for__movement`
  (gravity, `game_action__hitbox` pos/vel/accel) → `manage_world__entities`
  (128 entities; `m_entity_update_handler` is NULL **by design** — intentional consumer hook) →
  `poll_local_space_for__scrolling` (global_space vs local_space center, 3-axis).
- Entity: `_serialization_header` + `entity_data` (kind only) + 6 function
  pointers (dispose/update/enable/disable/serialize/deserialize). Kinds are
  only `None`/`Unknown` — no predefined entity types; entities created
  dynamically via game actions.
- World structure: global_space + local_spaces; chunk / region / tile systems
  (`chunk.c`, `chunk_pool.c`, `chunk_generator_table.c`, `region*.c`,
  `tile*.c`, `tile_logic_table.c`).

### 2.6 Presentation / IO / persistence (agent A3 — partial)

- **Rendering: retained model.** `Graphics_Window` (579-line header) composes
  `UI_Tile_Map` + `Sprite_Manager` + `Hitbox_Manager` **by UUID**;
  `graphics_window_manager.c` (1033 lines) manages windows by UUID. Render
  path: engine frame → graphics_window_manager → `p_PLATFORM_render_gfx_window`
  / `p_PLATFORM_compose_gfx_window` callbacks → backend.
- **UI:** `ui_manager` with focus tracking (`p_ui_element__focused`);
  elements: `ui_span`, `ui_window`, `ui_element`, `ui_text`; code-generated
  (see `tools/gen_ui_elements/`).
- **Audio:** `Audio_Effect` flags `IS_ACTIVE`, `RELEASE_ON_COMPLETE`, `LOOPING`.
- **Input:** `Input` struct — cursor + 15+ game-specific flags (forward,
  left/right, game_settings, lockon, use, use_secondary, examine, consume,
  turn_left/right) — i.e. input is game-action-oriented, not generic.
- **Log:** chain-linked `Log` of `Message` nodes (global/local/system).
- **Serialization:** UUID-based `serialization_header`, branding macros,
  deallocation tracking (`IDENTIFIER__UNKNOWN`).
- **Util:** `hash_map` (UUID-mapped pools), `bitmap`, `getter`, `enum_map`.
- **Multiplayer:** client/server, presence/host checks; TCP 512-byte payload.
- **Two string modules — mystery solved:** `lav_string` (80 lines) = parse
  strings→ints with length-limited conversions; `core_string` (14 lines) =
  strncpy variant returning length. Different jobs, not duplication.
- **Coupling:** rendering/UI reference entity-side types (Sprite_Manager,
  Hitbox_Manager, Game struct) directly — tight coupling, no clean seam.
- ⚠️ Gaps: UI .c deep-dive, full per-module LOC, complete global-state
  inventory were not finished (see §4).

### 2.7 Backends (agent A4 — full report saved to `agents/reports/backend_report_raw.md`)

- **Wiring:** each backend's `platform_defines.h` defines `PLATFORM__SDL` /
  `PLATFORM__NDS` / `PLATFORM__NO_GUI`; `core/platform_defines.h` branches on
  `#ifdef`; root Makefile `PLATFORM ?= sdl`; backend `Makefile.include`
  exports `INCLUDE_PLATFORM` / `SOURCE_PLATFORM` / `CFILES_*` / `OFILES_*` /
  `PLATFORM_LIBS` (SDL: `-lGL -lGLEW -lSDL2 -lcglm`; core adds `-lm`).
- **SDL (~43k):** ~34k is vendored: `glad.h` 16,837 + `glad.c` 9,458 (GLAD,
   OpenGL 3.0 loader) + `stb_image.h` 7,985. Real engine code:
   `sdl_defines.h` 9275; `sdl_sprite_manager.c` 5793; `sdl_texture_manager.c`
   5793; `sdl_gfx_window.c` 3785; `sdl_event.c` 2276; `sdl_render_world.c` 695;
   `gl_render_world.c` 500 (`GL_compose_world`, passthrough shader);
   `sdl_input.c` 534 + `gl_input.c` (viewport→game coords: clamp 0–255, flip Y,
   center cursor). **Audio stubbed in `TMP.c` — low priority**. **Multiplayer game-action handler (`m_PLATFORM_game_action_handler_for__multiplayer`) stubbed but OBSOLESCED** — core handles the full dispatch/receive/resolve lifecycle via function pointers installed in `begin_multiplayer_for__game()` (game.c:274-279): `m_game_action_handler__dispatch__multiplayer`, `_receive__multiplayer`, `_resolve__multiplayer`. The platform.h variant is never called. ⚠️ Discrepancy: raw report lists
   `sdl_game.c` as 2276 lines — **verified 67**; treat the 2276 as a report
   error (sdl_event.c is the 2276-line file).
- **NDS (~12.5k):** input via `scanKeys/keysHeld/keysDown/keysUp` + touch
  (`nds_input.c`); audio via mmEffect (`mmInitDefaultMem`, `mmLoadEffect`,
  `mmEffectRelease`); `nds_font.c` 3118 (largest real file), HUD bg 676,
  filesystem 518, `nds_ui.c` 494; build: devkitarm, `-lmm9 -lfilesystem
  -lfat -lnds9`, `ds_arm9.specs`.
- **no_gui (~1.7k):** `NOT_IMPL.c` (100 lines) stubs input/audio/rendering — **intentional** for headless server/debugging use case. Real: `no_gui_filesystem.c` 456, `no_gui_tcp_context.c` 377; gcc + clang-21.
- **Comparison matrix:** see saved report §4. Net: SDL = primary dev backend
   (full render/input/fs/time, audio low-priority, mp game-action handler obsolesced); NDS = most complete (full audio);
   no_gui = headless logic/fs/tcp only (render/input/audio stubs deliberate).

### 2.8 Build / tools / tests / docker (agent A5)

- **Makefiles:** root Makefile (`LAVENDER_DIR`, `PLATFORM ?= sdl`) +
  `Makefile.build` + per-area `Makefile.include` (core/sdl/no_gui/examples).
  Consumer projects: `lav_build` (shell wrapper; checks `LAVENDER_DIR`, sets
  `GAME_DIR`, runs `make -f $LAVENDER_DIR/Makefile`);
  `lav_build_client_and_server` (splits client/server via `-DIS_SERVER`,
  `build_client`/`build_server`, symlinks `compile_commands.json`).
- **Scaffolding:** `tools/lavender_tools/gen_lav_project.py` is the **active**
  scaffolder; `lav_new_project` is legacy/deprecated. Templates in
  `examples/template-files/`.
- **tools/lavender_tools (v1):** pyproject package — `gen_*.py` codegens,
  `analyze_pipeline.py`, `build.py`, and `lav_ai/` (`clang_server.py` =
  clangd LSP via pygls, `lav_ai_app.py`, `mcp_server.py`).
- **tools/editors:** `editor_map` (interactive Dear ImGui XML map editor,
  50KB+ single file — flagged for refactoring), `editor_ui`;
  `tools/gen_ui_elements/` = UI element codegen (base/containers/widgets).
- **tools2/docs/specs (v2 spec):** OVERVIEW, ARCHITECTURE, SCAN_FRAMEWORK
  (Layer 2: 5 domain analyzers w/ clangd verification), TOOL_REGISTRY,
  TRACEABILITY, CHECKPOINT, MCP_SERVER, CODEGEN, CI, MIGRATION.
- **Tests:** munit.h C framework; `tests/test_util.h` macros (`TEST_FUNCTION`,
  `INCLUDE_TEST__STATELESS`, `DEFINE_SUITE`, `MUNIT_OK/FAIL`); areas:
  core/sdl/no_gui/tools/editors/templates. ⚠️ Per-area test counts were left
  approximate by the agent — recount when resuming.
- **Docker:** `docker/platform/Dockerfile` = ubuntu:22.04 + mingw-w64 + libsdl2/glew/glm/mesa,
  `LAVENDER_DIR=/usr/share/lav_engine`; `docker/platform/{sdl,no_gui}` variants;
  `docker/platform/nds` empty (uses `devkitpro/devkitarm` image).
  `docker/sandbox/` = agent sandbox (`lav-sandbox` base + `lav-sandbox-agent`
  stages) + iron-proxy, one GitLab project per env file (see `docker/README.md`).
- **scripts/:** `digest_test_report.sh`, `process_test_reports.sh` (aider-based),
  `git_track.sh`, `cross_compare_c_modules.sh`.
- **Open build questions:** cause of README's "must run clean every build"
  (not found); root `compile_commands.json` currently empty `[]`.
- **Recent dev focus (doc-gen branch):** Layer 1 clangd LSP + Layer 2 scan
  tools, MCP integration, imgui map editor, tile-system refactor
  (multi-tilesheet, per-layer tilesheets), "AI slop cleanup" commits,
  lavender_tools packaging.

### 2.9 Explore-agent run status (task IDs for possible resume)

| Agent | Scope | Result | Task ID |
|-------|-------|--------|---------|
| A1 | platform API + game loop + dependency map | ✅ complete (numbers re-verified by me) | `ses_fcf975a1dffexZ9Dow4uLp5Bz4` |
| A2 | world/entity/scene/collision/process | ✅ complete | `ses_fcf962540ffeRxaqipPiZnErCx` |
| A3 | presentation stack (rendering/ui/audio/input/log/serialization/multiplayer/util) | 🟡 partial — module pages + render trace + coupling + 2-string answer done; UI .c deep-dive, full LOC, global-state inventory missing | `ses_fcf94db64ffeL25raO81yOMyHz` |
| A4 | backends | ✅ complete — report saved at `agents/reports/backend_report_raw.md` | `ses_fcf93d21cffelCFkkuwv0A1iTp` |
| A5 | build/tools/examples/tests/scripts/docker | 🟡 mostly complete — test counts approximate | `ses_fcf92b3d4ffebbpCaxi6CU1O63` |

First run (before context-window bump) produced 2 empty completions + 3
cancellations — all superseded by the second run above.

---

## 3. WHERE WE ARE (right now)

- `./agents/` exists with **only** `reports/backend_report_raw.md` inside.
- All exploration is done **except** the presentation-stack gaps (A3) and
  exact per-area test counts (A5).
- **No synthesis docs have been written yet** — nothing under `agents/`
  except the raw backend report. The heavy lifting (verification, cross-
  checking) is done; what remains is mostly writing.
- Known data-quality flags to fix while writing docs:
   1. `sdl_game.c` = 67 lines (not 2276 as in raw backend report).
   2. A1/A2 line-number citations from agent transcripts should be
      spot-checked before being quoted in final docs (file/LOC totals were
      verified; individual function line refs were not).
   3. "Clean every build" cause still unknown.
   4. SDL audio stub — low priority, not actively being worked on.
   5. `m_PLATFORM_game_action_handler_for__multiplayer` — obsolesced (core handles it via function pointers), stub in `TMP.c` is dead code.
   6. no_gui rendering/input/audio stubs — intentional design, not incomplete.
   7. `m_entity_update_handler` default NULL — intentional consumer hook, not a bug.

## 4. REMAINING (resume order)

1. **(Optional, cheap)** Resume A3 (`task_id` above) to finish: UI .c
   deep-dive, per-module LOC for presentation stack, complete global-state
   inventory. Alternatively do it inline — it's small.
2. **Write `agents/ARCHITECTURE.md`** — the roadmap doc:
   - Layer diagram: backends → platform.h → {game loop (game.c), process/game-action
     system, world (entity/scene/collision/chunk/tile), presentation
     (rendering/ui), IO (audio/input/log/serialization), support (util/sort/config)}.
   - Module dependency graph (use verified platform-awareness counts from §2.1).
   - Frame lifecycle from §2.3–2.5 (process poll → world update → render).
   - UUID-everywhere pattern; fixed-capacity managers; game-actions-as-processes.
3. **Write `agents/platform_api.md`** — from §2.2 + §2.7 wiring (merge A1 + A4).
4. **Write `agents/modules/*.md`** — 20 pages from §2.4–2.6 (A2 + A3 material;
   each: purpose / key types / key fns / deps / size / notes).
5. **Write `agents/backends/*.md`** — adapt `reports/backend_report_raw.md`
   (fix the sdl_game.c line-count error), add wiring + comparison matrix.
6. **Write `agents/build_and_tools.md`** — from §2.8.
7. **Write `agents/README.md`** — index + "how to read" guide + verified-facts
   appendix + open questions list (clean-every-build, SDL audio/mp stubs,
   entity update stub, NDS texture approach, no_gui use case).
8. Optional depth if time allows: recount tests per area; trace one concrete
   game-action end-to-end (input → process → world mutation → render).
