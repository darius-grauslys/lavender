# 6 Specification: core/include/ui/ui_manager.h

## 6.1 Overview

Manages a pool of `UI_Element` instances for a single `Graphics_Window`.
Handles allocation, deallocation, input polling, composition, rendering,
and priority ordering of UI elements. Each `Graphics_Window` that displays
UI has an associated `UI_Manager`.

## 6.2 Dependencies

- `defines.h` (for `UI_Manager`, `UI_Element`, all core types)
- `defines_weak.h` (forward declarations)
- `ui/ui_element.h` (for `UI_Element` operations)

## 6.3 Types

### 6.3.1 UI_Manager (struct)

    typedef struct UI_Manager_t {
        Serialization_Header _serialization_header;
        UI_Element *pM_ui_element_pool;
        UI_Element **pM_ptr_array_of__ui_elements;
        Repeatable_Psuedo_Random randomizer;
        UI_Element *p_ui_element__focused;
        UI_Element **p_ptr_of__ui_element__latest_in_ptr_array;
        Quantity__u16 max_quantity_of__ui_elements;
        UI_Manager_Flags__u8 ui_manager_flags__u8;
    } UI_Manager;

| Field | Type | Description |
|-------|------|-------------|
| `_serialization_header` | `Serialization_Header` | UUID for pool management. |
| `pM_ui_element_pool` | `UI_Element*` | Heap-allocated array of `UI_Element` instances. |
| `pM_ptr_array_of__ui_elements` | `UI_Element**` | Heap-allocated pointer array for priority ordering. |
| `randomizer` | `Repeatable_Psuedo_Random` | UUID generator for elements. |
| `p_ui_element__focused` | `UI_Element*` | Currently focused element (receives typed events). |
| `p_ptr_of__ui_element__latest_in_ptr_array` | `UI_Element**` | Points past the last allocated entry. |
| `max_quantity_of__ui_elements` | `Quantity__u16` | Maximum elements this manager can hold. |
| `ui_manager_flags__u8` | `UI_Manager_Flags__u8` | Dirty flag for composition. |

### 6.3.2 UI_Manager_Flags__u8 (u8)

| Flag | Bit | Description |
|------|-----|-------------|
| `UI_MANAGER_FLAG__IS_DIRTY` | 0 | Signals that composition needs to be re-run. |

### 6.3.3 f_Foreach_UI_Element (function pointer)

    typedef void (*f_Foreach_UI_Element)(
            UI_Manager *p_ui_manager,
            Game *p_game,
            Graphics_Window *p_gfx_window,
            UI_Element *p_ui_element);

## 6.4 Functions

### 6.4.1 Initialization and Memory

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `initialize_ui_manager` | `(UI_Manager*) -> void` | `void` | Initializes to empty state. Does not allocate pool. |
| `allocate_ui_manager__members` | `(UI_Manager*, Quantity__u16 max) -> bool` | `bool` | Heap-allocates element pool and pointer array. Returns true on success. |
| `release_ui_manager__members` | `(UI_Manager*) -> void` | `void` | Frees element pool and pointer array. |

### 6.4.2 Queries

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `get_quantity_of__ui_elements_in__ui_manager` | `(UI_Manager*) -> Quantity__u16` | `Quantity__u16` | Returns count of allocated elements. |

### 6.4.3 Polling and Rendering

| Function | Signature | Description |
|----------|-----------|-------------|
| `poll_ui_manager__update` | `(UI_Manager*, Game*, Graphics_Window*) -> void` | Processes input against all elements. Invokes appropriate handlers. |
| `update_ui_manager_origin__relative_to` | `(Game*, UI_Manager*, Vector__3i32 old, Vector__3i32 new) -> void` | Updates all element positions when manager origin changes. |
| `render_all_ui_elements_in__ui_manager` | `(UI_Manager*, Game*, Graphics_Window*) -> void` | Renders all sprite-mode elements. |
| `compose_all_ui_elements_in__ui_manager` | `(UI_Manager*, Game*, Graphics_Window*) -> void` | Invokes compose handlers for all tile-span-mode elements. |
| `foreach_ui_element_in__ui_manager` | `(UI_Manager*, Game*, Graphics_Window*, f_Foreach_UI_Element) -> void` | Iterates over all allocated elements. |

### 6.4.4 Priority Management

