# Planning: console.h — Incorrect Modules

**Review source:** `agents/core/review/include/debug/console.h/incorrect_modules.md`

**Source files reviewed (read-only):**
- `core/include/debug/console.h`
- `core/include/debug/debug.h`
- `core/source/debug/debug.c`
- Platform debug impls surveyed (read-only): `sdl/source/debug/sdl_debug.c`,
  `nds/source/debug/nds_debug.c`, `no_gui/source/debug/no_gui_debug.c`
- Entry points / test suites surveyed for callers: `core/source/main.c`,
  `core/source/game.c`, `tests/core/source/debug/test_suite_debug_debug.c`,
  `tests/core/source/MAIN_TEST_SUITE__CORE_ANCIENTS_GAME.c`

---

## 1. Problem Identification

The review flags two functions in `core/include/debug/console.h` as **Incorrect**:

- **`void print_console(const char *str)`** (line 8) — declared, never defined.
- **`void clear_console(void)`** (line 9) — declared, never defined.

Both are a single class of defect: a **Stub-real divergence**. The declarations
pass every structural check (valid C syntax, well-formed prototypes), but they
violate the semantic contract their names imply. There is no implementation body
in any `.c` file, so each function is an unfulfilled placeholder — the
**Translation Gap** between the declared interface layer and a translator/definition
layer that was never wired up.

- `print_console`: intent is to emit a null-terminated string to the console.
  With no body, no I/O occurs; any call resolves to an undefined symbol at link
  time (undefined reference).
- `clear_console`: intent is to clear the console display. Same gap — no body,
  no state mutated, link-time failure on any call.

A third latent defect sits in the same header and is **Coupled** to both: the
`Console` struct is declared empty (`typedef struct Console_t { } Console;`). An
empty struct is a degenerate **Representation Invariant** — it carries no concrete
storage to back any abstract console state. Neither function takes or constructs a
`Console`, so the struct is dead weight that invites a spurious assumption that a
console object exists.

**Root cause:** `console.h` is an unfinished, orphaned debug/console subsystem. The
codebase's actual debug API is the separate, varargs-based `core/include/debug/debug.h`
(`debug_info`, `debug_warning`, `debug_error`, …), whose header explicitly notes it is
platform-specific and not implemented by core. `console.h` was scaffolded but never
implemented nor integrated.

## 2. Impact Assessment

**No live callers or dependents exist.** A read-only survey found zero references to
`print_console`, `clear_console`, or the `Console` type anywhere in `./include`,
`./source`, the platform backends (`sdl/`, `nds/`, `no_gui/`), or the test suites.
Neither function is called, and nothing includes or relies on the empty `Console`
struct.

Consequences for the impact model:

- **No de facto contract to invalidate.** Because no caller was ever able to link
  against these symbols, there is no working code that has adapted to the broken
  (empty) behavior. Correcting the defect does not break any existing assumption —
  there is nothing coupled to it.
- **No cascading callers/callees/data structures** require changes in `./include` or
  `./source`. The blast radius is confined to the two declarations and the empty
  struct inside `console.h` itself.
- **Latent risk if left as-is:** the orphaned prototypes are a landmine. If a future
  developer calls `print_console`/`clear_console`, the build fails at link time
  rather than compile time — a deferred, confusing failure. The empty `Console`
  struct is an **Over Generalization** trap: it suggests a stateful console abstraction
  that does not exist, inviting speculative coupling (a **State Desync** between the
  implied object and the reality of stateless free functions).

## 3. Resolution Assessment

Two coherent resolution paths exist; both are behavior-preserving for current callers
(trivially, since there are none). Choose one:

### Path A (Recommended) — Remove the orphaned subsystem
The debug subsystem is already fully served by `debug.h` (varargs formatters,
platform-specific backends). `console.h` duplicates that intent with a divergent,
unimplemented surface.

1. Delete `core/include/debug/console.h` entirely (empty struct + both prototypes).
2. Confirm no build file, include list, or header references it (survey shows none).
3. No caller, test, or documentation updates required — nothing depends on it.

This restores a single **Single Source of Truth (SSOT)** for debug output and removes
the **Stub-real divergence**.

### Path B — Implement the declared contract (only if console is genuinely wanted)
If a distinct, non-`debug.h` console is intended, close the gap instead of deleting:

1. Add `core/source/debug/console.c` defining both functions.
   - `print_console(const char *str)`: enforce **Precondition** `str != NULL`;
     emit `str` to the console backend; define a **Postcondition** (message emitted).
     Handle the **Boundary Condition** of an empty string (`""`) and NULL explicitly.
   - `clear_console(void)`: clear the console display surface.
2. Resolve the empty `Console` struct: either give it real fields backing a genuine
   console state (restoring a valid **Representation Invariant**) or delete it, since
   neither function uses it. Do not leave a zero-size struct as a **Sentinel** of an
   abstraction that has no body.
3. Route the concrete I/O through the existing platform backends rather than a new
   parallel path (avoid **Spaghettification** / duplicate debug channels — keep DRY).

**Callers:** none to update under either path.
**Documentation:** if Path B, document pre/postconditions per a **Contract-First**
approach before implementing.

## 4. Test Verification Checklist

- **Existing tests:** the surveyed test suites (`test_suite_debug_debug.c` and the
  core/sdl/nds/no_gui debug suites) contain **no** references to `print_console`,
  `clear_console`, or `Console`. No existing assertion asserts on — or will be
  invalidated by — the broken behavior.
- **Path A (delete):** No test changes needed. Optionally add a **Lint Gate** /
  **Static Analysis** check that flags declared-but-undefined symbols, to prevent
  recurrence of this class of **Translation Gap**.
- **Path B (implement):** New tests required.
  - `print_console`: **Equivalence Check** against expected emitted output;
    a NULL-pointer and empty-string case to exercise the **Boundary Condition**;
    a **Round Trip Check** (write string → read console buffer → compare) to verify
    the emitted state.
  - `clear_console`: assert the console surface is empty after the call (**Postcondition**).
  - **Fuzzing** on `print_console` input for robustness; **Mutation Testing** to confirm
    the new suite actually detects regressions in the implementation.

## 5. Blast Radius Summary

- **Files changed:** Path A — 1 (`core/include/debug/console.h`, deleted).
  Path B — 2 (new `core/source/debug/console.c`, edited `console.h`).
- **Behavior-preserving for current callers:** Yes, trivially — there are no callers.
- **Phased approach needed:** No. The change is isolated to a single orphaned header.
- **De facto contracts invalidated:** None. No working code depends on the broken
  behavior; the only effect is removing a link-time landmine (Path A) or fulfilling
  an unused contract (Path B).

**Recommendation:** Path A. `console.h` is a dead, unimplemented duplicate of the
working `debug.h` subsystem; deleting it removes the **Stub-real divergence** with
zero downstream impact.
