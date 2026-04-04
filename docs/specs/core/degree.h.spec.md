# Specification: core/include/degree.h

## Overview

Provides angle and direction utilities using the engine's fixed-point
`Degree__u9` type — a 9-bit unsigned integer representing angles in
512 discrete steps (0–511), where 512 steps = 360°. This gives a
resolution of approximately 0.703° per step.

Also provides conversion between angles and `Direction__u8` compass
directions, and functions to compute directional offset vectors from
angles.

## Dependencies

- `defines.h` (for `Degree__u9`, `Direction__u8`, `Vector__3i32`,
  `Vector__3i32F4`, `Vector__3i32F20`)

## Types

### Degree__u9

    typedef uint16_t Degree__u9;

A 9-bit angle value stored in a 16-bit integer. Valid range: `[0, 511]`.

### Angle Constants

| Constant | Value | Degrees |
|----------|-------|---------|
| `ANGLE__0` | 0 | 0° |
| `ANGLE__27_5` | 32 | 27.5° |
| `ANGLE__45` | 64 | 45° |
| `ANGLE__90` | 128 | 90° |
| `ANGLE__180` | 256 | 180° |
| `ANGLE__270` | 384 | 270° |
| `ANGLE__360` | 512 | 360° (bounds check only) |
| `ANGLE__MASK` | `MASK(5)` | Wrapping mask for sub-angle arithmetic. |
| `ANGLE__OUT_OF_BOUNDS` | `MASK(10)` | Sentinel for invalid angles. |

## Functions

### Angle Computation

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `get_angle_between__vectors_3i32` | `(Vector__3i32 source, Vector__3i32 target) -> Degree__u9` | `Degree__u9` | Computes the angle from `source` to `target`. O(log N) complexity. |

### Direction Conversion

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `get_direction_from__angle` | `(Degree__u9) -> Direction__u8` | `Direction__u8` | Converts an angle to the nearest compass direction. |
| `get_angle_from__direction` | `(Direction__u8) -> Degree__u9` | `Degree__u9` | Converts a compass direction to its canonical angle. |

### Angle Arithmetic (static inline)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `is_degree_u9__out_of_bounds` | `(Degree__u9) -> bool` | `bool` | Returns true if `angle >= ANGLE__OUT_OF_BOUNDS`. |
| `add_angles` | `(Degree__u9, Degree__u9) -> Degree__u9` | `Degree__u9` | Adds two angles with wrapping via `ANGLE__MASK`. |
| `subtract_angles` | `(Degree__u9 angle_1, Degree__u9 angle_2) -> Degree__u9` | `Degree__u9` | Subtracts `angle_2` from `angle_1` with circular wrapping. |

### Offset Vectors from Angle

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `get_2i32F4_offset_from__angle` | `(Degree__u9) -> Vector__3i32F4` | `Vector__3i32F4` | Returns a unit-ish offset vector at the given angle. Good for short range (≤10 integer units). |
| `get_2i32F20_offset_from__angle` | `(Degree__u9) -> Vector__3i32F20` | `Vector__3i32F20` | Returns a high-precision offset vector at the given angle. Excellent accuracy for ray casting. |

## Agentic Workflow

### When to Use

Use `Degree__u9` and these functions when:

- Computing facing direction for entities.
- Performing ray casting (use `get_2i32F20_offset_from__angle` for
  precision).
- Converting between angle and compass direction for movement or
  animation selection.

### Precision Trade-offs

| Function | Precision | Use Case |
|----------|-----------|----------|
| `get_2i32F4_offset_from__angle` | Low (4-bit fractional) | Short-range entity movement, tile lookups |
| `get_2i32F20_offset_from__angle` | High (20-bit fractional) | Ray casting, long-distance calculations |

### Angle Wrapping

`add_angles` uses `ANGLE__MASK` (`MASK(5)` = 31) for wrapping, which
only preserves the lower 5 bits. This masks to 32 values, **not** the
full 512-step range. This is intentional for sub-angle arithmetic within
a quadrant.

`subtract_angles` correctly handles the full 0–511 range by adding
`ANGLE__360` when the result would be negative.

### Preconditions

- Angles should be in range `[0, 511]` for valid results.
- `get_angle_between__vectors_3i32` operates on the XY plane.

### Postconditions

- `subtract_angles` always returns a value in `[0, 511]`.
- `get_direction_from__angle` returns a valid `Direction__u8` bitmask.

### Error Handling

- `is_degree_u9__out_of_bounds` can be used to validate angles before use.
- No runtime error handling; invalid angles produce undefined results.
