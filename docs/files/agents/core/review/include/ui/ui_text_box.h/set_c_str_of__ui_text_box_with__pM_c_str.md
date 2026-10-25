# set_c_str_of__ui_text_box_with__pM_c_str

**File of origin:** `core/include/ui/ui_text_box.h`

## Semantic

This is a static inline wrapper function that delegates to the underlying `set_c_str_of__ui_text_with__pM_c_str` function, forwarding all parameters (`p_ui_manager`, `p_ui_text_box`, `pM_text__c_str`, `size_of__text`) unchanged. Its purpose is to provide a UI text box-specific interface that maps to the more general UI text implementation.

## Pre-conditions

1. `p_ui_manager` must be non-null (used to mark the UI manager as dirty).
2. `p_ui_text_box` must be non-null (the UI element whose text buffer will be replaced).
3. `pM_text__c_str` may be null or non-null:
   - If non-null: the function takes ownership of the pointer; the caller must not free or access it after the call.
   - If null: the function clears the existing buffer and sets `size_of__char_buffer` to 0.
4. `size_of__text` represents the size of the managed string buffer in bytes; it should be the valid size of `pM_text__c_str` when non-null.

## Post-conditions

1. The UI manager's dirty flag (`UI_MANAGER_FLAG__IS_DIRTY`) is set via `set_ui_manager_as__dirty`.
2. Any previously owned `pM_char_buffer` on the UI element is freed via `free_pM_text_of__ui_text` (which calls `free()` on the old buffer and sets it to 0).
3. `p_ui_text_box->pM_char_buffer` is set to `pM_text__c_str`.
4. `p_ui_text_box->size_of__char_buffer` is set to `size_of__text` if `pM_text__c_str` is non-null, otherwise 0.
5. Ownership of `pM_text__c_str` is transferred to the UI element; the caller must not free or use the pointer afterward.

## Correctness Verdict

**Correct**

## Semantic Alignment

The implementation correctly delegates to `set_c_str_of__ui_text_with__pM_c_str`, which performs the intended ownership-transfer semantics. The function:
- Marks the UI manager as dirty (ensuring re-composition).
- Frees the old buffer before assigning the new one (preventing leaks).
- Handles the null pointer case gracefully by setting the buffer to null and size to 0.
- Takes ownership of the `pM_text__c_str` pointer, consistent with the documented `pM` naming convention in the codebase.

The wrapper does not alter any semantics — it is a transparent pass-through. The underlying implementation matches the semantic intent of replacing the text buffer with ownership transfer.

## Implementation Correctness

- **Type compatibility:** All parameter types match exactly between the wrapper and the underlying function. `UI_Manager *`, `UI_Element *`, `char *`, and `Quantity__u32` are passed through with no implicit conversions or truncation.
- **Undefined behavior:** No null dereference occurs. The underlying `free_pM_text_of__ui_text` checks for null before calling `free()`. The null check on `pM_text__c_str` in the ternary expression prevents any issues with null input.
- **Validation:** The function does not perform null checks on `p_ui_manager` or `p_ui_text_box`. This is consistent with the codebase pattern — these are expected to be valid by the caller, and the underlying `set_c_str_of__ui_text_with__pM_c_str` also does not validate them. This is appropriate for a performance-oriented inline wrapper in this engine.

## Side Effects

1. **Mutates `p_ui_manager`:** Sets the `UI_MANAGER_FLAG__IS_DIRTY` flag, signaling that the UI needs to be recomposed.
2. **Mutates `p_ui_text_box`:** 
   - Frees the previously owned `pM_char_buffer` (if non-null).
   - Sets `pM_char_buffer` to the new `pM_text__c_str`.
   - Sets `size_of__char_buffer` to `size_of__text` (or 0 if `pM_text__c_str` is null).
3. **Takes ownership of `pM_text__c_str`:** The caller relinquishes all rights to the pointer; it will be freed by the UI element's lifecycle management (e.g., via `free_pM_text_of__ui_text` on subsequent calls or disposal).
