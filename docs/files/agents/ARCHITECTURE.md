# Lavender Engine — Architecture Roadmap

> High-level map of the Lavender monolithic C game engine. Start here, then
> follow the links in [../README.md](../README.md) into per-module pages.
> All facts verified against source on 2026-08-23 (branch `doc-gen`).

---

## 1. What the engine is

A **cross-platform, fixed-point, process-driven retro game engine** in C.
Hardware is abstracted behind a single API surface
(`core/include/platform.h`, 452 lines, ~50 functions) implemented by three
backends:

| Backend | Dir | LOC | Status |
|---------|-----|-----|--------|
| SDL2 + OpenGL 3.0 | `sdl/` | 43,127 | primary dev backend; audio low-priority; multiplayer game-action handler obsolesced (core handles full lifecycle) |
| Nintendo DS (devkitARM) | `nds/` | 12,494 | most complete (real audio, touch) |
| Headless | `no_gui/` | 1,699 | logic/fs/TCP only; rendering/input/audio stubs intentional (designed for headless servers + debugging) |

The engine core (`core/`) is ~43.5k LOC across 350 .c/.h files
(**~23.4k in .c files**, the rest headers — the API surface is unusually
header-heavy: most modules are thin .c + large inline-getter headers).

Pulled from the author's *AncientsGame* project; the engine is mid-refactor
(recent work: tile-system multi-tilesheet, imgui map editor, clangd/MCP
tooling — see [build_and_tools.md](build_and_tools.md)).

---

## 2. Layer diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│ L5  GAME (your project)                                             │
│     scenes, game-action logic, entity kinds, UI layouts, assets     │
├─────────────────────────────────────────────────────────────────────┤
│ L4  PRESENTATION                                                    │
│     rendering/ (Graphics_Window, sprites, textures, fonts)          │
│     ui/        (UI_Manager, elements, tile maps)                    │
├─────────────────────────────────────────────────────────────────────┤
│ L3  SIMULATION                                                      │
│     world/ (spaces, chunks, tiles, regions, camera)                 │
│     entity/   collisions/ (AABB hitboxes)   raycast/   inventory/   │
├─────────────────────────────────────────────────────────────────────┤
│ L2  ENGINE SERVICES (the "engine" proper)                           │
│     game.c / client.c / main.c                                      │
│     process/ (prioritized process manager)                          │
│     game_action/ (the universal state-mutation protocol)            │
│     scene/ (scene state machine)                                    │
├─────────────────────────────────────────────────────────────────────┤
│ L1  IO + PERSISTENCE (cross-cutting)                                │
│     input/  audio/  log/  serialization/ (UUID+headers)             │
│     multiplayer/ (TCP sockets, client/server)                       │
├─────────────────────────────────────────────────────────────────────┤
│ L0a PLATFORM API                                                    │
│     core/include/platform.h (the contract, ~50 PLATFORM_* fns)      │
│     platform_defines.h / platform_defaults.h (compile-time config)  │
│     config/implemented/engine_config.h (user-overridable knobs)     │
├─────────────────────────────────────────────────────────────────────┤
│ L0b BACKENDS   sdl/  nds/  no_gui/   (implement the L1 contract)    │
├─────────────────────────────────────────────────────────────────────┤
│ SUPPORT (no layer, used everywhere)                                 │
│     util/ (bitmap, hash_map, enum_map)  sort/  debug/               │
│     strings: lav_string (parse) + core_string (copy)                │
│     math: vectors.h, degree.h, numerics.h (fixed-point i32F4/F20)   │
└─────────────────────────────────────────────────────────────────────┘
```

**Reading rule:** arrows point *down* — a module may only call into lower
layers. The only upward mechanism is **function pointers** (vtables): the
game layer installs handlers into engine structs (scene load/enter/unload,
entity update, process run/dispose, game-action dispatch/receive/resolve,
collision handlers, sort heuristics), and the engine calls them back.

---

## 3. The frame (how a tick flows)

```
main.c (13 lines)
  initialize_game(&game)            // ~15 managers, all fixed-capacity
  run_game(&game)
    └─ per frame:
       manage_game__pre_render:
         1. PLATFORM_pre_render        ← backend pumps events, clears screen
         2. poll_input                 ← input.c; backend filled raw flags
         3. reset tick timer
         4. poll_process_manager       ← THE HEART: runs every active
                                          process's run handler, in
                                          priority order (4 levels)
                                          (game logic happens HERE —
                                          via processes & game actions)
         5. manage_world (when in game scene):
              a. poll_collision_resolver_aabb   (128 AABB hitboxes)
              b. poll_hitbox_manager__movement  (gravity/accel)
              c. manage_world__entities         (128 entities; update
                                                  handler is NULL by design —
                                                  intentional consumer hook)
              d. poll_local_space_for__scrolling
       manage_game__post_render:
         5. poll_input (second sample)
         6. process cleanup pass     (dispose handlers for finished procs)
         7. PLATFORM_poll_audio_effects
         8. PLATFORM_post_render     ← backend composes+swaps windows
         9. tick timer
  PLATFORM_close_game
