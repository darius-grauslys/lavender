# Overview

editor_map.py is a visualizer for the world serialization 
process of the Lavender game engine

Somethings are marked as "configurable" this means the
editor_map.json file in the project's ./assets directory
has a configuration field bearing the value of the
described property.

## Engine Source File References

The editor implementation MUST derive its understanding of
data types, struct layouts, constants, and serialization formats
from the engine source files listed below. Do NOT hardcode
values — always read and parse the engine source to determine
the correct implementation. If the engine source changes, the
editor should automatically adapt.

### Core Type Definitions

- `core/include/defines.h` — Master definition file for ALL
  structs, macros, and typedefs. This is the single source of
  truth for struct layouts including: `Entity`, `Chunk`,
  `Global_Space`, `Inventory`, `Item_Stack`, `Serialization_Header`,
  `Serialization_Header__UUID_64`, `Tile_Logic_Record`,
  `Tile_Logic_Context`, `Chunk_Data`, `Chunk_Flags`, etc.

- `core/include/defines_weak.h` — Forward declarations and
  weak/fallback definitions for all types. Contains the
  `#include <types/implemented/...>` pattern that loads
  project-local type overrides. The pattern is:
  ```c
  #include <types/implemented/world/tile_kind.h>
  #ifndef DEFINE_TILE_KIND
  // fallback definition
  #endif
  ```
  The editor must understand this pattern: if a project-local
  header defines the guard macro (e.g., `DEFINE_TILE_KIND`),
  the project-local definition takes precedence.

### Engine Configuration & Constants

- `core/include/platform_defaults.h` — Defines ALL default
  constants including chunk dimensions, local space manager
  dimensions, max entity counts, tile pixel sizes, etc.
  These are the fallback values when a project does not override.

- `core/include/config/implemented/engine_config.h` — Project-
  overridable engine constants. Contains commented-out `#define`
  directives that projects uncomment to override defaults from
  `platform_defaults.h`. The editor MUST parse the project's
  copy of this file (at `./include/config/implemented/engine_config.h`
  relative to the project directory) to detect overridden constants.
  For `BIT(n)` expressions, evaluate as `1 << n`.
  Fall back to `platform_defaults.h` defaults for any constant
  not overridden.

### Tile System

- `core/include/world/chunk.h` — Tile indexing within chunks.
  Contains `get_p_tile_from__chunk` and `set_tile_of__chunk`.
  The read-path indexing formula in `get_p_tile_from__chunk`
  is the authoritative tile index formula for serialized data.
  NOTE: The Y-axis is inverted in memory. NOTE: `set_tile_of__chunk`
  uses a DIFFERENT formula that does NOT invert Y — this is a
  known engine inconsistency; use the `get_p_tile_from__chunk`
  formula for serialization.

- `examples/template-files/include/types/implemented/world/tile.h` —
  Reference implementation of a project-local `Tile` struct.
  Demonstrates the `union` pattern with `GEN-RENDER-BEGIN/END`
  and `GEN-LAYER-BEGIN/END` markers, and critically the
  `u8 array_of__tile_data__u8[N]` member which deterministically
  encodes `sizeof(Tile) == N`.

- `examples/template-files/include/types/implemented/world/tile_kind.h` —
  Reference implementation of `Tile_Kind` enum with `GEN-LOGIC-BEGIN/END`
  and `GEN-NO-LOGIC-BEGIN/END` markers.

- `examples/template-files/include/types/implemented/world/tile_cover_kind.h` —
  Reference implementation of a project-local tile layer enum.
  NOTE: `Tile_Cover_Kind` is NOT an engine type — it is a user-defined
  tile layer enum. The editor must NOT hardcode `Tile_Cover_Kind`.
  Projects may define different tile layer enums with different names.
  The engine only guarantees `Tile_Kind` as the default layer
  (mapped via `Tile_Layer__Default`). Additional layers and their
  enum types are entirely project-defined.

- `examples/template-files/include/types/implemented/world/tile_layer.h` —
  Reference implementation of `Tile_Layer` enum with `GEN-BEGIN/END` markers.

- `core/include/types/implemented/world/tile_kind.h` — Engine default
  (nearly empty) `Tile_Kind`. Shows the `DEFINE_TILE_KIND` guard pattern.

- `core/include/types/implemented/world/tile_layer.h` — Engine default
  (nearly empty) `Tile_Layer`. Shows the `DEFINE_TILE_LAYER` guard pattern.

### Tile Layer to Tile Kind Enum Mapping

The engine's tile layer system works as follows:
- `Tile_Layer` enum defines named layers (e.g., `Tile_Layer__Ground`,
  `Tile_Layer__Cover`). The first layer (`Tile_Layer__Default`) always
  maps to `Tile_Kind` (from `tile_kind.h`).
- Additional layers beyond the default are project-defined. Their
  enum types (e.g., `Tile_Cover_Kind`) are NOT engine types — they
  are user-defined and may have any name.
