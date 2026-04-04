# Specification: tests/test_suite_game.c

## Overview

Example test suite source file at the repository root `tests/` directory.
Demonstrates the structure of a hand-edited test module. Tests the `game.c`
module by directly including its source.

## Dependencies

- `test_suite_game.h` (declares the `game` suite)
- `game.c` (production source, included directly)
- `test_util.h` (for `TEST_FUNCTION`, `DEFINE_SUITE`,
  `INCLUDE_TEST__STATELESS`, `END_TESTS`)
- `munit.h` (for `munit_assert_true`, `MUNIT_OK`)

## Compiler Warnings

    #warning Please make tests for: /home/shalidor/Projects/AncientsGame/tests/core/source/test_suite_game.c

## Source Inclusion

    #include <game.c>

## Test Functions

### is_true

    TEST_FUNCTION(is_true) {
        munit_assert_true(false);
        return MUNIT_OK;
    }

**Status:** Intentionally failing. `munit_assert_true(false)` always fails.
Serves as a placeholder until real tests are written.

## Suite Definition

    DEFINE_SUITE(game, INCLUDE_TEST__STATELESS(is_true), END_TESTS)

| Field | Value |
|-------|-------|
| Suite name | `game` |
| Prefix | `"game"` |
| Tests | `is_true` |
| Sub-suites | None |
