# 1 Specification: core/include/audio/audio_effect.h

## 1.1 Overview

Provides initialization, playback, and `static inline` flag management
functions for `Audio_Effect` — the engine's representation of a single
sound effect instance. An audio effect wraps a platform-specific audio
handle with a timer, kind discriminator, and flags controlling active
state, looping, and auto-release behavior.

## 1.2 Dependencies

- `defines.h` (for `Audio_Effect`, `Audio_Flags__u8`, `Audio_Effect_Kind`,
  `Timer__u32`, all flag macros)
- `defines_weak.h` (forward declarations)
- `platform.h` (for `PLATFORM_Audio_Context`, `PLATFORM_allocate_audio_effect`,
  `PLATFORM_play_audio_effect`)

## 1.3 Types

### 1.3.1 Audio_Effect (struct, defined in `defines.h`)

    typedef struct Audio_Effect_t {
        void                    *p_audio_instance_handle;
        Timer__u32              timer_for__audio;
        enum Audio_Effect_Kind  the_kind_of__audio_effect;
        Audio_Flags__u8         audio_flags__u8;
    } Audio_Effect;

| Field | Type | Description |
|-------|------|-------------|
| `p_audio_instance_handle` | `void*` | Platform-specific audio instance handle. Opaque pointer managed by the platform backend. |
| `timer_for__audio` | `Timer__u32` | Duration timer for the audio effect. When expired, the effect may be released if `RELEASE_ON_COMPLETE` is set. |
| `the_kind_of__audio_effect` | `enum Audio_Effect_Kind` | Discriminator identifying which sound effect this is. |
| `audio_flags__u8` | `Audio_Flags__u8` | Bitfield controlling active state, looping, and auto-release. |

### 1.3.2 Audio_Flags__u8 (u8, defined in `defines.h`)

| Flag | Bit | Description |
|------|-----|-------------|
| `AUDIO_FLAG__IS_ACTIVE` | 0 | Audio effect is currently playing. |
| `AUDIO_FLAG__RELEASE_ON_COMPLETE` | 1 | Automatically release the effect when its timer expires. |
| `AUDIO_FLAG__IS_LOOPING` | 2 | Audio effect loops continuously. |

### 1.3.3 Audio_Effect_Kind (enum, defined in `types/implemented/audio_effect_kind.h`)

    typedef enum Audio_Effect_Kind {
        Audio_Effect_Kind__None,
        Audio_Effect_Kind__Unknown
    } Audio_Effect_Kind;

Games extend this enum in their `types/implemented/audio_effect_kind.h` copy.
`Audio_Effect_Kind__None` is the sentinel (value 0).
`Audio_Effect_Kind__Unknown` is the end-of-enum sentinel.

## 1.4 Functions

### 1.4.1 Initialization

| Function | Signature | Description |
|----------|-----------|-------------|
| `initialize_audio_effect` | `(Audio_Effect*, void* p_audio_handle, Audio_Effect_Kind, Audio_Flags__u8, Timer__u32 duration) -> void` | Full initialization. Sets the audio handle, kind, flags, and duration timer. |

### 1.4.2 Convenience Initialization (static inline)

| Function | Signature | Description |
|----------|-----------|-------------|
| `set_audio_effect` | `(Audio_Effect*, Audio_Effect_Kind, Audio_Flags__u8, Timer__u32 duration) -> void` | Re-initializes an audio effect while preserving its existing `p_audio_instance_handle` and `IS_ACTIVE` flag. Calls `initialize_audio_effect` internally, passing the existing handle and OR-ing the existing `IS_ACTIVE` state into the new flags. |

### 1.4.3 Playback

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `play_audio_effect_and__forget` | `(PLATFORM_Audio_Context*, Audio_Effect_Kind, Audio_Flags__u8, Timer__u32 duration) -> Audio_Effect*` | `Audio_Effect*` | Allocates an audio effect from the platform audio context, initializes it, and begins playback. Returns a pointer to the allocated effect, or null on failure. The caller does not need to manage the returned effect — it will be released automatically if `AUDIO_FLAG__RELEASE_ON_COMPLETE` is set in the flags. |

