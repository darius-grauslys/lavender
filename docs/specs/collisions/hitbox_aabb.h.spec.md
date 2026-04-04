# Specification: core/include/collisions/core/aabb/hitbox_aabb.h

## Overview

Provides initialization, collision detection, position/velocity/acceleration
management, and spatial queries for the `Hitbox_AABB` struct — the engine's
primary axis-aligned bounding box hitbox type. This is the concrete hitbox
implementation used by the default collision system.

`Hitbox_AABB` instances are pooled and managed by `Hitbox_AABB_Manager`.
Their spatial data drives both the collision resolver and the collision node
spatial partitioning system.

See `module_topology__collision.mmd` for the type hierarchy.

## Dependencies

- `defines.h` (for `Hitbox_AABB`, `Vector__3i32F4`, `Vector__3i32`,
  `Vector__3i16F8`, `Direction__u8`, `Identifier__u32`, `Quantity__u32`,
  `Hitbox_Flags__u8`, `i32F4`, `i16F8`, `Signed_Index__i32`)
- `defines_weak.h` (forward declarations)
- `vectors.h` (for vector conversion and component access)
- `world/chunk_vectors.h` (for chunk coordinate extraction)
- `collisions/hitbox.h` (for `Hitbox_Flags__u8` manipulation)

## Types

### Hitbox_AABB (struct)

Defined in `defines.h`:

    typedef struct Hitbox_AABB_t {
        Serialization_Header _serialization_header;
        Vector__3i32F4 position__3i32F4;
        Vector__3i32F4 velocity__3i32F4;
        Vector__3i16F8 acceleration__3i16F8;
        Quantity__u32 width__quantity_u32;
        Quantity__u32 height__quantity_u32;
        Hitbox_Flags__u8 hitbox_aabb_flags__u8;
    } Hitbox_AABB;

| Field | Type | Description |
|-------|------|-------------|
| `_serialization_header` | `Serialization_Header` | UUID and struct size for pool management. UUID matches the owning entity's UUID. |
| `position__3i32F4` | `Vector__3i32F4` | Center position in world space. Fixed-point with 4 bits of fractional precision. |
| `velocity__3i32F4` | `Vector__3i32F4` | Current velocity. Applied to position each physics tick. |
| `acceleration__3i16F8` | `Vector__3i16F8` | Current acceleration. Applied to velocity each physics tick. 16-bit with 8 bits fractional. |
| `width__quantity_u32` | `Quantity__u32` | Full width of the bounding box. |
| `height__quantity_u32` | `Quantity__u32` | Full height of the bounding box. |
| `hitbox_aabb_flags__u8` | `Hitbox_Flags__u8` | Active and dirty flags. See `hitbox.h.spec.md`. |

### Constants

| Constant | Value | Description |
|----------|-------|-------------|
| `COLLISION_DELTA_THRESHOLD` | 4096 | Minimum axis delta to consider for displacement. Allows sliding along surfaces. |

## Functions

### Initialization

| Function | Signature | Description |
|----------|-----------|-------------|
| `initialize_hitbox_aabb` | `(Hitbox_AABB*) -> void` | Zero-initializes all fields. Hitbox is inactive and not allocated. |
| `initialize_hitbox_aabb_as__allocated` | `(Hitbox_AABB*, Identifier__u32 uuid, Quantity__u32 width, Quantity__u32 height, Vector__3i32F4 position) -> void` | Initializes with UUID, dimensions, and position. Sets the hitbox as active and dirty. |

### Collision Detection

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `is_hitbox_aabb__colliding` | `(Hitbox_AABB* checking, Hitbox_AABB* other) -> Direction__u8` | `Direction__u8` | Tests overlap between two AABBs. Returns a direction bitmask indicating collision sides, or `DIRECTION__NONE` if no collision. |
| `is_this_hitbox_aabb__overlapping_this_hitbox_aabb` | `(Hitbox_AABB* one, Hitbox_AABB* two) -> Direction__u8` | `Direction__u8` | Checks if corners of `one` are inside `two`. Returns direction bitmask. Note: if `two` is fully inside `one`, returns `DIRECTION__NONE`. |
| `is_this_hitbox_aabb__fully_inside_this_hitbox_aabb__without_velocity` | `(Hitbox_AABB* one, Hitbox_AABB* two) -> bool` | `bool` | Returns true if `one` is entirely contained within `two`, ignoring velocity. |

