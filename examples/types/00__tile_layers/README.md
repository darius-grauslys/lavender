# 00__tile_layers (types)

This tutorial shows **Game-Specific Configuration** in action: it
changes the *shape of the `Tile` struct* (two renderable tile layers
instead of one) and wires that into the renderer's **window
hierarchy**, so the world is composited from two graphics windows —
one per tile layer.

Expected visual: green dots (the cover layer, its own window) floating
on a solid red ground (the ground layer, its own window).

### How layers map to windows (the engine model):
When a window's compose function is `PLATFORM_compose_world`, the
world compositor collects **that window plus all of its descendants**
(in sorted window order) as an array of *render windows*. For every
tile of every chunk it calls the world's tile render kernel with **one
result slot per render window**; slot `i` is composited into render
window `i`'s chunk texture, sampled through window `i`'s own tile map
texture. The windows are then blitted to the screen in Z order.
So: **one `DECLARE_TILE_LAYER` in tile.h == one kernel result slot ==
one window in the hierarchy.**

# Build

Build the example with the following command:
`
lav_build -e PLATFORM=sdl FLAGS="-ggdb -w" -j$(nproc)
`

## Agent Advisory:

AI Agents should be aware that the outputted executable will NOT
terminate and should be ran with a timeout (a fresh `save/` takes
>15s to generate; use e.g. `timeout 30`):
`
mkdir -p build/sdl/save && cd build/sdl && timeout 30 ./00__tile_layers
`
Verify: exit code 124, zero `debug_error`/`debug_abort`, and
`build/sdl/screen.png` (written at frame 60) shows green dots on a
red background at 8px-tile resolution (the dots are the cover layer
from the second window; the red is the ground layer).

## 1) Adding a second tile layer to the Tile struct

`include/types/implemented/world/tile.h` (include-shadowed over
`core/include/...`) gains a second `DECLARE_TILE_LAYER`:
`
DECLARE_TILE_LAYER(
        Tile_Kind, 8, the_kind_of__tile, ...);   // layer 0 (ground)
DECLARE_TILE_LAYER(
        Tile_Kind, 8, the_kind_of__cover, ...);  // layer 1 (cover)
`
Each `DECLARE_TILE_LAYER` is one 8-bit bitfield of the tile — and one
render layer. (Note: the `__Tile_Data` member in the stock file is a
vestigial no-op; the real fields are the bitfields.)

The `Tile_Layer` enum (`tile_layer.h`) gains a matching entry:
`
Tile_Layer__Default = 0,   ...
Tile_Layer__Cover,         ...
Tile_Layer__Unknown
`
The layer *count* (`Tile_Layer__Unknown`) sizes engine-side per-layer
arrays (e.g. the chunk compositor's texture array), so it must grow
with the layers.

### Note - Chunk storage follows sizeof(Tile):
A tile is now 2 bytes; chunk memory, serialization and the save file
all scale with `sizeof(Tile)` from the shadowed header. Use a fresh
`save/` when changing the tile shape (old saves have 1-byte tiles).

## 2) Generating both layers (chunk generator)

`source/world/implemented/chunk_generator_registrar.c` now fills both
fields per tile:
`
p_tile->the_kind_of__tile  = Tile_Kind__RED;          // solid ground
p_tile->the_kind_of__cover = ((x + y) % 4 == 0)
        ? Tile_Kind__GREEN : Tile_Kind__None;          // sparse dots
`
`Tile_Kind__None` (0) in a layer means "transparent" for that layer.

## 3) The render kernel: one result slot per window

`m_f_tile_render_kernel__two_layers` in `scene__main.c` writes both
slots (slots arrive in hierarchy order: composed window first):
`
p_tile_kernel_render_results[0].index_of__texture =
    p_tile->the_kind_of__tile;    // ground window
if (quantity_of__tile_kernel_render_results > 1) {
    p_tile_kernel_render_results[1].index_of__texture =
        p_tile->the_kind_of__cover;  // cover window
}
`
(`index_of__texture` is 1-based; 0 = transparent/skip. The Tile_Kind
values are defined 1:1 with the tilesheet index slots.)

## 4) The second render window (load handler)

The world window (from `01__allocate_world`) stays the composed
window (`f_PLATFORM_compose_gfx_window = PLATFORM_compose_world`,
holds the camera, Z=0). A second window is allocated and made a
**CHILD of the world window** — which makes it kernel slot 1:
`
p_gfx_window__cover =
    allocate_graphics_window_from__graphics_window_manager(...);
set_graphics_window__tile_map__texture(
        p_gfx_window__cover, uuid_of__tileset_texture);
set_position_3i32_of__graphics_window(
        p_game, p_gfx_window__cover, get_vector__3i32(0, 0, 1)); // Z=1
set_graphics_window_as__parent_to__this_graphics_window(
        p_gfx_window_manager, p_gfx_window__world, p_gfx_window__cover);
`
- Each layer window samples the tilesheet through its **own** tile map
  texture (both use the same tileset here).
- Z=1 puts the cover above the ground when the windows are blitted to
  screen (siblings/descendants render in ascending Z).
- Only the **composed** window needs `set_graphics_window_as__in_need_
  of__composition` every frame; the world compositor recomposites and
  redraws ALL layer windows' textures as part of it.

### Note - Unload:
Release both windows in `m_unload_scene_as__main_handler` (the
backbuffer is platform-provided and outlives the scene).
