## 1. Header
- **Function name:** `PLATFORM_use_texture`
- **File of origin:** `core/include/platform.h`, line 152 (declared immediately under `// TODO: remove`)
- **Signature (header):**
  ```c
  void PLATFORM_use_texture(
          PLATFORM_Gfx_Context *p_PLATFORM_gfx_context,
          Texture texture);
  ```
- **Implementations:**
  - Canonical (SDL/GL): `sdl/source/rendering/sdl_texture_manager.c:161` — dispatches through `p_PLATFORM_gfx_context->SDL_gfx_sub_context__wrapper.f_SDL_use_texture(texture.p_PLATFORM_texture)`, the hook bound to `GL_use_texture` (`sdl/source/rendering/sdl_gfx_context.c:128-130`), which calls `glBindTexture(GL_TEXTURE_2D, handle)` (`sdl/source/rendering/opengl/gl_texture.c:203`).
  - Conforming stubs: `tests/core/source/PLATFORM.c:243`, `tests/templates/source/PLATFORM.c:243` (empty body, signature matches header).
  - **Conflicting (NDS):** `nds/source/rendering/nds_texture.c:242` — declares the 2nd parameter as `PLATFORM_Texture *texture` instead of `Texture texture`. See §7.
- **Note:** the prior file content ("no implementation found") is stale. Multiple implementations exist; this section documents them.

## 2. Semantic
Binds (activates) a texture on the active rendering backend so subsequent draw calls sample from it. The `Texture` is passed by value; the backend reads only its embedded `p_PLATFORM_texture` pointer and binds the corresponding platform/GPU handle. In the SDL/GL backend this is `glBindTexture(GL_TEXTURE_2D, handle)`. Marked `// TODO: remove` — architecturally intended to be inlined into sprite/world render calls (`agents/platform_api.md:685` — "Texture binding inlined into sprite/world render calls").

## 3. Pre-conditions
1. `p_PLATFORM_gfx_context` is non-null and points to an initialized graphics context whose `SDL_gfx_sub_context__wrapper.f_SDL_use_texture` sub-context hook has been bound (to `GL_use_texture` in the SDL/GL backend).
2. `texture.p_PLATFORM_texture` is non-null and points to a valid, previously-allocated `PLATFORM_Texture` carrying a valid backend handle (e.g. an assigned `GL_texture_handle` in the SDL/GL backend).
3. `Texture` is passed by value; `texture` is a shallow copy whose `p_PLATFORM_texture` still aliases the caller's underlying `PLATFORM_Texture` object.
4. This is **not** an initialization/RAII function — it performs no allocation and acquires no resource; "use" here means GPU state binding, not resource acquisition.

## 4. Post-conditions
1. The platform texture is bound to the active rendering backend (SDL/GL: `GL_TEXTURE_2D` bound to `p_PLATFORM_texture->GL_texture_handle` via `glBindTexture`).
2. Returns void.
3. `p_PLATFORM_gfx_context` is dispatched-through but not structurally mutated; the `Texture` value parameter is not mutated (only `texture.p_PLATFORM_texture` is read).
4. The GL backend validates the bind with `glGetError()` and logs (but does not propagate) any GL error — no state change occurs on failure.

## 5. Correctness Verdict
Incorrect

## 6. Semantic Alignment
The canonical SDL/GL implementation fulfills the intent: it binds the texture handle via the `f_SDL_use_texture` dispatch table to `GL_use_texture` -> `glBindTexture`. The NDK backend is an intentional no-op (NDS hardware manages textures without a bind step), which would be semantically acceptable *if* its signature matched the header. However, the NDK definition uses an incompatible parameter type (see §7), breaking the contract. The test/template stubs match the header and perform no work, consistent with the test double role.

