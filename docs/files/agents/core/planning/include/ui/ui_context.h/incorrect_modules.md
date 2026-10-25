# Planning: populate_window_with__ui — Incorrect Modules

**Review source:** `agents/core/review/include/ui/ui_context.h/incorrect_modules.md`
**Reviewed entry:** `./populate_window_with__ui.md` — Correctness Verdict: Incorrect

**Source files reviewed (read-only):**
- `core/include/ui/ui_context.h` (declaration of `populate_window_with__ui`)
- `core/source/ui/ui_context.c` (definition of `populate_window_with__ui`, plus sibling callers `_open_ui_window`, `close_ui_window`)
- `core/include/defines.h` (typedef `f_UI_Window__Load`, line 1767 — the load callback contract)
- `core/include/ui/ui_window_record.h` (`is_ui_window_record__valid`)
- `core/include/rendering/graphics_window.h` (`get_p_sprite_manager_from__graphics_window`, `get_p_ui_manager_from__graphics_window`)
- `core/include/game.h` (`get_p_gfx_context_from__game` — dereferences `p_game`)
- `tests/core/source/ui/test_suite_ui_ui_context.c` (existing test suite)

---

## 1. Problem Identification

`populate_window_with__ui` (core/source/ui/ui_context.c:265) is flagged **Incorrect**. Three distinct defects:

1. **Hardcoded offset (`Translation Gap` / `Stub-real divergence`):** The function accepts `Index__u16 index_of__ui_element_offset__u16` but forwards a literal `0` as the final argument to `p_ui_window_record->f_ui_window__load(...)`. The callback contract — `f_UI_Window__Load` (core/include/defines.h:1767) — explicitly declares its fifth parameter as `Index__u16 index_of__ui_element_offset__u16`, so the parameter is part of the semantic contract. Hardcoding `0` constitutes a `Surface-form leakage`: the surface-level parameter is not faithfully translated into the callback invocation, silently defeating the caller's intent.

2. **Missing `p_game` precondition check (`Precondition` / `Boundary Condition`):** Unlike every sibling function in this file (`_open_ui_window`, `close_ui_window`, `release_p_ui_manager_from__ui_context`), `populate_window_with__ui` does not validate `p_game` in debug mode. It immediately calls `get_p_gfx_context_from__game(p_game)` (core/include/game.h:265), which dereferences `p_game` (`return &p_game->gfx_context`). A null `p_game` therefore causes undefined behavior. This violates the `Precondition` shared by the module's other entry points and is a `Boundary Condition` that `Static Analysis` would flag; a `Conservative` guard is warranted.

3. **Dead code (`Information Hiding` / `Spaghettification`):** `p_sprite_manager` is retrieved via `get_p_sprite_manager_from__graphics_window(p_game, p_graphics_window)` but is never referenced afterward. The local is dead code that adds a misleading dependency and obscures the function's true `Representation Invariant` (that only the UI manager and load callback are needed).

## 2. Impact Assessment

**Callers relying on the broken behavior:**
- The only in-tree caller is `_open_ui_window` (core/source/ui/ui_context.c:323), which forwards its own `index_of__ui_element_offset__u16` parameter. The inline wrappers `open_ui_window_with__this_uuid` and `open_ui_window` (core/include/ui/ui_context.h) pass `0`. End-to-end today the offset is *always* `0`, so no current core path observes a non-zero offset — but the API surface and the `f_UI_Window__Load` contract both expect a forwarded offset.
- `f_UI_Window__Load` callback implementations (registered via `register_ui_window_into__ui_context`) consume the offset to place UI elements at the correct base index. These implementations live in platform code (the core registrar `ui_window_registrar.c` is empty, GEN-placeholdered). Any callback that reads the offset parameter currently receives `0` regardless of caller intent.

**Coupling / de facto contract:**
- The hardcoded `0` is a `Coupled` assumption: load callbacks may have come to depend on always receiving offset `0`. Correcting the forwarding invalidates that de facto contract for any platform-side callback that assumed `offset == 0`. This is the primary blast-radius risk.
- The missing `p_game` guard is `Coupled` to the assumption that callers always pre-validate `p_game`. `_open_ui_window` does, but `populate_window_with__ui` is a public API (declared in the header), so direct external callers could pass null. Adding the guard restores the module's `Single Source of Truth (SSOT)` for input validation.

**What correcting it invalidates:**
- Any load callback that silently relied on `offset == 0` (the broken behavior) will now receive the caller-provided offset. Such callbacks must be audited to confirm they handle a non-zero offset correctly (the intended `Faithful` behavior).
- Removing the unused `p_sprite_manager` retrieval has no behavioral impact (the value was never consumed), so it is safe with respect to `Conservation Law` of state.

