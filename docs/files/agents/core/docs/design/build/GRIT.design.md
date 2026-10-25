# GRIT Compilation — Pluggable Build Integration

## Problem

The Lavender core build system (`Makefile.build`, `Makefile.include`) provides a
unified, bear-based compilation pipeline: a single `%.o: %.c` pattern rule in the
top-level `Makefile.build` handles all source files, and `bear --force-preload`
intercepts every compiler invocation to produce `compile_commands.json`.

Certain Lavender projects (AncientsGame, DungeonGame) use **grit** to generate
`.c` and `.s` assets from sprite sheets. These files live in `lav_gen/grit/` and
need to be compiled alongside regular source. The current project Makefiles
override the core pattern rule with project-specific rules that re-invoke `$(CC)`
with hardcoded flags, duplicating compilation logic and breaking bear's ability
to intercept those invocations.

## Current State (AncientsGame)

`AncientsGame/Makefile.build` defines explicit rules for `$(CFILES_GAME)` and
`$(CFILES_GRIT)` that:

1. Call `$(CC)` directly (not via the core pattern rule).
2. Include a stale `$(ADD_COMPILE_COMMAND) add ...` callback that is never
   defined — it silently fails as `add: not found`.
3. Duplicate `$(CFLAGS) $(LIBS) $(INCLUDE) $(FLAGS)` from the core rule.

`AncientsGame/Makefile.include` adds:
- `$(GAME_DIR)/lav_gen/grit/$(BACKEND)` to `INCLUDE_GAME`
- `CFILES_GRIT` find command
- `OFILES_GAME := $(CFILES_GAME:.c=.o) $(CFILES_GRIT:.c=.o)`

## Desired State

A pluggable integration point so any project can register additional source
directories (grit output, generated code, etc.) without overriding the core
`%.o: %.c` pattern rule.

### Candidate Approaches

1. **Variable-based source discovery**
   - Introduce `EXTRA_C_DIRS` in core `Makefile.include` — a space-separated
     list of directories whose `.c` files get added to `CFILES_GAME`.
   - Core pattern rule already picks up anything matching `%.o: %.c` if `vpath`
     is set, so projects would set `vpath %.c $(EXTRA_C_DIRS)`.

2. **Extension hook file**
   - Projects provide an optional `Makefile.build.ext` that gets `include`'d
     after the core rules. The hook sets `vpath` and appends to `OFILES_GAME`.
   - No changes to core files needed.

3. **Pipeline registration**
   - A `.lavender/pipelines/build.json` declares extra source dirs, and
     `lav_new_project` / `gen_lav_project.py` generate the vpath/OFILES lines.
   - Most automated but requires tooling changes.

## Recommendation

Start with approach **2** (hook file). Zero core changes, projects opt in by
dropping a `Makefile.build.ext` that looks like:

```make
vpath %.c $(GAME_DIR)/lav_gen/grit/$(BACKEND)
export OFILES_GAME += $(wildcard $(GAME_DIR)/lav_gen/grit/$(BACKEND)/*.o)
```

Once validated across projects, approach **1** can replace the hook as the
canonical solution.

## Files Affected

| File | Action |
|------|--------|
| `core/Makefile.include` | Optionally add `EXTRA_C_DIRS` variable and vpath |
| `core/Makefile.build` | Optionally add `OFILES` accumulation hook |
| `examples/Makefiles/Makefile.include` | Document `EXTRA_C_DIRS` or hook usage |
| `tools/lavender_tools/gen_lav_project.py` | Optionally generate hook file |
| AncientsGame, DungeonGame | Replace custom rules with hook |

## Notes

- `$(ADD_COMPILE_COMMAND)` was an abandoned compile_commands.json callback
  from the pre-bear build system. It is never defined and can be removed.
- `bear --force-preload` handles all compilation interception; no per-rule
  callbacks needed.
- Grirt `.s` files from nitrogrit may need a separate pattern rule (e.g.,
  `%.o: %.s` for ARM assembly).
