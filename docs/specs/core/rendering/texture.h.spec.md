# 1. Specification: core/include/rendering/texture.h

## 1.1 Overview

Provides `static inline` helper functions for querying and mutating `Texture`
and `Texture_Flags` values. Textures are the fundamental image resource type
in the engine, wrapping a platform-specific `PLATFORM_Texture` pointer with
engine-managed flags that encode size, format, render method, visibility,
and read-only state. Also provides two non-inline functions for converting
flag-encoded dimensions to pixel counts.

## 1.2 Dependencies

- `defines_weak.h` (for `Texture_Flags` typedef)
- `defines.h` (for `Texture` struct, all `TEXTURE_FLAG__*` macros)

## 1.3 Types

### 1.3.1 Texture (struct)

    typedef struct Texture_t {
        PLATFORM_Texture *p_PLATFORM_texture;
        Texture_Flags texture_flags;
    } Texture;

| Field | Type | Description |
|-------|------|-------------|
| `p_PLATFORM_texture` | `PLATFORM_Texture*` | Platform-specific texture handle. |
| `texture_flags` | `Texture_Flags` | Encoded size, format, render method, and core flags. |

### 1.3.2 Texture_Flags (u32)

    typedef uint32_t Texture_Flags;

#### 1.3.2.1 Flag Layout (32 bits, MSB to LSB)

    [32..21] Platform-specific flags
    [20..13] Core flags (hidden, readonly, reserved)
    [12..10] Format (3 bits)
    [ 9.. 7] Render method (3 bits)
    [ 6.. 4] Width (3 bits)
    [ 3.. 1] Height (3 bits)

#### 1.3.2.2 Size Encoding

Width and height are each encoded as 3-bit indices:

| Value | Pixels |
|-------|--------|
| `0b000` | 8 |
| `0b001` | 16 |
| `0b010` | 32 |
| `0b011` | 64 |
| `0b100` | 128 |
| `0b101` | 256 |
| `0b110` | 512 |
| `0b111` | 1024 |

Special mappings for sizes > 1024 (e.g. `TEXTURE_FLAG__SIZE_2048x2048`).

#### 1.3.2.3 Convenience Size Macros

`TEXTURE_FLAG__SIZE_8x8`, `TEXTURE_FLAG__SIZE_16x16`,
`TEXTURE_FLAG__SIZE_32x32`, `TEXTURE_FLAG__SIZE_64x64`,
`TEXTURE_FLAG__SIZE_128x128`, `TEXTURE_FLAG__SIZE_256x256`,
`TEXTURE_FLAG__SIZE_512x512`, `TEXTURE_FLAG__SIZE_1024x1024`,
`TEXTURE_FLAG__SIZE_2048x2048`, `TEXTURE_FLAG__SIZE_4096x4096`,
`TEXTURE_FLAG__SIZE_8192x8192`, and various non-square combinations.

#### 1.3.2.4 Render Method (3 bits)

`TEXTURE_FLAG__RENDER_METHOD__0` through `TEXTURE_FLAG__RENDER_METHOD__7`.
Platform-specific meaning (e.g. on NDS: oamMain vs oamSub).

#### 1.3.2.5 Format (3 bits)

`TEXTURE_FLAG__FORMAT__15_RGB` (default), plus 7 platform-defined formats.

#### 1.3.2.6 Core Flags

| Flag | Description |
|------|-------------|
| `TEXTURE_FLAG__IS_HIDDEN` | Texture should not be rendered. |
| `TEXTURE_FLAG__IS_READONLY` | Texture data is read-only. |

#### 1.3.2.7 Composite Macro

    #define TEXTURE_FLAGS(size, method, format) ...

Combines size, render method, and format into a single `Texture_Flags` value.

## 1.4 Functions

### 1.4.1 Initialization (static inline)

| Function | Signature | Description |
|----------|-----------|-------------|
| `initialize_texture` | `(Texture) -> void` | Zeroes platform pointer and flags. **WARNING:** takes `Texture` by value — initializes a local copy only. Likely a bug; callers should initialize fields directly. |

### 1.4.2 Visibility (static inline)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `set_texture_flags_as__hidden` | `(Texture_Flags*) -> void` | `void` | Sets `TEXTURE_FLAG__IS_HIDDEN`. |
| `set_texture_flags_as__visible` | `(Texture_Flags*) -> void` | `void` | Clears `TEXTURE_FLAG__IS_HIDDEN`. |
| `is_texture_flags__hidden` | `(Texture_Flags) -> bool` | `bool` | True if `TEXTURE_FLAG__IS_HIDDEN` set. |

### 1.4.3 Read-Only (static inline)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `is_texture_flags__readonly` | `(Texture_Flags) -> bool` | `bool` | True if `TEXTURE_FLAG__IS_READONLY` set. |
| `set_texture_flags_as__readonly` | `(Texture_Flags*) -> void` | `void` | Sets `TEXTURE_FLAG__IS_READONLY`. |
| `set_texture_flags_as__not_readonly` | `(Texture_Flags*) -> void` | `void` | Clears `TEXTURE_FLAG__IS_READONLY`. |

### 1.4.4 Component Extraction (static inline)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `get_texture_flags__rendering_method` | `(Texture_Flags) -> Texture_Flags` | `Texture_Flags` | Returns the 3-bit render method value. |
| `get_texture_flags__format` | `(Texture_Flags) -> Texture_Flags` | `Texture_Flags` | Returns the 3-bit format value. |
| `get_texture_flags__width` | `(Texture_Flags) -> Texture_Flags` | `Texture_Flags` | Returns the 3-bit width index. |
| `get_texture_flags__height` | `(Texture_Flags) -> Texture_Flags` | `Texture_Flags` | Returns the 3-bit height index. |
| `get_texture_flags__size` | `(Texture_Flags) -> Texture_Flags` | `Texture_Flags` | Returns the 6-bit combined size value. |

### 1.4.5 Pixel Dimension Conversion

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `get_length_of__texture_flag__width` | `(Texture_Flags) -> Quantity__u16` | `Quantity__u16` | Returns the width in pixels. |
| `get_length_of__texture_flag__height` | `(Texture_Flags) -> Quantity__u16` | `Quantity__u16` | Returns the height in pixels. |

## 1.5 Agentic Workflow

### 1.5.1 Usage Pattern

`Texture_Flags` are passed to most allocation functions to specify desired
dimensions, format, and render method. `Sprite` contains two `Texture`
fields: `texture_for__sprite_to__sample` and `texture_of__sprite`.
`Aliased_Texture` wraps a `Texture` with a string name.
`PLATFORM_allocate_texture` / `PLATFORM_release_texture` manage the
underlying `PLATFORM_Texture`.

### 1.5.2 Preconditions

- Pointer-taking functions require non-null pointers.
- Value-taking functions have no preconditions.

## 1.6 Header Guard

`TEXTURE_H`
