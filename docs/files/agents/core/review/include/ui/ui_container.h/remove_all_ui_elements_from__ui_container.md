remove_all_ui_elements_from__ui_container — core/include/ui/ui_container.h

Removes all child UI elements from a container UI_Element, resetting each child to its initial (default) state and detaching them from the container's linked-list structure. In Lavender semantics, "removal" means clearing/resetting elements to their initial conditions (not RAII-style deallocation), consistent with the engine's initialization pattern.

Pre-conditions:
1. p_ui_container must be a non-null pointer to a writable UI_Element that has been initialized as a container (via initialize_ui_element_as__container).
2. p_ui_container must be a valid, accessible UI_Element in memory.
3. The container may have zero or more child elements linked via p_child / p_next; or it may have no children (p_child == NULL), in which case the function is a no-op on the child list.

Post-conditions:
1. All child UI elements linked from p_ui_container->p_child (via the p_next chain) are reset to their initial/default state (Lavender-style initialization — cleared to zero/default values, preserving the Serialization_Header).
2. p_ui_container->p_child is set to NULL, severing the link to all former children.
3. p_ui_container itself is not freed or reset; only its child links are cleared.
4. The function returns void (no return value).

Correctness Verdict: Correct

Semantic Alignment:
The function name and signature align with the container API declared in ui_container.h, which includes initialize_ui_element_as__container and add_ui_element_to__ui_container. The parameter type (UI_Element *) is consistent with how containers are represented throughout the codebase — a UI_Element struct whose p_child pointer links to a singly-linked list of child elements (p_child → first child, each child's p_next → next sibling).

The expected behavior — iterating the p_child/p_next chain, resetting each child via Lavender-style initialization (memset to zero except Serialization_Header, as seen in initialize_ui_element in ui_element.c), and then setting p_child to NULL — is consistent with the engine's conventions:

- initialize_ui_element (ui_element.c) clears the struct body via memset while preserving the Serialization_Header, then sets specific fields.
- m_ui_element__dispose_handler__default (ui_element.c) clears p_parent, p_child, and p_next to 0 after disposing.
- The Lavender philosophy states that "initialization" means cleaning a struct to its initial conditions for pool reuse, not resource acquisition (RAII).

No implementation of this function currently exists in the codebase. The declaration alone is correct and follows all naming and type conventions. If implemented as described above, it would fulfill the semantic intent.

Implementation Correctness:
No implementation exists to evaluate. The declaration itself is type-correct:
- Parameter type UI_Element * matches the container representation used throughout the codebase.
- Return type void is appropriate for a mutating function with no computed return value.
- No implicit conversions, truncation, or type mismatches are present in the declaration.
- No undefined behavior is introduced by the declaration itself.

Side Effects:
- Mutates p_ui_container->p_child (sets to NULL).
- Mutates each former child UI_Element (reset to default/initial state via memset-style clearing).
- Does not free memory or deallocate resources (consistent with Lavender's non-RAII initialization pattern).
- Does not modify p_ui_container's own Serialization_Header, handlers, or other non-child fields.
- No side effects on the UI_Manager, Graphics_Window, or Game state directly (those would be the caller's responsibility).
