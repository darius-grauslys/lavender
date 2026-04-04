# Specification: core/include/vectors.h

## Overview

Provides the engine's complete vector utility library: construction,
comparison, arithmetic, conversion between fixed-point formats, distance
calculations, and direction-based offset operations for all 3D vector
types used in the engine.

This is one of the most widely included headers, used by virtually every
system that deals with positions, velocities, or spatial calculations.

## Dependencies

- `defines.h` (for all vector types)
- `defines_weak.h`
- `numerics.h` (for fixed-point conversions, `multiply__i32F4`,
  `add_u32__no_overflow`)

## Constants

### Zero Vectors

| Constant | Type | Value |
|----------|------|-------|
| `VECTOR__3i32__0_0_0` | `Vector__3i32` | `{0, 0, 0}` |
| `VECTOR__3i32F4__0_0_0` | `Vector__3i32F4` | `{0, 0, 0}` |
| `VECTOR__3i32F20__0_0_0` | `Vector__3i32F20` | `{0, 0, 0}` |
| `VECTOR__3i16F8__0_0_0` | `Vector__3i16F8` | `{0, 0, 0}` |

### Unit Vectors

| Constant | Type | Value |
|----------|------|-------|
| `VECTOR__3i32F4__1_0_0` | `Vector__3i32F4` | `{1.0, 0, 0}` in F4 |
| `VECTOR__3i32F4__n1_0_0` | `Vector__3i32F4` | `{-1.0, 0, 0}` in F4 |
| `VECTOR__3i32F4__0_1_0` | `Vector__3i32F4` | `{0, 1.0, 0}` in F4 |
| `VECTOR__3i32F4__0_n1_0` | `Vector__3i32F4` | `{0, -1.0, 0}` in F4 |
| `VECTOR__3i32__1_0_0` | `Vector__3i32` | `{1, 0, 0}` |
| `VECTOR__3i32__n1_0_0` | `Vector__3i32` | `{-1, 0, 0}` |
| `VECTOR__3i32__0_1_0` | `Vector__3i32` | `{0, 1, 0}` |
| `VECTOR__3i32__0_n1_0` | `Vector__3i32` | `{0, -1, 0}` |

### Gravity Vectors

| Constant | Type | Description |
|----------|------|-------------|
| `VECTOR__3i16F8__0_0_nGRAVITY` | `Vector__3i16F8` | Gravity acceleration vector. |
| `VECTOR__3i16F8__0_0_nGRAVITY_PER_TICK` | `Vector__3i16F8` | Per-tick gravity vector. |

### Out-of-Bounds Sentinels

| Constant | Type | Value |
|----------|------|-------|
| `VECTOR__3i32__OUT_OF_BOUNDS` | `Vector__3i32` | `{BIT(31), BIT(31), BIT(31)}` |
| `VECTOR__3i32F4__OUT_OF_BOUNDS` | `Vector__3i32F4` | `{BIT(31), BIT(31), BIT(31)}` |
| `VECTOR__3i32F20__OUT_OF_BOUNDS` | `Vector__3i32F20` | `{BIT(31), BIT(31), BIT(31)}` |

## Functions

### Bounds Checking (static inline)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `is_vectors_3i32__out_of_bounds` | `(Vector__3i32) -> bool` | `bool` | True if any component equals the out-of-bounds sentinel. |
| `is_vectors_3i32F4__out_of_bounds` | `(Vector__3i32F4) -> bool` | `bool` | True if any component equals the out-of-bounds sentinel. |
| `is_vectors_3i32F20__out_of_bounds` | `(Vector__3i32F20) -> bool` | `bool` | True if any component equals the out-of-bounds sentinel. |

### Initialization (static inline)

| Function | Signature | Description |
|----------|-----------|-------------|
| `initialize_3i32F4_vector` | `(Vector__3i32F4*) -> void` | Sets all components to 0. |
| `initialize_3i32_vector` | `(Vector__3i32*) -> void` | Sets all components to 0. |

### Construction (static inline)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `get_vector__3u8` | `(u8, u8, u8) -> Vector__3u8` | `Vector__3u8` | Constructs a `Vector__3u8`. |
| `get_vector__3i16F8` | `(i16F8, i16F8, i16F8) -> Vector__3i16F8` | `Vector__3i16F8` | Constructs a `Vector__3i16F8`. |
| `get_vector__3i32F4` | `(i32F4, i32F4, i32F4) -> Vector__3i32F4` | `Vector__3i32F4` | Constructs a `Vector__3i32F4` from raw fixed-point values. |
| `get_vector__3i32F4_using__i32` | `(i32, i32, i32) -> Vector__3i32F4` | `Vector__3i32F4` | Constructs a `Vector__3i32F4` from integer values (auto-converts to F4). |
| `get_vector__3i32` | `(i32, i32, i32) -> Vector__3i32` | `Vector__3i32` | Constructs a `Vector__3i32`. |

