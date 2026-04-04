# Specification: core/include/ui/ui_button.h

## Overview

Specializes a `UI_Element` as a button. Buttons support click handling and
optional toggle behavior (toggleable buttons maintain an on/off state).

## Dependencies

- `defines.h` (for `UI_Element`, `UI_Button_Flags__u8`)
- `defines_weak.h` (forward declarations)

## Types

### UI_Button_Flags__u8 (u8)

| Flag | Bit | Description |
|------|-----|-------------|
| `UI_BUTTON_FLAGS__BIT_IS_TOGGLEABLE` | 0 | Button supports toggle. |
| `UI_BUTTON_FLAGS__BIT_IS_TOGGLED` | 1 | Button is currently toggled on. |

Stored in `UI_Element.ui_button_flags` (union member active when kind is
`UI_Element_Kind__Button`).

## Functions

### Initialization

| Function | Signature | Description |
|----------|-----------|-------------|
| `initialize_ui_element_as__button` | `(UI_Element*, m_UI_Clicked, bool toggleable, bool toggled) -> void` | Initializes as button. Sets kind to `UI_Element_Kind__Button`. Sets click and held handlers. |

### Default Handlers

| Function | Signature | Description |
|----------|-----------|-------------|
| `m_ui_button__clicked_handler__default` | `(UI_Element*, Game*, Graphics_Window*) -> void` | Default click handler. If toggleable, toggles state. |
| `m_ui_button__held_handler__default` | `(UI_Element*, Game*, Graphics_Window*) -> void` | Default held handler. |

### Toggle Queries (static inline)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `is_ui_button__toggleable` | `(UI_Element*) -> bool` | `bool` | True if toggleable flag set. |
| `is_ui_button__toggled` | `(UI_Element*) -> bool` | `bool` | True if toggled flag set. |

### Toggle Mutations (static inline)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `set_ui_button_as__toggleable` | `(UI_Element*) -> void` | `void` | Sets toggleable flag. |
| `set_ui_button_as__toggled` | `(UI_Element*) -> void` | `void` | Sets toggled flag. |
| `set_ui_button_as__untoggled` | `(UI_Element*) -> void` | `void` | Clears toggled flag. |
| `set_ui_button_as__non_toggleable` | `(UI_Element*) -> void` | `void` | Clears toggleable AND toggled flags. |
| `set_ui_button_as__toggled_or__not_toggled` | `(UI_Element*, bool) -> void` | `void` | Sets or clears toggled based on bool. |
| `set_ui_button_as__toggleable_or__non_toggleable` | `(UI_Element*, bool) -> void` | `void` | Sets or clears toggleable based on bool. |
| `toggle_ui_button` | `(UI_Element*) -> bool` | `bool` | Flips toggle state. Returns new state (true = toggled). |

## Agentic Workflow

### Usage Pattern

    UI_Element *p_button = allocate_ui_element_from__ui_manager(p_ui_manager);
    initialize_ui_element_as__button(
        p_button, my_click_handler, true, false);
    allocate_hitbox_for__ui_element(
        p_game, p_gfx_window, p_button, 32, 32, position);

### Preconditions

- All functions require non-null `p_ui_button`.
- Element must have been allocated from a `UI_Manager`.

## Header Guard

`UI_BUTTON_H`
