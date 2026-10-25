close_ui_window — core/source/ui/ui_context.c

Closes a UI window by invoking its registered close callback and then releasing the associated Graphics_Window from the graphics window manager.

Pre-conditions:
1. p_game must be a non-null pointer (checked in debug builds only).
2. uuid_of__graphics_window must refer to an allocated Graphics_Window in the graphics window manager (checked at runtime; returns early if not found).
3. The resolved Graphics_Window must have a non-null UI_Manager (checked at runtime; returns early if missing — this is documented in the header comment).
4. The Graphics_Window's kind (Graphics_Window_Kind) must be a valid enum value less than Graphics_Window_Kind__Unknown (bounds-checked by get_p_ui_window_record_from__ui_context).
5. The UI_Window_Record for that kind must be registered and valid — both f_ui_window__load and f_ui_window__close must be non-null (checked by is_ui_window_record__valid).

Post-conditions:
1. The f_ui_window__close callback has been invoked with the gfx context, graphics window, game, and UI_Manager.
2. The Graphics_Window has been released from the graphics window manager: reset (children, UI tile map, UI manager, sprite manager, hitbox manager released), deallocated, re-initialized to default state (Lavender-style pool cleanup), removed from the sorted window list, and the window list re-sorted.

Correctness Verdict: Correct

Semantic Alignment:
The implementation correctly fulfills the semantic intent. It validates all necessary preconditions, invokes the close callback, and then releases the graphics window. The ordering is correct: the close callback runs first while the Graphics_Window and UI_Manager are still valid, then release_graphics_window_from__graphics_window_manager handles the full teardown. The header documentation ("Will only close the given Graphics_Window uuid if the resolved Graphics_Window has a non-null ui_manager pointer") is accurately reflected in the implementation.

Implementation Correctness:
Type compatibility — All parameter types match their target function/callback types exactly. The f_ui_window__close callback is invoked with arguments matching its signature (Gfx_Context*, Graphics_Window*, Game*, UI_Manager*). The return value (bool) of the close callback is intentionally ignored, which is acceptable since close_ui_window returns void.
Undefined behavior — No pointer arithmetic, no null dereferences (all pointers are validated before use), no type punning, no out-of-bounds array access.
Validation — Validation is appropriate for the function's role. The debug-only null-check on p_game is consistent with the codebase's pattern. Runtime validation of graphics window existence, UI manager presence, and UI window record validity is performed.

Side Effects:
1. The f_ui_window__close callback is invoked, which may clean up UI elements and perform other UI-specific teardown.
2. The Graphics_Window is released via release_graphics_window_from__graphics_window_manager, which resets the window (releasing children, UI tile map, UI manager, sprite manager, and hitbox manager), deallocates it, re-initializes it to default state (Lavender-style initialization for pool reuse), removes it from the sorted window list, and re-sorts the windows.
3. Note: There is an unused local variable Graphics_Window *ptr_array_of__windows[MAX_QUANTITY_OF__GRAPHICS_WINDOWS] declared but never referenced. This is dead code that does not affect correctness but should be removed for code cleanliness.