### Equality (static inline)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `is_vectors_3i32F4__equal` | `(Vector__3i32F4, Vector__3i32F4) -> bool` | `bool` | Component-wise equality. |
| `is_vectors_3i16F8__equal` | `(Vector__3i16F8, Vector__3i16F8) -> bool` | `bool` | Component-wise equality. |
| `is_vectors_3i32F20__equal` | `(Vector__3i32F20, Vector__3i32F20) -> bool` | `bool` | Component-wise equality. |
| `is_vectors_3i32__equal` | `(Vector__3i32, Vector__3i32) -> bool` | `bool` | Component-wise equality. |
| `is_chunk_vectors_3i32__equal` | `(Chunk_Vector__3i32, Chunk_Vector__3i32) -> bool` | `bool` | Alias for `is_vectors_3i32__equal`. |

### Conversion (static inline)

| Function | Conversion | Description |
|----------|------------|-------------|
| `vector_3i32F4_to__vector_3i32` | `Vector__3i32F4 -> Vector__3i32` | Truncates fractional bits. |
| `vector_3i32_to__vector_3i32F4` | `Vector__3i32 -> Vector__3i32F4` | Shifts to add fractional bits. |
| `vector_3i32F20_to__vector_3i32F4` | `Vector__3i32F20 -> Vector__3i32F4` | Reduces precision. |
| `vector_3i32F4_to__vector_3i32F20` | `Vector__3i32F4 -> Vector__3i32F20` | Increases precision. |
| `vector_3i32F20_to__vector_3i32` | `Vector__3i32F20 -> Vector__3i32` | Truncates all fractional bits. |
| `vector_3i32F4_to__vector_3u8` | `Vector__3i32F4 -> Vector__3u8` | Truncates to unsigned bytes. |
| `vector_3i32F4_to__vector_3i16F8` | `Vector__3i32F4 -> Vector__3i16F8` | Converts F4 to F8 (left shift 4). |
| `vector_3i16F8_to__vector_3i32F4` | `Vector__3i16F8 -> Vector__3i32F4` | Converts F8 to F4 (right shift 4). |

### Arithmetic (static inline)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `add_vectors__3i32F4` | `(Vector__3i32F4, Vector__3i32F4) -> Vector__3i32F4` | `Vector__3i32F4` | Component-wise addition. |
| `add_vectors__3i32` | `(Vector__3i32, Vector__3i32) -> Vector__3i32` | `Vector__3i32` | Component-wise addition. |
| `add_vectors__3i16F8` | `(Vector__3i16F8, Vector__3i16F8) -> Vector__3i16F8` | `Vector__3i16F8` | Component-wise addition. |
| `subtract_vectors__3i32F4` | `(Vector__3i32F4, Vector__3i32F4) -> Vector__3i32F4` | `Vector__3i32F4` | Component-wise subtraction. |
| `subtract_vectors__3i32` | `(Vector__3i32, Vector__3i32) -> Vector__3i32` | `Vector__3i32` | Component-wise subtraction. |
| `subtract_vectors__3i32F20` | `(Vector__3i32F20, Vector__3i32F20) -> Vector__3i32F20` | `Vector__3i32F20` | Component-wise subtraction. |

### In-Place Arithmetic (static inline)

| Function | Signature | Description |
|----------|-----------|-------------|
| `add_p_vectors__3i32F4` | `(Vector__3i32F4*, Vector__3i32F4*) -> void` | Adds second into first. |
| `add_p_vectors__3i32F20` | `(Vector__3i32F20*, Vector__3i32F20*) -> void` | Adds second into first. |
| `add_p_vectors__3i32` | `(Vector__3i32*, Vector__3i32*) -> void` | Adds second into first. |
| `add_p_vectors__3i16F8` | `(Vector__3i16F8*, Vector__3i16F8*) -> void` | Adds second into first. |
| `subtract_p_vectors__3i32F4` | `(Vector__3i32F4*, Vector__3i32F4*) -> void` | Subtracts second from first. |
| `subtract_p_vectors__3i32` | `(Vector__3i32*, Vector__3i32*) -> void` | Subtracts second from first. |

