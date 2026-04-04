# Specification: core/include/ui/ui_element.h

## Overview

Defines the core operations on `UI_Element` — the fundamental building block
of the UI system. A `UI_Element` is a polymorphic UI node that can act as a
button, slider, draggable, drop zone, text field, text box, window element,
or logical grouping. Elements form a tree via `p_parent`/`p_child` pointers
and a linked list via `p_next` pointers.

Each element has event handler function pointers (clicked, dragged, dropped,
held, typed, transformed, composed, disposed) and is identified by a
`Serialization_Header` UUID. Spatial data (position, size) is stored in an
externally-managed `Hitbox_AABB` looked up by UUID.

## Dependencies

- `defines.h` (for `UI_Element`, `UI_Flags__u16`, handler typedefs, all core types)
- `defines_weak.h` (forward declarations)
- `collisions/core/aabb/hitbox_aabb.h` (for `Hitbox_AABB` position/size accessors)
- `collisions/core/aabb/hitbox_aabb_manager.h` (for UUID-based hitbox lookup)
- `numerics.h` (for fixed-point arithmetic helpers)
- `platform.h` (for platform function signatures)
- `serialization/identifiers.h` (for UUID utilities)
- `serialization/serialization_header.h` (for `GET_UUID_P`, `IS_DEALLOCATED_P`)
- `vectors.h` (for `Vector__3i32`, `Vector__3i32F4` operations)

## Types

### UI_Element (struct)

    typedef struct UI_Element_t {
        Serialization_Header    _serialization_header;
        m_UI_Clicked            m_ui_clicked_handler;
        m_UI_Dragged            m_ui_dragged_handler;
        m_UI_Dropped            m_ui_dropped_handler;
        m_UI_Receive_Drop       m_ui_receive_drop_handler;
        m_UI_Held               m_ui_held_handler;
        m_UI_Typed              m_ui_typed_handler;
        m_UI_Transformed        m_ui_transformed_handler;
        m_UI_Compose            m_ui_compose_handler;
        m_UI_Dispose            m_ui_dispose_handler;
        UI_Element *p_parent, *p_child, *p_next;
        UI_Tile_Span            ui_tile_span;
        union {
            struct { UI_Button_Flags__u8 ui_button_flags; };
            struct { };
            struct {
                Vector__3i32 slider__spanning_length__3i32;
                u32          slider__distance__u32;
            };
            struct {
                Typer typer;
                char *pM_char_buffer;
                Quantity__u32 size_of__char_buffer;
                Index__u32 index_of__cursor_in__char_buffer;
            };
            struct {
                Graphics_Window *p_ui_window__graphics_window;
            };
        };
        UI_Flags__u16           ui_flags;
        UI_Element_Data         ui_element_data;
        enum UI_Element_Kind    the_kind_of_ui_element__this_is;
    } UI_Element;

