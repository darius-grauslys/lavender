# `<config>` — Build Configuration

## Overview

The `<config>` element is the first child of `<root>`. It declares all build-time metadata: which C headers to include in generated output, where to write the `.c` and `.h` files, platform targeting for the visual editor, background image layers, and the function signature mappings that drive deterministic code generation.

## 1. `<include>` — Header Includes

The `<include>` element declares C headers that will appear as `#include <...>` directives at the top of the generated `.c` file.

### 1.1. Attributes

| Attribute | Required | Description |
|---|---|---|
| `sub_dir` | Yes | The subdirectory path within the `include/` folder where the generated `.h` file conceptually lives. Used to construct the self-include at the top of the `.c` file. Example: `"ui/implemented/generated/game/"` |

### 1.2. `<header>` Children

Each `<header>` child declares one include.

| Attribute | Required | Description |
|---|---|---|
| `path` | Yes | The include path as it appears in `#include <path>`. Example: `"ui/ui_element.h"` |

### 1.3. Generated Output

```c
#include <ui/implemented/generated/game/ui_window__game__equip.h>
#include <ui/ui_element.h>
#include <ui/ui_button.h>
// ... one per <header>
```

The self-include (derived from `sub_dir` + source filename + `.h`) is always inserted first, before all declared headers.

## 2. `<output>` — Output File Paths

**Mandatory.** Declares where the generated `.c` and `.h` files are written.

### 2.1. Attributes

| Attribute | Required | Default | Description |
|---|---|---|---|
| `base_dir` | No | `"./"` | Base directory prepended to `c_path` and `h_path` when writing files. |
| `c_path` | Yes | — | Relative path for the generated `.c` file. Example: `"./source/ui/implemented/generated/game/ui_window__game__equip.c"` |
| `h_path` | Yes | — | Relative path for the generated `.h` file. Example: `"./include/ui/implemented/generated/game/ui_window__game__equip.h"` |

## 3. `<platform>` — Visual Editor Configuration

This element is used exclusively by the human-driven visual UI editor (pyglet window). It is **not relevant for agentic work**.

### 3.1. Attributes

| Attribute | Description |
|---|---|
| `target` | Platform backend string, e.g. `"SDL"`. |
| `size` | Window dimensions as `"W,H"`, e.g. `"256,256"`. |

## 4. `<background>` — Background Image Layers

Declares background images for the visual editor preview. Up to 4 layers (0–3) are supported.

### 4.1. Attributes

| Attribute | Required | Default | Description |
|---|---|---|---|
| `layer` | No | Next available layer | Integer layer index (0–3). |
| `path` | Yes | — | File path to the background `.png` image. |
| `x` | No | `0` | Horizontal offset in pixels. |
| `y` | No | `0` | Vertical offset in pixels. |

## 5. `<ui_func_signature>` — Function Signature Mappings

These elements map XML element tag names to C function names used during code generation. They must be present for every element type used in the `<ui>` tree.

### 5.1. Attributes

| Attribute | Required | Description |
|---|---|---|
| `for` | Yes | The XML tag name this signature maps to. One of: `grid`, `group`, `alloc_child`, `allocate_ui`, `allocate_ui_container`, `code`, `button`, `slider`, `draggable`, `drop_zone`, `background`, `window_element`. |
| `c_signatures` | No | Comma-separated C function name(s). The first is used as the primary call. Not needed for `grid`, `group`, `code` (they use structural logic, not a single C call). |

### 5.2. Standard Signature Set

Copy this block as-is for most UI windows. Add or remove entries only if the `<ui>` tree uses or omits specific element types.

```xml
<ui_func_signature for="grid"/>
<ui_func_signature for="group"/>
<ui_func_signature for="alloc_child" c_signatures="allocate_ui_element_from__ui_manager_as__child"/>
<ui_func_signature for="allocate_ui" c_signatures="allocate_ui_element_from__ui_manager"/>
<ui_func_signature for="allocate_ui_container" c_signatures="allocate_many_ui_elements_from__ui_manager_in__succession"/>
<ui_func_signature for="code"/>
<ui_func_signature for="button" c_signatures="initialize_ui_element_as__button"/>
<ui_func_signature for="slider" c_signatures="initialize_ui_element_as__slider"/>
<ui_func_signature for="draggable" c_signatures="initialize_ui_element_as__draggable"/>
<ui_func_signature for="drop_zone" c_signatures="initialize_ui_element_as__drop_zone"/>
```

Optional additions when needed:

```xml
<ui_func_signature for="background" c_signatures="SDL_initialize_ui_element_as__background"/>
<ui_func_signature for="window_element" c_signatures="initialize_ui_element_as__window_element_and__open_window"/>
<ui_func_signature for="text_cstr" c_signatures="initialize_ui_element_as__text_with__const_c_str"/>
<ui_func_signature for="text_box" c_signatures="initialize_ui_element_as__text_box_with__buffer_size"/>
```
