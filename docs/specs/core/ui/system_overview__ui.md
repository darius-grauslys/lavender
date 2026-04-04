# System Overview: UI Subsystem

## Purpose

The UI subsystem provides a complete framework for building, composing,
rendering, and interacting with user interface elements. It manages pools of
UI elements, organizes them into windows backed by tile maps, handles input
events (click, drag, drop, hold, type), and supports both tile-based and
sprite-based rendering modes. The system is designed to be platform-agnostic
at the core level, with platform-specific rendering delegated through
function pointers.

## Architecture

### Data Hierarchy

    Game
    +-- Gfx_Context
    |   +-- UI_Context
    |   |   +-- UI_Manager[0..MAX_QUANTITY_OF__UI_MANAGERS-1]  (manager pool)
    |   |   |   +-- Serialization_Header  (UUID for lookup)
    |   |   |   +-- UI_Element *pM_ui_element_pool  (heap-allocated)
    |   |   |   |   +-- UI_Element[0..max_quantity_of__ui_elements-1]
    |   |   |   |       +-- Serialization_Header  (UUID for hitbox lookup)
    |   |   |   |       +-- Handler function pointers (9 event handlers)
    |   |   |   |       +-- Tree pointers: p_parent, p_child, p_next
    |   |   |   |       +-- UI_Tile_Span  (9-slice tile pattern)
    |   |   |   |       +-- UI_Flags__u16  (runtime state)
    |   |   |   |       +-- UI_Element_Data  (game-defined custom data)
    |   |   |   |       +-- UI_Element_Kind  (discriminator)
    |   |   |   |       +-- Union:
    |   |   |   |           +-- Button: UI_Button_Flags__u8
    |   |   |   |           +-- Slider: spanning_length, distance
    |   |   |   |           +-- Text/Text_Box: Typer, char buffer, cursor
    |   |   |   |           +-- Window: Graphics_Window*
    |   |   |   |
    |   |   |   +-- UI_Element **pM_ptr_array_of__ui_elements  (priority order)
    |   |   |   +-- UI_Element *p_ui_element__focused
    |   |   |   +-- Repeatable_Psuedo_Random randomizer  (UUID generation)
    |   |   |
    |   |   +-- UI_Window_Record[0..Graphics_Window_Kind__Unknown-1]  (registry)
    |   |       +-- f_UI_Window__Load   (load callback)
    |   |       +-- f_UI_Window__Close  (close callback)
    |   |       +-- signed_quantity_of__sprites
    |   |       +-- signed_quantity_of__ui_elements
    |   |
    |   +-- UI_Tile_Map_Manager
    |   |   +-- UI_Tile_Map__Small[0..UI_TILE_MAP__SMALL__MAX_QUANTITY_OF-1]
    |   |   +-- UI_Tile_Map__Medium[0..UI_TILE_MAP__MEDIUM__MAX_QUANTITY_OF-1]
    |   |   +-- UI_Tile_Map__Large[0..UI_TILE_MAP__LARGE__MAX_QUANTITY_OF-1]
    |   |
    |   +-- Graphics_Window_Manager
    |   |   +-- Graphics_Window[...]
    |   |       +-- UI_Tile_Map__Wrapper  (backing tile data)
    |   |       +-- origin, position, size
    |   |       +-- f_PLATFORM_compose_gfx_window
    |   |
    |   +-- Sprite_Context
    |   +-- Font_Manager
    |   +-- PLATFORM_Gfx_Context*
    |
    +-- Hitbox_Context
        +-- Hitbox_AABB_Manager
            +-- Hitbox_AABB[...]  (spatial data for UI elements, by UUID)

### Key Types

