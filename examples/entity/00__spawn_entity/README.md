# Introduction

This tutorial builds on `scene/01__allocate_world` and shows how to spawn an
entity in the world: a `Dummy` entity that owns a sprite (rendered into the
world's graphics window) and an AABB hitbox (the client's hitbox, which the
collision system keeps standing on the ground).

### Note - The world is the same as 01:
A checkerboard chunk generator (red/green ground tiles), a static camera, and
the fixed 4x3 chunk render band around the local space manager center. The
new pieces are the tile logic table (ground), the entity kind, and the
sprite.

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
2. `screen.png` contains the red/green checkerboard **and** a small orange
   16x16 square (the dummy sprite) slightly right of center.
3. There is no repeated `debug_error` spam. Two one-off startup messages are
   expected and come from the ENGINE, not this example:
   `attach_object_to__collision_system, failed to attach` and, right after,
   `remove_entry_from__collision_node, uuid__u32 not present in node`
   (see "Engine Notes" below).

## 1) Registering the textures

In `rendering/implemented/aliased_texture_registrar.c` we register two
textures: the 256x256 world tileset (as in 01) and the entity sprite sheet.

### Note - Sprite sheets are 256x256:
The sprite texture is loaded with `TEXTURE_FLAG__SIZE_256x256` even though
the sprite uses a single 16x16 frame of it. The texture manager and the GL
sprite path are built around 256x256 storage, and loading a real 16x16 file
crashes the (old i915/crocus) Mesa driver on framebuffer swap. `assets/entity/dummy.png`
is therefore a 256x256 sheet with the 16x16 orange square in the top-left
corner (frame 0).

## 2) Registering the tile logic table (ground)

In `world/implemented/tile_logic_table_registrar.c`:

1. `allocate_tile_logic_table_from__tile_logic_context(ctx, Tile_Layer__Default,
   Tile_Kind__Unknown)` allocates the table.
2. `initialize_tile_logic_table` + `allocate_tile_logic_table__tile_logic_entries`
   are REQUIRED: without them the table has no record array and every tile
   kind looks up nothing.
3. Records are zeroed on allocation, and zero flags mean WITH ground,
   passable, height 0 — which is what the checkerboard ground tiles (RED and
   GREEN) need, so they are left as-is. `Tile_Kind__None` is marked
   `TILE_LOGIC_FLAG__IS_WITHOUT_GROUND` explicitly (it is transparent/empty).

Without ground records the collision resolver's falling ray-cast never finds
a floor, the client hitbox falls straight through the world, and the client
local space manager chases it into chunks with no global spaces (process
pool saturation, crawl to a halt).

## 3) World setup (scene__main.c load handler)

Same checklist as 01, with three entity-relevant additions:

- The **spawn point is in world units: one whole value of Vector__3i32F4 is
  one tile** (a chunk is 8 tiles per axis). It sits one tile above the bottom
  layer (z=1) so the client hitbox lands on the z=0 ground.
- `allocate_hitbox_manager_from__hitbox_context(..., 256)` +
  `allocate_client_pool_for__game(..., 1)`.
- **The client's AABB hitbox is allocated HERE, planted at the spawn point,
  and sized.** It must exist (at the spawn point) before the load_client
  game action's outbound check runs in the first loop: that check reads the
  hitbox position to center the client's local space manager, then activates
  the hitbox and attaches it to the collision system. A missing/misplaced
  hitbox makes the engine re-center the local space manager onto the
  hitbox's actual chunk and the world slides out from under the client.

## 4) Graphics window + sprite manager

The world window is set up as in 01 (tileset texture, static camera,
`share_hitbox_manager_with__graphics_window`, `f_PLATFORM_compose_gfx_window
= PLATFORM_compose_world`), plus:

- `allocate_sprite_managers_from__sprite_context(ctx, 8)` — the sprite
  CONTEXT pool of Sprite_Managers starts empty and must be allocated before
  any per-window sprite manager.
- `allocate_sprite_manager_for__graphics_window(gfx, window, 16)` — the
  world window's sprite manager (16 slots).
- `world->p_graphics_window_for__world = window` — entity update handlers
  find the sprite manager through
  `get_p_graphics_window_from__world`.

## 5) The entity kind (types + registrar + update handler)

- `include/types/implemented/world/tile_kind.h`-style enum
  `include/types/implemented/entity/entity_kind.h` defines
  `Entity_Kind__Dummy` (1:1 with the entity function table slots).
- `entity_registrar.c` fills the `Entity_Functions` table (only
  `m_entity_update_handler` is needed) and registers the kind.
- `entity__dummy.c` — the update handler runs once per game tick for the
  entity and builds its components LAZILY (allocation only registers the
  entity; its components are built here, first tick):
  - **Sprite**: looked up with `get_p_sprite_by__uuid_from__sprite_manager`
    FIRST. `allocate_sprite_from__sprite_manager` is NOT idempotent — it
    grabs a fresh pool slot (plus a fresh platform texture and vertex
    object) on every call. Re-allocating it every tick overflows the sprite
    manager's fixed render-record array and corrupts the heap (segfault in
    the GL driver a dozen frames in). The lookup can return a DEALLOCATED
    slot (the pool dehashes by uuid), so validate with
    `is_sprite__deallocated`.
  - **Hitbox**: the scene's load handler already allocated it (it is the
    client's hitbox, keyed by the same uuid). The update handler just calls
    `set_size_of__hitbox_aabb`, which marks it dirty — that is what makes
    the collision system's per-tick movement pass (gravity) run for it.
    With ground registered in the tile logic table, the resolver's falling
    ray-cast finds the floor and the dummy lands on it and stays there.

## 6) The create_client process

`m_process__create_client` (registered with
`set_dispatch_handler_process_for__create_client`) runs when the load_client
game action finds no saved client file: it allocates the client's `Dummy`
entity (taking the client's uuid, so client and entity share identity and
the hitbox under that uuid) and sets the client as loaded. The hitbox is
NOT allocated here — see step 3.

## 7) The loops

As in 01: a first loop polls the tick timer + `manage_game__post_render`
until the load_client process finishes, then the main render loop
(`manage_game__pre_render` → `manage_world` → mark window dirty → compose →
render → `manage_game__post_render`). A screenshot is written once at frame
60.

## Engine Notes (things that are NOT this example's fault)

- `set_collision_node_for__global_space` has no call sites anywhere in the
  current engine, so a global space's collision node is never bound and
  `attach_object_to__collision_system` always prints
  `failed to attach` for a fresh client; the follow-up
  `remove_entry_from__collision_node, uuid__u32 not present in node` is the
  byproduct of that. Both are harmless here: ground collision uses the tile
  logic table, not the collision node.
