# Planning: Rendering — Incorrect Modules

**Review source:** `agents/core/review/include/rendering/incorrect_modules.md`

**Source files reviewed (read-only):**
- `core/source/rendering/sprite_context.c`
- `core/source/rendering/sprite_manager.c`
- `core/source/rendering/graphics_window_manager.c`
- `core/source/rendering/graphics_window.c`
- `core/source/rendering/gfx_context.c`
- `core/include/rendering/sprite_context.h`
- `core/include/rendering/sprite_manager.h`
- `core/include/rendering/graphics_window_manager.h`
- `core/include/rendering/graphics_window.h`
- `core/include/rendering/gfx_context.h`
- `core/include/rendering/gfx_context_helpers.h`
- `core/include/rendering/texture.h`
- `core/include/rendering/sprite_animation.h`
- `core/include/defines.h`
- `core/include/serialization/serialization_header.h`
- `core/include/serialization/hashing.h`
- `core/include/serialization/identifiers.h`
- `core/include/sort/heap_sort__opaque.h`
- `core/source/sort/heap_sort__opaque.c`
- `core/source/serialization/hashing.c`
- `core/source/game_action/game_action_manager.c`
- `core/source/ui/ui_context.c`
- `tests/core/source/rendering/test_suite_rendering_sprite_context.c`
- `tests/core/source/rendering/test_suite_rendering_sprite_manager.c`
- `tests/core/source/rendering/test_suite_rendering_graphics_window_manager.c`

---

## 1. Problem Identification

Twenty-three functions/modules across four source files are flagged as **Incorrect**. They are grouped below by source file.

### Group A — Sprite Context (`core/source/rendering/sprite_context.c`, `core/include/rendering/sprite_context.h`)

**A1. `allocate_sprite_manager_from__sprite_context`** — `Precondition` violation: the function does not validate `uuid_of__sprite_manager` against `IDENTIFIER__UNKNOWN__u32` via `is_identifier_u32__invalid` (the sibling `allocate_sprite_from__sprite_manager` does). Passing `IDENTIFIER__UNKNOWN__u32` produces a non-null `Sprite_Manager*` whose `Serialization_Header.uuid` remains `IDENTIFIER__UNKNOWN__u32`, making it appear deallocated (`is_serialized_struct__deallocated` returns true) and unfindable by `get_p_sprite_manager_by__uuid_from__sprite_context`. Additionally, if `get_next_available__allocation_in__contiguous_array` returns an already-allocated slot with a matching UUID, `allocate_sprite_manager__members` calls `initialize_sprite_manager` (memset to 0) without freeing the old `pM_pool_of__sprites` and `pM_sprite_render_records`, violating the `Conservation Law` (leaked allocations).

**A2. `release_sprite_manager_from__sprite_context`** — Three defects:
- **Lower-bound `Boundary Condition` gap (UB):** the bounds check `p_sprite_manager - p_sprite_context->pM_sprite_managers >= max_quantity_of__sprite_managers` compares a signed `ptrdiff_t` against an unsigned `Quantity__u8`. A pointer before the array start yields a negative `ptrdiff_t` that passes the check, causing an out-of-bounds write. The correct pattern (used in `release_game_action_from__game_action_manager`, `game_action_manager.c:87-94`) stores the difference in a `u32` first.
- **UB from pointer subtraction of unrelated pointers:** `p_sprite_manager - p_sprite_context->pM_sprite_managers` is UB when `p_sprite_manager` doesn't point into the array — exactly the case this guard is meant to detect.
- **Missing allocation check:** `pM_sprite_managers` is never verified non-null before dereferencing (unlike the allocate counterpart).
- **Conservation Law violation (memory leak):** member resources `pM_pool_of__sprites` and `pM_sprite_render_records` (allocated by `allocate_sprite_manager__members`) are never freed, unlike the sibling `release_sprite_from__sprite_manager` which frees `p_PLATFORM_sprite` before deallocating.
- **Surface-form leakage:** all `debug_error` calls reference `release_sprite_from__sprite_context` instead of `release_sprite_manager_from__sprite_context`.

**A3. `get_p_sprite_animation_group_from__sprite_context`** — `Surface-form leakage` / `Translation Gap`: the debug range check compares `the_kind_of__sprite_animation_group` against `Sprite_Animation_Kind__Unknown` instead of `Sprite_Animation_Group_Kind__Unknown`. The parameter is `Sprite_Animation_Group_Kind` and the backing array is sized by `Sprite_Animation_Group_Kind__Unknown`. This currently works only because both enums define `__None=0, __Unknown=1` with identical value sets; it diverges from intent and is fragile. Additionally, the null-pointer guard present in all sibling accessors (`register_sprite_animation_into__sprite_context`, `get_sprite_animation_from__sprite_context`, etc.) is omitted.

**A4. `get_p_sprite_manager_by__uuid_from__sprite_context`** — `Boundary Condition` / `State Desync`: the function does not guard the unallocated-pool state. After `initialize_sprite_context` (memset to 0), `pM_sprite_managers == NULL` and `max_quantity_of__sprite_managers == 0`. When a valid UUID is passed, `dehash_identitier_u32_in__contigious_array` → `poll_for__uuid_collision` computes `identifier % 0` — integer division by zero (UB/crash). The sibling allocate function guards this via `is_sprite_managers_allocated_in__sprite_context`. The null check on `p_sprite_context` is also missing (all sibling accessors include an `NDEBUG` guard).

**A5. `release_sprite_managers_from__sprite_context`** — `State Desync` / `Conservation Law` violation: after `free(p_sprite_context->pM_sprite_managers)`, the field is not set to `0` and `max_quantity_of__sprite_managers` is not reset to `0`. This leaves a dangling pointer that causes `is_sprite_managers_allocated_in__sprite_context` to return a dangling `true`, enabling a double-free on a second release call. The existing test `sprite_context__release_sprite_managers__clears_allocation` directly asserts `is_sprite_managers_allocated_in__sprite_context(&context)` is false after release — this test fails with the current code. Per-manager member pools are also leaked (same issue as A2).

**A6. `allocate_sprite_managers_from__sprite_context`** — `Undefined Behavior` on `malloc` failure: the function sets `max_quantity_of__sprite_managers` before checking the `malloc` result, then enters the initialization loop and dereferences the NULL pointer. Also leaves the struct in an inconsistent state (non-zero `max_quantity_of__sprite_managers` with NULL pointer) on failure. No null check on `p_sprite_context`. No validation of zero quantity (zero-size `malloc` is implementation-defined).

### Group B — Sprite Manager (`core/source/rendering/sprite_manager.c`)