- The mapping from layer to enum type is found in the project-local
  `tile.h` inside the `GEN-RENDER-BEGIN` / `GEN-RENDER-END` block.
  Each bitfield in that block corresponds to a tile layer, in order.
  The type of each bitfield (e.g., `Tile_Kind`, `Tile_Cover_Kind`)
  tells the editor which enum to use for that layer's dropdown.
  If a field is declared without an explicit bit width (no `: N`),
  the editor assumes **8 bits** for that layer.
- The editor must parse these bitfield type names dynamically and
  load the corresponding enum from the project's headers. It must
  NOT assume any specific layer enum name beyond `Tile_Kind`.

### Entity System

- `core/include/types/implemented/entity/entity_data.h` — Engine default
  `Entity_Data` struct. Projects override via `DEFINE_ENTITY_DATA`.
  The editor must parse the project-local version at
  `./include/types/implemented/entity/entity_data.h`.

- The `Entity` struct in `defines.h` contains:
  `Serialization_Header` + `Entity_Data` + `Entity_Functions`.
  `Entity_Functions` contains function pointers that are
  runtime-only and MUST NOT be serialized.

### World Serialization & Filesystem

- `core/source/world/serialization/world_directory.c` — Authoritative
  source for world filesystem layout, chunk directory path generation
  (quad-tree descent), and file naming (`t` for tiles, `e` for entities,
  `i` for inventories, `h` for world header). The editor MUST replicate
  this path generation logic exactly in Python, including any quirks.
  NOTE: `append_base64_value_to__path` contains a potential bug where
  `_base64_lexicon[value]` is used instead of `_base64_lexicon[b64]` —
  the editor must replicate the actual behavior.

- `core/source/world/global_space_manager.c` — Global space allocation,
  reference counting, and lifecycle management. Useful for understanding
  how global spaces are held/dropped and how UUIDs are generated.

- `core/source/world/local_space_manager.c` — Local space manager
  initialization and scrolling. Demonstrates the toroidal linked-list
  structure and Z-axis conditional compilation
  (`#if LOCAL_SPACE_MANAGER__DEPTH > 1`).

### UUID System

- UUID widths vary by type. Consult `defines.h`:
  - `Serialization_Header` uses `Identifier__u32` (32-bit) — used by
    `Entity`, `Inventory`, `Item_Stack`, `UI_Element`.
  - `Serialization_Header__UUID_64` uses `Identifier__u64` (64-bit) —
    used by `Global_Space`, `Chunk`, `Collision_Node`.
  - UUID branding scheme is defined in `defines_weak.h` under
    `UUID_BRANDING__*` macros.

# 1. UI

## 1.1 Editor Modes

Each Editor Mode should be its own python module
with separated concerns, inheriting from a common
Editor_Mode class.

Above the Workspace, is a tab selection of editor modes.

### Selection Tool:

For each editor mode, the 1st tool is always 
the Selection tool (unless explicitly stated otherwise
in the editor mode specification.)

Overrides the left click to select whatever the active
editor mode defines as a valid selection.

When the defined valid selection object of the active
editor mode is selected, the properties HUD per
section 1.3 is populated with the relevant fields of that
object. These fields are specified in section 3.

By default, the selection tool supports selecting
multiple elements.

By default, the copy functionality is only supported 
for single elements.

#### Selection Indicator

Defined valid selection objects of the active
editor mode are revealed with purple outline boxes of 3 pixel width.

#### Ctrl+C

Ctrl+C is overriden by default to copy the whole contents
of the valid selection.

#### Ctrl+V

Ctrl+V is overriden by default ot paste the whole contents
of the valid selection.

### Panning Tool:

For each editor mode, the 2nd tool is always
the Panning tool (unless explicitly stated otherwise
in the editor mode specification.)

By default the following inputs are overriden:

#### Scrolling Mouse Scroll Wheel: 

When shift is not held:

Scrolling up pans the Workspace up.
Scrolling down pans the Workspace down.

When Shift is held:

Scrolling up pans the Workspace left.
Scrolling down pans the Workspace right.

#### Arrow keys

Moves the Workspace by 1 world tile in the respective
directions of: left, right, up, and down arrows.

### 1.1.1 Global_Space View

Mode activation shortcut: Ctrl+G

#### 1.1.1.1 Tooling

##### 1.1.1.1.1 Global_Space Select

Valid selections are Global Spaces.

The selection indicator size if the chunk size of
the Global_Space. By default this is 8x8 tiles
and is configurable.

Ctrl+C will copy the entire global space this
includes:
- Chunk
- Entities
- Hitboxes
- Inventories

Ctrl+V will overwrite the contents of the selected
global space with the copied contents.

Arrow-Keys are overriden by this tool to move
the selected global space by the associated
arrow key direction.

