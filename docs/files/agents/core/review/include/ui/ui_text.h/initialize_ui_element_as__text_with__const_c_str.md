# initialize_ui_element_as__text_with__const_c_str

**File of origin:** `core/source/ui/ui_text.c`

## Semantic

Initializes a UI_Element as a text element by allocating a char buffer, copying the provided const C string into it, initializing the embedded Typer with the given font, and setting default text handlers (compose, transformed, dispose).

## Pre-conditions

1. `p_ui_text` must be non-null and point to a writable UI_Element.
2. `p_ui_text->pM_char_buffer` must be NULL — the element must not already be initialized as a text element. If non-null, the function logs an error and returns early without modification.
3. `p_font` should be a valid, non-null Font pointer. Passing NULL will set the Typer's font to NULL, which will cause issues at render time (e.g., null dereference in `m_ui_element__transformed_handler__text__centered` which accesses `p_font->max_width_of__font_letter`).
4. `p_text__const_c_str` should be a valid pointer to at least `size_of__text` bytes of readable memory. Passing NULL results in undefined behavior (memcpy with null source).
5. `size_of__text` is the number of bytes to allocate and copy. If 0, `malloc(0)` behavior is implementation-defined (may return NULL or a valid but zero-sized pointer).
6. The UI_Element's `ui_flags` are read before initialization to preserve existing flags (typically 0 for a zero-initialized struct, meaning the element starts disabled).

## Post-conditions

1. `p_ui_text` is initialized as a UI_Element of kind `UI_Element_Kind__Text` via `initialize_ui_element`.
2. `p_ui_text->pM_char_buffer` points to a newly allocated buffer of `size_of__text` bytes containing a copy of the first `size_of__text` bytes from `p_text__const_c_str`.
3. `p_ui_text->size_of__char_buffer` equals `size_of__text`.
4. The Typer is initialized with the provided font via `initialize_typer_with__font`.
5. Default text handlers are set: compose handler (`m_ui_element__compose_handler__text`), transformed handler (`m_ui_element__transformed_handler__text`), and dispose handler (`m_ui_element__dispose_handler__text`).
6. If `malloc` fails: the element is set as disabled (clears `UI_FLAGS__BIT_IS_ENABLED`), `size_of__char_buffer` is set to 0, and the function returns without copying text.

## Correctness Verdict

Correct

## Semantic Alignment

The implementation fulfills the semantic intent of initializing a UI_Element as a text element. The function correctly:

- Guards against re-initialization by checking `pM_char_buffer` before proceeding.
- Calls `initialize_ui_element` to zero the struct (Lavender-style cleanup) and set base fields (parent, child, next, kind, flags, default handlers).
- Allocates a char buffer of the correct size via `malloc`.
- Handles allocation failure by disabling the element and zeroing `size_of__char_buffer`.
- Initializes the Typer with the provided font via `initialize_typer_with__font`.
- Sets text-specific handlers (compose, transformed, dispose) via `initialize_ui_text__default_handlers`.
- Copies the text content into the buffer via `memcpy`.

The `#warning TODO: clamp c_str size based on config` indicates a known area for future improvement regarding size validation, but the current implementation is correct for valid inputs where `size_of__text` accurately reflects the number of bytes to copy from `p_text__const_c_str`.

## Implementation Correctness

**Type compatibility:** All parameter types match their target field types. `malloc` returns `void*`, implicitly converted to `char*` in C. `memcpy` and `memset` accept `void*` and `size_t`, compatible with `char*` and `Quantity__u32` respectively. No implicit conversions or truncation.

**Undefined behavior:** No broken pointer arithmetic, no null dereference (assuming valid inputs), no type punning, no out-of-bounds access (assuming `size_of__text` matches the source buffer size). The `memset` before `memcpy` is redundant since `memcpy` copies exactly `size_of__text` bytes filling the entire buffer, but it is harmless.

**Validation:** The function validates that the element is not already initialized as text (guard check on `pM_char_buffer`) and handles `malloc` failure. It does not validate `p_text__const_c_str` or `p_font` for null, which is the caller's responsibility in this low-level C codebase. The `#warning` indicates awareness that size clamping based on config is a future TODO.

## Side Effects

- Allocates memory for `pM_char_buffer` via `malloc`.
- Mutates `p_ui_text` struct fields: base UI_Element fields (via `initialize_ui_element`), `pM_char_buffer`, `size_of__char_buffer`, Typer fields (via `initialize_typer_with__font`), and handler pointers (via `initialize_ui_text__default_handlers`).
- May set the element as disabled (clears `UI_FLAGS__BIT_IS_ENABLED`) if allocation fails.
- Logs warnings and errors via `debug_warning` and `debug_error`.

## Lavender-Specific Semantics

This function is named "initialize" and performs **both** Lavender-style initialization (zeroing the struct to initial conditions via `initialize_ui_element`) and resource setup (allocating the char buffer via `malloc`). This is **not** the pool-cleanup pattern where "initialize" means "reset to initial conditions for reuse". Instead, this is a setup function that configures a UI_Element as a text element. The "initialize" in the function name refers to the overall setup process. The guard check on `pM_char_buffer` prevents re-initialization, consistent with pool-safety practices. The char buffer allocation and text copying constitute resource setup (RAII-style), which is acceptable here because this is a dedicated text-element initializer rather than a generic pool-reset function.