```

Scene flow wraps the frame loop: `run_game` walks the **Scene_Manager**
state machine — each scene kind has registered `m_Load_Scene` /
`m_Enter_Scene` / `m_Unload_Scene` handlers; switching scenes calls unload
→ load → enter. After the scene machine exits, `run_game` waits out pending
serialization (save/load) requests before returning.

---

## 4. The three load-bearing patterns

If you understand these three, you can navigate the whole codebase.

### 4.1 UUIDs everywhere (identity)
- Every serializable struct starts with a `Serialization_Header` carrying an
  `Identifier__u32` (a 32-bit hash of a 64-bit UUID; see
  `serialization/hashing.c`, 283 lines).
- `IDENTIFIER__UNKNOWN__u32` is the null/invalid sentinel;
  `is_identifier_u32__invalid()` tests it; `merge_identifiers_u32()` derives
  child UUIDs from parents.
- Managers are **contiguous fixed arrays**; lookup is by UUID via open
  addressing: `dehash_identitier_u32_in__contigious_array()`
  (note the original typos — `identitier`, `contigious` — they're in the API).
- Example: `Graphics_Window` does not point at its sprite/UI/hitbox
  managers — it stores `uuid_of__sprite_manager` / `uuid_of__ui_manager` /
  `uuid_of__hitbox_manager` and resolves them through
  `Sprite_Context` / `UI_Context` / `Hitbox_Context`.
  *Ownership* = window's own UUID == manager UUID; *sharing* = different
  valid UUID (see `does_graphics_window_own_a__sprite_manager()` etc.).

### 4.2 Game actions are the only way state changes (communication)
`Game_Action` (defines.h:2342) is a small struct:
`the_kind_of_game_action__this_action_is` (kind), `uuid_of__client__u32`
(origin), `uuid_of__game_action__responding_to` (request/response link),
`vector_3i32F4__broadcast_point` (proximity radius for broadcast actions),
and 8 flags (ALLOCATED, IN_OR_OUT_BOUND, WITH_PROCESS, PROCESSED_ON_INVOCATION,
RESPONSE, LOCAL, BROADCASTED, BAD_REQUEST).

Flow: **dispatch → (optionally TCP send) → receive → resolve → process**
- `dispatch_game_action()` → `p_game->m_game_action_handler__dispatch`
  (game-installed; decides local execution vs. send-to-server)
- server: `receive_game_action()` → `m_...__receive`
- resolution: `resolve_game_action()` → `m_...__resolve` → dispatches by
  kind through the **Game_Action_Logic_Table** (kind → handler)
- resolution spawns a **Process** whose **dispose handler** performs the
  actual mutation (spawn entity, move hitbox, change inventory, …) — i.e.
  *game actions are wrapped as processes*; the process system is the
  execution engine for everything, including save/load
  (`m_process__serialize_client__default` etc. live in `client.c`).

This is also the multiplayer protocol: the same actions travel over TCP
(`multiplayer/`, 512-byte packets, `MAX_SIZE_OF__TCP_PACKET BIT(9)` — must
stay a power of 2, the code uses `MASK(n)` arithmetic).

### 4.3 Fixed capacities, no core allocation (memory)
All pools are compile-time arrays in `defines.h` (2,597 lines — it defines
the structs too, not just constants):

| Constant | Value | Pool |
|---|---|---|
| `PROCESS_MAX_QUANTITY_OF` | 512 | processes |
| `PROCESS_MAX_PRIORITY_LEVEL` | 4 | priority levels (`PROCESS_PRIORITY__MINIMUM` = level-1) |
| `MAX_QUANTITY_OF__ENTITIES` | 128 | entities |
| `MAX_QUANTITY_OF__SPRITES` | 256 | sprites |
| `MAX_QUANTITY_OF__SPRITE_MANAGERS` | 4 | sprite managers |
| `MAX_QUANTITY_OF__HITBOX` | 256 | hitboxes |
| `MAX_QUANTITY_OF__HITBOX_MANAGERS` | 8 | hitbox manager instances |
| `MAX_QUANTITY_OF__HITBOX_AABB` | 256 | AABB collision entries |
| `MAX_QUANTITY_OF__TEXTURES` | 128 | textures |
| `MAX_QUANTITY_OF__ALIASED_TEXTURES` | 128 | aliased textures |
| `MAX_QUANTITY_OF__GAME_ACTIONS` | 512 | game actions |
| `MAX_QUANTITY_OF__INVENTORY` | 64 | inventories |
| `INVENTORY_ITEM_MAXIMUM_QUANTITY_OF` | 27 | item stacks per inventory |
| `ITEM_STACK_RECORD_MAX_QUANTITY_OF` | 256 | item stack records |
| `MAX_QUANTITY_OF__UI_ELEMENTS` | 128 | UI elements |
| `MAX_QUANTITY_OF__UI_MANAGERS` | (see platform_defaults.h) | UI managers |
| `SORT_LIST__MAXIMUM_QUANTITY_OF` | 64 | sort lists |
| `SORT_NODE__MAXIMUM_QUANTITY_OF` | 512 | sort nodes |
| `MAX_QUANTITY_OF__CLIENTS` | 4 | multiplayer clients |
| `MAX_QUANTITY_OF__TCP_SOCKETS` | 1 | TCP sockets |
| `MAX_SIZE_OF__TCP_PACKET` | BIT(9)=512 | packet size (power-of-2 required) |
| `MAX_QUANTITY_OF__TCP_PACKETS_PER__SOCKET` | BIT(8)=256 | packet queue |
| `MESSAGE_MAX_QUANTITY_OF` / `MESSAGE_MAX_LENGTH_OF` | 32 / 96 | log messages |
| `UI_TILE_MAP__SMALL/MEDIUM/LARGE__MAX_QUANTITY_OF` | 32 / 16 / 8 | UI tile maps |
| `PLATFORM__GFX_WINDOW__MAX_QUANTITY_OF` | 1 | platform-provided windows |

The `pM_` prefix marks the few real heap pointers in `Game`
(`pM_world`, `pM_clients`, `pM_ptr_array_of__clients`,
`pM_tcp_socket_manager`) — world and the client pool are malloc'd;
everything else is embedded.

Config override chain: **user** `engine_config.h` defines (all currently
commented out) → `platform_defaults.h` (`#ifndef` defaults) → backend
`platform_defines.h` (`PLATFORM__SDL`/`PLATFORM__NDS`/`PLATFORM__NO_GUI`).

