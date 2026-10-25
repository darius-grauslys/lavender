PLATFORM_initialize_audio — core/include/platform.h

Initializes the platform audio subsystem and resets the audio-effect pool slots to their default/inactive state.

Pre-conditions:
1. `p_PLATFORM_audio_context` must be a non-null pointer to a writable, backend-allocated `PLATFORM_Audio_Context`.
2. No null-pointer validation is performed — per codebase convention (low-level platform-backend function), the caller is responsible for passing a valid context.
3. On the NDS backend, the maxmod soundbank (`soundbank_bin`) and effect bank must be linked at compile time (external dependency).
4. The caller is expected to invoke this once during early platform initialization (e.g. from `PLATFORM_main`) before any other audio operation.

Post-conditions:
1. NDS backend: the context's `randomizer` is seeded; maxmod audio memory is initialized via `mmInitDefaultMem`; every sound effect in the effect bank is loaded via `mmLoadEffect` for each `MSL_BANKSIZE` entry.
2. NDS backend: every slot in `audio_effects[0 .. NDS_MAX_QUANTITY_OF__AUDIO_EFFECTS-1]` is reset to a default inactive state via `initialize_audio_effect` (kind = `Audio_Effect_Kind__None`, flags = `AUDIO_FLAGS__NONE`, timer = `{0,0}`, handle pointing into `maxmod_sfx_handles`).
3. SDL / no_gui / test backends: empty stub no-ops; the context is left unmodified (audio simply non-functional on those backends).
4. Returns `void` (no return value / status code).

Correctness Verdict: Correct

Semantic Alignment:
The function fulfills its role as a platform-level audio subsystem initializer. On the NDS backend (the only functional implementation) it (a) sets up platform audio resources and (b) resets the `audio_effects` pool slots to defaults. The pool-slot reset is Lavender-style initialization (clearing/reusing pool elements) and correctly delegates to `initialize_audio_effect`, which assigns all four `Audio_Effect` fields — no member omitted. The loop bounds (`MSL_BANKSIZE` for the effect bank, `NDS_MAX_QUANTITY_OF__AUDIO_EFFECTS` for the `audio_effects`/`maxmod_sfx_handles` arrays) correctly match their respective array extents, so the resets cover the entire pool. The stub no-ops in SDL/no_gui/test backends leave audio simply non-functional there, which is acceptable for backends without audio support.

Semantic classification (Lavender-specific — initialization ≠ RAII):
This function performs BOTH, which must be explicit:
- Lavender-style initialization / pool cleanup: resets each `audio_effects` slot to a default inactive state (consistent with the Lavender pattern where "initialize" = reset to initial conditions for reuse).
- Platform resource acquisition (RAII-style): `mmInitDefaultMem` + `mmLoadEffect` acquire/configure platform audio resources. The header `platform.h` (lines 13-19) explicitly states these `PLATFORM_*` functions are platform-dependent and "NOT implemented in core," and the audio section is the backend's responsibility. At the platform-abstraction layer, resource setup is necessary and legitimate; the "initialization ≠ RAII" principle governs core-engine struct lifecycle, not platform resource setup. (Sibling platform functions follow the same pattern, e.g. `PLATFORM_initialize_file_system_context`, `PLATFORM_initialize_rendering__game`, `PLATFORM_initialize_game`.)

The declaration is also marked `// TODO: remove` (platform.h line 41), and module reports indicate audio management is being moved inline ("Audio management now inline (Game struct holds context)"); the function is effectively deprecated in favor of inlined context management.

Implementation Correctness:
- Type compatibility: parameter `PLATFORM_Audio_Context *` matches the struct type; `&p_PLATFORM_audio_context->maxmod_sfx_handles[i]` (`mm_sfxhand *`) is implicitly converted to the `void *p_audio_handle` parameter of `initialize_audio_effect` — correct. `Audio_Effect_Kind__None` matches `enum Audio_Effect_Kind`; `AUDIO_FLAGS__NONE` matches `Audio_Flags__u8`; `(Timer__u32){0, 0}` matches `Timer__u32` (struct has two u32 members). The seed `(Psuedo_Random_Seed__u32)p_PLATFORM_audio_context` casts a pointer to `uint32_t`; on the 32-bit NDS target this is well-defined and non-truncating (cf. the entity_manager review, which uses explicit `(u32)(uint64_t)` narrowing on 64-bit targets).
- Undefined behavior: no pointer arithmetic, no null dereference (assumes valid input per codebase convention), no type punning, no out-of-bounds access. Loop index `Index__u8` vs small constants `MSL_BANKSIZE`/`NDS_MAX_QUANTITY_OF__AUDIO_EFFECTS` — no overflow. `NDS_get_p_audio_effect_by__index_in__audio_context` indexes `audio_effects[index]` within `[0,16)` — in bounds.
- Validation: none performed, consistent with the low-level platform-backend convention; the caller (`PLATFORM_main` at nds/source/nds_main.c:31) is responsible for passing a valid, backend-allocated context.

Side Effects:
- Mutates `p_PLATFORM_audio_context`: seeds its `randomizer` field; initializes maxmod memory; loads sound-effect banks; resets all `audio_effects` slots (whose `p_audio_instance_handle` is repointed into `maxmod_sfx_handles`).
- External side effects (NDS backend only): invokes maxmod library routines `mmInitDefaultMem` and `mmLoadEffect`, which initialize audio library state and load sound data into memory.
- SDL / no_gui / test backends: no side effects (empty stubs).
