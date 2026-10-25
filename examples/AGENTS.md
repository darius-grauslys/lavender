# AGENTS.md — Lavender Examples

Guide for AI agents implementing, evaluating, and testing the example
projects in this folder. Examples are standalone projects that teach one
concept each (scene setup, world allocation, UI, ...) by **shadowing**
the engine's stock `implemented/` files.

DO NOT MODIFY core/ or any backend in $LAVENDER_DIR.
ONLY MODIFY FILES IN CWD: examples/

- Layout: `examples/<topic>/<NN__name>/` — `NN` zero-padded so examples
  sort in tutorial order (e.g. `scene/00__empty_scene`,
  `scene/01__allocate_world`, `scene/02__allocate_ui`).
- Planned examples are tracked in `examples/EXAMPLES_TO_MAKE.md`.
- Every example carries its own `README.md` with a numbered walkthrough —
  keep it in sync with the code.
- Reference games (working, non-example): `~/Projects/Projects__Lavender/`
  (TowerDefense, AncientsGame). When in doubt how the engine behaves, read
  them — and remember Lavender is C with no C++ and a strong naming
  convention (`get_/set_/is_/m_/f_`, `__` separators, `__u8/__u32F4` types).

## 1) Scaffolding: `lav_new_project`

```sh
cd examples/<topic>
$LAVENDER_DIR/tools/legacy/lav_new_project          # uses cwd, or pass a dir arg
```

`LAVENDER_DIR` is set in the environment. The script:

1. Mirrors **every `*/implemented/` directory** found under
   `$LAVENDER_DIR/core` into the new project, preserving the
   `source/` vs `include/` split (`core/source/scene/implemented` →
   `./source/scene/implemented`, same for `core/include/...`).
2. Copies `examples/Makefiles/{Makefile.build,Makefile.include}`.
3. Copies `core/assets` (stock world/ui/entity assets) into the project.
4. Writes `opencode.json` (filesystem MCP config).

The stock `implemented/` files are the **base functionality**: scene
registrar, chunk generator registrar, tile logic table registrar,
aliased/sprite animation registrars, entity/item/game_action/hitbox
registrars, `object.c`, `engine_config.h`, the `types/implemented/*`
enums, etc. They are copied **no-clobber** (`cp -n`): re-running the
script adds newly added stock files but never overwrites your edits.

Rule: **edit the project's shadowed copies, never `core/`.** The build
replaces engine definitions with the project's `implemented/` files.

## 2) Implementing an example

Conventions that matter (verified against `scene/01__allocate_world`):

- **`GEN-*-BEGIN/END` markers** delimit code-generation-managed sections
  (`GEN-LOGIC`, `GEN-FORWARD`, `GEN-LOAD`, `GEN-FRAME`, `GEN-PRE-RENDER`,
  `GEN-PER-RENDER`, `GEN-POST-RENDER`, `GEN-UNLOAD`, `GEN-INCLUDE`,
  `GEN-TABLES`, `GEN-RECORDS`, `GEN-UI-MANAGEMENT`). Keep the markers;
  add code only *inside* them.
- **`Tile_Kind` values map 1:1 onto the tilesheet** (top-left tile =
  index 0, left→right, top→bottom). Index 0 is `None` and **must be
  transparent** in the tileset, because the render kernel's texture index
  is 1-based and 0 means "skip/transparent".
- **Tilesets must be 256x256** (8x8 tiles of 32px) to match the
  `TEXTURE_FLAG__SIZE_256x256` grid math in the GL chunk compositor.
- **Scene lifecycle**: allocate resources in
  `m_load_scene_as__<name>_handler`, release them in
  `m_unload_scene_as__<name>_handler`.
