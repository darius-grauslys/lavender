# Function Review: m_ui_element__compose_handler__default_only_recursive

## File of Origin
`core/source/ui/ui_element.c` (lines 541-567)

## Semantic
A UI element compose handler that performs **only** the recursive portion of composition — it delegates to the child element's compose handler without performing any non-recursive composition work (such as tile span generation or platform-level composition). This is the "recursive-only" counterpart to `m_ui_element__compose_handler__default`, which calls both `m_ui_element__compose_handler__default_non_recursive` and the child's compose handler.

## Pre-conditions
1. `p_ui_element` must be non-null (no explicit null check, but `does_ui_element_have__child` internally checks for null).
2. `p_game` must be valid and non-null (used to obtain the UI manager).
3. `p_graphics_window` must be valid and non-null (used to obtain the UI manager).
4. If `p_ui_element` has a child, the child pointer (`p_child`) must be valid or null.

## Post-conditions
1. If `p_ui_element` has no child, the function returns immediately with no side effects.
2. If `p_ui_element` has a child, the UI manager is marked as dirty.
3. If the child element has a compose handler, that handler is invoked on the child.
4. If the child element does not have a compose handler, the function returns after marking the UI manager dirty.

## Correctness Verdict
**Incorrect**

## Semantic Alignment
The implementation does **not** fulfill its semantic intent. The function is intended to retrieve the child of `p_ui_element` and recursively invoke the child's compose handler. However, there is a critical bug on line 556:

```c
UI_Element *p_ui_element__child =
    get_child_of__ui_element(p_ui_element__child);
```

The argument to `get_child_of__ui_element` is `p_ui_element__child` — the very variable being declared — rather than `p_ui_element` (the parent element). At this point, `p_ui_element__child` is an uninitialized local variable. Using it as an argument invokes **undefined behavior** in C.

The correct code should be:
```c
UI_Element *p_ui_element__child =
    get_child_of__ui_element(p_ui_element);
```

This is confirmed by comparison with:
- The sibling function `m_ui_element__compose_handler__default` (line 482), which correctly calls `get_child_of__ui_element(p_ui_element)`.
- `m_ui_element__dispose_handler__default` (line 68), which calls `get_child_of__ui_element(p_this_ui_element)`.
- `m_ui_element__transformed_handler__default` (line 462), which calls `get_child_of__ui_element(p_this_ui_element)`.

In every other call site in the file, the **parent** element is passed to `get_child_of__ui_element`. Only this function passes the uninitialized child variable.

## Implementation Correctness
- **Type compatibility**: The types are correct — `get_child_of__ui_element` takes a `UI_Element*` and returns a `UI_Element*`. No type mismatch.
- **Undefined behavior**: **Yes** — using the uninitialized local variable `p_ui_element__child` as an argument to `get_child_of__ui_element` is undefined behavior. The compiler may pass any garbage value to the function, which then dereferences it to access `p_child`, potentially causing a crash or corrupting the compose handler chain.
- **Validation**: The function correctly checks `does_ui_element_have__child(p_ui_element)` before proceeding, and checks `does_ui_element_have__compose_handler(p_ui_element__child)` before invoking the handler. These guards are appropriate. The bug is not a validation gap but a variable usage error.

## Side Effects
1. Marks the UI manager as dirty via `set_ui_manager_as__dirty` (if the element has a child).
2. Invokes the child element's `m_ui_compose_handler` (if the child has a compose handler).
3. Does **not** perform tile span generation, tile map updates, or platform-level composition (by design — this is the "recursive-only" variant).

## Summary
The function has a single-character-class bug: `p_ui_element__child` is used instead of `p_ui_element` as the argument to `get_child_of__ui_element` on line 556. This causes undefined behavior by reading an uninitialized variable and likely passing a garbage pointer to `get_child_of__ui_element`, which dereferences it. The fix is to change the argument from `p_ui_element__child` to `p_ui_element`.
