# Lavender Build System

## Overview

Lavender uses GNU Make with a layered include architecture. The top-level
`Makefile` delegates to `Makefile.build`, which chains platform-agnostic core
rules with platform-specific rules and optional game project rules.

Compiler: `clang-21` (set in `sdl/Makefile.include`).

## Quick Reference

```bash
# Build (SDL desktop)
make -e PLATFORM=sdl -e FLAGS="-w"

# Build with debug symbols
make -e PLATFORM=sdl -e FLAGS="-ggdb -w"

# Parallel build
make -e PLATFORM=sdl -e FLAGS="-w" -j$(nproc)

# Run tests (core only)
make test

# Run tests (core + SDL platform)
make test -e PLATFORM=sdl

# Clean
make clean

# Spot-check a single module (no .o produced, syntax + semantic check only)
make check-file FILE=core/source/rendering/graphics_window.c -e PLATFORM=sdl

# Generate compile_commands.json
# (automatically generated during build via Bear)
# To regenerate without building:
make compile_commands -e PLATFORM=sdl
```

### Building from a Game Project

Game projects (e.g. DungeonGame, AncientsGame) use `tools/lav_build`:

```bash
cd /path/to/MyGame
$LAVENDER_DIR/tools/lav_build -e PLATFORM=sdl
$LAVENDER_DIR/tools/lav_build test -e PLATFORM=sdl
$LAVENDER_DIR/tools/lav_build check-file FILE=source/my_scene.c -e PLATFORM=sdl
```

`lav_build` sets `GAME_DIR` from the current working directory and invokes
the engine's Makefile.

## Makefile Architecture

```
Makefile                    Top-level entry point. Defines targets:
                            default, test, clean, check-file, compile_commands.
    |
    +--> Makefile.build     Build orchestrator. Two-phase:
    |       |               Phase 1 (outer): Loads includes, creates build dir,
    |       |                                recurses via make -C $(BUILD).
    |       |               Phase 2 (inner): Runs in build dir. Defines the
    |       |                                unified %.o: %.c pattern rule.
    |       |                                Links $(GAME) from $(OFILES).
    |       |
    |       +--> Makefile.include       Aggregates all sub-includes.
    |       |       |                   Defines CFLAGS, OFILES, INCLUDE, LIBS.
    |       |       |
    |       |       +--> core/Makefile.include   Source discovery for core/.
    |       |       +--> $(PLATFORM)/Makefile.include  Platform source/libs/CC.
    |       |       +--> $(GAME_DIR)/Makefile.include  Game project sources.
    |       |
    |       +--> core/Makefile.build        vpath %.c $(SOURCE_CORE)
    |       +--> $(PLATFORM)/Makefile.build vpath %.c $(SOURCE_PLATFORM)
    |       +--> $(GAME_DIR)/Makefile.build vpath %.c $(SOURCE_GAME) + GAME_SETUP
    |
    +--> tests/Makefile     Test build. Similar two-phase structure.
                            Invoked by `make test` target.
```

### How `vpath` Works

Each `*/Makefile.build` declares a `vpath` directive telling Make where to
find `.c` source files:

```makefile
vpath %.c $(SOURCE_CORE)       # core/Makefile.build
vpath %.c $(SOURCE_PLATFORM)   # sdl/Makefile.build
vpath %.c $(SOURCE_GAME)       # game project Makefile.build
```

These accumulate. When Make needs `rendering/graphics_window.c` to build
`rendering/graphics_window.o`, it searches the vpath directories in order.
A single unified pattern rule in `Makefile.build` handles all compilation:

```makefile
%.o: %.c
    @mkdir -p $(dir $@)
    $(CC) $(CFLAGS) $(INCLUDE) $(FLAGS) -MMD -MP -MF $*.d -c $< -o $@
```

**Important**: Source file names must be unique across core, platform, and
game directories. This is enforced by naming convention (core uses `input.c`,
SDL uses `sdl_input.c`, etc.) but not by the build system itself.

## CFLAGS Management

Base compiler flags are defined **once** in `Makefile.include`:

```makefile
export CFLAGS := -Wall -Wextra -O2 -march=$(shell uname -m | sed "s/_/-/")
```

### Policy for Sub-Makefiles

- **APPEND** platform-specific flags with `+=`:
  ```makefile
  # nds/Makefile.include (example)
  export CFLAGS += -march=armv5te -mtune=arm946e-s -fomit-frame-pointer
  ```
- **NEVER** shadow with `:=` — this discards the base flags.
- The `tests/Makefile` defines its own `CFLAGS` because it does not load the
  root `Makefile.include`. Keep test CFLAGS in sync with the base definition.

### Additional Flag Variables

| Variable | Purpose | Example |
|----------|---------|---------|
| `CFLAGS` | Compiler warnings, optimization, architecture | `-Wall -Wextra -O2` |
| `FLAGS` | User-supplied build-time flags | `-ggdb -DIS_SERVER -DNDEBUG -DNLOG` |
| `INCLUDE` | Computed `-I` paths (do not set manually) | `-I.../core/include -I.../sdl/include` |
| `LIBS` / `PLATFORM_LIBS` | Linker libraries | `-lGL -lGLEW -lSDL2 -lcglm -lm` |

### Warning Suppression (`-w` in FLAGS)

Standard builds should pass `-w` in `FLAGS` to suppress warnings:

```bash
make -e PLATFORM=sdl -e FLAGS="-ggdb -w"
```

