# System Overview: Raycast System

## Purpose

The raycast system provides fixed-point ray construction, stepping, and
measurement primitives for line-of-sight checks, pathfinding probes, and
distance measurements across the tile grid. All operations use `i32F20`
fixed-point arithmetic (32-bit integers with 20 bits of fractional
precision), ensuring deterministic behavior on platforms without
floating-point hardware.

## Architecture

### Data Hierarchy

    Ray__3i32F20
    +-- Vector__3i32F20  ray_starting_vector__3i32F20  (origin, immutable after construction)
    +-- Vector__3i32F20  ray_current_vector__3i32F20   (current endpoint, advanced by stepping)
    +-- Degree__u9       angle_of__ray                 (direction, 10 bits)
    +-- Ray_Plane_Mode   ray_plane_mode                (operating plane, 2 bits)

    Path  (consumer of Ray)
    +-- Ray__3i32F20     leading_ray_of__path
    +-- Vector__3i32     path_nodes__3i32[PATH_VECTORS_MAX_QUANTITY_OF]
    +-- Degree__u9       obstruction_indicent_stack[PATH_VECTORS_MAX_QUANTITY_OF]

### Key Types

| Type | Role |
|------|------|
| `Ray__3i32F20` | The core raycasting primitive. Encapsulates an origin, a current endpoint, a direction angle, and a plane mode. Constructed on the stack or embedded in a `Path`. |
| `Vector__3i32F20` | 3-component vector at i32F20 fixed-point precision. Used internally by the ray for high-accuracy sub-tile arithmetic. |
| `Vector__3i32F4` | 3-component vector at i32F4 fixed-point precision. The standard entity/hitbox position format. Rays accept this as input and can produce it as output. |
| `Vector__3i32` | 3-component vector at whole integer precision. Used for tile and chunk coordinate lookups. Rays can produce this as output. |
| `Degree__u9` | 9-bit angular unit (0–511 steps per full circle, ~0.7° resolution). Determines ray direction. |
| `Ray_Plane_Mode` | Enum selecting which 2D plane (XY, XZ, or YZ) the ray operates in. The third component remains constant throughout the ray's lifetime. |
| `Path` | Pathfinding structure that owns a `Ray__3i32F20` as its leading probe. Uses ray extension to explore multiple directions from each node. |

### Constants

| Constant | Value | Description |
|----------|-------|-------------|
| `LENGTH_OF_RAY__i32F20` | 255 (`0b11111111`) | Maximum ray step length per invocation in i32F20 units. |
| `ANGLE__0` | 0 | 0° direction. |
| `ANGLE__27_5` | 32 | 27.5° direction. |
| `ANGLE__45` | 64 | 45° direction. |
| `ANGLE__90` | 128 | 90° direction. |
| `ANGLE__180` | 256 | 180° direction. |
| `ANGLE__270` | 384 | 270° direction. |
| `ANGLE__360` | 512 | 360° (bounds checking sentinel only). |
| `ANGLE__OUT_OF_BOUNDS` | `MASK(10)` | Sentinel for invalid/out-of-bounds angles. |
| `VECTOR__3i32F20__OUT_OF_BOUNDS` | `{BIT(31), BIT(31), BIT(31)}` | Sentinel for invalid/out-of-bounds vectors. |

### Plane Modes

| Value | Description |
|-------|-------------|
| `Ray_Plane_Mode__XY` | Ray steps in the X-Y plane. Default for 2D top-down gameplay. |
| `Ray_Plane_Mode__XZ` | Ray steps in the X-Z plane. |
| `Ray_Plane_Mode__YZ` | Ray steps in the Y-Z plane. |

## Fixed-Point Precision Hierarchy

The ray system operates at i32F20 precision internally but interfaces
with the rest of the engine at lower precisions:

    i32F20 (internal ray math, 20 fractional bits)
        |
        v  get_ray_endpoint_as__vector_3i32F4()
    i32F4  (entity positions, hitbox positions, 4 fractional bits)
        |
        v  get_ray_endpoint_as__vector_3i32()
    i32    (tile coordinates, chunk coordinates, whole integers)

When constructing a ray via `get_ray`, the i32F4 input is promoted to
i32F20 via `vector_3i32F4_to__vector_3i32F20`. When reading results,
the appropriate extraction function is used for the desired precision
level.

## Lifecycle

### 1. Construction

