# Lavender Retro C Game Engine - Backend Report

## Executive Summary

This report documents the three backend implementations (SDL, NDS, no_gui) of the Lavender retro C game engine, including directory layouts, platform function mappings, rendering details, build wiring, input/audio specifics, vendored code, completeness status, and comparison matrix.

---

## 1. SDL Backend

### 1.1 Directory Layout

```
sdl/
├── source/
│   ├── TMP.c                    (stub implementations, to be removed)
│   ├── debug/
│   ├── input/
│   │   ├── sdl_input.c          (SDL2 keyboard/mouse bindings)
│   │   └── opengl/
│   │       └── gl_input.c       (viewport-to-game-coordinate conversion)
│   ├── multiplayer/
│   ├── rendering/
│   │   ├── gl_chunk_texture_manager.c
│   │   ├── opengl/
│   │   │   ├── gl_debug.h
│   │   │   ├── gl_defines.h
│   │   │   ├── gl_gfx_sub_context.h
│   │   │   ├── gl_gfx_window.h
│   │   │   ├── gl_gfx_window_manager.h
│   │   │   ├── gl_input.h
│   │   │   ├── gl_render_world.h
│   │   │   ├── gl_sprite.h
│   │   │   ├── gl_sprite_manager.h
│   │   │   ├── gl_texture.h
│   │   │   ├── gl_typer.h
│   │   │   └── glad/
│   │   │       ├── glad.c       (~9,458 lines)
│   │   │       └── glad.h       (~16,837 lines)
│   │   ├── sdl_gfx_context.c    (291 lines)
│   │   ├── sdl_gfx_window.c     (3785 lines)
│   │   ├── sdl_gfx_window_manager.c
│   │   ├── sdl_render_world.c    (695 lines)
│   │   ├── sdl_sprite.c          (1709 lines)
│   │   ├── sdl_sprite_manager.c  (5793 lines)
│   │   ├── sdl_texture.c         (2330 lines)
│   │   └── sdl_texture_manager.c (5793 lines)
│   ├── serialization/
│   ├── time/
│   ├── ui/
│   ├── sdl_event.c               (2276 lines)
│   ├── sdl_game.c                (2276 lines)
│   ├── sdl_main.c                (0 lines)
│   ├── sdl_numerics.c            (334 lines)
│   └── TMP.c                     (stub implementations)
├── include/
│   ├── debug/
│   ├── input/
│   ├── multiplayer/
│   ├── platform_defines.h        (4916 lines)
│   ├── rendering/
│   ├── sdl_defines.h             (9275 lines)
│   ├── sdl_event.h               (544 lines)
│   ├── sdl_numerics.h            (498 lines)
│   └── serialization/
└── Makefile.include
```

### 1.2 Platform Function Mappings

#### Input (Implemented)
- `sdl_input.c`: SDL2 keyboard/mouse bindings via SDL_GetKeyState, SDL_PumpEvents
- `gl_input.c`: Viewport-to-game-coordinate conversion
  - Clamps input to 0-255
  - Flips Y-axis
  - Centers cursor

#### Rendering (Implemented)
- `sdl_render_world.c` (695 lines): Wrapper for OpenGL backend
- `gl_render_world.c` (500 lines): GL compose_world using GL_Shader_passthrough
- `sdl_sprite.c` (1709 lines): Sprite rendering
- `sdl_sprite_manager.c` (5793 lines): Sprite manager
- `sdl_texture.c` (2330 lines): Texture operations
- `sdl_texture_manager.c` (5793 lines): Texture manager
- `sdl_gfx_context.c` (291 lines): OpenGL sub-context linkage
- `sdl_gfx_window.c` (3785 lines): SDL window management

#### Audio (Stubbed — low priority)
- `TMP.c`: Stub implementations for all audio functions in SECTION_audio
  - `PLATFORM_initialize_audio`
  - `PLATFORM_allocate_audio_effect`
  - `PLATFORM_play_audio_effect`
  - `PLATFORM_poll_audio_effects`
  - `PLATFORM_play_audio__stream`
  - `PLATFORM_is_audio__streaming`