---

## 5. The `Game` struct (root of everything)

`Game` is defined in `core/include/defines.h:2546` — every manager is a
member, so `Game` is effectively the whole engine's state:

```c
typedef struct Game_t {
    Input input;                        // single-player input (clients use their own)
    Scene_Manager scene_manager;        // scene state machine
    Hitbox_Context hitbox_context;      // all hitbox manager instances
    World *pM_world;                    // THE world (heap; NULL until allocated)
    Process_Manager process_manager;    // 512 processes, 4 priority levels
    Sort_List_Manager sort_list_manager;
    Path_List_Manager path_list_manager;
    Log log__global, log__local, log__system;
    Gfx_Context gfx_context;            // windows, sprites, textures, UI ctx, fonts
    PLATFORM_Audio_Context *p_PLATFORM_audio_context;
    PLATFORM_File_System_Context *p_PLATFORM_file_system_context;
    Game_Action_Logic_Table game_action_logic_table;
    Session_Token session_token;
    Timer__u32 tick__timer_u32, time__seconds__u32, time__nanoseconds__u32;
    Quantity__u32 max_quantity_of__clients;
    Quantity__u32 index_to__next_client_in__pool;
    Client *pM_clients;
    Client **pM_ptr_array_of__clients;  // [0] = local player
    TCP_Socket_Manager *pM_tcp_socket_manager;
    m_Game_Action_Handler m_game_action_handler__dispatch;  // game-installed
    m_Game_Action_Handler m_game_action_handler__receive;
    m_Game_Action_Handler m_game_action_handler__resolve;
    m_Process m_process__serialize_client;                  // game-installed
    m_Process m_process__deserialize_client;
    m_Process m_process__create_client;
    u32F20 time_elapsed__u32F20;
    u32F20 tick_accumilator__u32F20;
    Game_Flags__u32 game_flags__u32;   // GAME_FLAG__IS_SERVER_OR__CLIENT
} Game;
```

