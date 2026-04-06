# 16 Specification: core/include/ui/ui_text_box.h

## 16.1 Overview

Specializes a `UI_Element` as an editable text box. Extends `UI_Text` with
click-to-focus and typed input handling. Supports numeric-only and
alphanumeric-only input filters.

## 16.2 Dependencies

- `defines.h` (for `UI_Element`, `Typer`, `Font`)
- `defines_weak.h` (forward declarations)
- `ui/ui_text.h` (for text manipulation functions, delegated to)

## 16.3 Functions

### 16.3.1 Initialization

| Function | Signature | Description |
|----------|-----------|-------------|
| `initialize_ui_element_as__text_box_with__const_c_str` | `(UI_Element*, Font*, const char*, Quantity__u32) -> void` | Initializes with borrowed const string. |
| `initialize_ui_element_as__text_box_with__pM_c_str` | `(UI_Element*, Font*, char*, Quantity__u32) -> void` | Initializes with owned string. Takes ownership. |
| `initialize_ui_element_as__text_box_with__buffer_size` | `(UI_Element*, Font*, Quantity__u32) -> void` | Initializes with internally allocated buffer. |

### 16.3.2 Handlers

| Function | Signature | Description |
|----------|-----------|-------------|
| `m_ui_element__compose_handler__text_box` | `(UI_Element*, Game*, Graphics_Window*) -> void` | Compose handler for text boxes. |
| `m_ui_element__clicked_handler__text_box` | `(UI_Element*, Game*, Graphics_Window*) -> void` | Sets focus to this text box on click. |
| `m_ui_element__typed_handler__text_box` | `(UI_Element*, Game*, Graphics_Window*, unsigned char) -> void` | Default typed handler — accepts all printable characters. |
| `m_ui_element__typed_handler__text_box__numeric` | `(UI_Element*, Game*, Graphics_Window*, unsigned char) -> void` | Typed handler that only accepts numeric characters. |
| `m_ui_element__typed_handler__text_box__alphanumeric` | `(UI_Element*, Game*, Graphics_Window*, unsigned char) -> void` | Typed handler that only accepts alphanumeric characters. |

### 16.3.3 Delegate Functions (static inline)

All are thin wrappers that delegate to the corresponding `ui_text.h` function:

| Function | Delegates To |
|----------|-------------|
| `set_c_str_of__ui_text_box_with__const_c_str` | `set_c_str_of__ui_text_with__const_c_str` |
| `set_c_str_of__ui_text_box_with__pM_c_str` | `set_c_str_of__ui_text_with__pM_c_str` |
| `buffer_c_str_of__ui_text_box` | `buffer_c_str_of__ui_text` |
| `clear_c_str_of__ui_text_box` | `clear_c_str_of__ui_text` |
| `set_cursor_of__ui_text_box` | `set_cursor_of__ui_text` |
| `append_symbol_into__ui_text_box` | `append_symbol_into__ui_text` |
| `append_c_str_into__ui_text_box` | `append_c_str_into__ui_text` |
| `insert_c_str_into__ui_text_box` | `insert_c_str_into__ui_text` |
| `get_p_const_c_str_text_of__ui_text_box` | `get_p_const_c_str_text_of__ui_text` |
| `get_p_typer_of__ui_text_box` | `get_p_typer_of__ui_text` |

## 16.4 Agentic Workflow

### 16.4.1 Usage Pattern

Text boxes extend text elements with input handling. The click handler sets
focus, and the typed handler processes keyboard input. Use the typed handler
variants to restrict input to numeric or alphanumeric characters.

### 16.4.2 Preconditions

- All functions require non-null `p_ui_text_box`.

## 16.5 Header Guard

`UI_TEXT_BOX_H`
