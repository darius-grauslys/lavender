# register_scene_into__scene_manager

**File of origin:** `core/source/scene/scene_manager.c`

## Semantic

Registers scene lifecycle handler functions (load, enter, unload) into a specific scene slot within the `Scene_Manager`'s contiguous array of `Scene` structs, identified by a `Scene_Kind` enum value.

## Pre-conditions

1. `p_scene_manager` must be non-null and must have been previously initialized via `initialize_scene_manager` (so that the `scenes` array and its `Serialization_Header` are valid).
2. `the_kind_of_scene_to__register` must be a valid `Scene_Kind` value, i.e., strictly less than `Scene_Kind__Unknown`. Values >= `Scene_Kind__Unknown` will cause `get_p_scene_from__scene_manager` to return null, and the function will early-return.
3. `m_load_scene`, `m_enter_scene`, and `m_unload_scene` are function pointers of types `m_Load_Scene`, `m_Enter_Scene`, and `m_Unload_Scene` respectively. They may be null (0), though passing null would make the scene invalid per `is_scene__valid` (which checks `m_enter_scene_handler`).

## Post-conditions

1. If `the_kind_of_scene_to__register` is valid, the `Scene` at that index in `p_scene_manager->scenes` has its `m_load_scene_handler`, `m_enter_scene_handler`, and `m_unload_scene_handler` fields set to the corresponding provided function pointers.
2. If the scene was already valid (i.e., `m_enter_scene_handler` was non-null before the call), a debug warning is emitted indicating an overwrite is occurring, but the overwrite proceeds.
3. If `the_kind_of_scene_to__register` is invalid (>= `Scene_Kind__Unknown`), the function returns early without modifying any scene state.
4. The `p_parent_scene`, `p_scene_data`, and `is_active` fields of the target `Scene` are **not** modified by this function; they retain whatever values were set by `initialize_scene` (all zeroed/false) or by prior calls.

## Correctness Verdict

**Correct**

## Semantic Alignment

The implementation fulfills its semantic intent. The function is specifically designed to register the three scene lifecycle handler function pointers into a scene slot. It correctly:

- Retrieves the target `Scene` pointer via `get_p_scene_from__scene_manager`, which performs bounds checking against `Scene_Kind__Unknown`.
- Guards against a null `p_scene` return (invalid scene kind) with an early return and debug output.
- Warns when overwriting an already-valid scene (detected via `is_scene__valid`, which checks `m_enter_scene_handler != 0`).
- Assigns all three handler fields (`m_load_scene_handler`, `m_enter_scene_handler`, `m_unload_scene_handler`) to the provided function pointer arguments.

The function intentionally does **not** set `p_parent_scene`, `p_scene_data`, or `is_active`. This is correct because `initialize_scene` (the Lavender-style initialization function) already zeroes these fields, and `register_scene_into__scene_manager` is narrowly scoped to registering handler functions, not performing full scene setup. There is no semantic drift.

## Implementation Correctness

- **Type compatibility:** The parameter types `m_Load_Scene`, `m_Enter_Scene`, and `m_Unload_Scene` match the corresponding struct field types exactly. No implicit conversions or truncation occur.
- **Undefined behavior:** No null dereference — the null check on `p_scene` prevents accessing a null pointer. No out-of-bounds access — `get_p_scene_from__scene_manager` validates `the_kind_of_scene_to__register < Scene_Kind__Unknown` before indexing into the `scenes` array. No broken pointer arithmetic or type punning.
- **Validation:** The validation is appropriate for the function's role. The bounds check on the scene kind is delegated to `get_p_scene_from__scene_manager`, and the null check on the returned pointer is performed here. The overwrite warning is a diagnostic aid, not a hard error, which is reasonable since overwriting may be intentional in some use cases.

## Side Effects

1. **Mutates** the `m_load_scene_handler`, `m_enter_scene_handler`, and `m_unload_scene_handler` fields of the `Scene` struct at index `the_kind_of_scene_to__register` in `p_scene_manager->scenes`.
2. **May call** `debug_warning` (when overwriting an already-valid scene) and `debug_error` (when the scene kind is invalid), which produce debug output and may halt execution depending on the platform backend.
3. No other state is modified. The `p_parent_scene`, `p_scene_data`, and `is_active` fields are left untouched.
