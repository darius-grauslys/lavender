# Audio — Thin wrapper over the platform audio contract

## Purpose & place in engine

The audio module manages discrete sound effects via the `Audio_Effect` type. It is a thin layer: it allocates an effect handle from the platform, sets flags, plays it, and the platform's per-frame `PLATFORM_poll_audio_effects` call drives playback completion, looping, and release.

- **Frame hook:** `PLATFORM_poll_audio_effects` is called once per frame in `manage_game__post_render` (`core/source/game.c`). This is the only time audio is ticked.
- **No effect pool in core:** Audio effects are created from any engine code holding a `PLATFORM_Audio_Context*`. The platform owns allocation and the actual sound buffer.
- **Lifecycle:** Effects live until destroyed by the platform (auto-release on completion) or by marking them inactive.
- **Effect lifecycle:** `play_audio_effect_and__forget()` → `PLATFORM_allocate_audio_effect()` (platform-owned memory) → `set_audio_effect()` (initializes struct, preserves `IS_ACTIVE`; `RELEASE_ON_COMPLETE` is OR'd in by the caller) → `PLATFORM_play_audio_effect()` kicks off playback → per-frame `PLATFORM_poll_audio_effects()` decrements timers, handles completion/looping/release. Core can also manually mark effects inactive via `set_audio_as__inactive()`.
- **Streaming:** The `Audio_Effect` type models one-shot effects only. For continuous streams there are `PLATFORM_play_audio__stream()` and `PLATFORM_is_audio__streaming()` (declared in `platform.h`, defined in the platform backends), but the audio module's `audio_effect.c/.h` do not currently expose a streaming wrapper.

## Public API surface

### Types

```c
typedef struct Audio_Effect_t {
    void                    *p_audio_instance_handle;
    Timer__u32              timer_for__audio;
    enum Audio_Effect_Kind  the_kind_of__audio_effect;
    Audio_Flags__u8         audio_flags__u8;
} Audio_Effect;
```
Defined in `core/include/defines.h`.

### Flag constants

Defined in `core/include/defines.h`:

```c
#define AUDIO_FLAGS__NONE 0
#define AUDIO_FLAG__IS_ACTIVE BIT(0)
#define AUDIO_FLAG__RELEASE_ON_COMPLETE BIT(1)
#define AUDIO_FLAG__IS_LOOPING BIT(2)
```

### Functions

```c
void initialize_audio_effect(
    Audio_Effect *p_audio_effect,
    void *p_audio_handle,
    enum Audio_Effect_Kind the_kind_of__audio_effect,
    Audio_Flags__u8 audio_flags,
    Timer__u32 duration_of__audio);
```
Sets all members of an `Audio_Effect`, including `p_audio_instance_handle` (from its `p_audio_handle` argument). `set_audio_effect()` calls it with the effect's *existing* handle, which is how the handle survives re-initialization.

```c
static inline void set_audio_effect(
    Audio_Effect *p_audio_effect,
    enum Audio_Effect_Kind the_kind_of__audio_effect,
    Audio_Flags__u8 audio_flags,
    Timer__u32 duration_of__audio);
```
Defined in `core/include/audio/audio_effect.h`. Re-initializes the effect while preserving `IS_ACTIVE` from the existing flags (`audio_flags | (p_audio_effect->audio_flags__u8 & AUDIO_FLAG__IS_ACTIVE)`).

```c
Audio_Effect *play_audio_effect_and__forget(
    PLATFORM_Audio_Context *p_PLATFORM_audio_context,
    enum Audio_Effect_Kind the_kind_of__audio_effect,
    Audio_Flags__u8 audio_flags,
    Timer__u32 duration_of__audio);
```
Allocates via `PLATFORM_allocate_audio_effect`, sets the effect with `AUDIO_FLAG__RELEASE_ON_COMPLETE` implicitly added, plays it, and returns the handle. Returns `0` on allocation failure.

### Static inline helpers (header-only)

```c
static inline bool is_audio__active(Audio_Effect *p_audio_effect);
static inline bool is_audio__released_on_completion(Audio_Effect *p_audio_effect);
static inline bool is_audio__looping(Audio_Effect *p_audio_effect);
static inline void set_audio_as__active(Audio_Effect *p_audio_effect);
static inline void set_audio_as__inactive(Audio_Effect *p_audio_effect);
static inline void set_audio_as__releasing_on_completion(Audio_Effect *p_audio_effect);
static inline void set_audio_as__not_releasing_on_completion(Audio_Effect *p_audio_effect);
static inline void set_audio_as__looping(Audio_Effect *p_audio_effect);
static inline void set_audio_as__not_looping(Audio_Effect *p_audio_effect);
```
All defined in `core/include/audio/audio_effect.h`. Bitwise test or set on `audio_flags__u8`.

## Key flows

### Audio effect from allocate to release (full path)

1. Any engine code calls `play_audio_effect_and__forget(p_PLATFORM_audio_context, kind, flags, duration)`.
2. `PLATFORM_allocate_audio_effect(p_PLATFORM_audio_context)` returns `Audio_Effect*` (platform-owned).
3. `play_audio_effect_and__forget()` OR's `RELEASE_ON_COMPLETE` into the flags; `set_audio_effect()` then initializes the struct, preserving `IS_ACTIVE`.
4. `PLATFORM_play_audio_effect(p_PLATFORM_audio_context, p_audio_effect)` starts playback.
5. Per-frame: `PLATFORM_poll_audio_effects(p_PLATFORM_audio_context)` runs.
    - The platform backend checks `IS_ACTIVE` and the timer.
    - If the effect is done and `RELEASE_ON_COMPLETE` is set, the platform frees the handle and clears `IS_ACTIVE`.
    - If `LOOPING` is set, the timer resets.
6. Core code can query state via the static inline helpers at any time.

## Dependencies

**Calls downward:**

| Function | Called from |
|---|---|
| `PLATFORM_allocate_audio_effect` | `play_audio_effect_and__forget` (`audio_effect.c`) |
| `PLATFORM_play_audio_effect` | `play_audio_effect_and__forget` (`audio_effect.c`) |
| `PLATFORM_poll_audio_effects` | `manage_game__post_render` (`game.c`) |
| `PLATFORM_initialize_audio` | NDS backend init (`nds/source/nds_main.c`; declared in `platform.h`, marked TODO:remove) |
| `PLATFORM_play_audio__stream` | Backend-specific code (declared in `platform.h`) |
| `PLATFORM_is_audio__streaming` | Backend-specific code (declared in `platform.h`) |

**Called upward:** None. The module is called by any code with access to `PLATFORM_Audio_Context*`.

**platform.h usage:** The `core/include/audio/audio_effect.h` header includes `platform.h` for `PLATFORM_Audio_Context*` in the public API signature; the source `.c` file does not include `platform.h`.

## CROSS-CUTTING CONCERNS

**Fixed-capacity / no allocation:** The `Audio_Effect` struct itself is not allocated by core. The platform backend owns the allocation pool. There is no `Audio_Effect` array in `defines.h`.

**Game-action protocol:** Audio effects are not game actions. They are intended to be triggered directly from engine code rather than flowing through the game-action dispatch pipeline. Note: no code in the repo currently calls `play_audio_effect_and__forget` (or any other public function here) — the API is unused outside the backends' `PLATFORM_*` implementations.

**Serialization:** `Audio_Effect` has no `Serialization_Header` and no built-in serialization. To persist audio state, the game layer must snapshot `the_kind_of__audio_effect`, `audio_flags__u8`, and `timer_for__audio` manually and re-create the effect via `play_audio_effect_and__forget`.

## Known rough edges

- SDL audio is **STUBBED** in `sdl/source/TMP.c`. NDS has real audio via the mmEffect library (`mmInitDefaultMem`/`mmLoadEffect`/`mmEffectRelease`). no_gui stubs audio with `NOT_IMPL.c`.
- No streaming wrapper exists in the audio module -- `PLATFORM_play_audio__stream` and `PLATFORM_is_audio__streaming` are declared in `platform.h` but the audio module's public API only exposes one-shot effects.
- `set_audio_effect` preserves `IS_ACTIVE` from existing flags but does not clear other flags (e.g. `RELEASE_ON_COMPLETE`, `LOOPING`), so repeated calls accumulate flags.

## Key files table

| File | Role |
|---|---|
| `core/source/audio/audio_effect.c` | Effect lifecycle: `initialize_audio_effect`, `play_audio_effect_and__forget` |
| `core/include/audio/audio_effect.h` | Public API: `set_audio_effect`, flag helpers (all static inline) |

