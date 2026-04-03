# UI Text Box Specification

## File
`core/include/ui/ui_text_box.h`

## Purpose
Specializes a `UI_Element` as an editable text box. Extends `UI_Text` with
click-to-focus and typed input handling. Supports numeric-only and
alphanumeric-only input filters.

## Dependencies
| Header | Purpose |
|--------|---------|
| `defines.h` | `UI_Element`, `Typer`, `Font` |
| `defines_weak.h` | Forward declarations |
| `ui/ui_text.h` | Text manipulation functions (delegated to) |

## Functions

### Non-Inline Initialization Functions

#### `initialize_ui_element_as__text_box_with__const_c_str`
