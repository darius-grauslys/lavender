# set_ui_element__sprite

**File of origin:** `core/include/ui/ui_element.h`

## Semantic

Associates a `Sprite *` with a `UI_Element *` by logically marking the element as "using a sprite" and storing the sprite reference.

## Pre-conditions

1. `p_ui_element` must be a non-null pointer to an initialized `UI_Element`.
2. `p_sprite` may be NULL or a valid `Sprite *` pointer.

## Post-conditions

1. The UI element's `ui_flags` would have `UI_FLAGS__BIT_IS_USING__SPRITE_OR_UI_TILE_SPAN` set (indicating sprite mode).
2. The sprite would be associated with the UI element for later lookup/release.

## Correctness Verdict

**Incorrect**

## Semantic Alignment

The function is **declared but never defined**. It appears in the header at lines 64–66:

```c
void set_ui_element__sprite(
        UI_Element *p_ui_element,
        Sprite *p_sprite);
```

However, no implementation exists in `core/source/ui/ui_element.c`. A search of the entire `core/source/ui/ui_element.c` file confirms that no `set_ui_element__sprite` definition is present. The only sprite-related functions implemented in the .c file are:

- `does_ui_element_have__sprite` — checks sprite existence via UUID lookup in `Sprite_Manager`
- `release_ui_element__sprite` — releases a sprite from `Sprite_Manager` by UUID lookup

Since `set_ui_element__sprite` has no implementation, any call to it will result in a **linker error** (undefined reference). The function cannot fulfill its semantic intent because:

1. **No implementation body exists** — the function is declared but never defined.
2. **No `p_sprite` field in `UI_Element`** — The `UI_Element` struct (defined in `core/include/defines.h`) has no `p_sprite` member. Sprites are managed externally through the `Sprite_Manager` using the UI element's UUID (via `GET_UUID_P(p_ui_element)`). There is no field to store the `Sprite *` parameter.
3. **Signature mismatch with the sprite management pattern** — The related `release_ui_element__sprite` function (in the .c file) takes `Game *` and `Graphics_Window *` parameters to access the `Sprite_Manager`. The `set_ui_element__sprite` declaration takes only `UI_Element *` and `Sprite *`, which is insufficient to register a sprite with the `Sprite_Manager` (which requires `Gfx_Context *`, `Sprite_Manager *`, `Graphics_Window *`, and a `uuid__u32`).

## Implementation Correctness

- **Type compatibility**: The parameter types (`UI_Element *` and `Sprite *`) are valid types, but the implementation does not exist, so type compatibility is moot.
- **Undefined behavior**: No undefined behavior can be assessed because the function body is absent.
- **Validation**: No validation exists because there is no implementation.

## Side Effects

Cannot be determined — the function has no implementation. If it were implemented following the pattern of `set_ui_element__tile_span_of__ui_element` (which sets the `UI_FLAGS__BIT_IS_USING__SPRITE_OR_UI_TILE_SPAN` flag and assigns the `ui_tile_span` field), it would mutate `p_ui_element->ui_flags`. However, since there is no `p_sprite` field in the `UI_Element` struct, the sprite cannot be stored directly on the element. The sprite would need to be registered with the `Sprite_Manager` via the element's UUID, which requires additional context parameters not present in the current signature.
