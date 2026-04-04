# Specification: core/include/types/implemented/audio_effect_kind.h

## Overview

Template header that defines the `Audio_Effect_Kind` enum — the set of
audio sound effects available in the game. This file is copied to the game
project directory by `tools/lav_new_project` and is meant to be extended
by the engine user. The contents are injected into `defines_weak.h` via
conditional compilation using the `DEFINE_AUDIO_EFFECT_KIND` guard macro.

## Template Behavior

This file resides in `core/include/types/implemented/` and is copied to
the game project's corresponding `types/implemented/` directory by the
`lav_new_project` script. The game developer extends the copy with
game-specific audio effect kinds. The original in core serves as the
default/template providing a minimal compilable definition.

If the game project does not provide this file (i.e. `DEFINE_AUDIO_EFFECT_KIND`
is not defined after the `#include`), `defines_weak.h` falls back to a
built-in default with only `None` and `Unknown`.

## Dependencies

None (self-contained).

## Types

### Audio_Effect_Kind (enum)

    typedef enum Audio_Effect_Kind {
        Audio_Effect_Kind__None,
        Audio_Effect_Kind__Unknown
    } Audio_Effect_Kind;

| Value | Description |
|-------|-------------|
| `Audio_Effect_Kind__None` | No audio effect / sentinel. |
| `Audio_Effect_Kind__Unknown` | End-of-enum sentinel. Used for array sizing. |

## Injection Mechanism

In `defines_weak.h`:

    #include <types/implemented/audio_effect_kind.h>
    #ifndef DEFINE_AUDIO_EFFECT_KIND
    enum Audio_Effect_Kind {
        Audio_Effect_Kind__None,
        Audio_Effect_Kind__Unknown,
    };
    #endif

The `#define DEFINE_AUDIO_EFFECT_KIND` at the top of this file prevents the
fallback definition from being used when the game project provides its own.

## Agentic Workflow

### Extension Pattern

Add game-specific audio effect kinds between `None` and `Unknown`:

    typedef enum Audio_Effect_Kind {
        Audio_Effect_Kind__None,
        Audio_Effect_Kind__Sword_Swing,
        Audio_Effect_Kind__Footstep,
        Audio_Effect_Kind__Door_Open,
        Audio_Effect_Kind__Unknown
    } Audio_Effect_Kind;

### Constraints

- `Audio_Effect_Kind__None` must remain the first entry (value 0).
- `Audio_Effect_Kind__Unknown` must remain the last entry.
- `Audio_Effect_Kind__Unknown` is used for array sizing in
  `PLATFORM_Audio_Context` (e.g. `audio_effects[NDS_MAX_QUANTITY_OF__AUDIO_EFFECTS]`).
- The `#define DEFINE_AUDIO_EFFECT_KIND` line must not be removed.

## Header Guard

`IMPL_AUDIO_EFFECT_KIND_H`
