f_ui_window__close__default — core/source/ui/ui_window.c

Default close handler for a UI window that releases the associated UI manager and graphics window.

Pre-conditions:
1. `p_gfx_window` must be a non-null pointer to a valid, allocated Graphics_Window with a valid serialization header (its UUID is accessed via `GET_UUID_P`).
2. `p_game` must be a non-null pointer to a valid Game instance; it is used to retrieve the Gfx_Context and underlying managers.
3. `p_gfx_context` may be null — it is a required parameter of the `f_UI_Window__Close` typedef but is never referenced in the function body.
4. `p_ui_manager` may be null — it is a required parameter of the `f_UI_Window__Close` typedef but is never referenced in the function body; the UI manager is instead looked up by UUID derived from `p_gfx_window`.

Post-conditions:
1. The UI_Manager associated with the graphics window's UUID is released from the UI_Context (deallocated and reset to initial conditions) — provided the graphics window owns its UI manager (i.e., `GET_UUID_P(p_gfx_window) == p_gfx_window->uuid_of__ui_manager`).
2. The Graphics_Window is released from the Graphics_Window_Manager via `release_graphics_window_from__graphics_window_manager`, which internally calls `reset_graphics_window` (releasing child windows, UI tile maps, UI manager, sprite manager, and hitbox manager) and then deallocates and reinitializes the window.
3. The function returns `true` unconditionally.

Correctness Verdict: Correct

Semantic Alignment:
The function fulfills its semantic intent of closing (releasing) a UI window and its associated resources. However, the explicit call to `release_p_ui_manager_from__ui_context` is redundant: `release_graphics_window_from__graphics_window_manager` internally invokes `reset_graphics_window`, which in turn calls `release_graphics_window_ui_manager` — this callee already handles releasing the UI manager (including the check for shared UI managers via `does_graphics_window_share_a__ui_manager`). The explicit call uses `GET_UUID_P(p_gfx_window)` (the graphics window's own UUID) rather than `p_gfx_window->uuid_of__ui_manager`; this works correctly when the window owns its UI manager, but in the shared case it will fail to find a matching UI_Manager and log a spurious "ui manager was not found" error before the implicit path correctly returns early.

Implementation Correctness:
Type compatibility — all parameter types match the `f_UI_Window__Close` typedef exactly. `GET_UUID_P(p_gfx_window)` casts `Graphics_Window*` to `Serialization_Header*` and accesses the `uuid` field, which is valid because `Serialization_Header _serialization_header` is the first member of `Graphics_Window`.
Undefined behavior — no null dereference of `p_gfx_window` occurs (it is dereferenced by `GET_UUID_P`, so the caller must ensure it is non-null). No null dereference of `p_game` occurs (it is passed to callees which validate it in debug builds). No type punning, no out-of-bounds access.
Validation — the function performs no validation of its own parameters; this is consistent with the pattern in the codebase where validation is delegated to callee functions (e.g., `release_graphics_window_from__graphics_window_manager` checks for null `p_graphics_window` in debug builds).

Side Effects:
1. Mutates the UI_Context by releasing (deallocating) the UI_Manager associated with the graphics window's UUID (if owned).
2. Mutates the Graphics_Window_Manager by releasing (deallocating and reinitializing) the Graphics_Window.
3. As a consequence of the above, also triggers release of child windows, UI tile maps, sprite managers, and hitbox managers associated with the graphics window (via `reset_graphics_window`).
4. The `p_gfx_context` and `p_ui_manager` parameters have no effect — they are unused.
