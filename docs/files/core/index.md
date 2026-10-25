# Core

The portable engine core — the heart of Lavender. It is completely
console-agnostic: every backend implements the platform abstraction
(`platform.h`), so `core/` never knows which console it is running on.

> Documentation for this section is in progress.

## Contents

- `include/` — public engine headers
- `source/` — engine implementation
- `assets/` — engine assets
- `planning/` — design documents

## Porting a new backend

Create a backend definition for everything declared in `platform.h`:

- Struct and macro definitions go in a `platform_defines.h` at the base level
  of the backend's include folder.
- Function definitions from `platform.h` can live anywhere in the backend
  (hint: be organized about it).