| Field | Type | Description |
|-------|------|-------------|
| `_serialization_header` | `Serialization_Header` | UUID for pool management and hitbox lookup. |
| `m_ui_clicked_handler` | `m_UI_Clicked` | Click event handler. DO NOT INVOKE directly. |
| `m_ui_dragged_handler` | `m_UI_Dragged` | Drag event handler. DO NOT INVOKE directly. |
| `m_ui_dropped_handler` | `m_UI_Dropped` | Drop event handler. DO NOT INVOKE directly. |
| `m_ui_receive_drop_handler` | `m_UI_Receive_Drop` | Receive-drop event handler. DO NOT INVOKE directly. |
| `m_ui_held_handler` | `m_UI_Held` | Held event handler. DO NOT INVOKE directly. |
| `m_ui_typed_handler` | `m_UI_Typed` | Typed event handler. DO NOT INVOKE directly. |
| `m_ui_transformed_handler` | `m_UI_Transformed` | Transform event handler. DO NOT INVOKE directly. |
| `m_ui_compose_handler` | `m_UI_Compose` | Compose event handler. DO NOT INVOKE directly. |
| `m_ui_dispose_handler` | `m_UI_Dispose` | Dispose handler. DO NOT INVOKE directly. DO NOT REMOVE FROM UI_MANAGER from within. |
| `p_parent` | `UI_Element*` | Parent in the UI tree. |
| `p_child` | `UI_Element*` | First child in the UI tree. |
| `p_next` | `UI_Element*` | Next sibling in linked list. |
| `ui_tile_span` | `UI_Tile_Span` | 9-slice tile pattern for tile-based composition. |
| `ui_button_flags` | `UI_Button_Flags__u8` | Button-specific flags (union, active when Button). |
| `slider__spanning_length__3i32` | `Vector__3i32` | Slider total span (union, active when Slider). |
| `slider__distance__u32` | `u32` | Slider current distance (union, active when Slider). |
| `typer` | `Typer` | Text layout engine (union, active when Text/Text_Box). |
| `pM_char_buffer` | `char*` | Text buffer (union, active when Text/Text_Box). |
| `size_of__char_buffer` | `Quantity__u32` | Text buffer size (union, active when Text/Text_Box). |
| `index_of__cursor_in__char_buffer` | `Index__u32` | Cursor position (union, active when Text/Text_Box). |
| `p_ui_window__graphics_window` | `Graphics_Window*` | Child window (union, active when Window). |
| `ui_flags` | `UI_Flags__u16` | Runtime state flags. |
| `ui_element_data` | `UI_Element_Data` | Game-defined custom data. |
| `the_kind_of_ui_element__this_is` | `enum UI_Element_Kind` | Element kind discriminator. |

### Handler Signatures

| Typedef | Signature |
|---------|-----------|
| `m_UI_Dispose` | `void (*)(UI_Element*, Game*, Graphics_Window*)` |
| `m_UI_Clicked` | `void (*)(UI_Element*, Game*, Graphics_Window*)` |
| `m_UI_Dragged` | `void (*)(UI_Element*, Game*, Graphics_Window*)` |
| `m_UI_Dropped` | `void (*)(UI_Element*, Game*, Graphics_Window*)` |
| `m_UI_Receive_Drop` | `void (*)(UI_Element*, UI_Element*, Game*, Graphics_Window*)` |
| `m_UI_Held` | `void (*)(UI_Element*, Game*, Graphics_Window*)` |
| `m_UI_Typed` | `void (*)(UI_Element*, Game*, Graphics_Window*, unsigned char)` |
| `m_UI_Compose` | `void (*)(UI_Element*, Game*, Graphics_Window*)` |
| `m_UI_Transformed` | `void (*)(UI_Element*, Hitbox_AABB*, Vector__3i32, Game*, Graphics_Window*)` |

### UI_Flags__u16 (u16)

| Flag | Bit | Description |
|------|-----|-------------|
| `UI_FLAGS__BIT_IS_ENABLED` | 0 | Element is active and composable. |
| `UI_FLAGS__BIT_IS_FOCUSED` | 1 | Element has input focus. |
| `UI_FLAGS__BIT_IS_NON_INTERACTIVE` | 2 | Composes but ignores input. |
| `UI_FLAGS__BIT_IS_BEING_HELD` | 3 | Cursor is holding this element. |
| `UI_FLAGS__BIT_IS_BEING_DRAGGED` | 4 | Element is being dragged. |
| `UI_FLAGS__BIT_IS_SNAPPED_X_OR_Y_AXIS` | 5 | Slider axis: 1=X, 0=Y. |
| `UI_FLAGS__BIT_IS_USING__SPRITE_OR_UI_TILE_SPAN` | 6 | 1=sprite, 0=tile span. |
| `UI_FLAGS__BIT_CUSTOM_0` through `UI_FLAGS__BIT_CUSTOM_3` | 12-15 | Safe for game use. |

## Functions

### Initialization

| Function | Signature | Description |
|----------|-----------|-------------|
| `initialize_ui_element` | `(UI_Element*, UI_Element* parent, UI_Element* child, UI_Element* next, UI_Element_Kind, UI_Flags__u16) -> void` | Base initialization. Sets kind, flags, tree pointers. All handlers set to null. |