| Type | Role |
|------|------|
| `UI_Context` | Top-level UI owner. Lives in `Gfx_Context`. Holds the UI manager pool and window record registry. |
| `UI_Window_Record` | Registration entry for a window type. Associates a `Graphics_Window_Kind` with load/close callbacks and resource requirements. |
| `UI_Manager` | Manages a pool of `UI_Element` instances for a single `Graphics_Window`. Handles allocation, input polling, composition, and priority ordering. |
| `UI_Element` | Polymorphic UI node. Can act as button, slider, draggable, drop zone, text, text box, window element, or container. Identified by UUID. |
| `UI_Tile_Map_Manager` | Pools tile maps in three size categories (Small, Medium, Large). Provides allocation/deallocation. |
| `UI_Tile_Map__Wrapper` | Size-agnostic handle to a tile map's raw data, width, height, and size category. |
| `UI_Tile_Span` | 9-slice tile pattern (4 corners, 4 edges, 1 fill) for composing scalable UI panels. |
| `UI_Tile` | Atomic visual unit: 10-bit tile index + 6-bit flags (flip, scale). |
| `Graphics_Window` | A renderable window surface. Contains a `UI_Tile_Map__Wrapper` for tile-based UI backing. |
| `Hitbox_AABB` | Axis-aligned bounding box storing position and size. UI elements reference these by UUID for spatial data. |

### Limits

| Macro | Default | Description |
|-------|---------|-------------|
| `MAX_QUANTITY_OF__UI_MANAGERS` | `8` | Maximum concurrent UI managers (and thus concurrent UI windows). |
| `UI_TILE_MAP__SMALL__MAX_QUANTITY_OF` | `32` | Pool size for small tile maps. |
| `UI_TILE_MAP__SMALL__WIDTH` | `8` | Width of small tile maps in tiles. |
| `UI_TILE_MAP__SMALL__HEIGHT` | `8` | Height of small tile maps in tiles. |
| `UI_TILE_MAP__MEDIUM__MAX_QUANTITY_OF` | `16` | Pool size for medium tile maps. |
| `UI_TILE_MAP__MEDIUM__WIDTH` | `16` | Width of medium tile maps in tiles. |
| `UI_TILE_MAP__MEDIUM__HEIGHT` | `16` | Height of medium tile maps in tiles. |
| `UI_TILE_MAP__LARGE__MAX_QUANTITY_OF` | `8` | Pool size for large tile maps. |
| `UI_TILE_MAP__LARGE__WIDTH` | `32` | Width of large tile maps in tiles. |
| `UI_TILE_MAP__LARGE__HEIGHT` | `32` | Height of large tile maps in tiles. |
| `UI_CONTAINER_PTR_ENTRIES_MAXIMUM_QUANTITY_OF` | `8` | Maximum children in a container element. |

## Element Kind Specializations

`UI_Element` is a polymorphic type discriminated by `UI_Element_Kind`. Each
kind activates a different union member and installs different default
handlers:

| Kind | Union Data | Key Handlers | Description |
|------|-----------|--------------|-------------|
| **Button** | `UI_Button_Flags__u8` | clicked, held | Clickable element with optional toggle state. |
| **Draggable** | *(empty)* | dragged, dropped | Element that follows the cursor when held. |
| **Drop_Zone** | *(empty)* | receive_drop | Region that accepts dropped draggable elements. |
| **Slider** | `spanning_length`, `distance` | dragged, transformed, dispose | Constrained draggable along one axis. Produces percentage values. |
| **Text** | `Typer`, `char*`, size, cursor | compose, transformed, dispose | Read-only text display using font rendering. |
| **Text_Box** | `Typer`, `char*`, size, cursor | compose, clicked, typed, transformed, dispose | Editable text input. Extends Text with focus and typed input. |
| **Window** | `Graphics_Window*` | *(via child window)* | Element that owns and manages a child `Graphics_Window`. |
| **Container** | *(external `UI_Container_Entries`)* | *(none specific)* | Logical grouping of up to 8 child elements in a flat array. |

## Rendering Model

### Two Rendering Modes

Each `UI_Element` renders in exactly one of two mutually exclusive modes,
controlled by `UI_FLAGS__BIT_IS_USING__SPRITE_OR_UI_TILE_SPAN`:

1. **Tile Span Mode** (flag cleared): The element's `UI_Tile_Span` is
   composed into the parent `Graphics_Window`'s `UI_Tile_Map__Wrapper` via
   the element's `m_ui_compose_handler`. The platform's
   `f_PLATFORM_compose_gfx_window` then reads the tile map to produce
   visible output.

2. **Sprite Mode** (flag set): A `Sprite` is rendered at the element's
   position. The sprite is managed through the `Sprite_Context`.