| Function | Signature | Description |
|----------|-----------|-------------|
| `set_ui_element_priority_higher_than__this_ui_element_in__ui_manager` | `(UI_Manager*, UI_Element* higher, UI_Element* lower) -> void` | Reorders pointer array for priority. |
| `set_ui_element_as__the_parent_of__this_ui_element` | `(UI_Manager*, UI_Element* parent, UI_Element* child) -> void` | Establishes parent-child and adjusts priority. |
| `swap_ui_element__children` | `(UI_Manager*, UI_Element* parent_one, UI_Element* parent_two) -> void` | Swaps child pointers of two parents. |
| `swap_priority_of__ui_elenents_within__ui_manager` | `(UI_Manager*, UI_Element*, UI_Element*) -> void` | Swaps priority (pointer array position) of two elements. |

### 6.4.5 Allocation

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `allocate_ui_element_from__ui_manager` | `(UI_Manager*) -> UI_Element*` | `UI_Element*` | Allocates one element. Returns null if exhausted. |
| `allocate_ui_element_from__ui_manager_as__child` | `(Game*, Graphics_Window*, UI_Manager*, UI_Element* parent) -> UI_Element*` | `UI_Element*` | Allocates and establishes as child. |
| `allocate_many_ui_elements_from__ui_manager` | `(UI_Manager*, UI_Element**, Quantity__u16) -> void` | `void` | Allocates multiple elements into a pointer buffer. |
| `allocate_many_ui_elements_from__ui_manager_in__succession` | `(UI_Manager*, Quantity__u16) -> UI_Element*` | `UI_Element*` | Allocates elements linked via `p_next`. Returns head. |
| `allocate_many_ui_elements_from__ui_manager_as__recursive_children` | `(UI_Manager*, Quantity__u8) -> UI_Element*` | `UI_Element*` | Allocates in recursive parent-child chain. Returns root. |

### 6.4.6 Deallocation

| Function | Signature | Description |
|----------|-----------|-------------|
| `release__ui_element_from__ui_manager` | `(Game*, Graphics_Window*, UI_Manager*, UI_Element*) -> void` | Disposes and deallocates one element. |
| `release_all__ui_elements_from__ui_manager` | `(Game*, Graphics_Window*, UI_Manager*) -> void` | Disposes and deallocates all elements. |

### 6.4.7 Lookup

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `get_p_ui_element_by__uuid_from__ui_manager` | `(UI_Manager*, Identifier__u32) -> UI_Element*` | `UI_Element*` | Finds element by UUID. Returns null if not found. |

### 6.4.8 Inline Functions (static inline)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `is_ui_manager__empty` | `(UI_Manager*) -> bool` | `bool` | True if no elements allocated. Checks `pM_ptr_array_of__ui_elements[0]`. |
| `get_p_ui_element_by__index_from__ui_manager` | `(UI_Manager*, Index__u16) -> UI_Element*` | `UI_Element*` | Index access. **WARNING:** positions may change due to priority reordering. Use UUIDs for stable references. Debug aborts if index >= `MAX_QUANTITY_OF__UI_ELEMENTS`. |
| `allocate_ui_element_from__ui_manager_in__succession` | `(UI_Manager*, UI_Element* predecessor) -> UI_Element*` | `UI_Element*` | Allocates and links as `predecessor->p_next`. |
| `is_ui_manager__dirty` | `(UI_Manager*) -> bool` | `bool` | True if dirty flag set. |
| `set_ui_manager_as__dirty` | `(UI_Manager*) -> void` | `void` | Sets dirty flag. |
| `set_ui_manager_as__NOT_dirty` | `(UI_Manager*) -> void` | `void` | Clears dirty flag. |

## 6.5 Agentic Workflow

### 6.5.1 Ownership

Owned by `UI_Context` (pooled in `ui_managers[]`). Associated with a
`Graphics_Window` via `uuid_of__ui_manager`. Contains and manages
`UI_Element` instances.

### 6.5.2 Preconditions

- `get_p_ui_element_by__index_from__ui_manager`: debug builds abort if index exceeds `MAX_QUANTITY_OF__UI_ELEMENTS`.
- All functions require non-null `p_ui_manager`.

### 6.5.3 Error Handling

- `get_p_ui_element_by__index_from__ui_manager` calls `debug_abort` on out-of-bounds in debug builds.

## 6.6 Header Guard

`UI_MANAGER_H`
