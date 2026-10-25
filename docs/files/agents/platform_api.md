# platform API — The Lavender Hardware Contract

**Purpose:** The single declaration of all platform-dependent functions (~50 PLATFORM\_*/m\_PLATFORM\_\*) that abstract every hardware subsystem behind a back-end-implementable C interface.

**Sources:** `core/include/platform.h` (452 lines, verified), `core/platform_defines.h` (188 lines, verified), `core/include/platform_defaults.h` (262 lines, verified), `sdl/include/platform_defines.h` (190 lines, verified), `nds/include/platform_defines.h` (399 lines, verified), `no_gui/include/platform_defines.h` (190 lines, verified). Additional source cross-references cited inline below.

---

## 1. What the contract is

`core/include/platform.h` is the **only** header in core that is not self-contained. It declares approximately 50 functions whose implementations live exclusively in the selected backend. The file's own header comment (lines 14-35) states:

> "This file contains all function signatures which are NOT implemented in core. Their implementation is platform dependent and will be implemented by a backend such as OpenGL, or nds."

### The #error guard

Line 6 contains the compile-time sentinel:

```c
#ifndef PLATFORM_DEFINES_H
#error Cannot build AncientsGame without a backend implementation.
#endif
```

This fires whenever a translation unit includes `platform.h` but no backend has defined `PLATFORM_DEFINES_H`. Every backend's `include/platform_defines.h` opens with `#define PLATFORM_DEFINES_H` (e.g. `sdl/include/platform_defines.h:2`, `nds/include/platform_defines.h:2`, `no_gui/include/platform_defines.h:2`), making the guard fire-only when no backend include path is set.

### The IO_path type

Line 11:

```c
typedef char IO_path[MAX_LENGTH_OF__IO_PATH];
```

`MAX_LENGTH_OF__IO_PATH` is resolved through the config override chain: `engine_config.h` (all knobs currently commented out) → `platform_defaults.h:8` (`#ifndef` default of 128) → backend `platform_defines.h` which may override it (SDL: 1024, NDS: guarded by `#ifndef PLATFORM__IO`, no_gui: 1024). The discrepancy between `platform_defaults.h` (128) and the SDL/NOS_GUI backends (1024) is intentional: SDL and no_gui redefine it in their `platform_defines.h` lines 6-8. The NDS backend guards it behind `#ifndef PLATFORM__IO` (line 8) and sets it to 128.

### The "not implemented in core" invariant

Every `PLATFORM_*` function declared in this header is implemented in exactly one backend directory. The core may call them (from `game.c`, `input.c`, `audio/`, `log/`, `rendering/`, `multiplayer/`, `serialization/`), but never defines them. The exceptions are the stdlib re-declarations at `platform.h:168-177` (`free`, `malloc`, `memcpy`, `memset`, `abs`, `srand`, `rand`, `strncmp`, `strnlen`, `strncpy`) which are forward declarations for static-linking scenarios (e.g., NDS).

---

## 2. How wiring works end-to-end

### (a) Build-time backend selection

The root `Makefile` (line 33) defines the default target: when `PLATFORM` is unset, `make` prints available options (`sdl`, `nds`, `no_gui`) and exits. The `else` branch (line 48) is taken when `PLATFORM` is set, and invokes `Makefile.build`.

The chain:

1. `make -e PLATFORM=sdl` (or `nds`/`no_gui`)
2. `Makefile` → `Makefile.build` → `include $(BASE_DIR)/Makefile.include`
3. `Makefile.include` (line 2): `include $(BASE_DIR)/$(PLATFORM)/Makefile.include`
4. Backend `Makefile.include` exports:
   - `INCLUDE_PLATFORM` — the `-I` include path to the backend's `include/` dir (e.g., `$(BASE_DIR)/sdl/include`)
   - `SOURCE_PLATFORM` — the source directory containing the backend `.c` files
   - `CFILES_PLATFORM` / `OFILES_PLATFORM` — the list of backend `.c` files to compile
   - `PLATFORM_LIBS` — linker flags (SDL: `-lGL -lGLEW -lSDL2 -lcglm`; NDS: `-lmm9 -lfilesystem -lfat -lnds9`; no_gui: none)

The root `Makefile.include` line 29 sets `CFLAGS := -Wall -Wextra -O2 -march=$(uname_m)` as base; backend Makefiles may append.

### (b) Context-struct ownership model

Each backend `platform_defines.h` defines `PLATFORM__*` macros (e.g. `#define PLATFORM__SDL` at `sdl/include/platform_defines.h:4`). Within `core/platform_defines.h`, `#ifdef` chains on `PLATFORM__SDL` / `PLATFORM__NDS` / `PLATFORM__NO_GUI` to enable platform-specific code paths.

**Core rule: backends DEFINE the PLATFORM context struct types; core stores opaque pointers to them.** The struct definitions are in backend-specific headers (e.g., `sdl/include/rendering/sdl_gfx_context.h` defines `PLATFORM_Gfx_Context`, `PLATFORM_Texture`, `PLATFORM_Sprite`; the NDS equivalent defines them differently to use OAM hardware). Core only knows forward declarations:

```c
typedef struct PLATFORM_Gfx_Context_t PLATFORM_Gfx_Context;   // platform.h:448
typedef struct PLATFORM_Texture_t PLATFORM_Texture_t;        // platform.h:449
typedef struct PLATFORM_Sprite_t PLATFORM_Sprite;            // platform.h:450
```

The actual struct layouts are backend-defined and opaque to core.

**Where each pointer is stored** (verified in `defines.h`):

| Core struct | Field name | Type | Line in defines.h |
|---|---|---|---|
| `Game` | `p_PLATFORM_audio_context` | `PLATFORM_Audio_Context*` | 2562 |
| `Game` | `p_PLATFORM_file_system_context` | `PLATFORM_File_System_Context*` | 2563 |
| `Gfx_Context` | `p_PLATFORM_gfx_context` | `PLATFORM_Gfx_Context*` | 2530 |
| `TCP_Socket_Manager` | `p_PLATFORM_tcp_context` | `PLATFORM_TCP_Context*` | 1239 |
| `TCP_Socket` | `p_PLATFORM_tcp_socket` | `PLATFORM_TCP_Socket*` | 1224 |
| `TCP_Socket_Manager` | `p_PLATFORM_tcp_socket__pending_connection` | `PLATFORM_TCP_Socket*` | 1241 |
| `Graphics_Window` | `p_PLATFORM_gfx_window` | `PLATFORM_Graphics_Window*` | 2494 |
| `Sprite` | `p_PLATFORM_sprite` | `PLATFORM_Sprite*` | 805 |
| `Texture` | `p_PLATFORM_texture` | `PLATFORM_Texture*` | 755 |
| `Typer` | `p_PLATFORM_graphics_window__typer_target` | `PLATFORM_Graphics_Window*` | 930 |

**Accessor inline functions** (in `core/include/game.h` lines 253-284):
- `get_p_PLATFORM_file_system_context_from__game(Game*)` → `p_game->p_PLATFORM_file_system_context`
- `get_p_PLATFORM_audio_context_from__game(Game*)` → `p_game->p_PLATFORM_audio_context`
- `get_p_PLATFORM_gfx_context_from__game(Game*)` → `p_game->gfx_context.p_PLATFORM_gfx_context`
- `get_p_PLATFORM_tcp_context_from__game(Game*)` → `p_game->pM_tcp_socket_manager ? p_game->pM_tcp_socket_manager->p_PLATFORM_tcp_context : 0`

### (c) Where contexts are allocated and initialized

