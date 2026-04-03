# Specification: core/include/world/camera.h

## Overview

Defines operations on `Camera` — the engine's viewport controller that
tracks a position, fulcrum (viewport dimensions), near/far planes, and
an optional follow target. Cameras can be attached to graphics windows
for world rendering.

## Dependencies

- `defines_weak.h` (forward declarations)
- `defines.h` (for `Camera`, `Graphics_Window`, `Game`, `Identifier__u32`)
- `vectors.h` (for `Vector__3i32F4`, `VECTOR__3i32F4__OUT_OF_BOUNDS`)

## Types

### Camera (struct)

    typedef struct Camera_t {
        Vector__3i32F4 position;
        m_Camera_Handler m_camera_handler;
        Quantity__u32 width_of__fulcrum;
        Quantity__u32 height_of__fulcrum;
        i32F20 z_near;
        i32F20 z_far;
        Identifier__u32 uuid_of__target__u32;
    } Camera;

| Field | Type | Description |
|-------|------|-------------|
| `position` | `Vector__3i32F4` | Camera position in pixel space. |
| `m_camera_handler` | `m_Camera_Handler` | Per-frame update callback. |
| `width_of__fulcrum` | `Quantity__u32` | Viewport width in pixels. |
| `height_of__fulcrum` | `Quantity__u32` | Viewport height in pixels. |
| `z_near` | `i32F20` | Near clipping plane. |
| `z_far` | `i32F20` | Far clipping plane. |
| `uuid_of__target__u32` | `Identifier__u32` | UUID of entity to follow, or `IDENTIFIER__UNKNOWN__u32`. |

### m_Camera_Handler (function pointer)

    typedef void (*m_Camera_Handler)(
            Camera *p_this_camera,
            Game *p_game,
            Graphics_Window *p_graphics_window);

### Default Constants

| Macro | Default | Description |
|-------|---------|-------------|
| `CAMERA_FULCRUM__WIDTH` | `256` | Default viewport width. |
| `CAMERA_FULCRUM__HEIGHT` | `196` | Default viewport height. |

## Functions

### Initialization

| Function | Signature | Description |
|----------|-----------|-------------|
| `initialize_camera` | `(Camera*, Vector__3i32F4, m_Camera_Handler, u32 width, u32 height, i32F20 z_near, i32F20 z_far) -> void` | Full initialization. |
| `initialize_camera_as__inactive` | `(Camera*) -> void` | Initializes with out-of-bounds position, null handler, and unknown dimensions. (static inline) |

### Default Handlers

| Function | Signature | Description |
|----------|-----------|-------------|
| `m_camera_handler__default` | `(Camera*, Game*, Graphics_Window*) -> void` | Default handler (no-op or basic behavior). |
| `m_camera_handler__follow__default` | `(Camera*, Game*, Graphics_Window*) -> void` | Follow handler that tracks `uuid_of__target__u32`. |

### State Queries

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `is_camera__active` | `(Camera*) -> bool` | `bool` | True if the camera has a valid (non-out-of-bounds) position. |
| `is_position_within__camera_fulcrum` | `(Camera*, Vector__3i32) -> bool` | `bool` | True if the position is OUTSIDE the fulcrum (inverted logic — returns true when NOT visible). (static inline) |

### Follow Target

| Function | Signature | Description |
|----------|-----------|-------------|
| `set_camera_to__follow` | `(Camera*, Identifier__u32) -> void` | Sets the follow target UUID. |

### Position Accessors (static inline)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `get_position_3i32_of__camera` | `(Camera*) -> Vector__3i32` | `Vector__3i32` | Returns integer position. |
| `get_position_3i32F4_of__camera` | `(Camera*) -> Vector__3i32F4` | `Vector__3i32F4` | Returns fixed-point position. |
| `get_x_i32_from__camera` | `(Camera*) -> i32` | `i32` | Returns X component. |
| `get_y_i32_from__camera` | `(Camera*) -> i32` | `i32` | Returns Y component. |
| `get_z_i32_from__camera` | `(Camera*) -> i32` | `i32` | Returns Z component. |

## Agentic Workflow

### Fulcrum Check Inversion

**WARNING:** `is_position_within__camera_fulcrum` returns `true` when the
position is OUTSIDE the fulcrum. This is inverted from what the name suggests.
The function checks `abs(delta) > fulcrum/2 + 16`.

### Ownership

Owned by `World` (at `world.camera`). Accessed via
`get_p_camera_from__world`. Can also be attached to `Graphics_Window` via
`set_p_camera_of__graphics_window`.

### Preconditions

- All functions require non-null `p_camera`.

## Header Guard

`CAMERA_H`
