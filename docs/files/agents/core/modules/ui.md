# UI — Retained-model UI system with tile maps and element hierarchies

**Sources:** `core/source/ui/` + `core/include/ui/`

## Surface Concerns

UI is an L4 PRESENTATION module providing a retained-model UI system built on tile maps and element hierarchies. `UI_Manager` instances live in `UI_Context` (fixed 8-slot array in `Gfx_Context`) and are associated with `Graphics_Window` objects by UUID; their element trees compose into tile map textures rendered as part of the window. Top consumers: game-layer scene code (code-generated `poll_ui_for__scene_*` calls `poll_ui_manager__update` each frame), `core/source/rendering/graphics_window.c` (compose hook), and game-installed load/close callbacks via `UI_Window_Record`.

- **Element hierarchy** — Tree-structured primitives with parent/child/next linkage. Each element has a kind (Button, Draggable, Slider, Drop_Zone, Text, Text_Box, Logical, Window), capabilities driven by nine callback function pointers, and an AABB hitbox (allocated from the window's hitbox manager, keyed by the element's UUID) for cursor-based focus and click detection.
- **Manager lifecycle** — `UI_Manager` maintains a malloc'd pool of element structs and a pointer array. Insertion order defines priority (later = lower priority). The manager handles focus detection, input dispatch, and element allocation/release; pool size is chosen at allocation time (`MAX_QUANTITY_OF__UI_ELEMENTS = 128` is the bound used by the inline index getter and the size the game layer typically allocates).
- **Tile maps** — Three fixed-size tile map types (Small: 8x8, Medium: 16x16, Large: 32x32) wrapped by `UI_Tile_Map__Wrapper` for dynamic sizing. Elements compose into tile maps via `generate_ui_span_in__ui_tile_map`, which then flows to the backend via `PLATFORM_compose_ui_span_in__gfx_window`.
- **Focus and input** — Single focused element per manager. Cursor-based detection scans elements in array order, skipping disabled and non-interactive elements. Strict cursor validation re-checks hitbox containment. Focus loss resets input mode to NORMAL. Writing mode activates for text elements on click.
- **Window registration** — `UI_Context.ui_window_record[]` indexed by `Graphics_Window_Kind` stores game-installed load/close callbacks and sprite/UI element allocation counts (positive = allocate new, negative = share parent, zero = none). Opening a window allocates a graphics window, optionally shares or allocates child managers, then calls the load callback.
- **Direct mutation, no game actions** — UI state mutates directly (allocation, position, release) from game processes. A `UI_MANAGER_FLAG__IS_DIRTY` flag notifies composition, but there is no game action wrapping. Dispose cascade (`m_ui_element__dispose_handler__default`) recursively disposes children and next-siblings, then releases hitbox and sprite.
- **Serialization and UUID branding** — Elements carry `Serialization_Header` branded with UUIDs derived from the parent manager's UUID (6 low bits). Resolution uses `dehash_identitier_u32_in__contigious_array()`.

## Public API Surface

### Key Types

**`UI_Element`** — defined in `defines.h`. The fundamental UI primitive. Key members:
- `UI_Element *p_parent, *p_child, *p_next` — tree linkage (parent/child/next).
- `enum UI_Element_Kind the_kind_of_ui_element__this_is` — Button, Draggable, Slider, Drop_Zone, Text, Text_Box, Logical, Window.
- `UI_Flags__u16 ui_flags` — IS_ENABLED, IS_FOCUSED, IS_NON_INTERACTIVE, IS_BEING_HELD, IS_BEING_DRAGGED, IS_SNAPPED_X_OR_Y_AXIS, IS_USING_SPRITE_OR_UI_TILE_SPAN.
- Nine callback function pointers: `m_ui_dispose_handler`, `m_ui_compose_handler`, `m_ui_clicked_handler`, `m_ui_dragged_handler`, `m_ui_dropped_handler`, `m_ui_receive_drop_handler`, `m_ui_held_handler`, `m_ui_typed_handler`, `m_ui_transformed_handler`.
- `UI_Tile_Span ui_tile_span` — tile span data when not using sprites.
- `UI_Element_Data ui_element_data` — game-layer per-element data.

**`UI_Manager`** — defined in `defines.h`. Container for elements. Key members:
- `UI_Element *pM_ui_element_pool` — malloc'd array of element structs.
- `UI_Element **pM_ptr_array_of__ui_elements` — malloc'd array of element pointers (priority order).
- `UI_Element *p_ui_element__focused` — currently focused element.
- `UI_Manager_Flags__u8 ui_manager_flags__u8` — includes UI_MANAGER_FLAG__IS_DIRTY.
- `Repeatable_Psuedo_Random randomizer` — UUID generation.