### Default Handlers

| Function | Signature | Description |
|----------|-----------|-------------|
| `m_ui_element__dispose_handler__default` | `(UI_Element*, Game*, Graphics_Window*) -> void` | Default dispose handler. Custom dispose handlers MUST call this. |
| `m_ui_element__compose_handler__default` | `(UI_Element*, Game*, Graphics_Window*) -> void` | Default compose: composes this element's tile span then recursively composes children. |
| `m_ui_element__compose_handler__default_non_recursive` | `(UI_Element*, Game*, Graphics_Window*) -> void` | Composes only this element, no children. |
| `m_ui_element__compose_handler__default_only_recursive` | `(UI_Element*, Game*, Graphics_Window*) -> void` | Composes only children, skipping this element. |
| `m_ui_element__transformed_handler__default` | `(UI_Element*, Hitbox_AABB*, Vector__3i32, Game*, Graphics_Window*) -> void` | Default transformed handler. On first call, assume position is unknown. |

### Hitbox Management

| Function | Signature | Description |
|----------|-----------|-------------|
| `allocate_hitbox_for__ui_element` | `(Game*, Graphics_Window*, UI_Element*, u32 width, u32 height, Vector__3i32 position) -> void` | Allocates a `Hitbox_AABB` and associates it with this element via UUID. |

### Position and Size

| Function | Signature | Description |
|----------|-----------|-------------|
| `set_positions_of__ui_elements_in__succession` | `(Game*, Graphics_Window*, UI_Element*, Vector__3i32 start, i32 x_stride, u32 per_row, i32 y_stride) -> void` | Positions a `p_next` linked list in a grid layout. |
| `set_position_3i32_of__ui_element` | `(Game*, Graphics_Window*, UI_Element*, Vector__3i32) -> void` | Sets position and invokes transformed handler. |
| `set_ui_element__size` | `(Game*, Graphics_Window*, UI_Element*, u32 width, u32 height) -> void` | Sets hitbox dimensions. |
| `set_ui_element__hitbox` | `(Game*, Graphics_Window*, UI_Element*, u32 width, u32 height, Vector__3i32) -> void` | Sets both size and position. |

### Sprite and Tile Span

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `set_ui_element__sprite` | `(UI_Element*, Sprite*) -> void` | `void` | Associates a sprite and sets sprite rendering mode. |
| `release_ui_element__PLATFORM_sprite` | `(Gfx_Context*, UI_Element*) -> void` | `void` | Releases the platform sprite. |
| `set_ui_tile_span_of__ui_element` | `(UI_Element*, UI_Tile_Span*) -> void` | `void` | Copies a tile span into the element. |
| `get_ui_tile_span_of__ui_element` | `(Hitbox_AABB_Manager*, Graphics_Window*, UI_Element*, u32* width, u32* height, u32* x, u32* y) -> const UI_Tile_Span*` | `const UI_Tile_Span*` | Returns tile span and computes tile-space dimensions/position. |
| `does_ui_element_have__sprite` | `(Sprite_Manager*, UI_Element*) -> bool` | `bool` | True if using sprite mode and has a valid sprite. |

### Tree Management

| Function | Signature | Description |
|----------|-----------|-------------|
| `set_child_of__ui_element` | `(UI_Element*, UI_Element* child) -> void` | Sets the child pointer. |
| `set_parent_of__ui_element` | `(UI_Element*, UI_Element* parent) -> void` | Sets the parent pointer. |
| `update_ui_element_origin__relative_to__recursively` | `(Game*, UI_Manager*, UI_Element*, Vector__3i32 old, Vector__3i32 new) -> void` | Recursively updates positions when parent origin changes. |
| `update_ui_element_origin__relative_to` | `(Game*, UI_Manager*, UI_Element*, Vector__3i32 old, Vector__3i32 new) -> void` | Updates position of this element only (non-recursive). |