**`initialize_game()` in `core/source/game.c` (lines 91-150)** — the bootstrap sequence:
1. `memset(p_game, 0, sizeof(Game))` — zero-initialize the entire Game struct
2. Initialize core managers: `initialize_gfx_context`, `initialize_scene_manager`, `initialize_process_manager`, `initialize_sort_list_manager`, `initialize_hitbox_context`, `initialize_aliased_texture_manager`, `initialize_log` (3 instances)
3. Initialize timers: `initialize_timer_u32` for seconds and nanoseconds
4. Set default game-action handlers to single-player variants
5. Initialize game-action logic table and register offline actions
6. Call **`PLATFORM_initialize_game(p_game)`** — backend populates context pointers
7. Call **`setup_platform_provided_graphics_windows()`** — creates platform-defined windows

**Per-backend PLATFORM\_initialize\_game:**

- **SDL** (`sdl/source/sdl_game.c:25-47`): Initializes SDL subsystems (timer, video, audio, events), sets `p_game->gfx_context.p_PLATFORM_gfx_context = &__SDL_Gfx_Context`, `p_game->p_PLATFORM_file_system_context = &__SDL_file_system_context`, calls `PLATFORM_initialize_file_system_context`.
- **NDS** (`nds/source/nds_main.c:19-65`, `PLATFORM_main`): Sets all three context pointers from global externs (`_NDS_gfx_context`, `_NDS_file_system_context`, `_NDS_audio_context`), registers entity-specific sprite allocators, initializes UI manager, establishes scenes.
- **no_gui** (`no_gui/source/no_gui_game.c:7-17`): Sets `p_game->gfx_context.p_PLATFORM_gfx_context = 0`, `p_game->p_PLATFORM_file_system_context = &__NO_GUI_file_system_context`, calls `PLATFORM_initialize_file_system_context`.

**TCP context initialization** (in `core/source/game.c:251-290`, `begin_multiplayer_for__game`):
1. `p_game->pM_tcp_socket_manager = malloc(sizeof(TCP_Socket_Manager))`
2. `initialize_tcp_socket_manager(...)`
3. `p_game->pM_tcp_socket_manager->p_PLATFORM_tcp_context = PLATFORM_tcp_begin(p_game)` — the backend allocates and returns a `PLATFORM_TCP_Context*`
4. If NULL, aborts and calls `stop_multiplayer_for__game`

**`stop_multiplayer_for__game`** (game.c:292-298): Calls `PLATFORM_tcp_end(p_game)`, then `free(p_game->pM_tcp_socket_manager)`.

### (d) The per-backend platform_defines.h role

Each backend's `platform_defines.h` serves three purposes:
1. **Backend identification macro**: `#define PLATFORM__SDL` / `#define PLATFORM__NDS` / `#define PLATFORM__NO_GUI` (used in `core/platform_defines.h` for compile-time branching).
2. **Platform-specific constant overrides**: `MAX_LENGTH_OF__IO_PATH`, `PLATFORM__GFX_WINDOW__MAX_QUANTITY_OF`, `UI_TILE_MAP_*`, etc.
3. **Platform-specific texture flag definitions**: SDL defines `TEXTURE_FLAG__FORMAT__RGB888`/`RGBA8888`, `TEXTURE_FLAG__SDL_FLAGS__BIT_COUNT`; NDS defines `TEXTURE_FLAG__USE_OAM` and extensive OAM helper macros; no_gui mirrors SDL.

### (e) Core/platform_defines.h — compile-time branching

`core/platform_defines.h` (188 lines) provides compile-time defaults and derives concrete values from bit-shift constants. Key derivations:

- Chunk/tile sizes from `CHUNK__WIDTH_AND__HEIGHT__BIT_SHIFT` and `CHUNK__DEPTH__BIT_SHIFT`
- UI tile map sizes from `UI_TILE__WIDTH_AND__HEIGHT__BIT_SHIFT`
- Camera fulcrum from `CAMERA_FULCRUM__WIDTH/HEIGHT`
- Local space manager volumes from `LOCAL_SPACE_MANAGER__WIDTH/HEIGHT/DEPTH`
- `SDL_QUANTITY_OF__INPUTS` = `QUANTITY_OF__INPUTS + 1`, plus `SDL_INPUT_CODE_EQUIP` and `SDL_INPUT_EQUIP` constants
- Texture flag SDL extensions: `TEXTURE_FLAG__FORMAT__RGB888`, `TEXTURE_FLAG__FORMAT__RGBA8888`, `TEXTURE_FLAG__SDL_FLAGS__BIT_COUNT`, `TEXTURE_FLAG__BIT_SHIFT__SDL_FLAGS`
- `PLATFORM__GFX_WINDOW__MAX_QUANTITY_OF` defaults to 128

---

## 3. THE API SURFACE

Below is every `PLATFORM_*` / `m_PLATFORM_*` function in `core/include/platform.h`, organized by the header's `SECTION_*` groups.

### SECTION_audio (lines 41-63)

**`PLATFORM_initialize_audio`** (line 42)
```c
void PLATFORM_initialize_audio(PLATFORM_Audio_Context *p_PLATFORM_audio_context);
```
*Behavior:* Backend initializes its audio subsystem and any effect pool. Marked `// TODO: remove`. Called from NDS `nds_main.c:31`. SDL stub: empty in `TMP.c:22`. NDS: real init via `mmInitDefaultMem` in `nds_audio.c:37`. no_gui stub: empty in `NOT_IMPL.c:59`.

**`PLATFORM_allocate_audio_effect`** (line 48)
```c
Audio_Effect *PLATFORM_allocate_audio_effect(PLATFORM_Audio_Context *p_PLATFORM_audio_context);
```
*Behavior:* Returns a pointer to an available `Audio_Effect` slot, or NULL on failure. Backend must reserve one from a fixed-capacity pool. SDL stub: returns 0 (`TMP.c:28`). NDS real: scans `audio_effects[]` for inactive slot (`nds_audio.c:67`). no_gui stub: returns 0 (`NOT_IMPL.c:61`).

**`PLATFORM_play_audio_effect`** (line 51)
```c
void PLATFORM_play_audio_effect(PLATFORM_Audio_Context *p_PLATFORM_audio_context, Audio_Effect *p_audio_effect);
```
*Behavior:* Starts playing the given audio effect. SDL stub: empty (`TMP.c:33`). NDS: `mmEffectPlay` via `nds_audio.c:94`. no_gui stub: empty (`NOT_IMPL.c:64`).

**`PLATFORM_poll_audio_effects`** (line 55)
```c
void PLATFORM_poll_audio_effects(PLATFORM_Audio_Context *p_PLATFORM_audio_context);
```
*Behavior:* Called once per post-render frame (game.c:748). Backend checks all active effects for completion, releasing those with `RELEASE_ON_COMPLETE`. SDL stub: empty (`TMP.c:37`). NDS real: `nds_audio.c:244`. no_gui stub: empty (`NOT_IMPL.c:68`).

**`PLATFORM_play_audio__stream`** (line 58)
```c
void PLATFORM_play_audio__stream(PLATFORM_Audio_Context *p_PLATFORM_audio_context, enum Audio_Stream_Kind the_kind_of__audio_stream);
```
*Behavior:* Starts continuous background audio stream. SDL stub: empty (`TMP.c:40`). NDS: `nds_audio.c:265`. no_gui stub: empty (`NOT_IMPL.c:71`).

**`PLATFORM_is_audio__streaming`** (line 62)
```c
bool PLATFORM_is_audio__streaming(PLATFORM_Audio_Context *p_PLATFORM_audio_context);
```
*Behavior:* Returns true if a background audio stream is currently playing. SDL stub: returns false (`TMP.c:44`). NDS: `nds_audio.c:271`. no_gui stub: returns false (`NOT_IMPL.c:75`).

### SECTION_debug (lines 69-71)

**`PLATFORM_coredump`** (line 69)
```c
void PLATFORM_coredump(void);
```
*Behavior:* Backend writes a memory dump. SDL: `sdl/source/debug/sdl_debug.c:5`. NDS: `nds/source/debug/nds_debug.c:6`. no_gui: not defined (likely uses core default or linker stub).

