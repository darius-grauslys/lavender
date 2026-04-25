# Overview

editor_map.py is a visualizer for the world serialization 
process of the Lavender game engine

Somethings are marked as "configurable" this means the
editor_map.json file in the project's ./assets directory
has a configuration field bearing the value of the
described property.

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
its bottom to the top of the Messags HUD.

The fields of properties are updated based on selected object.
The fields of properties for a selected object are determined
by section 3.

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

When resizing the Messages HUD, ensure the input is consumed
and does not propgate to the workspace.

The Message HUD is anchored to the bottom of the editor window
and anchored to the left and right sides of the window.

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

See core/source/world/global_space_manager.c
for implementation suggestions on memory management
of global spaces.

See core/source/world/local_space_manager.c
for implementation suggestions on chunk rendering
of global spaces (note it is local_space_manager
because local_space nodes point to global_space
nodes, and have additional overhead data to associate
adjacent local_spaces.)

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

## 3.1 Global_Space

No notes.

## 3.1.2 Chunk

### 3.1.2.1 Tile

Pay VERY close attention to the Tile memory footprint
it is VERY MUCH NOT TRIVIAL.

Look at ./examples/template-files/include/types/implemented/world/tile.h
Look at ./examples/template-files/include/types/implemented/world/tile_layer.h
Look at ./examples/template-files/include/types/implemented/world/tile_kind.h
Look at ./examples/template-files/include/types/implemented/world/tile_cover_kind.h
Look at ./examples/template-files/source/world/implemented/world/tile_logic_table__cover.c
Look at ./examples/template-files/source/world/implemented/world/tile_logic_table__ground.c
Look at ./examples/template-files/source/world/implemented/world/tile_logic_table_registrar.c

## 3.1.3 Entity

After the entire Global_Space is loaded
if the Entity does not have a matching hitbox
UUID, write an INFO message into the Message HUD:
"Entity: [UUID] lacks a Hitbox."

## 3.1.4 Inventory

No notes.

## 3.1.5 Hitbox

No notes.

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

# 6. Testing

For each python module, create unit tests to:
./tools/editors/editor_map/tests/

Prepend "test_" to the module name.

Preserve folder structure of each module relative to ./editor_map
into ./tests for example:
./tools/editors/editor_map/workspace/movement.py
-> ./tools/editors/editor_map/tests/workspace/test_movement.py

There is no integration testing at this time.
