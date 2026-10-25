get_p_ui_context_from__gfx_context — core/include/rendering/gfx_context.h

Returns a pointer to the UI_Context sub-object embedded in a Gfx_Context.

Pre-conditions:
1. p_gfx_context must be a non-null pointer to a valid Gfx_Context object (the parameter is dereferenced via the -> operator).
2. Ownership/lifetime of the returned pointer is bound to the lifetime of the Gfx_Context; it must not be used after the Gfx_Context is freed.

Post-conditions:
1. Returns a UI_Context * pointing to the ui_context member of *p_gfx_context (i.e., &p_gfx_context->ui_context).

Correctness Verdict: Correct

Semantic Alignment:
The implementation returns &p_gfx_context->ui_context, which directly fulfills the semantic intent of exposing the embedded UI_Context of a Gfx_Context. The Gfx_Context struct (defines.h:2527) declares UI_Context ui_context as a direct member, so the address-of this member is precisely the UI_Context owned by the gfx context.

Implementation Correctness:
Type compatibility — p_gfx_context->ui_context is of type UI_Context (a value member, defines.h:2527), so &p_gfx_context->ui_context is UI_Context *, matching the declared return type UI_Context * exactly. No implicit conversions, promotions, or truncation.
Undefined behavior — no pointer arithmetic, no type punning, no out-of-bounds access. The only dereferenced pointer is p_gfx_context, which must be non-null per pre-conditions; this is a low-level static inline getter, so null-checking here is the caller's responsibility.
Validation — appropriate for its role as a trivial accessor; no validation is performed because the function only takes the address of an embedded member. The caller is responsible for passing a valid, initialized Gfx_Context.
Initialization ≠ RAII — not applicable; the function name contains no init/initialize/reset token and performs no setup or cleanup.

Side Effects:
No side effects — this is a pure getter. The only observable effect is the return value (a pointer into internal struct state); no fields are read or written, and no callee is invoked.
