# clear_c_str_of__ui_text_box

**File of origin:** `core/include/ui/ui_text_box.h`

## Semantic

Clears the character buffer of a UI text box by zeroing all bytes, effectively emptying the text content. Marks the UI manager as dirty to trigger a redraw. This is a thin static inline wrapper that delegates to `clear_c_str_of__ui_text` in `core/source/ui/ui_text.c`.

## Pre-conditions

1. `p_ui_manager` must be a valid, non-null pointer to a `UI_Manager` struct.
2. `p_ui_text_box` must be a valid, non-null pointer to a `UI_Element` struct that has been initialized as a text box (i.e., initialized via one of the `initialize_ui_element_as__text_box_with__*` functions).
3. The `UI_Element` must have a non-null `pM_char_buffer` (i.e., it must have been initialized with an allocated or owned character buffer).
4. The `UI_Element` must have a valid `size_of__char_buffer` field indicating the size of the allocated buffer.

## Post-conditions

1. All bytes in the `pM_char_buffer` of the `UI_Element` are set to zero (null bytes).
2. The UI manager is marked as dirty via `set_ui_manager_as__dirty`, triggering a redraw of the UI.
3. The `size_of__char_buffer` field remains unchanged.
4. The `pM_char_buffer` pointer itself remains unchanged (memory is not freed, only zeroed).
5. **BUG: The `index_of__cursor_in__char_buffer` field is NOT reset to 0**, despite the text content being cleared. This means subsequent `append_symbol_into__ui_text_box` or `append_c_str_into__ui_text_box` calls will write at the old cursor position rather than at position 0, leaving leading null bytes in the buffer.

## Correctness Verdict

**Incorrect**

## Semantic Alignment

The function does not fully fulfill the semantic intent of "clearing" the text box. A proper clear operation should reset the cursor position (`index_of__cursor_in__char_buffer`) to 0, since the text content has been emptied. Without resetting the cursor, the text box is in an inconsistent state: the buffer is zeroed but the cursor still points to a non-zero position. This means:

- `append_symbol_into__ui_text_box` will write the next symbol at the old cursor position (e.g., position 5), leaving positions 0-4 as null bytes. This is semantically incorrect for a "cleared" text box — the cursor should be at position 0 so new text starts from the beginning.
- `handle_special_symbol__backspace__text_box` checks `index_of__cursor_in__char_buffer == 0` to decide if backspace is a no-op. If the cursor is not reset, backspace may attempt to manipulate characters that no longer exist in the logical text.

The underlying `clear_c_str_of__ui_text` implementation (in `core/source/ui/ui_text.c`, line 217) is:
```c
void clear_c_str_of__ui_text(
        UI_Manager *p_ui_manager,
        UI_Element *p_ui_text) {
    set_ui_manager_as__dirty(p_ui_manager);
    // TODO: clamp c_str size based on config.
    memset(p_ui_text->pM_char_buffer,
            0,
            p_ui_text->size_of__char_buffer);
}
```

It zeroes the buffer but does not reset `index_of__cursor_in__char_buffer` to 0.

## Implementation Correctness

1. **Null pointer dereference / Undefined behavior**: The function does not check whether `pM_char_buffer` is NULL before calling `memset`. If the `UI_Element` was initialized via `initialize_ui_element_as__text_with__pM_c_str` with a NULL `pM_text__c_str` argument, then `pM_char_buffer` will be NULL and `size_of__char_buffer` will be 0. Calling `memset(NULL, 0, 0)` is technically undefined behavior per the C standard (C11 §7.24.6.1: "If `s` is a null pointer, or if the size of the array pointed to by `s` is less than `n`, the behavior is undefined`), even though many implementations handle it as a no-op. If `size_of__char_buffer` were ever non-zero with a NULL `pM_char_buffer`, this would be a definite crash.

2. **Missing validation**: The function performs no validation on its inputs. It does not check:
   - Whether `p_ui_manager` is NULL.
   - Whether `p_ui_text_box` is NULL.
   - Whether `pM_char_buffer` is NULL before calling `memset`.

3. **Cursor not reset**: As noted in Semantic Alignment, `index_of__cursor_in__char_buffer` is not reset to 0 after clearing. This is a semantic bug that leads to incorrect behavior when subsequent text operations are performed.

4. **Type compatibility**: Parameter types match correctly — `UI_Manager *` and `UI_Element *` are passed through without implicit conversions or truncation.

5. **The `#warning TODO: clamp c_str size based on config`** indicates the implementation is acknowledged as incomplete by the original developers, though this relates more to a feature gap than a correctness bug.

## Side Effects

1. Marks the `UI_Manager` as dirty via `set_ui_manager_as__dirty`, setting the `UI_MANAGER_FLAG__IS_DIRTY` flag. This triggers a UI redraw on the next composition cycle.
2. Modifies the `pM_char_buffer` of the `UI_Element` by zeroing all bytes (via `memset`).
3. Does NOT modify `pM_char_buffer` pointer itself (memory is not freed or reallocated).
4. Does NOT modify `size_of__char_buffer`.
5. Does NOT modify `index_of__cursor_in__char_buffer` (this is a bug — see Semantic Alignment).
