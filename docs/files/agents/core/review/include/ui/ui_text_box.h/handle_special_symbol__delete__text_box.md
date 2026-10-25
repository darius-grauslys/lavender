# Function Review: handle_special_symbol__delete__text_box

**File of origin:** `core/source/ui/ui_text_box.c`

## Semantic

Handles the Delete key (forward delete) in a text box by removing the character at the cursor position and shifting all subsequent characters left by one. The cursor remains in place.

## Pre-conditions

1. `p_this_ui_text_box` must be a valid, non-null pointer to an initialized `UI_Element` of kind `UI_Text_Box` (or `UI_Text`), whose union member for text/text_box is active.
2. `p_this_ui_text_box->pM_char_buffer` must point to a valid allocated character buffer (or the function returns early if `size_of__char_buffer` is 0).
3. `p_this_ui_text_box->index_of__cursor_in__char_buffer` (cursor position) must be a valid index into the buffer. If it is `>= size_of__char_buffer`, the function returns early with no modification.
4. `p_this_ui_text_box->size_of__char_buffer` represents the total allocated buffer capacity (not content length). It must be greater than 0 for any deletion to occur.
5. `p_game` is accepted but unused (consistent with `handle_special_symbol__backspace__text_box`).

## Post-conditions

1. If `index_of__cursor_in__char_buffer >= size_of__char_buffer`, the function returns immediately with no modification to the buffer.
2. If `size_of__char_buffer == 0`, the function returns immediately with no modification.
3. Otherwise, the character at position `index_of__cursor_in__char_buffer` is deleted, and all characters from `index_of__cursor_in__char_buffer + 1` through `size_of__char_buffer - 1` are shifted left by one position.
4. The last position of the buffer (`pM_char_buffer[size_of__char_buffer - 1]`) is set to 0 (null terminator), ensuring the string remains properly null-terminated even when the content previously filled the entire buffer.
5. `index_of__cursor_in__char_buffer` is NOT modified — the cursor remains at the same position, which is correct for forward Delete semantics.
6. `size_of__char_buffer` is NOT modified — it represents buffer capacity, which does not change when characters are deleted.

## Correctness Verdict

Correct

## Semantic Alignment

The implementation correctly implements forward Delete (Delete key) semantics. The character at the cursor position is removed, and all characters after it are shifted left by one. The cursor remains in place, which is the expected behavior for forward delete (as opposed to backspace, which deletes the character before the cursor and decrements the cursor position).

The function is consistent with its companion `handle_special_symbol__backspace__text_box`, which handles the Backspace key by:
- Deleting the character before the cursor (at `cursor - 1`)
- Shifting characters from `cursor - 1` to `buffer_size - 2` left by one
- Decrementing the cursor position
- Null-terminating at `buffer_size - 1`

The delete function correctly does NOT decrement the cursor, since forward delete leaves the cursor in the same position (now pointing to what was previously the next character).

## Implementation Correctness

- **Type compatibility:** All field accesses use correct types. `Index__u32` and `Quantity__u32` are both `uint32_t`. The loop variable `index_of__char` is `Index__u32`, matching `index_of__cursor_in__char_buffer`. The loop bound uses `size_of__char_buffer - 1`, where `size_of__char_buffer` is `Quantity__u32`. No implicit conversions or truncation occur.
- **Undefined behavior:** No null pointer dereference (the function accesses `p_this_ui_text_box` fields; ensuring `p_this_ui_text_box` is valid is the caller's responsibility). No out-of-bounds access: the loop iterates from `cursor` to `size_of__char_buffer - 2` (inclusive), accessing `pM_char_buffer[index_of__char + 1]` which is at most `pM_char_buffer[size_of__char_buffer - 1]`. The null termination accesses `pM_char_buffer[size_of__char_buffer - 1]`, which is within bounds. No integer underflow: the second pre-condition check (`!size_of__char_buffer`) prevents `size_of__char_buffer - 1` from underflowing when `size_of__char_buffer` is 0, though this case is already caught by the first check since `index_of__cursor_in__char_buffer >= 0` is always true for unsigned types.
- **Validation:** The pre-condition checks are appropriate for the function's role. The function validates that the cursor is within bounds and that the buffer is non-empty before performing the shift. The second check (`!size_of__char_buffer`) is redundant since the first check (`cursor >= buffer_size`) already covers the case where `buffer_size` is 0, but it does not introduce any harm.

## Side Effects

- Mutates `p_this_ui_text_box->pM_char_buffer` by shifting characters left and null-terminating the last position.
- Does NOT modify `p_this_ui_text_box->index_of__cursor_in__char_buffer` (cursor stays in place for forward delete).
- Does NOT modify `p_this_ui_text_box->size_of__char_buffer` (buffer capacity unchanged).
- Does NOT call `set_ui_manager_as__dirty` (consistent with `handle_special_symbol__backspace__text_box`). The UI re-rendering is handled by the compose handler (`m_ui_element__compose_handler__text`) which calls `set_ui_manager_as__dirty` when invoked.