A ray is constructed from a world-space position (typically an entity's
hitbox position in i32F4), a direction angle, and a plane mode:

    Ray__3i32F20 ray = get_ray(
            entity_position__3i32F4,
            ANGLE__90,
            Ray_Plane_Mode__XY);

The starting position is automatically promoted from i32F4 to i32F20
precision internally. The current vector is initialized to equal the
starting vector (zero displacement).

**Preconditions:**
- `starting_vector` should be a valid world-space position.
- `angle` should be less than `ANGLE__360` (512).

**Postconditions:**
- `ray_current_vector__3i32F20` equals `ray_starting_vector__3i32F20`.

### 2. Iterative Stepping

Rays are advanced incrementally using one of three step functions, each
providing a different granularity:

| Function | Granularity | Use Case |
|----------|-------------|----------|
| `step_p_ray` | Sub-tile fixed-point step | Fine-grained sampling, smooth interpolation. |
| `step_p_ray_until__next_whole_integer` | Integer boundary crossing | Grid-aligned checks at integer resolution. |
| `step_p_ray_until__next_tile` | Tile boundary crossing | Tile-based line-of-sight, pathfinding probes. Most common. |

The step size for `step_p_ray` is determined by `LENGTH_OF_RAY__i32F20`
and the angle offset from `get_2i32F20_offset_from__angle`.

Tile boundaries for `step_p_ray_until__next_tile` are determined by
`TILE__WIDTH_AND__HEIGHT__BIT_SHIFT` (default: 3, meaning 8-unit tiles).

**Preconditions:**
- `p_ray` must be non-null. No debug guards are present — the caller is
  responsible for null checks.

**Postconditions:**
- `ray_current_vector__3i32F20` has advanced in the direction of
  `angle_of__ray` within the specified `ray_plane_mode`.
- `ray_starting_vector__3i32F20` is unchanged.

### 3. Endpoint Extraction

After stepping, the ray's current endpoint can be extracted at the
desired precision:

    Vector__3i32F4 pos_f4 = get_ray_endpoint_as__vector_3i32F4(&ray);
    Vector__3i32   pos_i  = get_ray_endpoint_as__vector_3i32(&ray);

### 4. Distance Measurement

All distance functions return **squared** distances to avoid square root
operations (which are expensive on fixed-point-only hardware):

    if (is_p_ray_within__squared_length_i32(&ray, 10 * 10)) {
        // Ray endpoint is within 10 units of origin
    }

    i32F4 dist_sq = get_squared_length_i32F4_of__ray(&ray);
    i32F20 dist_sq_hp = get_squared_length_i32F20_of__ray(&ray);

**Precision note:** Both `get_squared_length_i32F4_of__ray` and
`get_squared_length_i32F20_of__ray` convert the displacement to i32F4
before computing the squared distance. The full i32F20 precision is
**not** preserved in distance calculations. For most gameplay purposes
(tile-range distances) this is acceptable.

### 5. Validity Checking

Rays can become invalid (out-of-bounds). The sentinel pattern is used
for error cases:

    Ray__3i32F20 ray = get_ray__out_of_bounds();
    // is_ray__out_of_bouds(ray) returns true

    Ray__3i32F20 ray = some_ray_operation(...);
    if (is_ray__out_of_bouds(ray)) {
        // Operation failed or ray is invalid
        return;
    }

The sentinel uses `VECTOR__3i32F20__OUT_OF_BOUNDS` for both vectors and
`ANGLE__OUT_OF_BOUNDS` for the angle, ensuring all validity checks
trigger.

**Note:** The function name `is_ray__out_of_bouds` contains a typo
(`bouds` instead of `bounds`). This is the canonical name.

### 6. Ray Extension

A new ray can be constructed from an existing ray's current endpoint,
inheriting the source ray's plane mode:

    Ray__3i32F20 extension = get_ray_as__extension(
            &original_ray,
            new_angle);

This is used in pathfinding where rays probe in multiple directions from
a common point.

**Preconditions:**
- `p_ray` must be non-null and not out-of-bounds.

## Typical Usage Pattern: Tile-Based Raycasting

    Ray__3i32F20 ray = get_ray(origin, angle, Ray_Plane_Mode__XY);

    while (!is_ray__out_of_bouds(ray)) {
        step_p_ray_until__next_tile(&ray);

        Vector__3i32 tile_pos = get_ray_endpoint_as__vector_3i32(&ray);
        Tile *p_tile = get_tile_at(p_world, tile_pos);

        if (is_tile__blocking(p_tile)) {
            // Ray hit an obstacle
            break;
        }

        if (!is_p_ray_within__squared_length_i32F4(&ray, max_range)) {
            // Ray exceeded maximum range
            break;
        }
    }

