# Specification: core/include/ui/ui_text.h

## Overview

Specializes a `UI_Element` as a read-only text display. Text elements render
a string using a `Font` and `Typer` for layout. The text buffer can be a
const string, a mutable owned string, or an internally allocated buffer.

## Dependencies

- `defines.h` (for `UI_Element`, `Typer`, `Font`)
- `defines_weak.h` (forward declarations)

## Types

### Text-Specific Data (union members in UI_Element)

    struct {
        Typer typer;
        char *pM_char_buffer;
        Quantity__u32 size_of__char_buffer;
        Index__u32 index_of__cursor_in__char_buffer;
    };

| Field | Type | Description |
|-------|------|-------------|
| `typer` | `Typer` | Text rendering layout engine. |
| `pM_char_buffer` | `char*` | Text string (may be const-cast or owned). |
| `size_of__char_buffer` | `Quantity__u32` | Length of the text. |
| `index_of__cursor_in__char_buffer` | `Index__u32` | Cursor position. Not to be confused with typer's cursor which is for rendering only. |

## Functions

### Initialization

| Function | Signature | Description |
|----------|-----------|-------------|
| `initialize_ui_element_as__text_with__const_c_str` | `(UI_Element*, Font*, const char*, Quantity__u32) -> void` | Initializes with a borrowed const string. Element does NOT own the string. |
| `initialize_ui_element_as__text_with__pM_c_str` | `(UI_Element*, Font*, char*, Quantity__u32) -> void` | Initializes with an owned mutable string. Takes ownership. |
| `initialize_ui_element_as__text_with__buffer_size` | `(UI_Element*, Font*, Quantity__u32) -> void` | Initializes with an internally allocated buffer. |

### Text Manipulation

| Function | Signature | Description |
|----------|-----------|-------------|
| `set_c_str_of__ui_text_with__const_c_str` | `(UI_Manager*, UI_Element*, const char*, Quantity__u32) -> void` | Sets text from const string. Marks manager dirty. |
| `set_c_str_of__ui_text_with__pM_c_str` | `(UI_Manager*, UI_Element*, char*, Quantity__u32) -> void` | Sets text from owned string. Marks manager dirty. |
| `buffer_c_str_of__ui_text` | `(UI_Manager*, UI_Element*, Quantity__u32) -> void` | Allocates a new buffer of the given size. Marks manager dirty. |
| `clear_c_str_of__ui_text` | `(UI_Manager*, UI_Element*) -> void` | Clears the text. Marks manager dirty. |
| `set_cursor_of__ui_text` | `(UI_Element*, Index__u32) -> void` | Sets cursor position. |
| `append_symbol_into__ui_text` | `(UI_Manager*, UI_Element*, char) -> void` | Appends a single character. Marks manager dirty. |
| `append_c_str_into__ui_text` | `(UI_Manager*, UI_Element*, const char*, Quantity__u32) -> void` | Appends a string. Marks manager dirty. |
| `insert_c_str_into__ui_text` | `(UI_Manager*, UI_Element*, const char*, Quantity__u32, Index__u32) -> void` | Inserts a string at the given index. Marks manager dirty. |

### Handlers

| Function | Signature | Description |
|----------|-----------|-------------|
| `m_ui_element__compose_handler__text` | `(UI_Element*, Game*, Graphics_Window*) -> void` | Compose handler for text elements. |
| `m_ui_element__transformed_handler__text` | `(UI_Element*, Hitbox_AABB*, Vector__3i32, Game*, Graphics_Window*) -> void` | Transformed handler for text elements. |
| `m_ui_element__transformed_handler__text__centered` | `(UI_Element*, Hitbox_AABB*, Vector__3i32, Game*, Graphics_Window*) -> void` | Variant that centers text within bounds. |
| `m_ui_element__dispose_handler__text` | `(UI_Element*, Game*, Graphics_Window*) -> void` | Dispose handler for text elements. Frees owned buffers. |

### Accessors (static inline)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `get_p_const_c_str_text_of__ui_text` | `(UI_Element*, Quantity__u32*) -> const char*` | `const char*` | Returns text string. Writes size to `*p_OUT_size_of__text`. |
| `get_p_typer_of__ui_text` | `(UI_Element*) -> Typer*` | `Typer*` | Returns pointer to the typer. |

## Agentic Workflow

### Preconditions

- All functions require non-null `p_ui_text`.

### Relationships

- `UI_Text_Box` (see `ui_text_box.h`) extends this with input handling.

## Header Guard

`UI_TEXT_H`