Shift+Up and Shift+Down are overriden by this tool
to move the global space selection up and down on
the Z axis ("in and out of screen") and move the
Workspace view accordingly see section 2.1.1.

##### 1.1.1.1.2 Global_Space Pan

Shift + Arrow-Keys will move the workspace
by whole global spaces.

##### 1.1.1.1.3 Go-To

When this Tool is clicked, it will unselect itself
and spawn a Prompt window accepting the following
validated input fields:

X: i32
Y: i32
Z: i32

Upon clicking "OK" on the prompt window the workspace will 
move to the center of the specified chunk. The editor chunk space 
representation should be updated to show the new work area.

See section 2.1.1 for moving the Workspace

### 1.1.2 Chunk Edit

Mode activation shortcut: Ctrl+K

NOTE: This is by far the HARDEST and LEAST TRIVIAL part of this editor.
NOTE: See section 3.1.2.1 for more information on how Tiles work.

#### 1.1.2.1 Tooling

##### 1.1.2.1.1 Tile Select

Valid selections are Tiles.

The properties window should 

Ctrl+C will copy the selected tile.

Ctrl+V will overwrite the contents of the selected
tile with the copied contents.

Arrow-Keys are overriden by this tool to move
the selected tile by the associated
arrow key direction.

Shift+Up and Shift+Down are overriden by this tool
to move the tile selection up and down on
the Z axis ("in and out of screen") and move the
Workspace view accordingly see section 2.1.1.

##### 1.1.2.1.2 Chunk Pan

Arrow-Keys will move workspace by single tiles.

Shift + Arrow-Keys will move the workspace
by whole chunks.

##### 1.1.2.1.3 Tile Draw

When this tool is selected, the Tool Properties menu
will be populated with a complete 5 element wide scrollable
grid of tiles. Tiles selected in this grid are used to
replace tiles as describe here:

This tool will disable the selecting logic of valid objects on the Workspace.
When this tool is selected and the workspace is left clicked, Tiles that
would otherwise be selected are replaced.

### 1.1.3 Entity Edit

Mode activation shortcut: Ctrl+E

#### 1.1.3.1 Tooling

##### 1.1.3.1.1 Tile Select

Valid selections are Entities.

The Selection Indicator is centered on the position of
the entity component.

The Selection Indicator is the bounding hitbox of the entity.
The Selection Indicator is not present if the entity lacks a
Hitbox.

Ctrl+C will copy the entire entity this
includes:
- The entity selected
- The matching hitbox UUID
- The matcing Inventory UUID

Ctrl+V will create a new entity into the Workspace
where the mouse cursor is.

Del is overriden by this tool to delete the selected entity.

##### 1.1.3.1.2 Entity Pan

This is the pan tool for the Entity Editor mode.
It has default functionality as described in section 1.1.

#### 1.1.3.1.3 Create Entity

Going off of the entity type definition per section 3
populate the tool properties menu with fields needed
for creating a serialized entity.

Include property fields to define a hitbox if
the tool bool property "has hitbox" is checked off

Include property fields to define a inventory if
the tool bool property "has inventory" is checked off

When clicked in the world space, spawn the entity as a
new entry.

### 1.1.4 Container/Inventory Edit

Mode activation shortcut: Ctrl+I

THIS MODE IS PLACEHOLDER AT THIS TIME.
Implement as a stub editor mode that displays
"Container/Inventory Edit — Not yet implemented"
in the workspace area. Do not implement any tooling.

#### 1.1.4.1 Tooling

THIS MODE IS PLACEHOLDER AT THIS TIME.

## 1.2 Tool HUD

The tool hud is resizable and anchored to the right side
of the editor window, it is overlayed on top of the workspace.

When the tool hud takes input, it consumes it and does not let
it propogate to the workspace.

When resizing the tool HUD, ensure the input is consumed
and does not propgate to the workspace.

The Tool HUD anchors to the top of the screen and anchors
its bottom to the top of the Properties HUD.

### 1.2.1 Tool selection shortcuts:

Shift+N where N is [0-9]
And then Ctrl+Shift+N for [10-19]

Will select tools in order that they appear in this
spec for the given Editor Mode currently active.

### 1.2.2 Toolkit

Top most sub-window

A scrollable sub-window in the Tool HUD 
containing 5 wide grid of tools for selecting tools
defined under the currently active editor mode.

### 1.2.3 Tool Properties

Below "Toolkit" sub-window

For the tool selected, editor configurable properties 
on utilization of the selected tool are populated here.

## 1.3 Properties HUD

When resizing the Properties HUD, ensure the input is consumed
and does not propgate to the workspace.

The Properties HUD anchors to the top of the screen and anchors
its bottom to the top of the Messages HUD.

The fields of properties are updated based on selected object.
The fields of properties for a selected object are determined
by section 3 and derived from the engine source files.

### 1.3.1 Deriving Property Fields