**B1. `f_sort_heuristic__sprite_render_record`** — `Mode Confusion`: the `y` tie-breaker is inverted. When `one.y < two.y` (record one is higher on screen and should be drawn first/earlier in ascending-y order), the function returns `+1`, causing `heap_sort__opaque` to place it later (drawn last/on top). This produces visibly incorrect vertical layering within a z-layer. Additionally, the comparator never returns `0` for equal elements (falls through to `return -1`), violating the strict weak ordering contract expected by `heap_sort__opaque`.

**B2. `allocate_sprite_from__sprite_manager`** — Two defects:
- **UB on texture-allocation failure path:** when `PLATFORM_allocate_texture` fails, the code calls `PLATFORM_release_sprite(p_gfx_context, p_sprite->p_PLATFORM_sprite)`, but `p_PLATFORM_sprite` has not yet been allocated at that point — it is uninitialized/stale memory from the pool slot. This is a release of a never-allocated or stale pointer.
- **Missing `Boundary Condition` check:** `p_sprite_render_record__last` is written and incremented without verifying it hasn't exceeded the bounds of `pM_sprite_render_records` (i.e., `p_sprite_render_record__last < pM_sprite_render_records + max_quantity_of__sprites`). Over-allocation causes an out-of-bounds write.

**B3. `get_p_sprite_by__uuid_from__sprite_manager`** — Same `Boundary Condition` / `State Desync` as A4: when the sprite pool is unallocated (the default state after `initialize_sprite_manager`, which every `Sprite_Manager` starts in after `allocate_sprite_managers_from__sprite_context` initializes each slot), and a valid UUID is passed, `dehash_identitier_u32_in__contigious_array` → `poll_for__uuid_collision` computes `valid_uuid % 0` — integer division by zero. The sibling `clear_p_sprites_in__sprite_manager` guards this state with `if (!p_sprite_manager->pM_pool_of__sprites) { return; }`, but this getter does not.

**B4. `render_sprites_in__sprite_manager`** — Three defects:
- **`Translation Gap` (sprite centering):** the centering offset uses `>> 2` instead of `>> 1`. `i32_to__i32F4(width)` yields `width * 16` (4 fractional bits); `>> 1` gives `width * 8` = `width/2` pixels (correct centering); `>> 2` gives `width * 4` = `width/4` pixels (sprites offset right by an extra quarter-width). The in-source `TODO: why >> 2 and not >> 1?` confirms author suspicion.
- **Missing null check on `pM_sprite_render_records`:** the early guard `if (!p_sprite_render_record->p_sprite) return;` dereferences `pM_sprite_render_records` with no null check. If members were not allocated, this is a null dereference. The sibling `clear_p_sprites_in__sprite_manager` guards the analogous pointer.
- **Latent OOB risk:** the `continue`-path loop idiom `(++p_sprite_render_record)->p_sprite` evaluates the next element before the `< p_sprite_render_record__last` bounds check. Safe when active records are packed and the post-`last` slot is zeroed, but reads one element past the array if the manager is completely full.

### Group C — Graphics Window Manager (`core/source/rendering/graphics_window_manager.c`)

**C1. `initialize_graphics_window_manager`** — Two `Representation Invariant` breaches:
- `ptr_array_of__sorted_graphic_windows` is never zeroed. The array is scanned as a free-list by `get_next_available_p_ptr_graphics_window_from__sorted_list` and `get_sorted_slot_of__graphics_window_from__sorted_list`, which treat NULL as "free". A manager not pre-zeroed by its caller retains stale/garbage pointers. The test `graphics_window_manager__initialize__sorted_array_cleared` only passes because the test runtime happens to zero-initialize its stack variable.
- `memset(0)` leaves `graphics_window__parent__uuid == 0`. The codebase sentinel for "no parent / invalid identifier" is `IDENTIFIER__UNKNOWN__u32` (0xFFFFFFFF), per `is_identifier_u32__invalid` and `is_graphics_window_with__parent`. Because `0 != 0xFFFFFFFF`, `is_graphics_window_with__parent` returns TRUE for a freshly-initialized window. The test `graphics_window_manager__is_graphics_window_with__parent__false_after_init` fails on this assertion.

**C2. `_allocate_graphics_window_from__graphics_window_manager`** — `State Desync` / `Mode Confusion`: the assignment `graphics_window__flags = texture_flags_for__gfx_window` (line 177-179) overwrites the `COMPOSE_DIRTY` flag set moments earlier by `set_graphics_window_as__in_need_of__composition` (line 170-171). Additionally, `texture_flags_for__gfx_window` is `uint32_t` while `graphics_window__flags` is `uint8_t` (`Graphics_Window_Flags__u8`). Texture flags encode height in bits 0-2 and width in bits 3-5 (`TEXTURE_FLAG__LENGTH__BIT_COUNT = 3`). Window state flags use BIT(0) = IS_ENABLED, BIT(1) = COMPOSE_DIRTY, BIT(2) = IS_PLATFORM_PROVIDED. For texture heights where the enum is non-zero (x16=1, x32=2, x64=3, etc.), bits 0-2 of the texture flags corrupt the window state flags — e.g., a 64x64 texture flag (value 27 = 0b11011) sets IS_PLATFORM_PROVIDED (BIT 2), causing `is_graphics_window__platform_provided` to incorrectly return true. The dimensions are already stored separately in `width_of__graphics_window__u32` and `height_of__graphics_window__u32`, making the assignment redundant and harmful.

**C3. `set_graphics_window_as__parent_to__this_graphics_window`** — `Surface-form leakage` (wrong variable): the validation loop uses `is_graphics_window_a__child_of__this_graphics_window(p_graphics_window__child, p_graphics_window__parent)` with the fixed `p_graphics_window__parent` instead of the per-iteration `p_graphics_window`. This inverts the intended validation: when the child is already parented to THIS parent, the condition is true and the function incorrectly rejects with "child is already assigned to another parent"; when the child already has a DIFFERENT parent, the condition is false and the function silently allows reparenting (the exact conflict the guard is meant to forbid). The per-iteration variable `p_graphics_window` is dead (triggers `-Wunused-but-set-variable`). The sibling `release_children_of__graphics_window_from__graphics_window_manager` (line 370) confirms the correct pattern: `is_graphics_window_a__child_of__this_graphics_window(p_graphics_window__child, p_graphics_window)`.

**C4. `reset_children_of__graphics_window_from__graphics_window_manager`** — `Surface-form leakage` (wrong variable): in the `if` branch, `!is_graphics_window__platform_provided(p_graphics_window)` and `release_graphics_window_from__graphics_window_manager(p_game, p_graphics_window)` use `p_graphics_window` (the parent/subtree root) instead of `p_graphics_window__child`. This releases the parent instead of the child. On repeated matches, the first call clears the parent's sorted slot; the second call's `get_sorted_slot_of__graphics_window_from__sorted_list` returns NULL, and `*p_ptr_sorted_graphics_window_slot = 0;` dereferences NULL — UB/crash. The sibling `release_children_of__graphics_window_from__graphics_window_manager` (line 370) correctly passes `p_graphics_window__child`.

