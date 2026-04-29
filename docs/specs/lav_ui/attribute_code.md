# `<code>` — Inline C Code Injection

## Overview

The `<code>` element injects raw C code directly into the generated `.c` file at the current position in the element tree. It supports symbol resolution for named UI element indices and format-string substitution for the current element name.

## 1. Attributes

`<code>` has no XML attributes. Its content is the text body of the element.

## 2. Text Body

The text content of the `<code>` element is split by newlines (leading whitespace stripped per line) and emitted as C statements.

### 2.1. Symbol Resolution with `$`

Any token prefixed with `$` is resolved to the `#define` index constant of the named UI element, wrapped for offset arithmetic:

```
$p_inventory_column
```

Becomes:

```c
(UI_WINDOW__GAME__EQUIP_P_INVENTORY_COLUMN_<id> + index_of__ui_element_offset__u16)
```

The symbol must reference a `name` attribute declared earlier in the same XML file (on `<allocate_ui>`, `<allocate_ui_container>`, `<grid>`, or `<group>`).

### 2.2. Format String `{0}`

The placeholder `{0}` in code text is replaced with the current context's `p_ui_element` name (e.g., `p_ui_iterator` or a named element variable).

## 3. Generated C Output

Each non-empty line is emitted with appropriate indentation:

```c
    allocate_ui_for__ui_window__game__hud(p_gfx_context, p_gfx_window, p_game, p_ui_manager, index_of__ui_element_offset__u16);
    toggle_ui_button(get_p_ui_element_by__index_from__ui_manager(p_ui_manager, 0));
```

## 4. Example

```xml
<code>
    allocate_ui_for__ui_window__game__hud(p_gfx_context, p_gfx_window, p_game, p_ui_manager, index_of__ui_element_offset__u16);
    toggle_ui_button(get_p_ui_element_by__index_from__ui_manager(p_ui_manager, 0));
</code>
```

```xml
<code>
    set_ui_element__p_data(
        p_ui_iterator,
        get_p_ui_element_by__index_from__ui_manager(
            p_ui_manager,
            $p_inventory_column));
</code>
```