#### Game Actions (Stubbed — obsolesced)
- `TMP.c`: Stub for `m_PLATFORM_game_action_handler_for__multiplayer` — **OBSOLESCED**. Core now handles the full multiplayer game-action lifecycle via function-pointer callbacks installed at runtime in `begin_multiplayer_for__game()` (game.c:274-279): `m_game_action_handler__dispatch__multiplayer`, `_receive__multiplayer`, `_resolve__multiplayer`. The platform.h variant is declared but never called.

#### Serialization (Implemented)
- `sdl_filesystem.c`: SDL2 filesystem integration

#### Events (Implemented)
- `sdl_event.c` (2276 lines): SDL event loop and polling

#### Time (Implemented)
- `sdl_time.c`: SDL timer integration

---

### 1.3 Build System

#### Root Makefile
```
PLATFORM ?= sdl
```
Selects backend via PLATFORM variable.

#### Makefile.include
```
INCLUDE_PLATFORM=$(BASE_DIR)/sdl/include
SOURCE_PLATFORM=$(BASE_DIR)/sdl/source
CFILES_SDL: list of C files
OFILES_SDL: object files
PLATFORM_LIBS: -lGL -lGLEW -lSDL2 -lcglm
```

#### Platform Wiring
```
core/include/platform.h
#ifdef PLATFORM__
// Backend-specific defines
#endif
```

---

### 1.4 SDL Top Files by Size

| File | Lines | Description |
|------|-------|-------------|
| glad.h | ~16,837 | GLAD header |
| glad.c | ~9,458 | GLAD implementation |
| sdl_defines.h | 9,275 | SDL-specific defines |
| sdl_sprite_manager.c | 5,793 | Sprite manager |
| sdl_texture_manager.c | 5,793 | Texture manager |
| sdl_gfx_window.c | 3,785 | SDL window management |
| sdl_input.c | 534 | SDL2 input bindings |
| gl_render_world.c | 500 | GL compose_world |
| gl_gfx_window.c | 500 | GL graphics window |
| sdl_render_world.c | 695 | SDL OpenGL wrapper |

---

### 1.5 Backend Main File
- `sdl_main.c`: 0 lines (empty stub)

---

### 1.6 SDL Completeness Status

| Category | Status | Details |
|----------|--------|---------|
| Input | ✅ Full | SDL2 bindings, viewport conversion |
| Rendering | ✅ Full | OpenGL 3.0, sprites, textures, windows |
| Audio | ⬇️ Stubbed (low priority) | TMP.c contains stub implementations |
| Serialization | ✅ Full | SDL2 filesystem |
| Events | ✅ Full | SDL event loop |
| Time | ✅ Full | SDL timers |
| Multiplayer | ✅ Full (core handles dispatch) | `m_PLATFORM_game_action_handler_for__multiplayer` is **obsolesced** — core handles full lifecycle via function pointers in `begin_multiplayer_for__game()` |

---

### 1.7 Vendored Libraries

1. **GLAD** (glad.c/glad.h)
   - ~9,458 lines implementation
   - ~16,837 lines header
   - OpenGL 3.0 loader and binding generator

2. **STB Image** (via glad/stb_image.h)
   - ~7,985 lines
   - Image decoding and pixel operations

3. **SDL2** (external library)
   - Windowing, input, audio, events

4. **cglm** (external library)
   - Math/geometry utilities

---

## 2. NDS Backend

### 2.1 Directory Layout

```
nds/
├── source/
│   ├── input/
│   │   └── nds_input.c          (scanKeys, touch input)
│   ├── audio/
│   │   └── nds_audio.c           (mmEffect API)
│   ├── rendering/
│   ├── multiplayer/
│   ├── serialization/
│   ├── time/
│   ├── ui/
│   ├── font/
│   │   └── nds_font.c            (3,118 lines)
│   ├── filesystem/
│   │   └── nds_filesystem.c      (518 lines)
│   ├── ui_background/
│   │   ├── game/
│   │   │   └── nds_ui_background__game__hud.c (676 lines)
│   │   └── hud/
│   ├── main/
│   │   └── nds_main.c            (implementations)
│   └── ...
├── include/
│   ├── platform_defines.h         (backend-specific defines)
│   └── ...
└── Makefile
```

### 2.2 Platform Function Mappings

