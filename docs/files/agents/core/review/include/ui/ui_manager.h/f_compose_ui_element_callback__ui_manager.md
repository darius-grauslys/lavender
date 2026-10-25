# f_compose_ui_element_callback__ui_manager

**File of origin:** `core/source/ui/ui_manager.c`

## Semantic

Composes a single UI element by invoking its registered compose handler. This is a callback function conforming to the `f_Foreach_UI_Element` signature, used by `foreach_ui_element_in__ui_manager` to iterate over and compose each enabled UI element in the manager's pool.

## Pre-conditions

1. `p_ui_element` may be NULL; if so, the function returns early without dereferencing it.
2. `p_ui_manager` is part of the callback signature but is **not used** in this function's body. It is not dereferenced or validated.
3. `p_game` and `p_gfx_window` are passed through to the compose handler without null-checking in this function. The caller (`compose_all_ui_elements_in__ui_manager`) validates these in debug builds (`#ifndef NDEBUG`), but not in release builds.
4. `p_ui_element` must have its `ui_flags` field initialized (to check the enabled bit) and its `m_ui_compose_handler` field initialized (to check for a valid handler).

## Post-conditions

1. If `p_ui_element` is NULL or the `UI_FLAGS__BIT_IS_ENABLED` bit in `ui_flags` is not set, the function returns without side effects.
2. If `p_ui_element` does not have a compose handler (i.e., `is_ui_element__using_ui_tile_span` returns false, or `m_ui_compose_handler` is NULL), the function returns without side effects.
3. If both checks pass, the function invokes `p_ui_element->m_ui_compose_handler(p_ui_element, p_game, p_gfx_window)`. The observable side effect is whatever the compose handler does (e.g., drawing the element into the graphics window).

## Correctness Verdict

**Correct**

## Semantic Alignment

The implementation faithfully fulfills its semantic intent. The function:

- Guards against NULL `p_ui_element` before any dereference, using short-circuit evaluation (`||`) so that `is_ui_element__enabled` (which itself does not null-check) is only called when `p_ui_element` is non-NULL.
- Guards against elements without a compose handler by delegating to `does_ui_element_have__compose_handler`, which checks both the `UI_FLAGS__BIT_IS_USING__SPRITE_OR_UI_TILE_SPAN` flag (via `is_ui_element__using_ui_tile_span`) and the non-nullness of `m_ui_compose_handler` (via `get_ui_element__compose_handler`).
- Only invokes the compose handler after confirming it is non-NULL, so there is no risk of calling a NULL function pointer.
- Passes the correct arguments (`p_ui_element`, `p_game`, `p_gfx_window`) to the compose handler, matching the `m_UI_Compose` typedef signature (`void (*)(UI_Element*, Game*, Graphics_Window*)`).

## Implementation Correctness

- **Type compatibility:** The function signature `(UI_Manager*, Game*, Graphics_Window*, UI_Element*)` matches the `f_Foreach_UI_Element` typedef exactly. The `m_ui_compose_handler` field is of type `m_UI_Compose`, which is `void (*)(UI_Element*, Game*, Graphics_Window*)` — the arguments passed match this signature precisely. No implicit conversions or truncation.
- **Undefined behavior:** No null dereference (NULL `p_ui_element` is checked first). No out-of-bounds access. No type punning. The compose handler is verified non-NULL before invocation.
- **Validation:** The null check on `p_ui_element` is appropriate and necessary. The caller validates `p_ui_manager`, `p_game`, and `p_gfx_window` in debug builds. The function correctly relies on the caller for those validations rather than duplicating them, which is consistent with the codebase pattern.

## Side Effects

- Invokes `p_ui_element->m_ui_compose_handler(p_ui_element, p_game, p_gfx_window)`, which typically draws the UI element into the graphics window.
- No direct mutation of `p_ui_manager`, `p_game`, or `p_gfx_window` by this function itself — side effects are limited to whatever the compose handler does.
- If the early-return conditions are met (NULL element, disabled element, or no compose handler), there are no side effects.