### Tile Composition Pipeline

    UI_Tile_Span (9-slice pattern)
        |
        v
    generate_ui_span_in__ui_tile_map()
        |
        v
    UI_Tile_Map__Wrapper (raw tile data array)
        |
        v
    f_PLATFORM_compose_gfx_window() (platform reads tile map)
        |
        v
    Visible UI output

### Composition Flow

    compose_all_ui_elements_in__ui_manager()
        |
        +-- For each allocated UI_Element (in priority order):
            |
            +-- If tile span mode AND has compose handler:
                |
                +-- Invoke m_ui_compose_handler(element, game, gfx_window)
                    |
                    +-- Default: compose this element's tile span,
                    |   then recursively compose children.
                    |
                    +-- Variants:
                        +-- default_non_recursive: this element only
                        +-- default_only_recursive: children only

### Rendering Flow (Sprite Mode)

    render_all_ui_elements_in__ui_manager()
        |
        +-- For each allocated UI_Element (in priority order):
            |
            +-- If sprite mode AND has valid sprite:
                |
                +-- Render sprite at element's hitbox position

## Spatial Model

UI elements do **not** store position or size directly. Each element's UUID
(from `_serialization_header`) is used to look up a `Hitbox_AABB` from a
`Hitbox_AABB_Manager`:

    Hitbox_AABB *p_hitbox = get_p_hitbox_aabb_of__ui_element(
        p_hitbox_aabb_manager, p_ui_element);

This indirection allows the collision/hitbox system to manage spatial data
uniformly for both game entities and UI elements.

### Position and Size Operations

| Operation | Function |
|-----------|----------|
| Allocate hitbox | `allocate_hitbox_for__ui_element(game, gfx_window, element, width, height, position)` |
| Set position | `set_position_3i32_of__ui_element(game, gfx_window, element, position)` |
| Set size | `set_ui_element__size(game, gfx_window, element, width, height)` |
| Set both | `set_ui_element__hitbox(game, gfx_window, element, width, height, position)` |
| Grid layout | `set_positions_of__ui_elements_in__succession(game, gfx_window, element, start, x_stride, per_row, y_stride)` |
| Query position | `get_position_3i32_from__p_ui_element(hitbox_mgr, element)` |
| Query size | `get_width_from__p_ui_element(hitbox_mgr, element)` / `get_height_from__p_ui_element(...)` |

### Transform Propagation

When an element's position changes, its `m_ui_transformed_handler` is
invoked. For tree structures, transforms propagate recursively:

    update_ui_element_origin__relative_to__recursively(
        game, ui_manager, element, old_origin, new_origin);

This updates the element and all its children when a parent origin changes.

## Tree Structure

UI elements form a tree via three pointers:

    p_parent  -- hierarchical ownership (upward)
    p_child   -- first child (downward)
    p_next    -- sibling linked list (lateral)

    [Parent]
       |
       p_child
       |
       v
    [Child_A] --p_next--> [Child_B] --p_next--> [Child_C] --p_next--> NULL
       |
       p_child
       |
       v
    [Grandchild_A1] --p_next--> [Grandchild_A2] --p_next--> NULL

### Tree Semantics

- **Composition** propagates downward: composing a parent composes its
  children (via `m_ui_element__compose_handler__default`).
- **Transformation** propagates downward: moving a parent updates children
  (via `update_ui_element_origin__relative_to__recursively`).
- **Disposal** propagates downward: disposing a parent disposes its children.
- **Priority** is managed separately via the pointer array in `UI_Manager`,
  independent of tree structure.

## Lifecycle

### 1. System Initialization

    initialize_ui_context(&gfx_context.ui_context);
        -> All UI_Manager slots initialized to empty.
        -> All UI_Window_Record slots cleared.

    initialize_ui_tile_map_manager(&gfx_context.ui_tile_map_manager);
        -> All tile map pools (Small, Medium, Large) marked as deallocated.

### 2. Window Registration (Once at Startup)

    register_ui_windows(&gfx_context);
        -> For each game-defined window type:
            register_ui_window_into__ui_context(
                &ui_context,
                f_load_callback,
                f_close_callback,
                Graphics_Window_Kind__My_Window,
                sprite_count,
                element_count);

