# Introduction

This tutorial shows how chunk generation works in Lavender and how to
register your own chunk generator. It builds on `scene/01__allocate_world`
(same world setup: tileset, camera, render kernel, frame loop) and replaces
the checkerboard generator with a **per-chunk frame** pattern: the outer
ring of every 8x8x8 chunk is RED, the interior is GREEN. Because every
chunk gets the identical frame, it is obvious at a glance that each chunk in
the 4x3 render band was generated independently by the same generator.

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
2. `screen.png` shows a 4x3 grid of chunk "frames": each 64x64 px chunk
   area has a red border (one tile wide) around a green interior.

## 1) The chunk generator is a process

A chunk generator is registered as a PROCESS, not a plain function:

```c
void m_process__generate_chunk(Process *p_this_process, Game *p_game)
```

The engine runs one instance of it per chunk that needs generating (via the
process manager) and hands it the chunk's **global space** as process data.
That is what makes chunk generation cooperative: each chunk is a process
that yields, so loading the 12+ chunks of the render band never monopolizes
a frame (Lavender is a non-preemptive task scheduler — a process that
doesn't yield stalls the game).

## 2) Filling the chunk

- A chunk is `CHUNK__WIDTH x CHUNK__HEIGHT x CHUNK__DEPTH` tiles (8x8x8);
  the tile array is row-major:
  `index = x + y * WIDTH + z * WIDTH * HEIGHT`.
- `Tile_Kind` values map 1:1 onto the tilesheet (top-left tile = index 0,
  left-to-right, top-to-bottom). Index 0 (`None`) is transparent, so a
  generator only ever writes the kinds it wants visible (RED/GREEN here).
- The pattern writes RED on the outer ring of the chunk
  (`x==0 || x==7 || y==0 || y==7`), GREEN elsewhere.

## 3) The yield contract

The process fills **one z-slice (64 tiles) per invocation**, persists the z
cursor in `process_value_bytes__u8[1]` (those bytes persist between
invocations), and returns. After the final slice it calls:

```c
set_chunk_as__active(p_chunk);        // chunk is fully generated
set_chunk_as__visually_updated(p_chunk); // tell the compositor to pick it up
complete_process(p_this_process);     // done; process manager recycles it
```

## 4) Registration

`register_chunk_generators` (called from the scene load handler, routed
through `register_chunk_generators(...)` on the chunk generator table)
registers the generator under `Chunk_Generator_Kind__None` — the **default**
kind: any generation request that doesn't name a specific kind uses this
generator. A multi-biome game would register one generator per kind (in
`types/implemented/world/chunk_generator_kind.h`) and request the kind per
global space.

## 5) Everything else

Identical to `scene/01__allocate_world`: tileset registration, world
allocation + spawn point, tile render kernel (maps Tile_Kind straight onto
the tilesheet), graphics window + camera, and the
pre_render/manage_world/compose/render/post_render frame loop.
