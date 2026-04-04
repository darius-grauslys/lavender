# Specification: core/include/ui/ui_context.h

## Overview

Manages the collection of `UI_Manager` instances and the registry of
`UI_Window_Record` entries. Provides the high-level API for opening and
closing UI windows, which involves allocating graphics windows, UI managers,
and populating them with UI elements via registered load callbacks.

## Dependencies

- `defines.h` (for `UI_Context`, `UI_Manager`, `Graphics_Window`, all core types)
- `defines_weak.h` (forward declarations)
- `types/implemented/graphics_window_kind.h` (for `Graphics_Window_Kind` enum)

## Types

### UI_Context (struct)

    typedef struct UI_Context_t {
        UI_Manager ui_managers[MAX_QUANTITY_OF__UI_MANAGERS];
        UI_Window_Record ui_window_record[Graphics_Window_Kind__Unknown];
    } UI_Context;

| Field | Type | Description |
|-------|------|-------------|
| `ui_managers` | `UI_Manager[MAX_QUANTITY_OF__UI_MANAGERS]` | Pool of UI manager instances. |
| `ui_window_record` | `UI_Window_Record[Graphics_Window_Kind__Unknown]` | Registry indexed by `Graphics_Window_Kind`. |

### Limits

| Macro | Default | Description |
|-------|---------|-------------|
| `MAX_QUANTITY_OF__UI_MANAGERS` | `8` | Maximum concurrent UI managers. |

## Functions

### Initialization

| Function | Signature | Description |
|----------|-----------|-------------|
| `initialize_ui_context` | `(UI_Context*) -> void` | Initializes all UI managers and clears all window records. |

### Manager Allocation

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `allocate_p_ui_manager_from__ui_context` | `(UI_Context*, Identifier__u32, Quantity__u16 max_elements) -> UI_Manager*` | `UI_Manager*` | Allocates a UI manager from the pool. Returns null if exhausted. |
| `get_p_ui_manager_by__uuid_from__ui_context` | `(UI_Context*, Identifier__u32) -> UI_Manager*` | `UI_Manager*` | Finds a UI manager by UUID. |
| `release_p_ui_manager_from__ui_context` | `(Game*, Identifier__u32) -> void` | `void` | Releases a UI manager. |

### Window Registration

| Function | Signature | Description |
|----------|-----------|-------------|
| `register_ui_window_into__ui_context` | `(UI_Context*, f_UI_Window__Load, f_UI_Window__Close, Graphics_Window_Kind, Signed_Quantity__i32 sprites, Signed_Quantity__i16 elements) -> void` | Registers a window type with load/close callbacks and resource requirements. |

### Window Lifecycle

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `open_ui_window_with__this_uuid_and__parent_uuid` | `(Game*, Graphics_Window_Kind, Identifier__u32 uuid, Identifier__u32 parent_uuid) -> Graphics_Window*` | `Graphics_Window*` | Opens a UI window: allocates graphics window, UI manager, sprite manager (if needed), invokes load callback. Returns null on failure. |
| `populate_window_with__ui` | `(Game*, Graphics_Window*, Graphics_Window_Kind, Index__u16 offset) -> bool` | `bool` | Populates an existing window with UI elements via registered load callback. |
| `close_ui_window` | `(Game*, Identifier__u32) -> void` | `void` | Closes a UI window. Only closes if the resolved `Graphics_Window` has a non-null `UI_Manager` pointer. Invokes registered close callback. |

### Convenience (static inline)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `open_ui_window_with__this_uuid` | `(Game*, Graphics_Window_Kind, Identifier__u32) -> Graphics_Window*` | `Graphics_Window*` | Opens with no parent (`IDENTIFIER__UNKNOWN__u32`). |
| `open_ui_window` | `(Game*, Graphics_Window_Kind) -> Graphics_Window*` | `Graphics_Window*` | Opens with no parent and auto-generated UUID (`IDENTIFIER__UNKNOWN__u32`). |

## Agentic Workflow

### Window Lifecycle

    [Register] register_ui_window_into__ui_context (once at init)
        ↓
    [Open] open_ui_window → allocates Graphics_Window, UI_Manager,
           optional Sprite_Manager, calls f_UI_Window__Load
        ↓
    [Update] poll_ui_manager__update (each frame)
        ↓
    [Close] close_ui_window → calls f_UI_Window__Close, releases all resources

### Ownership

Owned by `Gfx_Context` (at `gfx_context.ui_context`). Contains `UI_Manager`
pool and `UI_Window_Record` registry. `register_ui_windows` (from
`implemented/ui_window_registrar.h`) populates the registry.

### Preconditions

- All functions require non-null pointers.
- `register_ui_window_into__ui_context`: `the_kind_of__window` must be less than `Graphics_Window_Kind__Unknown`.

## Header Guard

`UI_CONTEXT_H`
