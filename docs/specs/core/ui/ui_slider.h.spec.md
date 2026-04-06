# 9 Specification: core/include/ui/ui_slider.h

## 9.1 Overview

Specializes a `UI_Element` as a slider — a constrained draggable that moves
along a single axis within a defined span. Sliders produce a percentage
value based on their position within the span.

## 9.2 Dependencies

- `defines.h` (for `UI_Element`, slider union members)
- `defines_weak.h` (forward declarations)
- `game.h` (for `Game` type)
- `rendering/gfx_context.h` (for `Gfx_Context` accessors)
- `rendering/sprite.h` (for `Sprite` operations)
- `ui/ui_element.h` (for `UI_Element` operations, flag queries)
- `vectors.h` (for `Vector__3i32`)

## 9.3 Types

### 9.3.1 Slider-Specific Data (union members in UI_Element)

    struct {
        Vector__3i32 slider__spanning_length__3i32;
        u32          slider__distance__u32;
    };

| Field | Type | Description |
|-------|------|-------------|
| `slider__spanning_length__3i32` | `Vector__3i32` | Total span the slider can travel. |
| `slider__distance__u32` | `u32` | Current distance along the span. |

### 9.3.2 Axis Convention

- `UI_FLAGS__BIT_IS_SNAPPED_X_OR_Y_AXIS` = 1: slider moves along X axis.
- `UI_FLAGS__BIT_IS_SNAPPED_X_OR_Y_AXIS` = 0: slider moves along Y axis.

## 9.4 Functions

### 9.4.1 Initialization

| Function | Signature | Description |
|----------|-----------|-------------|
| `initialize_ui_element_as__slider` | `(UI_Element*, Vector__3i32 span, m_UI_Dragged, bool is_x_axis) -> void` | Initializes as slider. Sets kind to `UI_Element_Kind__Slider`. Sets dragged, transformed, and dispose handlers. |

### 9.4.2 Default Handlers

| Function | Signature | Description |
|----------|-----------|-------------|
| `m_ui_slider__dragged_handler__default` | `(UI_Element*, Game*, Graphics_Window*) -> void` | Default slider drag handler. |
| `m_ui_slider__dragged_handler__gfx_window__default` | `(UI_Element*, Game*, Graphics_Window*) -> void` | Slider drag handler that also scrolls the associated graphics window. |
| `m_ui_slider__transformed_handler__default` | `(UI_Element*, Hitbox_AABB*, Vector__3i32, Game*, Graphics_Window*) -> void` | Default slider transformed handler. |
| `m_ui_slider__dispose_handler__gfx_window__default` | `(UI_Element*, Game*, Graphics_Window*) -> void` | Dispose handler for gfx-window-associated sliders. |

### 9.4.3 Percentage Queries (static inline)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `get_percentage_i32F20_from__ui_slider` | `(Hitbox_AABB_Manager*, UI_Element*) -> i32F20` | `i32F20` | Returns slider position as fixed-point percentage. Divides `slider__distance__u32` by width (X) or height (Y). Debug aborts if not a slider. |
| `get_offset_from__ui_slider_percentage` | `(Hitbox_AABB_Manager*, UI_Element*, i32 range) -> i32` | `i32` | Returns a percentage of the given range. Debug aborts if not a slider. |

### 9.4.4 State Management (static inline)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `set_ui_slider_at__this_distance_u32` | `(UI_Element*, u32) -> void` | `void` | Sets `slider__distance__u32`. Debug aborts if not a slider. |
| `get_ui_slider__spanning_length` | `(UI_Element*) -> Vector__3i32` | `Vector__3i32` | Returns `slider__spanning_length__3i32`. |

## 9.5 Agentic Workflow

### 9.5.1 Preconditions

- All functions require non-null `p_ui_slider`.
- Debug builds abort if element is not `UI_Element_Kind__Slider` for percentage/distance functions.

### 9.5.2 Error Handling

- `get_percentage_i32F20_from__ui_slider`, `get_offset_from__ui_slider_percentage`, and `set_ui_slider_at__this_distance_u32` call `debug_error` and return 0/void if the element is not a slider (debug builds only).

## 9.6 Header Guard

`UI_SLIDER_H`
