# Specification: tests/core/include/test_suite_main.h

## Overview

Generated header for the `main.c` module suite. Preserved across regeneration.

## Dependencies

- `<test_util.h>`

## Declaration

    DECLARE_SUITE(main)

Note: The `main` suite is distinct from the test binary's `main()` entry
point. The engine's `main.c` is excluded from test compilation via
`CORE_OMIT := main.c`.