The Properties HUD fields for each object type MUST be derived
from the engine source, not hardcoded. The agent implementing
this should consult:

**For Global_Space properties:**
See the `Global_Space` struct in `core/include/defines.h`.
Display all non-pointer, non-function fields. Pointer fields
(e.g., `p_chunk`, `p_collision_node`, `p_generation_process`)
are runtime-only and should not be displayed.

**For Tile properties:**
See the project-local `./include/types/implemented/world/tile.h`.
Parse the `GEN-RENDER-BEGIN` / `GEN-RENDER-END` block to find
the tile layer enum fields. The first field is always `Tile_Kind`
(the engine-guaranteed default layer). Additional fields are
project-defined tile layer enums (e.g., a project might define
`Tile_Cover_Kind` or any other name). The editor must discover
these types dynamically from the bitfield type names in the
`GEN-RENDER-BEGIN` block — do NOT hardcode any layer enum name
beyond `Tile_Kind`. Each enum field should be an editable dropdown
populated from the corresponding parsed enum values.

**For Entity properties:**
See the `Entity` struct in `core/include/defines.h` and the
project-local `./include/types/implemented/entity/entity_data.h`.
Display `Serialization_Header` fields as read-only.
Display `Entity_Data` fields as editable.
Do NOT display `Entity_Functions` (runtime-only function pointers).
See `core/include/defines.h` for entity flag definitions
(`ENTITY_FLAG__*`) to interpret the entity flags bitfield.

**For Inventory properties (placeholder):**
Not yet implemented. See section 1.1.4.

### 1.3.2 Field Types

Map C types to validated input fields per section 1.7:
- `u8`, `u16`, `u32`, `u64` → unsigned integer fields
- `i8`, `i16`, `i32`, `i64` → signed integer fields
- Enum types → dropdown selection populated from parsed enum
- Bitfield/flags types → checkboxes for each known flag bit
- `Identifier__u32` / `Identifier__u64` → read-only unsigned integer

## 1.4 File Hierarchy HUD

The file hierarchy HUD shows world folders per section 3.
The sub folders of these world folders ARE NOT shown.

The world folders are treated as entities in the file hierarchy list
that can be clicked.

The file hierarchy has a "X" to delete the world. When clicked a Prompt
will appear requiring the user to type the name of the world before
clicking OK. If OK is clicked and the name is not correctly typed
nothing happens.

The file hierarchy has a "+" below the worlds to add new worlds.

The file hierarchy can be scrolled.

When resizing the File Hierarchy HUD, ensure the input is consumed
and does not propgate to the workspace.

The File Hierarchy HUD anchors to the top of the screen and anchors
its bottom to the top of the Messages HUD.

NOTE: If the project in the executing directory of the editor
is Under Defined per section 3. clicking or creating a world
should fail with an ERROR messages to Message HUD indicating
the project is under defined.

## 1.5 Message HUD

The Message HUD is implemented locally in
`tools/editors/editor_map/ui/message_hud.py`.
It supports SYSTEM, INFO, WARNING, and ERROR message levels.

When resizing the Messages HUD, ensure the input is consumed
and does not propgate to the workspace.

The Message HUD is anchored to the bottom of the editor window
and anchored to the left and right sides of the window.

Messages MUST word-wrap to the width of the Message HUD panel.
Long messages should never extend beyond the panel boundary or
require horizontal scrolling. Use `imgui.push_text_wrap_pos` /
`imgui.pop_text_wrap_pos` to wrap text at the available content
region width.

The Messages HUD is collapsable, clicking on a window title button
on the HUD will minimize the Messages HUD to just the title.

Ctrl+M will toggle the collapsed state of the Message HUD.

Whenever an ERROR or SYSTEM message is printed to the Message HUD while it
is collapsed, the Message HUD should automatically uncollapse.

When Ctrl+H is pressed, all active key-binds (dependent on
editor mode) should be printed to the Message HUD as a SYSTEM
message.

On editor startup, the Messages HUD should be uncollapsed
and print the version of the editor.

### 1.5.1 Writing Messages to Message HUD

The Message HUD should accept the following messages:

## 1.6 Prompts

Prompts are windows that overlay on top of the editor.
When they are clicked, they consume the input such that
the input does not activate the Workspace, or any UI
panel.

## 1.7 Validated Input Fields

Validated Input Fields are fields which are modifiable
(Backspace to delete, etc) and only accept user input
for the type it is associated with:

u8: Only [0-9] for max(u8) values
u16: Only [0-9] for max(u16) values
u32: Only [0-9] for max(u32) values
u64: Only [0=9] for max(u64) values
i8: Only [0-9] for max(i8) values
i16: Only [0-9] for max(i16) values
i32: Only [0-9] for max(i32) values
i64: Only [0=9] for max(i64) values
str: Any characters.
bool: A checkmark box

## 1.8 Readonly Fields

