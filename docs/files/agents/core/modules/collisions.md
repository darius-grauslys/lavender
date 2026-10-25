# Collisions — AABB hitbox resolution with spatial indexing

**Sources:** `core/source/collisions/collision_resolver_aabb.c` + `core/source/collisions/hitbox_context.c` + `core/source/collisions/core/aabb/hitbox_aabb.c` + `core/source/collisions/core/aabb/hitbox_aabb_manager.c` + `core/source/collisions/collision_node.c` + `core/source/collisions/collision_node_pool.c`

## Surface Concerns

L3 SIMULATION module. Manages AABB hitboxes across per-manager pools, a per-global-space spatial index, and a type-erased opaque-access API. Pure logic — zero `platform.h` includes. Called from `manage_world()` each simulation tick. Hitboxes carry position/velocity (fixed-point `i32F4`) and acceleration (`i16F8`); gravity applied per-tick via `nGRAVITY_PER_TICK`. Movement flows through `game_action__hitbox` processes.

- **AABB collision detection** — Two-phase overlap test: moving corners of hitbox_one vs static corners of hitbox_two, then still-corner comparison for direction resolution. Returns `Direction__u8` bitmask (NORTH/SOUTH/EAST/WEST/ANY). Edge-only collisions handled via edge-overlap check.
- **Hitbox manager abstraction** — `Hitbox_Context` provides a type-erased interface to hitbox managers. Each manager type has an invocation table (allocator, deallocator, property access). `opaque_access_to__hitbox()` dispatches to the type's handler for uniform get/set of dimensions, position, velocity, acceleration, and flags.
- **Spatial indexing** — Each `Global_Space` has a `Collision_Node` (linked list of hitbox UUIDs). On move, entries transfer between nodes (via `poll_for_collision_node_update` in the `game_action__hitbox` process; note entries are only *created* by that cross-boundary path and the client teleport process). `poll_collision_resolver_aabb()` is designed to poll 8 adjacent chunks (N/NE/E/SE/S/SW/W/NW) plus current for each hitbox — but see Known rough edges: the south branch is currently mis-wired.
- **Tile collision + ground detection** — Checks all 4 hitbox corners against tile geometry for unpassable tiles. If falling (`velocity.z < 0`), steps a single downward ray (`ANGLE__180`, XZ plane) one tile at a time, testing the 4 corner X/Y positions against tiles at each z-level until ground is found, then dispatches `game_action__hitbox` to snap to ground level. Stair climb detected via `TILE_STAIR_HEIGHT` threshold.
- **Collision resolution handlers** — Two game-installed callbacks: entity-entity uses velocity-delta resolution with squared-delta threshold (`COLLISION_DELTA_THRESHOLD = 4096`) and `>> 2` energy dampening; entity-tile adjusts hitbox velocity based on which axis has the larger delta.
- **Movement polling** — Iterates all hitbox records: skips non-dirty or inactive ones (only dirty + active hitboxes move), computes new position (`pos + vel`) and new velocity (`vel + acc`), applies gravity as new acceleration, dispatches `game_action__hitbox`. All movement flows through the action protocol.

## Public API Surface

### Key Types

**`Hitbox_AABB`** — pooled per hitbox manager
- `_serialization_header` (UUID-32) — identity
- `position__3i32F4` — center position, 4 fractional bits
- `velocity__3i32F4` — movement vector, 4 fractional bits
- `acceleration__3i16F8` — acceleration vector, 8 fractional bits
- `width__quantity_u32` / `height__quantity_u32` — full dimensions (halves derived via `>> 1`)
- `hitbox_aabb_flags__u8` — ACTIVE, DIRTY

**`Hitbox_AABB_Manager`** — heap-allocated per manager instance
- `pM_pool_of__hitboxes` — pointer to `Hitbox_AABB` array
- `pM_ptr_array_of__hitbox_records` — pointer array for iteration
- `quantity_of__hitboxes` — capacity of the pool
- `index_of__next_hitbox_aabb_in__records` — insertion cursor

**`Hitbox_Context`** — embedded in `Game`
- `hitbox_manager_instances[]` — contiguous array of managed instances
- `hitbox_manager_registration_records[]` — function-pointer tables per manager type
- `hitbox_manager_instance__invocation_table[]` — invocation table per manager type

**`Hitbox_Manager_Instance`** — per-managed-instance metadata
- `_serialization_header` (UUID-32) — identity
- `type_of__hitbox_manager` — `Hitbox_Manager_Type` discriminator
- `pVM_hitbox_manager` — opaque pointer to actual manager struct

**`Collision_Node`** — per global space
- `_serialization_header` (UUID-64) — identity
- `p_linked_list__collision_node_entries__tail` — linked list head

**`Collision_Node_Entry`** — pool entry linking hitbox UUIDs to spatial nodes
- `uuid_of__hitbox__u32` — `IDENTIFIER__UNKNOWN__u32` when free
- `p_previous_entry` — linked list pointer

