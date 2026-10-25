# engine_config — User-overridable compile-time knob file

**Sources:** `core/include/config/implemented/engine_config.h` + `core/include/platform_defaults.h` + backend `sdl/include/platform_defines.h`

## Surface Concerns

`engine_config.h` is the top-level, user-overridable compile-time configuration
file for the Lavender engine. It defines a set of `#define` constants spanning I/O
paths, pool sizes, geometry dimensions, input codes, and client/sprite/input
capacities. All values are commented out so the file serves as **documentation**
of available knobs and their intended defaults.

- **Override chain** — `engine_config.h` includes the backend
  `platform_defines.h` *first*, so the effective precedence is: user-shaded
  `engine_config.h` → backend `platform_defines.h` (sdl/, no_gui/, nds/) →
  `#ifndef` fallbacks in `platform_defaults.h` → `#ifndef` fallbacks in
  `defines.h` (e.g., `MAX_QUANTITY_OF__GAME_ACTIONS`). Backend `#define`s win
  over `platform_defaults.h` for any knob they set (e.g.,
  `MAX_LENGTH_OF__IO_PATH` is 1024 on SDL vs. 128 in the defaults).

- **Documentation-as-code** — Because every knob is commented out, scanning this
  file reveals the full configuration surface and intended value ranges without
  needing to read downstream code.

- **Compound define dependency** — Active derived macros
  (`CHUNK__QUANTITY_OF__TILES`, `VOLUME_OF__LOCAL_SPACE_MANAGER`,
  `QUANTITY_OF__GLOBAL_SPACE`, …) are computed from base macros *by name* at
  include time, so redefining a base macro in an earlier layer updates the
  compounds. The commented-out compounds in this file are stale: they reference
  a double-underscore `CHUNK__WIDTH__AND_HEIGHT__BIT_SHIFT` (active layers
  define the single-underscore `CHUNK__WIDTH_AND__HEIGHT__BIT_SHIFT`), use a raw
  shift for `CHUNK__DEPTH`, and one line is typed `CHUNK_HEIGHT`.

- **TCP power-of-2 requirement** — `MAX_SIZE_OF__TCP_PACKET` must be a power of 2
  (`BIT(n)`). The `game_action__tcp_delivery` module derives `MASK(n)` bit masks
  from this value; non-power-of-2 inputs break TCP delivery for all subsystems.

- **Compile-time checks** — `platform_defaults.h` emits `#error` if
  `LOCAL_SPACE_MANAGER` dimensions are smaller than the
  `GFX_CONTEXT__RENDERING_*__IN_CHUNKS` dimensions.

## Public API Surface

The full configuration surface — the commented-out knobs in `engine_config.h` plus fallback-only knobs from `platform_defaults.h` (marked *) — grouped by concern:

- **I/O paths**: `MAX_LENGTH_OF__IO_PATH` (128), `PATH_SEPERATOR` ("/", typo)
- **Pool sizes**: `PROCESS_MAX_QUANTITY_OF` (512), `MAX_QUANTITY_OF__GAME_ACTIONS` (512), `MAX_QUANTITY_OF__ENTITIES` (128), `MAX_QUANTITY_OF__SPRITES` (256), `MAX_QUANTITY_OF__TEXTURES` (128)
- **Clients / sprites / input**: `MAX_QUANTITY_OF__CLIENTS` (4), `MAX_QUANTITY_OF__SPRITE_MANAGERS`* (4), `MAX_QUANTITY_OF__SYMBOLS_IN__INPUT_WRITING_BUFFER__BIT_SHIFT`* (3, i.e. 8 symbols)
- **TCP**: `MAX_QUANTITY_OF__TCP_SOCKETS` (1), `MAX_SIZE_OF__TCP_PACKET` (`BIT(9)`=512), `MAX_QUANTITY_OF__TCP_PACKETS_PER__SOCKET` (`BIT(8)`=256), error codes `TCP_ERROR__DESTINATION_OVERFLOW` (-1), `TCP_ERROR__QUEUE_FULL` (-2)
- **Camera**: `CAMERA_FULCRUM__WIDTH` (256), `CAMERA_FULCRUM__HEIGHT` (196)
- **Tile/chunk geometry**: `TILE__WIDTH_AND__HEIGHT__BIT_SHIFT` (3), chunk bit-shift constants, compounds `CHUNK__WIDTH`/`CHUNK__HEIGHT`/`CHUNK__DEPTH`/`CHUNK__QUANTITY_OF__TILES` (computed from base macros at include time)
- **Local/world space**: `LOCAL_SPACE_MANAGER__WIDTH`/`HEIGHT`/`DEPTH` (8/8/1), `LOCAL_SPACE__WIDTH_AND__HEIGHT_IN__TILES__BIT_SHIFT` (3), `QUANTITY_OF__GLOBAL_SPACE` (`VOLUME_OF__LOCAL_SPACE_MANAGER * MAX_QUANTITY_OF__CLIENTS`, 256 by default)
- **Graphics**: `GFX_CONTEXT__RENDERING_WIDTH`/`HEIGHT`/`DEPTH`__`IN_CHUNKS` (4/3/1), `UI_TILE__WIDTH_AND__HEIGHT__BIT_SHIFT` (3)
- **Input**: `QUANTITY_OF__INPUTS` (14), `PLATFORM_INPUT` (sequential input codes and bitmasks, large multi-line `#define`)
- **UI tile maps**: `UI_TILE_MAP__SMALL`/`MEDIUM`/`LARGE` variants with dimension and quantity constants
- **Platform**: `PLATFORM__GFX_WINDOW__MAX_QUANTITY_OF` (1)

## Known rough edges

- All knobs commented out; users must uncomment or pre-define to change anything.
- The commented-out compounds in `engine_config.h` are stale (wrong base-macro
  names); only the active compounds in `platform_defaults.h`/backends are correct.
- The `CHUNK__QUANTITY_OF_TILES` guard (single underscore) never matches the
  defined `CHUNK__QUANTITY_OF__TILES` (double underscore), so the guard
  provides no redefinition protection in any layer.
- Typos: `PATH_SEPERATOR` (missing E); `platform_defaults.h`'s
  `#ifndef CHUNK__HEIGHT` fallback defines `CHUNK_HEIGHT` (missing underscore),
  so backends omitting `CHUNK__HEIGHT` leave it undefined for consumers.
- `CHUNK__DEPTH`'s active default is `BIT(1)` = 2; `nds/include/platform_defines.h`
  is a legacy unguarded file (no `#ifndef` wrappers or include guards) hardcoding 1.
- `PLATFORM_INPUT` is a large multi-line `#define` replacing all input constants.

## Key Files Table

| File | Role |
|------|------|
| `core/include/config/implemented/engine_config.h` | User-overridable knob file (all commented out); includes backend `platform_defines.h` first |
| `core/include/platform_defaults.h` | `#ifndef` fallback defaults + compile-time dimension checks |
| `sdl/include/platform_defines.h` (and no_gui/, nds/, core/) | Active backend defaults; nds/ is the legacy unguarded file |
