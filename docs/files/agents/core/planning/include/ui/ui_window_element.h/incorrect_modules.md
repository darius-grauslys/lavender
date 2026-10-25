# Planning: ui_window_element.h — Incorrect Modules

**Review source:** `agents/core/review/include/ui/ui_window_element.h/incorrect_modules.md`

**Source files reviewed (read-only):**
- `core/include/ui/ui_window_element.h`
- `core/source/ui/ui_window_element.c`
- `core/include/ui/ui_element.h`
- `core/include/defines.h` (`UI_Element`, `Graphics_Window`, `UI_Context`, handler typedefs)
- `core/include/defines_weak.h` (`enum UI_Element_Kind`)
- `core/source/ui/ui_context.c` (`_open_ui_window`, `open_ui_window_with__this_uuid_and__parent_uuid`)
- `tests/core/source/ui/test_suite_ui_ui_window_element.c`

---

## 1. Problem Identification

Two functions in `core/source/ui/ui_window_element.c` are flagged **Incorrect**. Both belong to the window-element subsystem. The `_m_ui_window_element__transformed_handler` is not itself flagged, but it shares defects with the flagged `_m_ui_window_element__update` and is addressed as a dependency in §3.

### 1.1 `_m_ui_window_element__update` — Release-Build Null-Dereference (UB)
The null checks on `p_graphics_window` and `p_ui_manager` are wrapped in `#ifndef NDEBUG`, so they execute **only in debug builds**. In release builds a failed UUID lookup or UI-Manager resolution is not checked, and the following dereferences (`get_p_ui_manager_from__graphics_window` reads `p_graphics_window->uuid_of__ui_manager`; `poll_ui_manager__update` is called on `p_ui_manager`) are **undefined behavior** on a null pointer. This is a **Boundary Condition** / **Precondition** violation: the function is a runtime handler (`m_UI_Clicked/Dragged/Dropped/Held`) and cannot assume its inputs are always valid, yet the guard that enforces that **Invariant** is compiled out in production.

### 1.2 `_m_ui_window_element__update` — Redundant UUID Re-derivation
The function accepts `Graphics_Window *p_gfx_window` (the window handed to it by the dispatch mechanism) but ignores it, re-deriving the window via `get_p_graphics_window_by__uuid_from__graphics_window_manager(...)` on the element's UUID. The re-derived window is the *same* object the dispatcher already supplied, so this is a **Translation Gap** (the provided parameter is not wired to the implementation) and a **Coupled** Law-of-Demeter chain (`game → gfx_context → graphics_window_manager → window`). It also adds a spurious failure mode: the UUID lookup can fail even when `p_gfx_window` is valid.

### 1.3 `_m_ui_window_element__update` — Misleading Debug Error Strings (Surface-form Leakage)
Both `debug_error` calls emit the literal `"_m_ui_window_element__clicked_handler"` instead of the real function name `"_m_ui_window_element__update"`. This is a copy-paste **Surface-form leakage** that misdirects debugging. The same wrong string appears in `_m_ui_window_element__transformed_handler` (`ui_window_element.c:66`).

### 1.4 `initialize_ui_element_as__window_element_and__open_window` — Kind Mismatch
The name commits to tagging the element `UI_Element_Kind__Window`, but the implementation passes `UI_Element_Kind__Button` to `initialize_ui_element`. This is a **Non-Injective Translation** at the type level: a window element and a button element become indistinguishable by `the_kind_of_ui_element__this_is`, breaking any downstream dispatch keyed on kind (e.g. `is_ui_element_of__this_kind`).

### 1.5 `initialize_ui_element_as__window_element_and__open_window` — Unlinked Graphics Window (State Desync)
The `UI_Element` union has a `UI_Window` variant holding `Graphics_Window *p_ui_window__graphics_window`, but the function **never assigns** it. The opened `p_graphics_window` is not linked back to the element, so the element holds no reference to the window it represents — a **State Desync**. No reader of this field was found in `core/source/ui/*` or `core/source/rendering/graphics_window.c`, so today the field is dead weight left at its memset-zero (null) value.

### 1.6 `initialize_ui_element_as__window_element_and__open_window` — Ordering Bug (Postcondition Violation)
`initialize_ui_element` is called **before** the null check on `p_graphics_window`. `initialize_ui_element` memsets the element and sets kind + default handlers. If `open_ui_window_with__this_uuid_and__parent_uuid` returns NULL, the element is *still* fully re-initialized (wrong kind, default handlers) — an inconsistent **Representation Invariant** state. The null check / early return must precede `initialize_ui_element` so a failed open leaves the element untouched.

