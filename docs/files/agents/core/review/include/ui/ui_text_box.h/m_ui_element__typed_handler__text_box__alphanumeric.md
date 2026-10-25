# m_ui_element__typed_handler__text_box__alphanumeric

**File of origin:** `core/source/ui/ui_text_box.c`

## Semantic

Typed handler for a UI text box that filters input to accept only alphanumeric characters (digits 0-9, lowercase letters a-z, uppercase letters A-Z). Special symbols (backspace, delete, escape, etc.) are delegated to `handle_special_symbols__text_box`. Non-matching symbols are silently discarded.

## Pre-conditions

1. `p_this_ui_text_box` must be a valid, initialized `UI_Element` of kind `UI_Element_Kind__Text_Box` with a valid `pM_char_buffer` and `size_of__char_buffer`.
2. `p_game` must be a valid, non-null `Game` pointer.
3. `p_graphics_window` must be a valid, non-null `Graphics_Window` pointer from which a `UI_Manager` can be retrieved via `get_p_ui_manager_from__graphics_window`.
4. `symbol` is an `unsigned char` representing the typed character.

## Post-conditions

1. If `symbol` is a special control character (carriage return, line feed, escape, backspace, delete, arrow keys), the corresponding special symbol handler is invoked and the function returns early.
2. If `symbol` is not an alphanumeric character, the function returns early without modifying the text box.
3. If `symbol` is an alphanumeric character, it is appended to the text box's character buffer via `append_symbol_into__ui_text_box`, which increments `index_of__cursor_in__char_buffer` and marks the UI manager as dirty.

## Correctness Verdict

**Incorrect**

## Semantic Alignment

The function's semantic intent is to accept only alphanumeric characters (digits, lowercase letters, uppercase letters). However, the implementation uses **strict** inequalities (`>` and `<`) instead of **inclusive** inequalities (`>=` and `<=`), causing it to reject the boundary characters of each range.

The filtering condition is:
```c
if (!((symbol > '0' && symbol < '9')
            || (symbol > 'a' && symbol < 'z')
            || (symbol > 'A' && symbol < 'Z'))) {
    return;
}
```

This means:
- `'0'` (digit zero) is **rejected** — `symbol > '0'` is false
- `'9'` (digit nine) is **rejected** — `symbol < '9'` is false
- `'a'` (lowercase a) is **rejected** — `symbol > 'a'` is false
- `'z'` (lowercase z) is **rejected** — `symbol < 'z'` is false
- `'A'` (uppercase A) is **rejected** — `symbol > 'A'` is false
- `'Z'` (uppercase Z) is **rejected** — `symbol < 'Z'` is false

Only the characters strictly between the boundaries are accepted (e.g., '1'-'8', 'b'-'y', 'B'-'Y').

Compare with the sibling function `m_ui_element__typed_handler__text_box__numeric`, which correctly uses inclusive bounds:
```c
if (symbol < '0' || symbol > '9')
    return;
```

The correct condition should be:
```c
if (!((symbol >= '0' && symbol <= '9')
            || (symbol >= 'a' && symbol <= 'z')
            || (symbol >= 'A' && symbol <= 'Z'))) {
    return;
}
```

This is an off-by-one bug that prevents users from typing the boundary alphanumeric characters.

## Implementation Correctness

- **Type compatibility:** All parameter types match the function signature and target field types. The `unsigned char symbol` parameter is compatible with the `char symbol` parameter of `append_symbol_into__ui_text`. No implicit conversions or truncation issues.
- **Undefined behavior:** No pointer dereferences without null checks are introduced by this function itself; it relies on the caller to pass valid pointers. The `get_p_ui_manager_from__graphics_window` call is assumed to return a valid pointer given valid inputs. No array out-of-bounds access within this function.
- **Validation:** The special symbol handling is delegated to `handle_special_symbols__text_box`, which is appropriate. The alphanumeric filtering is the function's own responsibility, and while the validation logic is present, it is incorrect due to the off-by-one error described above.

## Side Effects

1. May invoke special symbol handlers (e.g., backspace, delete, escape) which mutate the text box's character buffer and cursor position.
2. If the symbol is alphanumeric, calls `append_symbol_into__ui_text_box`, which:
   - Marks the `UI_Manager` as dirty via `set_ui_manager_as__dirty`.
   - Writes the symbol to `pM_char_buffer[index_of__cursor_in__char_buffer]` and increments `index_of__cursor_in__char_buffer`.