### Hitbox Access (static inline)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `get_p_hitbox_aabb_of__ui_element` | `(Hitbox_AABB_Manager*, UI_Element*) -> Hitbox_AABB*` | `Hitbox_AABB*` | Looks up hitbox by UUID via `get_p_hitbox_aabb_by__uuid_u32_from__hitbox_aabb_manager`. |
| `clamp_p_vector_3i32_to__ui_element` | `(Hitbox_AABB_Manager*, UI_Element*, Vector__3i32*) -> void` | `void` | Clamps position to element bounds via `clamp_p_vector_3i32_to__hitbox_aabb`. |
| `get_x_i32_from__p_ui_element` | `(Hitbox_AABB_Manager*, UI_Element*) -> Signed_Index__i32` | `Signed_Index__i32` | Returns integer X position. |
| `get_y_i32_from__p_ui_element` | `(Hitbox_AABB_Manager*, UI_Element*) -> Signed_Index__i32` | `Signed_Index__i32` | Returns integer Y position. |
| `get_z_i32_from__p_ui_element` | `(Hitbox_AABB_Manager*, UI_Element*) -> Signed_Index__i32` | `Signed_Index__i32` | Returns integer Z position. |
| `get_position_3i32_from__p_ui_element` | `(Hitbox_AABB_Manager*, UI_Element*) -> Vector__3i32` | `Vector__3i32` | Returns integer position via `vector_3i32F4_to__vector_3i32`. |
| `get_position_3i32F4_from__p_ui_element` | `(Hitbox_AABB_Manager*, UI_Element*) -> Vector__3i32F4` | `Vector__3i32F4` | Returns fixed-point position. |
| `get_width_from__p_ui_element` | `(Hitbox_AABB_Manager*, UI_Element*) -> Quantity__u32` | `Quantity__u32` | Returns width from hitbox. |
| `get_height_from__p_ui_element` | `(Hitbox_AABB_Manager*, UI_Element*) -> Quantity__u32` | `Quantity__u32` | Returns height from hitbox. |

### Linked List (static inline)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `link_ui_element_to__this_ui_element` | `(UI_Element* predecessor, UI_Element* successor) -> void` | `void` | Sets `predecessor->p_next = successor`. Self-link sets `p_next` to null. |
| `get_next__ui_element` | `(UI_Element*) -> UI_Element*` | `UI_Element*` | Returns `p_next`. |
| `get_parent_of__ui_element` | `(UI_Element*) -> UI_Element*` | `UI_Element*` | Returns `p_parent`. |
| `get_child_of__ui_element` | `(UI_Element*) -> UI_Element*` | `UI_Element*` | Returns `p_child`. |
| `iterate_to_next__ui_element` | `(UI_Element* volatile*) -> UI_Element*` | `UI_Element*` | Returns current, advances to `p_next`. Null-safe. |
| `iterate_to_parent_of__ui_element` | `(UI_Element* volatile*) -> UI_Element*` | `UI_Element*` | Returns current, advances to `p_parent`. Null-safe. |
| `iterate_to_child_of__ui_element` | `(UI_Element* volatile*) -> UI_Element*` | `UI_Element*` | Returns current, advances to `p_child`. Null-safe. |

### Kind Query (static inline)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `is_ui_element_of__this_kind` | `(UI_Element*, UI_Element_Kind) -> bool` | `bool` | True if element matches the given kind. |