Read only fields are fields which cannot be modified.

# 2. Functionality

## 2.1 Workspace

### 2.1.1 Global_Space rendering/management

See `core/source/world/global_space_manager.c`
for implementation suggestions on memory management
of global spaces. Key functions: `allocate_global_space_in__global_space_manager`,
`hold_global_space_within__global_space_manager`,
`drop_global_space_within__global_space_manager`.

See `core/source/world/local_space_manager.c`
for implementation suggestions on chunk rendering
of global spaces (note it is local_space_manager
because local_space nodes point to global_space
nodes, and have additional overhead data to associate
adjacent local_spaces.)

See `core/include/defines.h` for the `Global_Space`, `Local_Space`,
`Local_Space_Manager`, `Chunk`, and `Chunk_Data` struct definitions.

See `core/include/platform_defaults.h` for `LOCAL_SPACE_MANAGER__WIDTH`,
`LOCAL_SPACE_MANAGER__HEIGHT`, `LOCAL_SPACE_MANAGER__DEPTH`,
`GFX_CONTEXT__RENDERING_WIDTH__IN_CHUNKS`, etc.

Note: Z-axis support in `local_space_manager.c` is conditional on
`LOCAL_SPACE_MANAGER__DEPTH > 1`. When depth is 1, Z-axis code is
compiled out. The editor should support Z-axis navigation but
gracefully handle depth=1 worlds.

# 3. World Serialization Data

See core/source/world/serialization/world_directory.c
for identifying the location of world data on the filesystem
and navigating the world directory tree to find world data.

When implementing python logic to serialize/deserialze these
objects, have the scripts look at:

./include/types/implemented/entity/entity_data.h
./include/types/implemented/entity/item_data.h
./include/types/implemented/inventory/item.h
./include/types/implemented/world/tile.h

NOTE: these files are local to the PROJECT DIR not the GAME ENGINE DIR.
Meaning this editor will be invoked from a directory that is NOT this
git repo. Therefore these ./include files are relative to the executing
directory of the editor.

See core/include/defines.h on how these project configurable include files
are injected into the game engine to define the struct sizes.

## Loading Types

THE EDITOR MUST INTERPRET PROPERTY FIELDS BASED ON CONFIGURATION.
This is going to not be easy! See section 4.5 for guidance.

At this time, the editor will not support types defined
outside of what is specified in section 4.5.

## Under Defined Project

NOTE: if the local files are not present generate an ERROR message to
Message HUD.

## Deriving Serialization Formats from Engine Source

The editor MUST NOT hardcode struct sizes, field offsets, or
constant values. Instead, derive them from the engine source:

### Chunk Constants

Read chunk dimensions from the project's engine_config.h
(at `./include/config/implemented/engine_config.h` relative to
project dir). For any constant not overridden there, fall back
to the defaults in `core/include/platform_defaults.h`.

Key constants to resolve:
- `CHUNK__WIDTH` (default: `BIT(3)` = 8)
- `CHUNK__HEIGHT` (default: `BIT(3)` = 8, NOTE: engine has a
  macro typo `CHUNK_HEIGHT` vs `CHUNK__HEIGHT`)
- `CHUNK__DEPTH` (default: `BIT(1)` = 2)
- `CHUNK__QUANTITY_OF__TILES` (default: WIDTH * HEIGHT * DEPTH)

### Tile Size

Parse the project-local `./include/types/implemented/world/tile.h`.
Look for the `u8 array_of__tile_data__u8[N]` member inside the
`Tile` struct union. The array size `N` gives `sizeof(Tile)`.
See `examples/template-files/include/types/implemented/world/tile.h`
for the reference pattern.

### Tile Indexing

The authoritative tile index formula is in
`core/include/world/chunk.h` in the `get_p_tile_from__chunk`
function. The Y-axis is INVERTED in memory.

### Chunk Binary Layout

From `core/include/defines.h`, the `Chunk` struct is:
```
Serialization_Header__UUID_64 (size_of__struct: u32 + uuid: u64)
Chunk_Flags (u16)
Tile tiles[CHUNK__QUANTITY_OF__TILES]
```
The tile file (`t`) contains the raw tile array only.

### Entity Binary Layout

From `core/include/defines.h`, the serialized portion of
`Entity` is: `Serialization_Header` (u32 size + u32 uuid) +
`Entity_Data` (project-local, see entity_data.h).
`Entity_Functions` contains function pointers and MUST NOT
be serialized. See `core/include/defines.h` for the
`ENTITY_FLAG__IS_WITH_HITBOX__SERIALIZATION` and
`ENTITY_FLAG__IS_WITH_INVENTORY__SERIALIZATION` flags which
indicate associated components.

### Endianness

The engine targets NDS (ARM7/9, little-endian) and x86/x64
(little-endian). Assume little-endian for all serialized data.

## 3.1 Global_Space

