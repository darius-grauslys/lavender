# `<grid>` — Repeated Row Layout

## Overview

The `<grid>` element repeats its child elements a specified number of times, applying stride offsets per iteration. It is used to create uniform grids of UI elements (e.g., inventory rows). Unlike `<group>`, `<grid>` has a `size` attribute controlling repetition count and links rows together via `p_next` pointer chains in the generated C code.

## 1. Attributes

| Attribute | Required | Default | Description |
|---|---|---|---|
| `x` | No | `0` | Horizontal offset in pixels from parent context. |
| `y` | No | `0` | Vertical offset in pixels from parent context. |
| `stride__x` | No | `0` | Horizontal stride per grid iteration. |
| `stride__y` | No | `0` | Vertical stride per grid iteration. |
| `size` | No | `1` | Number of times to repeat the child elements. |
| `name` | No | Not set | If provided, a `#define` index constant is emitted in the `.h` file. |

## 2. Behavior

### 2.1. Iteration

The child elements are instantiated `size` times. Each iteration advances the position by `(stride__x, stride__y)`.

### 2.2. Row Linking

After each iteration (except the first), the generated C code links the previous row's last element to the current row's first element via `p_next` pointer assignment using `get_p_ui_element_by__index_from__ui_manager`.

### 2.3. Element Count Propagation

The total element count from all iterations is propagated to the parent context.

## 3. Generated C Pattern

For each iteration beyond the first:

```c
p_ui_iterator_previous_previous->p_next = get_p_ui_element_by__index_from__ui_manager(p_ui_manager, <last_index>);
p_ui_iterator_previous_previous = p_ui_iterator_previous;
```

## 4. Example

```xml
<grid x="44" y="15" size="9" stride__y="28" name="p_inventory_column">
    <allocate_ui_container size="3" stride__x="24">
        <drop_zone width="23" height="27" color="55,55,96"
            m_Receive_Drop_Handler="m_ui_drop_zone__receive_drop_handler__inventory_slot"/>
    </allocate_ui_container>
</grid>
```

Creates 9 rows of 3 drop zones each, spaced 28px vertically and 24px horizontally.