---

## 2. Impact Assessment

### 2.1 Dependents on the broken behavior
| Component | Location | Dependency on broken behavior | Effect of correcting it |
|---|---|---|---|
| clicked/dragged/dropped/held handler registration | `core/include/ui/ui_element.h` (inline setters) + `ui_window_element.c:108-121` | All four input events funnel into `_m_ui_window_element__update`. | Unconditional null-check + disable changes **release** behavior from "possible null-deref UB" to "element disabled, no-op". No caller relies on the crash; this is a pure safety improvement. |
| `poll_ui_manager__update` | `core/source/ui/ui_manager.c` | Invoked after the debug-only guard; UB in release if `p_ui_manager` null. | Guard becomes active in all builds → safe. |
| `get_p_ui_manager_from__graphics_window` | `core/source/rendering/graphics_window.c` (6+ call sites) + header | Reads `p_graphics_window->uuid_of__ui_manager`; UB if window null in release. | Widely shared callee — the fix only changes *how* the window is obtained (use `p_gfx_window`), not the callee. **No change** to this function. |
| `initialize_ui_element` | `core/source/ui/ui_element.c` | Called before the null check; its memset+kind+default-handler setup runs even on a failed open. | Reordering makes a failed open a no-op on the element. Any caller that assumed "call always leaves element initialized (as Button)" has that assumption invalidated. |
| Kind-keyed dispatch (`is_ui_element_of__this_kind`) | `core/include/ui/ui_element.h` | Window elements are currently mis-typed as `Button`. | Correcting to `Window` invalidates any code path that reads the `UI_Button` union member (`ui_button_flags`) or dispatches on kind == Button for these elements. None found in core/`source`; game-level callers must be verified. |
| `p_ui_window__graphics_window` union field | `core/include/defines.h` | Currently unassigned (null). | Assigning it makes the element→window link valid; any (future) reader moves from null to a live pointer. No current reader found, so low risk. |

### 2.2 Test-suite impact — critical
The suite at `tests/core/source/ui/test_suite_ui_ui_window_element.c` includes `ui_window_element.c` and has three tests, all built on the **same scenario**: a zeroed `Game` (`memset(&game,0,...)`) and `Graphics_Window_Kind__None`.

This scenario **cannot open a window**: `_open_ui_window` (`core/source/ui/ui_context.c:159`) returns NULL because the zeroed `UI_Context` has no valid registered `UI_Window_Record` for that kind (and a zeroed graphics-window-manager cannot allocate). Consequently:

- **Current code** (init-before-check, kind=Button): the element is memset and tagged `Button`; the tests assert `== UI_Element_Kind__Window`, so they **fail today**.
- **Naïve fix** (move null-check before init *and* set kind=Window): because the open fails, the element is **never initialized**, so its kind stays `None`(0), not `Window`. The same assertions **still fail**.

Therefore the existing tests assert the intended *success-path* postcondition but are built on a scenario that can only reach the *failure path*. They will pass under **neither** the current code nor the straightforward fix. This is a hard blocker: the tests require a valid fixture (a `Gfx_Context` with a registered `UI_Window_Record` and an allocatable graphics window / `UI_Manager`) to actually exercise a successful open. See §3.3/§4.

### 2.3 De-facto contracts invalidated
- **Release callers** of `_m_ui_window_element__update` implicitly assume the window/manager always resolve; making the guard unconditional removes the only (accidental) crash path — a behavior change that is strictly safer, not relied upon as a contract.
- **Kind == Button** for window elements is a de-facto contract for anything dispatching on kind or reading `ui_button_flags`; correcting to `Window` invalidates it.
- **Failed-open leaves element initialized-as-Button** is a de-facto contract; the reorder replaces it with "failed-open leaves element untouched".

---

## 3. Resolution Assessment

### 3.1 `_m_ui_window_element__update`
1. **Remove the `#ifndef NDEBUG` guards** so both null checks run in all builds; on null, disable the element and return early (mirror the existing debug path, now unconditional). Restores a **Total** handler.
2. **Use the `p_gfx_window` parameter directly** as the canonical window instead of re-deriving by UUID. This deletes the redundant lookup, the Law-of-Demeter chain, and the spurious failure mode — a behavior-preserving **Equivalence Check** on the happy path (same window object), with a smaller failure surface.
3. **Rename** the `debug_error` string to `"_m_ui_window_element__update"`.

Callers: none (signature unchanged; handler registration stays valid). Docs/tests: no direct test covers this internal handler; add a NULL-injection test (§4).