### Component Access (static inline)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `get_x_i32F4_from__vector_3i32F4` | `(Vector__3i32F4) -> i32F4` | `i32F4` | Returns raw x component. |
| `get_y_i32F4_from__vector_3i32F4` | `(Vector__3i32F4) -> i32F4` | `i32F4` | Returns raw y component. |
| `get_z_i32F4_from__vector_3i32F4` | `(Vector__3i32F4) -> i32F4` | `i32F4` | Returns raw z component. |
| `get_x_i32_from__vector_3i32F4` | `(Vector__3i32F4) -> i32` | `i32` | Returns integer x (truncated). |
| `get_y_i32_from__vector_3i32F4` | `(Vector__3i32F4) -> i32` | `i32` | Returns integer y (truncated). |
| `get_z_i32_from__vector_3i32F4` | `(Vector__3i32F4) -> i32` | `i32` | Returns integer z (truncated). |
| `get_x_i32_from__vector_3i32` | `(Vector__3i32) -> i32` | `i32` | Returns x component. |
| `get_y_i32_from__vector_3i32` | `(Vector__3i32) -> i32` | `i32` | Returns y component. |
| `get_z_i32_from__vector_3i32` | `(Vector__3i32) -> i32` | `i32` | Returns z component. |
| `get_p_x_i32_from__p_vector_3i32` | `(Vector__3i32*) -> i32*` | `i32*` | Returns pointer to x. |
| `get_p_y_i32_from__p_vector_3i32` | `(Vector__3i32*) -> i32*` | `i32*` | Returns pointer to y. |
| `get_p_z_i32_from__p_vector_3i32` | `(Vector__3i32*) -> i32*` | `i32*` | Returns pointer to z. |

### Distance (static inline)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `get_distance_squared_of__vector_3i32` | `(Vector__3i32) -> i32` | `i32` | Squared magnitude. |
| `get_distance_squared_of__vector_3i32F4` | `(Vector__3i32F4) -> i32F4` | `i32F4` | Squared magnitude in F4. |
| `get_distance_squared_of__vector_3i32F20` | `(Vector__3i32F20) -> i32F20` | `i32F20` | Squared magnitude (via F4 conversion). |
| `get_distance_squared_of__vector_3i32__no_overflow` | `(Vector__3i32, u32*) -> bool` | `bool` | Returns true on overflow. |
| `get_manhattan_distance__of_vector_3i32_as__u32` | `(Vector__3i32, Vector__3i32) -> Quantity__u32` | `Quantity__u32` | Manhattan distance between two points. |
| `get_distance_hamming_of__vectors_3i32` | `(Vector__3i32, Vector__3i32) -> i32F4` | `i32F4` | Hamming (Manhattan) distance. |
| `get_distance_hamming_of__vectors_3i32F4` | `(Vector__3i32F4, Vector__3i32F4) -> i32F4` | `i32F4` | Hamming distance in F4. |

### Distance Checks (static inline)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `is_vector_3i32F20_within__squared_distance_i32` | `(Vector__3i32F20, i32) -> bool` | `bool` | True if squared magnitude ≤ distance (integer precision). |
| `is_vector_3i32F20_within__squared_distance_i32F4` | `(Vector__3i32F20, i32) -> bool` | `bool` | True if squared magnitude ≤ distance (F4 precision). |
| `is_vector_3i32F4_within__distance_i32F4` | `(Vector__3i32F4, i32F4) -> bool` | `bool` | True if magnitude ≤ distance (compares squared). |
| `is_vector_3i32_within__distance_i32` | `(Vector__3i32, i32) -> bool` | `bool` | True if magnitude ≤ distance (compares squared). |

### Direction Offset

| Function | Signature | Description |
|----------|-----------|-------------|
| `offset_vector_by__direction` | `(Vector__3i32F4*, Direction__u8) -> void` | Offsets a vector by one unit in the given compass direction. |

## Agentic Workflow

### When to Use

Use `vectors.h` functions for all spatial operations in the engine:

- Entity position/velocity arithmetic.
- Chunk and tile coordinate calculations.
- Distance checks for collision, AI range detection, etc.
- Converting between coordinate systems (world F4, ray F20, tile i32).

### Conversion Chain

    Vector__3i32F20 (ray casting, high precision)
         ↕ vector_3i32F20_to__vector_3i32F4 / vector_3i32F4_to__vector_3i32F20
    Vector__3i32F4 (positions, velocities)
         ↕ vector_3i32F4_to__vector_3i32 / vector_3i32_to__vector_3i32F4
    Vector__3i32 (tile coordinates, chunk coordinates)
         ↕ vector_3i32F4_to__vector_3u8
    Vector__3u8 (local tile coordinates)

### Out-of-Bounds Convention

The `OUT_OF_BOUNDS` sentinel vectors use `BIT(31)` (the sign bit) for
each component. Use `is_vectors_3*__out_of_bounds` to check before
operating on vectors that may be invalid.

### Preconditions

- Vectors passed to distance functions should not overflow when squared.
  Use `get_distance_squared_of__vector_3i32__no_overflow` for safe
  distance calculations on large vectors.
- `offset_vector_by__direction`: direction must be a valid `Direction__u8`
  bitmask.

### Error Handling

- `get_distance_squared_of__vector_3i32__no_overflow` returns true on
  overflow, leaving the output pointer unmodified.
- No other functions perform overflow checking.