## 3. Resolution Assessment

**Plan to resolve:**

1. **Forward the offset (`Translation Gap` fix):** Replace the hardcoded `0` in the `f_ui_window__load(...)` invocation with `index_of__ui_element_offset__u16`. This restores `Lossless` / `Faithful` translation of the parameter per the `f_UI_Window__Load` contract.
   - Implementation change: one line in `populate_window_with__ui`.
   - Callers: `_open_ui_window` already forwards the correct value; no change needed. The inline `open_ui_window*` wrappers pass `0`, which remains valid (offset 0 is a legitimate value).
   - No header change required — the signature is already correct.

2. **Add the `p_game` `Precondition` guard:** Insert a `#ifndef NDEBUG` null check for `p_game` at the top of `populate_window_with__ui`, mirroring `_open_ui_window` / `close_ui_window` / `release_p_ui_manager_from__ui_context`. On failure, emit a `debug_error` and `return false`.
   - Implementation change: ~5 lines.
   - Callers: behavior-preserving for valid (non-null) `p_game`; only adds a defensive early-return for the null case.

3. **Remove dead code:** Delete the `Sprite_Manager *p_sprite_manager = get_p_sprite_manager_from__graphics_window(...)` local and its (now-unused) retrieval. This also removes a latent `Coupled` dependency on the sprite subsystem that `populate_window_with__ui` does not otherwise use, improving `Information Hiding`.
   - Implementation change: delete 3 lines.
   - No caller impact (value was never used).

**Phased approach:** Not required for the core fix — all three changes are localized to `populate_window_with__ui`. However, a **platform-side audit** of `f_UI_Window__Load` callback implementations is recommended as a follow-up to confirm they correctly handle a non-zero `index_of__ui_element_offset__u16` (the previously-suppressed path).

## 4. Test Verification Checklist

**Existing tests surveyed:** `tests/core/source/ui/test_suite_ui_ui_context.c` only tests `initialize_ui_context`. There are **no** tests for `populate_window_with__ui`, `open_ui_window`, or `close_ui_window`. Therefore:
- No existing assertions assert on the broken behavior (offset always `0`), so the fix does **not** invalidate existing tests.
- No existing assertions cover the `p_game == null` path.

**New tests needed:**
- **`Property Based Testing`** — invariant that the offset forwarded to the load callback equals the `index_of__ui_element_offset__u16` argument passed to `populate_window_with__ui`. A stub `f_UI_Window__Load` records the received offset; assert equality across a range of offset inputs.
- **`Boundary Condition`** / null-input test — invoke `populate_window_with__ui` with `p_game == null` (debug build) and assert it returns `false` without dereferencing (no crash / no `debug_abort`).
- **`Round Trip Check`** — for a registered UI window, verify that `populate_window_with__ui` sets `the_kind_of__window`, sets `GRAPHICS_WINDOW__FLAG__IS_ENABLED`, and sets `GRAPHICS_WINDOW__FLAG__COMPOSE__DIRTY`, then `close_ui_window` clears the window, preserving the window-record lifecycle.
- **`Equivalence Check`** — confirm that passing offset `0` reproduces the prior behavior (callback receives `0`), ensuring the `open_ui_window*` wrappers remain behavior-compatible.

**Blast radius for tests:** Low — no existing tests assert on the broken behavior. A new test file (e.g., `test_suite_ui_ui_context__populate.c`) or additions to the existing suite should cover the three invariants above.

## 5. Blast Radius Summary

- **Files needing changes:** 1 — `core/source/ui/ui_context.c` (the definition of `populate_window_with__ui`). The header `core/include/ui/ui_context.h` needs **no** change (signature already correct).
- **Behavior-preserving for current callers?** Yes for `_open_ui_window` (forwards correct offset; the only in-tree caller). The offset-forwarding change is semantically correct and matches the `f_UI_Window__Load` contract, but it **does** change the value observed by platform-side load callbacks (from always-`0` to caller-provided).
- **De facto contracts invalidated:** The implicit "offset is always `0`" assumption held by any platform-side `f_UI_Window__Load` implementation. These must be audited.
- **Phased approach:** Core fix is localized (single function). A **platform-side audit** of load callbacks is the recommended follow-up phase before relying on non-zero offsets in production paths.
- **Overall blast radius:** Low-to-Medium (1 core source file; platform-side callback audit required).
