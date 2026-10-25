# 02__allocate_ui

This tutorial expands `01__allocate_world` by allocating a **UI window**
(a HUD) on top of the world: a 256x256 graphics window that owns a
`UI_Manager` and three red buttons, driven by mouse input.

What "allocate a UI window" means in Lavender terms:

- a `Graphics_Window_Kind` entry (the window's "class"),
- a `UI_Window_Record` (load/close functions + element pool sizes)
  registered per kind,
- a `Graphics_Window` (256x256) with its own **ui tile map** (a
  32x32 grid of 8px `UI_Tile` slots) whose texture is the tileset,
- a `UI_Manager` (the pool of `UI_Element`s that live in the window),
- `UI_Element`s (here: buttons) with a **hitbox** (input) and a
  **tile span** (visuals).

### Note - Extra Steps:
We keep the world from `01__allocate_world` so you can see the UI
rendered *above* the world. The world is not the point of this
example; the UI allocation is.

# Build

Build the example with the following command:
`
lav_build -e PLATFORM=sdl FLAGS="-ggdb -w" -j$(nproc)
`

## Agent Advisory:

AI Agents should be aware that the outputted executable will NOT
terminate and should be ran with a timeout (a FRESH `save/` takes
>15s to generate; use e.g. `timeout 30`):
`
mkdir -p build/sdl/save && cd build/sdl && timeout 30 ./02__allocate_ui
`
Verify: exit code 124 (timeout), zero `debug_error`/`debug_abort` in
output, and `build/sdl/screen.png` (written automatically at frame 60)
shows three solid red 48x16 buttons in the top-left area (x = 16-64,
72-120, 128-176). The screenshot is taken from `scene__main.c`.

## 1) A Graphics_Window_Kind for the HUD

`include/types/implemented/rendering/graphics_window_kind.h` gains:
`
typedef enum Graphics_Window_Kind {
    Graphics_Window_Kind__None,
    Graphics_Window_Kind__UI__Hud,   // <-- new
} Graphics_Window_Kind;
`
The kind is just the key used when registering and later *opening*
the UI window.

## 2) UI_Tile_Kind: 8px sub-tiles of the tileset

`include/types/implemented/ui/ui_tile_kind.h` gains:
`
typedef enum UI_Tile_Kind {
    UI_Tile_Kind__None,
    UI_Tile_Kind__RED,   // 8px sub-tile index 1 of the tileset
} UI_Tile_Kind;
`
**Important:** UI tiles are 8px, and `UI_Tile_Kind` indexes the
8px sub-tiles of the window's ui-tile-map texture (a 256x256 texture
is a 32x32 grid of 8px sub-tiles), NOT the 32px world tiles. Sub-tile
index 1 is the top-left 8x8 block of the tileset's first (red) 32px
tile, so it is solid red. Index 0 is `None` and must be transparent.

## 3) The UI_Window_Record (register_ui_windows)

`source/ui/implemented/ui_window_registrar.c` registers, per kind, the
load/close function pair and the element pool quantities:
`
{
    Graphics_Window_Kind__UI__Hud,
    allocate_ui_for__ui_window__main,   // builds the buttons
    f_ui_window__close__main,
    0,    // quantity_of__sprites
    16,   // quantity_of__ui_elements
},
`
Registering only fills in the record — the window itself is opened
later (step 6).

## 4) The load function: building the buttons

`source/ui/implemented/ui_window__main.c` defines
`allocate_ui_for__ui_window__main(...)`, which runs at populate time.
For each of the 3 buttons it:

1. allocates `UI_Element`s (one call, linked in a succession),
2. `initialize_ui_element_as__button(p_ui_button,
   m_ui_button__clicked_handler__main, false, false)` — the click
   handler logs when the button is clicked,
3. `allocate_hitbox_for__ui_element(...)` — 48x16px hitbox, which
   ALSO defines the drawn size (48x16 px == 6x2 UI tiles),
4. gives the button a solid red `UI_Tile_Span` (corners, edges and
   fill all `UI_Tile_Kind__RED`) via `set_ui_tile_span_of__ui_element`.

The close function (`f_ui_window__close__main`) is the place to tear
down anything the load function created; the engine releases the
elements and the window itself.

### Note - Coordinate convention (the gotcha):
The hitbox position vector is the element's **CENTER** in
**window-center-relative** coordinates, **Y bottom-origin** — the same
space the SDL platform puts the mouse cursor in (see
`GL_process_input`: it subtracts the viewport center). So "16px from
the left edge, 16px from the top" of a 256x256 window is
`(-88, 104)`, i.e. `(16 + 48/2 - 128, 128 - (16 + 16/2))`. Positive
top-left-style values land far to the right/bottom.