**Why**: CFLAGS includes `-Wall -Wextra` which generates many warnings in
both source modules and the monolithic `defines.h` header. Since every `.c`
file includes `defines.h`, a single warning in that header propagates across
every compilation unit, producing enormous output that buries actual errors
and wastes context in agentic automation pipelines.

The `-w` flag (passed via `FLAGS`, which is appended after `CFLAGS`) takes
precedence and suppresses all warnings. This keeps build output focused on
errors only.

### Warning Audit Workflow

When explicitly resolving warnings, **do not** build with warnings enabled
in a normal interactive session. Instead:

1. Run a warning-enabled build with output captured:
   ```bash
   make -e PLATFORM=sdl -e FLAGS="-ggdb" 2>&1 | tee build_warnings.log
   ```
2. In an agentic pipeline, dispatch a **crawler agent** to perform the build
   and summarize the warnings. This avoids flooding the orchestrator's context
   with repeated warnings (especially those originating from `defines.h` which
   appear once per compilation unit).
3. The crawler should deduplicate warnings by source location and report:
   - Unique warning locations (file:line)
   - Warning category (`-Wsign-compare`, `-Wunused-parameter`, etc.)
   - Propagation count (how many `.o` files triggered the same header warning)

This keeps the warning audit tractable even on large codebases where
`defines.h` changes can produce hundreds of duplicate diagnostics.

## Incremental Builds

The build system generates `.d` dependency files via `-MMD -MP -MF` during
compilation. These files record which headers each `.c` file includes. On
subsequent builds, Make reads these files to determine which `.o` files are
stale:

```makefile
-include $(OFILES:.o=.d)
```

This means:
- Touching a `.c` file rebuilds only that `.o`.
- Touching a header rebuilds all `.o` files that depend on it.
- On first build (no `.d` files), everything compiles.

## Parallel Builds

The build system supports `make -jN` for parallel compilation:

```bash
make -e PLATFORM=sdl -j$(nproc)
```

This is safe because:
- Each `.o` file depends only on its `.c` source and headers (tracked by `.d` files).
- The link step depends on all `$(OFILES)`, so it waits for compilation to finish.
- `vpath`-based source discovery happens at parse time, not during rule execution.

## compile_commands.json

Generated automatically during every build using [Bear](https://github.com/rizsotto/Bear).
Bear intercepts compiler invocations at the OS level and writes a standard
`compile_commands.json` to the project root.

This file is used by:
- **clangd** — LSP server for IDE code navigation and diagnostics.
- **Lavender AI tooling** — agent-driven code analysis.

To regenerate without a full build:
```bash
make compile_commands -e PLATFORM=sdl
```

## Spot-Building (check-file)

Validate a single source module without producing an object file:

```bash
make check-file FILE=core/source/rendering/graphics_window.c -e PLATFORM=sdl
```

This runs `clang -fsyntax-only` with the full flag chain (CFLAGS, INCLUDE,
FLAGS). It performs preprocessing, parsing, and semantic analysis without
code generation — the fastest possible correctness check.

- **Exit 0**: Module compiles cleanly.
- **Non-zero**: Errors printed to stderr with file:line:col diagnostics.
- Accepts absolute paths or paths relative to the current working directory.
- Works from both the engine directory and game project directories (via `lav_build`).

## Platform Identification

Each platform backend provides a `platform_defines.h` header that defines a
platform identification macro:

| Platform | Header | Macro |
|----------|--------|-------|
| SDL | `sdl/include/platform_defines.h` | `#define PLATFORM__SDL` |
| NDS | `nds/include/platform_defines.h` | `#define PLATFORM__NDS` |
| No GUI | `no_gui/include/platform_defines.h` | `#define PLATFORM__NO_GUI` |
| Core (fallback) | `core/platform_defines.h` | *(none)* |

### How It Works

The build system adds `-I$(PLATFORM)/include` before `-Icore/include` in the
include path. Since all `platform_defines.h` files share the same header guard
(`PLATFORM_DEFINES_H`), the platform-specific version is found first and the
core fallback is skipped.

**No `-DPLATFORM__*` flags are passed on the command line.** Platform
identification is handled entirely through include path priority.

### Design Intent

The **engine code** (`core/`) intentionally does **not** check these
`PLATFORM__*` macros. The engine achieves platform abstraction through
function pointer vtables and compile-time include path routing.

These defines exist for **game project code** to branch on platform when
needed — for example, choosing different UI layouts or logic paths based
on the target backend.

## Test System

Tests use [munit](https://nemequ.github.io/munit/) and are scaffolded
automatically by `tests/update.sh`.

### Test Scaffolding

`tests/update.sh` walks the source tree and generates:
- `MAIN_TEST_SUITE__*.h/c` — hierarchical test suite wiring files.
- `test_suite_*.h/c` — per-module test stubs (only if they don't already exist).

The suite naming derives from `$GAME_DIR`:
- Engine self-test: `CORE_LAVENDER`
- Game project: `CORE_ANCIENTS_GAME` (CamelCase → UPPER_SNAKE_CASE)

### How Tests Include Sources

Test files `#include` their corresponding `.c` source file directly:
```c
#include <rendering/graphics_window.c>
```

This allows tests to access `static` functions. The `-MMD -MP` flags
correctly track these transitive dependencies — if `graphics_window.c` or
any header it includes changes, the test recompiles.

### Test Build Targets

```bash
make test                      # Core tests only (no platform)
make test -e PLATFORM=sdl      # Core + SDL platform tests
make test -j$(nproc)           # Parallel test build
```
