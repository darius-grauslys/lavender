# Function Review: `render_sprites_in__sprite_manager`

**File of origin:** `core/source/rendering/sprite_manager.c`

## 2. Semantic

Renders every enabled sprite owned by a `Sprite_Manager`: for each active `Sprite_Render_Record` it polls animation, syncs the record's render position to that sprite's `Hitbox_AABB` position (offset to center the sprite on its texture width), disables any sprite that lacks a hitbox, heap-sorts the active render records for depth ordering, then issues a `PLATFORM_render_sprite` draw call for each remaining enabled sprite.

## 3. Pre-conditions

1. `p_game` is non-null and valid.
2. `p_sprite_context` is non-null and valid.
3. `p_sprite_manager` is non-null and its members have been allocated via `allocate_sprite_manager__members` (i.e. `pM_sprite_render_records` is non-null and `p_sprite_render_record__last` lies within `[pM_sprite_render_records, pM_sprite_render_records + max_quantity_of__sprites]`).
4. `p_gfx_window` is non-null and valid.
5. Each active record's `p_sprite` points to a valid, allocated `Sprite` whose `texture_of__sprite.texture_flags` is a valid texture flag encoding a known width.
6. Active render records are packed contiguously from index `0` up to `p_sprite_render_record__last` (so a null `p_sprite` at index `0` implies an empty active set).

## 4. Post-conditions

1. For every enabled sprite that has an associated `Hitbox_AABB`, its `Sprite_Render_Record::position__3i32F4` is overwritten with the hitbox position and then shifted left by half the texture width (intent) to center the sprite.
2. Any enabled sprite with no associated `Hitbox_AABB` has `SPRITE_FLAG__BIT_IS_ENABLED` cleared via `set_sprite_as__disabled` and is omitted from rendering.
3. The active range `[pM_sprite_render_records, p_sprite_render_record__last)` of records is reordered in place by `heap_sort__opaque` according to `f_sort_heuristic__sprite_render_record`.
4. `PLATFORM_render_sprite` is invoked once per remaining enabled sprite, using that sprite and its (possibly updated) `position__3i32F4`.

## 5. Correctness Verdict

**Incorrect**

## 6. Semantic Alignment

The sprite-centering computation does not fulfill its intent. The relevant statement is:

```c
p_sprite_render_record->position__3i32F4.x__i32F4 -=
    i32_to__i32F4(
            get_length_of__texture_flag__width(
                p_sprite_render_record->p_sprite->texture_of__sprite.texture_flags)) >> 2; // TODO: why >> 2 and not >> 1?
```

`i32F4` is a fixed-point type with 4 fractional bits (`i32_to__i32F4(x) == x << 4`), and `get_length_of__texture_flag__width` returns an integer pixel width. To subtract half the texture width from an `i32F4` position, one converts the width to `i32F4` (`width * 16`) and then divides by 2 via `>> 1`, yielding `width * 8` — i.e. `width / 2` in real pixels. The code uses `>> 2`, which yields `width * 4` — i.e. `width / 4` in real pixels. Sprites are therefore offset to the right of their hitbox center by an additional quarter of the texture width instead of being centered. The in-source `TODO` confirms the author suspected this. **Semantic intent (center sprite on its hitbox) is not fulfilled.**

Secondary note (out of scope as its own review, but relevant to this function's correctness): the sort comparator `f_sort_heuristic__sprite_render_record` is not a strict weak ordering — it returns `-1` for the "equal/other" case and defines an inconsistent partial order — so the final depth sort may behave incorrectly depending on `heap_sort__opaque`'s contract.

## 7. Implementation Correctness

- **Type compatibility:** `get_length_of__texture_flag__width` returns `Quantity__u16` (`uint16_t`), widened to `Signed_Index__i32` for `i32_to__i32F4`; the widening is implicit but well-defined. The `>> 2` is the only type/arithmetically incorrect element (see Section 6).
- **Undefined behavior:** No broken pointer arithmetic or null dereferences on the happy path. The loop idiom (`continue` in a `do { ... } while ((++p) ...) `) matches the rest of the file (e.g. `release_sprite_from__sprite_manager`). The early guard `if (!p_sprite_render_record->p_sprite) return;` reads `pM_sprite_render_records` with **no null check**; if the manager's members were not allocated (caller only guards `p_sprite_manager != NULL`), this is a null dereference. The codebase's `clear_p_sprites_in__sprite_manager` guards the analogous pool pointer, so this missing guard is an inconsistency/robustness gap.
- **Validation:** No debug-mode validation of `p_sprite_manager` / `pM_sprite_render_records` is present here, unlike neighboring functions. The caller (`graphics_window.c:558`) checks `if (p_sprite_manager)` but does not guarantee members are allocated.
- **Loop bounds / OOB risk:** The `continue`-path evaluates `(++p_sprite_render_record)->p_sprite` before the `< p_sprite_render_record__last` bounds check. Because active records are packed contiguously and the post-`last` slot is zeroed, this is safe *unless* the manager is completely full (`p_sprite_render_record__last == pM_sprite_render_records + max_quantity_of__sprites`), in which case the increment reads one element past the allocated array. This is a latent, systemic risk of the file's loop idiom rather than something unique to this function.

## 8. Side Effects

- Mutates `Sprite_Render_Record::position__3i32F4` for every enabled, hitboxed sprite (overwrite + x offset).
- Calls `set_sprite_as__disabled`, which clears `SPRITE_FLAG__BIT_IS_ENABLED` on any `Sprite` whose render record had no matching `Hitbox_AABB`.
- Calls `poll_sprite_for__animation`, which may advance the sprite's animation frame index and set `SPRITE_FLAG__BIT_IS_NEEDING_GRAPHICS_UPDATE`.
- Reorders the `pM_sprite_render_records` array in place via `heap_sort__opaque` (swaps `Sprite_Render_Record` elements).
- Issues `PLATFORM_render_sprite` draw calls (platform-level rendering side effects).
