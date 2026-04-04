# Specification: tests/templates/munit.c

## Overview

The µnit testing framework implementation. Third-party library by Evan
Nemerson (MIT license). Copied into test trees by `update.sh`.

## Dependencies

- `munit.h`
- Standard: `<limits.h>`, `<time.h>`, `<errno.h>`, `<string.h>`,
  `<stdlib.h>`, `<stdio.h>`, `<stdarg.h>`, `<setjmp.h>`
- POSIX: `<unistd.h>`, `<sys/types.h>`, `<sys/wait.h>`
- Windows: `<windows.h>`, `<io.h>`, `<fcntl.h>`

## Configuration

| Macro | Default | Description |
|-------|---------|-------------|
| `MUNIT_OUTPUT_FILE` | `stdout` | Output stream |
| `MUNIT_TEST_TIME_FORMAT` | `"0.8f"` | Timing format |
| `MUNIT_TEST_NAME_LEN` | `37` | Name column width |
| `MUNIT_DISABLE_TIMING` | undefined | Disable timing |

## Components

### PRNG

PCG algorithm, 32-bit state, thread-safe via atomic CAS. Seeded from wall
clock or `--seed` argument.

### Timer

Embedded portable-snippets clock library. Supports wall, CPU, and monotonic
clocks via platform-specific backends.

### Test Execution

    munit_suite_main
    └── munit_test_runner_run
        └── munit_test_runner_run_suite (recursive)
            └── munit_test_runner_run_test
                └── munit_test_runner_run_test_with_params
                    ├── [fork] fork() + pipe + waitpid
                    └── [no-fork] direct execution
                        └── setup() → test() → tear_down()

### Forked Execution (POSIX)

Child: redirects stderr to tmpfile, runs test, writes MunitReport to pipe.
Parent: reads report, checks exit status and signals.

### CLI Arguments

`--seed`, `--iterations`, `--param`, `--color`, `--help`, `--single`,
`--show-stderr`, `--no-fork`, `--fatal-failures`, `--log-visible`,
`--log-fatal`, `--list`, `--list-params`
