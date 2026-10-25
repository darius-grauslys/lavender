## 1. Header
- **Function name:** `PLATFORM_play_audio__stream`
- **File of origin:** `core/include/platform.h` (line 58)

## 2. Semantic
Begins playback of a continuous background audio stream of the specified kind, dispatched to the platform audio backend.

## 3. Pre-conditions
1. `p_PLATFORM_audio_context` shall be non-null and shall point to a platform audio context in its initial (initialized) state, consistent with how the context is obtained via `get_p_PLATFORM_audio_context_from__game` (`core/include/game.h:259`).
2. `the_kind_of__audio_stream` shall be a valid enumerator of `enum Audio_Stream_Kind`.

## 4. Post-conditions
1. After return, the platform backend is instructed to begin continuous playback of the requested stream kind.
2. The sibling `PLATFORM_is_audio__streaming` (declared at `core/include/platform.h:62`) may subsequently read a backend tracking flag (e.g. `is_audio_context__streaming` in `nds_defines.h:273`) reflecting whether streaming is active. This declaration in `core` performs no state mutation.

## 5. Correctness Verdict
Correct

## 6. Semantic Alignment
The declaration faithfully encodes the intended contract documented in `agents/platform_api.md:173` ("Starts continuous background audio stream"): a `void` function accepting an audio context and a stream-kind enumerator. The parameter names and types map directly to intent (`p_PLATFORM_audio_context` for the target context, `the_kind_of__audio_stream` for the stream to play); there is no reordering, omission, or mislabeling, and as a pure platform API declaration there is no body to drift in `core`.

Finding (read for review, out of `core` scope): every concrete backend implementation located is an empty stub — `nds/source/audio/nds_audio.c:265`, `sdl/source/TMP.c:40`, `no_gui/source/NOT_IMPL.c:71`, and the test stubs `tests/core/source/PLATFORM.c:313` and `tests/templates/source/PLATFORM.c:313`. Because these bodies perform no work, the semantic intent ("starts streaming") is not actually realized by any current backend. This is a known placeholder/stub state (signaled by the `TMP.c`/`NOT_IMPL.c` file names) rather than a defect in the declaration itself, and is flagged here for awareness. Consequently, `PLATFORM_is_audio__streaming` can never observe a `true` streaming flag today.

Additionally, `enum Audio_Stream_Kind` is currently degenerate — it defines only `Audio_Stream_Kind__None` and `Audio_Stream_Kind__Unknown` (see `core/include/types/implemented/audio/audio_stream_kind.h:6-9`, mirrored in `defines_weak.h:156-161`). With no concrete stream kind defined, there is presently no meaningful value a caller could pass to actually start a stream.

## 7. Implementation Correctness
- **Type compatibility:** Declaration types are well-formed. `p_PLATFORM_audio_context` is `PLATFORM_Audio_Context *`, an opaque typedef (`typedef struct PLATFORM_Audio_Context_t PLATFORM_Audio_Context;` at `defines_weak.h:627`), so the declaration is layout-independent of any backend's struct definition (NDS `nds_defines.h:265`, SDL `sdl_defines.h:284`, no_gui `no_gui_defines.h:85` each define a distinct `PLATFORM_Audio_Context_t`). `the_kind_of__audio_stream` is `enum Audio_Stream_Kind`. No implicit conversions or truncation risks exist in the signature.
- **Undefined behavior:** None within `core`; this is a declaration with no body. There is no pointer arithmetic, dereference, type punning, or out-of-bounds access in `core/include/platform.h`. (The empty stub bodies in backends likewise introduce no UB — they are no-op functions.)
- **Validation:** As a platform API boundary, validation of `p_PLATFORM_audio_context` (non-null) and `the_kind_of__audio_stream` (valid enumerator) is the caller's responsibility, consistent with sibling functions `PLATFORM_play_audio_effect` and `PLATFORM_poll_audio_effects`, which also perform no argument checks. For a declaration (and a no-body stub) the question of in-function validation is moot; the established convention is to enforce preconditions at call sites.

## 8. Side Effects
- This declaration introduces no side effects within `core` (it has no body in `core`).
- The behavioral contract promises a backend-specific side effect: the platform audio backend begins continuous stream playback and, by design, sets a backend tracking flag (`is_audio_context__streaming`) that `PLATFORM_is_audio__streaming` later reads.
- In every current backend the implementation is an empty stub, so in practice no observable side effect occurs today; combined with the degenerate `Audio_Stream_Kind__None` default this implies "no stream" semantics at runtime.