**`PLATFORM_pre_abort`** (line 70)
```c
void PLATFORM_pre_abort(void);
```
*Behavior:* Called before abort in debug paths. SDL: `sdl_debug.c:13`. NDS: `nds_debug.c:11`.

**`PLATFORM_abort`** (line 71)
```c
void PLATFORM_abort(void);
```
*Behavior:* Backend-specific hard abort. SDL: `sdl_debug.c:16`. NDS: `nds_debug.c:15`.

### SECTION_entity (lines 77-79)

**`PLATFORM_render_entity`** (line 77)
```c
void PLATFORM_render_entity(Entity *entity, Game *game);
```
*Behavior:* Renders a single entity. Marked `// TODO: remove`. SDL: stub in `TMP.c`. NDS: `nds/source/rendering/nds_entity.c:10`. no_gui: stub in `NOT_IMPL.c`.

### SECTION_game_actions (lines 85-88)

**`m_PLATFORM_game_action_handler_for__multiplayer`** (line 86)
```c
void m_PLATFORM_game_action_handler_for__multiplayer(Game *p_this_game, Game_Action *p_game_action);
```
*Behavior:* Game-action handler for multiplayer. Marked `// TODO: remove, make PLATFORM_tcp PLATFORM_udp`.
**Status: OBSOLESCED.** Core now handles the full multiplayer game-action lifecycle via function-pointer callbacks installed at runtime in `begin_multiplayer_for__game()` (game.c:274–279): `m_game_action_handler__dispatch__multiplayer`, `m_game_action_handler__receive__multiplayer`, `m_game_action_handler__resolve__multiplayer`. These are the actual dispatch/receive/resolve paths used during the frame loop. The `m_PLATFORM_*` variant is declared in `platform.h` but **never called** from core — it exists only as stubs in `sdl/source/TMP.c:53` and `tests/*/source/PLATFORM.c`. Priority: **low**.

### SECTION_rendering (lines 93-159)

**`PLATFORM_put_char_in__typer`** (line 94)
```c
void PLATFORM_put_char_in__typer(Gfx_Context *p_gfx_context, Typer *p_typer, unsigned char letter);
```
*Behavior:* Renders a single character into a typer's output target. SDL: `sdl/source/rendering/sdl_typer.c:5`. NDS: `nds/source/rendering/font/nds_typer.c:10`. no_gui: stub in `NOT_IMPL.c:54`.

**`PLATFORM_allocate_sprite`** (line 99)
```c
PLATFORM_Sprite *PLATFORM_allocate_sprite(Gfx_Context *p_gfx_context, Graphics_Window *p_gfx_window, Sprite *p_sprite, Texture_Flags texture_flags_for__sprite);
```
*Behavior:* Allocates a backend sprite resource bound to a core Sprite. SDL: `sdl/source/rendering/sdl_sprite_manager.c:77`. NDS: `nds/source/rendering/sprite_manager.c:88`. no_gui: stub in `NOT_IMPL.c:78`.

**`PLATFORM_release_sprite`** (line 105)
```c
void PLATFORM_release_sprite(Gfx_Context *p_gfx_context, PLATFORM_Sprite *p_PLATFORM_sprite);
```
*Behavior:* Frees a backend sprite resource. SDL: `sdl_sprite_manager.c:122`. NDS: `nds/source/rendering/sprite_manager.c:216`. no_gui: stub in `NOT_IMPL.c:84`.

**`PLATFORM_release_all__sprites`** (line 109)
```c
void PLATFORM_release_all__sprites(PLATFORM_Gfx_Context *p_PLATFORM_gfx_context);
```
*Behavior:* Releases all backend sprites. SDL: stub in `TMP.c:74`. NDS: `nds/source/rendering/sprite_manager.c:228`. no_gui: stub in `NOT_IMPL.c:88`.

**`PLATFORM_render_sprite`** (line 117)
```c
void PLATFORM_render_sprite(Gfx_Context *p_gfx_context, Graphics_Window *p_gfx_window, Sprite *p_sprite, Vector__3i32F4 position_of__sprite__3i32F4);
```
*Behavior:* Renders a single sprite at the given position. SDL: `sdl/source/rendering/sdl_sprite.c:31`. NDS: `nds/source/rendering/nds_sprite.c:30`. no_gui: stub in `NOT_IMPL.c:92`.

