# `<allocate_ui_container>` — Sequential Multi-Element Allocation

## Overview

The `<allocate_ui_container>` element allocates multiple UI elements in succession from the UI manager and iterates over them in a generated `for` loop. Each child element is applied to every allocated element during iteration.

## 1. Attributes

| Attribute | Required | Default | Description |
|---|---|---|---|
| `x` | No | `0` | Horizontal offset in pixels from parent context. |
| `y` | No | `0` | Vertical offset in pixels from parent context. |
| `stride__x` | No | `0` | Horizontal stride per element in the container. |
| `stride__y` | No | `0` | Vertical stride per element in the container. |
| `size` | No | `1` | Number of UI elements to allocate. |
| `name` | No | Not set | If provided, a `#define` index constant is emitted in the `.h` file for the first element's ID. |

## 2. Generated C Output

### 2.1. Allocation and Loop

```c
p_ui_iterator = allocate_many_ui_elements_from__ui_manager_in__succession(p_ui_manager, <size>);
for (Index__u32 index_of__iteration__N=0; p_ui_iterator; iterate_to_next__ui_element(&p_ui_iterator), index_of__iteration__N++) {
    p_ui_iterator_previous = p_ui_iterator;
    // ... child element initialization ...
}
```

Where `N` is the context stack depth, ensuring unique loop variable names for nested containers.

### 2.2. Stride in Positioning

Inside the loop, position arguments use the iteration index as a multiplier:

```c
get_vector__3i32(
    <base_x> + <stride__x> * index_of__iteration__N,
    <base_y> + <stride__y> * index_of__iteration__N,
    0)
```

## 3. Child Processing

All children are processed inside the loop body. The `p_ui_iterator` variable points to the current element. After the loop, `p_ui_iterator_previous` holds the last element.

## 4. Example

```xml
<allocate_ui_container x="28" y="96" size="4" stride__y="24">
    <button width="16" height="12" color="64,196,64"/>
</allocate_ui_container>
```

Allocates 4 buttons spaced 24px apart vertically.