**C5. `get_graphics_window__p_root_parent`** — `Undefined Behavior` (null deref): in the broken-chain branch, `get_graphics_window__p_parent` returns 0, and the next statement dereferences it: `p_graphics_window__current_parent->graphics_window__parent__uuid = IDENTIFIER__UNKNOWN__u32`. The intended target was the pre-call value of `p_graphics_window__current_parent`, which was clobbered by the lookup assignment. Fix: store the lookup result in a separate variable and orphan the original window on null. Additionally, the depth-limit underflow guard `MAX_QUANTITY_OF__GRAPHICS_WINDOWS (8) >= --depth_to_search` does not correctly detect u32 wraparound (which occurs at 0 → UINT32_MAX, not at 8), so bounded depth limits ≤ 9 break after the first parent lookup.

**C6. `get_graphics_windows_from__graphics_window_manager`** — `Translation Gap` (wrong return value): on early exit (buffer full), returns `index_of__graphics_window` (the source-array loop index) instead of `index_of__gfx_window_in__ptr_array` (the count of windows actually written). The return type is `Quantity__u8` but `index_of__graphics_window` is `Index__u32` (uint32_t) — an implicit truncation. Additionally, the function does not check `is_graphics_window__allocated`, unlike the sibling `reset_children_of__graphics_window_from__graphics_window_manager`, so unallocated windows (with garbage/default kind values) may be included in the output buffer.

**C7. `release_graphics_window_from__graphics_window_manager`** — `Undefined Behavior` (null deref): `get_sorted_slot_of__graphics_window_from__sorted_list` can return NULL (0) if the window is not found in the sorted list. The caller then unconditionally dereferences it with `*p_ptr_sorted_graphics_window_slot = 0;` without a null check. This is reachable on double-release, prior sorted-list corruption, or a window never added to the sorted list. Additionally, `get_p_gfx_context_from__game(p_game)` is called twice redundantly.

**C8. `is_graphics_window_NOT_from__this_graphics_window_manager`** — `Undefined Behavior`: `p_graphics_window - p_graphics_window_manager->graphics_windows` is UB per C11 6.5.6p8 when `p_graphics_window` does not point into the `graphics_windows` array — exactly the scenario this function exists to detect. The guard is built on a UB foundation. Signed→unsigned conversion of `ptrdiff_t` to `Index__u32` wraps negative results to large values, so out-of-range detection relies on unsigned wraparound rather than a defined comparison. Only called from `set_graphics_window_as__parent_to__this_graphics_window` where both windows are expected to originate from this manager.

**C9. `sort_graphic_windows_in__graphic_window_manager`** — `Non-Injective Translation` (swapped arguments): the call passes `sizeof(Graphics_Window*)` as the 3rd argument and `MAX_QUANTITY_OF__GRAPHICS_WINDOWS` as the 4th. The `heap_sort__opaque` implementation (`core/source/sort/heap_sort__opaque.c`) uses the 3rd parameter as `length_of__array` (count) and the 4th as `size_of__type` (stride). The header (`heap_sort__opaque.h`) has misleading parameter names (`size_of__type` as 3rd, `size_of__array` as 4th) — a `Surface-form leakage` that obscures the mismatch. On 64-bit, both values are 8 (sizeof pointer = 8, MAX = 8), so the bug is coincidentally masked. On 32-bit, sizeof pointer = 4, causing `heap_sort__opaque` to treat the array as 4 elements with an 8-byte stride — out-of-bounds memory access and incomplete sorting. The sibling call in `render_sprites_in__sprite_manager` (sprite_manager.c:344) passes count as 3rd and sizeof as 4th, confirming the correct order.

### Group D — GFX Context Helpers (`core/include/rendering/gfx_context_helpers.h`)

**D1. `GFX_CONTEXT_allocate_graphics_window_with__ui_manager`** — `Stub-real divergence` (hard compile error): calls `allocate_ui_manager_for__graphics_window(p_gfx_context, p_graphics_window)` with 2 arguments, but the function requires 3 (`Gfx_Context *`, `Graphics_Window *`, `Quantity__u16 max_quantity_of__ui_elements`), as confirmed by the definition at `graphics_window.c:92` and the sibling call at `ui_context.c:244-247`. The `uuid__u32` parameter is received but never used.

**D2. `GFX_CONTEXT_allocate_graphics_window_with__sprite_pool`** — `Stub-real divergence`: references three non-existent symbols: `Sprite_Pool` (undeclared type; codebase uses `Sprite_Manager`), `allocate_sprite_pool_from__sprite_manager` (never defined; the real function is `allocate_sprite_manager_from__sprite_context`), and `get_p_sprite_manager_from__gfx_context` (not defined; `Gfx_Context` contains a `Sprite_Context`, accessed via `get_p_sprite_context_from__gfx_context`). The allocated sprite pool is stored in a local `p_sprite_pool` that is never associated with the `Graphics_Window` (no `uuid_of__sprite_manager` linkage). Copy-paste debug messages reference the wrong function names.

**D3. `GFX_CONTEXT_allocate_graphics_window_with__ui_manager_and__sprite_pool`** — Same `Stub-real divergence` as D2: uses non-existent `Sprite_Pool` type, `get_p_sprite_manager_from__gfx_context`, and `allocate_sprite_pool_from__sprite_manager`. The `uuid__u32` parameter is unused. No max-quantity parameter is provided for sprite allocation (the real `allocate_sprite_manager_from__sprite_context` requires `Quantity__u32 max_quantity_of__sprites`). The window's `uuid_of__sprite_manager` field is never set, so even if the symbols existed, the sprite manager would not be linked to the window.

### Group E — Platform-Provided Graphics Windows (`core/source/rendering/graphics_window_manager.c`)

**E1. `allocate_or_get__platform_provided_graphics_windows`** — `State Desync` (offset accumulation bug): the offset for subsequent calls to `PLATFORM_get_provided_windows` is computed as `offset_of__graphics_window + quantity_of__total_overflowed_windows__u32` (accumulated overflow count), but it should advance by the number of windows already retrieved (the buffer capacity when overflow occurs). Per the `platform.h` documentation (lines 206-216), with 13 windows and buffer size 8: call 1 fills 8, returns 5 overflow; call 2 should start at offset 8, but the code starts at offset 0 + 5 = 5, re-retrieving windows 5-7 (duplicates) and overwriting the output buffer, losing windows 0-4. The caller `reset_platform_provided_graphics_windows` propagates the same bug by incrementing `index_of__current_acquisition` by `quantity_overflowed__u32` instead of the number of windows placed in the buffer. Additionally, the VLA buffers (`ptr_array_of__PLATFORM_graphics_windows`, `array_of__texture_flags`) are not zeroed between do-while iterations, relying on `PLATFORM_get_provided_windows` to zero its output (a portability concern for non-SDL backends).