#### Input (Implemented)
- `nds_input.c`:
  - `scanKeys()` - Scan all keys
  - `keysHeld()` - Get keys currently held
  - `keysDown()` - Get keys just pressed
  - `keysUp()` - Get keys just released
  - `touchPosition` - Read touch input

#### Audio (Implemented)
- `nds_audio.c`:
  - `PLATFORM_initialize_audio` - Initialize NDS audio
  - `PLATFORM_allocate_audio_effect` - Allocate mmEffect
  - `PLATFORM_play_audio_effect` - Play audio effect
  - `PLATFORM_poll_audio_effects` - Poll mmEffect
  - Uses `mmInitDefaultMem`, `mmLoadEffect`, `mmEffectRelease`

#### Rendering (Implemented)
- `nds_font.c` (3,118 lines): NDS font rendering
- UI backgrounds implemented per module

#### Build System
```
DEVKITARM required
LIBS: -lmm9 -lfilesystem -lfat -lnds9
LDFLAGS: -specs=ds_arm9.specs
```

### 2.3 NDS Top Files by Size

| File | Lines | Description |
|------|-------|-------------|
| nds_font.c | 3,118 | NDS font rendering |
| nds_ui_background__game__hud.c | 676 | Game HUD background |
| nds_filesystem.c | 518 | NDS filesystem |
| nds_ui.c | 494 | UI rendering |
| nds_input.c | ? | Input handling |
| nds_audio.c | ? | Audio handling |
| nds_main.c | ? | Main implementations |

---

### 2.4 Backend Main File
- `nds_main.c`: Contains actual implementations for PLATFORM functions

### 2.5 NDS Completeness Status

| Category | Status | Details |
|----------|--------|---------|
| Input | ✅ Full | scanKeys, touchPosition |
| Audio | ✅ Full | mmEffect API integration |
| Rendering | ✅ Full | Fonts, UI backgrounds |
| Filesystem | ✅ Full | NDS filesystem |
| Build | ✅ Full | DEVKITARM, ds_arm9.specs |

---

### 2.6 Vendored Libraries

1. **DEVKITARM** - NDS toolchain
2. **ds_arm9.specs** - ARM9 linker script
3. **mm9 libraries** - `lmm9`, `lfilesystem`, `lfat`, `lnds9`

---

## 3. no_gui Backend

### 3.1 Directory Layout

```
no_gui/
├── source/
│   ├── input/
│   ├── audio/
│   ├── rendering/
│   ├── multiplayer/
│   ├── serialization/
│   ├── time/
│   ├── ui/
│   └── NOT_IMPL.c                (100 lines, stubs)
├── include/
│   ├── platform_defines.h         (backend-specific defines)
│   └── sdl_defines.h              (shared SDL defines)
└── Makefile.include
```

### 3.2 Platform Function Mappings

> **Headless design:** no_gui is deliberately designed for headless operation — running Lavender as a game server or for debugging without graphical output. All stubs below are **intentional**, not incomplete.

#### Input (Stubbed — intentional)
- `NOT_IMPL.c`: Stub implementations for input functions

#### Rendering (Stubbed — intentional)
- `NOT_IMPL.c`: Stub implementations for rendering functions

#### Audio (Stubbed — intentional)
- `NOT_IMPL.c`: Stub implementations for audio functions

#### Serialization (Implemented)
- `no_gui_filesystem.c` (456 lines): Minimal filesystem
- `no_gui_tcp_context.c` (377 lines): TCP context

#### Build System
```
CC: gcc
LD: clang-21
INCLUDE_NO_GUI=$(BASE_DIR)/no_gui/include
SOURCE_NO_GUI=$(BASE_DIR)/no_gui/source
```

### 3.3 no_gui Top Files by Size

| File | Lines | Description |
|------|-------|-------------|
| no_gui_filesystem.c | 456 | Minimal filesystem |
| no_gui_tcp_context.c | 377 | TCP context |
| NOT_IMPL.c | 100 | Stub implementations |

### 3.4 Backend Main File
- `NOT_IMPL.c`: Contains stub implementations for all platform functions

### 3.5 no_gui Completeness Status

> All stubs are **intentional** — no_gui is designed for headless server/debugging use.