## Displacement Measurement

The displacement from a ray's origin to its current endpoint can be
queried as a full vector or per-component:

| Function | Returns | Description |
|----------|---------|-------------|
| `get_vector__3i32F20_wrt__p_ray_and_its_origin` | `Vector__3i32F20` | Full displacement vector (current − starting). |
| `get_x_offset_i32F4_of__ray` | `i32F4` | X component of displacement, converted to i32F4. |
| `get_y_offset_i32F4_of__ray` | `i32F4` | Y component of displacement, converted to i32F4. |
| `get_z_offset_i32F4_of__ray` | `i32F4` | Z component of displacement, converted to i32F4. |

## Integration with Path System

The `Path` struct uses `Ray__3i32F20` as its `leading_ray_of__path`
field. The pathfinding system advances the ray along candidate routes,
using `get_ray_as__extension` to probe in different directions at each
node:

    Path
    +-- Ray__3i32F20    leading_ray_of__path
    +-- Vector__3i32    path_nodes__3i32[PATH_VECTORS_MAX_QUANTITY_OF]
    +-- Degree__u9      obstruction_indicent_stack[PATH_VECTORS_MAX_QUANTITY_OF]

At each path node, the leading ray is extended in candidate directions.
The resulting endpoint positions are recorded in `path_nodes__3i32`, and
any obstruction angles are pushed onto `obstruction_indicent_stack`.

## Integration with Degree System

The ray system depends on `degree.h` for angle-to-offset conversion.
Two precision levels are available:

| Function | Precision | Range | Use |
|----------|-----------|-------|-----|
| `get_2i32F4_offset_from__angle` | i32F4 | Accurate within ~10 integer units | Short-range probes |
| `get_2i32F20_offset_from__angle` | i32F20 | High accuracy at long distances | Internal ray stepping |

The `Degree__u9` type divides the circle into 512 steps, giving
approximately 0.7° resolution per step. Additional degree utilities
provide conversion between angles and cardinal/ordinal directions,
angle arithmetic with wrapping, and angle computation between two
world-space points.

## Integration with Collision System

Rays are used for line-of-sight checks across the tile grid. The
typical pattern is:

1. Construct a ray from a source entity's position toward a target.
2. Step the ray tile-by-tile using `step_p_ray_until__next_tile`.
3. At each tile, query the world for blocking geometry.
4. If the ray reaches the target without hitting an obstacle,
   line-of-sight is confirmed.

The ray system itself does not directly reference `Collision_Node` or
`Hitbox_AABB` types. Integration occurs at the caller level, where ray
endpoints are used to index into spatial structures.

## Debug Logging

`get_squared_length_i32F20_of__ray` contains a `debug_info` call that
logs the delta vector components:

    debug_info("%d, %d",
            i32F20_to__i32(delta_vector__3i32F20.x__i32F20),
            i32F20_to__i32(delta_vector__3i32F20.y__i32F20));

This is active in debug builds (when `NDEBUG` and `NLOG` are not
defined) and can produce significant output during intensive raycasting.
No other debug output (`debug_abort`, `debug_error`, `debug_warning`)
is emitted by the ray module.

## Capacity Constraints

- Rays are stack-local or embedded in `Path` instances. There is no
  global ray pool or allocation limit.
- The `Path` struct limits the number of path nodes and obstruction
  records to `PATH_VECTORS_MAX_QUANTITY_OF`.
- Ray stepping precision is bounded by the `Degree__u9` angular
  resolution (~0.7° per step) and the `LENGTH_OF_RAY__i32F20` step
  size (255 i32F20 units per step).

## Thread Safety

Ray operations are **not** thread-safe. Rays are typically stack-local
or owned by a single `Path` instance. The engine's cooperative
scheduling model ensures all ray operations occur on a single thread.

## Error Handling

- `get_ray__out_of_bounds` provides a sentinel value for error cases.
- `is_ray__out_of_bouds` checks both vector bounds and angle bounds.
- No `debug_abort` or `debug_error` calls exist in the ray module.
- The only debug output is the `debug_info` call in
  `get_squared_length_i32F20_of__ray`.
