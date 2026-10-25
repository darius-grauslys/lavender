# Planning: platform.h — Incorrect Modules

**Review source:** `agents/core/review/include/platform.h/incorrect_modules.md`

**Source files reviewed (read-only):**
- `core/include/platform.h` (declarations)
- `core/include/defines.h`, `core/include/defines_weak.h`
- `core/source/rendering/sprite_manager.c`
- `core/source/rendering/aliased_texture_manager.c`
- `core/source/rendering/graphics_window_manager.c`
- `core/source/game.c`
- `core/source/entity/entity.c`
- `core/source/multiplayer/tcp_socket.c`
- `core/source/multiplayer/tcp_socket_manager.c`
- `core/source/serialization/game_directory.c`
- `core/source/world/serialization/world_directory.c`
- Per-backend implementations: `sdl/source/*`, `nds/source/*`, `no_gui/source/*`
- `tests/core/source/PLATFORM.c`, `tests/templates/source/PLATFORM.c` (test stubs)

---

## 1. Problem Identification

The 29 functions flagged in the review cluster into **seven defect classes**. Each is summarized below; every flagged function is named in the Resolution Assessment (§3). Note that `PLATFORM_tcp_end` (review entry #29) carries a **Correct** verdict in its own review file — it is listed here only as a downstream *consequence* of the `PLATFORM_tcp_begin` Win32 inversion (see §1.3 / §3.3), not as an independent defect.

### 1.1 Signature/ABI Incompatibility (NDS backend) — **Non-Injective Translation**
The NDS backend defines five `PLATFORM_*` functions with parameter types or arities that conflict with the `platform.h` prototype included in the same translation unit — a C11 6.7p4 **constraint violation** (hard error under `-Wall`). The canonical SDL/no_gui/test-stub implementations are conformant; only the NDS definitions are broken, so two distinct signatures map onto one symbol name (`Non-Injective Translation`) and the core contract is not upheld on NDS.

- `PLATFORM_allocate_texture` — NDS defines `PLATFORM_Texture *` return, 2 params; header declares `bool`, 4 params.
- `PLATFORM_use_texture` — NDS defines 2nd param as `PLATFORM_Texture *texture`; header declares `Texture texture` (by value).
- `PLATFORM_release_texture` — NDS defines 2nd param as `PLATFORM_Texture *texture`; header declares `Texture texture`.
- `PLATFORM_allocate_sprite` — NDS defines 2 params (`PLATFORM_Gfx_Context *`, `Sprite_Allocation_Specification *`); header declares 4 params (`Gfx_Context *`, `Graphics_Window *`, `Texture_Flags`, `Sprite *`).
- `PLATFORM_release_sprite` — NDS defines 1st param as `PLATFORM_Gfx_Context *`; header declares `Gfx_Context *`.

### 1.2 Missing Return on Non-Void Function (NDS log backend) — **Postcondition** / UB
Six NDS log functions are declared `bool` but fall off the end of the success path without a `return` statement after a `void` callee call — **undefined behavior** (C99 §6.8.6.4); the documented "returns `true` on success" **Postcondition** is not honored:

- `PLATFORM_update_log__global` (`nds/source/nds_log.c:9`)
- `PLATFORM_update_log__local` (`nds/source/nds_log.c:22`)
- `PLATFORM_update_log__system` (`nds/source/nds_log.c:35`)
- `PLATFORM_clear_log__global` (`nds/source/nds_log.c:48`)
- `PLATFORM_clear_log__local` (`nds/source/nds_log.c:60`)
- `PLATFORM_clear_log__system` (`nds/source/nds_log.c:72`)

### 1.3 TCP/Socket Logic Defects
- **`PLATFORM_tcp_server`** — the `listen()`-failure path returns `0` without closing the socket descriptor or resetting the pool slot, leaking both the OS descriptor and a pool slot (violates the "failed call leaves the context pool usable" **Postcondition** / **Conservation Law**). The `fcntl`-failure path also has an inverted error-log condition in the SDL mirror.
- **`PLATFORM_tcp_close_socket`** — the NO_GUI implementation inverts the return-value contract: it returns `false` on error and `true` on success, contradicting the header's "returns `true` if any errors were encountered." The core caller `unbind_tcp_socket` (`tcp_socket.c:177`) has adapted to this inverted semantics, so SDL and NO_GUI builds disagree with the documented contract (**de facto contract coupling**).
- **`PLATFORM_tcp_poll_connect`** — the `EALREADY` errno (which Linux yields on every re-issued `connect()` against a still-connecting socket) is absent from the `switch`, falling to `default` and reporting `Disconnected`. Since the contract requires calling this function "every frame," any connection with latency beyond one frame is prematurely reported failed (**Under Specified Dispatch** / unhandled **Boundary Condition**). The re-issue-`connect()` technique itself is non-portable; the POSIX-recommended approach is `select`/`poll` + `getsockopt(SO_ERROR)`.
- **`PLATFORM_tcp_begin`** — the Win32 path inverts the `WSAStartup` condition: `!WSAStartup(...)` is true on *success*, so the function logs an error and returns `NULL` on the success path while proceeding only when `WSAStartup` *failed* (sockets used without Winsock initialized) (**Mode Confusion** / inverted logic).
- **`PLATFORM_tcp_end`** — **no independent defect** (its own review verdict is *Correct*). It is listed in the review solely because, as a consequence of the `PLATFORM_tcp_begin` Win32 inversion, its `WSACleanup()` is reached on both the begin-success-abort path and the begin-failure path. Correcting `PLATFORM_tcp_begin` removes this anomaly; `PLATFORM_tcp_end` itself needs no change. (A separate, out-of-scope hygiene note: it does not close still-open OS socket descriptors before freeing the context.)

### 1.4 Filesystem I/O Defects
- **`PLATFORM_write_file`** — the `fwrite` return value (`size_of__write`) is stored then discarded; the function unconditionally returns `PLATFORM_Write_File_Error__None`, so short writes and total failures are silently swallowed. Callers' `if (error)` checks in `entity.c` are dead code (**Contract-First** violation: the error-reporting half of the contract is never produced).
- **`PLATFORM_read_file`** — the NDS backend has the `End_Of_File` check commented out; the no_gui backend has no check at all. Both always return `PLATFORM_Read_File_Error__None`. The `System_Busy` enum value is never produced by any backend (**backend parity / Stub-real divergence**).
- **`PLATFORM_get_position_in__file`** — the return type `Index__u32` (unsigned) cannot represent the documented `-1` error **Sentinel**; `ftell`'s `-1L` becomes `UINT32_MAX`. The null-handler error path returns `PLATFORM_Read_File_Error__Unknown` (= 3), which is a valid non-error file position — the error **Sentinel** is neither self-consistent nor distinguishable from a real offset. The debug abort message mislabels the function as `PLATFORM_read_file`.
- **`PLATFORM_set_position_in__file`** — the debug null-check path returns `PLATFORM_Read_File_Error__Unknown` (value 3, implicitly `true`) from a `bool` function on an error path that should return `false`. The debug abort message mislabels the function as `PLATFORM_read_file` (copy-paste defect).
- **`PLATFORM_append_base_directory_to__path`** — the `strncpy` count is `MAX_LENGTH_OF__IO_PATH` (the full buffer size) regardless of the write offset `*p_index_of__path_end`, so when the offset is non-zero the copy can write past the end of the buffer by up to `*p_index_of__path_end` bytes (**Boundary Condition** violation). All current call sites pass offset 0, so the overflow is latent.

### 1.5 Rendering Defects
- **`PLATFORM_get_provided_windows`** — the `index_of__offset__u32` parameter is completely ignored (no pagination), only a single window (the lazily-allocated backbuffer) is ever exposed despite `PLATFORM__GFX_WINDOW__MAX_QUANTITY_OF` being 128, and the overflow return value is wrong (returns `0` for non-empty buffers, `1` only for zero-size). The caller `allocate_or_get__platform_provided_graphics_windows` (`graphics_window_manager.c:926-978`) loops on the overflow return, so it receives the same single window repeatedly and never observes overflow (**Semantic contract failure**).
- **`PLATFORM_update_texture`** — the only implementation is an empty stub (`tests/core/source/PLATFORM.c:239`); no real backend (SDL, NDS, no_gui) provides one (**Stub-real divergence**). Additionally, unlike `PLATFORM_use_texture` and `PLATFORM_release_texture`, it omits the `PLATFORM_Gfx_Context *` first parameter, breaking the sub-context dispatch pattern. It is also missing from `no_gui/source/NOT_IMPL.c` (an oversight). It is never called anywhere.
- **`PLATFORM_render_entity`** — the NDS reference implementation (`nds/source/rendering/nds_entity.c`) reads `p_entity->sprite_wrapper.p_sprite` and `p_entity->sprite_wrapper.direction`, but the current `Entity` struct (`defines.h:1127-1134`) has no `sprite_wrapper` field. It also calls undeclared helpers (`is_entity_not__updating_graphics`, `set_entity_as__hidden`, etc.) and `#include`s a non-existent header (`rendering/render_entity.h`) — a **Translation Gap** between the stale reference and the current core API. The function is marked `// TODO: remove` (`platform.h:76`).
- **`PLATFORM_release_gfx_window`** — the SDL implementation resets the manager's slot bookkeeping but never invokes the backend's `f_SDL_release_gfx_window` (`GL_release_gfx_window`) callback, so the GL texture and framebuffer objects allocated by `PLATFORM_allocate_gfx_window` are leaked (**Conservation Law** violation — acquired resources not reclaimed). The full-release helper exists (`sdl_gfx_window_manager.c:214`) but is not wired into this hook. The function has zero call sites, so the leak is latent.
- **`PLATFORM_project_world`** — declared at `platform.h:260` with no doc comment (unlike siblings `PLATFORM_project_gfx_window` and `PLATFORM_compose_world`). No production backend implements it; only empty test/template stubs exist (**Stub-real divergence**). Any production caller would hit a **linker error**.
- **`PLATFORM_initialize_rendering__game`** — the SDL implementation uses `SDL_ASSERT_HOST_NULL` as a standalone statement whose boolean result is discarded; the macro only evaluates `(!...->f_hook)` and takes no action, so a null/unbound hook is never caught. In release builds the macro expands to nothing. The correct macro (`SDL_DEBUG_ABORT_IF__HOOK_NULL`) should be used. Marked `// TODO: remove`.

### 1.6 Audio Polling Defect
- **`PLATFORM_poll_audio_effects`** — the NDS implementation has no `is_audio__active` guard, so it processes all 16 pool slots every frame. After an effect with `AUDIO_FLAG__RELEASE_ON_COMPLETE` completes and is released, the flag is never cleared, and `timer_for__audio.remaining__u32` stays at 0 (so `poll_timer_u32` returns true every frame). This causes `mmEffectRelease` to be called repeatedly on an already-released handle — a **use-after-free / double-free** pattern that violates the effect-pool **Representation Invariant** and breaks the pool-recycling cleanup design. The root cause is the missing `is_audio__active` check at the top of the loop.

### 1.7 Time Defects
- **`PLATFORM_get_time_elapsed`** — the no_gui `clock_gettime` path overwrites `timespec__current.tv_sec` with the baseline value before computing the delta, producing a baseline-dominated (not elapsed) result that overflows `u32F20`. The nanosecond borrow is also inverted. This code is duplicated verbatim in the test stub (**Stub-real divergence**). The NDS implementation returns `i32F20` (signed) while the header declares `u32F20` (unsigned) — a type mismatch. The SDL/GL path corrupts the timer accumulators by feeding absolute uptime instead of per-call delta into `progress_timer__u32`.

---

## 2. Impact Assessment

### 2.1 Callers in `core/source` (shared core, compiled into all backends)

| Core caller file | Functions called | Impact of fix |
|---|---|---|
| `core/source/rendering/sprite_manager.c` (lines 104, 111, 119, 127, 171, 225) | `PLATFORM_allocate_texture`, `PLATFORM_release_sprite`, `PLATFORM_allocate_sprite`, `PLATFORM_release_texture` | The core callers pass the **header-conformant** signatures. On an NDS build the NDS definitions conflict (constraint violation) — the build is uncompilable as-is. Fixing the NDS signatures brings them into alignment and makes the core call sites valid on NDS. No caller-side changes needed for the canonical path. |
| `core/source/rendering/aliased_texture_manager.c` (lines 92, 168, 310, 331, 351) | `PLATFORM_allocate_texture`, `PLATFORM_allocate_texture_with__path`, `PLATFORM_release_texture` | Same as above: core passes `Texture` by value; fixing the NDS `Texture`-vs-`PLATFORM_Texture*` mismatch makes these call sites valid on NDS. |
| `core/source/rendering/graphics_window_manager.c` (lines 147, 928, 942-978) | `PLATFORM_allocate_gfx_window`, `PLATFORM_get_provided_windows` | `allocate_or_get__platform_provided_graphics_windows` loops on the overflow return of `PLATFORM_get_provided_windows`. Correcting the pagination/overflow semantics invalidates the assumption that the same single window is returned every iteration — the caller's loop will now correctly advance through distinct windows and observe overflow. |
| `core/source/game.c` (lines 267, 295, 629, 748) | `PLATFORM_tcp_begin`, `PLATFORM_tcp_end`, `PLATFORM_get_time_elapsed`, `PLATFORM_poll_audio_effects` | `begin_multiplayer_for__game` treats a `NULL` return from `PLATFORM_tcp_begin` as fatal and aborts — fixing the Win32 WSAStartup inversion means multiplayer can now begin on Win32 (currently impossible). Because `stop_multiplayer_for__game` (line 295) then calls `PLATFORM_tcp_end`, the corrected begin path also removes the double-reach of `WSACleanup` (see §1.3). `poll_elapsed_time__u32F20_of__game` (line 629) consumes the `u32F20` return; fixing the no_gui overflow and the timer-accumulator corruption means time deltas will be correct. `manage_game__post_render` (line 748) calls `PLATFORM_poll_audio_effects` every frame; fixing the double-release makes audio safe. |
| `core/source/entity/entity.c` (lines 161, 180, 248, 261, 275, 331) | `PLATFORM_read_file`, `PLATFORM_write_file` | `deserialize_entity` / `m_entity_deserialization_handler__default` check `if (error)` to detect read failures; fixing the NDS/no_gui `End_Of_File` check means EOF will now be signalled (currently silently swallowed). `m_entity_serialization_handler__default` checks `if (error)` on writes; making `PLATFORM_write_file` inspect `fwrite`'s return activates these checks (currently dead code). |
| `core/source/multiplayer/tcp_socket.c` (lines 82, 177-183) | `PLATFORM_tcp_poll_connect`, `PLATFORM_tcp_close_socket` | `poll_tcp_socket_for__connection` calls `PLATFORM_tcp_poll_connect` every frame when state is `Connecting`; fixing the `EALREADY` handling means multi-frame connections will now succeed. `unbind_tcp_socket` treats the return with inverted semantics — fixing the NO_GUI return-value inversion **requires updating this caller** in lockstep (see §2.4). |
| `core/source/serialization/game_directory.c` (line 12), `core/source/world/serialization/world_directory.c` (lines 82, 137, 336) | `PLATFORM_append_base_directory_to__path` | All current call sites pass offset 0, so the `strncpy` overflow is latent. Fixing it does not invalidate any current caller assumption; it hardens the function for future non-zero-offset callers. |
| `core/source/game.c` (lines 654, 664, 674 — all commented out) | `PLATFORM_update_log__global`, `PLATFORM_update_log__local`, `PLATFORM_update_log__system` | The call sites are commented out, so the missing-return UB in the NDS log functions is currently unreachable from core. Fixing the missing returns is still required for correctness when the calls are re-enabled. |

### 2.2 Callers in `core/include` (inline helpers / macros)
- `core/include/rendering/nds_sprite_manager.h:82` — `NDS_allocate_sprite__8x8_on__oam_main` is missing a `return` despite declaring a `PLATFORM_Sprite *` return type (a caller-site defect, separate from the function body).
- `core/include/game.h` — `clear_log__system` / `clear_log__local` / `clear_log__global` invoke the `PLATFORM_clear_log__*` functions (the caller clears the core `Log` struct via `initialize_log`, then delegates backend clearing to the platform function). The NDS missing-return UB is reachable if these callers are active on NDS.

### 2.3 Callers in `tests`
- `tests/core/source/PLATFORM.c` / `tests/templates/source/PLATFORM.c` — provide stubs for all 29 functions. The stubs are mostly conformant (matching the header signature) and return safe defaults (`false`, `0`, `UINT32_MAX`, etc.). However:
  - The `PLATFORM_get_time_elapsed` stub duplicates the no_gui `clock_gettime` defect verbatim (`tests/core/source/PLATFORM.c:87-121`), so test builds on non-Windows platforms produce the same overflow.
  - The `PLATFORM_get_position_in__file` stub returns `-1` (→ `UINT32_MAX`), which actually matches the *documented* contract better than the real implementations.
  - The `PLATFORM_tcp_close_socket` stub returns `false` (matching the header contract, not the NO_GUI inversion).
  - The `PLATFORM_read_file` / `PLATFORM_write_file` stubs return `Unknown` unconditionally, so tests do not exercise the error-reporting paths.
- Subsystem test suites (`test_suite_audio_audio_effect.c`, `test_suite_multiplayer_tcp_socket_manager.c`, etc.) test the core wrappers and inline helpers, **not** the `PLATFORM_*` functions directly (they rely on the test stubs in `PLATFORM.c`). No existing test asserts on the broken behavior of any of the 29 functions.

### 2.4 De Facto Contracts Coupled to Broken Behavior
- **`PLATFORM_tcp_close_socket` (NO_GUI)**: the core caller `unbind_tcp_socket` (`tcp_socket.c:177-183`) has adapted to the inverted return value (`if (!result) { ... failed ... }`). Correcting the NO_GUI implementation to honor the header contract will invert this caller's logic — `unbind_tcp_socket` must be updated in lockstep. This is the primary **de facto contract coupling** and the one fix that is *not* behavior-preserving for a current caller.
- **`PLATFORM_tcp_poll_connect`**: `poll_tcp_socket_for__connection` (`tcp_socket.c:82`) stores the returned state directly and short-circuits on `Disconnected`. The `EALREADY` bug means any multi-frame connection permanently fails; fixing it changes the state-transition graph the caller relies on (connections can now complete over multiple frames).
- **`PLATFORM_get_provided_windows`**: `allocate_or_get__platform_provided_graphics_windows` (`graphics_window_manager.c:926-978`) loops `do { ... } while (overflow);` — it relies on the overflow return to terminate. The broken implementation always returns `0`, so the loop terminates after one iteration with the same single window. Fixing the overflow semantics makes the loop iterate correctly across multiple windows — the caller's loop structure is sound and needs no change, but its termination behavior changes meaning.
- **`PLATFORM_write_file` / `PLATFORM_read_file`**: callers check `if (error)` expecting `None` (0) to mean success. Currently the functions always return `None`, so the checks never fire. Fixing the error reporting activates these checks — callers that currently proceed unconditionally on a write/read failure will now handle/abort the error. This is the intended behavior change.
- **`PLATFORM_tcp_end`**: no caller-side coupling to a broken behavior of its own; its only anomaly (double-reach of `WSACleanup`) is inherited from `PLATFORM_tcp_begin` and is resolved by fixing that function.

---

## 3. Resolution Assessment

### 3.1 Signature/ABI Incompatibility (NDS backend) — `PLATFORM_allocate_texture`, `PLATFORM_use_texture`, `PLATFORM_release_texture`, `PLATFORM_allocate_sprite`, `PLATFORM_release_sprite`

**What needs to change:**
1. **`PLATFORM_allocate_texture`** (`nds/source/rendering/nds_texture_manager.c:43`): change the return type from `PLATFORM_Texture *` to `bool`, change the signature to match the header's 4-parameter form (`PLATFORM_Gfx_Context *`, `PLATFORM_Graphics_Window *`, `Texture_Flags`, `Texture *p_OUT_texture`), and implement the body to allocate a `PLATFORM_Texture`, write it into `p_OUT_texture->p_PLATFORM_texture`, set `p_OUT_texture->texture_flags`, and return `false` on success / `true` on failure.
2. **`PLATFORM_use_texture`** (`nds/source/rendering/nds_texture.c:242`): change the 2nd parameter from `PLATFORM_Texture *texture` to `Texture texture` and read `texture.p_PLATFORM_texture` in the body.
3. **`PLATFORM_release_texture`** (`nds/source/rendering/nds_texture_manager.c:76`): change the 2nd parameter from `PLATFORM_Texture *texture` to `Texture texture` and read `texture.p_PLATFORM_texture` in the body.
4. **`PLATFORM_allocate_sprite`** (`nds/source/rendering/sprite_manager.c:88`): change to the 4-parameter header signature and implement to allocate a `PLATFORM_Sprite`, write `p_sprite->p_PLATFORM_sprite`, and return the pointer (or NULL on failure).
5. **`PLATFORM_release_sprite`** (`nds/source/rendering/sprite_manager.c:216`): change the 1st parameter from `PLATFORM_Gfx_Context *` to `Gfx_Context *` and read `p_gfx_context->p_PLATFORM_gfx_context` to access the platform context.

**Caller updates:** None required. The core callers (`sprite_manager.c`, `aliased_texture_manager.c`) already pass the header-conformant signatures. (Separately, fix the missing `return` in the inline caller `NDS_allocate_sprite__8x8_on__oam_main` at `nds_sprite_manager.h:82`.)

**Tests/docs:** No test asserts on the broken signatures. The `// TODO: remove` markers on `platform.h` for the texture bind/use/dispose cluster suggest these may instead be inlined into sprite/world render paths — an alternative resolution is to eliminate them entirely and inline disposal into the render path.

### 3.2 Missing Return on Non-Void Function (NDS log backend) — all six `PLATFORM_*_log__*` functions

**What needs to change:** Add `return true;` after the `NDS_update_log` / `NDS_clear_log` call on the success path in all six functions in `nds/source/nds_log.c` (lines 9, 22, 35, 48, 60, 72). The success path should return `true` (rendering occurred); the non-idle short-circuit path already returns `false`.

**Caller updates:** None. The core call sites (`game.c:654,664,674`) are commented out.

**Tests/docs:** The test stubs (`tests/core/source/PLATFORM.c:436-447`) already return `false` correctly (no UB). No test exercises the NDS log functions directly.

**Test recommendation:** `Property Based Testing` — verify that the return value is `true` when the active UI window is `Idle` and `false` otherwise, across all six functions.

### 3.3 TCP/Socket Logic Defects

**`PLATFORM_tcp_server`** (`sdl/source/multiplayer/unix/sdl_unix_tcp_context.c:236-239`, `sdl/source/multiplayer/win64/sdl_win64_tcp_context.c:228-231`, `no_gui/source/multiplayer/no_gui_tcp_context.c:236-239`):
- Add socket close + pool-slot reset on the `listen()`-failure path, mirroring the existing `fcntl`-failure and `bind`-failure cleanup paths.
- Fix the SDL `fcntl`-failure path's inverted error-log condition (`if (PLATFORM_tcp_close_socket(...))` should be `if (!PLATFORM_tcp_close_socket(...))`).

**`PLATFORM_tcp_close_socket`** (`no_gui/source/multiplayer/no_gui_tcp_context.c:250-265`):
- Invert the return values to match the header contract: return `true` on error (null pointer, close failure), `false` on success.
- **Caller update required:** `unbind_tcp_socket` (`tcp_socket.c:177-183`) must be updated in lockstep — change `if (!result)` to `if (result)` (treat `true` as failure). The SDL implementations already conform, so the caller must work with the conformant semantics.
- Fix the Win64 debug_error message label (`"SDL::WIN64::SDL_tcp_close_socket"` → `"SDL::WIN64::PLATFORM_tcp_close_socket"`).

**`PLATFORM_tcp_poll_connect`** (`sdl/source/multiplayer/sdl_tcp_context.c:157`, `no_gui/source/multiplayer/no_gui_tcp_context.c:166`):
- Add an `EALREADY` case to the `switch` that maps to `TCP_Socket_State__Connecting`.
- **Recommended (more robust):** replace the re-issue-`connect()` technique with the POSIX-recommended pattern: call `connect()` once (yields `EINPROGRESS`), then poll for writability with `select()`/`poll()`, and use `getsockopt(fd, SOL_SOCKET, SO_ERROR, ...)` to read the definitive result. This eliminates platform-dependent `connect()` re-issue behavior.
- Add a null check on `p_PLATFORM_tcp_socket` for consistency with `PLATFORM_tcp_close_socket`.

**`PLATFORM_tcp_begin`** (`sdl/source/multiplayer/win64/sdl_win64_tcp_context.c`):
- Remove the `!` negation: `if (WSAStartup(MAKEWORD(2,2), &__SDL_wsa_data))` (true on failure → log + return NULL; false on success → proceed).
- Fix the misspelled debug label `"PLATFORM_tcp_being"` → `"PLATFORM_tcp_begin"`.

**`PLATFORM_tcp_end`** — **no code change required.** Its own review verdict is *Correct*; it is listed only as a consequence of `PLATFORM_tcp_begin`. Fixing `PLATFORM_tcp_begin`'s WSAStartup condition removes the double-reach of `WSACleanup`, which is the entirety of the anomaly attributed to `PLATFORM_tcp_end`. (Optional, out-of-scope hygiene: iterate the socket pool and close still-open descriptors before freeing the context — a separate resource-management concern, not part of this defect.)

**Caller updates:** `begin_multiplayer_for__game` (`game.c:267`) will now succeed on Win32 instead of aborting. `stop_multiplayer_for__game` (`game.c:295`) calls `PLATFORM_tcp_end`, which is already correct (Win32 `WSACleanup` is the proper counterpart).

**Tests/docs:** No test exercises TCP on a real socket. **Test recommendation:** `Fuzzing` the `PLATFORM_tcp_poll_connect` state machine with simulated `connect()` return values (`EINPROGRESS`, `EALREADY`, `EWOULDBLOCK`, success, `ECONNREFUSED`) to verify the state transitions.

### 3.4 Filesystem I/O Defects

**`PLATFORM_write_file`** (`sdl/source/serialization/sdl_filesystem.c:144`, `nds/source/serialization/nds_filesystem.c:298`, `no_gui/source/serialization/no_gui_filesystem.c:319`):
- Inspect `fwrite`'s return value (`size_of__write`): if it is less than `quantity_of__writes`, return `PLATFORM_Write_File_Error__Max_Size_Reached` (or `Unknown` for a hard failure). The NDS backend has a commented-out TODO referencing this exact comparison.

**`PLATFORM_read_file`** (`sdl/source/serialization/sdl_filesystem.c:167`, `nds/source/serialization/nds_filesystem.c:333`, `no_gui/source/serialization/no_gui_filesystem.c:342`):
- Restore the `End_Of_File` check on the NDS backend (currently commented out).
- Add an `End_Of_File` check to the no_gui backend (currently absent).
- Consider adding `System_Busy` detection where the platform API supports it (e.g., file-locking errors).

**`PLATFORM_get_position_in__file`** (`sdl/source/serialization/sdl_filesystem.c:201`, `nds/source/serialization/nds_filesystem.c:369`, `no_gui/source/serialization/no_gui_filesystem.c:373`):
- Fix the return-type/sentinel mismatch: either change the return type to a signed type with a defined error **Sentinel**, or document that `UINT32_MAX` is the error sentinel (matching the test stub's `-1` → `UINT32_MAX`). The current error path returns `PLATFORM_Read_File_Error__Unknown` (= 3), which is a valid file position — this must be changed to a non-ambiguous sentinel.
- Fix the debug_abort message to reference `PLATFORM_get_position_in__file` instead of `PLATFORM_read_file`.

**`PLATFORM_set_position_in__file`** (`sdl/source/serialization/sdl_filesystem.c`, `nds/source/serialization/nds_filesystem.c`, `no_gui/source/serialization/no_gui_filesystem.c`):
- Fix the debug null-check path: return `false` (not `PLATFORM_Read_File_Error__Unknown`, which converts to `true`).
- Fix the debug_abort message to reference `PLATFORM_set_position_in__file` instead of `PLATFORM_read_file`.

**`PLATFORM_append_base_directory_to__path`** (`sdl/source/serialization/sdl_filesystem.c:55`, `no_gui/source/serialization/no_gui_filesystem.c:232`):
- Change the `strncpy` count from `MAX_LENGTH_OF__IO_PATH` to `MAX_LENGTH_OF__IO_PATH - *p_index_of__path_end` (matching the `append_path` helper at `game_directory.c:42`).
- **Caller updates:** None — all current call sites pass offset 0, so the fix is purely defensive; no caller assumption is invalidated.

**Tests/docs:** No test directly exercises these filesystem functions (they go through the test stubs in `PLATFORM.c` which return `Unknown`/`-1`). **Test recommendation:** `Property Based Testing` for the path-building function with non-zero offsets; `Round Trip Check` for read/write position consistency.

### 3.5 Rendering Defects

**`PLATFORM_get_provided_windows`** (`sdl/source/rendering/sdl_gfx_window_manager.c:51-84`):
- Implement the `index_of__offset__u32` parameter: skip already-acquired windows by starting iteration at the offset index.
- Iterate over the platform's window list (up to `PLATFORM__GFX_WINDOW__MAX_QUANTITY_OF` = 128 for SDL) instead of exposing only the single backbuffer.
- Compute the overflow return correctly: return the count of available windows omitted due to insufficient buffer capacity.

**`PLATFORM_update_texture`**:
- **Option A (fix signature):** add `PLATFORM_Gfx_Context *p_PLATFORM_gfx_context` as the first parameter to match the sibling `PLATFORM_use_texture` / `PLATFORM_release_texture` dispatch pattern, and add the function to `no_gui/source/NOT_IMPL.c`.
- **Option B (remove):** given the `// TODO: remove` markers on the texture bind/use/dispose cluster, inline the texture update into the sprite/world render path and drop the function entirely.
- **Caller updates:** None (the function is never called).

**`PLATFORM_render_entity`** (`nds/source/rendering/nds_entity.c`):
- The NDS reference implementation is structurally incompatible with the current `Entity` struct (no `sprite_wrapper` field) and references undeclared helpers and a non-existent header. Given the `// TODO: remove` marker (`platform.h:76`), the recommended resolution is to either (a) rewrite the implementation against the current `Entity` struct API, or (b) remove the function and inline entity rendering into the sprite/world render path.
- **Caller updates:** None — the function is never called from core.

**`PLATFORM_release_gfx_window`** (`sdl/source/rendering/sdl_gfx_window_manager.c:116-123`):
- Invoke the backend's `f_SDL_release_gfx_window` (`GL_release_gfx_window`) callback before resetting the manager slot, mirroring the full-release helper at `sdl_gfx_window_manager.c:214`.
- **Caller updates:** None — zero call sites. The fix is purely corrective.

**`PLATFORM_project_world`** (`platform.h:260`):
- Add a doc comment to match siblings `PLATFORM_project_gfx_window` and `PLATFORM_compose_world`.
- Provide a real implementation in the SDL backend (or at minimum a no_gui stub in `NOT_IMPL.c`).
- **Caller updates:** None — no production caller exists yet.

**`PLATFORM_initialize_rendering__game`** (`sdl/source/rendering/sdl_gfx_context.c:280-289`):
- Replace `SDL_ASSERT_HOST_NULL` (whose result is discarded) with `SDL_DEBUG_ABORT_IF__HOOK_NULL` (which warns and returns early if the hook is null).
- **Caller updates:** None — the function is called from `nds_game.c:34` on NDS and from the SDL game-init path.

**Tests/docs:** Test stubs for rendering functions are empty no-ops. **Test recommendation:** `Fuzzing` the `PLATFORM_get_provided_windows` pagination logic with buffer sizes from 0 to `MAX_QUANTITY_OF` and offsets from 0 to the window count; `Equivalence Check` between the SDL implementation and the documented example ("for buffer size 8 ... call 1 → index:0, returns 5; call 2 → index:8, returns 0").

### 3.6 Audio Polling Defect

**`PLATFORM_poll_audio_effects`** (`nds/source/audio/nds_audio.c:244`):
- Add an `is_audio__active` guard at the top of the loop to skip inactive slots. This prevents the double-release of already-released effects and avoids unnecessary timer polling.
- Additionally (or alternatively), clear `AUDIO_FLAG__RELEASE_ON_COMPLETE` after releasing the effect, so the slot is not re-processed. The `set_audio_as__not_releasing_on_completion` helper exists (`audio_effect.h:72`) but is never called.
- **Caller updates:** None — `manage_game__post_render` (`game.c:748`) calls this once per frame.

**Tests/docs:** The audio test suite (`test_suite_audio_audio_effect.c`) tests the `Audio_Effect` struct and flag queries but does not test `PLATFORM_poll_audio_effects`. **Test recommendation:** `Property Based Testing` — simulate a pool with one `RELEASE_ON_COMPLETE` effect, advance frames, and assert `mmEffectRelease` is called exactly once.

### 3.7 Time Defect

**`PLATFORM_get_time_elapsed`** (`sdl/source/time/sdl_time.c`, `no_gui/source/time/no_gui_time.c`, `tests/core/source/PLATFORM.c:87`):
- Fix the no_gui `clock_gettime` path: do not overwrite `timespec__current.tv_sec` with the baseline; compute the delta as `current.tv_sec - baseline.tv_sec` and fix the nanosecond borrow to `current.tv_nsec + 1e9 - baseline.tv_nsec` when `current.tv_nsec < baseline.tv_nsec`.
- Fix the NDS return-type mismatch: change `i32F20` to `u32F20` (or add an explicit cast).
- Fix the SDL accumulator corruption: pass the per-call delta (not absolute uptime) to `progress_timer__u32`.
- **Update the test stub** (`tests/core/source/PLATFORM.c:87`) so it no longer duplicates the no_gui defect.
- **Caller updates:** `poll_elapsed_time__u32F20_of__game` (`game.c:629`) consumes the return value and the timer accumulators; fixing both means time deltas and accumulated timers will be correct.

**Tests/docs:** **Test recommendation:** `Round Trip Check` — verify that summing `PLATFORM_get_time_elapsed` deltas over N frames approximates the wall-clock elapsed time; `Property Based Testing` for the fixed-point overflow boundary.

---

## 4. Test Verification Checklist

### 4.1 Existing Tests Survey
- **`tests/core/source/PLATFORM.c`** — provides stubs for all 29 functions; these stubs are the only "tests" that compile against the `PLATFORM_*` interface. Key observations:
  - `PLATFORM_get_time_elapsed` stub (lines 87-121) duplicates the no_gui `clock_gettime` defect verbatim — **test builds on non-Windows will produce the same overflow**; must be fixed alongside the implementation.
  - `PLATFORM_get_position_in__file` stub (line 407) returns `-1` (→ `UINT32_MAX`), which matches the *documented* contract better than the real implementations.
  - `PLATFORM_tcp_close_socket` stub (line ~494) returns `false` (matching the header contract, not the NO_GUI inversion).
  - `PLATFORM_read_file` / `PLATFORM_write_file` stubs return `Unknown` unconditionally — they do not exercise error-reporting paths.
  - No stub asserts on the broken behavior; all return safe defaults.
- **Subsystem test suites** (`test_suite_audio_audio_effect.c`, `test_suite_multiplayer_tcp_socket_manager.c`, `test_suite_rendering_*.c`, `test_suite_serialization_*.c`) test the **core wrappers and inline helpers**, not the `PLATFORM_*` functions directly. They rely on the stubs in `PLATFORM.c` and thus do not catch backend defects.
- No existing test asserts on the broken behavior of any of the 29 functions.

### 4.2 Test Impact Assessment (per defect class)

| Defect class | Existing tests affected? | New tests needed? | Test technique |
|---|---|---|---|
| Signature/ABI (NDS) | No | Yes — `Equivalence Check` between NDS signatures and header | Compile-time verification (`Lint Gate`) |
| Missing return (NDS log) | No | Yes — assert return value is `true` on Idle path | `Property Based Testing` |
| TCP/socket logic (incl. `tcp_end` consequence) | No | Yes — simulate `connect()` errno values; verify begin/end pairing | `Fuzzing`, `Equivalence Check` |
| Filesystem I/O | No | Yes — path-building with non-zero offsets; read/write error propagation | `Property Based Testing`, `Round Trip Check` |
| Rendering | No | Yes — pagination logic, resource release symmetry | `Fuzzing`, `Equivalence Check` |
| Audio polling | No | Yes — assert `mmEffectRelease` called exactly once | `Property Based Testing` |
| Time | Partial (stub duplicates defect) | Yes — delta summation, overflow boundary; fix stub to match impl | `Round Trip Check`, `Property Based Testing` |

### 4.3 Test Impact Summary
- **Blast radius: Low-Medium.** No existing test asserts on the broken behavior. The test stubs in `PLATFORM.c` are mostly conformant (returning safe defaults), so fixing the implementations will not invalidate existing test assertions. The one exception is `PLATFORM_get_time_elapsed` — the test stub duplicates the no_gui defect, so fixing both the stub and the implementation is required to avoid divergence.
- A **phased approach** is recommended for the TCP fixes: fix `PLATFORM_tcp_close_socket`'s return-value inversion and update `unbind_tcp_socket` simultaneously (they are coupled). The other fixes can proceed independently.

---

## 5. Blast Radius Summary

- **Files requiring changes:** Approximately 15-20 files across three backends plus core and tests:
  - **NDS backend** (`nds/source/`): `nds_texture_manager.c` (allocate/release_texture), `nds_texture.c` (use_texture), `sprite_manager.c` (allocate/release_sprite), `nds_log.c` (6 log functions), `nds_audio.c` (poll_audio_effects), `nds_timer.c` (get_time_elapsed), `nds_entity.c` (render_entity), `nds_filesystem.c` (read/write/get/set_position_file).
  - **SDL backend** (`sdl/source/`): `sdl_tcp_context.c` (tcp_poll_connect), `sdl_unix_tcp_socket.c` / `sdl_win64_tcp_socket.c` (tcp_close_socket label), `sdl_unix_tcp_context.c` / `sdl_win64_tcp_context.c` (tcp_server listen cleanup, tcp_begin WSAStartup inversion), `sdl_filesystem.c` (read/write/get/set_position_file, append_base_directory), `sdl_gfx_window_manager.c` (get_provided_windows, release_gfx_window), `sdl_gfx_context.c` (initialize_rendering__game), `sdl_time.c` (get_time_elapsed). (`sdl_texture_manager.c` / `sdl_sprite_manager.c` are already conformant — no change needed.)
  - **no_gui backend** (`no_gui/source/`): `no_gui_tcp_context.c` (tcp_server, tcp_close_socket inversion, tcp_poll_connect), `no_gui_filesystem.c` (read/write/get/set_position_file, append_base_directory), `NOT_IMPL.c` (add missing stubs for `PLATFORM_update_texture`, `PLATFORM_project_world`).
  - **Core** (`core/source/`): `tcp_socket.c` (update `unbind_tcp_socket` to match corrected `PLATFORM_tcp_close_socket` return semantics).
  - **Tests** (`tests/core/source/`): `PLATFORM.c` (fix `PLATFORM_get_time_elapsed` stub so it does not duplicate the no_gui defect).
  - **No change:** `PLATFORM_tcp_end` (correct as-is; anomaly resolved by fixing `PLATFORM_tcp_begin`).

- **Behavior-preserving for current callers?** Mostly yes, with two notable exceptions:
  1. **`PLATFORM_tcp_close_socket` (NO_GUI)**: fixing the return-value inversion **invalidates** the de facto contract that `unbind_tcp_socket` has adapted to. The caller must be updated in lockstep.
  2. **`PLATFORM_get_provided_windows`**: fixing the pagination/overflow semantics changes the return values the caller `allocate_or_get__platform_provided_graphics_windows` relies on to terminate its loop. The loop structure is sound and will work correctly with the fix, but the caller's termination condition changes meaning.

- **Phased approach needed?** **Yes.**
  - Phase 1 (build-unblocking): the five NDS signature mismatches (`PLATFORM_allocate_texture`, `PLATFORM_use_texture`, `PLATFORM_release_texture`, `PLATFORM_allocate_sprite`, `PLATFORM_release_sprite`) are C11 6.7p4 constraint violations that make the NDS build **uncompilable** as-is under `-Wall`. These are the highest-priority fixes.
  - Phase 2 (coupled contract): `PLATFORM_tcp_close_socket` + `unbind_tcp_socket` must be fixed together.
  - Phase 3 (independent): all remaining fixes (log returns, tcp_server/poll_connect/begin, filesystem I/O, rendering, audio, time) are independent and can proceed in any order.

- **De facto contracts invalidated:**
  1. `unbind_tcp_socket` relying on the inverted `PLATFORM_tcp_close_socket` return value (NO_GUI).
  2. `PLATFORM_get_provided_windows` returning `0` (no overflow) on every call, which `allocate_or_get__platform_provided_graphics_windows` uses to terminate its loop after one iteration.
  3. `PLATFORM_write_file` / `PLATFORM_read_file` always returning `None`, which makes `if (error)` checks in `entity.c` dead code.
  4. `PLATFORM_get_time_elapsed` returning overflow/baseline-dominated values on no_gui/non-Windows, which `poll_elapsed_time__u32F20_of__game` propagates into the tick accumulator.
  5. `PLATFORM_tcp_poll_connect` returning `Disconnected` on the second poll, which permanently halts connection polling in `poll_tcp_socket_for__connection`.

- **Build breakage:** The five NDS signature mismatches are C11 6.7p4 constraint violations that make the NDS build **uncompilable** as-is under `-Wall` (`nds/Makefile:17`). These are the highest-priority, hard-blocking fixes; all other defects are latent or runtime-semantic and do not block compilation.
