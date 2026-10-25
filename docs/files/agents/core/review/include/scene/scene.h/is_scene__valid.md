# is_scene__valid

**File of origin:** `core/include/scene/scene.h`

## Semantic

Checks whether a `Scene` has been registered with valid handler functions by testing whether its `m_enter_scene_handler` function pointer is non-null. A scene is considered "valid" (i.e., registered and ready for use) when at least its enter-scene handler has been assigned.

## Pre-conditions

1. `p_scene` must be non-null. The function dereferences `p_scene` without a null check; null-checking is the caller's responsibility (consistent with the codebase pattern where callers like `register_scene_into__scene_manager` validate the pointer before invoking this helper).

## Post-conditions

1. Returns `true` if `p_scene->m_enter_scene_handler` is non-null, indicating the scene has been registered with an enter-scene handler.
2. Returns `false` if `p_scene->m_enter_scene_handler` is null, indicating the scene has not been registered or has been cleared via `initialize_scene`.

## Correctness Verdict

**Correct**

## Semantic Alignment

The implementation fulfills its semantic intent. In the Lavender engine, `initialize_scene` sets all handler pointers (including `m_enter_scene_handler`) to `0` (null), effectively clearing the scene for pool reuse. When a scene is registered via `register_scene_into__scene_manager`, the `m_enter_scene_handler` is assigned a non-null function pointer. Therefore, checking `m_enter_scene_handler` for non-null is a valid proxy for determining whether a scene has been registered. The function correctly leverages C's implicit conversion of function pointers to boolean (non-null → `true`, null → `false`).

## Implementation Correctness

- **Type compatibility:** `m_enter_scene_handler` is of type `m_Enter_Scene` (a function pointer: `void (*)(Scene*, Game*)`). Returning it as `bool` relies on C's well-defined implicit conversion where any non-null pointer evaluates to `true` and a null pointer evaluates to `false`. No truncation or implicit conversion issues.
- **Undefined behavior:** No null dereference (caller ensures `p_scene` is non-null), no out-of-bounds access, no type punning, no broken pointer arithmetic.
- **Validation:** The function does not null-check `p_scene`, which is appropriate for an inline helper. The caller (`register_scene_into__scene_manager`) already validates the pointer before calling this function. This is consistent with the codebase's pattern of keeping lightweight inline helpers free of defensive checks.

## Side Effects

No side effects. The function is a pure read operation that only inspects the `m_enter_scene_handler` field of the `Scene` struct.