**`PLATFORM_initialize_rendering__game`** (line 127)
```c
void PLATFORM_initialize_rendering__game(PLATFORM_Gfx_Context *gfx_context);
```
*Behavior:* Initializes the rendering subsystem. Called from NDS `nds_game.c:34` (via `NDS_initialize_gfx_context`). Marked `// TODO: remove`. SDL: not directly called (inlined into `sdl_game.c`'s `PLATFORM_initialize_game`). no_gui: not defined separately.

**`PLATFORM_allocate_texture`** (line 132)
```c
bool PLATFORM_allocate_texture(PLATFORM_Gfx_Context *p_PLATFORM_gfx_context, PLATFORM_Graphics_Window *p_PLATFORM_gfx_window, Texture_Flags texture_flags, Texture *p_OUT_texture);
```
*Behavior:* Allocates a backend texture of the given size/format. Returns true on failure. SDL: `sdl/source/rendering/sdl_texture_manager.c:102`. NDS: `nds/source/rendering/nds_texture_manager.c:43`. no_gui: stub in `NOT_IMPL.c:19` (returns 0/true).

**`PLATFORM_allocate_texture_with__path`** (line 141)
```c
bool PLATFORM_allocate_texture_with__path(PLATFORM_Gfx_Context *p_PLATFORM_gfx_context, PLATFORM_Graphics_Window *p_PLATFORM_gfx_window, Texture_Flags texture_flags, const char *c_str__path, Texture *p_OUT_texture);
```
*Behavior:* Same as `allocate_texture` but loads from a file path. SDL: `sdl/source/rendering/sdl_texture_manager.c:129`. NDS: not defined in `nds_texture_manager.c` (uses `allocate_texture` with pre-loaded data). no_gui: stub in `NOT_IMPL.c:25` (returns 0/true).

**`PLATFORM_update_texture`** (line 148)
```c
void PLATFORM_update_texture(Texture texture);
```
*Behavior:* Updates the backend texture data from the core Texture struct. SDL: not directly defined (texture update via `allocate_texture_with__path` reload). NDS: not defined. no_gui: not defined.

**`PLATFORM_use_texture`** (line 152)
```c
void PLATFORM_use_texture(PLATFORM_Gfx_Context *p_PLATFORM_gfx_context, Texture texture);
```
*Behavior:* Binds a texture for rendering. Marked `// TODO: remove`. SDL: `sdl/source/rendering/sdl_texture_manager.c:161`. NDS: `nds/source/rendering/nds_texture.c:242`. no_gui: not defined.

**`PLATFORM_release_texture`** (line 156)
```c
void PLATFORM_release_texture(PLATFORM_Gfx_Context *p_PLATFORM_gfx_context, Texture texture);
```
*Behavior:* Frees a backend texture resource. SDL: `sdl_texture_manager.c:170`. NDS: `nds/source/rendering/nds_texture_manager.c:76`. no_gui: stub in `NOT_IMPL.c:32`.

### SECTION_world / SECTION_core (lines 168-191)

**Stdlib re-declarations** (lines 168-177): `free`, `malloc`, `memcpy`, `memset`, `abs`, `srand`, `rand`, `strncmp`, `strnlen`, `strncpy`. For static-linking scenarios where standard libc functions must be resolved locally.

**`PLATFORM_initialize_time`** (line 179)
```c
void PLATFORM_initialize_time(void);
```
*Behavior:* Backend initializes its clock/timer subsystem. SDL: `SDL_initialize_time()` called from `sdl_game.c:26`. NDS: called from `nds_main.c`. no_gui: `PLATFORM_initialize_time()` in `time/no_gui_time.c`.

**`PLATFORM_get_date_time`** (line 180)
```c
void PLATFORM_get_date_time(Date_Time *p_date_time);
```
*Behavior:* Fills a `Date_Time` struct with the current wall-clock date/time. SDL: `sdl/source/time/sdl_time.c:81`. NDS: not defined. no_gui: not defined.

**`PLATFORM_get_time_elapsed`** (line 182)
```c
u32F20 PLATFORM_get_time_elapsed(Timer__u32 *p_timer__seconds__u32, Timer__u32 *p_timer__nanoseconds__u32);
```
*Behavior:* Returns elapsed time as a u32F20 fixed-point value since last call. Updates the timer accumulators in-place. SDL: `sdl/source/time/sdl_time.c:18`. NDS: not defined separately. no_gui: `time/no_gui_time.c`.

**`PLATFORM_initialize_game`** (line 186)
```c
void PLATFORM_initialize_game(Game *p_game);
```
*Behavior:* Called from `game.c:143` after core manager initialization. Backend sets up context pointers, initializes SDL/NDS subsystems, and calls `PLATFORM_initialize_file_system_context`. SDL: `sdl_game.c:25`. NDS: called from `nds_main.c:19` (as `PLATFORM_main`). no_gui: `no_gui_game.c:7`.

**`PLATFORM_close_game`** (line 187)
```c
void PLATFORM_close_game(Game *p_game);
```
*Behavior:* Called from `main.c:11` after the game loop exits. SDL: `sdl_game.c:49` (disposes gfx context, SDL_Quit). NDS: not defined. no_gui: `no_gui_game.c:19` (empty body).

**`PLATFORM_pre_render`** (line 189)
```c
void PLATFORM_pre_render(Game *p_game);
```
*Behavior:* Called at the start of each frame (`game.c:738`). Backend pumps input events and clears the screen. SDL: `sdl_game.c:55` (SDL_PumpEvents + SDL_poll + SDL_clear_screen). NDS: `nds_game.c:13` (swiWaitForVBlank). no_gui: stub in `NOT_IMPL.c:8` (empty).

**`PLATFORM_post_render`** (line 191)
```c
void PLATFORM_post_render(Game *game);
```
*Behavior:* Called at the end of each frame (`game.c:753`). Backend composes and swaps windows. SDL: `sdl_game.c:62` (SDL_GL_SwapWindow). NDS: `nds_game.c:17` (bgSetScroll + bgUpdate + oamUpdate). no_gui: stub in `NOT_IMPL.c:9` (empty).

### SECTION_ui (lines 196-266)

**`PLATFORM_allocate_gfx_window`** (line 197)
```c
PLATFORM_Graphics_Window *PLATFORM_allocate_gfx_window(Gfx_Context *p_gfx_context, Texture_Flags texture_flags_for__gfx_window);
```
*Behavior:* Creates a platform-defined graphics window. SDL: `sdl/source/rendering/sdl_gfx_window_manager.c:86`. NDS: not directly called (uses `NDS_initialize_gfx_context`). no_gui: stub in `NOT_IMPL.c:36` (returns 0).

**`PLATFORM_release_gfx_window`** (line 201)
```c
void PLATFORM_release_gfx_window(Gfx_Context *p_gfx_context, Graphics_Window *p_graphics_window);
```
*Behavior:* Destroys a platform graphics window. SDL: `sdl_gfx_window_manager.c:116`. NDS: not defined. no_gui: stub in `NOT_IMPL.c:42` (empty).

**`PLATFORM_get_provided_windows`** (line 217)
```c
Quantity__u32 PLATFORM_get_provided_windows(Gfx_Context *p_gfx_context, PLATFORM_Graphics_Window **ptr_array_of__PLATFORM_graphics_windows, Texture_Flags *array_of__texture_flags, Quantity__u32 quantity_of__ptrs_in_buffer__u32, Index__u32 index_of__offset__u32);
```
*Behavior:* Fills a caller-provided buffer with platform-provided window pointers, returning the number of windows omitted if the buffer was too small. Supports pagination via `index_of__offset__u32`. SDL: `sdl_gfx_window_manager.c:51`.

**`PLATFORM_compose_gfx_window`** (line 229)
```c
void PLATFORM_compose_gfx_window(Game *p_game, Graphics_Window *p_gfx_window);
```
*Behavior:* Composes (renders tiles/UI) of a gfx window. Called via the `f_PLATFORM_compose_gfx_window` function pointer stored in `Graphics_Window` (defines.h:2491). SDL: `sdl/source/rendering/sdl_gfx_window.c:104`. NDS: not directly defined (NDS uses its own rendering pipeline). no_gui: stub in `NOT_IMPL.c:46` (empty).

**`PLATFORM_compose_ui_span_in__gfx_window`** (line 236)
```c
void PLATFORM_compose_ui_span_in__gfx_window(Game *p_game, Graphics_Window *p_gfx_window, Quantity__u32 width_of__ui_tile_span, Quantity__u32 height_of__ui_tile_span, Index__u32 index_x__u32, Index__u32 index_y__u32);
```
*Behavior:* Renders a UI tile span within a graphics window. SDL: `sdl_gfx_window.c:112`. NDS: not defined. no_gui: not defined.

**`PLATFORM_compose_world`** (line 248)
```c
void PLATFORM_compose_world(Game *p_game, Graphics_Window *p_gfx_window);
```
*Behavior:* Renders world tiles and local player data within a graphics window. SDL: `sdl_gfx_window.c` (via render path). no_gui: stub in `NOT_IMPL.c:11` (empty, different signature with explicit parameters). NDS: not defined.

**`PLATFORM_project_gfx_window`** (line 256)
```c
void PLATFORM_project_gfx_window(Game *p_game, Graphics_Window *p_gfx_window);
```
*Behavior:* Renders a gfx window via 3D projection. SDL: `sdl/source/rendering/sdl_gfx_window.c:128`. NDS: not defined. no_gui: not defined.

**`PLATFORM_project_world`** (line 260)
```c
void PLATFORM_project_world(Game *p_game, Graphics_Window *p_gfx_window);
```
*Behavior:* Renders world data via 3D projection. SDL: `sdl/source/rendering/sdl_gfx_window.c`. NDS: not defined. no_gui: not defined.

**`PLATFORM_render_gfx_window`** (line 264)
```c
void PLATFORM_render_gfx_window(Game *p_game, Graphics_Window *p_gfx_window);
```
*Behavior:* Final render pass for a graphics window. Called via the `f_PLATFORM_render_gfx_window` function pointer in `Graphics_Window` (defines.h:2492). SDL: `sdl_gfx_window.c:128`. NDS: not defined. no_gui: stub in `NOT_IMPL.c:50` (empty).

### SECTION_scene (line 270)

No functions declared in this section.

### SECTION_serialization (lines 272-347)

**`PLATFORM_initialize_file_system_context`** (line 277)
```c
void PLATFORM_initialize_file_system_context(Game *p_game, PLATFORM_File_System_Context *p_PLATOFRM_file_system_context);
```
*Behavior:* Initializes the file system context and registers serialization processes. Note the typo: parameter is `p_PLATOFRM_file_system_context` (missing 'F'). Marked `// TODO: remove`. SDL: `serialization/sdl_filesystem.c:19`. NDS: `nds/source/serialization/nds_filesystem.c:94`. no_gui: `no_gui/source/serialization/no_gui_filesystem.c`.

**`PLATFORM_get_base_directory`** (line 284)
```c
Quantity__u32 PLATFORM_get_base_directory(IO_path path);
```
*Behavior:* Fills `path` with the engine's base directory and returns the path length. SDL: `sdl/source/serialization/sdl_filesystem.c:13`. NDS: not defined. no_gui: not defined.

**`PLATFORM_access`** (line 286)
```c
int PLATFORM_access(const char *p_c_str, IO_Access_Kind io_access_kind);
```
*Behavior:* File existence/access check. SDL: `sdl/source/serialization/unix/unix_filesystem.c:25` (also `win64_file_system.c:22`). NDS: `nds_filesystem.c:22`. no_gui: not defined (uses standard `access()`).

**`PLATFORM_opendir`** (line 287)
```c
PLATFORM_Directory *PLATFORM_opendir(const char *p_c_str);
```
*Behavior:* Opens a directory for iteration. SDL: `unix_filesystem.c:33`, `win64_file_system.c:35`. NDS: not defined. no_gui: `no_gui/source/serialization/no_gui_filesystem.c`.

**`PLATFORM_closedir`** (line 288)
```c
void PLATFORM_closedir(PLATFORM_Directory *p_dir);
```
*Behavior:* Closes a previously opened directory. SDL: `unix_filesystem.c:41`. NDS: `nds_filesystem.c:39`. no_gui: `no_gui_filesystem.c`.

**`PLATFORM_mkdir`** (line 289)
```c
bool PLATFORM_mkdir(const char *p_c_str, uint32_t file_code);
```
*Behavior:* Creates a directory. SDL: `unix_filesystem.c:51`, `win64_file_system.c:57`. NDS: `nds_filesystem.c:48`. no_gui: `no_gui_filesystem.c`.

**`PLATFORM_append_base_directory_to__path`** (line 291)
```c
void PLATFORM_append_base_directory_to__path(PLATFORM_File_System_Context *p_PLATFORM_file_system_context, char *p_c_str_path, Index__u32 *p_index_of__path_end);
```
*Behavior:* Prepends the base directory to a user-provided path, setting `p_index_of__path_end` to the resulting path length. NDS: `nds_filesystem.c:150`. SDL: `sdl_filesystem.c` (implicit in `PLATFORM_initialize_file_system_context`). no_gui: `no_gui_filesystem.c`.

**`PLATFORM_get_quantity_of__active_serialization_requests`** (line 296)
```c
Quantity__u32 PLATFORM_get_quantity_of__active_serialization_requests(PLATFORM_File_System_Context *p_PLATFORM_file_system_context);
```
*Behavior:* Returns count of active serialization requests. Called from `game.c:725` to drain pending saves/loads before exiting. SDL: `sdl_filesystem.c:232`. NDS: `nds_filesystem.c:73`. no_gui: `no_gui_filesystem.c`.

**`PLATFORM_allocate_serialization_request`** (line 299)
```c
Serialization_Request *PLATFORM_allocate_serialization_request(PLATFORM_File_System_Context *p_PLATOFRM_file_system_context);
```
*Behavior:* Allocates a serialization request slot. Note the typo: `p_PLATOFRM_file_system_context` again. SDL: `sdl_filesystem.c:69`. NDS: `nds_filesystem.c:155`. no_gui: `no_gui_filesystem.c`.

**`PLATFORM_release_serialization_request`** (line 302)
```c
void PLATFORM_release_serialization_request(PLATFORM_File_System_Context *p_PLATOFRM_file_system_context, Serialization_Request *p_serialization_request);
```
*Behavior:* Releases a serialization request slot. Typo: `p_PLATOFRM_file_system_context`. SDL: `sdl_filesystem.c`. NDS: `nds_filesystem.c:210`. no_gui: `no_gui_filesystem.c`.

**`PLATFORM_open_file`** (line 306)
```c
enum PLATFORM_Open_File_Error PLATFORM_open_file(PLATFORM_File_System_Context *p_PLATFORM_file_system_context, const char *p_path, const char *p_flags, Serialization_Request *p_serialization_request);
```
*Behavior:* Opens a file for serialization. SDL: `sdl_filesystem.c:112`. NDS: `nds_filesystem.c`. no_gui: `no_gui_filesystem.c`.

**`PLATFORM_close_file`** (line 312)
```c
void PLATFORM_close_file(PLATFORM_File_System_Context *p_PLATFORM_file_system_context, Serialization_Request *p_serialization_request);
```
*Behavior:* Closes a file opened by `PLATFORM_open_file`. SDL: `sdl_filesystem.c:130`. NDS: `nds_filesystem.c:284`. no_gui: `no_gui_filesystem.c`.

**`PLATFORM_write_file`** (line 316)
```c
enum PLATFORM_Write_File_Error PLATFORM_write_file(PLATFORM_File_System_Context *p_PLATFORM_file_system_context, u8 *source, Quantity__u32 length_of__data, Quantity__u32 quantity_of__writes, void *p_file_handler);
```
*Behavior:* Writes data to a file opened for serialization. SDL: `sdl_filesystem.c:144`. NDS: `nds_filesystem.c:298`. no_gui: `no_gui_filesystem.c`.

**`PLATFORM_read_file`** (line 323)
```c
enum PLATFORM_Read_File_Error PLATFORM_read_file(PLATFORM_File_System_Context *p_PLATFORM_file_system_context, u8 *destination, Quantity__u32 *p_length_of__data_to_read, Quantity__u32 quantity_of__reads, void *p_file_handler);
```
*Behavior:* Reads data from a file. SDL: `sdl_filesystem.c:167`. NDS: `nds_filesystem.c:333`. no_gui: `no_gui_filesystem.c`.

**`PLATFORM_get_position_in__file`** (line 333)
```c
Index__u32 PLATFORM_get_position_in__file(PLATFORM_File_System_Context *p_PLATFORM_file_system_context, void *p_file_handler);
```
*Behavior:* Returns current file position (or -1 on error). SDL: `sdl_filesystem.c:201`. NDS: `nds_filesystem.c:369`. no_gui: `no_gui_filesystem.c`.

**`PLATFORM_set_position_in__file`** (line 337)
```c
bool PLATFORM_set_position_in__file(PLATFORM_File_System_Context *p_PLATFORM_file_system_context, Index__u32 position_in__file_u32, void *p_file_handler);
```
*Behavior:* Sets file read/write position. SDL: `sdl_filesystem.c:216`. NDS: `nds_filesystem.c:384`. no_gui: `no_gui_filesystem.c`.

**`PLATFORM_get_directories`** (line 342)
```c
Quantity__u32 PLATFORM_get_directories(PLATFORM_File_System_Context *p_PLATFORM_file_system_context, IO_path path, char *p_directory_name__buffer, Quantity__u32 size_of__directory_name__buffer, Quantity__u32 max_length_of__directory_name);
```
*Behavior:* Lists directory entries into a caller buffer. SDL: `unix_filesystem.c:55`, `win64_file_system.c:61`. NDS: not defined. no_gui: `no_gui_filesystem.c`.

### SECTION_input (lines 351-354)

**`PLATFORM_poll_input`** (line 352)
```c
void PLATFORM_poll_input(Game *p_game, Input *p_input);
```
*Behavior:* Fills the Input struct with current input state. SDL: `sdl/source/input/sdl_input.c:315`. NDS: `nds/source/input/nds_input.c:5` (uses `scanKeys`/`keysHeld`/`keysDown`/touch). no_gui: stub in `NOT_IMPL.c:98` (empty).

### SECTION_inventory (line 358)

No functions declared. File system functions handle inventory serialization.

### SECTION_log (lines 362-375)

All six log functions are marked `// TODO: remove` — the core `Log` is now managed in-process within `Game` with direct message writes.

**`PLATFORM_update_log__global`** (line 364)
```c
bool PLATFORM_update_log__global(Game *p_game);
```
*Behavior:* Backend renders the global log (e.g., on-screen). All stubbed. SDL: `TMP.c:166`. NDS: `nds/source/nds_log.c:9`. no_gui: `TMP.c:166`.

**`PLATFORM_update_log__local`** (line 365)
```c
bool PLATFORM_update_log__local(Game *p_game);
```
*Behavior:* Backend renders the local log. SDL: `TMP.c:167`. NDS: `nds_log.c:22`. no_gui: `TMP.c:167`.

**`PLATFORM_update_log__system`** (line 366)
```c
bool PLATFORM_update_log__system(Game *p_game);
```
*Behavior:* Backend renders the system log. SDL: `TMP.c:168`. NDS: `nds_log.c:35`. no_gui: `TMP.c:168`.

**`PLATFORM_clear_log__global`** (line 370)
```c
bool PLATFORM_clear_log__global(Game *p_game);
```
*Behavior:* Clears the global log on the backend display. SDL: `TMP.c:170`. NDS: `nds_log.c:48`. no_gui: `TMP.c:170`.

**`PLATFORM_clear_log__local`** (line 371)
```c
bool PLATFORM_clear_log__local(Game *p_game);
```
*Behavior:* Clears the local log on the backend display. SDL: `TMP.c:171`. NDS: `nds_log.c:60`. no_gui: `TMP.c:171`.

**`PLATFORM_clear_log__system`** (line 372)
```c
bool PLATFORM_clear_log__system(Game *p_game);
```
*Behavior:* Clears the system log on the backend display. SDL: `TMP.c:172`. NDS: `nds_log.c:72`. no_gui: `TMP.c:172`.

### SECTION_multiplayer (lines 378-443)

**`PLATFORM_tcp_begin`** (line 381)
```c
PLATFORM_TCP_Context *PLATFORM_tcp_begin(Game *p_game);
```
*Behavior:* Initializes the backend TCP subsystem, returns a `PLATFORM_TCP_Context*` to be stored in `TCP_Socket_Manager.p_PLATFORM_tcp_context`. Called from `game.c:267` via `begin_multiplayer_for__game`. SDL: `sdl/source/multiplayer/unix/sdl_unix_tcp_context.c:6` (also `win64/sdl_win64_tcp_context.c:9` for Windows). NDS: not defined. no_gui: `no_gui/source/multiplayer/no_gui_tcp_context.c:40`.

**`PLATFORM_tcp_end`** (line 384)
```c
void PLATFORM_tcp_end(Game *p_game);
```
*Behavior:* Shuts down the backend TCP subsystem. Called from `game.c:295` via `stop_multiplayer_for__game`. SDL: `sdl_unix_tcp_context.c:20`, `sdl_win64_tcp_context.c:27`. NDS: not defined. no_gui: `no_gui_tcp_context.c:54`.

**`PLATFORM_tcp_connect`** (line 390)
```c
PLATFORM_TCP_Socket *PLATFORM_tcp_connect(PLATFORM_TCP_Context *p_PLATFORM_tcp_context, IPv4_Address *p_ipv4_address);
```
*Behavior:* Opens an outgoing TCP connection. Returns NULL on failure. Called from `tcp_socket.c`. SDL: `sdl/source/multiplayer/sdl_tcp_context.c:101`. NDS: not defined. no_gui: `no_gui_tcp_context.c:112`.

**`PLATFORM_tcp_poll_connect`** (line 399)
```c
TCP_Socket_State PLATFORM_tcp_poll_connect(PLATFORM_TCP_Socket *p_PLATFORM_tcp_socket);
```
*Behavior:* Polls a connecting socket's status. Called every frame during connection. SDL: `sdl_tcp_context.c:157`. NDS: not defined. no_gui: `no_gui_tcp_context.c:166`.

**`PLATFORM_tcp_server`** (line 407)
```c
PLATFORM_TCP_Socket *PLATFORM_tcp_server(PLATFORM_TCP_Context *p_PLATFORM_tcp_context, Index__u16 port);
```
*Behavior:* Creates a listening socket on the given port. Returns NULL on failure. SDL: `sdl_tcp_context.c:181`. NDS: not defined. no_gui: `no_gui_tcp_context.c:190`.

**`PLATFORM_tcp_close_socket`** (line 414)
```c
bool PLATFORM_tcp_close_socket(PLATFORM_TCP_Context *p_PLATFORM_tcp_context, PLATFORM_TCP_Socket *p_PLATFORM_tcp_socket);
```
*Behavior:* Closes a TCP socket. SDL: `unix/sdl_unix_tcp_socket.c:26` (also `win64/sdl_win64_tcp_socket.c:26`). NDS: not defined. no_gui: `no_gui_tcp_context.c:250`.

**`PLATFORM_tcp_poll_accept`** (line 422)
```c
PLATFORM_TCP_Socket *PLATFORM_tcp_poll_accept(PLATFORM_TCP_Context *p_PLATFORM_tcp_context, PLATFORM_TCP_Socket *p_PLATFORM_tcp_socket__server, IPv4_Address *p_ipv4);
```
*Behavior:* Accepts an incoming connection from the server socket. Returns NULL if none available. SDL: `sdl_tcp_context.c:243`. NDS: not defined. no_gui: `no_gui_tcp_context.c:271`.

**`PLATFORM_tcp_send`** (line 430)
```c
i32 PLATFORM_tcp_send(PLATFORM_TCP_Socket *p_PLATFORM_tcp_socket, u8 *p_bytes, Quantity__u32 length_of__bytes);
```
*Behavior:* Sends data over a TCP socket. Returns bytes sent or -1 on error. SDL: `sdl_tcp_context.c:316`. NDS: not defined. no_gui: `no_gui_tcp_context.c:343`.

**`PLATFORM_tcp_recieve`** (line 440)
```c
i32 PLATFORM_tcp_recieve(PLATFORM_TCP_Socket *p_PLATFORM_tcp_socket, u8 *p_bytes, Quantity__u32 length_of_bytes_in__destination);
```
*Behavior:* Receives data from a TCP socket. Returns bytes received or `TCP_ERROR__XXX`. **Note the typo:** `recieve` instead of `receive` (the function name itself is misspelled). SDL: `sdl_tcp_context.c:332`. NDS: not defined. no_gui: `no_gui_tcp_context.c:359`.

### SECTION_defines (lines 448-451)

Opaque forward declarations for backend-defined types:
```c
typedef struct PLATFORM_Gfx_Context_t PLATFORM_Gfx_Context;
typedef struct PLATFORM_Texture_t PLATFORM_Texture_t;
typedef struct PLATFORM_Sprite_t PLATFORM_Sprite;
```
These are forward declarations — the actual struct bodies are in backend headers (e.g., `sdl/include/rendering/sdl_gfx_context.h`).

---

## 4. Per-backend implementation status

| Function Group | SDL | NDS | no_gui |
|---|---|---|---|
| Audio (6) | stubbed (TMP.c) | real (nds_audio.c) | stubbed (NOT_IMPL.c) |
| Debug (3) | real (sdl_debug.c) | real (nds_debug.c) | not defined (core defaults) |
| Entity (1) | stubbed (TMP.c) | real (nds_entity.c) | stubbed (NOT_IMPL.c) |
| Game actions (1) | **obsolesced** (see above) | real (nds_game_action.c) | stubbed (NOT_IMPL.c) |
| Rendering — sprites/typer | real (sdl_sprite.c, sdl_typer.c) | real (nds_sprite.c, nds_typer.c) | stubbed (NOT_IMPL.c) |
| Rendering — textures | real (sdl_texture_manager.c) | real (nds_texture_manager.c) | stubbed (NOT_IMPL.c) |
| Rendering — gfx windows | real (sdl_gfx_window.c, sdl_gfx_window_manager.c) | partial (nds_gfx_window.c) | stubbed (NOT_IMPL.c) |
| Rendering — compose/world/project | real (sdl_gfx_window.c, gl_render_world.c) | partial (nds_chunk.c) | stubbed (NOT_IMPL.c) |
| Filesystem (8) | real (sdl_filesystem.c + unix/win64) | real (nds_filesystem.c) | real (no_gui_filesystem.c) |
| Time (3) | real (sdl_time.c) | real (via nds_main.c/nds_game.c) | real (no_gui_time.c) |
| Game lifecycle (4) | real (sdl_game.c) | real (nds_main.c + nds_game.c) | real (no_gui_game.c) |
| Log (6) | stubbed (TMP.c) | real (nds_log.c) | stubbed (TMP.c) |
| TCP (9) | real (sdl_tcp_context.c + unix/win64) | stubbed | real (no_gui_tcp_context.c) |
| Input (1) | real (sdl_input.c) | real (nds_input.c) | stubbed (NOT_IMPL.c) |

> **no_gui headless intent:** The no_gui backend is deliberately designed for headless operation — running Lavender as a game server or for debugging without graphical output. Its rendering stubs (`NOT_IMPL.c`), input stub, and audio stub are **intentional**, not incomplete. The no_gui backend provides real implementations for filesystem (`no_gui_filesystem.c`), TCP multiplayer (`no_gui_tcp_context.c`), and time (`no_gui_time.c`), which is sufficient for server/simulation use cases.

**File locations per backend:**

| Category | SDL | NDS | no_gui |
|---|---|---|---|
| Audio | `sdl/source/TMP.c:22-47` | `nds/source/audio/nds_audio.c:37-274` | `no_gui/source/NOT_IMPL.c:59-76` |
| Debug | `sdl/source/debug/sdl_debug.c` | `nds/source/debug/nds_debug.c` | — |
| Entity | `sdl/source/TMP.c` | `nds/source/rendering/nds_entity.c` | `no_gui/source/NOT_IMPL.c` |
| Filesystem | `sdl/source/serialization/sdl_filesystem.c` + `unix/unix_filesystem.c` + `win64/win64_file_system.c` | `nds/source/serialization/nds_filesystem.c` | `no_gui/source/serialization/no_gui_filesystem.c` |
| TCP | `sdl/source/multiplayer/sdl_tcp_context.c` + `unix/` + `win64/` | — | `no_gui/source/multiplayer/no_gui_tcp_context.c` |
| Input | `sdl/source/input/sdl_input.c` | `nds/source/input/nds_input.c` | `no_gui/source/NOT_IMPL.c` |
| Time | `sdl/source/time/sdl_time.c` | `nds/source/` (integrated) | `no_gui/source/time/no_gui_time.c` |
| Game lifecycle | `sdl/source/sdl_game.c` | `nds/source/nds_main.c` + `nds_game.c` | `no_gui/source/no_gui_game.c` |
| Log | `sdl/source/TMP.c:166-172` | `nds/source/nds_log.c` | `sdl/source/TMP.c:166-172` |
| Sprites/Textures | `sdl/source/rendering/sdl_sprite_manager.c` + `sdl_texture_manager.c` | `nds/source/rendering/sprite_manager.c` + `nds_texture_manager.c` | `no_gui/source/NOT_IMPL.c` |
| GFX Windows | `sdl/source/rendering/sdl_gfx_window_manager.c` + `sdl_gfx_window.c` | `nds/source/rendering/nds_gfx_window.c` | `no_gui/source/NOT_IMPL.c` |

---

## 5. Cross-cutting concerns

**Power-of-2 TCP packet sizing + MASK(n) arithmetic.** `platform_defaults.h:19-36` documents that `MAX_SIZE_OF__TCP_PACKET` must be `BIT(n)` (power of 2) because `MASK(n)` is derived from it (`MASK(n) = BIT(n) - 1`). Non-power-of-2 values cause `game_action__tcp_delivery` to fail because the packet boundary arithmetic uses `MASK(n)` for offsetting within TCP payloads. `MAX_SIZE_OF__TCP_PACKET` defaults to `BIT(9)` = 512 bytes. `MAX_QUANTITY_OF__TCP_PACKETS_PER__SOCKET` defaults to `BIT(8)` = 256. `MAX_QUANTITY_OF__TCP_SOCKETS` defaults to 1. These are compile-time constants in `platform_defaults.h:15-36` that the backend's `platform_defines.h` may override.

**Fixed capacities.** All manager pool sizes come from `platform_defaults.h` `#ifndef` defaults or `defines.h` hard-coded values. Examples: `MAX_QUANTITY_OF__ENTITIES` = 128, `MAX_QUANTITY_OF__SPRITES` = 256, `MAX_QUANTITY_OF__GAME_ACTIONS` = 512, `MAX_QUANTITY_OF__UI_ELEMENTS` = 128, `MESSAGE_MAX_QUANTITY_OF` = 32, `MESSAGE_MAX_LENGTH_OF` = 96. The NDS backend overrides several of these in its `platform_defines.h` (e.g., `GFX_CONTEXT__RENDERING_WIDTH__IN_CHUNKS` = 6 vs. default 4).

**Config override chain.** Three layers:
1. `core/include/config/implemented/engine_config.h` — user-overridable knobs, all currently commented out
2. `core/include/platform_defaults.h` — `#ifndef` defaults (the primary fallback)
3. Backend `platform_defines.h` — platform-specific overrides

The `#ifndef` guards mean that a backend's `platform_defines.h` can selectively override any `platform_defaults.h` constant without touching defaults.

**No-dynamic-allocation expectation of core.** Core's manager pools are all static arrays. The only `malloc` calls in core are for `Game.pM_world`, `Game.pM_clients`, `Game.pM_ptr_array_of__clients`, and `Game.pM_tcp_socket_manager`. Backend implementations may allocate freely within their own context structs, but core modules should not `malloc` — they use fixed-capacity pools.

**"Engine calls down, backend never calls up" rule + exception.** Core calls platform functions during the frame loop; backends generally do not call back into core except via function pointers installed into context structs. The notable exception: `PLATFORM_poll_input` fills the `Input` struct that core reads; audio callbacks (not used in the current codebase) would go through the `Audio_Effect` pool; scene handlers (`m_enter_scene_handler`, `m_load_scene_handler`) are game-installed function pointers called by core.

**`TODO:remove` markers in platform.h.** Every function marked `// TODO: remove` should be tracked.
Priority: **low** — these are all functions whose responsibilities were absorbed into the core's function-pointer architecture or inlined into `initialize_game`, but the platform.h declarations haven't been cleaned up yet. None are called during normal operation.

| Line | Function | Reason |
|---|---|---|
| 41-43 | `PLATFORM_initialize_audio` | Audio management now inline (Game struct holds context) |
| 76-79 | `PLATFORM_render_entity` | Entity rendering delegated to per-entity sprite allocators |
| 85-88 | `m_PLATFORM_game_action_handler_for__multiplayer` | **OBSOLESCED** — core now handles via `m_game_action_handler__dispatch__multiplayer` etc. (game.c:274-279). "make PLATFORM_tcp PLATFORM_udp" |
| 126-127 | `PLATFORM_initialize_rendering__game` | Rendering init moved into per-backend initialize_game |
| 151-154 | `PLATFORM_use_texture` | Texture binding inlined into sprite/world render calls |
| 276-279 | `PLATFORM_initialize_file_system_context` | File system init merged into initialize_game |
| 363-364 | `PLATFORM_update_log__global` | Logs now managed in-process |
| 365-366 | `PLATFORM_update_log__local` | Same |
| 367-368 | `PLATFORM_update_log__system` | Same |
| 370-371 | `PLATFORM_clear_log__global` | Same |
| 372-373 | `PLATFORM_clear_log__local` | Same |
| 374-375 | `PLATFORM_clear_log__system` | Same |

**The coredump/abort debug hook contract.** Three debug functions at `platform.h:69-71` — `PLATFORM_coredump()`, `PLATFORM_pre_abort()`, `PLATFORM_abort()` — are called by the `debug/` module when `debug_abort()` is invoked. The debug module (`core/source/debug/debug.c`) calls these before `exit(-1)`. SDL implements them in `sdl/source/debug/sdl_debug.c` (coredump: `kill(getpid(), SIGSEGV)`; pre_abort: `log`; abort: `SDL_Log("ABORTED")`). NDS implements them in `nds/source/debug/nds_debug.c` (coredump: `printf` + `swiExit` to 0; pre_abort: `printf`; abort: `VramSetPrimaryBank(VRAM_A); memset`).

---

## 6. Known rough edges

**Typo in function signatures (load-bearing, priority: very low):**
1. `p_PLATOFRM_file_system_context` — the filesystem context parameter in `PLATFORM_initialize_file_system_context` (line 279), `PLATFORM_allocate_serialization_request` (line 300), `PLATFORM_release_serialization_request` (line 303). Note the `PLATOFRM` misspelling (missing 'F' after PLAT).
2. `PLATFORM_tcp_recieve` — the function name itself is misspelled (line 440), should be `PLATFORM_tcp_receive`. This is used by `multiplayer/tcp_socket.c` throughout.
3. `dehash_identitier_u32_in__contigious_array` — in `defines.h:2252`, typos in both `identitier` (identifier) and `contigious` (contiguous). This is in the UUID hash table lookup used by `client.c:339`, `game.c:339`.

**Stub files:**
- `sdl/source/TMP.c` (177 lines): contains stubs for audio (6, **low priority**), game_actions (1, **obsolesced — see above**), rendering helpers (~15), log (6). Marked `// !!THIS FILE IS TO BE REMOVED COMPLETELY IN THE FUTURE!!`
- `no_gui/source/NOT_IMPL.c` (100 lines): stubs all rendering, input, and audio functions. **Intentional** — no_gui is designed as a headless backend for servers and debugging. Marked `// This file includes everything from platform.h which is NOT implemented.`

**Signature inconsistencies:**
- `PLATFORM_compose_world` has different signatures between the header (line 248: `Game *p_game, Graphics_Window *p_gfx_window`) and the no_gui stub (`NOT_IMPL.c:11`: adds `Local_Space_Manager *p_local_space_manager` and `Texture *ptr_array_of__textures` plus `f_Tile_Render_Kernel f_tile_render_kernel`). This is a breaking signature discrepancy.

**Open questions:**
- `PLATFORM_tcp_begin`/`PLATFORM_tcp_end` are stubbed in NDS but TCP is used for save/load. The NDS filesystem uses SD card I/O (`fatInitDefault()`) and does not need TCP for multiplayer.
- `PLATFORM_compose_world` has different signatures between the header (line 248) and the no_gui stub (`NOT_IMPL.c:11`), but this is likely only called by no_gui which uses its own compose path.
- Entity's `m_entity_update_handler` default is NULL — this is **intentional**: it's a hook for engine consumers to install per-entity update logic. No default behavior is expected.
- `PLATFORM_update_texture` and `PLATFORM_update_chunk` are declared in the header but never called from core rendering paths (textures are re-allocated when content changes).
- `PLATFORM__GFX_WINDOW__MAX_QUANTITY_OF` is 1 in `platform_defaults.h:259` but 128 in `sdl/include/platform_defines.h:187` and `no_gui/include/platform_defines.h:187`. NDS does not redefine it, so NDS gets the default of 1.

---

## 7. Key files table

| File | LOC (verified) | Role |
|---|---|---|
| `core/include/platform.h` | 452 | The platform API contract — all function declarations |
| `core/platform_defines.h` | 188 | Compile-time defaults, chunk/tile derivations, SDL-specific texture flags |
| `core/include/platform_defaults.h` | 262 | `#ifndef` defaults for all capacities, constants, input codes |
| `core/include/config/implemented/engine_config.h` | — (all commented out) | User-overridable knobs (empty defaults) |
| `sdl/include/platform_defines.h` | 190 | `#define PLATFORM__SDL`; overrides `MAX_LENGTH_OF__IO_PATH` to 1024; `PLATFORM__GFX_WINDOW__MAX_QUANTITY_OF` = 128 |
| `nds/include/platform_defines.h` | 399 | `#define PLATFORM__NDS`; NDS-specific: OAM texture flags, chunk sizes (6x5), tile sizes, UI tile sheet indices, entity limits |
| `no_gui/include/platform_defines.h` | 190 | `#define PLATFORM__NO_GUI`; mirrors SDL defaults; `MAX_LENGTH_OF__IO_PATH` = 1024 |
| `sdl/source/sdl_game.c` | 67 | SDL's `PLATFORM_initialize_game`, `close_game`, `pre_render`, `post_render` |
| `sdl/source/TMP.c` | 177 | SDL stubs (audio, log, game_actions, rendering helpers) |
| `sdl/source/sdl_input.c` | 534 | SDL `PLATFORM_poll_input` implementation |
| `sdl/source/sdl_texture_manager.c` | 5793 | SDL texture allocation/release |
| `sdl/source/sdl_sprite_manager.c` | 5793 | SDL sprite allocation/release |
| `sdl/source/sdl_gfx_window.c` | 3785 | SDL gfx window composition/rendering |
| `sdl/source/sdl_event.c` | 2276 | SDL event handling (the 2276-line file, NOT sdl_game.c) |
| `sdl/source/serialization/sdl_filesystem.c` | — | SDL file system context + serialization |
| `sdl/source/serialization/unix/unix_filesystem.c` | — | SDL Unix-specific `access`, `opendir`, `mkdir`, `get_directories` |
| `sdl/source/serialization/win64/win64_file_system.c` | — | SDL Windows-specific filesystem |
| `sdl/source/multiplayer/sdl_tcp_context.c` | — | SDL TCP socket implementation |
| `sdl/source/multiplayer/unix/sdl_unix_tcp_context.c` | — | SDL Unix TCP context begin/end |
| `sdl/source/multiplayer/win64/sdl_win64_tcp_context.c` | — | SDL Windows TCP context begin/end |
| `sdl/source/time/sdl_time.c` | — | SDL time functions |
| `sdl/source/debug/sdl_debug.c` | — | SDL coredump/pre_abort/abort |
| `nds/source/nds_main.c` | 66 | NDS entry point: initializes all contexts, registers entity handlers, runs game |
| `nds/source/nds_game.c` | 49 | NDS `PLATFORM_pre_render`/`post_render` (VBlank, bgScroll, oamUpdate) |
| `nds/source/audio/nds_audio.c` | 274 | NDS real audio via mmEffect |
| `nds/source/input/nds_input.c` | — | NDS `PLATFORM_poll_input` (scanKeys/touch) |
| `nds/source/serialization/nds_filesystem.c` | 518 | NDS filesystem (fatInitDefault, SD card I/O) |
| `nds/source/debug/nds_debug.c` | — | NDS coredump/pre_abort/abort (printf + swiExit) |
| `nds/source/nds_log.c` | 84 | NDS real log update/clear (LCD output) |
| `no_gui/source/no_gui_game.c` | 19 | no_gui `PLATFORM_initialize_game`/`close_game` |
| `no_gui/source/NOT_IMPL.c` | 100 | no_gui stubs for input/audio/rendering |
| `no_gui/source/no_gui_filesystem.c` | 456 | no_gui real filesystem implementation |
| `no_gui/source/multiplayer/no_gui_tcp_context.c` | 377 | no_gui real TCP implementation |

---

*Written: 2026-08-25. All line numbers and function counts verified against source on `doc-gen` branch.*
