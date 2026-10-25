# Function Review: `f_sort_swap__sprite_render_record`

**File of origin:** `core/source/rendering/sprite_manager.c`

---

## Semantic

Swaps two `Sprite_Render_Record` values in-place using a temporary copy. This is a sort-swap callback used by the generic sort routine over the sprite render record array.

---

## Pre-conditions

1. `p_context` may be unused (it is not referenced within the function body).
2. `pv_sprite_render_record__one` must be a non-null pointer to a valid `Sprite_Render_Record` instance.
3. `pv_sprite_render_record__two` must be a non-null pointer to a valid `Sprite_Render_Record` instance.
4. Both pointers must reference distinct, properly aligned `Sprite_Render_Record` objects (no aliasing).

---

## Post-conditions

1. The `Sprite_Render_Record` objects pointed to by `pv_sprite_render_record__one` and `pv_sprite_render_record__two` have had their contents swapped.
2. After return, the value previously held at `*p_sprite_render_record__one` is now at `*p_sprite_render_record__two`, and vice versa.
3. No other memory or state is modified.

---

## Correctness Verdict

**Correct**

---

## Semantic Alignment

The implementation performs a standard three-step swap:

1. Copies the first record into a local `Sprite_Render_Record temporary`.
2. Assigns the second record's contents into the first.
3. Assigns the temporary (original first) into the second.

This matches the semantic intent of a swap operation. The struct `Sprite_Render_Record` contains:

```c
typedef struct Sprite_Render_Record_t {
    Vector__3i32F4 position__3i32F4;
    Sprite *p_sprite;
} Sprite_Render_Record;
```

The full struct is copied via assignment — no fields are omitted, reordered, or partially copied. The swap is value-based and complete.

---

## Implementation Correctness

- **Type compatibility:** The `void*` parameters are cast to `Sprite_Render_Record*` before use. The cast is correct and matches the expected type used elsewhere in the file (e.g., `f_sort_heuristic__sprite_render_record` performs the same cast).
- **Undefined behavior:** No null dereferences occur (pre-conditions require valid pointers). No pointer arithmetic is performed. The struct copy is a plain assignment, which is well-defined for this struct (it contains only a value type `Vector__3i32F4` and a pointer `Sprite*`, both safely copyable).
- **Validation:** This function is a low-level swap callback invoked by a generic sort routine. It does not perform validation, which is appropriate — the caller (the sort routine) is responsible for ensuring valid pointers are passed.

---

## Side Effects

The function mutates the two `Sprite_Render_Record` objects passed via the `void*` parameters, swapping their contents. No other side effects.
