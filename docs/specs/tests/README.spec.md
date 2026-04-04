# Specification: tests/README

## Overview

Developer-facing documentation for writing unit tests within the test
infrastructure. Serves as a quick-reference guide for the most commonly
used macros and conventions.

## Dependencies

- `test_util.h` (for all referenced macros)
- `munit.h` (for assertion macros and result codes)

## Content

### Recommended Test Pattern

1. Declare the test function using `TEST_FUNCTION(name)`.
2. Register the test using `INCLUDE_TEST__STATELESS(name)` inside a
   `DEFINE_SUITE` block.

### Suite Registration

    DEFINE_SUITE([module name],
        INCLUDE_TEST__STATELESS(name),
        END_TESTS)

### Return Values

| Return Value | Meaning |
|-------------|---------|
| `MUNIT_OK` | Test passed. |
| `MUNIT_FAIL` | Test failed. |

### Assertions

Directs developers to `munit.h` for the full list.

### Source Inclusion Technique

Credits Mike Long on StackOverflow for including the C source file directly
into the test module to access static functions.
