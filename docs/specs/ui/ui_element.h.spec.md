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
| `UI_FLAGS__BIT_IS_SNAPPED_X_OR_Y_AXIS` | 5 | Slider axis: 1=X, 0