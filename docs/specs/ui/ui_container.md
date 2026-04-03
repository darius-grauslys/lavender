# UI Container Specification

## File
`core/include/ui/ui_container.h`

## Purpose
Provides functions to use a `UI_Element` as a container — a logical grouping
mechanism that holds a fixed-size array of child `UI_Element` values
(`UI_Container_Entries`).

## Dependencies
| Header       | Purpose                              |
|--------------|--------------------------------------|
| `defines.h`  | `UI_Element`, `UI_Container_Entries` |

## Types

### `UI_Container_Entries` (defined in `defines.h`)
