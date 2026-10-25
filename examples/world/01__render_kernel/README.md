# Introduction

This tutorial shows how the **tile render kernel** works — the function that
decides what the compositor draws for every tile. It builds on
`world/00__chunk_generator` (same per-chunk frame generator: RED outer ring,
GREEN interior) and installs a kernel that deliberately **inverts** the
generator's decision (RED<->GREEN) and mirrors the right half of every
chunk on x. Comparing the two screenshots is the lesson: the chunk
generator's data is just *input*; the kernel controls what is drawn.

# Build

Build the example with the following command:
`
lav_build -e PLATFORM=sdl FLAGS="-ggdb -w" -j$(nproc)
`

## Agent Advisory:

AI Agents should be aware that the outputted executable will NOT terminate
and should be ran with a timeout (it never exits on its own). To verify the
example, run it from `build/sdl/` (after `rm -rf save && mkdir -p save`) and
check:

1. stdout shows the scene transition and, ~60 frames in, `screen.png` is
   written.
2. `screen.png` shows the INVERSE of `world/00__chunk_generator`: where
   00 showed a red frame around a green interior, this shows a green frame
   around a red interior — and the right half of each chunk is mirrored.

## 1) What the kernel is

A chunk is composed into a chunk texture by the GL compositor, and for
every tile the compositor asks the world's tile render kernel what to draw.
The kernel is set explicitly on the world (the engine does NOT set one in
`initialize_world`):

```c
set_f_tile_render_kernel_of__world(
        get_p_world_from__game(p_game),
        m_f_tile_render_kernel__inverted_frame);
```

Signature:

```c
void kernel(
        Local_Space *p_local_space,                    // the space being composed
        Tile_Render_Kernel_Result *p_tile_kernel_render_results,
        Quantity__u32 quantity_of__tile_kernel_render_results,
        u8 x__local, u8 y__local, u8 z__local)         // tile coords in the chunk
```

It is called once per tile, per graphics window, and draws nothing itself —
it fills in **one result slot per graphics window**:

- `index_of__texture` — the 1-based tilesheet index to draw
  (0 = skip/transparent). `Tile_Kind` values are conventionally defined
  1:1 with the tilesheet slots, so the stock kernel just copies
  `tile->the_kind_of__tile`.
- `is_flipped__x` / `is_flipped__y` — optional per-tile mirroring.

Slot 0 is the **composed** window (the one that owns the camera); extra
slots feed parent-child graphics window hierarchies for multi-layer
rendering — see `types/00__tile_layers` for that pattern.

## 2) This example's kernel

The generator (unchanged from 00) writes RED on the chunk's outer ring and
GREEN in the interior. The kernel:

```c
Index__u16 index_of__texture =
    (p_tile)
    ? (p_tile->the_kind_of__tile == Tile_Kind__RED)
        ? Tile_Kind__GREEN
        : Tile_Kind__RED
    : 0;
p_tile_kernel_render_results[0].index_of__texture = index_of__texture;
p_tile_kernel_render_results[0].is_flipped__x = (x__local >= CHUNK__WIDTH / 2);
```

inverts the generator's RED/GREEN choice and mirrors the right half of each
chunk — so the screenshot shows a GREEN frame around a RED interior, with
each chunk's right half flipped. The kernel reads the tile through
`get_p_chunk_from__global_space` + `get_p_tile_from__chunk` (guarded: a
missing chunk yields index 0 = transparent).

## 3) Everything else

Identical to `world/00__chunk_generator`: same generator registration,
world setup, camera, and frame loop.
