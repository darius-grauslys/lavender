# Specification: core/include/numerics.h

## Overview

Provides the engine's core numeric utility functions: fixed-point
arithmetic conversions, safe arithmetic operations (clamped, no-overflow,
delta), min/max, clamping, modular arithmetic, linear interpolation, and
fixed-point multiplication/division helpers.

This is one of the most widely included headers in the engine, as nearly
every subsystem performs fixed-point arithmetic.

## Dependencies

- `defines.h` (for all numeric typedefs)
- `defines_weak.h`
- `<stdint.h>`

## Macros

### Arithmetic Shift Macros

| Macro | Description |
|-------|-------------|
| `ARITHMETRIC_MASK(x, n)` | Modular mask that handles negative values correctly: `((x>=0) ? x & n : ((n+1 - ((-x) & n)) & n))`. |
| `ARITHMETRIC_R_SHIFT(x, n)` | Right shift that preserves sign for negative values (compiler-independent): `((x>=0) ? x >> n : -((-x) >> n))`. |
| `ARITHMETRIC_L_SHIFT(x, n)` | Left shift defined for negative values via unsigned cast: `(i32)((u32)(x) << n)`. |
| `ARITHMETRIC_L_SHIFT__u64(x, n)` | 64-bit variant of arithmetic left shift. |

## Constants

| Constant | Type | Value | Description |
|----------|------|-------|-------------|
| `MAX__U8` | `u8` | 255 | Maximum `u8` value. |
| `MAX__U16` | `u16` | 65535 | Maximum `u16` value. |
| `MAX__U32` | `u32` | 4294967295 | Maximum `u32` value. |

## Functions

### Index/Quantity Bounds Checking (static inline)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `is_index_u8__out_of_bounds` | `(Index__u8) -> bool` | `bool` | True if `== INDEX__UNKNOWN__u8`. |
| `is_index_u16__out_of_bounds` | `(Index__u16) -> bool` | `bool` | True if `== INDEX__UNKNOWN__u16`. |
| `is_index_u32__out_of_bounds` | `(Index__u32) -> bool` | `bool` | True if `== INDEX__UNKNOWN__u32`. |
| `is_quantity_u8__out_of_bounds` | `(Quantity__u8) -> bool` | `bool` | True if `== QUANTITY__UNKNOWN__u8`. |
| `is_quantity_u16__out_of_bounds` | `(Quantity__u16) -> bool` | `bool` | True if `== QUANTITY__UNKNOWN__u16`. |
| `is_quantity_u32__out_of_bounds` | `(Quantity__u32) -> bool` | `bool` | True if `== QUANTITY__UNKNOWN__u32`. |

### Fixed-Point Conversions (static inline)

| Function | Conversion | Description |
|----------|------------|-------------|
| `i32_to__i32F4` | `i32 -> i32F4` | Left shift by 4. |
| `i32F4_to__i32` | `i32F4 -> i32` | Arithmetic right shift by 4. |
| `i32_to__i32F8` | `i32 -> i32F8` | Left shift by 8. |
| `i32F8_to__i32` | `i32F8 -> i32` | Arithmetic right shift by 8. |
| `i32_to__i32F20` | `i32 -> i32F20` | Left shift by 20. |
| `i32F20_to__i32` | `i32F20 -> i32` | Arithmetic right shift by 20. |
| `i32F20_to__i32F4` | `i32F20 -> i32F4` | Arithmetic right shift by 16. |
| `i32F4_to__i32F20` | `i32F4 -> i32F20` | Left shift by 16. |
| `i32F20_to__i32F8` | `i32F20 -> i32F8` | Arithmetic right shift by 12. |
| `i32F8_to__i32F20` | `i32F8 -> i32F20` | Left shift by 12. |

### Min/Max (static inline)

| Function | Signature | Description |
|----------|-----------|-------------|
| `min__u8` | `(u8, u8) -> u8` | Returns the smaller value. |
| `min__u32` | `(u32, u32) -> u32` | Returns the smaller value. |
| `max__u8` | `(u8, u8) -> u8` | Returns the larger value. |
| `max__u32` | `(u32, u32) -> u32` | Returns the larger value. |
| `max__i32` | `(i32, i32) -> i32` | Returns the larger value. |

### Clamped Arithmetic (static inline)

| Function | Signature | Description |
|----------|-----------|-------------|
| `add_u8__clamped` | `(u8, u8, u8 clamp) -> u8` | Addition clamped to `clamp`. Uses `MAX__U8` for overflow detection. |
| `add_u16__clamped` | `(u16, u16, u16 clamp) -> u16` | Addition clamped to `clamp`. Uses `MAX__U16` for overflow detection. |
| `add_u32__clamped` | `(u32, u32, u32 clamp) -> u32` | Addition clamped to `clamp`. Uses `MAX__U32` for overflow detection. |
| `subtract_u8__clamped` | `(u8, u8, u8 min) -> u8` | Subtraction clamped to `min`. |
| `subtract_u16__clamped` | `(u16, u16, u16 min) -> u16` | Subtraction clamped to `min`. |
| `subtract_u32__clamped` | `(u32, u32, u32 min) -> u32` | Subtraction clamped to `min`. |
| `multiply_u8__clamped` | `(u8, u8, u8 clamp) -> u8` | Multiplication clamped to `clamp`. |
| `multiply_u16__clamped` | `(u16, u16, u16 clamp) -> u16` | Multiplication clamped to `clamp`. |
| `multiply_u32__clamped` | `(u32, u32, u32 clamp) -> u32` | Multiplication clamped to `clamp`. |
| `r_bitshift_u8__clamped` | `(u8, u8 shift, u8 min) -> u8` | Right shift clamped to `min`. Checks `shift >= 8`. |
| `r_bitshift_u16__clamped` | `(u16, u16 shift, u16 min) -> u16` | Right shift clamped to `min`. Checks `shift >= 16`. |
| `r_bitshift_u32__clamped` | `(u32, u32 shift, u32 min) -> u32` | Right shift clamped to `min`. Checks `shift >= 32`. |

