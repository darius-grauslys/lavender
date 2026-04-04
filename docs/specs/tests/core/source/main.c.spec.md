# Specification: tests/core/source/main.c

## Overview

Generated entry point for the test binary. Produced by `gen_main()` in
`update.sh`. Regenerated on every code generation run.

## Dependencies

- `MAIN_TEST_SUITE__CORE_ANCIENTS_GAME.h`
- `munit.h` (for `MunitSuite`, `munit_suite_main`, `MUNIT_ARRAY_PARAM`)

## Functions

### main

    int main(int argc, char* argv[MUNIT_ARRAY_PARAM(argc + 1)]);

1. Declares `MunitSuite test_suite`.
2. Calls `include_test_suite__CORE_ANCIENTS_GAME(&test_suite)`.
3. Returns `munit_suite_main(&test_suite, (void*) "µnit", argc, argv)`.
