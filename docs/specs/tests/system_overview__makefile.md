# System Overview: Test Build System

## Purpose

Two Makefiles collaborate to build and run the test binary:

1. **Root `Makefile`** — Provides the `test` target that orchestrates code
   generation, compilation, and compile_commands.json symlinking.
2. **`tests/Makefile`** — Compiles all generated and hand-written test sources
   into a single test binary.

## Architecture

### Root Makefile test Target

    make test [-e PLATFORM=<platform>]

    1. Copy tests/ from LAVENDER_DIR if GAME_DIR differs.
    2. Run update.sh to regenerate suite wiring.
    3. Invoke tests/Makefile:
       - No platform: BUILD=build/test_core
       - With platform: BUILD=build/test_$(PLATFORM)
    4. Symlink compile_commands.json.

### Include Path Order (tests/Makefile)

    INCLUDES := \
        $(SOURCE_GAME) $(INCLUDE_GAME) \
        $(SOURCE_PLATFORM) $(INCLUDE_PLATFORM) \
        $(SOURCE_CORE) $(INCLUDE_CORE) \
        $(INCLUDE_TEST_GAME) $(INCLUDE_TEST_PLATFORM) $(INCLUDE_TEST_CORE)

Game overrides platform, platform overrides core.

### Platform Fallback

When PLATFORM is empty:

    INCLUDE_PLATFORM = $(LAVENDER_DIR)/tests/templates/include
    SOURCE_PLATFORM  = $(LAVENDER_DIR)/tests/templates/source

### Source Discovery

| Variable | Search Root | Exclusion |
|----------|-------------|-----------|
| `CFILES_TEST_CORE` | `tests/core/source` | `*/implemented/*` if game != engine |
| `CFILES_TEST_PLATFORM` | `tests/<platform>/source` | None |
| `CFILES_TEST_GAME` | `tests/<game>/source` | None |

### Compilation

    $(CC) $(CFLAGS) $(INCLUDE) $(FLAGS) -c <source>.c -o <object>.o

    CFLAGS := -Wall -O2
    CORE_OMIT := main.c

### Linking

    $(LD) $(LDFLAGS) $(FLAGS_LINKER) $(OFILES) $(LIBPATHS) $(LIBS) -o $(OUTPUT)

### Compilation Database

    $(MAKE) ... | grep -wE 'cc|gcc|g++' | grep -w '\-c' | \
        jq -nR '[inputs|{directory:..., command:., file:...}]' \
        > $(BUILD)/compile_commands.json