### Flag Queries (static inline)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `get_ui_element__flags` | `(UI_Element*) -> UI_Flags__u16` | `UI_Flags__u16` | Returns raw flags. |
| `is_ui_element__enabled` | `(UI_Element*) -> bool` | `bool` | True if `IS_ENABLED` set. |
| `is_ui_element__focused` | `(UI_Element*) -> bool` | `bool` | True if `IS_FOCUSED` set. |
| `is_ui_element__non_interactive` | `(UI_Element*) -> bool` | `bool` | True if `IS_NON_INTERACTIVE` set. |
| `is_ui_element__being_held` | `(UI_Element*) -> bool` | `bool` | True if `IS_BEING_HELD` set. |
| `is_ui_element__being_dragged` | `(UI_Element*) -> bool` | `bool` | True if `IS_BEING_DRAGGED` set. |
| `is_ui_element__snapped_x_or_y_axis` | `(UI_Element*) -> bool` | `bool` | True if `IS_SNAPPED_X_OR_Y_AXIS` set (X axis). |
| `is_ui_element__using_sprite_or__ui_tile_span` | `(UI_Element*) -> bool` | `bool` | Raw flag check for `IS_USING__SPRITE_OR_UI_TILE_SPAN`. |
| `is_ui_element__using_sprite` | `(UI_Element*) -> bool` | `bool` | True if using sprite rendering mode. |
| `is_ui_element__using_ui_tile_span` | `(UI_Element*) -> bool` | `bool` | True if using tile span rendering mode. |
| `does_ui_element_have__parent` | `(UI_Element*) -> bool` | `bool` | Null-safe. True if has parent. |
| `does_ui_element_have__child` | `(UI_Element*) -> bool` | `bool` | Null-safe. True if has child. |
| `does_ui_element_have__next` | `(UI_Element*) -> bool` | `bool` | Null-safe. True if has next. |

### Flag Mutations (static inline)

| Function | Signature | Description |
|----------|-----------|-------------|
| `set_ui_element_as__focused` | `(UI_Element*) -> void` | Sets `IS_FOCUSED`. |
| `set_ui_element_as__NOT_focused` | `(UI_Element*) -> void` | Clears `IS_FOCUSED`. |
| `set_ui_element_as__being_dragged` | `(UI_Element*) -> void` | Sets `IS_BEING_DRAGGED`. |
| `set_ui_element_as__NOT_being_dragged` | `(UI_Element*) -> void` | Clears `IS_BEING_DRAGGED`. |
| `set_ui_element_as__being_held` | `(UI_Element*) -> void` | Sets `IS_BEING_HELD`. |
| `set_ui_element_as__dropped` | `(UI_Element*) -> void` | Clears both `IS_BEING_HELD` and `IS_BEING_DRAGGED`. |
| `set_ui_element_as__using_sprite` | `(UI_Element*) -> void` | Sets `IS_USING__SPRITE_OR_UI_TILE_SPAN`. |
| `set_ui_element_as__using_ui_tile_span` | `(UI_Element*) -> void` | Clears `IS_USING__SPRITE_OR_UI_TILE_SPAN`. |
| `set_ui_element_as__snapped_x_axis` | `(UI_Element*) -> void` | Sets `IS_SNAPPED_X_OR_Y_AXIS`. |
| `set_ui_element_as__snapped_y_axis` | `(UI_Element*) -> void` | Clears `IS_SNAPPED_X_OR_Y_AXIS`. |
| `set_ui_element__snapped_state` | `(UI_Element*, bool is_x) -> void` | Sets axis based on bool. |
| `set_ui_element_as__enabled` | `(UI_Element*) -> void` | Sets `IS_ENABLED`. |
| `set_ui_element_as__disabled` | `(UI_Element*) -> void` | Clears `IS_ENABLED`. |
| `set_ui_element_as__non_interactive` | `(UI_Element*) -> void` | Sets `IS_NON_INTERACTIVE`. Different from disabled: still composes but ignores input. Use for background overlays. |
| `set_ui_element_as__interactive` | `(UI_Element*) -> void` | Clears `IS_NON_INTERACTIVE`. |

### Handler Setters (static inline)

| Function | Signature | Description |
|----------|-----------|-------------|
| `set_ui_element__dispose_handler` | `(UI_Element*, m_UI_Dispose) -> void` | Sets dispose handler. |
| `set_ui_element__clicked_handler` | `(UI_Element*, m_UI_Clicked) -> void` | Sets click handler. |
| `set_ui_element__dragged_handler` | `(UI_Element*, m_UI_Dragged) -> void` | Sets drag handler. |
| `set_ui_element__dropped_handler` | `(UI_Element*, m_UI_Dropped) -> void` | Sets drop handler. |
| `set_ui_element__receive_drop_handler` | `(UI_Element*, m_UI_Receive_Drop) -> void` | Sets receive-drop handler. |
| `set_ui_element__held_handler` | `(UI_Element*, m_UI_Held) -> void` | Sets held handler. |
| `set_ui_element__typed_handler` | `(UI_Element*, m_UI_Typed) -> void` | Sets typed handler. |
| `set_ui_element__transformed_handler` | `(UI_Element*, m_UI_Transformed) -> void` | Sets transformed handler. |
| `set_ui_element__compose_handler` | `(UI_Element*, m_UI_Compose) -> void` | Sets compose handler. **Side effect:** also calls `set_ui_element_as__using_ui_tile_span`. |

