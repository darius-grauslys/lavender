# Specification: core/include/raycast/ray.h

## Overview

Provides construction, stepping, and measurement utilities for the
`Ray__3i32F20` struct — the engine's fixed-point raycasting primitive.
Rays are used for line-of-sight checks, pathfinding probes, and
distance measurements across the tile grid.

All ray operations use `i32F20` fixed-point arithmetic (32-bit integers
with 20 bits of fractional precision), providing sub-tile accuracy
without floating-point hardware — critical for deterministic behavior
on the Nintendo DS and other fixed-point-only targets.

## Dependencies

- `defines.h` (for `Ray__3i32F20`, `Vector__3i32F4`, `Vector__3i32F20`,
  `Vector__3i32`, `Degree__u9`, `Ray_Plane_Mode`, `i32F4`, `i32F20`,
  `i32`)
- `defines_weak.h` (forward declarations)
- `degree.h` (for `is_degree_u9__out_of_bounds`, `get_2i32F20_offset_from__angle`,
  `get_2i32F4_offset_from__angle`, angle arithmetic)
- `vectors.h` (for `vector_3i32F20_to__vector_3i32F4`,
  `vector_3i32F20_to__vector_3i32`, `vector_3i32F4_to__vector_3i32F20`,
  `subtract_vectors__3i32F20`,
  `is_vectors_3i32F20__out_of_bounds`,
  `is_vector_3i32F20_within__squared_distance_i32`,
  `is_vector_3i32F20_within__squared_distance_i32F4`,
  `get_distance_squared_of__vector_3i32F4`,
  `get_distance_squared_of__vector_3i32F20`)

## Types

### Ray__3i32F20 (struct)

Defined in `defines.h`:

    typedef struct Ray__3i32F20_t {
        Vector__3i32F20 ray_starting_vector__3i32F20;
        Vector__3i32F20 ray_current_vector__3i32F20;
        Degree__u9 angle_of__ray        : 10;
        Ray_Plane_Mode ray_plane_mode   : 2;
    } Ray__3i32F20;

| Field | Type | Bits | Description |
|-------|------|------|-------------|
| `ray_starting_vector__3i32F20` | `Vector__3i32F20` | 96 | Origin point of the ray in i32F20 fixed-point space. Immutable after construction. |
| `ray_current_vector__3i32F20` | `Vector__3i32F20` | 96 | Current endpoint of the ray after stepping. Initially equals the starting vector. |
| `angle_of__ray` | `Degree__u9` | 10 | Direction of the ray expressed as a 9-bit degree value (0–511). See Degree Constants below. |
| `ray_plane_mode` | `Ray_Plane_Mode` | 2 | Which 2D plane the ray operates in (XY, XZ, or YZ). |

### Ray_Plane_Mode (enum)

Defined in `defines.h`:

    typedef enum Ray_Plane_Mode {
        Ray_Plane_Mode__XY,
        Ray_Plane_Mode__XZ,
        Ray_Plane_Mode__YZ,
    } Ray_Plane_Mode;

| Value | Description |
|-------|-------------|
| `Ray_Plane_Mode__XY` | Ray steps in the X-Y plane. Default for 2D top-down gameplay. |
| `Ray_Plane_Mode__XZ` | Ray steps in the X-Z plane. |
| `Ray_Plane_Mode__YZ` | Ray steps in the Y-Z plane. |

### Degree__u9 (u16)

A 9-bit angular unit where the full circle is divided into 512 steps.
Defined in `defines.h`:

    typedef uint16_t Degree__u9;

| Constant | Value | Angle |
|----------|-------|-------|
| `ANGLE__0` | 0 | 0° |
| `ANGLE__27_5` | 32 | 27.5° |
| `ANGLE__45` | 64 | 45° |
| `ANGLE__90` | 128 | 90° |
| `ANGLE__180` | 256 | 180° |
| `ANGLE__270` | 384 | 270° |
| `ANGLE__360` | 512 | 360° (bounds checking only) |
| `ANGLE__MASK` | `MASK(5)` | Mask for sub-angle bits (lower 5 bits). |
| `ANGLE__OUT_OF_BOUNDS` | `MASK(10)` | Sentinel for invalid/out-of-bounds rays. |

