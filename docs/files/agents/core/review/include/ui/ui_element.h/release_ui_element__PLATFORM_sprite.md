release_ui_element__PLATFORM_sprite — core/source/ui/ui_element.c, lines 352-380

Releases the Sprite associated with the given UI_Element from its Sprite_Manager.

Pre-conditions:
1. p_game must be a non-null pointer to a valid Game object.
2. p_graphics_window must be a non-null pointer to a valid Graphics_Window that has an associated Sprite_Manager.
3. p_ui_element must be a non-null pointer to a valid UI_Element with a valid Serialization_Header (UUID).
4. The Sprite_Manager obtained from p_graphics_window must be non-null; otherwise the behavior is undefined in release builds (see Implementation Correctness).

Post-conditions:
1. If a Sprite with the UI_Element's UUID exists in the Sprite_Manager, it is released from the manager (deallocated and its platform sprite freed).
2. If no such Sprite exists, the function is a no-op.
3. p_game, p_graphics_window, and p_ui_element are not otherwise mutated; only the Sprite_Manager's internal state is affected.

Correctness Verdict: Incorrect

Semantic Alignment:
The implementation's logic is semantically correct for releasing a sprite associated with a UI element. The flow — obtaining the Sprite_Manager from the Graphics_Window, looking up the Sprite by the UI_Element's UUID, and releasing it — matches the intent of the function and is consistent with the inline sprite-release logic in `m_ui_element__dispose_handler__default`.

However, there is a critical mismatch between the header declaration and the implementation:

- **Header declaration** (core/include/ui/ui_element.h, lines 68-70):
  `void release_ui_element__PLATFORM_sprite(Gfx_Context *p_gfx_context, UI_Element *p_ui_element);`

- **Source implementation** (core/source/ui/ui_element.c, lines 352-380):
  `void release_ui_element__sprite(Game *p_game, Graphics_Window *p_graphics_window, UI_Element *p_ui_element);`

The function name differs (`release_ui_element__PLATFORM_sprite` vs `release_ui_element__sprite`), and the parameter signatures are completely different. `PLATFORM` is NOT a macro in this codebase — it is a literal prefix used for platform-specific functions (e.g., `PLATFORM_release_sprite`, `PLATFORM_allocate_sprite`). The header-declared function `release_ui_element__PLATFORM_sprite` has no matching implementation in the source file, and the implemented function `release_ui_element__sprite` has no matching declaration in the header. This mismatch means the function as declared in the header would cause a linker error if called.

Additionally, the debug error message on line 364 references the header name (`release_ui_element__PLATFORM_sprite`) rather than the implementation name (`release_ui_element__sprite`), further confirming the inconsistency.

Implementation Correctness:
- **Type compatibility**: The `does_ui_element_have__sprite` function is declared to return `bool` but returns a `Sprite*` (via `get_p_sprite_by__uuid_from__sprite_manager`). In C this is an implicit pointer-to-bool conversion, which is valid but produces a type mismatch that may trigger compiler warnings with strict type checking.
- **Undefined behavior — null pointer dereference**: The function does NOT check whether `p_sprite_manager` is NULL before passing it to `does_ui_element_have__sprite`. In debug builds (`#ifndef NDEBUG`), the null is caught by the debug check inside `get_p_sprite_by__uuid_from__sprite_manager`, which logs an error and returns NULL — preventing the crash. However, in release builds, the `#ifndef NDEBUG` guard is skipped entirely, and `get_p_sprite_by__uuid_from__sprite_manager` dereferences `p_sprite_manager->pM_pool_of__sprites` with a NULL `p_sprite_manager`, causing undefined behavior. The comparable function `m_ui_element__dispose_handler__default` correctly guards against this with `if (!p_sprite_manager) return;` before any sprite operations.
- **Validation**: The function relies on the caller to provide valid `p_game`, `p_graphics_window`, and `p_ui_element` pointers. The debug-only null check on `does_ui_element_have__sprite` is insufficient for release builds. A release-mode guard for `p_sprite_manager == NULL` is missing.

Side Effects:
- Mutates the Sprite_Manager's internal state by releasing the Sprite associated with the UI_Element's UUID (deallocating it from the sprite pool and freeing its platform sprite via `PLATFORM_release_sprite`).
- No other observable side effects on `p_game`, `p_graphics_window`, or `p_ui_element`.
- Note: the function is currently unused — no callers exist in the codebase (the equivalent logic is inlined in `m_ui_element__dispose_handler__default`).
