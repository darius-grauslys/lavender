# 1 Specification: core/include/types/implemented/audio_stream_kind.h

## 1.1 Overview

Template header that defines the `Audio_Stream_Kind` enum — the set of
streaming audio tracks (music, ambient loops) available in the game. This
file is copied to the game project directory by `tools/lav_new_project`
and is meant to be extended by the engine user.

## 1.2 Template Behavior

This file resides in `core/include/types/implemented/` and is copied to
the game project's corresponding `types/implemented/` directory by the
`lav_new_project` script. The game developer extends the copy with
game-specific audio stream kinds. If `DEFINE_AUDIO_STREAM_KIND` is not
defined after the `#include`, `defines_weak.h` falls back to a built-in
default.

## 1.3 Dependencies

None (self-contained).

## 1.4 Types

### 1.4.1 Audio_Stream_Kind (enum)

    typedef enum Audio_Stream_Kind {
        Audio_Stream_Kind__None,
        Audio_Stream_Kind__Unknown
    } Audio_Stream_Kind;

| Value | Description |
|-------|-------------|
| `Audio_Stream_Kind__None` | No stream / sentinel. |
| `Audio_Stream_Kind__Unknown` | End-of-enum sentinel. Used for array sizing. |

## 1.5 Injection Mechanism

In `defines_weak.h`:

    #include <types/implemented/audio_stream_kind.h>
    #ifndef DEFINE_AUDIO_STREAM_KIND
    enum Audio_Stream_Kind {
        Audio_Stream_Kind__None,
        Audio_Stream_Kind__Unknown
    };
    #endif

## 1.6 Agentic Workflow

### 1.6.1 Extension Pattern

    typedef enum Audio_Stream_Kind {
        Audio_Stream_Kind__None,
        Audio_Stream_Kind__Overworld_Theme,
        Audio_Stream_Kind__Battle_Theme,
        Audio_Stream_Kind__Unknown
    } Audio_Stream_Kind;

### 1.6.2 Constraints

- `Audio_Stream_Kind__None` must remain first (value 0).
- `Audio_Stream_Kind__Unknown` must remain last.
- The `#define DEFINE_AUDIO_STREAM_KIND` line must not be removed.

## 1.7 Header Guard

`IMPL_AUDIO_STREAM_KIND_H`