### Point-In-Box Tests

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `is_vector_3i32F4_inside__hitbox_aabb` | `(Vector__3i32F4, Hitbox_AABB*) -> bool` | `bool` | Returns true if the fixed-point vector is inside the AABB. |
| `is_vector_3i32_inside__hitbox_aabb` | `(Vector__3i32, Hitbox_AABB*) -> bool` | `bool` | Returns true if the integer vector is inside the AABB. |

### Bounding Box Extraction

| Function | Signature | Description |
|----------|-----------|-------------|
| `get_aa_bb_as__vectors_3i32F4_from__hitbox_aabb` | `(Hitbox_AABB*, Vector__3i32F4* aa, Vector__3i32F4* bb) -> void` | Writes the min (aa) and max (bb) corners as fixed-point vectors. |
| `get_aa_bb_as__vectors_3i32_from__hitbox_aabb` | `(Hitbox_AABB*, Vector__3i32* aa, Vector__3i32* bb) -> void` | Writes the min (aa) and max (bb) corners as integer vectors. |
| `initialize_vector_3i32F4_as__aa_bb` | `(Vector__3i32F4*, Hitbox_AABB*, Direction__u8 corner) -> void` | Initializes a vector as a specific corner of the AABB, including velocity offset. |
| `initialize_vector_3i32F4_as__aa_bb_without__velocity` | `(Vector__3i32F4*, Hitbox_AABB*, Direction__u8 corner) -> void` | Same as above but without velocity offset. |
| `initialize_vector_3i32_as__aa_bb` | `(Vector__3i32*, Hitbox_AABB*, Direction__u8 corner) -> void` | Integer version with velocity offset. |
| `initialize_vector_3i32_as__aa_bb_without__velocity` | `(Vector__3i32*, Hitbox_AABB*, Direction__u8 corner) -> void` | Integer version without velocity offset. |

### Position Management

| Function | Signature | Description |
|----------|-----------|-------------|
| `set_hitbox_aabb__position_with__3i32F4` | `(Hitbox_AABB*, Vector__3i32F4) -> void` | Sets position directly. **Do not use** if the hitbox is registered in the collision system; use game actions instead. |
| `set_hitbox_aabb__position_with__3i32` | `(Hitbox_AABB*, Vector__3i32) -> void` | Sets position from integer vector. Same caveat as above. |
| `clamp_p_vector_3i32_to__hitbox_aabb` | `(Hitbox_AABB*, Vector__3i32*) -> void` | Clamps the given vector to be within the AABB bounds. |

### Direction Queries

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `get_movement_direction_of__hitbox_aabb` | `(Hitbox_AABB*) -> Direction__u8` | `Direction__u8` | Returns a direction bitmask based on the current velocity vector. |
| `get_tile_transition_direction_of__hitbox_aabb` | `(Hitbox_AABB*, Vector__3i32F4* aa, Vector__3i32F4* bb) -> Direction__u8` | `Direction__u8` | Returns the direction of tile boundary crossings based on the AABB corners. |

### Flag Accessors (static inline)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `is_hitbox_aabb__dirty` | `(Hitbox_AABB*) -> bool` | `bool` | Delegates to `is_hitbox_flags__dirty`. |
| `set_hitbox_aabb_as__dirty` | `(Hitbox_AABB*) -> bool` | `bool` | Delegates to `set_hitbox_flags_as__dirty`. |
| `set_hitbox_aabb_as__not_dirty` | `(Hitbox_AABB*) -> bool` | `bool` | Delegates to `set_hitbox_flags_as__not_dirty`. |
| `is_hitbox_aabb__active` | `(Hitbox_AABB*) -> bool` | `bool` | Delegates to `is_hitbox_flags__active`. |
| `set_hitbox_aabb_as__active` | `(Hitbox_AABB*) -> bool` | `bool` | Delegates to `set_hitbox_flags_as__active`. |
| `set_hitbox_aabb_as__disabled` | `(Hitbox_AABB*) -> bool` | `bool` | Delegates to `set_hitbox_flags_as__disabled`. |

