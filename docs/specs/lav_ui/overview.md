# UI XML Specification — Overview

This specification describes the XML format used by `ui_builder.py` to generate C source (`.c`) and header (`.h`) files for a UI system. Each XML file declares a UI window layout: its includes, output paths, background layers, and a tree of UI elements (buttons, sliders, drop zones, draggables, grids, groups, containers, and inline C code).

## When to Use This Specification

An agent should consult these specs when:

- Creating a new UI window XML file for C code generation.
- Modifying the layout, elements, or behavior of an existing UI window.
- Understanding how XML attributes map to generated C function calls.
- Debugging generated C output or resolving missing symbol/field errors.

## File Structure

Every XML file has a `<root>` element containing exactly two children:

1. `<config>` — Declares includes, output paths, platform target, backgrounds, and function signature mappings. See `attribute_config.md`.
2. `<ui>` — Declares the element tree and code generation entry point. See `attribute_ui.md`.

## Element Reference

| Element | Spec File | Purpose |
|---|---|---|
| `<config>` | `attribute_config.md` | Build configuration, includes, outputs |
| `<ui>` | `attribute_ui.md` | Root UI element container |
| `<group>` | `attribute_group.md` | Logical grouping with positional offset |
| `<grid>` | `attribute_grid.md` | Repeated row layout |
| `<allocate_ui>` | `attribute_allocate_ui.md` | Single UI element allocation |
| `<allocate_ui_container>` | `attribute_allocate_ui_container.md` | Sequential multi-element allocation with loop |
| `<alloc_child>` | `attribute_alloc_child.md` | Child element allocation on current element |
| `<button>` | `attribute_button.md` | Button initialization |
| `<slider>` | `attribute_slider.md` | Slider initialization |
| `<draggable>` | `attribute_draggable.md` | Draggable element initialization |
| `<drop_zone>` | `attribute_drop_zone.md` | Drop zone initialization |
| `<text_cstr>` | `attribute_text_cstr.md` | Static text label initialization |
| `<text_box>` | `attribute_text_box_buffer_sized.md` | Text box with buffer initialization |
| `<window_element>` | `attribute_window_element.md` | Sub-window element initialization |
| `<background>` | `attribute_background.md` | Background element initialization |
| `<code>` | `attribute_code.md` | Inline C code injection |

## Conventions

- All `__` prefixed attribute values are internal/editor-only and must be disregarded by agents.
- Positions (`x`, `y`) are in pixel coordinates, top-left origin.
- Colors are `"R,G,B"` tuples (0–255).
- Named elements produce `#define` index constants in the `.h` file.
- The `$name` syntax inside `<code>` blocks resolves to the `#define` index of a named element.