See `core/include/defines.h` for the `Global_Space` struct definition.
See `core/source/world/global_space_manager.c` for allocation, UUID
generation (`get_uuid_for__global_space`), reference counting, and
lifecycle management.

Global spaces are not serialized as monolithic blobs. Their components
(tiles, entities, inventories) are serialized to separate files within
the chunk directory tree. See `core/source/world/serialization/world_directory.c`
for the filesystem layout.

## 3.1.2 Chunk

See `core/include/defines.h` for the `Chunk` and `Chunk_Data` struct
definitions. The chunk tile file (`t`) contains the raw
`Tile tiles[CHUNK__QUANTITY_OF__TILES]` array.

See `core/include/world/chunk.h` for tile indexing, chunk flag
management, and the `get_p_tile_from__chunk` function which defines
the authoritative tile index formula.

See `core/include/platform_defaults.h` for `CHUNK__WIDTH`,
`CHUNK__HEIGHT`, `CHUNK__DEPTH`, and `CHUNK__QUANTITY_OF__TILES`.
These may be overridden by the project's `engine_config.h`.

### 3.1.2.1 Tile

Pay VERY close attention to the Tile memory footprint
it is VERY MUCH NOT TRIVIAL.

The Tile struct is project-local. The editor must parse the
project's `./include/types/implemented/world/tile.h` to determine
the tile layout. The key patterns to look for:

1. `u8 array_of__tile_data__u8[N]` — gives `sizeof(Tile) == N`
2. `GEN-RENDER-BEGIN` / `GEN-RENDER-END` — contains the tile layer
   enum fields with their bit widths. The first field is always
   `Tile_Kind` (engine default layer). Additional fields are
   project-defined tile layer enums whose names must be discovered
   dynamically from the bitfield type names. These are the editable
   properties in the Properties HUD.
3. `GEN-LAYER-BEGIN` / `GEN-LAYER-END` — contains the logic and
   animation sub-fields organized into byte-aligned groups.

#### 3.1.2.1.1 Bitfield Default Rules

**GEN-RENDER fields without explicit bit widths:**
If a field in the `GEN-RENDER-BEGIN` / `GEN-RENDER-END` block is
declared without an explicit bit width (e.g. `Tile_Kind the_kind_of__tile;`
instead of `Tile_Kind the_kind_of__tile : 10;`), the editor MUST
assume the field occupies **8 bits** (one full byte). This is the
common case for Under Defined or minimal projects where the Tile
struct has `array_of__tile_data__u8[1]` and a single layer field
with no bit width annotation.

**GEN-LAYER sub-bit field defaults:**
If the `GEN-LAYER-BEGIN` / `GEN-LAYER-END` block is empty or
absent, the editor MUST assume the following defaults for each
tile layer:
- Logic bit field width: **0** bits
- Animation bit field width: **0** bits
- Remainder bit field width: **8** bits

This means each layer occupies exactly 1 byte with no logic or
animation sub-partitioning. The full byte is treated as the
remainder (the raw enum value).

These defaults ensure that a minimal `tile.h` such as:
```c
typedef struct Tile_t {
    union {
        struct {
            // GEN-RENDER-BEGIN
            Tile_Kind the_kind_of__tile;
            // GEN-RENDER-END
        };
        struct {
            // GEN-LAYER-BEGIN
            // GEN-LAYER-END
        };
        u8 array_of__tile_data__u8[1];
    };
} Tile;
```
is correctly interpreted as a 1-byte tile with a single 8-bit
`Tile_Kind` layer, zero logic bits, zero animation bits, and
8 remainder bits.

Reference files for understanding the patterns:
- `examples/template-files/include/types/implemented/world/tile.h`
- `examples/template-files/include/types/implemented/world/tile_layer.h`
- `examples/template-files/include/types/implemented/world/tile_kind.h`
- `examples/template-files/include/types/implemented/world/tile_cover_kind.h`

For tile indexing within chunks, see `core/include/world/chunk.h`
(`get_p_tile_from__chunk`). The Y-axis is inverted in memory.

For tile logic tables (optional, lower priority):
- `examples/template-files/source/world/implemented/world/tile_logic_table__cover.c`
- `examples/template-files/source/world/implemented/world/tile_logic_table__ground.c`
- `examples/template-files/source/world/implemented/world/tile_logic_table_registrar.c`

## 3.1.3 Entity

See `core/include/defines.h` for the `Entity` struct layout.
The serialized portion is `Serialization_Header` + `Entity_Data`.
`Entity_Functions` MUST NOT be serialized (contains function pointers).

See `core/include/types/implemented/entity/entity_data.h` for the
engine default `Entity_Data`. The project may override this via
`DEFINE_ENTITY_DATA` in `./include/types/implemented/entity/entity_data.h`.

