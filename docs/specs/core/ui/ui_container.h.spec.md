# Specification: core/include/ui/ui_container.h

## Overview

Provides functions to use a `UI_Element` as a container — a logical grouping
mechanism that holds a fixed-size array of child `UI_Element` values
(`UI_Container_Entries`).

## Dependencies

- `defines.h` (for `UI_Element`, `UI_Container_Entries`)

## Types

### UI_Container_Entries (typedef)

    #define UI_CONTAINER_PTR_ENTRIES_MAXIMUM_QUANTITY_OF 8
    typedef UI_Element UI_Container_Entries[
        UI_CONTAINER_PTR_ENTRIES_MAXIMUM_QUANTITY_OF];

A fixed-size array of `UI_Element` values used as container storage.

## Functions

| Function | Signature | Description |
|----------|-----------|-------------|
| `initialize_ui_element_as__container` | `(UI_Element*, UI_Container_Entries*) -> void` | Configures a `UI_Element` to act as a container backed by the given entries. |
| `remove_all_ui_elements_from__ui_container` | `(UI_Element*) -> void` | Removes all child elements from the container. |
| `add_ui_element_to__ui_container` | `(UI_Element*) -> void` | Adds a UI element to the container. **Note:** signature does not include the element to add — may be a header declaration error or determined from internal state. |

## Agentic Workflow

### Usage Pattern

Containers are a specialized usage of `UI_Element`. Container entries are a
flat array, not using the linked-list (`p_next`/`p_child`) traversal of the
standard UI element tree.

### Preconditions

- All functions require non-null `p_ui_container`.

## Header Guard

`UI_CONTAINER_H`
