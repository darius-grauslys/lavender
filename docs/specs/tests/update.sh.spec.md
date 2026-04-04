# Specification: tests/update.sh

## Overview

Top-level code generation script. Orchestrates creation and maintenance of
test suite hierarchies for core, platform, and game source trees.

## Dependencies

- `update_recursive.sh` (must be in same directory)
- Environment: `GAME_DIR`, `LAVENDER_DIR`, `PLATFORM`
- Tools: `bash`, `find`, `sed`, `cp`, `mkdir`, `realpath`
- Templates: `munit.h`, `munit.c`, `test_util.h`, `platform_defines.h`,
  `PLATFORM.c`

## Derived Variables

| Variable | Derivation |
|----------|-----------|
| `base_dir` | `realpath "${GAME_DIR}"` |
| `core_dir` | `realpath "${LAVENDER_DIR}/core/source"` |
| `platform_dir` | `realpath "${LAVENDER_DIR}/${PLATFORM}/source"` |

## Functions

### gen_main(include_dir, source_dir, [skip_platform_stubs])

1. Removes `#include <main.c>` from `test_suite_main.c` files.
2. Generates `main.c`:

        #include <MAIN_TEST_SUITE__CORE_ANCIENTS_GAME.h>
        int main(int argc, char* argv[MUNIT_ARRAY_PARAM(argc + 1)]) {
            MunitSuite test_suite;
            include_test_suite__CORE_ANCIENTS_GAME(&test_suite);
            return munit_suite_main(&test_suite, (void*) "µnit", argc, argv);
        }

3. Copies `test_util.h`, `munit.h`, `munit.c` from templates.
4. If `skip_platform_stubs` is empty: copies `platform_defines.h` and
   `PLATFORM.c` (only if not existing).

### update_core([skip_platform_stubs])

1. Creates `tests/core/{include,source}`.
2. Calls `update_recursive.sh` with tree name `"core"`.
   - Exclusion: `"*/implemented*"` if `GAME_DIR != LAVENDER_DIR`, else `""`.
3. Calls `gen_main`.

## Execution Flow

    1. update_core($1)
    2. If $1 (platform): generate platform test tree with "*/implemented*" exclusion
    3. If GAME_DIR != LAVENDER_DIR: generate game test tree with no exclusion

## Idempotency

Safe to run repeatedly. Suite wiring always regenerated. Module stubs only
created if missing. Templates always copied. Platform stubs only if missing.