**World** (allocated by `allocate_world_for__game`) holds the simulation
managers: `entity_manager`, `global_space_manager`, `chunk_pool`,
`chunk_generator_table`, `collision_node_pool`, `tile_logic_context`,
`inventory_manager`, `item_manager`, `camera`, `repeatable_pseudo_random`
(original typo kept), `p_graphics_window_for__world`, `spawn_point`, and
game-installed callbacks: `f_hitbox_aabb_tile_touch_handler`,
`f_hitbox_aabb_collision_handler`, `f_tile_render_kernel`.

**Client** (multiplayer player state, one per connected player):
`game_action_manager__inbound` + `__outbound`, `local_space_manager`
(each client owns its own 8×8×1 grid of local spaces), `input_of__client`,
entity pointer, flags (ACTIVE/LOADED/SAVING/FAILED_TO_LOAD).

---

## 6. Module map (size + coupling)

Per-module core `.c` LOC (verified) and platform coupling (files that
include `platform.h`):

| Module | .c LOC | platform.h files | Role (one line) |
|---|---|---|---|
| `world/` | 3,685 | 4 | spaces/chunks/tiles/camera — the spatial model |
| `ui/` | 3,913 | 3 | UI managers/elements/tile maps (code-gen friendly) |
| `rendering/` | 3,030 | 6 | Graphics_Window, sprites, textures, fonts |
| `game_action/` | 2,710 | 3 | action kinds + logic table + TCP delivery |
| `collisions/` | 2,267 | 0 | AABB resolver + collision-node tree (pure logic) |
| `inventory/` | 995 | 1 | items, item stacks, inventories |
| `process/` | 964 | 4 | prioritized process manager |
| `sort/` | 924 | 0 | heuristic sort lists + opaque heap sort |
| `multiplayer/` | 682 | 3 | TCP sockets, client/server defaults |
| `serialization/` | 651 | 1 | UUID hashing, headers, pools, requests |
| `entity/` | 600 | 1 | entity struct + vtable + manager |
| `scene/` | 173 | 0 | scene state machine |
| `log/` | 153 | 0 | message queue (3 logs in Game) |
| `raycast/` | 114 | 0 | fixed-point DDA-ish ray stepping |
| `debug/` | 96 | 1 | debug_info/warning/error/abort (backend-implemented) |
| `util/` | 87 | 1 | bitmap, hash_map, enum_map |
| `input/` | 46 | 0 | input flags + cursor + write buffer |
| `audio/` | 39 | 1 | Audio_Effect flags wrapper |
| `config/` | — (include-only) | 0 | `engine_config.h` compile-time knobs |
| top-level | 2,282 | — | `game.c` 880, `degree.c` 678, `client.c` 516, strings, vectors, random, `main.c` 13 |

Dependency direction (who calls whom, verified by includes + calls):

