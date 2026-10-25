play_audio_effect_and__forget — core/source/audio/audio_effect.c

Allocates a new Audio_Effect from the platform pool, configures it with the given
kind, duration, and a forced RELEASE_ON_COMPLETE flag, hands it to the platform to
start playback, and returns the handle. Returns 0 if the platform fails to allocate.

Pre-conditions:
1. p_PLATFORM_audio_context must be non-null (it is passed to both
   PLATFORM_allocate_audio_effect and PLATFORM_play_audio_effect).
2. the_kind_of__audio_effect is any enum Audio_Effect_Kind value
   (Audio_Effect_Kind__None or Audio_Effect_Kind__Unknown).
3. audio_flags is any Audio_Flags__u8 (a u8); no range constraint needed.
4. duration_of__audio is any Timer__u32.

Post-conditions:
1) If allocation fails, 0 is returned and the caller receives no Audio_Effect.
2) If allocation succeeds, the returned Audio_Effect is fully initialized:
   - the_kind_of__audio_effect holds the caller-supplied kind.
   - p_audio_instance_handle is set by PLATFORM_allocate_audio_effect.
   - audio_flags__u8 equals audio_flags | AUDIO_FLAG__RELEASE_ON_COMPLETE
     (the IS_ACTIVE bit is preserved from the struct's prior state via
     set_audio_effect).
   - timer_for__audio holds duration_of__audio.
3) PLATFORM_play_audio_effect is called with the new Audio_Effect, starting
   playback on the platform side.
4) The effect is marked for automatic release when playback completes
   (RELEASE_ON_COMPLETE was forced by this function).

Correctness Verdict: Correct

Semantic Alignment:
All four struct fields are assigned through the set_audio_effect path — no
member is omitted. The struct has exactly four fields and the function writes
to all four (the_kind_of__audio_effect, p_audio_instance_handle,
audio_flags__u8, timer_for__audio). The RELEASE_ON_COMPLETE flag is correctly
OR'd into the flags before initialization, and the IS_ACTIVE bit is preserved
from the struct's existing state per the set_audio_effect contract.

Implementation Correctness:
Type compatibility — every parameter type matches its target field type
exactly (PLATFORM_Audio_Context *, enum Audio_Effect_Kind, Audio_Flags__u8,
Timer__u32). The OR (audio_flags | AUDIO_FLAG__RELEASE_ON_COMPLETE) operates
on two u8 values, so no truncation occurs.
No undefined behavior — allocation failure is checked with `if (!p_audio_effect)
return 0` before any dereference. No null dereference, no type punning, no
out-of-bounds access.
Validation — p_PLATFORM_audio_context is validated by the platform functions it
is passed to. Enum values and flag values are not validated here; this is
consistent with the Lavender pattern where the caller supplies enum/flag values.

Side Effects:
1. Allocates memory for a new Audio_Effect from the platform pool via
   PLATFORM_allocate_audio_effect.
2. Mutates the returned Audio_Effect struct (sets kind, flags, timer, handle).
3. Calls PLATFORM_play_audio_effect, which triggers the platform's audio
   engine to begin playback.
4. Forces the RELEASE_ON_COMPLETE flag (the effect will be automatically freed
   by the platform when playback completes).
5. Returns a valid Audio_Effect pointer on success, 0 on failure.
