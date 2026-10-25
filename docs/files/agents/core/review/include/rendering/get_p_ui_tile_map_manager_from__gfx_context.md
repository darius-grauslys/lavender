get_p_ui_tile_map_manager_from__gfx_context — core/include/rendering/gfx_context.h

Returns a pointer to the UI_Tile_Map_Manager member embedded in a Gfx_Context.

Pre-conditions:
1. p_gfx_context must be a non-null pointer to a valid Gfx_Context object.

Post-conditions:
1. Returns a valid pointer to the ui_tile_map_manager field owned by the passed Gfx_Context.

Correctness Verdict: Correct

Semantic Alignment:
The implementation fulfills the semantic intent — it returns the address of the embedded UI_Tile_Map_Manager, which is exactly what the function name and role imply. No drift.

Implementation Correctness:
Type compatibility — the field ui_tile_map_manager is declared as UI_Tile_Map_Manager (defines.h:2528), so &p_gfx_context->ui_tile_map_manager yields UI_Tile_Map_Manager *, matching the declared return type exactly. No implicit conversions or truncation.
No undefined behavior — no pointer arithmetic, no type punning, no out-of-bounds access. A null p_gfx_context would cause a null dereference, but this matches the precondition and is the caller's responsibility.
No validation is needed in-body — this is a trivial static inline accessor. Null-checking is deferred to the caller, consistent with the six sibling getters in the same file (get_p_PLATFORM_gfx_context_from__gfx_context, get_p_aliased_texture_manager_from__gfx_context, get_p_ui_context_from__gfx_context, get_p_graphics_window_manager_from__gfx_context, get_p_font_manager_from__gfx_context, get_p_sprite_context_from__gfx_context), none of which perform checks.

Side Effects:
No side effects — the function performs no mutation and only returns a pointer into the caller-provided struct.

Notes:
The "Initialization ≠ RAII" rule does not apply — the function name contains no init/initialize/reset and performs no initialization or cleanup.
