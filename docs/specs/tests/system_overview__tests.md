# System Overview: Test Infrastructure

## Purpose

The test infrastructure provides a framework for unit testing the engine's
core modules, platform-specific modules, and game-specific modules. It is
built on top of the µnit (munit) testing library and uses a hierarchical
test suite structure that mirrors the source directory layout. Code generation
scripts automatically create test stubs and suite wiring for every source
module, ensuring that new modules are immediately visible in the test harness.

## Architecture

### Data Hierarchy

    Root Makefile (test target)
    +-- update.sh (code generation)
    |   +-- update_recursive.sh (recursive per directory)
    |       +-- MAIN_TEST_SUITE__<TREE>_<DIR>.h  (always regenerated)
    |       +-- MAIN_TEST_SUITE__<TREE>_<DIR>.c  (always regenerated)
    |       +-- test_suite_<module>.h             (generated if missing)
    |       +-- test_suite_<module>.c             (generated if missing)
    |
    +-- tests/Makefile (compilation)
    |   +-- CFILES_TEST_CORE   (find tests/core/source -name *.c)
    |   +-- CFILES_TEST_PLATFORM (find tests/<platform>/source -name *.c)
    |   +-- CFILES_TEST_GAME   (find tests/<game>/source -name *.c)
    |   +-- OFILES -> OUTPUT (linked test binary)
    |
    +-- tests/core/source/main.c (generated entry point)
        +-- include_test_suite__CORE_ANCIENTS_GAME(&test_suite)
        +-- munit_suite_main(&test_suite, ...)
            +-- MunitSuite (root: CORE_ANCIENTS_GAME)
                +-- MunitSuite[0]: main          (test_suite_main.c)
                +-- MunitSuite[1]: vectors       (test_suite_vectors.c)
                +-- MunitSuite[2]: core_string   (test_suite_core_string.c)
                +-- MunitSuite[3]: random        (test_suite_random.c)
                +-- MunitSuite[4]: client        (test_suite_client.c)
                +-- MunitSuite[5]: degree        (test_suite_degree.c)
                +-- MunitSuite[6]: game          (test_suite_game.c)
                +-- MunitSuite[7]: CORE_INPUT    (directory suite)
                +-- MunitSuite[8]: CORE_RENDERING
                +-- MunitSuite[9]: CORE_WORLD
                |   +-- MunitSuite: chunk        (test_suite_world_chunk.c)
                |   +-- ...
                +-- MunitSuite[10]: CORE_INVENTORY
                +-- MunitSuite[11]: CORE_SORT
                +-- MunitSuite[12]: CORE_DEBUG
                +-- MunitSuite[13]: CORE_AUDIO
                +-- MunitSuite[14]: CORE_LOG
                +-- MunitSuite[15]: CORE_SERIALIZATION
                +-- MunitSuite[16]: CORE_GAME_ACTION
                +-- MunitSuite[17]: CORE_ENTITY
                +-- MunitSuite[18]: CORE_UI
                +-- MunitSuite[19]: CORE_COLLISIONS
                +-- MunitSuite[20]: CORE_UTIL
                +-- MunitSuite[21]: CORE_MULTIPLAYER
                +-- MunitSuite[22]: CORE_RAYCAST
                +-- MunitSuite[23]: CORE_PROCESS
                +-- MunitSuite[24]: CORE_SCENE

### Key Types

| Type | Role |
|------|------|
| `MunitSuite` | µnit test suite. Contains a prefix string, array of `MunitTest`, array of child `MunitSuite`, iteration count, and options. |
| `MunitTest` | µnit test case. Contains name, test function pointer, optional setup/teardown, options, and parameter enums. |
| `MunitResult` | Test outcome enum: `MUNIT_OK`, `MUNIT_FAIL`, `MUNIT_SKIP`, `MUNIT_ERROR`. |
| `f_test_suite_includer` | `void (*)(MunitSuite*)`. Function pointer type used by `INCLUDE_SUB_SUITES` to wire child suites. |

### Limits

| Macro | Default | Description |
|-------|---------|-------------|
| `MUNIT_TEST_NAME_LEN` | 37 | Column width for test name display in output. |
| Root sub-suite count | 26 | 7 module suites + 18 directory suites + 1 NULL sentinel. |

## File Layout

    tests/
    ├── Makefile                         Build system for test binary
    ├── README                           Developer guide
    ├── update.sh                        Top-level code generation
    ├── update_recursive.sh              Recursive directory scanner
    ├── test_util.h                      Live macro library (with debug printf)
    ├── test_suite_game.c                Example: hand-edited test at repo root
    │
    ├── templates/                       Template files copied into test trees
    │   ├── munit.h                      µnit header
    │   ├── munit.c                      µnit implementation
    │   ├── test_util.h                  Clean macro library (no debug printf)
    │   ├── include/
    │   │   └── platform_defines.h       Platform constant stubs
    │   └── source/
    │       └── PLATFORM.c               Platform function stubs
    │
    └── core/
        ├── include/
        │   ├── MAIN_TEST_SUITE__CORE_ANCIENTS_GAME.h
        │   ├── test_suite_main.h
        │   ├── test_suite_vectors.h
        │   ├── test_suite_core_string.h
        │   ├── test_suite_random.h
        │   ├── test_suite_client.h
        │   ├── test_suite_degree.h
        │   ├── test_suite_game.h
        │   └── world/
        │       └── test_suite_world_chunk.h
        └── source/
            ├── main.c                   Generated entry point
            ├── munit.c                  Copied from templates/
            ├── MAIN_TEST_SUITE__CORE_ANCIENTS_GAME.c
            ├── test_suite_main.c
            ├── test_suite_vectors.c
            ├── test_suite_core_string.c
            ├── test_suite_random.c
            ├── test_suite_client.c
            ├── test_suite_degree.c
            └── world/
                └── test_suite_world_chunk.c