The `register_ui_windows` function is game-specific and implemented in the
game project's `implemented/` directory.

### 3. Window Opening

    Graphics_Window *p_gfx_window =
        open_ui_window(p_game, Graphics_Window_Kind__My_Window);

This performs the following steps:

    a. Look up UI_Window_Record for the given Graphics_Window_Kind.
    b. Allocate a Graphics_Window from the Graphics_Window_Manager.
    c. Allocate a UI_Tile_Map__Wrapper from the UI_Tile_Map_Manager.
    d. Allocate a UI_Manager from the UI_Context pool.
       -> Heap-allocate element pool and pointer array.
    e. If sprite_count > 0, allocate a sprite pool.
       If sprite_count < 0, use parent window's sprite pool.
    f. Invoke f_UI_Window__Load callback:
       -> Allocate UI_Element instances from the UI_Manager.
       -> Initialize elements as buttons, sliders, text, etc.
       -> Allocate hitboxes for each element.
       -> Set positions and sizes.
       -> Set up event handlers.
       -> Compose initial tile map content.

### 4. Per-Frame Update

    poll_ui_manager__update(p_ui_manager, p_game, p_gfx_window);
        -> Process input against all elements (in priority order):
            -> Hit test cursor position against element hitboxes.
            -> If cursor presses on element:
                -> Set IS_BEING_HELD flag.
                -> Invoke m_ui_held_handler.
            -> If cursor moves while holding:
                -> Set IS_BEING_DRAGGED flag.
                -> Invoke m_ui_dragged_handler.
            -> If cursor releases:
                -> Clear held/dragged flags.
                -> Invoke m_ui_dropped_handler.
                -> If over a Drop_Zone, invoke m_ui_receive_drop_handler.
            -> If element is focused and key pressed:
                -> Invoke m_ui_typed_handler.
            -> If element is clicked:
                -> Invoke m_ui_clicked_handler.

### 5. Composition (When Dirty)

    if (is_ui_manager__dirty(p_ui_manager)) {
        compose_all_ui_elements_in__ui_manager(
            p_ui_manager, p_game, p_gfx_window);
        set_ui_manager_as__NOT_dirty(p_ui_manager);
    }

    -> For each tile-span-mode element with a compose handler:
        -> Invoke m_ui_compose_handler.
        -> Default handler: write 9-slice tile span into tile map,
           then recursively compose children.

### 6. Rendering (Each Frame)

    render_all_ui_elements_in__ui_manager(
        p_ui_manager, p_game, p_gfx_window);

    -> For each sprite-mode element:
        -> Render sprite at element's hitbox position.

    f_PLATFORM_compose_gfx_window(p_gfx_window);
    -> Platform reads UI_Tile_Map__Wrapper to produce visible tile output.

### 7. Window Closing

    close_ui_window(p_game, uuid_of__gfx_window);

    -> Resolve Graphics_Window by UUID.
    -> If window has a UI_Manager:
        -> Invoke f_UI_Window__Close callback (default: f_ui_window__close__default).
            -> release_all__ui_elements_from__ui_manager:
                -> For each allocated element:
                    -> Invoke m_ui_dispose_handler (frees owned resources).
                    -> Release hitbox.
                    -> Release sprite (if any).
                    -> Deallocate element from pool.
            -> release_ui_manager__members (free heap arrays).
        -> Release UI_Manager back to UI_Context pool.
    -> Release tile map back to UI_Tile_Map_Manager.
    -> Release Graphics_Window.

## Input Event Flow

### Event Handler Dispatch

    Input Event
        |
        v
    poll_ui_manager__update()
        |
        +-- Hit test: cursor position vs. element hitboxes
        |   (iterates priority-ordered pointer array, highest first)
        |
        +-- Determine event type:
            |
            +-- Click --> m_ui_clicked_handler
            |   +-- Button: toggle state, invoke custom handler
            |   +-- Text_Box: set focus to this element
            |
            +-- Hold --> m_ui_held_handler
            |   +-- Button: default held behavior
            |
            +-- Drag --> m_ui_dragged_handler
            |   +-- Draggable: move element to cursor position
            |   +-- Slider: constrain movement along axis, update distance
            |
            +-- Drop --> m_ui_dropped_handler
            |   +-- Draggable: finalize position
            |   +-- If over Drop_Zone --> m_ui_receive_drop_handler
            |
            +-- Type --> m_ui_typed_handler
                +-- Text_Box: append/insert character (with optional filter)