See `core/include/defines.h` for `ENTITY_FLAG__IS_WITH_HITBOX__SERIALIZATION`
and `ENTITY_FLAG__IS_WITH_INVENTORY__SERIALIZATION` flags which indicate
whether the entity has associated hitbox/inventory components.

After the entire Global_Space is loaded
if the Entity does not have a matching hitbox
UUID, write an INFO message into the Message HUD:
"Entity: [UUID] lacks a Hitbox."

## 3.1.4 Inventory

See `core/include/defines.h` for the `Inventory` and `Item_Stack`
struct definitions. Inventories use 32-bit UUIDs
(`Serialization_Header`). The UUID encoding scheme for inventory
containers vs entity inventories is defined by the
`UUID_BIT_SHIFT__INVENTORY__*` and `UUID_MASK__INVENTORY__*`
macros in `core/include/defines.h`.

## 3.1.5 Hitbox

See `core/include/defines.h` for `Hitbox_AABB` and
`Hitbox_AABB_Manager` struct definitions. Hitboxes use 32-bit
UUIDs (`Serialization_Header`). The `Hitbox_Context` manages
multiple hitbox manager instances of different types.

# 4. Software Architecture

For Agentic work, adhere the following architecture:

## 4.1 UI

### 4.1.1 Editor Mode

Make a base Editor_Mode class, and in ./tools/editors/editor_map/modes/
create each editor mode.

See section 4.4, as Editor_Modes should handle keybind overriding using the
keybind_manager.

### 4.1.2 Tools

Make a base Tool class, and in ./tools/editors/editor_map/tools/[MODE]/
create each tool under each editor mode ([MODE]) as an implementation of Tool.

See section 4.4, as Tools should handle keybind overriding using the
keybind_manager.

For the Selection and Pan tools, make base classes of these tools.

### 4.2 Workspace

Place all rendering logic of the workspace in:
./tools/editors/editor_map/workspace/render.py

Place all object management logic of the workspace in:
./tools/editors/editor_map/workspace/objects.py

Place all workspace movement in:
./tools/editors/editor_map/workspace/movement.py

Have deserialization/serialization occur on a separate thread.
When saving to a file, make a .tmp variant, then do a checksum
on the .tmp, if the checksum is valid write it to the actual
file, and delete .tmp.

Implement a thread safety contract between movement.py
and objects.py where objects.py does not allow public access
of objects held by serialization/deserialization threads.

serialization processes spawn by movement.py are the only
modules who use private access to objects.py, ensure this
is documented in the code.

### 4.3 Serialization

Create a python module representing each object in section 3 of this spec:
./tools/editors/editor_map/core/

Add the relevant serialization/deserialization logic to these files
and have serialization/deserialization logic trickle down from
Global_Space. Provide exposure to the workspace object memory 
via function arguments.

The movement logic of the workspace should make the needed calls to serialization.

### 4.4 Shortcut Keybinding Implementation.

For now, keybindings are NOT reassignable.

To ease the burden of the complexity of keybind logic in the editor
Make the following python modules:
./tools/editors/editor_map/keybinds/keybind.py
./tools/editors/editor_map/keybinds/keybind_manager.py

Implement Keybinds as a dict to map inputs to a stack of function callbacks.
When overriding keybinds, there are the following functions:

set_base_keybinds(dict)
push_override(dict)
pop_override()
clear_override_stack()

set_base_keybinds is to be called on editor start up.
The editor will put all NON tool and NON editor_mode keybinds
(like Ctrl+H for Message HUD keybind help) These base keybinds
are used when the keybind override stack is empty.

When calling push_override, for each keybind in the dict push
the function callback for that keybind into the keybind override stack.
THEN, add the whole key list of the dict argument to a "callee_override_stack"

When pop_override is called, pop the callee_override_stack
and for each key in the popped list, pop the callback function of that
key from the keybind override stack.

When clear_override_stack is called, empty the keybind override stack.

## 4.5 Loading Types 

All fully defined types in defines_weak.h should be implemented as pythonic
representations in:
./tools/editors/editor_map/core/

Additionally, define a c_enum.py type to:
./tools/editors/editor_map/core/

At this time, when determining properties of a supported editor object
the editor should identify and use defines_weak types, and types declared
in the local directories of:

./include/types/implemented/*

Note a great deal of these types will be enums.
If a type fails to load in ./include/types/implemented/*
The editor should produce an ERROR message, and not load the type.

If one of the supported editor objects uses a type which type
that failed to load (not found) the project should be considered
Under Defined per section 3.

### 4.5.1 C Enum Parsing

Implement a C enum parser that handles the patterns found in the
engine source. The parser must support:

1. `typedef enum Name { ... } Name;` declarations
2. Sequential values (auto-incrementing from 0 or from last explicit value)
3. Explicit value assignments (e.g., `Foo = 5,`)
4. Alias assignments (e.g., `Foo = Bar,` where Bar is a prior enum member)
5. `GEN-LOGIC-BEGIN` / `GEN-LOGIC-END` markers
6. `GEN-NO-LOGIC-BEGIN` / `GEN-NO-LOGIC-END` markers
7. `GEN-BEGIN` / `GEN-END` markers
8. Comments (single-line `//` and multi-line `/* */`)

See `core/include/defines_weak.h` for the `#include` + `#ifndef DEFINE_*`
pattern that determines which header provides the authoritative definition.

