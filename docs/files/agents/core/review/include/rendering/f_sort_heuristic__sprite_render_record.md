f_sort_heuristic__sprite_render_record — core/source/rendering/sprite_manager.c, lines 244-272

## 1. Header
- **Function name:** `f_sort_heuristic__sprite_render_record`
- **File of origin:** `core/source/rendering/sprite_manager.c`

## 2. Semantic
Comparator passed to `heap_sort__opaque` to order `Sprite_Render_Record` entries into render order:
primarily ascending by `z` (depth layer), with ascending `y` as the tie-breaker so that,
within a layer, sprites higher on screen (`y` smaller) are drawn first and sprites lower on
screen (`y` larger) draw last / on top (standard 2D y-sorting).

## 3. Pre-conditions
1. `pv_sprite_render_record__one` and `pv_sprite_render_record__two` point to valid,
   initialized `Sprite_Render_Record` objects.
2. Neither pointer is NULL.
3. Both records' `position__3i32F4.z__i32F4` and `.y__i32F4` fields hold initialized values
   (`i32F4` is `int32_t`).
4. `p_context` is unused (may be `NULL` or a `Game*`); no constraint is imposed by this
   function.

## 4. Post-conditions
1. Returns `Signed_Quantity__i32` following the `heap_sort__opaque` contract: negative when
   record one should sort before two ("one < two"), positive when it should sort after
   ("one > two"), zero when equal.
2. Neither record nor any external state is mutated (pure comparator).
3. Records are not consumed or freed.

## 5. Correctness Verdict
Incorrect

## 6. Semantic Alignment
The `z` axis comparison is correct: it returns `+1` when `one.z > two.z`, placing higher-z
sprites later (drawn on top). The `y` tie-breaker is **inverted**. When `one.y < two.y`
(record one is higher on screen and should be drawn first / earlier in ascending y), the
function returns `+1`, asserting one is "greater." This makes `heap_sort__opaque` place one
later (drawn last / on top of two), which is the opposite of intended ascending-y ordering.

Effect: within a z-layer sprites render in reversed vertical order — sprites near the top of
the screen are drawn last (on top) and sprites near the bottom are drawn first (behind) —
producing visibly incorrect layering.

Additionally the function never returns `0` for equal elements; it falls through to
`return -1`, so equal records are treated as "one < two." This only affects stability of
identical elements and does not corrupt ordering of distinct ones, but it is not a clean
comparator.

## 7. Implementation Correctness
- Type compatibility: `i32F4` is `int32_t`; `>`, `<` are well-defined on these fixed-point
  values. `void *`-to-`Sprite_Render_Record *` casts are correct. Return type
  `Signed_Quantity__i32` is used consistently.
- Undefined behavior: None. No null dereferences (caller passes valid elements), no
  out-of-bounds access, no type punning.
- Validation: Appropriate. The function is `static` and is only invoked from
  `render_sprites_in__sprite_manager` over the manager's own record array, so defensive
  NULL checks are not required (mirrors the sibling `test_opaque_heuristic__i32` comparator
  pattern). No pre-validation of the caller's pointer is the function's responsibility.
- Primary bug: the `y` comparison is inverted (direction error), as detailed above.
- Minor: `p_context` is declared but unused (no `(void)p_context;` cast); cosmetic only.

## 8. Side Effects
No side effects. Pure comparator; it does not read or write `p_context`, does not mutate
either `Sprite_Render_Record`, and invokes no further functions.

### Call site (context)
```
heap_sort__opaque(
        p_game,
        p_sprite_manager->pM_sprite_render_records,
        p_sprite_manager->p_sprite_render_record__last
                - p_sprite_manager->pM_sprite_render_records,
        sizeof(Sprite_Render_Record),
        f_sort_heuristic__sprite_render_record,
        f_sort_swap__sprite_render_record);
```