- **World setup checklist** (for any world example):
  1. `register_aliased_textures(...)` (tileset loaded in the
     project's `aliased_texture_registrar.c`).
  2. `allocate_world_for__game(p_game)` — **returns bool, check it**.
  3. `initialize_world(p_game, world)`.
  4. `world->spawn_point = ...` — the default is OUT_OF_BOUNDS; without
     it the local space manager loads at garbage (0x200000).
  5. `register_chunk_generators(...)` (project's
     `chunk_generator_registrar.c`, registered under
     `Chunk_Generator_Kind__None`).
  6. `register_tile_logic_tables(...)`.
  7. `set_f_tile_render_kernel_of__world(...)` — `initialize_world` does
     NOT set a kernel; without one the renderer cannot pick textures.
     The kernel is called per tile and fills `index_of__texture`
     (1-based) per graphics window.
  8. `allocate_client_pool_for__game(p_game, 1)` +
     `set_dispatch_handler_process_for__create_client(...)` + an AABB
     hitbox for the local client.
  9. Allocate the world's graphics window:
     `set_graphics_window__tile_map__texture`, a camera,
     `share_hitbox_manager_with__graphics_window`, and
     `f_PLATFORM_compose_gfx_window = PLATFORM_compose_world`.
  10. In the enter handler: dispatch
      `dispatch_game_action__world__load_world_and__get_a_process` +
      `dispatch_game_action__world__load_client_and__get_a_process`, and
      `enqueue_process(load_client, load_world)` (client depends on world).
- **Frame loop (SDL platform)** — SDL does **not** compose/render for
  you; do it explicitly each tick:

  ```
  while(!poll__game_tick_timer(p_game));
  manage_game__pre_render(p_game);
  manage_world(p_game);                              // poll world/processes
  set_graphics_window_as__in_need_of__composition(win);
  compose_graphic_windows_in__graphics_window_manager(p_game);
  render_graphic_windows_in__graphics_window_manager(p_game);
  manage_game__post_render(p_game);
  ```

- **Render band is FIXED**: 4 chunks wide x 3 chunks tall around the
  local space manager center — `x in [lsm_x-2, lsm_x+1]`,
  `y in [lsm_y-3, lsm_y-1]`. The camera only translates the view; to
  center the band on chunk (cx,cy) use camera =
  `((cx - 0.5) * 64, (cy - 1.5) * 64)`.
- **Chunk generators yield**: Lavender is non-preemptive; a process that
  monopolizes a frame stalls the game. The stock pattern is to fill one
  z-slice (64 tiles) per invocation, persisting the z cursor in
  `process_value_bytes__u8`, then `complete_process` after the final
  slice.

## 3) Building

From the example directory (NOT the repo root):

```sh
lav_build -e PLATFORM=sdl   FLAGS="-ggdb -w" -j$(nproc)   # visual
lav_build -e PLATFORM=nogui FLAGS="-ggdb -w" -j$(nproc)   # headless
```

- Binary lands at `build/<platform>/<example-name>`; `assets/` is
  copied to `build/<platform>/` automatically.
- `lav_build clean` removes `build/<platform>/` **including `save/`** —
  the save dir must exist at runtime (the FS layer does not create
  parents), so `mkdir -p build/<platform>/save` after a clean.
- Rebuild after ANY header change — include shadowing means the project's
  headers are what compiles.

## 4) Running & evaluating

- **The engine never exits** — always run with a timeout:
  `timeout 12 build/sdl/<name>` (check exit/output, kill the rest).
- **Fresh world for reproducible generation tests**:
  `rm -rf build/sdl/save && mkdir -p build/sdl/save`.
- **Visual verification (SDL)**: have the scene call `gl_debug_screencap`
  once after N frames (e.g. 60) and run from `build/sdl/` so the PNG
  lands at `build/sdl/screen.png`. Then verify with PIL: count colors and
  map the tile grid (sample at `32*t + 16` px):

  ```python
  from PIL import Image
  im = Image.open('build/sdl/screen.png')
  for ty in range(6):
      print(''.join('R' if im.getpixel((32*tx+16, 32*ty+16))[0] > 128
                    else 'G' for tx in range(8)))
  ```

- **Headless verification (no_gui)**: stdout is sufficient — confirm the
  scene transition messages and absence of `debug_error` spam.
- **Tileset inspection/editing**: use the `tiles_*` MCP tools
  (`tile_info`, `tile_sample`, `tile_fill`, `tile_swap`, `tile_copy`,
  `tile_crop`, `tile_undo`) directly on `assets/world/*.png` — and copy
  the result into `build/sdl/assets/` (or rebuild, which re-copies).

## 5) Debugging with GDB

Two MCP tool families are available (assume you have the same):

- **Raw GDB** (`gdb_gdb_*`): `gdb_start` → `file <binary>` with cwd set
  to `build/sdl` → `run`. Breakpoint on `manage_game__post_render` with
  condition `is_client__active(get_p_local_client_by__from__game(&game))`
  to stop at a stable per-frame point; `continue` to step frames.
- **Game-aware lav-gdb** (`lav-gdb_*`): `session_start`,
  `navigate_step` (frame-stepping with a stuck-frame watchdog),
  `graphics_screenshot`, `process_list`, `process_pool`, `client_list`,
  `client_actions`, `ui_list`, `trace`. NOTE: `lav-gdb_session_stop`
  permanently kills that MCP server's GDB session (it cannot be
  restarted) — prefer raw GDB for iterative work.

