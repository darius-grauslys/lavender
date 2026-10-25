# PLATFORM_allocate_audio_effect

**File of origin:** `core/include/platform.h` (declared line 48)

`PLATFORM_allocate_audio_effect` is a **platform-abstracted** function: its
signature lives in the core header with a doc comment, but the core itself
contains no implementation. Concrete backends supply the implementation
(NDS: `nds/source/audio/nds_audio.c` — the only live one; SDL/no_gui/tests
ship not-implemented stubs that always return null).

## Semantic

Claims an inactive slot from the fixed-size, pre-allocated audio-effect pool
held by the given `PLATFORM_Audio_Context`, marks it active, and returns a
pointer to it. Returns null when the pool is exhausted. This is a **static
pool allocator**, not a heap allocation — consistent with Lavender's
"Initialization != RAII" model (it acquires/claims a slot from existing
storage rather than allocating resources).

## Pre-conditions

1. `p_PLATFORM_audio_context` must be non-null and point to a valid,
   initialized `PLATFORM_Audio_Context`. The implementation dereferences it
   with no null-guard, so a null context is undefined behavior (caller
   responsibility).
2. The context's `audio_effects[]` pool must exist and be in its default
   (all slots inactive) state: inactive slots have `AUDIO_FLAG__IS_ACTIVE`
   clear, which holds for zero-initialized pools.

## Post-conditions

1. On success: returns a non-null `Audio_Effect *` pointing to the
   first inactive slot (lowest index) in the context's pool.
2. On success: the returned slot has `AUDIO_FLAG__IS_ACTIVE` set
   (it is now claimed/active). This is the sole mutation performed.
3. On failure (pool exhausted): returns null (0). No slot is mutated.
4. The other effect fields (`p_audio_instance_handle`, `timer_for__audio`,
   `the_kind_of__audio_effect`, and `audio_flags__u8` aside from the active
   bit) are left untouched; the caller is expected to populate them
   afterward (e.g. via `set_audio_effect`, which preserves the active bit).

## Correctness Verdict

Correct

## Semantic Alignment

The NDS reference implementation fulfills the semantic intent: it scans the
bounded pool for the first inactive slot, marks it active, and returns it;
null is returned on exhaustion. The stub backends (SDL/no_gui/tests) do not
fulfill the semantic (they unconditionally return null), but they are
explicit not-implemented stubs, not a contract violation.

Noted divergence: the header doc comment reads "Returns false if fails to
allocate audio effect." but the return type is `Audio_Effect *` (the failure
value is null/0, not a boolean). The type system prevents misuse, but the
comment is textually incorrect; it should read "Returns null (0) if fails
to allocate audio effect."

## Implementation Correctness

- **Types:** `Audio_Effect *` return matches the pointer yielded by
  `NDS_get_p_audio_effect_by__index_in__audio_context`; parameter
  `PLATFORM_Audio_Context *` matches. No implicit conversion or truncation.
- **Undefined behavior:** None under the stated pre-conditions. The loop
  bound `NDS_MAX_QUANTITY_OF__AUDIO_EFFECTS` (16) matches the array
  dimension exactly (`nds_defines.h:263/269`) — no off-by-one, no OOB.
  `p_audio_effect` is initialized to 0 before the loop, so the not-found
  path correctly reaches the `return 0`.
- **Validation:** No null-check on `p_PLATFORM_audio_context`; acceptable for
  a platform-internal hot path as a caller responsibility, but it is an
  implicit pre-condition (see above). No per-slot validation is needed since
  the index is tightly bounded.
- The returned pointer aliases a slot inside the caller-provided context's
  pool (not separately owned), which matches the contract.

## Side Effects

1. Sets the `AUDIO_FLAG__IS_ACTIVE` bit in the `audio_flags__u8` field of
   the first inactive `Audio_Effect` slot within the context's pool — i.e.
   it claims the slot. This is the primary, intended side effect.
2. Does not resize, reorder, or otherwise touch any other pool slot, nor the
   context pointer itself, nor the returned slot's `p_audio_instance_handle`,
   `timer_for__audio`, `the_kind_of__audio_effect`, or other flag bits.
3. Does not allocate heap memory.
4. In NDS builds with `NDEBUG` undefined, emits a `debug_warning` string on
   the exhausted-pool failure path (build-dependent, minor).

## Notes (Lavender pool lifecycle)

The active bit is the slot-freeing marker: `set_audio_as__inactive`
(`audio_effect.h:60`) clears it, and `set_audio_as__active`
(`audio_effect.h:54`) — used here — sets it. `initialize_audio_effect`
(`core/source/audio/audio_effect.c:4`) only assigns semantic fields and does
NOT perform RAII resource setup or reset the active bit; `set_audio_effect`
preserves the active bit (`audio_flags | AUDIO_FLAG__IS_ACTIVE`). This
confirms `PLATFORM_allocate_audio_effect` composes correctly with the
surrounding Lavender audio lifecycle (claim -> configure -> play -> release).
