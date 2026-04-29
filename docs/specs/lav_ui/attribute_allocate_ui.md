# `<allocate_ui>` — Single UI Element Allocation

## Overview

The `<allocate_ui>` element allocates a single UI element from the UI manager. It serves as a wrapper that creates the element, then processes its children (typically a single initializer like `<button>`, `<slider>`, etc.) to configure the element.

## 1. Attributes

| Attribute | Required | Default | Description |
|---|---|---|---|
| `x` | No | `0` | Horizontal offset in pixels from parent context. |
| `y` | No | `0` | Vertical offset in pixels from parent context. |
| `name` | No | Not set | If provided, the allocated element is stored in a named local `UI_Element *<name>` variable, and a `#define` index constant is emitted in the `.h` file. If omitted, the element is assigned to the shared `p_ui_iterator` variable. |

## 2. Generated C Output

### 2.1. With `name`

```c
UI_Element *p_button__singleplayer = allocate_ui_element_from__ui_manager(p_ui_manager);
```

### 2.2. Without `name`

```c
p_ui_iterator = allocate_ui_element_from__ui_manager(p_ui_manager);
```

## 3. Child Processing

All direct children are processed after allocation. Typically one initializer child (e.g., `<button>`, `<slider>`, `<drop_zone>`, `<draggable>`, `<window_element>`) configures the allocated element.

## 4. Element ID Advancement

After processing, the current element ID advances by the parent context's `quantity_of__elements` (typically 1 for a single `<allocate_ui>`).

## 5. Example

```xml
<allocate_ui x="128" y="28" name="p_button_setting__resume">
    <button width="104" height="32" color="64,196,64"/>
</allocate_ui>
```
