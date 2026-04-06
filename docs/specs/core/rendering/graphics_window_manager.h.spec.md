# 1. Specification: core/include/rendering/graphics_window_manager.h

## 1.1 Overview

Manages a fixed-size pool of `Graphics_Window` instances. Provides
allocation, deallocation, lookup, parent-child relationships, sorting by
priority, and batch composition/rendering of all windows.

## 1.2 Dependencies

- `defines.h` (for `Graphics_Window_Manager`, `Graphics_Window`, `Gfx_Context`)
- `defines_weak.h` (forward declarations)
- `serialization/hashing.h` (for UUID hashing and `get_next_available__random_uuid_in__contiguous_array`)
- `serialization/identifiers.h` (for `is_identifier_u32__invalid`)

## 1.3 Types

### 1.3.1 Graphics_Window_Manager (struct)

    typedef struct Graphics_Window_Manager_t {
        Graphics_Window graphics_windows[MAX_QUANTITY_OF__GRAPHICS_WINDOWS];
        Graphics_Window *ptr_array_of__sorted_graphic_windows[
            MAX_QUANTITY_OF__GRAPHICS_WINDOWS];
        Repeatable_Psuedo_Random randomizer;
    } Graphics_Window_Manager;

| Field | Type | Description |
|-------|------|-------------|
| `graphics_windows` | `Graphics_Window[8]` | Fixed pool of window instances. |
| `ptr_array_of__sorted_graphic_windows` | `Graphics_Window*[8]` | Pointer array sorted by priority. |
| `randomizer` | `Repeatable_Psuedo_Random` | UUID generator for windows. |

### 1.3.2 Constants

| Macro | Value | Description |
|-------|-------|-------------|
| `MAX_QUANTITY_OF__GRAPHICS_WINDOWS` | `8` | Maximum concurrent graphics windows. |

## 1.4 Functions

### 1.4.1 Initialization

| Function | Signature | Description |
|----------|-----------|-------------|
| `initialize_graphics_window_manager` | `(Graphics_Window_Manager*) -> void` | Initializes all windows as deallocated. |

### 1.4.2 Allocation

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `allocate_graphics_window_with__uuid_from__graphics_window_manager` | `(Gfx_Context*, Graphics_Window_Manager*, Identifier__u32, Texture_Flags) -> Graphics_Window*` | `Graphics_Window*` | Allocates a window with a specific UUID. Calls `PLATFORM_allocate_gfx_window`. Returns null on failure. |
| `allocate_graphics_window_from__graphics_window_manager` | `(Gfx_Context*, Graphics_Window_Manager*, Texture_Flags) -> Graphics_Window*` | `Graphics_Window*` | Convenience wrapper that auto-generates a UUID. (static inline) |

### 1.4.3 Parent-Child

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `set_graphics_window_as__parent_to__this_graphics_window` | `(Graphics_Window_Manager*, Graphics_Window* parent, Graphics_Window* child) -> void` | `void` | Establishes parent-child relationship. |
| `is_graphics_window_a__descendant_of__this_graphics_window` | `(Graphics_Window_Manager*, Graphics_Window* child, Graphics_Window* ancestor) -> bool` | `bool` | True if child is a descendant of ancestor. |
| `is_graphics_window_a__parent` | `(Graphics_Window_Manager*, Graphics_Window*) -> bool` | `bool` | True if the window has children. (static inline) |
| `is_graphics_window_with__parent` | `(Graphics_Window*) -> bool` | `bool` | True if the window has a parent UUID. (static inline) |
| `get_graphics_window__p_parent` | `(Graphics_Window_Manager*, Graphics_Window*) -> Graphics_Window*` | `Graphics_Window*` | Returns parent window. |
| `get_graphics_window__p_root_parent` | `(Graphics_Window_Manager*, Graphics_Window*, Quantity__u32*) -> Graphics_Window*` | `Graphics_Window*` | Returns root ancestor. Out-param receives depth. |

### 1.4.4 Release and Reset

| Function | Signature | Description |
|----------|-----------|-------------|
| `release_graphics_window_from__graphics_window_manager` | `(Game*, Graphics_Window*) -> void` | Releases a window. |
| `reset_platform_provided_graphics_windows` | `(Game*, bool) -> void` | Resets all platform-provided windows. Used during scene transitions. |
| `reset_children_of__graphics_window_from__graphics_window_manager` | `(Game*, Graphics_Window_Manager*, Graphics_Window*, bool) -> void` | Resets children of a window. |

### 1.4.5 Lookup

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `get_p_graphics_window_by__uuid_from__graphics_window_manager` | `(Graphics_Window_Manager*, Identifier__u32) -> Graphics_Window*` | `Graphics_Window*` | Finds a window by UUID. |
| `get_graphics_windows_from__graphics_window_manager` | `(Graphics_Window_Manager*, Graphics_Window**, Quantity__u8, Graphics_Window_Kind) -> Quantity__u8` | `Quantity__u8` | Fills buffer with windows of the given kind. Returns count found. |
| `get_p_graphics_window_by__index_in_ptr_array_from__manager` | `(Graphics_Window_Manager*, Index__u32) -> Graphics_Window*` | `Graphics_Window*` | Direct index access into sorted pointer array. (static inline) |
| `get_index_in_ptr_array_of__gfx_window_and__quantity_of__descendants` | `(Graphics_Window_Manager*, Graphics_Window*, Quantity__u32*) -> Quantity__u32` | `Quantity__u32` | Returns index in pointer array. Out-param receives descendant count. |

### 1.4.6 Platform-Provided Windows

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `allocate_or_get__platform_provided_graphics_windows` | `(Gfx_Context*, Graphics_Window_Manager*, Graphics_Window**, Quantity__u32, Quantity__u32*, Index__u32) -> bool` | `bool` | Allocates or retrieves platform-provided windows. Returns `false` only on allocation failure. |
| `setup_platform_provided_graphics_windows` | `(Gfx_Context*) -> bool` | `bool` | Sets up all platform-provided windows. |
| `itterate_platform_graphics_windows` | `(Gfx_Context*, Index__u32*) -> Graphics_Window*` | `Graphics_Window*` | Auto-incrementing iterator over platform-provided windows. |
| `get_default_platform_graphics_window` | `(Gfx_Context*) -> Graphics_Window*` | `Graphics_Window*` | Returns the first platform-provided window. |

### 1.4.7 Composition and Rendering

| Function | Signature | Description |
|----------|-----------|-------------|
| `compose_graphic_windows_in__graphics_window_manager` | `(Game*) -> void` | Composes all windows in priority order. |
| `render_graphic_windows_in__graphics_window_manager` | `(Game*) -> void` | Renders all windows in priority order. |
| `sort_graphic_windows_in__graphic_window_manager` | `(Graphics_Window_Manager*) -> void` | Sorts windows by priority. |

## 1.5 Agentic Workflow

### 1.5.1 Ownership

Owned by `Gfx_Context` (at `gfx_context.graphics_window_manager`). Accessed
via `get_p_graphics_window_manager_from__gfx_context`.

### 1.5.2 Preconditions

- All functions require non-null pointers.

## 1.6 Header Guard

`GRAPHICS_WINDOW_MANAGER_H`
