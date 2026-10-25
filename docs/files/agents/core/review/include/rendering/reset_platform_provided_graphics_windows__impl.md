reset_platform_provided_graphics_windows — core/source/rendering/graphics_window_manager.c

Resets (cleans up) every platform-provided Graphics_Window by acquiring them in offset-batched pages and dispatching each to reset_graphics_window.

Pre-conditions:
1. p_game is a non-null pointer to an initialized Game whose p_gfx_context is valid.
2. p_game->p_gfx_context->graphics_window_manager is initialized (held by reference, not owned).
3. The platform (via PLATFORM_get_provided_windows) provides a finite, ordered set of platform graphics windows; it must zero/null-terminate its output array and return 0 once all windows for the requested offset have been exhausted so the do-while can terminate.
4. is_releasing_unprovided_children is a bool; no value constraint.

Post-conditions:
1. Every platform-provided Graphics_Window reachable through allocate_or_get__platform_provided_graphics_windows has been passed to reset_graphics_window along with p_game and is_releasing_unprovided_children.
2. p_graphics_window_manager is not mutated by this function (it is only read as a lookup/allocation context by the callee).
3. If acquire_or_get__platform_provided_graphics_windows fails for a batch, debug_error is invoked and the function returns immediately, leaving the not-yet-fetched windows untouched.
4. The stack-local ptr_array_of__graphics_windows buffer is discarded on return.

Correctness Verdict: Correct

Semantic Alignment:
The implementation fulfills the semantic intent — it walks all platform-provided graphics windows (in pages of up to MAX_QUANTITY_OF__GRAPHICS_WINDOWS, advanced by the reported overflow count) and resets each via reset_graphics_window. The offset advancement `index_of__current_acquisition += quantity_overflowed__u32` correctly progresses past each fetched page with no gap or overlap, and the do-while terminates once allocate_or_get__platform_provided_graphics_windows reports zero remaining overflow. Per Lavender semantics, "reset" here is Lavender-style reset (cleaning to initial conditions / pool cleanup via the release_* helpers in reset_graphics_window), not RAII resource acquisition — though the acquisition helper incidentally may allocate Graphics_Window objects for platform windows not yet tracked, which are then immediately reset (see Side Effects).

Implementation Correctness:
Type compatibility: index_of__current_acquisition (Index__u32 / uint32_t) and quantity_overflowed__u32 (Quantity__u32 / uint32_t) are both uint32_t; the addition is well-typed with no truncation. MAX_QUANTITY_OF__GRAPHICS_WINDOWS is `8` (int), used as the array bound and the loop bound; comparing the uint32_t index against it is safe and in-range (0..7). is_releasing_unprovided_children (bool) is passed unchanged to reset_graphics_window's bool parameter. ptr_array_of__graphics_windows is `Graphics_Window *[8]`, indexed by index_of__gfx_window (0..7), in bounds.
Undefined behavior: no null dereference is reachable within this function — ptr_array_of__graphics_windows[index_of__gfx_window] is null-checked before being passed to reset_graphics_window. The buffer is stack-allocated and strictly bounded by MAX_QUANTITY_OF__GRAPHICS_WINDOWS; no out-of-bounds access occurs. get_p_gfx_context_from__game(p_game) and get_p_graphics_window_manager_from__gfx_context(...) are single field-offset accesses returning pointers to embedded structs; no arithmetic or type punning is performed.
Validation: p_game is not null-checked, which is consistent with the codebase's low-level rendering functions (e.g. reset_graphics_window, reset_children_of__graphics_window_from__graphics_window_manager) where validation is the caller's responsibility.

Side Effects:
- Mutates each acquired platform-provided Graphics_Window through reset_graphics_window, which releases its children, ui_tile_map, ui_manager, sprite_manager, and hitbox_manager.
- Incidentally, allocate_or_get__platform_provided_graphics_windows may allocate and assign Graphics_Window objects (via _allocate_graphics_window_from__graphics_window_manager and set_graphics_window_as__platform_provided) for platform windows that have no tracked Graphics_Window yet; those are then reset inline.
- On acquisition failure, invokes debug_error and returns early (no further windows are reset in that call).