### Degree Utility Functions (from degree.h)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `get_angle_between__vectors_3i32` | `(Vector__3i32 source, Vector__3i32 target) -> Degree__u9` | `Degree__u9` | Log(N) complexity angle calculation between two points. |
| `get_direction_from__angle` | `(Degree__u9) -> Direction__u8` | `Direction__u8` | Converts angle to cardinal/ordinal direction bitmask. |
| `get_angle_from__direction` | `(Direction__u8) -> Degree__u9` | `Degree__u9` | Converts direction bitmask to angle. |
| `is_degree_u9__out_of_bounds` | `(Degree__u9) -> bool` | `bool` | True if angle >= `ANGLE__OUT_OF_BOUNDS`. (static inline) |
| `add_angles` | `(Degree__u9, Degree__u9) -> Degree__u9` | `Degree__u9` | Adds two angles with wrapping via `ANGLE__MASK`. (static inline) |
| `subtract_angles` | `(Degree__u9, Degree__u9) -> Degree__u9` | `Degree__u9` | Subtracts angle_2 from angle_1 with wrapping. (static inline) |
| `get_2i32F4_offset_from__angle` | `(Degree__u9) -> Vector__3i32F4` | `Vector__3i32F4` | Direction offset at i32F4 precision. Excellent for short range, not accurate beyond ~10 integer units. |
| `get_2i32F20_offset_from__angle` | `(Degree__u9) -> Vector__3i32F20` | `Vector__3i32F20` | Direction offset at i32F20 precision. High accuracy; long-distance inaccuracy limited only by Degree__u9 resolution. |

### Fixed-Point Constants

| Constant | Value | Description |
|----------|-------|-------------|
| `LENGTH_OF_RAY__i32F20` | `0b11111111` (255) | Maximum ray step length per invocation in i32F20 units. |

## Functions

### Construction

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `get_ray` | `(Vector__3i32F4 starting_vector, Degree__u9 angle, Ray_Plane_Mode plane_mode) -> Ray__3i32F20` | `Ray__3i32F20` | Constructs a ray from a starting position (converted from i32F4 to i32F20 internally via `vector_3i32F4_to__vector_3i32F20`), an angle, and a plane mode. The current vector is initialized to the starting vector. |
| `get_ray_as__extension` | `(Ray__3i32F20 *p_ray, Degree__u9 angle) -> Ray__3i32F20` | `Ray__3i32F20` | Constructs a new ray that begins at the current endpoint of `p_ray` and proceeds in the given angle. Inherits the plane mode of the source ray. |
| `get_ray__out_of_bounds` | `(void) -> Ray__3i32F20` | `Ray__3i32F20` | Returns a sentinel ray with `VECTOR__3i32F20__OUT_OF_BOUNDS` for both vectors and `ANGLE__OUT_OF_BOUNDS` for the angle. (static inline) |

### Stepping

| Function | Signature | Description |
|----------|-----------|-------------|
| `step_p_ray` | `(Ray__3i32F20*) -> void` | Advances the ray's current vector by one fixed-point step in the ray's direction. The step size is determined by `LENGTH_OF_RAY__i32F20` and the angle offset from `get_2i32F20_offset_from__angle`. |
| `step_p_ray_until__next_whole_integer` | `(Ray__3i32F20*) -> void` | Advances the ray until its current position crosses the next whole integer boundary (i.e. the i32F20 fractional part wraps to a new integer value). Used for grid-aligned sampling. |
| `step_p_ray_until__next_tile` | `(Ray__3i32F20*) -> void` | Advances the ray until it enters the next tile. Tile boundaries are determined by `TILE__WIDTH_AND__HEIGHT__BIT_SHIFT` (default: 3, meaning 8-unit tiles). |

### Validity Check (static inline)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `is_ray__out_of_bouds` | `(Ray__3i32F20 ray) -> bool` | `bool` | Returns true if the ray's current vector is out of bounds (via `is_vectors_3i32F20__out_of_bounds`) OR the angle is out of bounds (via `is_degree_u9__out_of_bounds`). Note: takes the ray **by value**, not by pointer. Note: the function name contains a typo (`bouds` instead of `bounds`). |

### Endpoint Extraction (static inline)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `get_ray_endpoint_as__vector_3i32F4` | `(Ray__3i32F20*) -> Vector__3i32F4` | `Vector__3i32F4` | Converts the ray's current endpoint from i32F20 to i32F4 precision via `vector_3i32F20_to__vector_3i32F4`. |
| `get_ray_endpoint_as__vector_3i32` | `(Ray__3i32F20*) -> Vector__3i32` | `Vector__3i32` | Converts the ray's current endpoint from i32F20 to whole integer coordinates via `vector_3i32F20_to__vector_3i32`. |