See `core/include/types/implemented/world/tile_kind.h` for the engine
default (nearly empty) enum with `GEN-*` markers.

See `examples/template-files/include/types/implemented/world/tile_kind.h`
for a populated project-local enum.

NOTE: Enum member names do not always match the enum type name.
For example, the template file
`examples/template-files/include/types/implemented/world/tile_cover_kind.h`
defines a `Tile_Cover_Kind` enum but uses `Tile_Kind__None`,
`Tile_Kind__Logical`, and `Tile_Kind__Unknown` as member names.
The parser must not assume member name prefixes match the typedef name.

NOTE: `Tile_Cover_Kind` is a project-defined type, NOT an engine type.
The editor must discover tile layer enum types dynamically by parsing
the `GEN-RENDER-BEGIN` / `GEN-RENDER-END` block in the project's
`tile.h`. See "Tile Layer to Tile Kind Enum Mapping" in the Engine
Source File References section.

### 4.5.2 Engine Config Parsing

Implement a parser for `engine_config.h` that:

1. Reads the project-local file at
   `./include/config/implemented/engine_config.h`
2. Identifies uncommented `#define CONSTANT_NAME value` lines
3. Evaluates `BIT(n)` expressions as `1 << n`
4. Evaluates `MASK(n)` expressions as `(1 << n) - 1`
5. Falls back to defaults from `core/include/platform_defaults.h`
   for any constant not overridden

See `core/include/config/implemented/engine_config.h` for the
override pattern (commented-out `#define` directives that projects
uncomment).

See `core/include/platform_defaults.h` for all default constant
values and their derivation formulas.

### 4.5.3 Tile Struct Size Extraction

Parse the project-local `./include/types/implemented/world/tile.h`
to extract `sizeof(Tile)` from the `u8 array_of__tile_data__u8[N]`
pattern. Also extract tile layer enum fields from the
`GEN-RENDER-BEGIN` / `GEN-RENDER-END` block.

If a field in the `GEN-RENDER` block is declared without an explicit
bit width (e.g. `Tile_Kind the_kind_of__tile;` instead of
`Tile_Kind the_kind_of__tile : 10;`), assume the field is **8 bits**
wide (one full byte per layer).

Also extract sub-bit field layouts from the `GEN-LAYER-BEGIN` /
`GEN-LAYER-END` block. If the block is empty or absent, assume
default layouts for each layer: logic=0 bits, animation=0 bits,
remainder=8 bits (the full byte is the raw enum value).

See `examples/template-files/include/types/implemented/world/tile.h`
for the reference pattern with explicit bit widths and populated
GEN-LAYER block. See `core/include/types/implemented/world/tile.h`
for the minimal pattern without bit widths and an empty GEN-LAYER
block.

### 4.5.4 Source-Driven Validation

When the editor starts, it should validate its pythonic type
representations against the engine source files. If the engine
source has changed in a way that invalidates the editor's
assumptions, the editor should produce an ERROR message
describing the mismatch.

The following engine source files should be consulted at
editor startup to derive or validate implementation:

| Purpose | Engine Source File |
|---------|-------------------|
| All struct definitions | `core/include/defines.h` |
| Forward declarations & type override pattern | `core/include/defines_weak.h` |
| Default constants | `core/include/platform_defaults.h` |
| Project constant overrides | `core/include/config/implemented/engine_config.h` |
| Tile indexing formula | `core/include/world/chunk.h` |
| World filesystem layout | `core/source/world/serialization/world_directory.c` |
| Global space management | `core/source/world/global_space_manager.c` |
| Local space management | `core/source/world/local_space_manager.c` |
| Entity data (engine default) | `core/include/types/implemented/entity/entity_data.h` |
| Tile struct (reference) | `examples/template-files/include/types/implemented/world/tile.h` |
| Tile_Kind (reference) | `examples/template-files/include/types/implemented/world/tile_kind.h` |
| Tile layer enum (reference, project-defined) | `examples/template-files/include/types/implemented/world/tile_cover_kind.h` |
| Tile_Layer (reference) | `examples/template-files/include/types/implemented/world/tile_layer.h` |

# 6. Testing

For each python module, create unit tests to:
./tools/editors/editor_map/tests/

Prepend "test_" to the module name.

Preserve folder structure of each module relative to ./editor_map
into ./tests for example:
./tools/editors/editor_map/workspace/movement.py
-> ./tools/editors/editor_map/tests/workspace/test_movement.py

There is no integration testing at this time.
