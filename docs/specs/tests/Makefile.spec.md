# Specification: tests/Makefile

## Overview

Compiles all generated and hand-written test sources into a single test
binary. Supports three source trees (core, platform, game).

## Dependencies

- `$(DIR_CORE)/Makefile.include` (defines `SOURCE_CORE`, `INCLUDE_CORE`)
- `$(DIR_PLATFORM)/Makefile.include` (when PLATFORM set)
- Tools: GNU Make, `find`, `realpath`, `jq`, `grep`, `mkdir`

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `LAVENDER_DIR` | Yes | Engine root |
| `GAME_DIR` | Yes | Game project root |
| `PLATFORM` | No | Platform identifier |
| `BUILD` | Yes | Build output directory |
| `ADD_COMPILE_COMMAND` | No | compile_commands.json helper |

## Key Variables

| Variable | Value |
|----------|-------|
| `TARGET` | `$(shell basename $(GAME_DIR))` |
| `CFLAGS` | `-Wall -O2` |
| `CORE_OMIT` | `main.c` |
| `LIBS` | `$(PLATFORM_LIBS)` |

## Platform Fallback

When PLATFORM is empty:

    INCLUDE_PLATFORM = $(LAVENDER_DIR)/tests/templates/include
    SOURCE_PLATFORM  = $(LAVENDER_DIR)/tests/templates/source

## Include Path Order

1. `SOURCE_GAME`, `INCLUDE_GAME`
2. `SOURCE_PLATFORM`, `INCLUDE_PLATFORM`
3. `SOURCE_CORE`, `INCLUDE_CORE`
4. `INCLUDE_TEST_GAME`, `INCLUDE_TEST_PLATFORM`, `INCLUDE_TEST_CORE`

## Source Discovery

| Variable | Root | Exclusion |
|----------|------|-----------|
| `CFILES_TEST_CORE` | `tests/core/source` | `*/implemented/*` if game != engine |
| `CFILES_TEST_PLATFORM` | `tests/<platform>/source` | None |
| `CFILES_TEST_GAME` | `tests/<game>/source` | None |

## Build Rules

- Each source tree has its own compilation rule.
- All objects linked into `$(OUTPUT)`.
- `compile_commands.json` generated via grep + jq pipeline.