### Displacement Measurement (static inline)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `get_vector__3i32F20_wrt__p_ray_and_its_origin` | `(Ray__3i32F20*) -> Vector__3i32F20` | `Vector__3i32F20` | Returns the displacement vector from the ray's origin to its current endpoint (`current - starting`) via `subtract_vectors__3i32F20`. |
| `get_x_offset_i32F4_of__ray` | `(Ray__3i32F20*) -> i32F4` | `i32F4` | Returns the X component of displacement, converted from i32F20 to i32F4 via `i32F20_to__i32F4`. |
| `get_y_offset_i32F4_of__ray` | `(Ray__3i32F20*) -> i32F4` | `i32F4` | Returns the Y component of displacement, converted from i32F20 to i32F4. |
| `get_z_offset_i32F4_of__ray` | `(Ray__3i32F20*) -> i32F4` | `i32F4` | Returns the Z component of displacement, converted from i32F20 to i32F4. |

### Distance Measurement (static inline)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `is_p_ray_within__squared_length_i32` | `(Ray__3i32F20*, i32 length) -> bool` | `bool` | Returns true if the squared distance from origin to current endpoint is within the given squared length (in whole integer units). Uses `is_vector_3i32F20_within__squared_distance_i32`. |
| `is_p_ray_within__squared_length_i32F4` | `(Ray__3i32F20*, i32F4 length) -> bool` | `bool` | Returns true if the squared distance from origin to current endpoint is within the given squared length (in i32F4 units). Uses `is_vector_3i32F20_within__squared_distance_i32F4`. |
| `get_squared_length_i32F4_of__ray` | `(Ray__3i32F20*) -> i32F4` | `i32F4` | Returns the squared distance from origin to current endpoint. Converts displacement to i32F4 before squaring via `get_distance_squared_of__vector_3i32F4`. |
| `get_squared_length_i32F20_of__ray` | `(Ray__3i32F20*) -> i32F20` | `i32F20` | Returns the squared distance from origin to current endpoint at full i32F20 precision. Internally converts to i32F4 for the actual computation (via `get_distance_squared_of__vector_3i32F20`). Emits a `debug_info` log with the delta vector components. |

## Agentic Workflow

### Ray Construction Pattern

Rays are constructed from a world-space position (typically an entity's
hitbox position in i32F4) and a direction angle:

    Ray__3i32F20 ray = get_ray(
            entity_position__3i32F4,
            ANGLE__90,
            Ray_Plane_Mode__XY);

The starting position is automatically promoted from i32F4 to i32F20
precision internally. The current vector is initialized to the starting
vector (zero displacement).

### Iterative Stepping Pattern

Rays are advanced incrementally using the step functions. This is the
primary usage pattern for tile-based raycasting:

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

### Step Granularity

Three levels of stepping granularity are provided:

| Function | Granularity | Use Case |
|----------|-------------|----------|
| `step_p_ray` | Sub-tile fixed-point step | Fine-grained sampling, smooth interpolation. |
| `step_p_ray_until__next_whole_integer` | Integer boundary crossing | Grid-aligned checks at integer resolution. |
| `step_p_ray_until__next_tile` | Tile boundary crossing | Tile-based line-of-sight, pathfinding probes. Most common. |

### Ray Extension Pattern

To create a branching or deflected ray from an existing ray's endpoint:

    Ray__3i32F20 extension = get_ray_as__extension(
            &original_ray,
            new_angle);
    // extension starts where original_ray currently is
    // extension inherits original_ray's plane mode

This is used in pathfinding (see `Path` struct) where rays probe in
multiple directions from a common point.

### Out-of-Bounds Sentinel Pattern

Functions that may fail to produce a valid ray return the out-of-bounds
sentinel:

    Ray__3i32F20 ray = some_ray_operation(...);
    if (is_ray__out_of_bouds(ray)) {
        // Operation failed or ray is invalid
        return;
    }

The sentinel uses `VECTOR__3i32F20__OUT_OF_BOUNDS` (`{BIT(31), BIT(31),
BIT(31)}`) for both vectors and `ANGLE__OUT_OF_BOUNDS` (`MASK(10)`) for
the angle, ensuring all validity checks trigger.

### Fixed-Point Precision Hierarchy

The ray system operates at i32F20 precision internally but interfaces
with the rest of the engine at i32F4 precision:

    i32F20 (internal ray math, 20 fractional bits)
        |
        v  get_ray_endpoint_as__vector_3i32F4()
    i32F4  (entity positions, hitbox positions, 4 fractional bits)
        |
        v  get_ray_endpoint_as__vector_3i32()
    i32    (tile coordinates, chunk coordinates, whole integers)