## Source Inclusion Strategy

Test modules `#include` the original `.c` source file directly:

    #include <game.c>
    #include <world/chunk.c>

This gives the test full access to static functions and file-scope variables
without requiring any modifications to the production code. The trade-off is
that each test module compiles the full translation unit, which can increase
build times but ensures complete coverage of internal implementation details.

Credit: Mike Long on StackOverflow for this technique.

## Platform Stub Strategy

When tests are built without a real platform backend, the infrastructure
provides two stub files from `tests/templates/`:

- `platform_defines.h`: Defines all platform-specific constants with
  reasonable defaults. All definitions use `#ifndef` guards allowing
  override.

- `PLATFORM.c`: Provides no-op or error-returning implementations of all
  `PLATFORM_*` functions. Guarded by `#if !defined(PLATFORM)` so it is
  automatically excluded when a real platform backend is present.

The stubs return "failure" or "empty" values rather than crashing, allowing
tests to exercise core engine logic that calls `PLATFORM_*` functions without
requiring a real graphics, audio, file system, or networking backend.

## Lifecycle

### 1. Initialization (Code Generation)

    $ cd tests/ && ./update.sh [platform]

    -> Creates tests/core/{include,source} directories.
    -> Calls update_recursive.sh for core/source.
       -> For each .c file: generates test_suite_<name>.{h,c} if missing.
       -> For each subdirectory: recurses, generates MAIN_TEST_SUITE files.
       -> Registers all modules and subdirs in parent MAIN_TEST_SUITE.
    -> Generates main.c with root suite invocation.
    -> Copies munit.h, munit.c, test_util.h from templates/.
    -> If no platform: copies platform_defines.h, PLATFORM.c from templates/.
    -> If platform specified: repeats for platform source tree.
    -> If GAME_DIR != LAVENDER_DIR: repeats for game source tree.

### 2. Test Authoring

Developers edit generated test_suite_<module>.c files:

    #include <test_suite_game.h>
    #include <game.c>

    TEST_FUNCTION(is_true) {
        munit_assert_true(false);
        return MUNIT_OK;
    }

    DEFINE_SUITE(game,
        INCLUDE_TEST__STATELESS(is_true),
        END_TESTS)

### 3. Building

    $ make test [-e PLATFORM=<platform>]

    -> Root Makefile copies tests/ if GAME_DIR != LAVENDER_DIR.
    -> Runs update.sh to regenerate suite wiring.
    -> Invokes tests/Makefile with BUILD directory.
    -> tests/Makefile discovers all .c files via find.
    -> Compiles each with include paths: game > platform > core > test headers.
    -> Links all .o files into single test binary.
    -> Generates compile_commands.json for IDE integration.

### 4. Execution

    $ ./build/test_core/<target> [--seed SEED] [--no-fork] [--list] ...

    -> main() calls include_test_suite__CORE_ANCIENTS_GAME(&test_suite).
    -> include_sub_suites_for__CORE_ANCIENTS_GAME wires 25 child suites.
    -> Each child suite's includer wires its own children recursively.
    -> munit_suite_main traverses the tree, running all MunitTest functions.
    -> Each test runs in a forked child process (POSIX) for crash isolation.
    -> Results reported: OK (green), FAIL (red), SKIP (yellow), ERROR (red).

### 5. Suite Wiring (Runtime Detail)

When `include_test_suite__CORE_ANCIENTS_GAME` is called:

    1. Sets prefix to "CORE_ANCIENTS_GAME".
    2. Sets tests to empty array (no tests at root level).
    3. Calls include_sub_suites_for__CORE_ANCIENTS_GAME:
       a. Iterates 26 f_test_suite_includer function pointers.
       b. For each non-NULL includer, calls it with &sub_suites[i].
       c. Each includer (e.g., include_test_suite__game) populates:
          - prefix = "game"
          - tests = { {"is_true", MunitTestFunc_is_true, ...}, END_TESTS }
          - suites = NULL (leaf suite)
       d. Directory includers (e.g., include_test_suite__CORE_WORLD)
          recursively wire their own sub-suites.
    4. Sets suites pointer to the populated sub_suites array.

### 6. Deallocation

No explicit deallocation. All suite data is statically allocated via
file-scope arrays generated by the macros. The test binary exits after
`munit_suite_main` returns.

## Integration with Build System

The root `Makefile` `test` target and `tests/Makefile` collaborate:

| Concern | Root Makefile | tests/Makefile |
|---------|--------------|----------------|
| Code generation | Invokes `update.sh` | N/A |
| Source discovery | N/A | `find` for CFILES_TEST_* |
| Include paths | N/A | Aggregates 9 include directories |
| Platform fallback | Passes PLATFORM env | Falls back to templates/ stubs |
| Core main.c exclusion | N/A | `CORE_OMIT := main.c` |
| Compilation database | Symlinks result | Generates via grep + jq |
| Linking | N/A | Links all OFILES into OUTPUT |

## Capacity Constraints

- Each source `.c` file produces exactly one `MunitSuite` (module suite).
- Each source directory produces exactly one `MunitSuite` (directory suite).
- The root suite count (26) is derived from 7 top-level `.c` files +
  18 subdirectories + 1 NULL sentinel, as counted by `update_recursive.sh`.
- Module test files are never overwritten by code generation, preserving
  hand-written tests.
- Directory suite files are always overwritten to pick up new modules.