## 5) The window hierarchy (load handler)

Same layout as the reference games (AncientsGame):
`
backbuffer (platform-provided ROOT, presented to screen)
├── ground   (256x256, composes the WORLD, camera, z=0)
└── HUD      (256x256, ui_manager, z=1)
`
The world is composed in the **ground** window, NOT the backbuffer,
because the platform world compositor (`GL_compose_world`) treats each
*child* of the composed window as a world render layer — a UI window
must therefore NOT be a child of the ground window.

## 6) Opening the HUD (enter handler, manual open)

We do the "open" manually (allocate -> equip -> populate) because the
record's load function runs at populate time and NEEDS the window to
already be fully equipped:
`
// 1) allocate with a fixed uuid (so we can close it on unload)
p_gfx_window__ui__hud =
    allocate_graphics_window_with__uuid_from__graphics_window_manager(
            p_gfx_context, p_gfx_window_manager, 1,
            TEXTURE_FLAGS(TEXTURE_FLAG__SIZE_256x256, 0,
                          TEXTURE_FLAG__FORMAT__RGBA8888));
// 1.5) position Z=1 => rendered ABOVE the ground (z=0) sibling.
//     MUST be set BEFORE the UI is populated: moving a window after
//     its UI elements exist shifts them through the hitbox manager,
//     which assumes the ui_manager owns it.
set_position_3i32_of__graphics_window(p_game, p_gfx_window__ui__hud,
                                      get_vector__3i32(0, 0, 1));
// 2) ui tile map + texture (the tileset): UI spans draw their 8px
//    sub-tiles out of THIS texture.
set_graphics_window__ui_tile_map(p_gfx_window__ui__hud,
        allocate_ui_tile_map_with__ui_tile_map_manager(
            get_p_ui_tile_map_manager_from__gfx_context(p_gfx_context),
            UI_Tile_Map_Size__Large));
set_graphics_window__ui_tile_map__texture(p_gfx_window__ui__hud,
        uuid_of__tileset_texture);
// 3) share the world's hitbox manager (elements' hitboxes live here)
share_hitbox_manager_with__graphics_window(p_gfx_window__ui__hud,
        GET_UUID_P(get_p_world_from__game(p_game)));
// 4) the element pool
allocate_ui_manager_for__graphics_window(p_gfx_context,
        p_gfx_window__ui__hud, 16);
// 5) populate: sets the kind, runs allocate_ui_for__ui_window__main,
//    marks the window enabled + in need of composition
populate_window_with__ui(p_game, p_gfx_window__ui__hud,
        Graphics_Window_Kind__UI__Hud, 0);
// parent it under the backbuffer (sibling of ground)
set_graphics_window_as__parent_to__this_graphics_window(
        p_gfx_window_manager, p_gfx_window__backbuffer,
        p_gfx_window__ui__hud);
`
Sibling windows render in ascending window-position Z, so Z=1 puts the
HUD above the ground's Z=0.

## 7) The frame loop: poll + compose

The SDL platform does NOT poll ui managers or render for you:
`
manage_game__pre_render(p_game);
manage_world(p_game);
// poll the HUD for input (focus/clicks/drops) every frame:
poll_ui_manager__update(
        get_p_ui_manager_from__graphics_window(p_game, p_gfx_window__ui__hud),
        p_game, p_gfx_window__ui__hud);
set_graphics_window_as__in_need_of__composition(p_gfx_window__ground);
compose_graphic_windows_in__graphics_window_manager(p_game);
render_graphic_windows_in__graphics_window_manager(p_game);
manage_game__post_render(p_game);
`
The HUD re-marks itself dirty through its (dirty) ui_manager, so it
re-composes every frame; the world only needs the ground window marked
dirty.

### Note - screen scaling:
The HUD texture is 256x256 but the default SDL viewport is 256x192,
so window Y coordinates are scaled 0.75x on screen (X is 1:1). A
button at window y=16..32 appears at screen y=12..24. This is engine
behavior, not a bug in the example.

## 8) Unload

`
close_ui_window(p_game, GET_UUID_P(p_gfx_window__ui__hud));  // runs
    // f_ui_window__close__main, releases the window
release_graphics_window_from__graphics_window_manager(
        p_game, p_gfx_window__ground);
`
The backbuffer is platform-provided and outlives the scene.