---

## 2. Impact Assessment

### Sprite Context subsystem

- **`allocate_sprite_manager_from__sprite_context` (A1):** Called by `allocate_sprite_manager_for__graphics_window` (`graphics_window.c:104`), which sets `p_graphics_window->uuid_of__sprite_manager` to the window's own UUID and allocates a manager. If a caller passes `IDENTIFIER__UNKNOWN__u32` or a colliding UUID, the returned manager is silently unusable and unfindable by `get_p_sprite_manager_from__graphics_window` (inline in `graphics_window.h`), which is called from `f_graphics_window__default_render` (`graphics_window.c:546`) and `release_graphics_window_sprite_manager` (`graphics_window.c:366`). Correcting the UUID validation will cause these callers to receive NULL for invalid UUIDs — callers must handle this (currently they do check for NULL). The leaked-allocation issue in the collision path is currently masked because collisions are rare with random UUIDs.

- **`release_sprite_manager_from__sprite_context` (A2):** Called by `release_graphics_window_sprite_manager` (`graphics_window.c:344`), which is called from `reset_graphics_window` (`graphics_window.c:401`). The lower-bound UB and missing allocation check can cause crashes when a foreign or unmapped pointer is passed. The memory leak (not freeing `pM_pool_of__sprites` and `pM_sprite_render_records`) means every released sprite manager leaks its sprite pool and render-record array. Correcting the bounds check to use unsigned arithmetic (matching `release_game_action_from__game_action_manager`) will not change behavior for valid pointers. Adding member-pool freeing will change the release semantics — callers that rely on the current "mark deallocated but keep pools" behavior (if any) would need updating, though the review indicates the intent is to free pools.

