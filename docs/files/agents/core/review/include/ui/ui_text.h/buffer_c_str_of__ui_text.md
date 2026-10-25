# buffer_c_str_of__ui_text

**File of origin:** `core/source/ui/ui_text.c`

## Semantic

Allocates (or re-allocates) a zero-initialized character buffer of the given size on a `UI_Element` that is being used as a text element. If a buffer already exists, it is freed first. If the requested size is zero, the buffer pointer is nulled and the size is set to zero. Marks the owning `UI_Manager` as dirty so that the UI will be recomposed.

## Pre-conditions

1. `p_ui_manager` must be a valid, non-null pointer to an initialized `UI_Manager`.
2. `p_ui_text` must be a valid, non-null pointer to a `UI_Element` whose kind is `UI_Element_Kind__Text` or `UI_Element_Kind__Text_Box` (so that the `pM_char_buffer`, `size_of__char_buffer`, and `index_of__cursor_in__char_buffer` union members are active).
3. If `p_ui_text->pM_char_buffer` is non-null prior to the call, it must have been allocated via `malloc` (or a compatible allocator) so that `free_pM_text_of__ui_text` can safely free it.
4. `size_of__text` is a `Quantity__u32` (`uint32_t`); it may be zero.

## Post-conditions

1. The `UI_Manager` is marked as dirty (`UI_MANAGER_FLAG__IS_DIRTY` is set).
2. Any previously allocated `pM_char_buffer` has been freed and set to `NULL` (0).
3. If `size_of__text` is zero:
   - `p_ui_text->pM_char_buffer` is `NULL` (0).
   - `p_ui_text->size_of__char_buffer` is set to `0`.
4. If `size_of__text` is non-zero:
   - `p_ui_text->pM_char_buffer` points to a newly allocated buffer of `size_of__text` bytes.
   - `p_ui_text->size_of__char_buffer` is set to `size_of__text`.
   - The buffer is zero-initialized (all bytes set to 0).

## Correctness Verdict

**Incorrect**

## Semantic Alignment

The function's intent is to (re)allocate a zero-initialized C-string buffer of the specified size for a UI text element. The overall logic flow — marking the manager dirty, freeing the old buffer, handling the zero-size case, allocating, setting the size, and zeroing the buffer — is semantically correct in structure. However, there is a critical deviation from the pattern used by sibling functions: **the function does not check for `malloc` failure**.

Compare with `set_c_str_of__ui_text_with__const_c_str` (lines 167-181), which performs the same sequence but includes a NULL check after `malloc`:

```c
p_ui_text->pM_char_buffer = malloc(size_of__text);
if (!p_ui_text->pM_char_buffer) {
    p_ui_text->size_of__char_buffer = 0;
    debug_error("set_c_str_of__ui_text_with__const_c_str, failed to allocate pM_char_buffer.");
    return;
}
```

In `buffer_c_str_of__ui_text`, the `malloc` result is assigned and used unconditionally without any NULL check. If `malloc` returns `NULL` (allocation failure), the function proceeds to:
1. Set `p_ui_text->size_of__char_buffer = size_of__text` (a non-zero value), creating an inconsistency between the size field and the null buffer pointer.
2. Call `memset(p_ui_text->pM_char_buffer, 0, size_of__text)` with a NULL first argument, which is **undefined behavior** (C11 §7.24.6.1: "If `s` is a null pointer, the behavior is undefined").

This is a genuine bug that can cause a crash on allocation failure.

## Implementation Correctness

- **Type compatibility:** All field accesses are type-correct. `pM_char_buffer` is `char *`, `size_of__char_buffer` is `Quantity__u32` (`uint32_t`), and `size_of__text` is `Quantity__u32`. `malloc` accepts `size_t` and `Quantity__u32` is implicitly convertible. `memset` receives a `void *` (from `char *`), a value of `0`, and a `size_t` (from `Quantity__u32`). No type mismatches.
- **Undefined behavior:** The primary UB is the `memset` call on a potentially NULL pointer when `malloc` fails. This is the critical defect.
- **Validation:** The function appropriately delegates null-pointer validation to the caller (consistent with the rest of the codebase, e.g., `set_c_str_of__ui_text_with__const_c_str` does not validate `p_ui_manager` or `p_ui_text` for null). However, it fails to validate the result of `malloc`, which is a resource allocation that can fail at runtime. The sibling functions `initialize_ui_element_as__text_with__const_c_str`, `initialize_ui_element_as__text_with__buffer_size`, and `set_c_str_of__ui_text_with__const_c_str` all perform this check; `buffer_c_str_of__ui_text` is the only one that omits it.

## Side Effects

1. **Mutates `p_ui_manager`:** Sets the `UI_MANAGER_FLAG__IS_DIRTY` flag via `set_ui_manager_as__dirty`.
2. **Mutates `p_ui_text`:** Frees any existing `pM_char_buffer` and allocates a new one (or sets it to NULL if size is zero). Sets `size_of__char_buffer` to `size_of__text` (or 0). Zero-initializes the allocated buffer.
3. **Heap allocation:** Calls `malloc` to allocate `size_of__text` bytes and `free` to release any prior buffer.
