# Manual Core Module Review Process

## Purpose

This document defines the manual, step-by-step process for reviewing core modules
of the Lavender codebase. It is the operational companion to `design_guide.md` and
the terminology index.

## Rules

1. **Follow `./agents/core/design/design_guide.md`** for all analysis work.
2. **Use terminology from `./agents/terminiologies/index.md`** consistently in all
   analysis output.
3. **Analysis is written to the chat only.** Do not write analysis to any file.
4. Progress is tracked with the script `./track_core_modules.py` via its CLI:
   - `./track_core_modules.py --next` — find the module next to review.
   - `./track_core_modules.py --current` — see what has already been tracked.
   - `./track_core_modules.py --track MODULE_NAME` — track a module name as done
     with analysis. Use this only when the user says a module is done.

## Workflow

1. Write this process document (before reading anything else).
2. Run `./track_core_modules.py --next` to find the next module to review.
3. Read the `.md` files referenced by that module's entry.
4. Proceed with analysis per `design_guide.md`, using the shared terminology.
5. Write the analysis to the chat.
6. When the user says the module is done, run
   `./track_core_modules.py --track MODULE_NAME` to record it.
7. Repeat from step 2 for the next module.
