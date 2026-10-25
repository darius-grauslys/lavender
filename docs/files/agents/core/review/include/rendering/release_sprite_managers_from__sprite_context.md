# Release Sprite Managers From Sprite Context

## 1. Header

**Function name:** `release_sprite_managers_from__sprite_context`
**File of origin:** `core/source/rendering/sprite_context.c` (lines 39-47)

## 2. Semantic

Releases (tears down) the contiguous `Sprite_Manager` array owned by a `Sprite_Context`: validates that the managers pool is currently allocated, calls `free` on it, and — per Lavender release semantics (the counterpart to allocate — should restore the managers-related bookkeeping to the struct's initial/cleaned state so the context can be safely re-allocated or returned to a pool).

## 3. Pre-conditions

1. `p_sprite_context` must be a non-null pointer to a valid `Sprite_Context`. There is no null guard on `p_sprite_context` itself; it is dereferenced indirectly via `is_sprite_managers_allocated_in__sprite_context`, so a null value is undefined behavior. This matches the codebase-wide convention (caller responsibility), consistent with `allocate_sprite_managers_from__sprite_context` and the inline accessors in `sprite_context.h`, so it is treated as caller responsibility rather than a defect here.
2. `p_sprite_context->pM_sprite_managers` should point to a live (not already freed) heap allocation of `Sprite_Manager * max_quantity_of__sprite_managers`, or be null. When null, the guarded allocation check short-circuits and the function returns early (no harm). When non-null, it must be a valid pointer previously returned by `malloc` (i.e., allocated via `allocate_sprite_managers_from__sprite_context`) so that `free` is well-defined.

## 4. Post-conditions

1. **Intended:** `p_sprite_context->pM_sprite_managers` is set to null and `p_sprite_context->max_quantity_of__sprite_managers` is reset to 0, so the context's managers subsystem is returned to its initial (cleaned) state and `is_sprite_managers_allocated_in__sprite_context(p_sprite_context)` returns false.
2. **Intended:** The heap allocation previously held by `p_sprite_context->pM_sprite_managers` is freed.
3. **If the allocation check fails (pointer null):** the function returns early, emits a `debug_error`, and leaves the context unchanged.
4. **Actual (current implementation):** `p_sprite_context->pM_sprite_managers` is NOT set to null after `free` and `max_quantity_of__sprite_managers` is NOT reset — the intended post-conditions are violated (see Implementation Correctness, Issue 1).

## 5. Correctness Verdict

**Incorrect**

## 6. Semantic Alignment

The happy-path behavior — guarding against a no-op release and calling `free` on the managers array — is correct in spirit. However, the release is incomplete:

- After `free`, `p_sprite_context->pM_sprite_managers` retains its former (now dangling) address instead of being nulled. Per Lavender semantics, release is the counterpart to allocate and should restore the struct to its initial/cleaned conditions; the dangling pointer breaks that contract. The existing test `sprite_context__release_sprite_managers__clears_allocation` (test_suite_rendering_sprite_context.c:50-59) directly asserts `is_sprite_managers_allocated_in__sprite_context(&context)` is false after release, which requires `pM_sprite_managers == NULL`. With the current code that predicate still reads the dangling (non-null) pointer and returns true, so the test fails.
- `max_quantity_of__sprite_managers` is likewise left stale, so the managers bookkeeping is not fully restored to the post-`initialize_sprite_context` state (which that test also asserts: `max_quantity_of__sprite_managers == 0`).

This is not semantic drift in a computation, but an incompleteness of the teardown that violates the intended post-conditions and the established allocate → use → release → re-allocate lifecycle.

## 7. Implementation Correctness

- **Issue 1 (critical — dangling pointer / missing NULL reset after free):** After `free(p_sprite_context->pM_sprite_managers)` the field is never assigned `0`. Consequences:
  - `is_sprite_managers_allocated_in__sprite_context` returns a dangling `true` after release, which directly fails `sprite_context__release_sprite_managers__clears_allocation`.
  - The guard in a second call to `release_sprite_managers_from__sprite_context` passes (predicate is true), causing `free` on an already-freed pointer → undefined behavior (double free).
  - Fix: assign `p_sprite_context->pM_sprite_managers = 0;` after `free`. For full "return to initial conditions" semantics, also assign `p_sprite_context->max_quantity_of__sprite_managers = 0;` (mirroring `initialize_sprite_context` and satisfying its test's `max_quantity_of__sprite_managers == 0` expectation).

- **Issue 2 (memory leak — per-manager member pools):** As with the sibling `release_sprite_manager_from__sprite_context` (see its review, Issue 4), each `Sprite_Manager` entry owns heap allocations made by `allocate_sprite_manager__members` (`pM_pool_of__sprites`, `p_sprite_render_records`). This whole-context release only `free`s the managers array and never `free`s each manager's member pools. On context teardown these per-manager pools are leaked. The fix requires iterating the array and releasing each manager's members before `free` of the array — out of scope for the minimal NULL-reset fix, but a real leak.

- **Issue 3 (missing null check on `p_sprite_context`):** `p_sprite_context` is dereferenced without a null guard (via `is_sprite_managers_allocated_in__sprite_context`). This is consistent with the codebase convention (caller responsibility) and with `allocate_sprite_managers_from__sprite_context`, so it is "by design" here; noted for completeness.

- **Type compatibility:** `p_sprite_context->pM_sprite_managers` is `Sprite_Manager *`; `malloc` returns `void *` and the result is stored without an explicit cast — correct and idiomatic in C. `free` receives a `void *`-compatible pointer. No truncation or sign issues.

- **Undefined behavior:** Apart from the NULL-`p_sprite_context` case (caller responsibility) and the dangling-pointer/double-free above, there is no pointer arithmetic, no type punning, and no out-of-bounds access.

## 8. Side Effects

1. **Memory deallocation:** The heap block previously allocated for `p_sprite_context->pM_sprite_managers` (via `allocate_sprite_managers_from__sprite_context`) is freed.
2. **Intended mutation:** After release the context's managers fields should be `pM_sprite_managers = NULL` and `max_quantity_of__sprite_managers = 0` (returning the managers subsystem to its initial/cleaned state). **The current implementation fails to perform this mutation**, leaving a dangling `pM_sprite_managers` and a stale `max_quantity_of__sprite_managers`.
3. **Leaked side effect (missing):** No per-manager member pools (`pM_pool_of__sprites`, `p_sprite_render_records`) are freed; they are leaked on teardown.
4. No global state, file I/O, or callbacks are touched; the function does not free any other allocations owned by the context.