### Handler Queries (static inline)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `does_ui_element_have__dispose_handler` | `(UI_Element*) -> bool` | `bool` | Null-safe. True if handler non-null. |
| `does_ui_element_have__clicked_handler` | `(UI_Element*) -> bool` | `bool` | Null-safe. |
| `does_ui_element_have__dragged_handler` | `(UI_Element*) -> bool` | `bool` | Null-safe. |
| `does_ui_element_have__dropped_handler` | `(UI_Element*) -> bool` | `bool` | Null-safe. |
| `does_ui_element_have__receive_drop_handler` | `(UI_Element*) -> bool` | `bool` | Null-safe. |
| `does_ui_element_have__held_handler` | `(UI_Element*) -> bool` | `bool` | Null-safe. |
| `does_ui_element_have__typed_handler` | `(UI_Element*) -> bool` | `bool` | Null-safe. |
| `does_ui_element_have__transformed_handler` | `(UI_Element*) -> bool` | `bool` | Null-safe. |
| `does_ui_element_have__compose_handler` | `(UI_Element*) -> bool` | `bool` | True only if using tile span mode AND compose handler is non-null. |

### Handler Getters (static inline)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `get_ui_element__typed_handler` | `(UI_Element*) -> m_UI_Typed` | `m_UI_Typed` | Returns raw function pointer. |
| `get_ui_element__transformed_handler` | `(UI_Element*) -> m_UI_Transformed` | `m_UI_Transformed` | Returns raw function pointer. |
| `get_ui_element__compose_handler` | `(UI_Element*) -> m_UI_Compose` | `m_UI_Compose` | Returns raw function pointer. |
| `get_ui_element__p_ui_tile_span` | `(UI_Element*) -> const UI_Tile_Span*` | `const UI_Tile_Span*` | Returns pointer to embedded tile span. |

## Agentic Workflow

### Spatial Model

UI elements do NOT store position/size directly. Each element's UUID (from
`_serialization_header`) is used to look up a `Hitbox_AABB` from a
`Hitbox_AABB_Manager`. To access spatial data you need both the element and
a `Hitbox_AABB_Manager*`:

    Hitbox_AABB *p_hitbox = get_p_hitbox_aabb_of__ui_element(
        p_hitbox_aabb_manager, p_ui_element);

### Rendering Modes

An element renders in one of two mutually exclusive modes:
1. **Tile Span mode** (`is_ui_element__using_ui_tile_span`): The element's
   `ui_tile_span` is composed into the graphics window's tile map via
   `m_ui_compose_handler`.
2. **Sprite mode** (`is_ui_element__using_sprite`): A `Sprite` is rendered
   at the element's position.

### Tree Structure

- `p_parent` / `p_child`: Hierarchical ownership. Children are disposed when
  parents are disposed.
- `p_next`: Sibling linked list for iteration.
- Composition and transformation propagate through the tree.

### Preconditions

- All non-null-safe functions require non-null `p_ui_element`.
- `does_ui_element_have__parent/child/next` are null-safe.
- `iterate_to_*` functions are null-safe.

### Postconditions

- `set_ui_element__compose_handler` also sets tile span rendering mode.
- `set_ui_element_as__dropped` clears both held and dragged flags.
- `link_ui_element_to__this_ui_element` with self-link sets `p_next` to null.

### Error Handling

- Debug builds use `debug_abort` / `debug_error` for null pointer violations
  in non-null-safe functions.

## Header Guard

`UI_ELEMENT_H`