### Position Getters (static inline)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `get_position_3i32F4_of__hitbox_aabb` | `(Hitbox_AABB*) -> Vector__3i32F4` | `Vector__3i32F4` | Returns the position. Debug builds call `debug_error` and return `VECTOR__3i32F4__OUT_OF_BOUNDS` on null. |
| `get_position_3i32_of__hitbox_aabb` | `(Hitbox_AABB*) -> Vector__3i32` | `Vector__3i32` | Returns position converted to integer. Debug builds call `debug_error` and return `VECTOR__3i32__OUT_OF_BOUNDS` on null. |
| `get_velocity_3i32F4_of__hitbox_aabb` | `(Hitbox_AABB*) -> Vector__3i32F4` | `Vector__3i32F4` | Returns velocity. Debug builds call `debug_error` and return `VECTOR__3i32F4__0_0_0` on null. |
| `get_acceleration_3i16F8_of__hitbox_aabb` | `(Hitbox_AABB*) -> Vector__3i16F8` | `Vector__3i16F8` | Returns acceleration. Debug builds call `debug_error` and return `VECTOR__3i16F8__0_0_0` on null. |

### Dimension Getters (static inline)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `get_width_u32_of__hitbox_aabb` | `(Hitbox_AABB*) -> Quantity__u32` | `Quantity__u32` | Returns width. Debug builds call `debug_error` and return 0 on null. |
| `get_height_u32_of__hitbox_aabb` | `(Hitbox_AABB*) -> Quantity__u32` | `Quantity__u32` | Returns height. Debug builds call `debug_error` and return 0 on null. |
| `set_size_of__hitbox_aabb` | `(Hitbox_AABB*, Quantity__u32 width, Quantity__u32 height) -> void` | `void` | Sets dimensions and marks dirty. Debug builds call `debug_error` on null. |

### Velocity Setters (static inline)

| Function | Signature | Description |
|----------|-----------|-------------|
| `apply_x_velocity_to__hitbox_aabb` | `(Hitbox_AABB*, i32F4) -> void` | Adds to x velocity. Debug builds call `debug_error` on null. |
| `apply_y_velocity_to__hitbox_aabb` | `(Hitbox_AABB*, i32F4) -> void` | Adds to y velocity. Debug builds call `debug_error` on null. |
| `apply_z_velocity_to__hitbox_aabb` | `(Hitbox_AABB*, i32F4) -> void` | Adds to z velocity. Debug builds call `debug_error` on null. |
| `apply_velocity_to__hitbox_aabb` | `(Hitbox_AABB*, Vector__3i32F4*) -> void` | Adds vector to velocity. Debug builds call `debug_error` on null. |
| `set_x_velocity_to__hitbox_aabb` | `(Hitbox_AABB*, i32F4) -> void` | Sets x velocity. Marks dirty. |
| `set_y_velocity_to__hitbox_aabb` | `(Hitbox_AABB*, i32F4) -> void` | Sets y velocity. Marks dirty. |
| `set_z_velocity_to__hitbox_aabb` | `(Hitbox_AABB*, i32F4) -> void` | Sets z velocity. Marks dirty. |
| `set_velocity_to__hitbox_aabb` | `(Hitbox_AABB*, Vector__3i32F4) -> void` | Sets full velocity vector. Marks dirty. |

### Acceleration Setters (static inline)

| Function | Signature | Description |
|----------|-----------|-------------|
| `set_x_acceleration_to__hitbox_aabb` | `(Hitbox_AABB*, i16F8) -> void` | Sets x acceleration. Marks dirty. |
| `set_y_acceleration_to__hitbox_aabb` | `(Hitbox_AABB*, i16F8) -> void` | Sets y acceleration. Marks dirty. |
| `set_z_acceleration_to__hitbox` | `(Hitbox_AABB*, i16F8) -> void` | Sets z acceleration. Marks dirty. |
| `set_acceleration_to__hitbox_aabb` | `(Hitbox_AABB*, Vector__3i16F8) -> void` | Sets full acceleration vector. Marks dirty. |

### Position Setters (static inline, TODO: REMOVE)

These are marked for removal. Use `dispatch_game_action__hitbox` instead
when the hitbox is registered in the collision system.

| Function | Signature | Description |
|----------|-----------|-------------|
| `set_x_position_to__hitbox_aabb` | `(Hitbox_AABB*, i32F4) -> void` | Sets x position. Marks dirty. |
| `set_y_position_to__hitbox_aabb` | `(Hitbox_AABB*, i32F4) -> void` | Sets y position. Marks dirty. |
| `set_z_position_to__hitbox_aabb` | `(Hitbox_AABB*, i32F4) -> void` | Sets z position. Marks dirty. |
| `offset_x_position_to__hitbox_aabb` | `(Hitbox_AABB*, i32F4) -> void` | Adds to x position. Marks dirty. |
| `offset_y_position_to__hitbox_aabb` | `(Hitbox_AABB*, i32F4) -> void` | Adds to y position. Marks dirty. |
| `offset_z_position_to__hitbox_aabb` | `(Hitbox_AABB*, i32F4) -> void` | Adds to z position. Marks dirty. |