When constructing a ray via `get_ray`, the i32F4 input is promoted to
i32F20 via `vector_3i32F4_to__vector_3i32F20`. When reading results,
use the appropriate extraction function for the desired precision level.

### Squared Distance Convention

All distance functions return **squared** distances to avoid square root
operations (which are expensive on fixed-point-only hardware). Comparisons
should use squared thresholds:

    // WRONG: comparing against linear distance
    // if (get_length_of_ray(...) < 10) ...

    // CORRECT: comparing against squared distance
    if (is_p_ray_within__squared_length_i32(&ray, 10 * 10)) {
        // Ray endpoint is within 10 units of origin
    }

### Precision Loss in Distance Functions

Both `get_squared_length_i32F4_of__ray` and
`get_squared_length_i32F20_of__ray` convert the displacement to i32F4
before computing the squared distance (via
`get_distance_squared_of__vector_3i32F4` or
`get_distance_squared_of__vector_3i32F20` which internally does the
same). This means the full i32F20 precision is **not** preserved in
distance calculations. For most gameplay purposes (tile-range distances)
this is acceptable.

### Debug Logging

`get_squared_length_i32F20_of__ray` contains a `debug_info` call that
logs the delta vector components:

    debug_info("%d, %d",
            i32F20_to__i32(delta_vector__3i32F20.x__i32F20),
            i32F20_to__i32(delta_vector__3i32F20.y__i32F20));

This is active in debug builds (when `NDEBUG` and `NLOG` are not
defined) and can produce significant output during intensive raycasting.
Consider this when profiling or reviewing log output.

### Relationship to Path System

The `Path` struct (defined in `defines.h`) uses `Ray__3i32F20` as its
`leading_ray_of__path` field. The pathfinding system advances the ray
along candidate routes, using `get_ray_as__extension` to probe in
different directions at each node:

    typedef struct Path_t {
        Ray__3i32F20    leading_ray_of__path;
        Vector__3i32    path_nodes__3i32[PATH_VECTORS_MAX_QUANTITY_OF];
        Degree__u9      obstruction_indicent_stack[PATH_VECTORS_MAX_QUANTITY_OF];
        ...
    } Path;

### Relationship to Degree System

The ray system depends on `degree.h` for angle-to-offset conversion.
Two precision levels are available:

- `get_2i32F4_offset_from__angle`: Short-range, lower precision.
  Excellent within ~10 integer units.
- `get_2i32F20_offset_from__angle`: Long-range, high precision.
  Used internally by the ray stepping functions.

The `Degree__u9` type divides the circle into 512 steps, giving
approximately 0.7° resolution per step.

### Plane Mode Usage

Most 2D top-down gameplay uses `Ray_Plane_Mode__XY`. The XZ and YZ
modes exist for 3D or side-view projections. The plane mode determines
which two components of the 3D vector are affected by stepping; the
third component remains constant throughout the ray's lifetime.

### Preconditions

- `get_ray`: `starting_vector` should be a valid world-space position.
  `angle` should be less than `ANGLE__360` (512).
- `get_ray_as__extension`: `p_ray` must be non-null and not
  out-of-bounds.
- All `step_p_ray*` functions: `p_ray` must be non-null. No debug
  guards are present — the caller is responsible for null checks.
- All `static inline` measurement functions: `p_ray` must be non-null.

### Postconditions

- After `get_ray`: `ray_current_vector__3i32F20` equals
  `ray_starting_vector__3i32F20` (zero displacement).
- After any `step_p_ray*` call: `ray_current_vector__3i32F20` has
  advanced in the direction of `angle_of__ray` within the specified
  `ray_plane_mode`. `ray_starting_vector__3i32F20` is unchanged.
- After `get_ray__out_of_bounds`: `is_ray__out_of_bouds` returns true.

### Error Handling

- `get_ray__out_of_bounds` provides a sentinel value for error cases.
- `is_ray__out_of_bouds` checks both vector bounds and angle bounds.
- No `debug_abort` or `debug_error` calls in this header. The only
  debug output is a `debug_info` call in
  `get_squared_length_i32F20_of__ray`.

### Thread Safety

Ray operations are **not** thread-safe. Rays are typically stack-local
or owned by a single `Path` instance. The engine's cooperative
scheduling model (see `process.h` specification) ensures all ray
operations occur on a single thread.
