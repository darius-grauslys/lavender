m_ui_draggable__dragged_handler__default — core/source/ui/ui_draggable.c

Default event handler that repositions a draggable UI element to the current cursor position when dragging begins.

Pre-conditions:
1. p_this_draggable must be a non-null pointer to a valid UI_Element that has been initialized as a draggable element.
2. p_game must be a non-null pointer to a valid Game with an initialized input subsystem (p_input).
3. p_graphics_window must be a non-null pointer to a valid Graphics_Window with an associated hitbox manager.
4. The UI_Element pointed to by p_this_draggable must have a valid UUID (via Serialization_Header) for hitbox lookup.

Post-conditions:
1. p_this_draggable has its UI_FLAGS__BIT_IS_FOCUSED flag set.
2. p_this_draggable has its UI_FLAGS__BIT_IS_BEING_DRAGGED flag set.
3. If a hitbox AABB exists for the element, the element's position (and its child elements recursively) is updated to the cursor position.
4. If no hitbox AABB exists, the element is disabled (UI_FLAGS__BIT_IS_ENABLED cleared) and an error is logged.
5. The function returns void; no return value is produced.

Correctness Verdict: Correct

Semantic Alignment:
The function correctly implements the semantic intent of a default dragged handler: when a draggable UI element is being dragged, it should be repositioned to follow the cursor. The function first sets the appropriate flags (focused and being dragged), then attempts to retrieve the hitbox component. If the hitbox is missing, it gracefully disables the element and logs an error rather than crashing. If the hitbox exists, it repositions the element to the cursor position via set_position_3i32_of__ui_element, which also handles child elements recursively through the transformed handler. The implementation aligns with the Lavender engine's pattern of using hitbox AABBs for UI element positioning and transformation.

Implementation Correctness:
Type compatibility — all parameter types match their usage: UI_Element* is passed to functions expecting UI_Element*, Game* to functions expecting Game*, Graphics_Window* to functions expecting Graphics_Window*. The cast of the void* returned by get_pV_hitbox_manager_from__graphics_window to Hitbox_AABB_Manager* is appropriate given the engine's design of using void* for polymorphic manager access.
Undefined behavior — no broken pointer arithmetic, no null dereference, no type punning, no out-of-bounds access. All pointer dereferences are guarded by null checks (e.g., the p_hitbox_aabb null check before use). The function does not dereference p_game or p_graphics_window directly; it passes them to accessor functions.
Validation — the function validates the presence of a hitbox component and handles the missing case gracefully by logging an error and disabling the element. This is appropriate validation for a default handler. The lack of null checks on p_this_draggable, p_game, and p_graphics_window is consistent with the engine's convention of treating these as caller responsibilities (similar to other UI handler functions in the codebase).

Side Effects:
The function mutates the UI_Element pointed to by p_this_draggable:
- Sets the UI_FLAGS__BIT_IS_FOCUSED flag.
- Sets the UI_FLAGS__BIT_IS_BEING_DRAGGED flag.
- If no hitbox is found: clears the UI_FLAGS__BIT_IS_ENABLED flag (disabling the element).
- If a hitbox is found: updates the element's position (and recursively any child elements) to the current cursor position via set_position_3i32_of__ui_element, which may trigger the element's transformed handler.
- Logs an error message via debug_error if the hitbox component is missing.
