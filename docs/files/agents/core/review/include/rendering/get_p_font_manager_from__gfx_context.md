get_p_font_manager_from__gfx_context — core/include/rendering/gfx_context.h

Returns the address of the embedded font_manager member of a Gfx_Context.

Pre-conditions:
1. p_gfx_context must be a non-null pointer to a valid, writable Gfx_Context object.
2. The Gfx_Context must be at least partially initialized (the caller is responsible for the lifetime/validity of the pointed-to object; this accessor does not validate the field's contents).

Post-conditions:
1) Returns a non-null pointer equal to &p_gfx_context->font_manager.
2) The returned pointer aliases the font_manager member of the caller's Gfx_Context; it is valid for the lifetime of that Gfx_Context object.

Correctness Verdict: Correct

Semantic Alignment:
The implementation fulfills the semantic intent: it returns the address of the font_manager sub-object embedded in Gfx_Context. The Gfx_Context_t struct (core/include/defines.h:2524-2532) declares Font_Manager font_manager as a direct (non-pointer) member of type Font_Manager (defined at defines.h:889-891), so taking its address yields a Font_Manager *. The name, return type, and body are all consistent.

Implementation Correctness:
- Type compatibility: Return type Font_Manager * exactly matches &p_gfx_context->font_manager (font_manager is a Font_Manager). No implicit conversions or truncation.
- Undefined behavior: No pointer arithmetic, no type punning, no out-of-bounds access. Note: p_gfx_context is not null-checked; passing NULL would dereference NULL when forming the member address, which is undefined behavior. This is consistent with the convention of the other static inline accessors in the same file (get_p_ui_context_from__gfx_context, get_p_sprite_context_from__gfx_context, etc.), which likewise perform no validation. Per the module's convention, null-check validation is the caller's responsibility, so this is not a defect of this function.
- Validation: None performed, which is appropriate for a low-level accessor; validation belongs to the caller.

Side Effects:
No side effects — the function is a pure accessor. It computes and returns an address without reading or modifying any state.

Note (Initialization ≠ RAII):
This function is not an initialization function (its name contains no "init"/"initialize"/"reset"); it is a pure getter. However, it is invoked by initialize_gfx_context (core/source/rendering/gfx_context.c:26-27) to obtain the address of the font_manager member, which is then passed to initialize_font_manager for Lavender-style reset-to-default (memset-based cleanup) rather than RAII resource acquisition. That semantics belongs to the caller, not to this accessor.