&&&& 289 - 310 needs to be redone, just do a edge table instead of a ascii diagram.
```
                    game.c ─────────────────────────────┐
                     │  │  │  │  │                      │
   scene/ ──►  process/ ◄──► game_action/ ◄──► multiplayer/ ──► platform(TCP)
                     │         │                │
                     ▼         ▼                ▼
                  world/ ◄─ entity/       serialization/ ◄────────┐
                     │  │  │              (UUID + headers)        │
                     ▼  ▼  ▼                                      │
                collisions/  inventory/  raycast/                 │
                     │                                            │
                     ▼                                            │
              rendering/ ◄──► ui/    (both resolve managers by UUID)
                     │
                     ▼
              platform (rendering: 6 files — the heaviest platform consumer)

   client.c ──► game_action/ + world(local spaces) + serialization
   input/ audio/ log/ ──► platform (audio/log have PLATFORM_* update fns)
   util/ sort/ strings/math ──► nobody (leaf support)
```

Pure-logic modules (zero platform includes): `collisions`, `config`,
`input`, `log`, `raycast`, `scene`, `sort` — these are the easiest to read
and test in isolation (and are what `no_gui` exercises).

---

&&&& 318 - 340, this is prohibitively too many files for an agent to read needs to be a index table specifying when to read a file when trying to do X in Lavender.
## 7. Key files to read first (a guided path)

1. `core/source/main.c` (13) — the whole bootstrap in one screen.
2. `core/source/game.c` (880) — `initialize_game`, `run_game`,
   `manage_game__pre/post_render`. The frame.
3. `core/include/platform.h` (452) — the platform contract
   (see [platform_api.md](platform_api.md)).
4. `core/source/process/process_manager.c` (246) +
   `core/include/process/process.h` (343) — the execution engine.
5. `core/include/game_action/game_action.h` (179) +
   `core/source/game_action/*.c` (2,710) — the state-mutation protocol.
6. `core/include/defines.h` (2,597) — skim: all structs + capacities.
7. `core/source/world/world.c` + `core/include/world/world.h` (159) —
   the spatial simulation tick.
8. `core/source/client.c` (516) — multiplayer player state + save/load
   processes.
9. `core/source/rendering/graphics_window_manager.c` (1,033) — the render
   path into the platform.
10. `sdl/source/sdl_game.c` (67) + `sdl/source/sdl_event.c` (2,276) —
    how a backend plugs in.

---

## 8. Known rough edges (for orientation, not a bug list)

- `m_entity_update_handler` default is **NULL by design** — it is an intentional hook for engine consumers to install per-entity update logic. No default behavior is expected.
- `Game.input` has a `TODO: should memory condense these fields later`.
- `get_ticks_elapsed__game` is marked `TODO: obsolete, and inaccurate`.
- SDL audio is stubbed in `sdl/source/TMP.c` — **low priority**, not actively being worked on.
- SDL multiplayer game-action handler (`m_PLATFORM_game_action_handler_for__multiplayer`) is stubbed but **obsolesced** — core now handles the full dispatch/receive/resolve lifecycle via function pointers installed in `begin_multiplayer_for__game()` (game.c:274-279). The platform.h declaration is never called.
- Original typos are load-bearing names: `tick_accumilator__u32F20`, `Repeatable_Psuedo_Random`, `dehash_identitier_u32_in__contigious_array`, `get_process_priorty_of__process`, `save_world`'s parameter `p_PLATOFRM_file_system_context`. Don't "fix" them without a project-wide rename. **Priority: very low**.
- `core/include/game.h` header comment: *"This entire file is not implemented in core. You will need to compile with a backend."* — same for `debug/`. Core-only builds need a backend for these.
- README note: builds "must run clean every time" — cause never diagnosed (open question, see [../README.md](../README.md)).
- `// TODO: remove` in `platform.h` — **low priority**, ~12 functions whose responsibilities were absorbed into core's function-pointer architecture but declarations haven't been cleaned up.
- no_gui rendering/input/audio stubs — **intentional**, not incomplete. no_gui is designed as a headless backend for servers and debugging.

---

## 9. Where things are

| Doc | Contents |
|---|---|
| [platform_api.md](platform_api.md) | full PLATFORM_* contract + wiring |
| [modules/](modules/) | one page per core module |
| [backends/](backends/) | sdl / nds / no_gui + comparison |
| [build_and_tools.md](build_and_tools.md) | Makefiles, lav_build, tooling, tests, docker |
| [reports/backend_report_raw.md](reports/backend_report_raw.md) | raw backend explorer report |
| [../CHECKPOINT.md](../CHECKPOINT.md) | session history + open questions |