| Category | Status | Details |
|----------|--------|---------|
| Input | ✅ Intentionally stubbed | NOT_IMPL.c (headless) |
| Audio | ✅ Intentionally stubbed | NOT_IMPL.c (headless) |
| Rendering | ✅ Intentionally stubbed | NOT_IMPL.c (headless) |
| Serialization | ✅ Full | no_gui_filesystem.c, no_gui_tcp_context.c |

---

### 3.6 Vendored Libraries

- **gcc** - C compiler
- **clang-21** - Linker

---

## 4. Backend Comparison Matrix

| Feature | SDL | NDS | no_gui |
|---------|-----|-----|--------|
| **Total Files** | 103 | 123 | 12 |
| **Total LOC** | 43,127 | 12,494 | 1,699 |
| **Input** | ✅ Full | ✅ Full | ⬇️ Intentionally stubbed (headless) |
| **Audio** | ⬇️ Stubbed (low priority) | ✅ Full | ⬇️ Intentionally stubbed (headless) |
| **Rendering** | ✅ Full | ✅ Full | ⬇️ Intentionally stubbed (headless) |
| **Filesystem** | ✅ Full | ✅ Full | ✅ Full |
| **Serialization** | ✅ Full | ✅ Full | ✅ Full |
| **Time** | ✅ Full | ✅ Full | ✅ Real |
| **Multiplayer** | ✅ Full (core handles dispatch) | ✅ Full | ✅ Real (TCP) |
| **Build Tool** | SDL2 | DEVKITARM | gcc/clang |
| **External Libs** | GLAD, STB, SDL2, cglm | mm9, fs, fat, nds9 | gcc, clang |
| **Primary Use** | Dev + visual debugging | NDS cartridge | Headless server + headless debugging |

---

## 5. Platform Wiring Mechanism

### 5.1 Core Platform Interface

`core/include/platform.h` (452 lines) defines all PLATFORM_* function signatures:

```c
// Audio section
void PLATFORM_initialize_audio(PLATFORM_Audio_Context *p_PLATFORM_audio_context);
Audio_Effect *PLATFORM_allocate_audio_effect(PLATFORM_Audio_Context *p_PLATFORM_audio_context);
void PLATFORM_play_audio_effect(PLATFORM_Audio_Context *p_PLATFORM_audio_context, Audio_Effect *p_audio_effect);
void PLATFORM_poll_audio_effects(PLATFORM_Audio_Context *p_PLATFORM_audio_context);
void PLATFORM_play_audio__stream(PLATFORM_Audio_Context *p_PLATFORM_audio_context, enum Audio_Stream_Kind the_kind_of__audio_stream);
bool PLATFORM_is_audio__streaming(PLATFORM_Audio_Context *p_PLATFORM_audio_context);

// Rendering section
void PLATFORM_initialize_rendering__game(PLATFORM_Gfx_Context *p_PLATFORM_gfx_context);
void PLATFORM_allocate_texture__with_size(PLATFORM_Texture *texture, Texture_Flags flags, uint32_t width, uint32_t height);
Texture_Flags *PLATFORM_get_p_texture_flags_from__PLATFORM_texture(PLATFORM_Texture *texture);
Quantity__u32 PLATFORM_get_max_quantity_of__allocations_for__texture_flags(...);
Quantity__u32 PLATFORM_get_quantity_of__available_allocations_for__texture_flags(...);
bool PLATFORM_has_support_for__texture_flag__render_method(...);

// Input section
void PLATFORM_initialize_input(Game *p_game);
void PLATFORM_update_input(Game *p_game);
void PLATFORM_update_input__for__sprite(Sprite *p_sprite);
void PLATFORM_release_all__sprites(PLATFORM_Gfx_Context *p_PLATFORM_gfx_context);
Quantity__u32 PLATFORM_get_quantity_of__allocated_sprites(PLATFORM_Gfx_Context *p_PLATFORM_gfx_context);
Quantity__u32 PLATFORM_get_max_quantity_of__allocated_sprites(PLATFORM_Gfx_Context *p_PLATFORM_gfx_context);
```

### 5.2 Backend Platform Defines

Each backend's `platform_defines.h` defines a PLATFORM__ macro:

```c
// SDL backend
#define PLATFORM__SDL

// NDS backend
#define PLATFORM__NDS

// no_gui backend
#define PLATFORM__NO_GUI
```