**`UI_Context`** — defined in `defines.h`. Root UI state in `Gfx_Context`. Key members:
- `UI_Manager ui_managers[MAX_QUANTITY_OF__UI_MANAGERS]` — contiguous fixed array (8).
- `UI_Window_Record ui_window_record[Graphics_Window_Kind__Unknown]` — per-window registration.

**`UI_Tile_Map__Wrapper`** — defined in `defines.h`. Dynamic view over one of three fixed tile map types. Key members:
- `UI_Tile_Raw *p_ui_tile_data` — pointer to tile data.
- `Quantity__u32 width_of__ui_tile_map, height_of__ui_tile_map`.
- `UI_Tile_Map_Size catagory_size_of__ui_tile_map` — Small, Medium, or Large.

**`UI_Window_Record`** — defined in `defines.h`. Registration metadata. Key members:
- `f_UI_Window__Load f_ui_window__load`, `f_UI_Window__Close f_ui_window__close` — game callbacks.
- `Signed_Quantity__i32 signed_quantity_of__sprites`, `Signed_Quantity__i16 signed_quantity_of__ui_elements` — allocation policy.

### Key Functions

**Manager lifecycle:**
- `void initialize_ui_manager(UI_Manager *);`
- `bool allocate_ui_manager__members(UI_Manager *, Quantity__u16);` — returns true on success.
- `void release_ui_manager__members(UI_Manager *);`

**Element lifecycle:**
- `void initialize_ui_element(UI_Element *, UI_Element *, UI_Element *, UI_Element *, enum UI_Element_Kind, UI_Flags__u16);`
- `UI_Element *allocate_ui_element_from__ui_manager(UI_Manager *);` — returns element or 0.
- `UI_Element *allocate_ui_element_from__ui_manager_as__child(Game *, Graphics_Window *, UI_Manager *, UI_Element *);`
- `void release__ui_element_from__ui_manager(Game *, Graphics_Window *, UI_Manager *, UI_Element *);`

**Focus and input:**
- `void poll_ui_manager__update(UI_Manager *, Game *, Graphics_Window *);`
- `UI_Element *detect_focus_in__ui_manager(UI_Manager *, Game *);` — returns focused element or 0.
- `UI_Element *detect_focus__strictly_under_cursor_in__ui_manager(UI_Manager *, Game *);`

**Composition and rendering:**
- `void compose_all_ui_elements_in__ui_manager(UI_Manager *, Game *, Graphics_Window *);`
- `void render_all_ui_elements_in__ui_manager(UI_Manager *, Game *, Graphics_Window *);` — declared in `ui_manager.h`, no core implementation.

**Window registration:**
- `void register_ui_window_into__ui_context(UI_Context *, f_UI_Window__Load, f_UI_Window__Close, Graphics_Window_Kind, Signed_Quantity__i32, Signed_Quantity__i16);`
- `Graphics_Window *open_ui_window(Game *, Graphics_Window_Kind);` — returns window or 0.
- `void close_ui_window(Game *, Identifier__u32);`

## Key Files Table

| File | Role |
|------|------|
| `core/source/ui/ui_manager.c` | Manager CRUD, focus, input dispatch, element allocation, priority |
| `core/include/ui/ui_element.h` | Element API, inline helpers, handler accessors |
| `core/source/ui/ui_context.c` | Window registry, open/close, populate flow |
| `core/source/ui/ui_element.c` | Element init, dispose cascade, compose, position |
| `core/source/ui/ui_text.c` | Text composition, string rendering, char buffers |
| `core/source/ui/ui_text_box.c` | Text box, typed input, cursor |
| `core/source/ui/ui_slider.c` | Slider element, drag value computation |
| `core/source/ui/ui_tile_map_manager.c` | Tile map allocation/release |
| `core/source/ui/ui_tile_map.c` | Tile map fill, generate span, copy |
| `core/include/ui/ui_tile_map.h` | Tile map sizes, wrapper, span generation |
| `core/include/ui/ui_manager.h` | Manager type, dirty flag, allocation API |
| `core/include/ui/ui_context.h` | UI_Context, window registration |
| `core/source/ui/ui_window_element.c` | Window element: opens child UI window, forwards input, moves window on transform |
| `core/source/ui/ui_window.c` | Default window-close callback |
| `core/source/ui/ui_drop_zone.c` | Drop zone, receive-drop handler |
| `core/source/ui/ui_draggable.c` | Draggable element, drag start and position |
| `core/source/ui/ui_button.c` | Button init, click/toggle default handlers |
