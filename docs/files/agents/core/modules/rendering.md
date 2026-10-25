# Rendering — retained-model rendering pipeline, windows, sprites, textures

**Sources:** `core/source/rendering/` + `core/include/rendering/`

## Surface Concerns

Rendering is the **L4 PRESENTATION** module. It provides a retained-model rendering pipeline: `Graphics_Window` objects compose UI tile maps and render sprite pools into platform-provided backbuffers. Driven from the main scene loop (`scene__main.c`): code-generated `GEN-PRE-RENDER` code calls `compose_graphic_windows_in__graphics_window_manager()` and `render_graphic_windows_in__graphics_window_manager()` each frame; the backend frame swap happens in `PLATFORM_post_render` from `manage_game__post_render`.

- **Window lifecycle and Z-ordering** — `Graphics_Window_Manager` owns `Graphics_Window` objects in a fixed-size array (8), maintaining a sorted pointer array for Z-order rendering via a tree-aware heuristic (parent/child, root, orphan, then Z). Windows compose and render through per-window function pointers that default to `f_graphics_window__default_compose` / `f_graphics_window__default_render`.
- **Ownership vs sharing** — Windows store UUIDs (not pointers) for their sprite manager, UI manager, and hitbox manager. Ownership means the window's UUID equals the manager's UUID; sharing means a different valid UUID. Release functions check ownership before freeing.
- **Sprite lifecycle + animation** — `Sprite_Manager` allocates sprites from a malloc'd pool, sorts render records by Z/Y depth for painter's algorithm, and calls `PLATFORM_render_sprite`. Sprite positions are read from the window's hitbox manager (a missing hitbox disables the sprite). Animation groups advance frame indices via tickable `Sprite_Animation` state with custom handler support.
- **Texture aliasing** — `Aliased_Texture_Manager` maps names to `Texture` structs (up to 128). Loads from paths via platform base directory + relative path. Texture flags pack width, height, format, and render method into a bitfield. Notable contract: the texture API's `bool` returns are inverted — true means failure.
- **Fonts + Typer** — `Font_Manager` allocates from a fixed 8-slot pool; each `Font` carries a 256-entry glyph lookup table plus a font texture, populated by the game layer. `Typer` is a text-output primitive targeting either a PLATFORM texture or window, with cursor wrapping and AABB hitbox coupling to collisions.
- **Platform render contract** — Each backend implements `PLATFORM_render_sprite`, `PLATFORM_render_gfx_window`, `PLATFORM_compose_gfx_window`, and `PLATFORM_post_render`. The retained-model pattern builds scene state (windows, sprites, tile maps); the backend composites/swaps in `PLATFORM_post_render`. `platform.h` (above `PLATFORM_render_sprite`) recommends backends batch sprite data for a single final call.
- **Fixed-capacity managers** — All managers use compile-time arrays. The exceptions are the sprite pool, the sprite manager pool (`Sprite_Context.pM_sprite_managers`), and the UI element pool, all `malloc`'d; text elements additionally `malloc` a char buffer. No other runtime allocation.
- **Direct mutation protocol** — Presentation state mutates directly (not through game actions). Sprite allocation, UI creation, window positioning all happen inline from game logic during the frame.
- **Cross-layer coupling** — Rendering has more `platform.h` includes than any other core module. Sprite rendering fetches AABB hitboxes from the hitbox manager, creating tight coupling to Simulation. World directly holds `Graphics_Window*`.

## Public API Surface

### Key Types

**`Graphics_Window`** — defined in `defines.h`. Key members:
- `origin_of__gfx_window`, `position_of__gfx_window` (`Vector__3i32`)
- `width_of__graphics_window__u32`, `height_of__graphics_window__u32`
- `the_kind_of__window` (`Graphics_Window_Kind`)
- `graphics_window__flags` (IS_ENABLED, IS_PLATFORM_PROVIDED, COMPOSE__DIRTY)
- `p_PLATFORM_gfx_window` (opaque backend window handle)
- `uuid_of__sprite_manager`, `uuid_of__ui_manager`, `uuid_of__hitbox_manager` (UUIDs)
- `ui_tile_map__wrapper` (embedded `UI_Tile_Map__Wrapper`)
- `p_camera` (Camera pointer for per-window cameras)
- `f_PLATFORM_compose_gfx_window`, `f_PLATFORM_render_gfx_window` (per-window backend function pointers)

**`Gfx_Context`** — defined in `defines.h`. Root presentation context stored in `Game.gfx_context`. Key members:
- `p_PLATFORM_gfx_context` (opaque backend root context)
- Inline managers: `aliased_texture_manager`, `ui_context`, `ui_tile_map_manager`, `graphics_window_manager`, `font_manager`, `sprite_context`

