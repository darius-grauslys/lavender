# Specification: tests/templates/test_util.h

## Overview

Template version of the test utility macro header. Copied into new test
trees by `update.sh`. Does not include diagnostic `printf` output or the
`test_log` function.

## Dependencies

- `<munit.h>`

## Include Guard

    #ifndef TEST_UTIL_H
    #define TEST_UTIL_H

## Types

    typedef void (*f_test_suite_includer)(MunitSuite *test_suite);

## Macros

Identical to the live `tests/test_util.h` except:

| Aspect | Template | Live |
|--------|----------|------|
| Prefix | `#name "_"` | `#name` |
| Debug printf | None | Present |
| `test_log` | Absent | Present |
| `<stdio.h>` | Not included | Included |

All macro names, signatures, and generated symbol patterns are identical
between the two versions.