### 3.2 `_m_ui_window_element__transformed_handler`
1. **Rename** its `debug_error` string to `"_m_ui_window_element__transformed_handler"`.
2. Optionally apply the same "use `p_gfx_window` directly" change for consistency (its null check is already unconditional, so only the string and the redundant lookup are in scope).

Callers: none.

### 3.3 `initialize_ui_element_as__window_element_and__open_window`
1. **Reorder**: perform the `p_graphics_window` null check **before** `initialize_ui_element`; on NULL, log and return without mutating the element (preserves the no-partial-init **Postcondition**).
2. **Pass `UI_Element_Kind__Window`** instead of `UI_Element_Kind__Button`.
3. **Assign `p_ui_window_element->p_ui_window__graphics_window = p_graphics_window;`** after the null check, linking the element to its window (resolves the **State Desync**).

Callers: signature unchanged. Any caller relying on "element always initialized / tagged Button after this call" must be re-examined (none found in core; verify game-level scene/UI-open call sites).

### 3.4 Phased approach (recommended)
Blast radius is contained to one translation unit (`ui_window_element.c`) plus the test file, but the fixes have different risk profiles, so phase them:
- **Phase 1 (safe, behavior-preserving):** unconditional null checks in `_m_ui_window_element__update`, use `p_gfx_window` directly, fix all three misleading debug strings (incl. transformed handler). Happy-path behavior is preserved; release UB is removed.
- **Phase 2 (semantic):** kind → `Window`, and assign `p_ui_window__graphics_window`. Verify no kind/`ui_button_flags` consumers break.
- **Phase 3 (failure semantics + tests):** reorder null-check before `initialize_ui_element`, and **rework the test suite** to use a valid open fixture (see §4).

A single-phase fix is tempting but conflates a safe safety fix with a semantic contract change and a test-rewrite; phasing isolates the kind-change blast radius from the null-safety fix.

---

## 4. Test Verification Checklist

**Existing tests (all on a zeroed `Game` + `Graphics_Window_Kind__None`):**
- `..._sets_kind`, `..._with_origin`, `..._graphics_window_pointer` all assert the success-path postcondition (`kind == Window`; the last also documents the `p_ui_window__graphics_window` link) but are constructed so the open **always fails**.
- Today they **fail** (element ends as `Button`). Under the straightforward fix they **still fail** (element left untouched → kind `None`). They assert on *correct* behavior but cannot reach it with the current fixture.

**Required test changes:**
1. **Add a valid-open fixture**: a `Gfx_Context` with a registered, valid `UI_Window_Record` for the kind under test and an allocatable graphics window / `UI_Manager`, so `_open_ui_window` succeeds. Only then can the three existing assertions validate the success path (kind == `Window`, `p_ui_window__graphics_window` non-null).
2. **Strengthen `..._graphics_window_pointer`**: it currently asserts only `kind`; add a real assertion that `p_ui_window_element->p_ui_window__graphics_window` equals the opened window (**Round Trip Check** element↔window).
3. **Add a failure-path test**: with the fixture *without* a valid record (or an exhausted manager), assert that after a failed open the element is **untouched** (kind/handlers unchanged) — verifies the §1.6 reorder (**Postcondition** / **Invariant**).
4. **Add a release null-injection test for `_m_ui_window_element__update`**: pass a NULL / unresolvable window and assert the element is disabled and no UB occurs (**Property Based Testing** / **Fuzzing** of the boundary).

**Blast radius (tests): Medium.** Three existing tests need fixture rework, plus ~2 new tests. No other suites reference these functions directly. Because Phase 3 depends on the fixture, test updates are sequenced after the semantic fix.

---

## 5. Blast Radius Summary
- **Files changed:** `core/source/ui/ui_window_element.c` (primary), `tests/core/source/ui/test_suite_ui_ui_window_element.c` (fixture + new tests). Optionally the spec doc referenced by the tests (`docs/specs/core/ui/ui_window_element.h.spec.md`) for kind/failure-path wording.
- **Behavior-preserving for current callers?** Phase 1 is fully behavior-preserving on the happy path and only removes release UB. Phases 2–3 change semantics (kind tag, element↔window link, failure-state) and invalidate the de-facto contracts listed in §2.3.
- **Phased approach:** Yes — three phases as in §3.4 to isolate the kind-contract change from the safety fix and the test rewrite.
- **De-facto contracts invalidated:** release-time crash on unresolved window (removed, safe); `kind == Button` for window elements; "failed open still initializes element as Button".