- **`get_p_sprite_manager_by__uuid_from__sprite_context` (A4):** Called by `get_p_sprite_manager_from__graphics_window` (inline, `graphics_window.h`), which is called from `f_graphics_window__default_render` and `release_graphics_window_sprite_manager`. The division-by-zero crash occurs whenever a valid UUID is looked up on a context whose sprite managers have not been allocated — a legitimate state after `initialize_sprite_context`. Correcting this to return NULL (as the function's contract intends) will change the return from crash to NULL for these callers; they already check for NULL, so no cascading changes needed beyond the fix itself.

- **`release_sprite_managers_from__sprite_context` (A5):** Called during context teardown. The dangling pointer after `free` causes `is_sprite_managers_allocated_in__sprite_context` to return a dangling `true`, enabling double-free. Correcting this (nulling the pointer and resetting the count) is behavior-preserving for correct callers but prevents the double-free crash. The test `sprite_context__release_sprite_managers__clears_allocation` currently fails and will pass after the fix.

- **`allocate_sprite_managers_from__sprite_context` (A6):** Called during context initialization. The missing malloc-failure check causes a null dereference on OOM. Correcting this (checking malloc before using) is behavior-preserving for the success path. The test `sprite_context__allocate_sprite_managers__succeeds` is unaffected.

- **`get_p_sprite_animation_group_from__sprite_context` (A3):** Called by sprite animation group lookup code. The wrong enum constant currently works by coincidence (both enums have `__Unknown = 1`). Correcting it changes nothing at runtime but removes fragility. Adding the missing null check is behavior-preserving for valid callers.

### Sprite Manager subsystem

- **`f_sort_heuristic__sprite_render_record` (B1):** Called only from `render_sprites_in__sprite_manager` (`sprite_manager.c:344`) via `heap_sort__opaque`. The inverted `y` comparison causes sprites within the same z-layer to render in reversed vertical order (top sprites drawn last/on top of bottom sprites). Correcting the comparison direction changes render ordering — any visual output that currently relies on the inverted behavior will change. No callers outside `render_sprites_in__sprite_manager` use this comparator.

- **`allocate_sprite_from__sprite_manager` (B2):** Called by `allocate_p_sprite_from__graphics_window` (`graphics_window.c:534`), which is called from scene/entity code. The UB on the texture-allocation failure path (releasing an unallocated `p_PLATFORM_sprite`) can crash or corrupt memory. Correcting this (not calling `PLATFORM_release_sprite` when the texture allocation failed) is behavior-preserving for the success path. The missing bounds check on `p_sprite_render_record__last` is a latent OOB that triggers only when more sprites are allocated than `max_quantity_of__sprites`.

- **`get_p_sprite_by__uuid_from__sprite_manager` (B3):** Called from sprite lookup code (e.g., animation polling). The division-by-zero crash occurs on a freshly-initialized `Sprite_Manager` (default state after `allocate_sprite_managers_from__sprite_context`) when a valid UUID is looked up. Correcting this to return NULL matches the function's contract. The test `sprite_manager__get_p_sprite_by__uuid__returns_null_when_empty` allocates members first (so the pool is non-null), so it does not currently catch this crash.

- **`render_sprites_in__sprite_manager` (B4):** Called from `f_graphics_window__default_render` (`graphics_window.c:558`), which is the default render callback for graphics windows. The `>> 2` centering bug causes all sprites to render offset by an extra quarter-width to the right of their hitbox center. Correcting to `>> 1` changes sprite positioning on screen — any visual layout relying on the current offset will shift. The missing null check on `pM_sprite_render_records` and the OOB loop risk are latent issues. Note: the `heap_sort__opaque` call in this function (line 344) passes count as 3rd and sizeof as 4th, which matches the implementation's parameter usage — this call is correct (unlike C9).

### Graphics Window Manager subsystem

- **`initialize_graphics_window_manager` (C1):** Called from `initialize_gfx_context` (`gfx_context.c:9`), which is called during game initialization. The missing zeroing of `ptr_array_of__sorted_graphic_windows` causes `get_next_available_p_ptr_graphics_window_from__sorted_list` and `get_sorted_slot_of__graphics_window_from__sorted_list` to read stale pointers. The `parent__uuid == 0` (instead of `IDENTIFIER__UNKNOWN__u32`) causes `is_graphics_window_with__parent` to return TRUE for freshly-initialized windows, which is consumed by `f_sort_heuristic__p_graphics_window` (line 690), `is_graphics_window_a__parent` (line 77), and `is_graphics_window_a__descendant_of__this_graphics_window` (line 855). Correcting both issues changes the sort heuristic's behavior for newly allocated windows. Tests `graphics_window_manager__initialize__sorted_array_cleared` and `graphics_window_manager__is_graphics_window_with__parent__false_after_init` currently fail and will pass after the fix.

- **`_allocate_graphics_window_from__graphics_window_manager` (C2):** Called by `allocate_graphics_window_with__uuid_from__graphics_window_manager` (line 206, the public allocation entry point) and by `allocate_or_get__platform_provided_graphics_windows` (line 959). The flag-overwrite bug causes newly allocated windows to lack `COMPOSE_DIRTY`, so they may not be composited on their first frame (checked by `is_graphics_window_in_need_of__composition` at `graphics_window.c:409` and consumed by `compose_graphic_windows_in__graphics_window_manager`). The bit-overlap corruption causes windows with non-zero height texture flags to incorrectly report `IS_PLATFORM_PROVIDED`. Correcting this (removing the redundant assignment or reordering) restores correct composition and flag state.

- **`set_graphics_window_as__parent_to__this_graphics_window` (C3):** Called from window hierarchy setup code. The inverted validation allows reparenting a child that already has a different parent (silent data corruption) and incorrectly rejects reparenting to the same parent (false error). Correcting the loop variable to `p_graphics_window` restores the intended validation. No callers rely on the broken behavior.

- **`reset_children_of__graphics_window_from__graphics_window_manager` (C4):** Called from `reset_graphics_window` (`graphics_window.c:379`), which is called from `release_graphics_window_from__graphics_window_manager` (`graphics_window.c:386`) and `reset_platform_provided_graphics_windows`. The wrong-variable bug causes the parent (subtree root) to be released instead of children, corrupting the very window whose children are being processed and crashing on repeated matches. Correcting to `p_graphics_window__child` restores proper subtree teardown. Callers rely on correct teardown behavior, so this fix is behavior-preserving for correct usage.

- **`get_graphics_window__p_root_parent` (C5):** Called from `f_sort_heuristic__p_graphics_window` (line 690) and `is_graphics_window_a__descendant_of__this_graphics_window` (line 891). The null-deref in the broken-chain branch crashes whenever a window has a valid parent UUID that no longer maps to any window. Correcting this (orphaning the correct window) restores safe chain recovery. The depth-limit bug causes bounded-depth searches to terminate prematurely. Correcting it changes the depth at which the search stops for bounded inputs.

- **`get_graphics_windows_from__graphics_window_manager` (C6):** Called from window query code. The wrong return value on early exit returns the source-array index instead of the count written, causing callers to misinterpret how many windows were collected. Including unallocated windows may expose garbage kind values. Correcting both issues changes the return value and the contents of the output buffer for callers that rely on them.

- **`release_graphics_window_from__graphics_window_manager` (C7):** Called from `reset_children_of__graphics_window_from__graphics_window_manager` (line 344), `release_children_of__graphics_window_from__graphics_window_manager` (line 375), and the GFX_CONTEXT helpers in `gfx_context_helpers.h`. The null-deref on a missing sorted slot crashes on double-release or sorted-list corruption. Correcting this (null check before dereference) prevents crashes. No callers rely on the crash behavior.

- **`is_graphics_window_NOT_from__this_graphics_window_manager` (C8):** Called from `set_graphics_window_as__parent_to__this_graphics_window` (lines 238, 244). The UB on the failure path is currently masked because both windows are expected to originate from the same manager. Correcting this (e.g., using pointer comparison within the array bounds) is behavior-preserving for the happy path but makes the failure path sound.

- **`sort_graphic_windows_in__graphic_window_manager` (C9):** Called from `_allocate_graphics_window_from__graphics_window_manager` (line 187), `set_graphics_window_as__parent_to__this_graphics_window` (line 276), and `release_graphics_window_from__graphics_window_manager` (line 410). On 64-bit, the swapped arguments are coincidentally equivalent (both 8). On 32-bit, the swap causes OOB access and incomplete sorting. Correcting the argument order is behavior-preserving on 64-bit (no change) and fixes OOB on 32-bit. Additionally, the `heap_sort__opaque.h` header has misleading parameter names (`size_of__type` as 3rd, `size_of__array` as 4th) that contradict the implementation (`length_of__array` as 3rd, `size_of__type` as 4th) — this `Surface-form leakage` should be corrected in the header to prevent future confusion.

### GFX Context Helpers

- **`GFX_CONTEXT_allocate_graphics_window_with__ui_manager` (D1):** Not currently included/invoked anywhere in the core or SDL/NDS backends (the `gfx_context_helpers.h` header is not included by any `.c` file). If included, it produces a hard compile error. Correcting the argument count (adding `max_quantity_of__ui_elements`) makes it compilable. The `uuid__u32` parameter being unused is a design question — the graphics window allocation generates its own UUID internally.

- **`GFX_CONTEXT_allocate_graphics_window_with__sprite_pool` (D2) and `GFX_CONTEXT_allocate_graphics_window_with__ui_manager_and__sprite_pool` (D3):** Same as D1 — not currently included anywhere. Both reference non-existent types/functions (`Sprite_Pool`, `allocate_sprite_pool_from__sprite_manager`, `get_p_sprite_manager_from__gfx_context`). Correcting requires replacing these with `Sprite_Manager`, `allocate_sprite_manager_from__sprite_context` (or `allocate_sprite_manager_for__graphics_window`), and `get_p_sprite_context_from__gfx_context`, plus adding a max-quantity parameter and linking the manager to the window's `uuid_of__sprite_manager` field.

### Platform-Provided Graphics Windows

- **`allocate_or_get__platform_provided_graphics_windows` (E1):** Called from `setup_platform_provided_graphics_windows` (line 994), `itterate_platform_graphics_windows` (line 1015), and `reset_platform_provided_graphics_windows` (line 927). The offset bug causes duplicate window retrieval and loss of earlier windows when the platform has more windows than the buffer capacity. Correcting the offset to advance by retrieved count (not overflow count) changes the iteration order and completeness. The caller `reset_platform_provided_graphics_windows` also needs the same correction (`index_of__current_acquisition += quantity_overflowed__u32` → advance by retrieved count).

---

## 3. Resolution Assessment

### Group A — Sprite Context

**A1. `allocate_sprite_manager_from__sprite_context`** (`sprite_context.c:53-80`):
- Add `is_identifier_u32__invalid(uuid_of__sprite_manager)` check (return NULL if invalid), matching the precedent in `allocate_sprite_from__sprite_manager`.
- In the collision path, if `get_next_available__allocation_in__contiguous_array` returns an already-allocated slot, free the old `pM_pool_of__sprites` and `pM_sprite_render_records` before `initialize_sprite_manager` zeroes the pointers.
- No caller changes needed (callers already check for NULL return).

**A2. `release_sprite_manager_from__sprite_context`** (`sprite_context.c:82-103`):
- Fix the bounds check: store `p_sprite_manager - p_sprite_context->pM_sprite_managers` in a `u32` (matching `release_game_action_from__game_action_manager`), or add an explicit lower-bound guard `p_sprite_manager >= p_sprite_context->pM_sprite_managers`.
- Add `is_sprite_managers_allocated_in__sprite_context(p_sprite_context)` check before dereferencing `pM_sprite_managers`.
- Free `p_sprite_manager->pM_pool_of__sprites` and `p_sprite_manager->pM_sprite_render_records` before marking the slot deallocated (matching `release_sprite_from__sprite_manager`'s pattern of freeing platform resources first).
- Fix debug messages: `release_sprite_from__sprite_context` → `release_sprite_manager_from__sprite_context`.
- No caller changes needed.

**A3. `get_p_sprite_animation_group_from__sprite_context`** (`sprite_context.h:96-108`):
- Change `Sprite_Animation_Kind__Unknown` to `Sprite_Animation_Group_Kind__Unknown` in the range check.
- Add the standard `NDEBUG` null check on `p_sprite_context` (matching all sibling accessors).
- No caller changes needed.

**A4. `get_p_sprite_manager_by__uuid_from__sprite_context`** (`sprite_context.h:30-36`):
- Add `is_sprite_managers_allocated_in__sprite_context(p_sprite_context)` guard (return NULL if unallocated), matching `allocate_sprite_manager_from__sprite_context`.
- Add the standard `NDEBUG` null check on `p_sprite_context`.
- No caller changes needed (callers already handle NULL).

**A5. `release_sprite_managers_from__sprite_context`** (`sprite_context.c:39-47`):
- After `free(p_sprite_context->pM_sprite_managers)`, set `p_sprite_context->pM_sprite_managers = 0` and `p_sprite_context->max_quantity_of__sprite_managers = 0`.
- For full `Conservation Law` compliance, iterate the array and free each manager's `pM_pool_of__sprites` and `pM_sprite_render_records` before freeing the array (requires fixing A2 first so per-manager release is correct).
- No caller changes needed.

**A6. `allocate_sprite_managers_from__sprite_context`** (`sprite_context.c:10-37`):
- Move `max_quantity_of__sprite_managers` assignment after the malloc-success check.
- Check `malloc` return for NULL before entering the initialization loop; if NULL, return `false` without mutating `max_quantity_of__sprite_managers`.
- Add null check on `p_sprite_context` (matching the codebase convention or adding `#ifndef NDEBUG` guard).
- Add zero-quantity check (return `false` if `quantity_of__sprite_managers == 0`).
- No caller changes needed.

### Group B — Sprite Manager

**B1. `f_sort_heuristic__sprite_render_record`** (`sprite_manager.c:244-272`):
- Fix the `y` comparison: when `one.y < two.y`, return `-1` (not `+1`) so that higher-on-screen sprites sort first in ascending-y order.
- Return `0` for equal elements (both z and y equal) instead of falling through to `return -1`, to satisfy the strict weak ordering contract.
- No caller changes needed (only called from `render_sprites_in__sprite_manager`).

**B2. `allocate_sprite_from__sprite_manager`** (`sprite_manager.c:85-145`):
- In the `PLATFORM_allocate_texture` failure path, remove the `PLATFORM_release_sprite(p_gfx_context, p_sprite->p_PLATFORM_sprite)` call — `p_PLATFORM_sprite` has not been allocated yet at that point.
- Add a bounds check before writing to `p_sprite_render_record__last`: verify `p_sprite_manager->p_sprite_render_record__last < p_sprite_manager->pM_sprite_render_records + p_sprite_manager->max_quantity_of__sprites` before the write-and-increment.
- No caller changes needed.

**B3. `get_p_sprite_by__uuid_from__sprite_manager`** (`sprite_manager.c:372-389`):
- Add a guard: `if (!p_sprite_manager->pM_pool_of__sprites || !p_sprite_manager->max_quantity_of__sprites) { return 0; }` before calling `dehash_identitier_u32_in__contigious_array`, matching `clear_p_sprites_in__sprite_manager`.
- No caller changes needed (callers already handle NULL).

**B4. `render_sprites_in__sprite_manager`** (`sprite_manager.c:274-365`):
- Fix the centering offset: change `>> 2` to `>> 1`.
- Add a null check on `p_sprite_manager->pM_sprite_render_records` before the early guard `if (!p_sprite_render_record->p_sprite) return;`.
- The `heap_sort__opaque` call (line 344) is correct (count as 3rd, sizeof as 4th) — no change needed. (This contrasts with C9 where the call is swapped.)
- No caller changes needed.

### Group C — Graphics Window Manager

**C1. `initialize_graphics_window_manager`** (`graphics_window_manager.c:95-104`):
- Add `memset(p_graphics_window_manager->ptr_array_of__sorted_graphic_windows, 0, sizeof(Graphics_Window*) * MAX_QUANTITY_OF__GRAPHICS_WINDOWS)` to zero the sorted pointer array.
- After `initialize_serialization_header__contiguous_array` (which memsets to 0), explicitly set each window's `graphics_window__parent__uuid = IDENTIFIER__UNKNOWN__u32`, OR change the memset to use `IDENTIFIER__UNKNOWN__u32` for the parent UUID field. The cleaner approach: after the existing initialization, loop over all windows and set `graphics_window__parent__uuid = IDENTIFIER__UNKNOWN__u32`.
- Tests `graphics_window_manager__initialize__sorted_array_cleared` and `graphics_window_manager__is_graphics_window_with__parent__false_after_init` will pass after the fix. No caller changes needed.

**C2. `_allocate_graphics_window_from__graphics_window_manager`** (`graphics_window_manager.c:107-191`):
- Remove the line `p_graphics_window__available->graphics_window__flags = texture_flags_for__gfx_window;` (line 177-179). The dimensions are already captured in `width_of__graphics_window__u32` and `height_of__graphics_window__u32`. The `COMPOSE_DIRTY` flag set by `set_graphics_window_as__in_need_of__composition` and `IS_ENABLED` set by `set_graphics_window_as__enabled` will no longer be overwritten.
- No caller changes needed.

**C3. `set_graphics_window_as__parent_to__this_graphics_window`** (`graphics_window_manager.c:226-278`):
- In the validation loop, change `is_graphics_window_a__child_of__this_graphics_window(p_graphics_window__child, p_graphics_window__parent)` to `is_graphics_window_a__child_of__this_graphics_window(p_graphics_window__child, p_graphics_window)` (using the per-iteration variable).
- Remove the now-unused `p_graphics_window` variable or use it properly.
- No caller changes needed.

**C4. `reset_children_of__graphics_window_from__graphics_window_manager`** (`graphics_window_manager.c:321-354`):
- Change `!is_graphics_window__platform_provided(p_graphics_window)` to `!is_graphics_window__platform_provided(p_graphics_window__child)`.
- Change `release_graphics_window_from__graphics_window_manager(p_game, p_graphics_window)` to `release_graphics_window_from__graphics_window_manager(p_game, p_graphics_window__child)`.
- No caller changes needed.

**C5. `get_graphics_window__p_root_parent`** (`graphics_window_manager.c:629-710`):
- Store the lookup result in a separate variable: `Graphics_Window *p_parent = get_graphics_window__p_parent(...)`. On null, orphan `p_graphics_window__current_parent` (the original, not the null result): `p_graphics_window__current_parent->graphics_window__parent__uuid = IDENTIFIER__UNKNOWN__u32`.
- Fix the depth-limit underflow guard: replace `MAX_QUANTITY_OF__GRAPHICS_WINDOWS >= --depth_to_search` with a proper check, e.g., `if (depth_to_search == 0) break;` before decrementing, or compare against the original depth limit.
- No caller changes needed.

**C6. `get_graphics_windows_from__graphics_window_manager`** (`graphics_window_manager.c:414-442`):
- Change the early-exit return from `return index_of__graphics_window;` to `return index_of__gfx_window_in__ptr_array;`.
- Add `is_graphics_window__allocated(p_graphics_window)` check before including a window in the output buffer.
- No caller changes needed (the corrected return value is what callers expect).

**C7. `release_graphics_window_from__graphics_window_manager`** (`graphics_window_manager.c:381-412`):
- Add a null check on `p_ptr_sorted_graphics_window_slot` before `*p_ptr_sorted_graphics_window_slot = 0;`. If NULL, log an error and skip the sorted-slot clearing (or handle gracefully).
- Remove the redundant `get_p_gfx_context_from__game(p_game)` call (reuse the already-stored `p_gfx_context`).
- No caller changes needed.

**C8. `is_graphics_window_NOT_from__this_graphics_window_manager`** (`graphics_window_manager.c:220-228`):
- Rewrite the membership check to avoid UB on unrelated pointers. Use a defined comparison: check `p_graphics_window >= p_graphics_window_manager->graphics_windows && p_graphics_window < p_graphics_window_manager->graphics_windows + MAX_QUANTITY_OF__GRAPHICS_WINDOWS`. While pointer comparison of unrelated pointers is technically UB per C11, this is the standard pattern and is well-defined in practice on all mainstream platforms. Alternatively, use the index-based approach from `release_game_action_from__game_action_manager`.
- No caller changes needed.

**C9. `sort_graphic_windows_in__graphic_window_manager`** (`graphics_window_manager.c:625-638`):
- Swap the 3rd and 4th arguments to `heap_sort__opaque`: pass `MAX_QUANTITY_OF__GRAPHICS_WINDOWS` (count) as 3rd and `sizeof(Graphics_Window*)` (stride) as 4th, matching the implementation's parameter order (`length_of__array`, `size_of__type`).
- Additionally, correct the misleading parameter names in `heap_sort__opaque.h` to match the implementation (`length_of__array` as 3rd, `size_of__type` as 4th), or correct the implementation to match the header. The header should be authoritative for the public API; the implementation should be updated to match (rename parameters and update the body accordingly). This is a `Surface-form leakage` fix that prevents future confusion.
- No caller changes needed (behavior-preserving on 64-bit; fixes OOB on 32-bit).

### Group D — GFX Context Helpers

**D1. `GFX_CONTEXT_allocate_graphics_window_with__ui_manager`** (`gfx_context_helpers.h:18-50`):
- Add the missing third argument to `allocate_ui_manager_for__graphics_window`: `p_gfx_context, p_graphics_window, <max_quantity_of__ui_elements>`. The function needs a max-quantity parameter — either add it as a function parameter or use a default constant.
- The `uuid__u32` parameter is unused (window UUID is generated internally) — either use it or remove it.
- No callers currently exist (header not included anywhere), so no cascading changes.

**D2. `GFX_CONTEXT_allocate_graphics_window_with__sprite_pool`** (`gfx_context_helpers.h:118-155`):
- Replace `Sprite_Pool` with `Sprite_Manager`.
- Replace `get_p_sprite_manager_from__gfx_context` with `get_p_sprite_context_from__gfx_context` + `allocate_sprite_manager_from__sprite_context`.
- Replace `allocate_sprite_pool_from__sprite_manager` with `allocate_sprite_manager_from__sprite_context(p_sprite_context, uuid__u32, <max_quantity_of__sprites>)`.
- Associate the allocated manager with the window by setting `p_graphics_window->uuid_of__sprite_manager = uuid__u32` (matching `allocate_sprite_manager_for__graphics_window` in `graphics_window.c:104-108`).
- Add a max-quantity parameter.
- Fix copy-paste debug messages.
- No callers currently exist.

**D3. `GFX_CONTEXT_allocate_graphics_window_with__ui_manager_and__sprite_pool`** (`gfx_context_helpers.h:55-85`):
- Same fixes as D2, plus ensure the UI manager allocation also receives the correct max-quantity argument (same issue as D1).
- Associate the sprite manager with the window via `uuid_of__sprite_manager`.
- No callers currently exist.

### Group E — Platform-Provided Graphics Windows

**E1. `allocate_or_get__platform_provided_graphics_windows`** (`graphics_window_manager.c:908-986`):
- Track the number of windows placed in the buffer separately from the overflow count. When overflow occurs (buffer full), advance the offset by `quantity_of__ptrs_in_buffer__u32` (the number of windows retrieved in this batch), not by the overflow count.
- Change `offset_of__graphics_window + quantity_of__total_overflowed_windows__u32` to use a separate `quantity_of__windows_placed_in__buffer__u32` accumulator that increments by `quantity_of__ptrs_in_buffer__u32` when overflow occurs.
- Fix the caller `reset_platform_provided_graphics_windows` (line 927): change `index_of__current_acquisition += quantity_overflowed__u32` to advance by the number of windows actually placed in the buffer.
- Zero the VLA buffers between do-while iterations (or document the dependency on `PLATFORM_get_provided_windows` zeroing its output).
- No external caller changes needed (callers of `setup_platform_provided_graphics_windows` and `itterate_platform_graphics_windows` are unaffected by the internal offset fix).

---

## 4. Test Verification Checklist

### Existing tests that need updating or will be affected:

**Sprite Context tests** (`test_suite_rendering_sprite_context.c`):
- `sprite_context__release_sprite_managers__clears_allocation` — currently FAILS. Asserts `is_sprite_managers_allocated_in__sprite_context(&context)` is false after release. Will PASS after A5 fix (nulling `pM_sprite_managers`).
- `sprite_context__get_p_sprite_manager_by__uuid__returns_null_when_not_found` — allocates managers first (pool is non-null), so does not catch the A4 division-by-zero crash. Needs a new test case for the unallocated-pool state.
- **Missing test:** `sprite_context__get_p_sprite_manager_by__uuid__on_unallocated_pool__returns_null` — should verify NULL return (not crash) when managers are not allocated.
- **Missing test:** `sprite_context__allocate_sprite_managers__malloc_failure__returns_false` — `Property Based Testing` for the OOM path (A6).
- **Missing test:** `sprite_context__release_sprite_manager__frees_member_pools` — `Round Trip Check` for the allocate→release lifecycle (A2).

**Sprite Manager tests** (`test_suite_rendering_sprite_manager.c`):
- `sprite_manager__get_p_sprite_by__uuid__returns_null_when_empty` — allocates members first (pool is non-null), so does not catch the B3 division-by-zero crash. Needs a new test for the unallocated-pool state.
- **Missing test:** `sprite_manager__get_p_sprite_by__uuid__on_unallocated_pool__returns_null` — verify NULL return (not crash) when `pM_pool_of__sprites` is NULL (B3).
- **Missing test:** `sprite_manager__allocate_sprite_from__sprite_manager__texture_failure__no_release_sprite` — `Equivalence Check` for the error path (B2).
- **Missing test:** `sprite_manager__render_sprites__centers_sprite_on_hitbox` — `Golden-file Test` or position assertion for the `>> 1` centering fix (B4).
- **Missing test:** `sprite_manager__f_sort_heuristic__sprite_render_record__ascending_y` — `Property Based Testing` for the comparator (B1).

**Graphics Window Manager tests** (`test_suite_rendering_graphics_window_manager.c`):
- `graphics_window_manager__initialize__sorted_array_cleared` — currently FAILS. Will PASS after C1 fix (zeroing `ptr_array_of__sorted_graphic_windows`).
- `graphics_window_manager__is_graphics_window_with__parent__false_after_init` — currently FAILS. Will PASS after C1 fix (setting `parent__uuid = IDENTIFIER__UNKNOWN__u32`).
- **Missing test:** `graphics_window_manager__initialize__parent_uuid_is_unknown` — assert `parent__uuid == IDENTIFIER__UNKNOWN__u32` after init (C1).
- **Missing test:** `graphics_window_manager__sort__arguments_correct_order` — `Equivalence Check` verifying `heap_sort__opaque` receives count as 3rd and sizeof as 4th (C9).
- **Missing test:** `graphics_window_manager__release__null_sorted_slot__no_crash` — `Fuzzing` for the null-sorted-slot path (C7).
- **Missing test:** `graphics_window_manager__get_graphics_windows__returns_count_not_index` — verify return value equals windows written, not source index (C6).
- **Missing test:** `graphics_window_manager__set_parent__rejects_already_parented_child` — verify the corrected validation (C3).
- **Missing test:** `graphics_window_manager__reset_children__releases_child_not_parent` — verify correct target (C4).
- **Missing test:** `graphics_window_manager__root_parent__null_deref_fixed` — verify orphaning works without crash (C5).
- **Missing test:** `graphics_window_manager__allocate__compose_dirty_flag_preserved` — verify `COMPOSE_DIRTY` is set after allocation (C2).
- **Missing test:** `graphics_window_manager__allocate_or_get__platform_provided__correct_offset` — `Property Based Testing` with >8 platform windows (E1).

### Test impact summary:
- **Tests that currently fail and will pass after fixes:** 4 (sprite_context__release_sprite_managers__clears_allocation, graphics_window_manager__initialize__sorted_array_cleared, graphics_window_manager__is_graphics_window_with__parent__false_after_init, and the previously-failing sprite_context test)
- **Tests that need new cases for edge cases:** 8+ (division-by-zero on unallocated pools, null-sorted-slot, argument order, centering, comparator ordering, offset accumulation)
- **Tests that need assertion updates:** 0 (no existing tests assert on broken behavior)
- **Blast radius for tests:** Medium — 4 existing tests currently fail (indicating the bugs are real and observable), and 8+ new test cases are needed for edge cases and boundary conditions.

---

## 5. Blast Radius Summary

- **Files requiring changes:** 5 source files + 1 header + 1 sort header + 2 test files
  - `core/source/rendering/sprite_context.c` (A1, A2, A5, A6)
  - `core/include/rendering/sprite_context.h` (A3, A4)
  - `core/source/rendering/sprite_manager.c` (B1, B2, B3, B4)
  - `core/source/rendering/graphics_window_manager.c` (C1–C9, E1)
  - `core/include/rendering/gfx_context_helpers.h` (D1, D2, D3)
  - `core/include/sort/heap_sort__opaque.h` (C9 — parameter name correction)
  - `core/source/rendering/graphics_window.c` (C4 caller — no change needed, already correct)
  - `tests/core/source/rendering/test_suite_rendering_sprite_context.c` (new test cases)
  - `tests/core/source/rendering/test_suite_rendering_graphics_window_manager.c` (new test cases)
  - `tests/core/source/rendering/test_suite_rendering_sprite_manager.c` (new test cases)

- **Behavior preservation for current callers:**
  - Most fixes are behavior-preserving for correct callers (UB elimination, missing validation, missing cleanup).
  - **Non-preserving changes:** B1 (render order changes — sprites within a z-layer will render in correct vertical order), C1 (sort heuristic behavior changes for newly-initialized windows — `is_graphics_window_with__parent` now correctly returns false), C2 (newly allocated windows will have `COMPOSE_DIRTY` set and correct flag state), C6 (return value changes on early exit), E1 (platform window iteration order/completeness changes).
  - **Compile-breaking changes:** D1, D2, D3 (currently non-compilable if included).

- **Phased approach recommended:**
  - **Phase 1 (High priority — UB/crash fixes):** A2 (bounds check + null deref), A4 (division by zero), A5 (dangling pointer/double-free), A6 (malloc null deref), B2 (release of unallocated resource), B3 (division by zero), C5 (null deref), C7 (null deref), C8 (pointer subtraction UB). These are crash/corruption bugs with no behavioral change for correct callers.
  - **Phase 2 (Correctness fixes — behavior changes):** A1 (UUID validation), B1 (sort direction), B4 (centering offset), C1 (init completeness), C2 (flag overwrite), C3 (parent validation), C4 (child release), C6 (return value), C9 (sort arguments), E1 (offset accumulation). These change observable behavior but are the intended fixes.
  - **Phase 3 (Compile fixes):** D1, D2, D3 (GFX_CONTEXT helpers — non-compilable if included).
  - **Phase 4 (Test updates):** Add the new test cases, update failing tests.

- **De facto contracts that would be invalidated:**
  - `is_graphics_window_with__parent` returning TRUE for freshly-initialized windows (C1) — relied upon by `f_sort_heuristic__p_graphics_window` and `is_graphics_window_a__descendant_of__this_graphics_window`. Correcting this changes sort behavior for new windows.
  - `release_sprite_manager_from__sprite_context` not freeing member pools (A2) — if any caller relies on the manager slot being reusable without re-allocating members, this contract is invalidated.
  - `get_graphics_windows_from__graphics_window_manager` returning source index instead of count (C6) — if any caller interprets the return value as a count, it would currently get wrong values for partial fills.
  - The `heap_sort__opaque.h` header parameter naming (`Surface-form leakage`) — the misleading names may have caused the C9 bug and could cause future confusion. Correcting the header is a documentation fix but should be done alongside the C9 fix.