Reliable inspection patterns (learned the hard way):

- Prefer **GDB Python** (`gdb.parse_and_eval`) over `set $var` /
  user-defined commands — convenience variables and `argN` are
  unreliable inside breakpoint command scripts under `-ggdb -w`.
- Many getters are `static inline` with no out-of-line symbol; `call`
  on them returns garbage. Read memory directly with casts, e.g.
  `(Client*)game.pM_ptr_array_of__clients[0]`, and `&game.process_manager`.
- `Process` is 72 bytes; pool slot = `(ptr - &game.process_manager.processes) / 72`.
  Table offsets are pointer deltas: `idx = (delim - &table.ptr_array_of__processes) / 8`.

Common failure signatures:

- **Black screen, world "loaded"**: global spaces stuck at
  `global_space_flags__u8 = 20` (IS_DIRTY | IS_AWAITING_CONSTRUCTION) →
  `is_global_space__active()` false → compositor skips them. Check the
  process pool/table for generator processes that never completed/were
  released (zombies with status 0, `p_generation_process` dangling).
- **LSM center = 0x200000 (2097152)**: spawn point never set.
- **`stat_chunk_file__tile, directories do not exist`**: `save/` missing.
- A `debug_error` with `CRASH_ON_ERROR` off is non-fatal and printed to
  stderr — clean runs should print nothing.

## 6) Tooling inventory (assumed available)

| Tool | Use |
|---|---|
| `bash` + file tools (read/write/edit/glob/grep) | everything on disk |
| `lav_build` (`tools/lav_build`) | build examples |
| `tools/legacy/*` | `lav_new_project` (scaffold), `lav_scene`, `lav_ui_builder`, `lav_update_ui`, `lav_new_game_action` |
| `gdb_gdb_*` MCP | raw GDB debugging |
| `lav-gdb_*` MCP | game-aware stepping/scanning (see caveats above) |
| `tiles_*` MCP | PNG tileset inspection/editing |
| `open-brain_*` MCP | long-term memory |
| `question` / `todowrite` / `task` | user interaction, planning, subagents |

## 7) Memory (OpenBrain)

- **Search before re-deriving**: `open-brain_search` /
  `open-brain_fetch` for prior engine facts (render band, GA flow,
  process pool quirks, tileset rules).
- **Capture after verifying**: save confirmed engine behaviors and
  root-cause findings as short observations (`open-brain_capture_thought`,
  keep each under ~500 tokens — the embedder rejects larger input).
  Tag engine-fact findings clearly (e.g. "Lavender ... (date)").

## 8) Definition of done

1. `lav_build` succeeds; `timeout` run shows no `debug_error` spam.
2. Behavior verified: screenshot pixel analysis (SDL) or stdout
   transitions (no_gui) prove the example does what its README says.
3. `README.md` walkthrough updated to match the code.
4. No build artifacts staged for commit (`build/`, `.cache/`, `save/`);
   the tileset in `assets/` and `build/sdl/assets/` match (md5).
5. New engine facts / gotchas saved to OpenBrain.