### Focus Model

Only one element per `UI_Manager` can be focused at a time
(`p_ui_element__focused`). Focus is set when a text box is clicked. The
focused element receives typed events.

## Priority System

The `UI_Manager` maintains a pointer array (`pM_ptr_array_of__ui_elements`)
that determines the order in which elements are polled for input and
composed. Higher-priority elements are checked first during hit testing,
meaning they receive input events before lower-priority elements at the
same position.

| Operation | Function |
|-----------|----------|
| Raise priority | `set_ui_element_priority_higher_than__this_ui_element_in__ui_manager` |
| Set parent-child (adjusts priority) | `set_ui_element_as__the_parent_of__this_ui_element` |
| Swap priority | `swap_priority_of__ui_elenents_within__ui_manager` |
| Swap children | `swap_ui_element__children` |

**Warning:** Element indices in the pointer array may change due to priority
reordering. Use UUIDs for stable element references.

## Dirty Flag Mechanism

The `UI_Manager` has a dirty flag (`UI_MANAGER_FLAG__IS_DIRTY`) that signals
when tile-based composition needs to be re-run. Operations that modify
visual state (text changes, element additions/removals) set this flag.
The game loop checks the flag and re-composes only when necessary:

    Text mutation functions (set_c_str_of__ui_text_*, append_*, insert_*, etc.)
        -> set_ui_manager_as__dirty()

    Game loop:
        if (is_ui_manager__dirty(p_ui_manager)):
            compose_all_ui_elements_in__ui_manager(...)
            set_ui_manager_as__NOT_dirty(p_ui_manager)

## Tile Map Subsystem

### Tile Map Pooling

Tile maps come in three fixed-size categories, pooled by the
`UI_Tile_Map_Manager`:

| Category | Default Dimensions | Default Pool Size |
|----------|--------------------|-------------------|
| Small | 8 × 8 tiles | 32 |
| Medium | 16 × 16 tiles | 16 |
| Large | 32 × 32 tiles | 8 |

Allocation returns a `UI_Tile_Map__Wrapper` that provides size-agnostic
access to the underlying tile data.

### 9-Slice Composition

`UI_Tile_Span` defines a 9-slice pattern. When written into a tile map
region via `generate_ui_span_in__ui_tile_map`, the pattern is expanded:

    +--+--------+--+
    |TL| Top    |TR|   TL, TR, BL, BR = corner tiles
    +--+--------+--+
    |  |        |  |   Top, Right, Bottom, Left = edge tiles (repeated)
    |L | Fill   | R|
    |  |        |  |   Fill = interior tile (repeated)
    +--+--------+--+
    |BL| Bottom |BR|
    +--+--------+--+

### Tile Data

Each `UI_Tile` is a 16-bit value:
- Bits [0..9]: `UI_Tile_Kind` — index into a tileset.
- Bits [10..15]: `UI_Tile_Flags` — flip horizontal/vertical, scale
  horizontal/vertical, two general-purpose flags.

Tiles are stored as `UI_Tile_Raw` (u16) in the tile map arrays.

## Slider Mechanics

Sliders are constrained draggables that move along a single axis:

    +-- Slider Span (spanning_length) --+
    |                                    |
    [====|=============================]
          ^
          slider__distance__u32

- Axis is determined by `UI_FLAGS__BIT_IS_SNAPPED_X_OR_Y_AXIS`:
  1 = X axis, 0 = Y axis.
- `slider__distance__u32` tracks current position along the span.
- `get_percentage_i32F20_from__ui_slider` returns position as a fixed-point
  fraction of the total span.
- `get_offset_from__ui_slider_percentage` maps the percentage to an
  arbitrary range.
- The `m_ui_slider__dragged_handler__gfx_window__default` variant scrolls
  the associated `Graphics_Window` based on slider position.

## Window Element Nesting