**`Collision_Node_Pool`** — embedded in `World`
- `collision_nodes[]` — per global space
- `collision_node_entries[]` — pool of entry structs

### Key Functions

```c
Direction__u8 is_hitbox_aabb__colliding(Hitbox_AABB *a, Hitbox_AABB *b);
Direction__u8 is_this_hitbox_aabb__overlapping_this_hitbox_aabb(Hitbox_AABB *one, Hitbox_AABB *two);
bool is_vector_3i32F4_inside__hitbox_aabb(Vector__3i32F4 v, Hitbox_AABB *h);
void set_hitbox_aabb__position_with__3i32F4(Hitbox_AABB *h, Vector__3i32F4 pos);
void initialize_hitbox_aabb_as__allocated(Hitbox_AABB *h, Identifier__u32 uuid, Quantity__u32 w, Quantity__u32 h, Vector__3i32F4 pos);
Hitbox_AABB *allocate_hitbox_aabb_from__hitbox_aabb_manager(Hitbox_AABB_Manager *mgr, Identifier__u32 uuid);
void release_hitbox_aabb_from__hitbox_aabb_manager(Game *g, Hitbox_AABB_Manager *mgr, Hitbox_AABB *h);
Hitbox_Manager_Instance *allocate_hitbox_manager_from__hitbox_context(Hitbox_Context *ctx, Identifier__u32 uuid, Hitbox_Manager_Type type, Quantity__u32 count);
bool opaque_access_to__hitbox(Hitbox_Context *ctx, Identifier__u32 uuid_mgr, Identifier__u32 uuid_hitbox, void *dims, void *pos, void *vel, void *acc, Hitbox_Flags__u8 *flags, bool is_setting);
void *get_pV_hitbox_from__hitbox_context(Hitbox_Context *ctx, Identifier__u32 uuid_mgr, Identifier__u32 uuid_hitbox);
void poll_collision_resolver_aabb(Game *g, Hitbox_AABB_Manager *mgr, f_Hitbox_AABB_Collision_Handler handler, f_Hitbox_AABB_Tile_Touch_Handler tile_handler);
void poll_hitbox_aabb_for__tile_collision(Game *g, Local_Space_Manager *lsm, Hitbox_AABB *h, f_Hitbox_AABB_Tile_Touch_Handler handler);
void poll_hitbox_manager_for__movement(Game *g, Hitbox_AABB_Manager *mgr);
bool add_entry_to__collision_node(Collision_Node_Pool *pool, Collision_Node *node, Chunk_Vector__3i32 gsv, Identifier__u32 uuid);
void remove_entry_from__collision_node(Collision_Node_Pool *pool, Collision_Node *node, Identifier__u32 uuid);
void poll_for__collisions_within_this__collision_node(Game *g, World *w, Collision_Node *node, f_Hitbox_AABB_Collision_Handler handler, Hitbox_AABB *hitbox);
```

## Known rough edges

- **South neighbor never polled:** in `poll_collision_resolver_aabb()`, the SOUTH branch checks `is_local_space__active(...->p_local_space__south)` but then polls the **east** local space's collision node (copy-paste of the EAST branch). Actual behavior: current + N + NE + E + SE + **E (again)** + SW + W + NW — south is never polled and east is polled twice, making neighbor collision detection asymmetric.
- **`poll_for__collisions_within_this__collision_node()` is AABB-specific** despite the type-erased design: it hard-casts the world-UUID hitbox manager to `Hitbox_AABB_Manager*` (collision_node.c).
- **`is_vector_3i32F4_inside__hitbox_aabb()`** (hitbox_aabb.c) tests `vector.z >= aa.z && vector.z <= aa.z` — `aa.z` twice where the upper bound should be `bb.z`. Since `aa.z == bb.z` today it behaves as an exact z-equality test; latent bug if the AABB ever gains z extent.
- `poll_collision_resolver_aabb()` / `poll_hitbox_manager_for__movement()` iterate the manager's dense pointer array and `break` on the first null — correct only because release is swap-with-tail; a gap would silently stop iteration.

## Key Files Table

| File | Role |
|------|------|
| `core/source/collisions/collision_resolver_aabb.c` | Main collision pass, tile collision, ground detection |
| `core/source/collisions/core/aabb/hitbox_aabb.c` | AABB geometry, collision detection, corner math |
| `core/source/collisions/hitbox_context.c` | Opaque hitbox access, manager allocation/deallocation |
| `core/source/collisions/core/aabb/hitbox_aabb_manager.c` | AABB manager, movement polling |
| `core/source/collisions/collision_node.c` | Collision node linked list, 1-hitbox polling |
| `core/source/collisions/collision_node_pool.c` | Collision node + entry pool allocation |
| `core/source/collisions/hitbox_manager_instance.c` | Manager instance init |
| `core/source/collisions/implemented/hitbox_context/hitbox_manager_registrar.c` | Register AABB manager type |
