# `<group>` — Logical Grouping

## Overview

The `<group>` element creates a positional context for its children without allocating any UI element itself. It offsets all descendant positions and optionally applies stride for sequential children. Groups can be nested.

## 1. Attributes

| Attribute | Required | Default | Description |
|---|---|---|---|
| `x` | No | `0` | Horizontal offset in pixels, added to the parent context's position. |
| `y` | No | `0` | Vertical offset in pixels, added to the parent context's position. |
| `stride__x` | No | `0` | Horizontal stride in pixels applied per sequential child element. |
| `stride__y` | No | `0` | Vertical stride in pixels applied per sequential child element. |
| `name` | No | Not set | If provided, a `#define` index constant is emitted in the `.h` file for the current element ID. |

## 2. Behavior

### 2.1. Context Stacking

A new context is pushed onto the context stack with the computed `x`, `y`, `stride__x`, and `stride__y`. All children inherit this context. The context is popped after all children are processed.

### 2.2. Child Processing

Each direct child element is processed in document order via the signature dispatch system. A newline is emitted between children in the generated C source.

### 2.3. Element Count Propagation

The total number of elements allocated by children is propagated upward to the parent context's `quantity_of__sub_elements`.

## 3. Generated C Output

`<group>` itself generates no C function calls. It only affects the positional arithmetic of its descendants.

## 4. Example

```xml
<group x="52" y="72" stride__y="44">
    <allocate_ui name="p_button__a">
        <button width="80" height="24"/>
    </allocate_ui>
    <allocate_ui name="p_button__b">
        <button width="80" height="24"/>
    </allocate_ui>
</group>
```

The first button is at `(52, 72)`, the second at `(52, 116)` due to `stride__y="44"`.