### Chunk Coordinate Getters (static inline)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `get_x_i32F4_from__hitbox_aabb` | `(Hitbox_AABB*) -> i32F4` | `i32F4` | Returns x position as fixed-point. |
| `get_y_i32F4_from__hitbox_aabb` | `(Hitbox_AABB*) -> i32F4` | `i32F4` | Returns y position as fixed-point. |
| `get_z_i32F4_from__hitbox_aabb` | `(Hitbox_AABB*) -> i32F4` | `i32F4` | Returns z position as fixed-point. |
| `get_x_i32_from__hitbox_aabb` | `(Hitbox_AABB*) -> Signed_Index__i32` | `Signed_Index__i32` | Returns x position as integer. |
| `get_y_i32_from__hitbox_aabb` | `(Hitbox_AABB*) -> Signed_Index__i32` | `Signed_Index__i32` | Returns y position as integer. |
| `get_z_i32_from__hitbox_aabb` | `(Hitbox_AABB*) -> Signed_Index__i32` | `Signed_Index__i32` | Returns z position as integer. |
| `get_chunk_x_i32_from__hitbox_aabb` | `(Hitbox_AABB*) -> Signed_Index__i32` | `Signed_Index__i32` | Returns chunk x coordinate derived from position. |
| `get_chunk_y_i32_from__hitbox_aabb` | `(Hitbox_AABB*) -> Signed_Index__i32` | `Signed_Index__i32` | Returns chunk y coordinate derived from position. |
| `get_chunk_z_i32_from__hitbox_aabb` | `(Hitbox_AABB*) -> Signed_Index__i32` | `Signed_Index__i32` | Returns chunk z coordinate derived from position. |

## Agentic Workflow

### Hitbox AABB Lifecycle

    [Uninitialized]
        |
        initialize_hitbox_aabb(p_hitbox)
        |
    [Initialized, Inactive]
        |
        initialize_hitbox_aabb_as__allocated(p_hitbox, uuid, w, h, pos)
        |
    [Allocated, Active, Dirty]
        |
        (physics tick: velocity applied to position)
        (collision resolver: checks and responds)
        set_hitbox_aabb_as__not_dirty
        |
    [Allocated, Active, Clean]
        |
        (velocity/acceleration modified)
        set_hitbox_aabb_as__dirty
        |
    [Allocated, Active, Dirty]
        |
        set_hitbox_aabb_as__disabled
        |
    [Allocated, Inactive]

### Dirty Flag Contract

All setter functions (`set_*_velocity_to__hitbox_aabb`,
`set_*_acceleration_to__hitbox_aabb`, `set_*_position_to__hitbox_aabb`,
`set_size_of__hitbox_aabb`) automatically mark the hitbox as dirty. The
`apply_*_velocity_to__hitbox_aabb` functions do **not** mark dirty (they
are additive and typically called during physics integration which already
manages the dirty state).

### Position Modification Warning

Functions marked `TODO: REMOVE` (`set_x_position_to__hitbox_aabb`,
`offset_x_position_to__hitbox_aabb`, etc.) directly modify position without
going through the game action system. If the hitbox is registered in the
collision system (i.e. has a `Collision_Node_Entry`), direct position
modification can cause the hitbox to be in the wrong `Collision_Node`,
leading to missed collisions. Use `dispatch_game_action__hitbox` instead.

### Preconditions

- All `static inline` functions require a non-null `p_hitbox_aabb`. Debug
  builds call `debug_error` on null and return a safe default value.
- `set_hitbox_aabb__position_with__3i32F4` and
  `set_hitbox_aabb__position_with__3i32`: Must not be called on hitboxes
  registered in the collision system. Use game actions instead.

### Postconditions

- After `initialize_hitbox_aabb_as__allocated`: `is_hitbox_aabb__active`
  returns true, `is_hitbox_aabb__dirty` returns true.
- After any setter: `is_hitbox_aabb__dirty` returns true.

### Error Handling

- All `static inline` getters return safe defaults (zero vectors, zero
  dimensions, out-of-bounds vectors) on null in debug builds.
- All `static inline` setters return early on null in debug builds.
- `debug_error` is called with a descriptive message for each null check.
