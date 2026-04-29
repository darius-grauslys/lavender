# `<alloc_child>` — Child Element Allocation

## Overview

The `<alloc_child>` element allocates a UI element as a child of the current element (typically the current `p_ui_iterator` inside a container loop). It does not advance the parent's element index, meaning the child shares the same iteration slot as its parent.

## 1. Attributes

`<alloc_child>` has no attributes of its own. It uses the parent context for positioning.

## 2. Generated C Output

```c
p_ui_iterator_child = allocate_ui_element_from__ui_manager_as__child(p_game, p_gfx_window, p_ui_manager, p_ui_iterator);
```

After allocation, `p_ui_iterator_child` becomes the active element for child initializer processing.

## 3. Child Processing

Direct children of `<alloc_child>` (e.g., `<draggable>`, `<button>`) initialize the child element. The context's `p_ui_element` is temporarily set to `p_ui_iterator_child`.

## 4. Example

```xml
<allocate_ui_container size="3" stride__x="24">
    <drop_zone width="23" height="27" color="55,55,96"
        m_Receive_Drop_Handler="m_ui_drop_zone__receive_drop_handler__inventory_slot"/>
    <alloc_child>
        <draggable width="18" height="22" color="196,64,64"/>
    </alloc_child>
</allocate_ui_container>
```

Each of the 3 drop zones gets a draggable child element.
