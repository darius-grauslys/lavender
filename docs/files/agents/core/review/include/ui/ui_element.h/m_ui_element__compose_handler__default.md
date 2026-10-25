m_ui_element__compose_handler__default — core/source/ui/ui_element.c, lines 467-493

Composes the UI element non-recursively, then recursively composes its child element if the child exists and has a compose handler.

Pre-conditions:
1. p_ui_element must be a non-null pointer to a valid, initialized UI_Element. The function assumes this (it is a handler invoked through a function pointer on the element itself).
2. p_game must be a valid, non-null Game pointer (used to retrieve the UI manager and hitbox manager).
3. p_graphics_window must be a valid, non-null Graphics_Window pointer (used to retrieve the UI manager, hitbox manager, and UI tile map).
4. p_ui_element must have its m_ui_compose_handler set to a valid function (this function itself satisfies that precondition when set during initialize_ui_element).

Post-conditions:
1. The UI element p_ui_element has been composed — its UI tile span has been generated in the UI tile map and the platform-specific compose function has been invoked (via m_ui_element__compose_handler__default_non_recursive).
2. The UI manager is marked as dirty.
3. If p_ui_element has a child (p_child is non-null) and that child has a compose handler (child uses a UI tile span and has a non-null m_ui_compose_handler), the child's compose handler is invoked recursively, composing the child and its descendants.
4. If p_ui_element has no child, or the child lacks a compose handler, only p_ui_element itself is composed.

Correctness Verdict: Correct

Semantic Alignment:
The function correctly implements a depth-first compose traversal of the parent-to-child UI element hierarchy. It first composes the current element via the non-recursive helper, then checks for a child using the null-safe does_ui_element_have__child macro (which verifies both p_ui_element and p_ui_element->p_child are non-null). If a child exists, it retrieves the child pointer (safe because non-null was just verified) and checks whether the child has a compose handler via does_ui_element_have__compose_handler (which verifies both the UI tile span flag and the function pointer). If the child has a compose handler, it is invoked recursively.

The function does NOT traverse the p_next (sibling) chain. This is consistent with the design pattern: siblings are expected to be composed separately by the UI manager or caller. The compose handler's responsibility is to compose a single element and its child subtree.

The non-recursive delegate, m_ui_element__compose_handler__default_non_recursive, is called unconditionally on the parent element. This is appropriate because this function IS the compose handler — it is only invoked when the caller has already determined the element should be composed (i.e., the element has a compose handler and uses a UI tile span).

Implementation Correctness:
- Type compatibility: p_ui_element__child->m_ui_compose_handler is of type m_UI_Compose, which has the signature (UI_Element*, Game*, Graphics_Window*) -> void. The call passes (p_ui_element__child, p_game, p_graphics_window), matching exactly. No implicit conversions or truncation.
- Undefined behavior: No null dereference — p_ui_element__child is verified non-null via does_ui_element_have__child before being used in does_ui_element_have__compose_handler and the subsequent function pointer call. No broken pointer arithmetic, no type punning, no out-of-bounds access.
- Validation: Appropriate validation is performed for the child (existence check and compose handler check). The parent element is assumed valid because this is a handler invoked through a function pointer on the element itself, consistent with the codebase pattern (e.g., m_ui_element__dispose_handler__default and m_ui_element__transformed_handler__default also do not null-check their p_this_ui_element parameter).

Side Effects:
- Marks the UI manager as dirty (via m_ui_element__compose_handler__default_non_recursive).
- Generates a UI span in the UI tile map (via m_ui_element__compose_handler__default_non_recursive).
- Invokes the platform-specific compose function for the element's tile span (via m_ui_element__compose_handler__default_non_recursive).
- Recursively composes child UI elements if they exist and have compose handlers.