**`Sprite_Manager`** — defined in `defines.h`. Key members:
- `pM_pool_of__sprites` (Sprite*) — malloc'd pool
- `pM_sprite_render_records` (Sprite_Render_Record*) — pre-computed render positions
- `max_quantity_of__sprites`

**`Sprite`** — defined in `defines.h`. Key members:
- `p_PLATFORM_sprite` (opaque backend sprite handle)
- `texture_for__sprite_to__sample`, `texture_of__sprite` (Texture structs)
- `sprite_flags__u8` (IS_ENABLED, IS_NEEDING_GRAPHICS_UPDATE, FLIPPED_X/Y)
- `animation` (Sprite_Animation) + `m_sprite_animation_handler` (callback)

**`Typer`** — defined in `defines.h`. Text layout target. Key members:
- `text_bounding_box` (Hitbox_AABB)
- `cursor_position__3i32`, `p_font` (Font*)
- `texture_of__typer_target` / `p_PLATFORM_graphics_window__typer_target` (dual-target union)

### Key Functions

- `void initialize_graphics_window(Graphics_Window *p_graphics_window);`
- `Graphics_Window *allocate_graphics_window_from__graphics_window_manager(Gfx_Context *p_gfx_context, Graphics_Window_Manager *p_manager, Texture_Flags texture_flags);` — returns window or 0 on failure.
- `void release_graphics_window_from__graphics_window_manager(Game *p_game, Graphics_Window *p_window);`
- `void render_graphic_windows_in__graphics_window_manager(Game *p_game);`
- `void compose_graphic_windows_in__graphics_window_manager(Game *p_game);`
- `Sprite *allocate_p_sprite_from__graphics_window(Game *p_game, Graphics_Window *p_window, Identifier__u32 uuid, Texture texture, Texture_Flags flags);` — returns sprite or 0 if the window's sprite pool is unallocated or full.
- `Sprite *allocate_sprite_from__sprite_manager(Gfx_Context *p_gfx_context, Sprite_Manager *p_manager, Graphics_Window *p_window, Identifier__u32 uuid, Texture texture, Texture_Flags flags);` — returns sprite or 0 if full.
- `void release_sprite_from__sprite_manager(Gfx_Context *p_gfx_context, Sprite_Manager *p_manager, Sprite *p_sprite);`
- `void render_sprites_in__sprite_manager(Game *p_game, Sprite_Context *p_context, Sprite_Manager *p_manager, Graphics_Window *p_window);`
- `bool does_graphics_window_own_a__sprite_manager(Graphics_Window *p_window);` / `bool does_graphics_window_share_a__sprite_manager(Graphics_Window *p_window);`

## Key Files Table

| File | Role |
|------|------|
| `core/source/rendering/graphics_window_manager.c` | Window CRUD, Z-sort heuristic, compose/render dispatch, platform-provided windows |
| `core/include/rendering/graphics_window.h` | Graphics_Window API, ownership getters, position helpers |
| `core/source/rendering/aliased_texture_manager.c` | Texture name-aliasing: allocate, lookup, release (inverted bool returns) |
| `core/source/rendering/sprite_manager.c` | Sprite pool, Z-sort render records, render loop |
| `core/include/rendering/sprite.h` | Sprite flag inlines, animation polling API |
| `core/source/rendering/graphics_window.c` | Window init, release, position, default compose/render |
| `core/source/rendering/font/typer.c` | Text layout, cursor wrapping, char rendering |
| `core/source/rendering/sprite_context.c` | Sprite manager pool allocation from sprite context |
| `core/include/rendering/sprite_context.h` | Sprite_Context getters, animation/group registration |
| `core/include/rendering/graphics_window_manager.h` | Manager API, allocation, parent/child, sort |
| `core/include/rendering/gfx_context.h` | Gfx_Context root context + getters |
| `core/source/rendering/sprite.c` | Animation polling, looping, group-set transitions |
| `core/include/rendering/texture.h` | Texture flag bitfield accessors |
| `core/include/rendering/sprite_manager.h` | Sprite_Manager allocation/render API |
| `core/include/rendering/aliased_texture_manager.h` | Aliased_Texture_Manager API |
| `core/source/rendering/font/font_manager.c` | Font slot allocation (8-slot pool) |
| `core/source/rendering/font/font.c` | Font glyph table init |
| `core/source/rendering/implemented/` | GEN registrars: game-layer aliased textures, sprite animations |
