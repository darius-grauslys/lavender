# System Overview: Test Code Generation Scripts

## Purpose

The `update.sh` and `update_recursive.sh` scripts form a two-tier code
generation system that automatically creates and maintains the test suite
hierarchy. When a developer adds a new `.c` source file to the engine, running
`update.sh` generates the corresponding test stub and wires it into the suite
tree — ensuring that no module is accidentally left untested.

## Architecture

### Script Roles

| Script | Role |
|--------|------|
| `update.sh` | Top-level orchestrator. Sets up directory structure, invokes `update_recursive.sh` for each source tree (core, platform, game), and generates `main.c`. |
| `update_recursive.sh` | Recursive worker. Scans a single directory level for `.c` files and subdirectories, generates suite headers/sources, and recurses into subdirectories. |

### Data Flow

    update.sh
    │
    ├── export base_dir, core_dir, platform_dir
    │
    ├── update_core($1)
    │   ├── mkdir -p tests/core/{include,source}
    │   ├── update_recursive.sh \
    │   │     core/source "" core/include core/source "core" [exclusion]
    │   │   ├── find *.c at top level -> test_suite_game.{h,c}, etc.
    │   │   ├── find subdirs -> input/, rendering/, world/, ...
    │   │   │   └── recurse for each subdir
    │   │   ├── Generate MAIN_TEST_SUITE__CORE_ANCIENTS_GAME.{h,c}
    │   │   └── sed __COUNT -> actual count (26)
    │   └── gen_main(core/include, core/source, $1)
    │       ├── Generate main.c
    │       ├── Copy munit.h, munit.c, test_util.h
    │       └── Copy platform_defines.h, PLATFORM.c (if no platform)
    │
    ├── [if $1 (platform) specified]
    │   ├── mkdir -p tests/$1/{include,source}
    │   └── update_recursive.sh \
    │         $platform_dir "" tests/$1/include tests/$1/source $1 "*/implemented*"
    │
    └── [if LAVENDER_DIR != GAME_DIR]
        ├── mkdir -p tests/$(basename $GAME_DIR)/{include,source}
        └── update_recursive.sh \
              $GAME_DIR/source "" $(basename)/include $(basename)/source $(basename) ""

### Naming Derivation

Directory suite names are derived from the path relative to the search base:

    Source: core/source/world       -> Suite: CORE_WORLD
    Source: core/source/world/gen   -> Suite: CORE_WORLD_GEN
    Full:   MAIN_TEST_SUITE__CORE_WORLD

Module suite names use the basename without extension:

    Source: core/source/game.c      -> Suite: game
    Source: core/source/world/chunk.c -> Suite: chunk
    File:   test_suite_world_chunk.{h,c}

### Generated File Structure Per Directory

**Header (always regenerated):**

    #include "test_suite_<module_a>.h"
    #include "test_suite_<module_b>.h"
    #include "<subdir>/MAIN_TEST_SUITE__<TREE>_<SUBDIR>.h"

    #include <test_util.h>
    DECLARE_SUITE(<suite_name>);

**Source (always regenerated):**

    #include <<path>/MAIN_TEST_SUITE__<NAME>.h>

    INCLUDE_SUB_SUITES(<suite_name>, <count>,
    INCLUDE_SUITE(<module_a>),
    INCLUDE_SUITE(<module_b>),
    INCLUDE_SUITE(<TREE>_<SUBDIR>),
    NULL);

    DEFINE_SUITE_WITH__SUB_SUITES(<suite_name>, END_TESTS);

### Generated File Structure Per Module (only if missing)

**Header:**

    #include <test_util.h>
    DECLARE_SUITE(<module_name>)

**Source:**

    #include <<path>/test_suite_<name>.h>
    #include <<relative_path_to_original>.c>

    #warning Please make tests for: <full_path>

    DEFINE_SUITE(<module_name>, END_TESTS)

## Idempotency

- **Directory suite files** (MAIN_TEST_SUITE__*): Always regenerated.
- **Module test files** (test_suite_*): Only generated if missing.
- **Template files** (munit.h, munit.c, test_util.h): Always copied.
- **Platform stubs** (platform_defines.h, PLATFORM.c): Only copied if missing.
