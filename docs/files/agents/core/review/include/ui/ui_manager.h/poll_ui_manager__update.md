poll_ui_manager__update — core/source/ui/ui_manager.c

Dispatches UI update logic based on the current input mode and click state. It first checks for writing-mode input, then prioritizes click-released, click-held, and click-dragged events, delegating to the appropriate sub-handler for each.

Pre-conditions:
1. p_ui_manager must be a non-null pointer to a valid, initialized UI_Manager object.
2. p_game must be a non-null pointer to a valid Game object (used to retrieve the Input subsystem).
3. p_graphics_window must be a non-null pointer to a valid Graphics_Window object.

Post-conditions:
1. If input mode is INPUT_MODE__WRITING, poll_ui_manager__update_for__input_writing is invoked with (p_ui_manager, p_game, p_graphics_window).
2. If no click action is active, the function returns without further side effects beyond the optional writing-mode dispatch.
3. Exactly one of the following may occur based on click state:
   - Click released → poll_ui_manager__update_for__clicked_and_dropped(p_ui_manager, p_game, p_graphics_window) is called, then the function returns.
   - Click held → poll_ui_manager__update_for__held(p_game, p_graphics_window, p_ui_manager) is called, then the function returns.
   - Click dragged → poll_ui_manager__update_for__drag(p_game, p_graphics_window, p_ui_manager) is called, then the function returns.

Correctness Verdict: Correct

Semantic Alignment:
The function correctly implements a dispatcher that routes input events to specialized sub-handlers. The priority order (released > held > dragged) and the separation of writing-mode handling are semantically sound. The switch statement treats INPUT_MODE__NORMAL and any unknown/default mode identically (no-op), which is the intended behavior — only WRITING mode triggers special handling before click dispatch.

Implementation Correctness:
Type compatibility — all arguments passed to each sub-handler match the parameter types declared in their respective function signatures exactly. The parameter ordering differs between sub-handlers (e.g., poll_ui_manager__update_for__held takes Game*, Graphics_Window*, UI_Manager* whereas poll_ui_manager__update_for__clicked_and_dropped takes UI_Manager*, Game*, Graphics_Window*), but each call site correctly matches its target's signature. No implicit conversions or truncation occur.
No undefined behavior — no pointer arithmetic, no null dereference (null validation is the caller's responsibility for this dispatcher), no type punning, no out-of-bounds access. The local variable p_input is a simple pointer read with no mutation.
No validation is needed within this function — it is a dispatcher; ensuring valid pointers is the caller's responsibility.

Side Effects:
The function itself performs no direct mutations. Its only observable effects are the indirect side effects of the sub-handlers it may invoke, which can mutate UI element focus, drag state, held state, and typing state. The local variable p_input is a read-only pointer to the game's input subsystem.