### No-Overflow Arithmetic (static inline)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `subtract_u8__no_overflow` | `(u8, u8) -> u8` | `u8` | Returns 0 if would underflow. |
| `subtract_u16__no_overflow` | `(u16, u16) -> u16` | `u16` | Returns 0 if would underflow. |
| `subtract_u32__no_overflow` | `(u32, u32) -> u32` | `u32` | Returns 0 if would underflow. |
| `add_u8__no_overflow` | `(u8, u8, u8*) -> bool` | `bool` | Returns true on overflow (output not written). |
| `add_u16__no_overflow` | `(u16, u16, u16*) -> bool` | `bool` | Returns true on overflow (output not written). |
| `add_u32__no_overflow` | `(u32, u32, u32*) -> bool` | `bool` | Returns true on overflow (output not written). |
| `add_u64__no_overflow` | `(u64, u64, u64*) -> bool` | `bool` | Returns true on overflow (output not written). |

### Delta (static inline)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `delta_u8__no_overflow` | `(u8, u8) -> u8` | `u8` | Absolute difference. |
| `delta_u16__no_overflow` | `(u16, u16) -> u16` | `u16` | Absolute difference. |
| `delta_u32__no_overflow` | `(u32, u32) -> u32` | `u32` | Absolute difference. |

### Clamping (static inline)

| Function | Signature | Description |
|----------|-----------|-------------|
| `clamp__u8` | `(u8 value, u8 min, u8 max) -> u8` | Clamps value to [min, max]. |
| `clamp__p_u8` | `(u8*, u8 min, u8 max) -> void` | In-place clamp. |
| `clamp__i32` | `(i32 value, i32 min, i32 max) -> i32` | Clamps value to [min, max]. |
| `clamp__p_i32` | `(i32*, i32 min, i32 max) -> void` | In-place clamp. |

### Modulo (static inline)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `mod__i8_into__u8` | `(i8, i8) -> u8` | `u8` | Positive modulo for signed values. |
| `mod__i32_into__u32` | `(i32, i32) -> u32` | `u32` | Positive modulo for signed values. |

### Linear Interpolation (static inline)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `lerp__i32F4` | `(i32F4, i32F4, i32F4 x) -> i32F4` | `i32F4` | 1D lerp in F4 fixed-point. |
| `lerp__xy__i32F4` | `(i32F4 v00, v10, v01, v11, x, y) -> i32F4` | `i32F4` | 2D bilinear lerp in F4. |
| `lerp__i32F8` | `(i32F8, i32F8, i32F8 x) -> i32F8` | `i32F8` | 1D lerp in F8 fixed-point. |
| `lerp__xy__i32F8` | `(i32F8 v00, v10, v01, v11, x, y) -> i32F8` | `i32F8` | 2D bilinear lerp in F8. |

### Fixed-Point Division (static inline)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `divide_into__i32F4` | `(i32 p, i32 q) -> i32F4` | `i32F4` | `(p << 4) / q`. |
| `divide_into__i32F8` | `(i32 p, i32 q) -> i32F8` | `i32F8` | `(p << 8) / q`. |

### Fixed-Point Multiplication (static inline)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `multiply__i32F4` | `(i32F4, i32F4) -> i32F4` | `i32F4` | `(x * y) >> 4`. Max input: `BIT(12)` magnitude. |
| `multiply__i32F8` | `(i32F8, i32F8) -> i32F8` | `i32F8` | `(x * y) >> 8`. Max input: `BIT(8)` magnitude. |

## Agentic Workflow

### Fixed-Point Arithmetic Convention

The engine uses fixed-point arithmetic throughout to avoid floating-point
on platforms without an FPU (e.g. Nintendo DS). The naming convention is:

- `i32F4`: signed 32-bit, 4 fractional bits (28.4 format).
- `i32F8`: signed 32-bit, 8 fractional bits (24.8 format).
- `i32F20`: signed 32-bit, 20 fractional bits (12.20 format).

Conversion between formats always uses arithmetic shifts to preserve
sign correctness.

### Preconditions

- `multiply__i32F4`: inputs must not exceed `BIT(12)` in magnitude to
  avoid overflow in the intermediate `x * y` product.
- `multiply__i32F8`: inputs must not exceed `BIT(8)` in magnitude.
- `divide_into__i32F4` / `divide_into__i32F8`: `q` must not be 0.

### Error Handling

- No runtime error handling. Division by zero is undefined behavior.
- Overflow in fixed-point multiplication silently wraps.
