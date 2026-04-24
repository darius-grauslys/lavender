# Overview

editor_ui.py is a python script used for modifying .xml files
in a graphical and interactive manner.

It is important to review ./tools/tool-invocation-spec.md before
attempting to implement this file.

It is important to review ./tools/ui_builder.py (LEGACY)
for a historical understanding of the ui visualizer.

It is important to review ./tools/gen_ui.py for a
modern but untested implementation by AI on the
ui generation.

It is important to review tool_ui_viewer.py for a
modern but untested implementation by AI on the
ui visualization.

Any python tech stack for UI and tool imeplementation is permited.
The more stable and popular the better.

# 1. Work Area

The work area is the interactive cursor and arrow key spannable
space beneath the UI HUDs.

It is a 8x8 pixel grid with the grid size defined in the .xml file.

UI elements snap to the 8x8 grid.
UI elements are highlighted in a 3 pixel wide border when
clicked on. When clicked on UI elements will have a X on
the top right of the UI element within the purple border
when clicked, the UI element will be removed from the .xml.tmp file
per section 2.2. The purple outline border is shaped to the
UI element dimensions specified in the .xml file.

When a UI element is clicked on, the properties HUD will be
updated with the UI element .xml.tmp properties. These properties
can be edited and will automatically update the view and .xml.tmp
when changed.

When CTRL-F is held, ALL UI elements will have their purple
outlines revealed, and during this mode, whenever a UI element
is focused (hovered by mouse) it will change its purple outline
to a bright red one. It will revert back to purple when focus is
lost. This functionality is to determine ui bounding boxes.

A Undo/Redo system of 128 historical ring buffer records
will be kept. When undoing, if a new historical record is made
all possible redos prior to the new record are invalidated
and will be overwritten by new records.

Setting the properties of a UI element per section 5 is redo/undoable
Creation and deletion of UI elements are redo/undoable

## 1.1 Zoom and Pan

The work area supports zoom and pan:

* **Ctrl + Mouse Wheel** or **Ctrl + Up/Down Arrow**: Zoom in/out
  (range 0.125× to 8×).
* **Mouse Wheel**: Pan vertically.
* **Shift + Mouse Wheel**: Pan horizontally.
* **Arrow Keys** (without Ctrl): Pan in the corresponding direction.

Zoom is centered on the current view origin. All element positions,
grid lines, backgrounds, and drag-create previews scale with the
zoom factor.

## 1.2 Creating UI_Elements

(Previously section 1.1)

See section 4 on the tool selection of UI elements.

when a UI tool is selected, the work space will 
accept single click and click and drag.
If the UI tool is configured to function in a 1x1 tile
space (8x8 pixels) single click will spawn a .xml.tmp element
configured by the tool, with position set to the area clicked.

When a UI tool is click-and-dragged 8x8 pixel tiles will be selected
as the span of that UI element, and when released will be saved
to the .xml.tmp file per section 2.2.

If the tool does not support 1x1 tile, and the bounding box of click
and drag only covers a 1x1 section, the ui element will not be made.
No error is written to message hud for this.

### 1.2.1 Span generation

The underlying workspace will render the the UI_Span defined by
the TOOL section 4. Going off of the bounding box defined in
.xml.tmp for the ui element generated, the UI span selection will
be rendered. If the ui bounding box covers 1x1 and the tool supports
1x1 spanning, then the 1x1 UI tileset selection configured in the tool
will be used to render onto the work space.

If the bounding box covers 2x2 tiles, the first ui tileset selection
is the top left, the 3rd is the top right, the 7th is bottom left
and the 9th is bottom right.

If th ebounding box covers NxN tiles where N>=3 then the corners
are set per 2x2 rule, and the top edge is the 2nd ui tileset selection
the left edge is the 4th, the right edge is the 6th and the bottom edge
is the 8th. The center space is filled with the 5th selection.

# 2. Left hand file HUD navigator.

This UI space should be expandable and overlayed over the work area.
This UI space will have a complete file tree view with collapsable
directories. The file tree will be rooted to:
./assets/ui

## 2.1 open .png
If a .png file is clicked, the work space will be a READONLY
view of the .png file.

## 2.2 .xml
If a .xml file is clicked, the work space will be a
construction of the xml. If construction fails, a log of errors
will be displayed in the Message HUD section 3.

Errors will be written ot the Message HUD as an ERROR message.

When a .xml is being viewed, it is actively written to a .xml.tmp
file. If a .xml is being viewed and a .xml.tmp file already exists
then the .xml.tmp file will be used.

When the file is saved with CTRL+S the contents of .xml.tmp will
be written to .xml

Saving will be written to the Message HUD as an INFO message.

# 3. Collapsable bottom Message HUD

The message HUD is collapsable if the title bar of it is clicked.
When collapsed only the title bar will be visible and when clicked it will
uncollapse the message HUD.

The message HUD will have a scroll bar, and accept mouse wheel input
(when cursor is hovering over) and arrow key input (when focused) to scroll.

INFO messages have no background and the text is black.
ERROR messages have a dark red background and the text is white.

# 4. Top Right hand TOOL hud.

The TOOL hud takes 50% of the vertical space shared
with the properties hud

The tool hud is populated based on a tools.json file found
in:
./assets/ui/tools.json

If the file is missing, there are no existing tools for the project.
Tools should be generated with empty UI spans for each of the UI elements
supported in the UI editor see: ./tools/gen_ui_elements/widgets.py

## 4.1 UI Span

Each tool has a configurable UI_Span.

When a tool is clicked, the properties window will reveal
the UI_Span configuration of that tool.

The UI_Span has a checkmarkable toggle of 1x1 tile support
The UI_Span has a checkmarkable toggle of NxN tile support.

All toggles are off by default.

When on, if there is no saved record of configuration in
tools.json the ui tile indices for the spans will be the
0 index of the ui tileset indices.

### 4.1.1 UI Tileset Selection on UI Span

1x1 tile support will have 1 ui tileset index option
NxN tile support will have 9 ui tileset index options

The 1x1 selection will be above the 9x9 selection.

Every selection is a button with a tile index as its title.
and the background of the buttom is the 8x8 pixel segment of
the ui tileset corresponding to the UI tile selected.

When the button is clicked, a pop up window will appear of
the UI tileset (default tileset per tool-invocation.md at this time.)

When the UI tileset is clicked, the corresponding tile clicked will
be used to set the index of that UI span selection button.

Changes made are automatically saved to tools.json

# 5. Bottom Right hand Properties hud.

The Properties hud takes 50% of the vertical space shared
with the TOOL hud.

The properties space is filled as needed as described by other sections.
There should be property fill and update-respose strategies for each
widget supported.