## 7. Implementation Correctness
- **Type compatibility (canonical / SDL / stubs):** The SDL definition matches the header exactly — `Texture texture` by value, then `texture.p_PLATFORM_texture` (type `PLATFORM_Texture *`, from `defines.h:755`) is forwarded to `f_SDL_Use_Texture` whose typedef is `void (*f_SDL_Use_Texture)(PLATFORM_Texture *p_PLATFORM_texture)` (`sdl/include/sdl_defines.h:141-142`). Exact match, no implicit conversion or truncation. The test stubs match the header signature verbatim. The NDK `PLATFORM_Texture` is a fully-defined struct (`nds/include/nds_defines.h:17-27`) but remains a *different* type from the core `Texture` wrapper struct. ✓ (canonical path)
- **Conflicting types (NDS backend):** `nds/source/rendering/nds_texture.c:242-246` defines
  ```c
  void PLATFORM_use_texture(
          PLATFORM_Gfx_Context *p_PLATFORM_gfx_context,
          PLATFORM_Texture *texture) { /* no-op */ }
  ```
  The second parameter is `PLATFORM_Texture *` (`struct PLATFORM_Texture_t *`), whereas the `platform.h` prototype visible in this same translation unit (pulled in via `core/include/defines.h:4` -> `#include "platform.h"`, confirmed reachable because `INCLUDES = core/include nds/include` per `nds/Makefile:60` and no shadowing `nds/include/defines.h` exists) declares it as `Texture` (`struct Texture_t`, forward-declared in `defines_weak.h:382`, completed in `defines.h:754-757`). `struct Texture_t` and `struct PLATFORM_Texture_t *` are incompatible types, so this is a **C11 6.7p4 constraint violation ("conflicting types for 'PLATFORM_use_texture'")** diagnosed as a hard error under the NDK `-Wall` flags (`nds/Makefile:17`). This is the **same defect class** already documented for `PLATFORM_allocate_texture`'s NDK backend (`agents/core/review/include/platform.h/PLATFORM_allocate_texture.md` §7) and for `PLATFORM_allocate_sprite`. Because no `Texture` member is read in the no-op body, this manifests as a compile-time failure rather than runtime UB, but it still makes the NDK backend uncompilable as written.
- **No-GUI backend:** `no_gui/source/NOT_IMPL.c` contains **no** `PLATFORM_use_texture` stub (confirmed: the only NDK/no-gui texture functions stubbed there are the allocate/update/release set for the SDL contract; `PLATFORM_use_texture` is absent). The no-GUI backend therefore has no link-time definition — it is only safe because no_gui code paths do not reference the function. (Latent link-time risk, same "Missing from NOT_IMPL catalog" oversight noted for `PLATFORM_update_texture`.)
- **Undefined behavior:** No UB on the happy path. The SDL wrapper dereferences `p_PLATFORM_gfx_context` with no null-check and `GL_use_texture` dereferences `p_PLATFORM_texture->GL_texture_handle` with no null-check of `p_PLATFORM_texture`; per Lavender's convention these are caller preconditions and the validation pattern is consistent with `SDL_release_texture` / `SDL_allocate_texture` siblings. No broken pointer arithmetic, no out-of-bounds, no type punning.
- **Validation appropriateness:** No in-function validation; consistent with the engine's PAL pattern where validation is the caller's responsibility at the platform boundary. The `// TODO: remove` marker signals the function is deprecated/architected-for-removal, so adding defensive checks here would be wasteful — the function should be eliminated and its binding inlined (as `platform_api.md:685` directs).
- **Lavender init semantics:** Not applicable — this is a binding/state function, not an initializer; it does not clean structs to pool defaults nor perform resource acquisition.

## 8. Side Effects
- Binds the platform texture to the active rendering backend (SDL/GL: `glBindTexture(GL_TEXTURE_2D, p_PLATFORM_texture->GL_texture_handle)`); this mutates driver-side GL texture-unit state.
- Does **not** mutate `p_PLATFORM_gfx_context` (dispatch only) nor the `Texture` value parameter (reads `texture.p_PLATFORM_texture` only).
- The GL backend may emit a `debug_error` message on `glGetError()` failure; no compensating cleanup or state revert occurs on failure.
- Allocates/frees no GPU memory (binding is a state operation, not an allocation).