### 5.3 Core Platform Defines Selection

`core/platform_defines.h` uses #ifdef to select backend-specific defines:

```c
#ifdef PLATFORM__
// Backend-specific defines
#endif
```

### 5.4 Build System Wiring

**Root Makefile:**
```
PLATFORM ?= sdl
```

**Makefile.build:**
```
vpath %.c $(SOURCE_CORE)
```

**Backend Makefile.include:**
```
INCLUDE_PLATFORM=$(BASE_DIR)/sdl/include
SOURCE_PLATFORM=$(BASE_DIR)/sdl/source
CFILES_SDL: export list
OFILES_SDL: export list
PLATFORM_LIBS: -lGL -lGLEW -lSDL2 -lcglm
```

**Core Makefile.include:**
```
OFILES_CORE: export list
PLATFORM_LIBS: -lm
```

---

## 6. Surprises & Open Questions

### 6.1 Surprises

1. **SDL Input Implementation** - `sdl_input.c` and `gl_input.c` work together:
   - `sdl_input.c` handles SDL2 keyboard/mouse bindings
   - `gl_input.c` converts viewport coordinates to game coordinates (clamps 0-255, flips Y, centers cursor)

2. **SDL Rendering Architecture**:
   - `sdl_render_world.c` (695 lines) wraps OpenGL
   - `gl_render_world.c` (500 lines) implements GL compose_world using GL_Shader_passthrough
   - OpenGL 3.0 sub-context linked in `sdl_gfx_context.c` (291 lines)

3. **NDS Audio Implementation** - Uses mmEffect API with `mmInitDefaultMem`, `mmLoadEffect`, `mmEffectRelease`

4. **TMP.c Stub Pattern** - Platform-specific stubs are stored in TMP.c for SDL backend to be removed in the future

5. **Backend Main Files**:
   - SDL: `sdl_main.c` is 0 lines (empty)
   - NDS: `nds_main.c` has actual implementations
   - no_gui: `NOT_IMPL.c` has stub implementations

### 6.2 Open Questions

1. **SDL Audio Status** - Why is audio stubbed? **Answer: low priority**, not actively being worked on.

2. **SDL Multiplayer** - `m_PLATFORM_game_action_handler_for__multiplayer` is stubbed. **Answer: OBSOLESCED** — core handles the full dispatch/receive/resolve lifecycle via function pointers installed in `begin_multiplayer_for__game()` (game.c:274-279).

3. **NDS Rendering** - How does NDS handle textures vs OpenGL? Is it using a different approach?

4. **no_gui Use Case** - What scenarios would `no_gui` backend be used for? **Answer: headless game servers and headless debugging** — rendering/input/audio stubs are intentional, not incomplete.

5. **Platform Defines** - What backend-specific defines are defined in each backend's `platform_defines.h`?

6. **Completion Timeline** - When will SDL audio and multiplayer be implemented? Audio = low priority (no timeline). Multiplayer = already handled by core, platform.h stub is dead code.

---

## 7. Conclusion

The Lavender engine demonstrates a well-structured cross-platform architecture with three distinct backend implementations:

1. **SDL Backend** (~43k LOC): Fully implemented rendering and input. Audio is stubbed (**low priority**). Multiplayer is **fully functional** — core handles the dispatch/receive/resolve lifecycle; the `m_PLATFORM_game_action_handler_for__multiplayer` platform.h stub is obsolesced. Uses GLAD for OpenGL and is the primary development backend.

2. **NDS Backend** (~12.5k LOC): Fully implemented across all categories. Uses DEVKITARM and NDS-specific libraries.

3. **no_gui Backend** (~1.7k LOC): Headless backend with **intentional** stubs for rendering/input/audio. Provides real filesystem, TCP multiplayer, and time implementations. Designed for headless game servers and debugging.

The platform wiring mechanism is clean and modular, using conditional compilation and backend-specific defines. The build system allows easy switching between backends via the PLATFORM variable.

**Key Observation**: The SDL backend is the primary development backend. The multiplayer game-action handler in platform.h is **not** missing — it's obsolesced. Core handles the full lifecycle via function-pointer callbacks. Audio stubs are low priority. no_gui stubs are intentional design, not incompleteness.
