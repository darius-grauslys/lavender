# Specification: tests/core/source/test_suite_main.c

## Overview

Generated test suite for the engine's `main.c`. Empty suite, no tests.

## Dependencies

- `test_suite_main.h`

## Notes

Does NOT `#include <main.c>`. The `gen_main` function removes such includes
via `sed`. The engine's `main.c` is excluded via `CORE_OMIT := main.c`.

## Suite Definition

    DEFINE_SUITE(main, END_TESTS)