A `UI_Element` of kind `Window` owns a child `Graphics_Window`. This enables
nested UI windows:

    [Parent Graphics_Window]
        |
        +-- UI_Manager
            |
            +-- UI_Element (Kind: Window)
                |
                +-- p_ui_window__graphics_window
                    |
                    +-- [Child Graphics_Window]
                        |
                        +-- UI_Manager (child)
                            |
                            +-- UI_Element (Button, Text, etc.)

The child window's lifetime is tied to the parent `UI_Element`'s lifetime.
Opening is done via `initialize_ui_element_as__window_element_and__open_window`,
which calls `open_ui_window_with__this_uuid_and__parent_uuid`.

## Text Input Pipeline

### Text Element (Read-Only)

    initialize_ui_element_as__text_with__const_c_str(element, font, "Hello", 5);
        -> Sets kind to Text.
        -> Installs compose, transformed, dispose handlers.
        -> Borrows the const string (does NOT own it).

    Composition:
        m_ui_element__compose_handler__text
            -> Uses Typer to lay out glyphs into the tile map.

### Text Box (Editable)

    initialize_ui_element_as__text_box_with__buffer_size(element, font, 128);
        -> Sets kind to Text_Box.
        -> Allocates internal buffer of 128 bytes.
        -> Installs compose, clicked, typed, transformed, dispose handlers.

    Click -> m_ui_element__clicked_handler__text_box
        -> Sets focus to this element.

    Type -> m_ui_element__typed_handler__text_box (or numeric/alphanumeric variant)
        -> Appends character to buffer.
        -> Marks UI_Manager as dirty.

    Composition:
        m_ui_element__compose_handler__text_box
            -> Uses Typer to lay out current buffer contents.

### Input Filters

| Handler | Accepts |
|---------|---------|
| `m_ui_element__typed_handler__text_box` | All printable characters. |
| `m_ui_element__typed_handler__text_box__numeric` | Numeric characters only. |
| `m_ui_element__typed_handler__text_box__alphanumeric` | Alphanumeric characters only. |

## Relationship to External Systems

| Concern | Managed By |
|---------|------------|
| UI element allocation and pooling | `UI_Context` → `UI_Manager` |
| Spatial data (position, size) for UI elements | `Hitbox_Context` → `Hitbox_AABB_Manager` |
| Tile map storage pooling | `UI_Tile_Map_Manager` |
| Graphics window allocation | `Graphics_Window_Manager` (in `Gfx_Context`) |
| Sprite allocation for sprite-mode elements | `Sprite_Context` (in `Gfx_Context`) |
| Font resources for text rendering | `Font_Manager` (in `Gfx_Context`) |
| Platform-specific tile map rendering | `f_PLATFORM_compose_gfx_window` |
| Platform-specific sprite rendering | Platform render functions |
| Window type registration | Game project's `register_ui_windows` implementation |

The `UI_Element._serialization_header` UUID is the bridge between the UI
system and the hitbox system: it references a `Hitbox_AABB` by UUID, which
is resolved through the `Hitbox_AABB_Manager` for all spatial queries.

## Capacity Constraints

- Each `UI_Manager` has a fixed maximum element count set at allocation time
  (`allocate_ui_manager__members`). This determines both the pool size and
  the pointer array size.
- The `UI_Context` holds at most `MAX_QUANTITY_OF__UI_MANAGERS` (default 8)
  concurrent managers, limiting the number of simultaneously open UI windows.
- Tile map availability is bounded by the pool sizes in
  `UI_Tile_Map_Manager`. Each `Graphics_Window` consumes one tile map.
- Container elements hold at most
  `UI_CONTAINER_PTR_ENTRIES_MAXIMUM_QUANTITY_OF` (default 8) children.

## Error Handling

- Debug builds use `debug_abort` for null pointer violations in non-null-safe
  functions and for out-of-bounds index access in `UI_Manager`.
- Debug builds use `debug_error` for type mismatches (e.g., calling slider
  functions on non-slider elements).
- Allocation functions return null pointers when pools are exhausted.
- `UI_Tile_Map__Wrapper` validation functions (`is_ui_tile_map__wrapper__valid`,
  etc.) allow callers to check wrapper integrity before use.
