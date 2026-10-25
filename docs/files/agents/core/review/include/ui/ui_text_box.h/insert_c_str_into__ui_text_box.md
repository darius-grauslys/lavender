insert_c_str_into__ui_text_box — core/include/ui/ui_text_box.h

Delegates to insert_c_str_into__ui_text (core/source/ui/ui_text.c, lines 271-292).

Inserts up to `size_of__text` bytes from `p_text__const_c_str` into the text box's
char buffer at `index_to__insert_at`, then advances the cursor to the end of the
inserted region. The UI manager is marked dirty to trigger a re-compose.

Pre-conditions:
1. p_ui_manager must be a non-null pointer to a valid UI_Manager.
2. p_ui_text must be a non-null pointer to a properly initialized UI_Element of kind
   UI_Element_Kind__Text with a non-null pM_char_buffer and size_of__char_buffer > 0.
3. p_text__const_c_str must be non-null (passed to strncpy; NULL is undefined behavior).
4. index_to__insert_at must be < p_ui_text->size_of__char_buffer (enforced at runtime).
5. size_of__text is the number of bytes to attempt to copy from the source.

Post-conditions:
1. p_ui_text->pM_char_buffer has up to `clamp` bytes of text written starting at
   index_to__insert_at, where clamp = min(size_of__text, size_of__char_buffer -
   index_to__insert_at).
2. p_ui_text->index_of__cursor_in__char_buffer is set to index_to__insert_at + clamp.
3. The UI manager is marked dirty.
4. If index_to__insert_at >= size_of__char_buffer, the function returns early with no
   mutation and an error is logged.

Correctness Verdict: Incorrect

Semantic Alignment:
The function's intent is to insert a fixed number of bytes (`size_of__text`) from a
source buffer into the text box's char buffer at a specified index. The implementation
diverges from this intent in two ways:

1. **strncpy is used instead of memcpy.** The sibling function
   `append_c_str_into__ui_text` (core/source/ui/ui_text.c, lines 249-261) correctly
   uses `memcpy` to copy exactly `clamp` bytes. `insert_c_str_into__ui_text` uses
   `strncpy`, which stops at the first null byte in the source string. If
   `p_text__const_c_str` contains embedded null bytes before `clamp` bytes, fewer bytes
   are copied than intended, yet the cursor is still advanced by `clamp`. This is a
   semantic mismatch: `size_of__text` represents a byte count, not a null-terminated
   string length, so `strncpy` is the wrong primitive.

2. **No null-termination guarantee.** `strncpy` does not null-terminate when the source
   is >= `clamp` bytes. While the buffer uses `size_of__char_buffer` for length tracking
   (not null-termination), the absence of a null terminator after insertion could cause
   issues if any consumer treats the buffer as a C string. The sibling `append` function
   has the same issue, but `strncpy` makes it worse by introducing inconsistent behavior
   when embedded nulls are present.

Implementation Correctness:
- Type compatibility: All parameter types match their usage. `Quantity__u32` and
  `Index__u32` are both `uint32_t`; `min__u32` accepts and returns `u32`. No implicit
  conversions or truncation.
- No undefined behavior from pointer arithmetic: The bounds check
  (`index_to__insert_at >= p_ui_text->size_of__char_buffer`) guarantees
  `index_to__insert_at < size_of__char_buffer`, so the subtraction
  `size_of__char_buffer - index_to__insert_at` cannot underflow, and the pointer offset
  `pM_char_buffer + index_to__insert_at` is in-bounds.
- No null dereference on p_ui_text->pM_char_buffer: If the buffer is NULL,
  size_of__char_buffer is expected to be 0, which makes the bounds check fail and the
  function returns early. However, this relies on an invariant (NULL buffer implies zero
  size) that is not explicitly enforced.
- Missing null check on p_text__const_c_str: If p_text__const_c_str is NULL, strncpy is
  passed a null source pointer, which is undefined behavior. The function should either
  assert non-null or handle NULL gracefully.
- Missing null check on p_ui_manager: If p_ui_manager is NULL, set_ui_manager_as__dirty
  dereferences a null pointer. However, this is consistent with the codebase pattern
  where callers are expected to provide valid pointers.

Side Effects:
- Marks the UI manager as dirty via set_ui_manager_as__dirty.
- Mutates p_ui_text->pM_char_buffer (writes text at index_to__insert_at).
- Mutates p_ui_text->index_of__cursor_in__char_buffer (advances to end of insertion).
- Logs an error via debug_error if the index is out of bounds.