### 1.4.4 Flag Queries (static inline)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `is_audio__active` | `(Audio_Effect*) -> bool` | `bool` | True if `AUDIO_FLAG__IS_ACTIVE` is set. |
| `is_audio__released_on_completion` | `(Audio_Effect*) -> bool` | `bool` | True if `AUDIO_FLAG__RELEASE_ON_COMPLETE` is set. |
| `is_audio__looping` | `(Audio_Effect*) -> bool` | `bool` | True if `AUDIO_FLAG__IS_LOOPING` is set. |

### 1.4.5 Flag Mutations (static inline)

| Function | Signature | Description |
|----------|-----------|-------------|
| `set_audio_as__active` | `(Audio_Effect*) -> void` | Sets `AUDIO_FLAG__IS_ACTIVE`. |
| `set_audio_as__inactive` | `(Audio_Effect*) -> void` | Clears `AUDIO_FLAG__IS_ACTIVE`. |
| `set_audio_as__releasing_on_completion` | `(Audio_Effect*) -> void` | Sets `AUDIO_FLAG__RELEASE_ON_COMPLETE`. |
| `set_audio_as__not_releasing_on_completion` | `(Audio_Effect*) -> void` | Clears `AUDIO_FLAG__RELEASE_ON_COMPLETE`. |
| `set_audio_as__looping` | `(Audio_Effect*) -> void` | Sets `AUDIO_FLAG__IS_LOOPING`. |
| `set_audio_as__not_looping` | `(Audio_Effect*) -> void` | Clears `AUDIO_FLAG__IS_LOOPING`. |

## 1.5 Agentic Workflow

### 1.5.1 Usage Pattern — Fire and Forget

The most common usage is `play_audio_effect_and__forget`:

    play_audio_effect_and__forget(
        p_PLATFORM_audio_context,
        Audio_Effect_Kind__Sword_Swing,
        AUDIO_FLAG__RELEASE_ON_COMPLETE,
        duration_timer);

This allocates, initializes, and plays the effect in one call. The effect
is automatically released when its timer expires because
`AUDIO_FLAG__RELEASE_ON_COMPLETE` is set.

### 1.5.2 Usage Pattern — Managed Playback

For effects that need to be controlled after creation (e.g. looping ambient
sounds):

    Audio_Effect *p_effect = PLATFORM_allocate_audio_effect(
        p_PLATFORM_audio_context);
    initialize_audio_effect(
        p_effect,
        p_effect->p_audio_instance_handle,
        Audio_Effect_Kind__Ambient_Wind,
        AUDIO_FLAG__IS_LOOPING,
        duration_timer);
    PLATFORM_play_audio_effect(
        p_PLATFORM_audio_context,
        p_effect);
    // Later:
    set_audio_as__inactive(p_effect);

### 1.5.3 Usage Pattern — Re-initialization with `set_audio_effect`

`set_audio_effect` preserves the platform audio handle and the active state,
allowing you to change the kind, flags, or duration of an already-allocated
effect without reallocating:

    set_audio_effect(
        p_effect,
        Audio_Effect_Kind__New_Sound,
        AUDIO_FLAG__RELEASE_ON_COMPLETE,
        new_duration);

The `IS_ACTIVE` flag from the existing effect is preserved via OR into the
new flags. The `p_audio_instance_handle` is reused.

### 1.5.4 Ownership

Audio effects are pooled in `PLATFORM_Audio_Context`. The pool size is
platform-defined. The platform backend manages allocation and deallocation
of the pool via `PLATFORM_allocate_audio_effect`.

### 1.5.5 Polling

`PLATFORM_poll_audio_effects` is called each frame to update timers and
release completed effects. This is a platform function, not declared in
this header.

### 1.5.6 Preconditions

- All functions require non-null `p_audio_effect`.
- `play_audio_effect_and__forget` requires non-null `p_PLATFORM_audio_context`.
- `play_audio_effect_and__forget` returns null if the platform audio pool
  is exhausted.

### 1.5.7 Postconditions

- `initialize_audio_effect` overwrites all fields of the `Audio_Effect`.
- `set_audio_effect` preserves `p_audio_instance_handle` and the existing
  `IS_ACTIVE` state.
- Flag mutation functions modify only the targeted bit, preserving all others.

## 1.6 Header Guard

`AUDIO_EFFECT_H`
